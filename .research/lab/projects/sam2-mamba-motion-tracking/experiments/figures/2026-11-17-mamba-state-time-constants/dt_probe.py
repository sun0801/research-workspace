"""学習済みの重みで val（tuning）の動画を数本だけ流し、Mamba の1歩の中身を記録する（推論だけ）。

SAM2 repo は読み取りだけ。`MambaCell._step` をこのスクリプトの中で差し替えて、同じ計算をしながら統計を取る
（返す値は元の式のまま）。評価の出力は --out-dir（プロジェクトの外の一時フォルダ）に書かせる。

記録するもの（段・state を持ち越したフレーム数ごと）:
- dt の実際の値（入力に依存する分を含む）と、bias だけの値との比
- 1ステップで state が残る割合 exp(-dt·|A|) の平均、半減期
- Mamba の出力（out_proj の後）のうち、前のフレームから持ち越した state から来る分・今のフレームで書いた分・
  state を通らない分（D·x）の大きさ

使い方（SAM2 repo の .venv-sam2 の python で）:
  CUDA_VISIBLE_DEVICES=0 python dt_probe.py --checkpoint <checkpoint.pt> --limit-videos 8 --eval-out <tmp dir> --out data/dt_probe_A.json
"""
import argparse
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2")
sys.path.insert(0, str(REPO))

BUCKETS = [(0, 0), (1, 1), (2, 3), (4, 7), (8, 15), (16, 31), (32, 63), (64, 10 ** 9)]


def bucket(c):
    for lo, hi in BUCKETS:
        if lo <= c <= hi:
            return f"{lo}" if lo == hi else (f"{lo}-{hi}" if hi < 10 ** 9 else f"{lo}+")
    return "?"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--limit-videos", type=int, default=8)
    p.add_argument("--eval-out", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    out_path = Path(args.out).resolve()
    os.chdir(REPO)

    import torch
    import torch.nn.functional as F

    import sam2.modeling.temporal_adapters as ta

    cur = {"count": 0}
    acc = defaultdict(lambda: defaultdict(float))
    n_calls = defaultdict(int)

    orig_stream = ta.TemporalAdapterBase.stream_step

    def stream_step(self, *a, **kw):
        cur["count"] = int(self._update_count)
        if self.reset_interval > 0 and self._update_count % self.reset_interval == 0:
            cur["count"] = 0
        return orig_stream(self, *a, **kw)

    def _step(self, x, conv_state_in, ssm_state_in):
        m = self.mamba
        xz = m.in_proj(x)
        xi, z = xz.chunk(2, dim=-1)
        conv_state = torch.cat((conv_state_in[..., 1:], xi.unsqueeze(-1).to(conv_state_in.dtype)), dim=-1)
        xi = (conv_state * m.conv1d.weight[:, 0, :].unsqueeze(0)).sum(dim=-1)
        if m.conv1d.bias is not None:
            xi = xi + m.conv1d.bias
        xi = m.act(xi)
        x_dbl = m.x_proj(xi)
        dt_raw, b_in, c_in = torch.split(x_dbl, [m.dt_rank, self.d_state, self.d_state], dim=-1)
        delta = F.softplus(F.linear(dt_raw, m.dt_proj.weight).float() + m.dt_proj.bias.float())
        a = -torch.exp(m.A_log.float())
        xi_f = xi.float()
        decay = torch.exp(delta.unsqueeze(-1) * a.unsqueeze(0))
        carried = ssm_state_in * decay
        written = delta.unsqueeze(-1) * b_in.float().unsqueeze(1) * xi_f.unsqueeze(-1)
        ssm_state = carried + written
        c = c_in.float().unsqueeze(1)
        y = (ssm_state * c).sum(dim=-1)
        y = y + m.D.float().unsqueeze(0) * xi_f
        gate = F.silu(z.float())
        out = m.out_proj(y * gate)
        # ---- 統計（出力には影響しない）
        w = m.out_proj.weight.float()
        o_carry = F.linear((carried * c).sum(-1) * gate, w)
        o_write = F.linear((written * c).sum(-1) * gate, w)
        o_skip = F.linear(m.D.float().unsqueeze(0) * xi_f * gate, w)
        o_all = o_carry + o_write + o_skip
        d_bias = F.softplus(m.dt_proj.bias.float())
        ratio = delta / d_bias.unsqueeze(0)
        decay_bias = torch.exp(d_bias.unsqueeze(-1) * a)
        sel = torch.linspace(0, delta.shape[0] - 1, min(256, delta.shape[0]), device=delta.device).long()
        hl = (math.log(2) / (delta[sel].unsqueeze(-1) * (-a).unsqueeze(0))).flatten()
        qs = torch.quantile(hl, torch.tensor([0.1, 0.5, 0.9], device=hl.device))
        rq = torch.quantile(ratio[sel].flatten(), torch.tensor([0.1, 0.5, 0.9], device=hl.device))
        key = (str(self.d_model), bucket(cur["count"]))
        s = acc[key]
        vals = {
            "dt_mean": delta.mean(), "dt_median": delta[sel].median(), "dt_bias_mean": d_bias.mean(),
            "ratio_q10": rq[0], "ratio_q50": rq[1], "ratio_q90": rq[2],
            "retain_mean": decay.mean(), "retain_bias_mean": decay_bias.mean(),
            "halflife_q10": qs[0], "halflife_q50": qs[1], "halflife_q90": qs[2],
            "sq_carry": o_carry.pow(2).sum(), "sq_write": o_write.pow(2).sum(), "sq_skip": o_skip.pow(2).sum(),
            "sq_all": o_all.pow(2).sum(), "state_rms": ssm_state.pow(2).mean().sqrt(),
            "dot_carry_all": (o_carry * o_all).sum(),
        }
        for k2, v in vals.items():
            s[k2] += float(v)
        n_calls[key] += 1
        return out, conv_state, ssm_state

    ta.TemporalAdapterBase.stream_step = stream_step
    ta.MambaCell._step = _step

    import training.mose_adapter_eval as ev

    sys.argv = ["mose_adapter_eval", "--condition", "probe", "--trainer-checkpoint", args.checkpoint,
                "--limit-videos", str(args.limit_videos), "--out-dir", args.eval_out, "--overwrite"]
    ev.main()

    names = {"256": "64段", "64": "128段", "32": "256段"}
    rows = []
    for (dm, b), s in acc.items():
        n = n_calls[(dm, b)]
        r = {"level": names[dm], "frames_carried": b, "calls": n}
        for k2 in ("dt_mean", "dt_median", "dt_bias_mean", "ratio_q10", "ratio_q50", "ratio_q90", "retain_mean",
                   "retain_bias_mean", "halflife_q10", "halflife_q50", "halflife_q90", "state_rms"):
            r[k2] = s[k2] / n
        r["out_share_carry"] = math.sqrt(s["sq_carry"] / s["sq_all"])
        r["out_share_write"] = math.sqrt(s["sq_write"] / s["sq_all"])
        r["out_share_skip"] = math.sqrt(s["sq_skip"] / s["sq_all"])
        r["proj_carry_on_all"] = s["dot_carry_all"] / s["sq_all"]
        rows.append(r)
    order = {f"{lo}" if lo == hi else (f"{lo}-{hi}" if hi < 10 ** 9 else f"{lo}+"): i for i, (lo, hi) in enumerate(BUCKETS)}
    rows.sort(key=lambda r: (["64段", "128段", "256段"].index(r["level"]), order[r["frames_carried"]]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"checkpoint": args.checkpoint, "limit_videos": args.limit_videos, "rows": rows}, indent=1) + "\n")
    print(f"{'段':6s} {'持越':>6s} {'calls':>6s} {'dt/bias 10/50/90%':>22s} {'残る':>6s} {'(bias)':>7s} {'半減期 10/50/90%':>20s} "
          f"{'持越分':>7s} {'今書いた分':>9s} {'D·x':>6s} {'射影':>7s} {'state rms':>10s}")
    for r in rows:
        print(f"{r['level']:6s} {r['frames_carried']:>6s} {r['calls']:6d} "
              f"{r['ratio_q10']:6.2f}/{r['ratio_q50']:5.2f}/{r['ratio_q90']:5.2f}   {r['retain_mean']:6.3f} {r['retain_bias_mean']:7.3f} "
              f"{r['halflife_q10']:6.1f}/{r['halflife_q50']:5.1f}/{r['halflife_q90']:6.1f} "
              f"{r['out_share_carry']:7.3f} {r['out_share_write']:9.3f} {r['out_share_skip']:6.3f} {r['proj_carry_on_all']:7.3f} {r['state_rms']:10.4f}")


if __name__ == "__main__":
    main()
