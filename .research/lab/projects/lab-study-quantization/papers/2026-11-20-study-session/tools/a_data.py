"""案A用の計算例データ（説明用の計算例）を作る。ハンズオンの quant.core を使う。CPUのみ。
使い方: cd quantization_handson && CUDA_VISIBLE_DEVICES= .venv/bin/python <this file> out.json
"""
import json
import sys

import torch

sys.path.insert(0, "/mnt/HDD10TB-2/aburatani/quantization_handson")
from quant.core import calc_qparams, dequantize, fake_quant, quantize  # noqa: E402

out = {}
# 演習①と同じ設定（seed 0, 4096個, 外れ値20）
for tag, outl in (("plain", 0.0), ("outlier20", 20.0)):
    torch.manual_seed(0)
    x = torch.randn(4096)
    if outl:
        x[0] = outl
    rows = []
    for bits in (8, 6, 4, 3, 2):
        for sym in (True, False):
            s, z, qmin, qmax = calc_qparams(x.min(), x.max(), bits, sym)
            xh = dequantize(quantize(x, s, z, qmin, qmax), s, z)
            mse = (xh - x).pow(2).mean()
            sq = 10 * torch.log10(x.pow(2).mean() / mse)
            rows.append(dict(bits=bits, sym=sym, scale=s.item(), zero=int(z.item()), mse=mse.item(), sqnr=sq.item()))
    out[tag] = rows
# 丸め誤差とクリップ誤差: 範囲を[-c, c]に絞る（4bit対称）。N(0,1) 4096個（seed 0）
torch.manual_seed(0)
x = torch.randn(4096)
cs, tot, rnd, clip = [], [], [], []
for c in torch.linspace(0.5, 4.5, 41).tolist():
    s, z, qmin, qmax = calc_qparams(torch.tensor(-c), torch.tensor(c), 4, True)
    xh = fake_quant(x, s, z, qmin, qmax)
    inside = x.abs() <= c
    e = (xh - x).pow(2)
    cs.append(c)
    tot.append(e.mean().item())
    clip.append((e * (~inside)).sum().item() / x.numel())
    rnd.append((e * inside).sum().item() / x.numel())
out["tradeoff"] = dict(c=cs, total=tot, rounding=rnd, clipping=clip)
# 較正3方法の計算例: 合成データ（99.9%はN(0,1)，0.1%はN(0,6^2)），4bit非対称，seed 0
torch.manual_seed(0)
n = 100000
x = torch.randn(n)
k = n // 1000
x[:k] = torch.randn(k) * 6
lo_mm, hi_mm = x.min().item(), x.max().item()
q = torch.quantile(x[:16_000_000], torch.tensor([1e-4, 1 - 1e-4])).tolist()
best, be = None, 1e9
for r in torch.linspace(0.1, 1.0, 91).tolist():
    qp = calc_qparams(torch.tensor(lo_mm * r), torch.tensor(hi_mm * r), 4, False)
    e = (fake_quant(x, *qp) - x).pow(2).mean().item()
    if e < be:
        best, be = r, e


def mse_of(lo, hi):
    qp = calc_qparams(torch.tensor(lo), torch.tensor(hi), 4, False)
    return (fake_quant(x, *qp) - x).pow(2).mean().item()


out["calib"] = dict(
    hist=torch.histc(x, bins=120, min=-25, max=25).tolist(),
    minmax=[lo_mm, hi_mm], percentile=[min(q[0], 0.0), max(q[1], 0.0)], mse=[lo_mm * best, hi_mm * best],
    mse_ratio=best,
    err=dict(minmax=mse_of(lo_mm, hi_mm), percentile=mse_of(q[0], q[1]), mse=be))
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out["calib"]["err"]), out["calib"]["minmax"], out["calib"]["percentile"], out["calib"]["mse"])
