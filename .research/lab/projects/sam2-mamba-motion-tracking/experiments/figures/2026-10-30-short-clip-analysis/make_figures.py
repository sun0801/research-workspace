"""短区間学習（A〜E）の結果の分析図。10/30 MTG資料用。

入力はすべて SAM2 repo `/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs/` の下:
- val（125動画・313対象）の対象ごとの結果: 各runの `eval/tuning/<条件>/objects.jsonl`、F0は `mose_temporal_mamba_20260930/tuning/F0_step_002789`
- 対応つき比較: `short_clip/stage4_p0/paired_summary.json`（`training.mose_adapter_summary compare`）
- 学習中の記録（Cometに送った値と同じもの）: 各runの `samples.jsonl`（1更新ごとのloss）、`val_history.jsonl`（val-25）
- 固定した200区間でのloss: `short_clip/diag_loss_curve/per_clip.jsonl`（F0・A・B・C）、`short_clip/diag_loss_curve_p0/per_clip.jsonl`（F0・P0・D・E）

SAM2 repo の `.venv-sam2/bin/python -I make_figures.py` で実行する。
"""
import json
import statistics as st
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.transforms import blended_transform_factory

plt.rcParams["font.family"] = "Noto Sans CJK JP"
OUT = Path(__file__).resolve().parent
RUNS = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2/runs")
SC = RUNS / "short_clip"
RUN = {
    "A": SC / "A_v3_nockpt/20261027T154219+0900_1895c45",
    "B": SC / "B_decoder/20261027T154800+0900_1895c45",
    "C": SC / "C_v3_decoder/20261027T154143+0900_1895c45",
    "D": SC / "D_p0_decoder/20261029T164918+0900_30afc59",
    "E": SC / "E_p0_v3_decoder/20261029T174247+0900_30afc59",
}
EVAL = {"F0": RUNS / "mose_temporal_mamba_20260930/tuning/F0_step_002789", "P0": SC / "P0/eval/tuning/P0"}
for c in ["A", "B", "C", "D", "E", "E-reset1"]:
    EVAL[c] = RUN[c[0]] / "eval/tuning" / c
OUTLIER = "e7b34ab6"  # E と E-reset1・D の差のほとんどを1対象で生む動画

# 既定の参照パレット（dataviz skill, references/palette.md）の順番どおり。色は条件に固定する
COLOR = {"A": "#2a78d6", "B": "#eb6834", "C": "#1baf7a", "D": "#eda100", "E": "#e87ba4"}
MARK = {"A": "o", "B": "s", "C": "^", "D": "D", "E": "v"}
LABEL = {"A": "A（F0→V3）", "B": "B（F0→デコーダ）", "C": "C（F0→V3＋デコーダ）",
         "D": "D（P0→デコーダ）", "E": "E（P0→V3＋デコーダ）"}
INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def style(ax):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def load_objects(c):
    return {(r["video"], r["object_id"]): r for r in map(json.loads, open(EVAL[c] / "objects.jsonl"))}


def bootstrap_pp(a, b, exclude=None):
    """mose_adapter_summary と同じ方法（動画単位、10,000回、seed 123）。exclude の動画を除いて計算する。"""
    oa, ob = load_objects(a), load_objects(b)
    per = {}
    for k in oa:
        if k[0] != exclude:
            per.setdefault(k[0], [[], []])
            per[k[0]][0].append(oa[k]["J&F"])
            per[k[0]][1].append(ob[k]["J&F"])
    v = np.array([np.mean(x) - np.mean(y) for x, y in per.values()])
    rng = np.random.default_rng(123)
    means = v[rng.integers(0, len(v), size=(10000, len(v)))].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return v.mean() * 100, lo * 100, hi * 100


# ---------------------------------------------------------------- 01 forest
def fig_forest():
    comp = json.loads((SC / "stage4_p0/paired_summary.json").read_text())["comparisons"]

    def pp(key):
        r = comp[key]["J&F"]
        return r["mean_pp"], *r["ci95_pp"]

    groups = [
        ("学習の効果（H6）", [("D − P0", pp("D-P0"), False), ("E − P0", pp("E-P0"), False)]),
        ("Mambaの効果（H5）", [("E − D", pp("E-D"), False),
                            (f"E − D（{OUTLIER}を除く）", bootstrap_pp("E", "D", OUTLIER), True)]),
        ("stateの記憶（H7）", [("E − E-reset1（毎フレームreset）", pp("E-E-reset1"), False),
                           (f"E − E-reset1（{OUTLIER}を除く）", bootstrap_pp("E", "E-reset1", OUTLIER), True)]),
        ("初期値の違い（参考）", [("D − B（P0とF0、デコーダだけ）", pp("D-B"), False),
                            ("E − C（P0とF0、V3＋デコーダ）", pp("E-C"), False)]),
    ]
    rows = []
    for title, items in groups:
        rows.append(("h", title))
        rows += [("i", *it) for it in items]

    fig, ax = plt.subplots(figsize=(8.4, 5.0), dpi=200)
    fig.patch.set_facecolor(BG)
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.axvline(0, color=MUTED, lw=1, ls="--")
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    yt, yl = [], []
    for i, row in enumerate(rows):
        y = -i
        if row[0] == "h":
            ax.text(-0.62, y, row[1], fontsize=9, fontweight="bold", color=INK, va="center", transform=tr)
            continue
        _, label, (m, lo, hi), sub = row
        ax.plot([lo, hi], [y, y], color=COLOR["A"], lw=2, solid_capstyle="round", alpha=0.55 if sub else 1)
        ax.plot(m, y, "o", ms=8, mfc=BG if sub else COLOR["A"], mec=COLOR["A"], mew=2)
        ax.text(1.01, y, f"{m:+.2f} [{lo:+.2f}, {hi:+.2f}]", fontsize=8, color=INK, va="center", transform=tr)
        yt.append(y)
        yl.append(label)
    ax.set_yticks(yt, yl, fontsize=8.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("J&Fの差（ポイント）、95%区間は動画単位のpaired bootstrap", fontsize=8.5, color=MUTED)
    fig.text(0.01, 0.96, "P0から始めたD・E：学習は効いたが、Mambaと記憶の効果は0を含む", fontsize=10.5, color=INK, va="top")
    fig.text(0.01, 0.01, f"val 125動画・313対象、RTX A4000。白抜きは動画{OUTLIER}（1対象でJ&Fが条件により0.07〜0.78）を除いた値。"
             "source: SAM2 repo runs/short_clip/stage4_p0/paired_summary.json",
             fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.36, right=0.80, top=0.86, bottom=0.14)
    fig.savefig(OUT / "01-p0-val-paired-diff.png", facecolor=BG)


# ---------------------------------------------------------------- 02 by frame position
BUCKETS = [(1, 8), (9, 32), (33, 100), (101, 10**6)]


def by_position(c):
    acc = [[] for _ in BUCKETS]
    for r in load_objects(c).values():
        for m in r["frame_metrics"]:
            t = m["frame_id"] - r["first_frame"]
            for i, (lo, hi) in enumerate(BUCKETS):
                if lo <= t <= hi:
                    acc[i].append((m["J"] + m["F"]) / 2)
    return np.array([np.mean(a) for a in acc]) * 100, [len(a) for a in acc]


def fig_position():
    f0, n = by_position("F0")
    x = np.arange(len(BUCKETS))
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_facecolor(BG)
    style(ax)
    ax.axhline(0, color=MUTED, lw=1)
    p0 = by_position("P0")[0] - f0
    ax.plot(x, p0, color=MUTED, lw=2, ls="--", marker="o", ms=6, label="P0（配布されたSAM2.1）")
    ax.annotate("P0", (x[-1], p0[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    for c in ["A", "B", "D", "E"]:
        y = by_position(c)[0] - f0
        ax.plot(x, y, color=COLOR[c], lw=2, marker=MARK[c], ms=7, mec=BG, mew=1.5, label=LABEL[c])
        ax.annotate(c, (x[-1], y[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    ax.set_xticks(x, [f"{lo}〜{hi}" if hi < 10**6 else f"{lo}〜" for lo, hi in BUCKETS], fontsize=8.5)
    ax.set_xlabel("boxを与えたフレームからの経過フレーム数（括弧内は全条件共通の採点フレーム数）", fontsize=8.5, color=MUTED,
                  labelpad=16)
    for i, k in enumerate(n):
        ax.text(x[i], -0.11, f"({k:,})", fontsize=7, color=MUTED, ha="center", transform=blended_transform_factory(ax.transData, ax.transAxes))
    ax.set_ylabel("F0とのJ&Fの差（ポイント）", fontsize=8.5, color=MUTED)
    ax.set_xlim(-0.3, len(BUCKETS) - 0.6)
    ax.legend(fontsize=7.5, frameon=False, loc="lower left")
    ax.set_title("学習の効果は後半のフレームで大きい（最初の8フレームはほぼ同じ）", fontsize=10.5, color=INK, loc="left")
    fig.text(0.01, 0.01, "val 313対象の全採点フレームの平均。Eの101〜の低下は主に動画e7b34ab6の1対象。\n"
             "source: 各条件の eval/tuning/*/objects.jsonl の frame_metrics", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.10, right=0.95, top=0.90, bottom=0.24)
    fig.savefig(OUT / "02-jf-gain-by-frame-position.png", facecolor=BG)


# ---------------------------------------------------------------- 03 training log (Comet)
def fig_training_log():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.6), dpi=200)
    fig.patch.set_facecolor(BG)
    for ax in (a1, a2):
        style(ax)
    for c in "ABCDE":
        ep = {}
        for r in map(json.loads, open(RUN[c] / "samples.jsonl")):
            ep.setdefault(r["epoch"], []).append(r["loss"])
        e = sorted(ep)
        y = [st.median(ep[k]) for k in e]
        a1.plot(np.array(e) + 1, y, color=COLOR[c], lw=2, marker=MARK[c], ms=4.5, mec=BG, mew=1, label=LABEL[c])
        vh = [json.loads(l) for l in open(RUN[c] / "val_history.jsonl")]
        a2.plot([v["step"] / 1121 for v in vh], [v["val_J&F"] for v in vh], color=COLOR[c], lw=2, marker=MARK[c], ms=5,
                mec=BG, mew=1, label=LABEL[c])
    a1.set_xlabel("epoch（1 epoch = 1,121更新）", fontsize=8.5, color=MUTED)
    a1.set_ylabel("学習lossの中央値（epochごと）", fontsize=8.5, color=MUTED)
    a1.set_title("(a) 学習loss：全条件が同じ動きで上下（区間の難しさ）", fontsize=9.5, color=INK, loc="left")
    a2.set_xlabel("epoch", fontsize=8.5, color=MUTED)
    a2.set_ylabel("val-25のJ&F", fontsize=8.5, color=MUTED)
    a2.set_title("(b) val-25：25動画では上下が大きく判断に使えない", fontsize=9.5, color=INK, loc="left")
    h, l = a2.get_legend_handles_labels()
    fig.legend(h, l, fontsize=7.5, frameon=False, loc="lower center", ncol=5, bbox_to_anchor=(0.5, 0.06))
    fig.text(0.01, 0.01, "Cometに送った値と同じ（手元の記録から再計算）。A〜Eは全更新で同じ区間・同じプロンプトを見る（seed 123）。"
             "source: 各runの samples.jsonl・val_history.jsonl", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.27, wspace=0.22)
    fig.savefig(OUT / "03-training-log.png", facecolor=BG)


# ---------------------------------------------------------------- 04 fixed-clip loss
def fig_fixed_clip():
    rows = [json.loads(l) for f in ("diag_loss_curve", "diag_loss_curve_p0") for l in open(SC / f / "per_clip.jsonl")]
    f0 = np.array(next(r["mix"] for r in rows if r["model"] == "F0"))
    p0 = np.array(next(r["mix"] for r in rows if r["model"] == "P0"))
    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
    fig.patch.set_facecolor(BG)
    style(ax)
    ax.axhline(0, color=MUTED, lw=1)
    ax.plot([0], [np.median(p0 - f0)], "o", color=MUTED, ms=7)
    ax.annotate("P0", (0, np.median(p0 - f0)), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    for c in "ABCDE":
        pts = sorted((r["epoch"], np.median(np.array(r["mix"]) - f0)) for r in rows if r["model"] == c)
        if not pts:
            continue
        start = 0.0 if c in "ABC" else np.median(p0 - f0)
        e = [0] + [p[0] for p in pts]
        y = [start] + [p[1] for p in pts]
        ax.plot(e, y, color=COLOR[c], lw=2, marker=MARK[c], ms=5, mec=BG, mew=1, label=LABEL[c])
        ax.annotate(c, (e[-1], y[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8, color=INK, va="center")
    ax.set_xlabel("epoch（0は初期値：A〜CはF0、D・EはP0）", fontsize=8.5, color=MUTED)
    ax.set_ylabel("F0との差の中央値（同じ区間どうし）", fontsize=8.5, color=MUTED)
    ax.legend(fontsize=7.5, frameon=False, loc="upper right")
    ax.set_title("固定した200区間のloss：P0から始めると2 epochでF0の水準、その後はほぼ横ばい", fontsize=10, color=INK, loc="left")
    fig.text(0.01, 0.01, "trainの動画のうち学習に使っていない8フレームの区間200個、学習と同じプロンプトの混合（mix）。RTX PRO 4500。\n"
             "source: runs/short_clip/diag_loss_curve*/per_clip.jsonl", fontsize=6.5, color=MUTED)
    fig.subplots_adjust(left=0.11, right=0.95, top=0.90, bottom=0.18)
    fig.savefig(OUT / "04-fixed-clip-loss.png", facecolor=BG)


if __name__ == "__main__":
    fig_forest()
    fig_position()
    fig_training_log()
    fig_fixed_clip()
