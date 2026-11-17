"""学習中の checkpoint（2 epoch ごと）から、adapter の各パラメータがどれだけ・どう動いたかを読む（CPUだけ）。

- 変化の大きさ：相対（‖Δ‖/‖w‖）と絶対（要素の RMS）。
- 向き：‖w_end‖/‖w_start‖ と cos(w_start, w_end)。重み減衰だけなら cos≈1 でノルムだけ縮む。
- 動き方：checkpoint 間の変化どうしの相関（正なら同じ向きに進み続けている。0 付近ならランダムウォーク）。
- Adam の状態：sqrt(exp_avg_sq)（勾配の大きさ。clip 後）と eps（1e-8）の比。
- 比較の物差し：Σlr（毎回同じ向きに lr ずつ動いた場合の上限）と sqrt(Σlr²)（毎回ランダムな向きに動いた場合の目安）。

使い方: CUDA_VISIBLE_DEVICES="" python param_motion.py <run_dir> [<run_dir> ...]
"""
import glob
import math
import os
import re
import sys

import torch

P = "temporal_mamba_adapter."
LR0, LR1, WD = 3e-4, 3e-5, 0.1  # config_resolved.yaml: adapter_lr の cosine、weight_decay


def lr_at(where):
    return LR1 + 0.5 * (LR0 - LR1) * (1 + math.cos(math.pi * where))


def rms(t):
    return float(t.float().pow(2).mean().sqrt())


def load(run):
    out = {}
    for f in glob.glob(os.path.join(run, "checkpoints", "checkpoint_*.pt")):
        m = re.search(r"checkpoint_(\d+)\.pt$", f)
        if m:
            out[int(m.group(1))] = f
    return dict(sorted(out.items()))


def opt_index(ck):
    """optimizer の state の番号 → パラメータ名。グループ内は named_parameters の順（形で検算）。"""
    sd = ck["model"]
    names = [k for k in sd if k.startswith(P)]
    groups = ck["optimizer"]["param_groups"]
    adapter_groups = [g for g in groups if abs(g["lr"] - groups[-1]["lr"]) < 1e-12]
    decay = [g for g in adapter_groups if g["weight_decay"] > 0][0]["params"]
    nodecay = [g for g in adapter_groups if g["weight_decay"] == 0][0]["params"]
    st = ck["optimizer"]["state"]

    def is_nodecay(n):
        return ("bias" in n) or (".alphas." in n) or n.endswith(".A_log") or n.endswith(".mamba.D") or (".norms." in n)

    # named_parameters の順は state_dict の順と違う（Mamba は A_log, D が先）ので、形で対応を確かめながら割り当てる
    order_mamba = ["A_log", "D", "in_proj.weight", "conv1d.weight", "conv1d.bias", "x_proj.weight",
                   "dt_proj.weight", "dt_proj.bias", "out_proj.weight"]
    ordered = []
    for lv in ("64", "128", "256"):
        ordered += [f"{P}norms.{lv}.weight", f"{P}norms.{lv}.bias"]
    ordered_cells = [f"{P}cells.{lv}.mamba.{k}" for lv in ("64", "128", "256") for k in order_mamba]
    rest = [n for n in names if n not in ordered and n not in ordered_cells]
    cand = {}
    for label, idxs, flt in (("decay", decay, lambda n: not is_nodecay(n)), ("nodecay", nodecay, is_nodecay)):
        pool = [n for n in names if flt(n)]
        # 形が合う並びを探す：候補の並び（norms→cells→残り / cells→残り→norms など）を試す
        tries = [
            [n for n in ordered if flt(n)] + [n for n in ordered_cells if flt(n)] + [n for n in rest if flt(n)],
            [n for n in ordered_cells if flt(n)] + [n for n in rest if flt(n)] + [n for n in ordered if flt(n)],
            [n for n in ordered_cells if flt(n)] + [n for n in ordered if flt(n)] + [n for n in rest if flt(n)],
        ]
        ok = None
        for tr in tries:
            if len(tr) == len(idxs) and all(tuple(st[i]["exp_avg"].shape) == tuple(sd[n].shape) for i, n in zip(idxs, tr)):
                ok = tr
                break
        assert ok is not None, f"{label}: 形の合う並びが見つからない（{len(pool)} 個 / {len(idxs)} 個）"
        for i, n in zip(idxs, ok):
            cand[n] = i
    return cand


def main():
    for run in sys.argv[1:]:
        cks = load(run)
        eps = list(cks)
        data = {e: torch.load(f, map_location="cpu", weights_only=False) for e, f in cks.items()}
        last = data[eps[-1]]
        steps = last["steps"]
        total = max(v for v in steps.values() if isinstance(v, int)) if isinstance(steps, dict) else int(steps)
        per_ep = total / eps[-1]
        s0, s1 = int(per_ep * eps[0]), total
        sum_lr = sum(lr_at(s / total) for s in range(s0, s1))
        sum_lr2 = math.sqrt(sum(lr_at(s / total) ** 2 for s in range(s0, s1)))
        sum_lr_all = sum(lr_at(s / total) for s in range(0, total))
        print(f"== {run}\n   epochs {eps}, 総更新 {total}（1 epoch {per_ep:.0f}）")
        print(f"   ep{eps[0]}→ep{eps[-1]}: Σlr = {sum_lr:.3f}, sqrt(Σlr²) = {sum_lr2:.4f} | 全体の Σlr = {sum_lr_all:.3f}"
              f" | 重み減衰だけのときの縮み exp(-{WD}·Σlr) = {math.exp(-WD * sum_lr):.3f}（ep{eps[0]}→ep{eps[-1]}）")
        idx = opt_index(last)
        names = [k for k in last["model"] if k.startswith(P)]
        print(f"   {'name':46s} {'wd':>3s} {'rms(w)':>8s} {'rmsΔ':>8s} {'‖Δ‖/‖w‖':>8s} {'norm比':>6s} {'cos':>6s} "
              f"{'Δ/√Σlr²':>8s} {'Δ/Σlr':>7s} {'区間相関':>7s} {'√v(ep'+str(eps[0])+')':>10s} {'√v(end)':>9s} {'√v<1e-8':>8s}")
        for n in names:
            w0, w1 = data[eps[0]]["model"][n].float(), last["model"][n].float()
            d = w1 - w0
            rel = float(d.norm() / w0.norm().clamp_min(1e-12))
            nr = float(w1.norm() / w0.norm().clamp_min(1e-12))
            cos = float((w0 * w1).sum() / (w0.norm() * w1.norm()).clamp_min(1e-12))
            ds = [data[eps[i + 1]]["model"][n].float() - data[eps[i]]["model"][n].float() for i in range(len(eps) - 1)]
            cors = []
            for a, b in zip(ds[:-1], ds[1:]):
                den = a.norm() * b.norm()
                if float(den) > 0:
                    cors.append(float((a * b).sum() / den))
            cor = sum(cors) / len(cors) if cors else float("nan")
            i = idx[n]
            v0 = data[eps[0]]["optimizer"]["state"][i]["exp_avg_sq"].float().sqrt()
            v1 = last["optimizer"]["state"][i]["exp_avg_sq"].float().sqrt()
            wd = "0" if last["optimizer"]["state"] and any(i in g["params"] and g["weight_decay"] == 0 for g in last["optimizer"]["param_groups"]) else "0.1"
            print(f"   {n[len(P):]:46s} {wd:>3s} {rms(w1):8.4f} {rms(d):8.5f} {rel:8.4f} {nr:6.3f} {cos:6.3f} "
                  f"{rms(d) / sum_lr2:8.2f} {rms(d) / sum_lr:7.4f} {cor:7.3f} {float(v0.median()):10.2e} {float(v1.median()):9.2e} "
                  f"{float((v1 < 1e-8).float().mean()) * 100:7.1f}%")
        # A_log は初期値が分かる（log 1..16）
        for lv in ("64", "128", "256"):
            n = f"{P}cells.{lv}.mamba.A_log"
            a0 = torch.log(torch.arange(1, 17).float())[None].expand_as(last["model"][n])
            for e in (eps[0], eps[-1]):
                d = data[e]["model"][n].float() - a0
                print(f"   A_log L{lv} 初期値→ep{e}: rmsΔ {rms(d):.5f}, mean|Δ| {float(d.abs().mean()):.5f}, max|Δ| {float(d.abs().max()):.4f}, "
                      f"平均（符号つき） {float(d.mean()):+.5f}")


if __name__ == "__main__":
    main()
