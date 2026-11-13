"""Flow settings sweep on the 6 selected MOSE videos (2026-11-13, after the 11/13 MTG).

11/13 MTG: Farneback / DIS were compared only with their default settings ("bringing something that cannot work
and saying it does not work"). Here each method is run with several settings on the same 6 videos x first 20
pairs as flow_cost.py, all at 1024x1024 (the SAM2 input).

Per (video, pair, object present at t and t+1):
  iou      the object at t moved forward by the flow (every pixel moved, pixels leaving the image dropped,
           9x9 closing) vs the object at t+1
  border   the object touches the image border at t or t+1 (entering / leaving objects: the visible part
           does not move like the object, so the IoU is a weaker check there)
Time: the flow call only, CPU methods with 1 thread, RAFT on cuda:0 (RTX A4000) with synchronize.

  CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 python flow_sweep.py \
      --selection data/selected_videos.json --out data/sweep.jsonl
"""
import argparse
import json
import time

import cv2
import numpy as np
import torch
from PIL import Image

from flow_cost import R, frames_of
from flow_raft import load, raft_flow, to_input

S = 1024
CPU = {
    "farneback_L3_w15": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 3, 15, 3, 5, 1.2, 0),
    "farneback_L5_w15": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 5, 15, 3, 5, 1.2, 0),
    "farneback_L5_w31": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 5, 31, 3, 7, 1.5, 0),
    "farneback_L7_w21": lambda a, b: cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 7, 21, 5, 7, 1.5, 0),
    "dis_ultrafast": (lambda d: lambda a, b: d.calc(a, b, None))(cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_ULTRAFAST)),
    "dis_fast": (lambda d: lambda a, b: d.calc(a, b, None))(cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_FAST)),
    "dis_medium": (lambda d: lambda a, b: d.calc(a, b, None))(cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)),
}
GPU = ("raft_small", "raft_large")


def moved_iou(flow, m0, m1):
    ys, xs = np.nonzero(m0)
    xt = np.round(xs + flow[ys, xs, 0]).astype(int)
    yt = np.round(ys + flow[ys, xs, 1]).astype(int)
    ok = (xt >= 0) & (xt < S) & (yt >= 0) & (yt < S)
    mv = np.zeros((S, S), np.uint8)
    mv[yt[ok], xt[ok]] = 1
    mv = cv2.morphologyEx(mv, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)) > 0
    return float((mv & m1).sum() / (mv | m1).sum())


def touches_border(m):
    return bool(m[0].any() or m[-1].any() or m[:, 0].any() or m[:, -1].any())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection", required=True)
    ap.add_argument("--pairs", type=int, default=20)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    assert "RTX A4000" in torch.cuda.get_device_name(0), "set CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0"
    dev = torch.device("cuda")
    raft = {m: load(m, dev)[0] for m in GPU}
    cv2.setNumThreads(1)
    sel = json.load(open(args.selection))
    out = open(args.out, "w")
    for c in sel["fast"] + sel["slow"]:
        vid, stratum = c["video"], c["stratum"]
        fs = frames_of(vid)[: args.pairs + 1]
        imgs = [cv2.imread(f"{R}/JPEGImages/{vid}/{f}") for f in fs]
        labs = [cv2.resize(np.array(Image.open(f"{R}/Annotations/{vid}/{f[:-4]}.png")), (S, S),
                           interpolation=cv2.INTER_NEAREST) for f in fs]
        grays = [cv2.cvtColor(cv2.resize(im, (S, S), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY) for im in imgs]
        for t in range(len(fs) - 1):
            flows, times = {}, {}
            for name, fn in CPU.items():
                t0 = time.perf_counter(); flows[name] = fn(grays[t], grays[t + 1])
                times[name] = (time.perf_counter() - t0) * 1000
            for name in GPU:
                a, b = to_input(imgs[t], S, "cuda"), to_input(imgs[t + 1], S, "cuda")
                torch.cuda.synchronize(); t0 = time.perf_counter()
                f = raft_flow(raft[name], a, b, 12)
                torch.cuda.synchronize(); times[name] = (time.perf_counter() - t0) * 1000
                flows[name] = f[0].permute(1, 2, 0).cpu().numpy()
            ids = sorted(int(x) for x in np.unique(labs[t]) if x != 0)
            for oid in ids:
                m0, m1 = labs[t] == oid, labs[t + 1] == oid
                if not m0.any() or not m1.any():
                    continue
                row = {"video": vid, "stratum": stratum, "t": t, "object": oid,
                       "border": touches_border(m0) or touches_border(m1),
                       "iou": {n: moved_iou(f, m0, m1) for n, f in flows.items()}, "ms": times}
                out.write(json.dumps(row) + "\n")
        out.flush()
        print(vid, stratum, "done", flush=True)


if __name__ == "__main__":
    main()
