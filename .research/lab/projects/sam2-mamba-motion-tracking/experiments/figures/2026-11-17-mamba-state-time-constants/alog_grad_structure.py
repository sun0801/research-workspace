"""Adam の状態（exp_avg_sq）から、A_log の要素ごとの勾配の大きさが、時定数（dt·|A|）とどう関係するかを見る（CPUだけ）。

使い方: CUDA_VISIBLE_DEVICES="" python alog_grad_structure.py <checkpoint.pt>
"""
import math
import sys

import torch
import torch.nn.functional as F

from param_motion import P, opt_index

EPS = 1e-8


def main():
    ck = torch.load(sys.argv[1], map_location="cpu", weights_only=False)
    sd, st = ck["model"], ck["optimizer"]["state"]
    idx = opt_index(ck)
    for lv in ("64", "128", "256"):
        pre = f"{P}cells.{lv}.mamba."
        a = torch.exp(sd[pre + "A_log"].float())
        dt = F.softplus(sd[pre + "dt_proj.bias"].float())
        rate = dt[:, None] * a  # 1ステップで exp(-rate) 残る
        hl = math.log(2) / rate
        v = st[idx[pre + "A_log"]]["exp_avg_sq"].float().sqrt()
        print(f"== L{lv}: A_log の √v 全体 median {float(v.median()):.2e}, 要素の RMS {float(v.pow(2).mean().sqrt()):.2e}, "
              f"eps({EPS:g}) 未満 {float((v < EPS).float().mean()) * 100:.1f}%")
        for name, m in (("半減期 < 2", hl < 2), ("2〜8", (hl >= 2) & (hl < 8)), ("8〜32", (hl >= 8) & (hl < 32)),
                        ("32〜128", (hl >= 32) & (hl < 128)), ("128 以上", hl >= 128)):
            vv = v[m]
            damp = (vv / (vv + EPS)).mean()
            print(f"   {name:10s}: 要素 {int(m.sum()):5d}（{float(m.float().mean()) * 100:4.1f}%） √v median {float(vv.median()):.2e} "
                  f"eps 未満 {float((vv < EPS).float().mean()) * 100:5.1f}%  更新の倍率 √v/(√v+eps) 平均 {float(damp):.3f}")
        c = torch.corrcoef(torch.stack([torch.log(rate).flatten(), torch.log(v.flatten().clamp_min(1e-30))]))[0, 1]
        print(f"   log(dt·|A|) と log(√v) の相関 {float(c):+.3f}")
        for other in ("in_proj.weight", "dt_proj.weight", "dt_proj.bias", "x_proj.weight", "out_proj.weight", "D"):
            vo = st[idx[pre + other]]["exp_avg_sq"].float().sqrt()
            print(f"   {other:16s} √v median {float(vo.median()):.2e} RMS {float(vo.pow(2).mean().sqrt()):.2e} eps 未満 {float((vo < EPS).float().mean()) * 100:5.1f}% "
                  f"更新の倍率 平均 {float((vo / (vo + EPS)).mean()):.3f}")


if __name__ == "__main__":
    main()
