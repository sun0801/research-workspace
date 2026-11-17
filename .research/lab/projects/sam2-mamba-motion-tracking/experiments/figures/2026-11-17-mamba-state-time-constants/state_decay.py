"""学習済みV3（PyramidAdapter）の重みから、Mambaのstateが1ステップでどれだけ残るかを読む（CPUだけ）。

残る割合 = exp(-dt * |A|)。dt は softplus(dt_proj.bias) だけを使う（入力に依存する分 dt_proj.weight @ x は含めない）。
並列（マスごと）では 1ステップ = 1フレーム、シリアルでは 1ステップ = 1マス。

使い方: CUDA_VISIBLE_DEVICES="" python state_decay.py <checkpoint.pt> [<checkpoint.pt> ...]
"""
import math
import sys

import torch
import torch.nn.functional as F

KS = (1, 4, 8, 16, 64, 100, 256, 1024, 4096, 16384, 65536)


def stats(A_log, dt_bias, tag):
    A = torch.exp(A_log.float())  # (D, N)
    dt = F.softplus(dt_bias.float())  # (D,)
    rate = dt[:, None] * A
    hl = math.log(2) / rate
    q = torch.quantile(hl.flatten(), torch.tensor([0.0, 0.1, 0.5, 0.9, 1.0]))
    print(f"{tag}: dt min/med/max {dt.min():.4f}/{dt.median():.4f}/{dt.max():.4f} | "
          f"|A| min/max {A.min():.2f}/{A.max():.2f} | half-life(steps) min/10%/50%/90%/max "
          + "/".join(f"{v:.1f}" for v in q))
    for k in KS:
        r = torch.exp(-rate * k)
        print(f"    k={k:>6}: mean {r.mean():.4f}  >0.5: {(r > 0.5).float().mean() * 100:5.1f}%  max {r.max():.3g}")


def main():
    for name in sys.argv[1:]:
        ck = torch.load(name, map_location="cpu", weights_only=False)
        sd = ck["model"]
        print("==", name, "epoch", ck.get("epoch"))
        for lv in ("64", "128", "256"):
            pre = f"temporal_mamba_adapter.cells.{lv}.mamba."
            stats(sd[pre + "A_log"], sd[pre + "dt_proj.bias"], f"trained L{lv}")
            A0 = torch.log(torch.arange(1, sd[pre + "A_log"].shape[1] + 1).float())[None]
            print(f"    A_log と初期値(log 1..16)の差: max {float((sd[pre + 'A_log'] - A0).abs().max()):.4f}, "
                  f"mean {float((sd[pre + 'A_log'] - A0).abs().mean()):.4f}")
    # 初期値の参照（mamba_simple の既定: dt は [1e-3, 1e-1] の対数一様、A = 1..16）
    torch.manual_seed(0)
    for D, lv in ((512, "64"), (128, "128"), (64, "256")):
        dt = torch.exp(torch.rand(D) * (math.log(0.1) - math.log(0.001)) + math.log(0.001)).clamp(min=1e-4)
        inv = dt + torch.log(-torch.expm1(-dt))
        A_log = torch.log(torch.arange(1, 17).float())[None].repeat(D, 1)
        stats(A_log, inv, f"init    L{lv}")


if __name__ == "__main__":
    main()
