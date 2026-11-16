"""案A用: DeiT-Tiny の活性のチャネルごとの最大値（2層，文字を大きく）。quantization_handson の .venv で CPU 実行。
使い方: cd quantization_handson && CUDA_VISIBLE_DEVICES= .venv/bin/python <this> <out.png>
"""
import sys

sys.path.insert(0, "/mnt/HDD10TB-2/aburatani/quantization_handson")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from plot_act_dist import channel_absmax  # noqa: E402
from quant.experiment import load_fp32  # noqa: E402

plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 18
vit = load_fp32("deit_tiny", "cpu")
items = [("blocks.11.attn.qkv（LayerNorm後）", "blocks.11.attn.qkv"), ("blocks.0.mlp.fc2（GELU後）", "blocks.0.mlp.fc2")]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
for ax, (t, n) in zip(axes, items):
    v = channel_absmax(vit, n, "deit_tiny", "cpu", -1)
    ax.bar(range(len(v)), v.sort(descending=True).values.numpy(), width=1.0)
    ax.set_title(f"DeiT-Tiny {t}", fontsize=16)
    ax.set_xlabel("チャネル（大きい順）")
    ax.set_ylabel("max |x|")
    print(t, f"max {v.max():.2f} median {v.median():.2f} ratio {v.max() / v.median():.1f}")
plt.tight_layout()
plt.savefig(sys.argv[1], dpi=150)
