"""段ごとに、state を持ち越すことが特徴（adapter の出力）をどれだけ変えているかを測る（推論だけ）。

各フレーム・各段で、同じ入力に対して
  (a) 持ち越した state で1歩進めたときの残差 α·W_out(h)
  (b) その段の state だけ 0 に戻して1歩進めたときの残差
を両方計算し、‖(a)−(b)‖／‖特徴‖ と ‖(a)‖／‖特徴‖ を記録する。モデルが使うのは (a) だけなので、評価の結果は変わらない。
(b) は「その段だけ毎フレーム reset した場合」の、その段への直接の効果（下の段への伝わり方は含まない）。

SAM2 repo は読み取りだけ（import のみ）。`PyramidAdapter._forward_impl` をこのスクリプトの中で差し替える。

使い方（SAM2 repo の .venv-sam2 の python で）:
  CUDA_VISIBLE_DEVICES=0 python carry_effect_probe.py --checkpoint <checkpoint.pt> --limit-videos 8 --eval-out <tmp> --out data/carry_effect_A.json
"""
import argparse
import json
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
    from sam2.modeling.temporal_adapters import PYRAMID_LEVELS

    cur = {"count": 0}
    acc = defaultdict(lambda: defaultdict(float))
    orig_stream = ta.TemporalAdapterBase.stream_step

    def stream_step(self, *a, **kw):
        cur["count"] = int(self._update_count)
        return orig_stream(self, *a, **kw)

    def _forward_impl(self, pix_feat, high_res_features, state):
        feats = {"64": pix_feat}
        feats["256"], feats["128"] = high_res_features[0], high_res_features[1]
        b = pix_feat.shape[0]
        new_state, prev_h = {}, None
        outputs = dict(feats)
        fresh = self.init_state(b, pix_feat.device, state[self.levels[0]].ssm_state.dtype
                                if False else state[self.levels[0]].conv_state.dtype)
        for name in self.levels:
            feat = feats[name]
            _, c, h, w = feat.shape
            x = self.norms[name](self._to_tokens(feat))
            if prev_h is not None:
                up = F.interpolate(prev_h, scale_factor=2.0, mode="bilinear", align_corners=False)
                x = x + self._to_tokens(self.topdown[name](up))
            hseq, new_state[name] = self.cells[name](x, state[name])
            residual = self._to_map(self.alphas[name] * self.outs[name](hseq), b, h, w).to(feat.dtype)
            # ---- 統計：同じ入力で、この段の state だけ 0 にした場合
            h0, _ = self.cells[name](x, fresh[name])
            res0 = self._to_map(self.alphas[name] * self.outs[name](h0), b, h, w).to(feat.dtype)
            fn = feat.float().norm()
            s = acc[(name, bucket(cur["count"]))]
            s["n"] += 1
            s["res"] += float(residual.float().norm() / fn)
            s["carry"] += float((residual.float() - res0.float()).norm() / fn)
            s["carry_over_res"] += float((residual.float() - res0.float()).norm() / residual.float().norm().clamp_min(1e-12))
            outputs[name] = feat + residual
            prev_h = self._to_map(hseq, b, h, w)
        high_res_out = [outputs["256"], outputs["128"]] + list(high_res_features[2:])
        return outputs["64"], high_res_out, new_state

    ta.TemporalAdapterBase.stream_step = stream_step
    ta.PyramidAdapter._forward_impl = _forward_impl

    import training.mose_adapter_eval as ev

    sys.argv = ["mose_adapter_eval", "--condition", "probe", "--trainer-checkpoint", args.checkpoint,
                "--limit-videos", str(args.limit_videos), "--out-dir", args.eval_out, "--overwrite"]
    ev.main()

    order = {(f"{lo}" if lo == hi else (f"{lo}-{hi}" if hi < 10 ** 9 else f"{lo}+")): i for i, (lo, hi) in enumerate(BUCKETS)}
    rows = []
    for (name, bk), s in acc.items():
        n = s["n"]
        rows.append({"level": name, "frames_carried": bk, "calls": int(n), "residual_over_feature": s["res"] / n,
                     "carry_effect_over_feature": s["carry"] / n, "carry_effect_over_residual": s["carry_over_res"] / n})
    rows.sort(key=lambda r: (["64", "128", "256"].index(r["level"]), order[r["frames_carried"]]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"checkpoint": args.checkpoint, "limit_videos": args.limit_videos, "rows": rows}, indent=1) + "\n")
    print(f"{'段':5s} {'持越':>6s} {'calls':>6s} {'‖残差‖/‖特徴‖':>14s} {'‖持越の効果‖/‖特徴‖':>20s} {'‖持越の効果‖/‖残差‖':>20s}")
    for r in rows:
        print(f"{r['level']:5s} {r['frames_carried']:>6s} {r['calls']:6d} {r['residual_over_feature']:14.4f} "
              f"{r['carry_effect_over_feature']:20.5f} {r['carry_effect_over_residual']:20.4f}")


if __name__ == "__main__":
    main()
