#!/bin/bash
# NOTE 2026-11-17 15:06: stopped after the DanceTrack command had started (it kept running); the MOSE command
# below was NOT run from here, see run_mose_gpu1.sh (GPU 1, in parallel).
# Full motion diagnosis (2026-11-17): DanceTrack train (about 34 min) then MOSE tuning (about 51 min), GPU 0 = RTX A4000.
cd /mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2
D=/mnt/HDD10TB-2/aburatani/research-workspace/.research/lab/projects/sam2-mamba-motion-tracking/experiments/figures/2026-11-16-dataset-motion-diagnosis
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0 PYTHONPATH=$PWD
.venv-sam2/bin/python $D/motion_diag.py --dataset dancetrack --out $D/data/dancetrack --gaps 1 2 4 8 --pairs 12 \
  --save-fields runs/latent_corr/motion_diag/20261116/dancetrack_fields.pt 2>&1 | tee $D/data/dancetrack.log
.venv-sam2/bin/python $D/motion_diag.py --dataset mose --out $D/data/mose --gaps 1 2 4 --pairs 12 \
  --save-fields runs/latent_corr/motion_diag/20261116/mose_fields.pt 2>&1 | tee $D/data/mose.log
echo "ALL DONE $(date '+%F %T')" | tee $D/data/run_full.done
