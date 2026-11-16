"""活性チャネル分布の図を，スライド上で16pt相当に読める大きさで描き直す（CPU，ハンズオンの関数を利用）．"""
import os
import sys

sys.path.insert(0, "/mnt/HDD10TB-2/aburatani/quantization_handson")
os.chdir("/mnt/HDD10TB-2/aburatani/quantization_handson")
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

from plot_act_dist import channel_absmax  # noqa: E402
from quant.experiment import load_fp32  # noqa: E402

for f in font_manager.findSystemFonts():
    if "NotoSansCJK-Regular" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "font.size": 15, "axes.spines.top": False, "axes.spines.right": False})
OUT = sys.argv[1]
if os.path.exists(OUT):
    sys.exit("exists: " + OUT)
vit, res = load_fp32("deit_tiny", "cpu"), load_fp32("resnet18", "cpu")
items = [("DeiT qkv入力（LN後）", channel_absmax(vit, "blocks.11.attn.qkv", "deit_tiny", "cpu", -1)),
         ("DeiT fc2入力（GELU後）", channel_absmax(vit, "blocks.0.mlp.fc2", "deit_tiny", "cpu", -1)),
         ("ResNet18 layer4.1.conv2入力", channel_absmax(res, "layer4.1.conv2", "resnet18", "cpu", 1))]
fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.9))
for ax, (title, v) in zip(axes, items):
    ax.bar(range(len(v)), v.sort(descending=True).values.numpy(), width=1.0, color="#1f77b4")
    ax.set_title(title, fontsize=15)
    ax.set_xlabel("チャネル（大きい順）")
    print(f"{title}: max {v.max():.2f} median {v.median():.2f} ratio {v.max() / v.median():.2f}")
axes[0].set_ylabel("チャネルごとの max |x|")
fig.tight_layout()
fig.savefig(OUT, dpi=150)
