"""ViEW 8ページ版：4手法の HOTA 系指標を alpha（位置の一致の閾値）ごとに描く.

TrackEval の HOTA.plot_single_tracker_results（trackeval/metrics/hota.py）と同じ線・凡例で，
タイトルだけを除いて手法ごとに1枚ずつ出力する. 原稿で4枚を2×2に並べるため，図の大きさと文字の大きさだけ小さくしている. 値は表の評価runの pedestrian_detailed.csv（COMBINED 行）から読む.

    python3 2026-10-29-hota-alpha-curves.py
"""
import csv
import os.path as osp

import numpy as np
from matplotlib import pyplot as plt

TRACKEVAL = "/mnt/HDD10TB-2/aburatani/TrackEval/data/trackers/dancetrack/val"
STATEFUL = ("/mnt/HDD10TB-2/aburatani/2025_09_aburatani_Mamba_Trackers/artifacts/sam2_minimal_integration/trackeval/"
            "sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100_seqinfo/"
            "sam2_stateful_minimal_20260723T_sam2_minimal_25seq_epoch100")
# (出力ファイル名, TrackEval の tracker フォルダ)
METHODS = [
    ("sam2", osp.join(TRACKEVAL, "my_sam2_model")),
    ("samurai", osp.join(TRACKEVAL, "my_samurai_model")),
    ("ours_window", osp.join(TRACKEVAL, "my_samurai_mamba_model")),
    ("ours_state", STATEFUL),
]
# TrackEval の HOTA.float_array_fields のうち描かれる8つと，同じ線の種類
FIELDS = ["HOTA", "DetA", "AssA", "DetRe", "DetPr", "AssRe", "AssPr", "LocA"]
STYLES = ["r", "b", "g", "b--", "b:", "g--", "g:", "m"]
ALPHAS = list(range(5, 100, 5))  # TrackEval の array_labels（0.05, 0.10, ..., 0.95）
OUT_DIR = osp.dirname(osp.abspath(__file__))


def load_combined(tracker_dir):
    with open(osp.join(tracker_dir, "pedestrian_detailed.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["seq"] == "COMBINED":
                return {k: np.array([float(row[f"{k}___{a}"]) for a in ALPHAS]) for k in FIELDS}
    raise ValueError(f"COMBINED row not found in {tracker_dir}")


def main():
    plt.rcParams.update({"font.size": 7, "legend.fontsize": 5.5, "lines.linewidth": 1.0})
    plt.figure(figsize=(2.4, 2.1))
    array_labels = np.array(ALPHAS) / 100.0
    for name, path in METHODS:
        res = load_combined(path)
        for field, style in zip(FIELDS, STYLES):
            plt.plot(array_labels, res[field], style)
        plt.xlabel("alpha")
        plt.ylabel("score")
        plt.axis([0, 1, 0, 1])
        plt.legend([f"{k} ({np.round(np.mean(res[k]), 2)})" for k in FIELDS], loc="lower left",
                   handlelength=1.8, labelspacing=0.25, borderpad=0.3)
        plt.tight_layout(pad=0.2)
        out = osp.join(OUT_DIR, f"2026-10-29-hota-alpha-{name}")
        plt.savefig(out + ".pdf")
        plt.savefig(out + ".png", dpi=300)
        plt.clf()
        print(name, path, {k: round(float(np.mean(v)), 2) for k, v in res.items()})


if __name__ == "__main__":
    main()
