"""B案用: 活性のチャネル別最大値の図（スライド用に文字を大きくした版）．正本 2026-11-13-act-channel-absmax.png と同じ計算（quantization_handson の plot_act_dist.channel_absmax）を CPU で再実行する．
実行: cd /mnt/HDD10TB-2/aburatani/quantization_handson && .venv/bin/python <このファイル>"""
import os
import sys

sys.path.insert(0, "/mnt/HDD10TB-2/aburatani/quantization_handson")
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from plot_act_dist import channel_absmax  # noqa: E402
from quant.experiment import load_fp32  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), "experiments", "figures",
                   "2026-11-14-act-channel-absmax-large.png")
plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["font.size"] = 17
vit = load_fp32("deit_tiny", "cpu")
res = load_fp32("resnet18", "cpu")
items = [("DeiT-Tiny qkv 入力\n（LayerNorm 後）", channel_absmax(vit, "blocks.11.attn.qkv", "deit_tiny", "cpu", -1)),
         ("DeiT-Tiny fc2 入力\n（GELU 後）", channel_absmax(vit, "blocks.0.mlp.fc2", "deit_tiny", "cpu", -1)),
         ("ResNet18 conv 入力\n（ReLU 後）", channel_absmax(res, "layer4.1.conv2", "resnet18", "cpu", 1))]
fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9))
for ax, (title, v) in zip(axes, items):
    ax.bar(range(len(v)), v.sort(descending=True).values.numpy(), width=1.0)
    ax.set_title(title, fontsize=17)
    ax.set_xlabel("チャネル（大きい順）")
    ax.spines[["top", "right"]].set_visible(False)
    print(title.replace("\n", " "), f"max {v.max():.2f} median {v.median():.2f} ratio {v.max() / v.median():.1f}")
axes[0].set_ylabel("max |x|")
plt.tight_layout()
plt.savefig(OUT, dpi=150, facecolor="white")
