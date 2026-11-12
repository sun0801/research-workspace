"""Figures and summary table for compute.py (2026-11-12).

  python fig.py --data data [--fields .../fields.pt]
  # writes 01-arrows-median.png, 02-arrows-p90.png, 03-coherence.png, 04-masks-median.png, 05-iou.png, data/summary.md

Figures carry only what is plotted (titles, axes, legends); the reading of each figure is in the experiment log
and the MTG materials. Examples (chosen by rule, not by eye): per speed stratum, among (object, pair) with
>= 40 target cells, the pair at the 50th (01, 04) / 90th (02) percentile of the A-b (softmax) edge_gt1.
Aggregation: per object, mean over its pairs; per stratum, mean over objects (95% bootstrap interval over
objects, 10,000 resamples, seed 123).
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib import rcParams
from matplotlib.lines import Line2D
from PIL import Image

rcParams["font.family"] = "Noto Sans CJK JP"
ROOT = Path("/mnt/HDD10TB-2/aburatani/dataset/MOSE-v1-data/MOSE_release/train")
RES, CELL, CELLS = 1024, 16, 64
METHODS = ("softmax", "argmax", "raft", "identity")
LABEL = {"softmax": "A-b（softmax τ=0.02）", "argmax": "類似度最大（argmax）", "raft": "RAFT（参照）",
         "identity": "同じ位置（identity）"}
COLOR = {"softmax": "#2a78d6", "argmax": "#eb6834", "raft": "#1baf7a", "identity": "#eda100"}
OK, BAD = "#2a78d6", "#eb6834"
STRATA = ("slow", "mid", "fast")
SNAME = {"slow": "遅い", "mid": "中くらい", "fast": "速い", "all": "全体"}
METRICS = (("edge_gt1", "隣のマスと1マス以上ずれる割合", "辺の割合"),
           ("fold", "移動先が折り返す（交差する）割合", "マスの割合"),
           ("iou", "運んだマスクと正解のIoU", "IoU"))


def frame_paths(video):
    """Frame paths sorted by number (skips macOS ._ files), same order as video_frames of the stage-0 code."""
    return sorted((p for p in (ROOT / "JPEGImages" / video).glob("*.jpg") if p.stem.isdigit()), key=lambda p: int(p.stem))


def image(path):
    return np.asarray(Image.open(path).convert("RGB").resize((RES, RES), Image.Resampling.BILINEAR))


def crop_box(f):
    m = (f["tgt"] | f["prev_lab"]).numpy()
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min() - 3, ys.max() + 4, xs.min() - 3, xs.max() + 4
    side = max(y1 - y0, x1 - x0, 12)
    cy, cx = (y0 + y1) / 2, (x0 + x1) / 2
    y0 = int(np.clip(round(cy - side / 2), 0, CELLS - side)); x0 = int(np.clip(round(cx - side / 2), 0, CELLS - side))
    return y0, y0 + side, x0, x0 + side


def outline(ax, mask, color, lw=1.6):
    ax.contour(np.kron(mask.numpy().astype(float), np.ones((CELL, CELL))), levels=[0.5], colors=[color],
               linewidths=lw)


def local_disc(u, tgt):
    """Per target cell: max ||u(p) - u(p')|| over 4-neighbours in the target."""
    u = u.float()
    out = torch.zeros(CELLS, CELLS)
    for dy, dx in ((0, 1), (1, 0)):
        a = tgt[: CELLS - dy, : CELLS - dx] & tgt[dy:, dx:]
        d = (u[:, : CELLS - dy, : CELLS - dx] - u[:, dy:, dx:]).norm(dim=0) * a
        out[: CELLS - dy, : CELLS - dx] = torch.maximum(out[: CELLS - dy, : CELLS - dx], d)
        out[dy:, dx:] = torch.maximum(out[dy:, dx:], d)
    return out


def arrows(ax, u, tgt, step):
    disc = local_disc(u, tgt)
    ys, xs = np.nonzero(tgt.numpy())
    keep = (ys % step == 0) & (xs % step == 0)
    ys, xs = ys[keep], xs[keep]
    uy, ux = u[0].float().numpy()[ys, xs], u[1].float().numpy()[ys, xs]
    cx, cy = (xs + 0.5) * CELL, (ys + 0.5) * CELL
    bad = disc.numpy()[ys, xs] > 1
    for sel, col in ((~bad, OK), (bad, BAD)):
        # from where the state comes (t-1, p + u) to the cell p at t
        ax.quiver(cx[sel] + ux[sel] * CELL, cy[sel] + uy[sel] * CELL, -ux[sel] * CELL, -uy[sel] * CELL,
                  color=col, angles="xy", scale_units="xy", scale=1, width=0.006, headwidth=3.5,
                  headlength=4, minlength=0.1)
    return float(bad.mean()) if len(bad) else 0.0


def pick(rows, st, pct):
    cand = sorted([r for r in rows if r["stratum"] == st and r["cells"] >= 40 and r["softmax"]["edge_gt1"] is not None],
                  key=lambda r: r["softmax"]["edge_gt1"])
    return cand[min(len(cand) - 1, int(round(pct / 100 * (len(cand) - 1))))]


def framed(ax, ext):
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_xticks([]); ax.set_yticks([])


def example_setup(rows, fields, pct, st):
    r = pick(rows, st, pct)
    f = fields[(r["video"], r["object"], r["t"])]
    paths = frame_paths(r["video"])
    y0, y1, x0, x1 = crop_box(f)
    return r, f, image(paths[r["t"] - 1]), image(paths[r["t"]]), (x0 * CELL, x1 * CELL, y1 * CELL, y0 * CELL), y1 - y0


def arrows_figure(rows, fields, pct, out):
    """Per stratum: the displacement of every target cell (A-b, RAFT) on frame t."""
    fig, axes = plt.subplots(3, 2, figsize=(8.4, 12.6))
    for i, st in enumerate(STRATA):
        r, f, _, cur, ext, side = example_setup(rows, fields, pct, st)
        step = 1 if side <= 24 else 2 if side <= 44 else 3
        for j, m in enumerate(("softmax", "raft")):
            ax = axes[i, j]
            ax.imshow(cur, alpha=0.45)
            arrows(ax, f["u"][m], f["tgt"], step)
            framed(ax, ext)
            if i == 0:
                ax.set_title("A-b" if m == "softmax" else "RAFT", fontsize=14)
        axes[i, 0].set_ylabel(SNAME[st], fontsize=14)
    handles = [Line2D([], [], color=OK, lw=2.5, label="隣のマスとの差 ≤ 1マス"),
               Line2D([], [], color=BAD, lw=2.5, label="隣のマスとの差 > 1マス")]
    fig.legend(handles=handles, loc="lower center", ncol=2, fontsize=12, frameon=False)
    fig.subplots_adjust(left=0.07, right=0.99, top=0.96, bottom=0.05, hspace=0.06, wspace=0.04)
    fig.savefig(out, dpi=110)
    plt.close(fig)


def masks_figure(rows, fields, pct, out):
    """Per stratum: frames t-1 and t with the GT outline, and the t-1 mask moved by A-b / RAFT."""
    gt = "#c71f7a"
    fig, axes = plt.subplots(3, 4, figsize=(15, 11.6))
    for i, st in enumerate(STRATA):
        r, f, prev, cur, ext, _ = example_setup(rows, fields, pct, st)
        panels = [("t−1", prev, f["prev_lab"], None), ("t", cur, f["tgt"], None),
                  ("A-bで運んだマスク", cur, f["tgt"], "softmax"), ("RAFTで運んだマスク", cur, f["tgt"], "raft")]
        for j, (ttl, img, lab, m) in enumerate(panels):
            ax = axes[i, j]
            if m is None:
                ax.imshow(img)
            else:
                ax.imshow(img, alpha=0.45)
                heat = np.kron(f["moved"][m].float().clamp(0, 1).numpy(), np.ones((CELL, CELL)))
                im = ax.imshow(np.ma.masked_less(heat, 0.05), cmap="Blues", vmin=0, vmax=1, alpha=0.8)
            outline(ax, lab, gt, 1.8)
            framed(ax, ext)
            if i == 0:
                ax.set_title(ttl, fontsize=14)
        axes[i, 0].set_ylabel(SNAME[st], fontsize=14)
    fig.legend(handles=[Line2D([], [], color=gt, lw=2.5, label="正解のマスク（輪郭）")], loc="lower left",
               bbox_to_anchor=(0.05, 0.03), fontsize=12, frameon=False)
    cax = fig.add_axes([0.55, 0.06, 0.3, 0.012])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.set_label("運んだマスクの値（マスの被覆率、0〜1）", fontsize=11)
    fig.subplots_adjust(left=0.04, right=0.99, top=0.96, bottom=0.11, hspace=0.06, wspace=0.04)
    fig.savefig(out, dpi=110)
    plt.close(fig)


def bars(ax, table, key, methods, title, ylabel):
    groups = STRATA + ("all",)
    width = 0.8 / len(methods)
    for j, m in enumerate(methods):
        xs = np.arange(len(groups)) + (j - (len(methods) - 1) / 2) * width
        mean = [table[(g, m, key)][0] for g in groups]
        lo = [table[(g, m, key)][0] - table[(g, m, key)][1] for g in groups]
        hi = [table[(g, m, key)][2] - table[(g, m, key)][0] for g in groups]
        ax.bar(xs, mean, width - 0.02, color=COLOR[m], label=LABEL[m], edgecolor="white", linewidth=1)
        ax.errorbar(xs, mean, yerr=[lo, hi], fmt="none", ecolor="#555555", elinewidth=1, capsize=2)
    ax.set_xticks(np.arange(len(groups)), [SNAME[g] for g in groups], fontsize=12)
    ax.set_xlabel("物体の速さ", fontsize=11)
    ax.set_title(title, fontsize=13)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.grid(axis="y", color="#dddddd", lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def coherence_figure(table, out):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    methods = ("softmax", "argmax", "raft")
    bars(axes[0], table, "edge_gt1", methods, "隣のマスと移動が1マス以上違う辺の割合", "割合")
    bars(axes[1], table, "fold", methods, "移動先が折り返す（交差する）マスの割合", "割合")
    axes[1].legend(fontsize=11, frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def iou_figure(table, out):
    fig, ax = plt.subplots(figsize=(8, 4.8))
    bars(ax, table, "iou", ("softmax", "argmax", "raft", "identity"), "運んだマスクと正解のマスクのIoU", "IoU")
    ax.set_ylim(0, 1)
    ax.legend(fontsize=10.5, frameon=False, loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.0))
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.arange(0, 1.01, 0.2))
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    plt.close(fig)


def aggregate(rows):
    by_obj = defaultdict(list)
    for r in rows:
        by_obj[(r["video"], r["object"])].append(r)
    rng = np.random.default_rng(123)
    table = {}
    for st in STRATA + ("all",):
        objs = [v for v in by_obj.values() if st == "all" or v[0]["stratum"] == st]
        for m in METHODS:
            for key, _, _ in METRICS + (("edge_disc", "", ""), ("epe_raft", "", "")):
                vals = []
                for v in objs:
                    xs = [r[m][key] for r in v if r[m][key] is not None]
                    if xs:
                        vals.append(np.mean(xs))
                vals = np.array(vals)
                boot = rng.choice(vals, (10000, len(vals))).mean(1) if len(vals) else np.array([np.nan])
                table[(st, m, key)] = (vals.mean() if len(vals) else np.nan, *np.percentile(boot, [2.5, 97.5]), len(vals))
        vals = []
        for v in objs:
            xs = [r["softmax"]["dup15"] for r in v if r["softmax"]["dup15"] is not None]
            if xs:
                vals.append(np.mean(xs))
        table[(st, "softmax", "dup15")] = (np.mean(vals), np.nan, np.nan, len(vals))
    return table


def summary_md(rows, table, out):
    lines = [f"(object, pair) rows: {len(rows)}; objects: {table[('all', 'softmax', 'iou')][3]}", ""]
    keys = (("edge_gt1", "隣と1マス以上ずれる辺の割合"), ("edge_disc", "隣との差の平均（マス）"),
            ("fold", "折り返しの割合"), ("iou", "運んだマスクのIoU"), ("epe_raft", "RAFTとの差（マス）"))
    for key, name in keys:
        lines += [f"### {name}（{key}）", "", "| 方式 | " + " | ".join(SNAME[g] for g in STRATA + ("all",)) + " |",
                  "|---|" + "---|" * 4]
        for m in METHODS:
            cells = []
            for g in STRATA + ("all",):
                v, lo, hi, _ = table[(g, m, key)]
                cells.append(f"{v:.3f} [{lo:.3f}, {hi:.3f}]")
            lines.append(f"| {LABEL[m]} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["### 前景の複製（softmax、t−1の物体のマスのうち列の和>1.5の割合、物体平均）", "",
              "| " + " | ".join(SNAME[g] for g in STRATA + ("all",)) + " |", "|" + "---|" * 4,
              "| " + " | ".join(f"{table[(g, 'softmax', 'dup15')][0]:.3f}" for g in STRATA + ("all",)) + " |", ""]
    out.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, default=Path("data"))
    ap.add_argument("--fields", type=Path,
                    default=Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/latent_corr/shape_coherence/20261112/fields.pt"))
    args = ap.parse_args()
    rows = [json.loads(l) for l in (args.data / "pairs.jsonl").read_text().splitlines()]
    rows = [r for r in rows if r["stratum"] is not None]
    fields = torch.load(args.fields, weights_only=False)
    here = Path(__file__).resolve().parent
    table = aggregate(rows)
    summary_md(rows, table, args.data / "summary.md")
    coherence_figure(table, here / "03-coherence.png")
    iou_figure(table, here / "05-iou.png")
    arrows_figure(rows, fields, 50, here / "01-arrows-median.png")
    arrows_figure(rows, fields, 90, here / "02-arrows-p90.png")
    masks_figure(rows, fields, 50, here / "04-masks-median.png")

if __name__ == "__main__":
    main()
