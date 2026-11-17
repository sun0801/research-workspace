#!/bin/bash
# 2026-11-17: MOSE part of the full motion diagnosis, moved to GPU 1 (RTX PRO 4500) to run in parallel with the
# DanceTrack part on GPU 0 (the sequential run_full.sh was stopped after it had started DanceTrack).
cd /mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2
D=/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/sam2-mamba-motion-tracking/experiments/figures/2026-11-16-dataset-motion-diagnosis
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=1 PYTHONPATH=$PWD
.venv-sam2/bin/python $D/motion_diag.py --dataset mose --out $D/data/mose --gaps 1 2 4 --pairs 12 --expect-gpu "RTX PRO 4500" \
  --save-fields runs/latent_corr/motion_diag/20261116/mose_fields.pt 2>&1 | tee $D/data/mose.log
while pgrep -f "motion_diag.py --dataset dancetrack" > /dev/null; do sleep 10; done
echo "ALL DONE $(date '+%F %T')" | tee $D/data/run_full.done
