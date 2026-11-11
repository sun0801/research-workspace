cv2 4.13.0, Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz, default threads 72, loadavg [1.951171875, 2.08935546875, 2.09521484375] -> [14.44775390625, 8.59814453125, 5.138671875]

## flow call time, median ms over all pairs (6 videos pooled)

| size | threads | farneback | dis_ultrafast | dis_fast | dis_medium |
|---|---|---|---|---|---|
| native | 72 | 571.8 | 19.4 | 34.8 | 100.0 |
| native | 1 | 532.2 | 29.7 | 62.6 | 305.8 |
| 1024sq | 72 | 255.1 | 9.8 | 20.4 | 55.7 |
| 1024sq | 1 | 247.2 | 14.8 | 31.4 | 154.6 |
| 512sq | 72 | 64.2 | 2.9 | 9.3 | 20.9 |
| 512sq | 1 | 60.0 | 3.6 | 8.1 | 37.7 |
| 256sq | 72 | 15.4 | 0.9 | 4.7 | 8.6 |
| 256sq | 1 | 15.5 | 0.9 | 2.0 | 9.7 |

## flow call time by stratum (threads=1), median ms

| size | stratum | farneback | dis_ultrafast | dis_fast | dis_medium |
|---|---|---|---|---|---|
| native | fast | 534.4 | 29.7 | 62.6 | 309.7 |
| native | slow | 530.7 | 29.7 | 62.5 | 303.4 |
| 1024sq | fast | 265.0 | 14.8 | 31.4 | 153.9 |
| 1024sq | slow | 245.6 | 14.8 | 31.5 | 156.6 |
| 512sq | fast | 60.0 | 3.6 | 8.0 | 37.7 |
| 512sq | slow | 60.0 | 3.7 | 8.1 | 37.7 |
| 256sq | fast | 15.5 | 0.9 | 2.1 | 9.7 |
| 256sq | slow | 15.4 | 0.9 | 2.0 | 9.7 |

## preprocessing (resize INTER_AREA + gray), median ms per frame

| size | threads | ms |
|---|---|---|
| native | 72 | 0.29 |
| native | 1 | 1.60 |
| 1024sq | 72 | 2.84 |
| 1024sq | 1 | 17.99 |
| 512sq | 72 | 4.51 |
| 512sq | 1 | 10.24 |
| 256sq | 72 | 7.42 |
| 256sq | 1 | 7.83 |

## reference: |median flow in mask - GT centroid step| (cells, median over object steps)

| size | stratum | zero flow | farneback | dis_ultrafast | dis_fast | dis_medium |
|---|---|---|---|---|---|---|
| native | fast | 7.89 / 4.87 / 4.71 | 7.90 / 4.87 / 4.71 | 1.92 / 1.26 / 1.81 | 4.07 / 1.27 / 1.84 | 1.37 / 1.54 / 1.64 |
| native | slow | 0.44 / 0.28 / 0.35 | 0.10 / 0.07 / 0.24 | 0.02 / 0.07 / 0.12 | 0.02 / 0.07 / 0.12 | 0.03 / 0.07 / 0.11 |
| 1024sq | fast | 7.89 / 4.87 / 4.71 | 7.80 / 4.68 / 4.71 | 1.00 / 1.13 / 1.78 | 3.15 / 1.22 / 1.84 | 1.38 / 1.45 / 1.83 |
| 1024sq | slow | 0.44 / 0.28 / 0.35 | 0.06 / 0.07 / 0.20 | 0.02 / 0.08 / 0.17 | 0.02 / 0.08 / 0.12 | 0.04 / 0.07 / 0.11 |
| 512sq | fast | 7.89 / 4.87 / 4.71 | 7.06 / 3.55 / 3.31 | 0.63 / 1.03 / 1.45 | 2.99 / 1.13 / 1.81 | 1.39 / 1.26 / 1.72 |
| 512sq | slow | 0.44 / 0.28 / 0.35 | 0.04 / 0.08 / 0.15 | 0.05 / 0.08 / 0.26 | 0.06 / 0.08 / 0.17 | 0.03 / 0.08 / 0.12 |
| 256sq | fast | 7.89 / 4.87 / 4.71 | 5.36 / 1.30 / 1.85 | 1.63 / 1.11 / 1.84 | 2.10 / 1.06 / 1.65 | 1.33 / 1.13 / 1.46 |
| 256sq | slow | 0.44 / 0.28 / 0.35 | 0.05 / 0.08 / 0.26 | 0.07 / 0.10 / 0.36 | 0.11 / 0.09 / 0.28 | 0.06 / 0.08 / 0.18 |

(per video, order: 24df9789, b6cadd11, 2e85e790, 198021ad, 5f14e5d2, f28b429a)

## repeat (threads=1): median ms, run1 vs run2

| size | method | run1 | run2 | diff |
|---|---|---|---|---|
| 1024sq | farneback | 247.2 | 245.0 | -0.9% |
| 1024sq | dis_ultrafast | 14.8 | 15.2 | +2.9% |
| 1024sq | dis_fast | 31.4 | 32.3 | +2.8% |
| 1024sq | dis_medium | 154.6 | 153.9 | -0.5% |
| 256sq | farneback | 15.5 | 15.3 | -0.8% |
| 256sq | dis_ultrafast | 0.9 | 0.9 | +2.0% |
| 256sq | dis_fast | 2.0 | 2.1 | +0.9% |
| 256sq | dis_medium | 9.7 | 9.6 | -1.1% |
