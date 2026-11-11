"""Print Markdown tables from data/timing.json (and data/timing_repeat.json if present).

Per (size, threads, method): median over all pairs of the 6 videos (pooled), and per stratum.
Usage: python summarize.py > data/summary.md
"""
import json, os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SIZES = ["native", "1024sq", "512sq", "256sq"]
METHODS = ["farneback", "dis_ultrafast", "dis_fast", "dis_medium"]


def pooled(rows, **kw):
    sel = [r for r in rows if all(r[k] == v for k, v in kw.items())]
    return np.concatenate([r["times_ms"] for r in sel]) if sel else np.array([])


def main():
    t = json.load(open(f"{D}/timing.json"))
    rows, meta = t["rows"], t["meta"]
    threads = sorted({r["threads"] for r in rows}, reverse=True)
    print(f"cv2 {meta['cv2']}, {meta['cpu_model']}, default threads {meta['cv2_default_threads']}, "
          f"loadavg {meta['loadavg_start']} -> {meta['loadavg_end']}\n")
    print("## flow call time, median ms over all pairs (6 videos pooled)\n")
    print("| size | threads | " + " | ".join(METHODS) + " |")
    print("|---|---|" + "---|" * len(METHODS))
    for s in SIZES:
        for th in threads:
            vals = [pooled(rows, size=s, threads=th, method=m) for m in METHODS]
            print(f"| {s} | {th} | " + " | ".join(f"{np.median(v):.1f}" if len(v) else "-" for v in vals) + " |")
    print("\n## flow call time by stratum (threads=1), median ms\n")
    print("| size | stratum | " + " | ".join(METHODS) + " |")
    print("|---|---|" + "---|" * len(METHODS))
    for s in SIZES:
        for st in ["fast", "slow"]:
            vals = [pooled(rows, size=s, threads=1, method=m, stratum=st) for m in METHODS]
            print(f"| {s} | {st} | " + " | ".join(f"{np.median(v):.1f}" for v in vals) + " |")
    print("\n## preprocessing (resize INTER_AREA + gray), median ms per frame\n")
    print("| size | threads | ms |")
    print("|---|---|---|")
    for s in SIZES:
        for th in threads:
            v = np.concatenate([p["times_ms"] for p in t["preprocess"] if p["size"] == s and p["threads"] == th])
            print(f"| {s} | {th} | {np.median(v):.2f} |")
    print("\n## reference: |median flow in mask - GT centroid step| (cells, median over object steps)\n")
    print("| size | stratum | zero flow | " + " | ".join(METHODS) + " |")
    print("|---|---|---|" + "---|" * len(METHODS))
    th0 = rows[0]["threads"]
    for s in SIZES:
        for st in ["fast", "slow"]:
            cells, zero = [], None
            for m in METHODS:
                sel = [r for r in rows if r["size"] == s and r["threads"] == th0 and r["method"] == m
                       and r["stratum"] == st and "err_cells_median" in r]
                cells.append(" / ".join(f"{r['err_cells_median']:.2f}" for r in sel))
                zero = " / ".join(f"{r['zero_flow_err_median']:.2f}" for r in sel)
            print(f"| {s} | {st} | {zero} | " + " | ".join(cells) + " |")
    print("\n(per video, order: " + ", ".join(dict.fromkeys(r["video"] for r in rows)) + ")")
    if os.path.exists(f"{D}/timing_repeat.json"):
        rep = json.load(open(f"{D}/timing_repeat.json"))["rows"]
        print("\n## repeat (threads=1): median ms, run1 vs run2\n")
        print("| size | method | run1 | run2 | diff |")
        print("|---|---|---|---|---|")
        for s in sorted({r["size"] for r in rep}, key=SIZES.index):
            for m in METHODS:
                a = np.median(pooled(rows, size=s, threads=1, method=m))
                b = np.median(pooled(rep, size=s, threads=1, method=m))
                print(f"| {s} | {m} | {a:.1f} | {b:.1f} | {100 * (b - a) / a:+.1f}% |")


if __name__ == "__main__":
    main()
