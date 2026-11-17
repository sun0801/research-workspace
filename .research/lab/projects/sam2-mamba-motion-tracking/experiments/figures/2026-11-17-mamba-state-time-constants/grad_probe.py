"""学習済みの重みで、学習と同じ forward・loss を K 区間だけ回し、adapter の各パラメータの勾配（clip 前）を測る。

重みは更新しない（optimizer を作らない）。SAM2 repo は読み取りだけ（import するだけ）。

- 勾配の大きさ：要素の RMS（区間ごとの勾配の2乗平均の平方根）。
- 向きのそろい方：‖区間平均の勾配‖ / sqrt(区間ごとの ‖勾配‖² の平均)。
  どの区間でも同じ向きなら 1、区間ごとにばらばらなら 1/sqrt(K) 付近。
- 全体の勾配ノルムと、clip（max_norm 0.1）で掛かる倍率。

使い方（SAM2 repo の .venv-sam2 の python で）:
  CUDA_VISIBLE_DEVICES=1 python grad_probe.py --config A_v3_nockpt --checkpoint <checkpoint.pt> --clips 64 --out data/grad_probe_A.json
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

REPO = Path("/mnt/HDD10TB-2/aburatani/2025_03_aburatani_sam2")
sys.path.insert(0, str(REPO))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--clips", type=int, default=64)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    out_path = Path(args.out).resolve()
    os.chdir(REPO)

    import torch
    from hydra import initialize_config_module
    from hydra.core.global_hydra import GlobalHydra
    from hydra.utils import instantiate

    from training.check_short_clip import build, first_batches
    from training.utils.train_utils import register_omegaconf_resolvers

    register_omegaconf_resolvers()
    if not GlobalHydra.instance().is_initialized():
        initialize_config_module("sam2", version_base="1.2")
    device = torch.device("cuda:0")
    model, cfg = build(args.config, device, ["scratch.num_train_workers=2"])
    state = torch.load(args.checkpoint, map_location="cpu", weights_only=False)["model"]
    model.load_state_dict(state, strict=True)
    model.train()
    loss_fn = instantiate(cfg.trainer.loss, _convert_="all")["all"]
    max_norm = float(cfg.trainer.optim.gradient_clip.max_norm)
    params = {n: q for n, q in model.named_parameters() if q.requires_grad}
    assert all(n.startswith("temporal_mamba_adapter.") for n in params), "adapter 以外が学習対象になっている"
    s1 = {n: torch.zeros_like(q, dtype=torch.float64) for n, q in params.items()}
    s2 = {n: torch.zeros_like(q, dtype=torch.float64) for n, q in params.items()}
    sq_norm = {n: 0.0 for n in params}
    totals, losses = [], []
    torch.manual_seed(123)
    batches = first_batches(cfg, args.clips)
    for k, batch in enumerate(batches):
        batch = batch.to(device)
        model.zero_grad(set_to_none=True)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            outputs = model(batch)
            loss = loss_fn(outputs, batch.masks)
        core = loss["core_loss"] if isinstance(loss, dict) else loss
        core.backward()
        tot = 0.0
        for n, q in params.items():
            g = q.grad.detach().double()
            s1[n] += g
            s2[n] += g * g
            v = float((g * g).sum())
            sq_norm[n] += v
            tot += v
        totals.append(math.sqrt(tot))
        losses.append(float(core.detach()))
        print(f"clip {k}: loss {losses[-1]:.3f} grad_norm_total {totals[-1]:.4g}", flush=True)
    K = len(totals)
    rows = {}
    for n in params:
        numel = s2[n].numel()
        rms = math.sqrt(float(s2[n].sum()) / K / numel)
        mean_g = s1[n] / K
        align = float(mean_g.norm()) / math.sqrt(sq_norm[n] / K) if sq_norm[n] > 0 else float("nan")
        elem = float((s1[n].abs() / (K * s2[n]).sqrt().clamp_min(1e-300)).mean())
        rows[n] = {"numel": numel, "grad_rms": rms, "grad_norm_rms": math.sqrt(sq_norm[n] / K),
                   "share_of_total_sq": sq_norm[n] / sum(sq_norm.values()),
                   "alignment_tensor": align, "alignment_element_mean": elem}
    st = sorted(totals)
    factors = sorted(min(1.0, max_norm / t) for t in totals)
    result = {"config": args.config, "checkpoint": args.checkpoint, "clips": K, "max_norm": max_norm,
              "loss_mean": sum(losses) / K, "grad_norm_total": {"min": st[0], "median": st[K // 2], "max": st[-1]},
              "clip_factor": {"min": factors[0], "median": factors[K // 2], "max": factors[-1]},
              "noise_floor_alignment": 1 / math.sqrt(K), "params": rows}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=1) + "\n")
    print(f"grad_norm_total median {st[K // 2]:.4g}, clip factor median {factors[K // 2]:.4g}, 1/sqrt(K) {1 / math.sqrt(K):.3f}")
    print(f"{'name':48s} {'grad_rms':>10s} {'×clip(med)':>11s} {'share':>8s} {'align':>7s} {'elem':>6s}")
    for n, r in rows.items():
        print(f"{n[len('temporal_mamba_adapter.'):]:48s} {r['grad_rms']:10.3e} {r['grad_rms'] * factors[K // 2]:11.3e} "
              f"{r['share_of_total_sq']:8.5f} {r['alignment_tensor']:7.3f} {r['alignment_element_mean']:6.3f}")


if __name__ == "__main__":
    main()
