---
type: Concept
title: Qwen3.8-Flash-Next Training and Stability
description: Muon with split orthogonalization and Canzona distribution, larger-batch/larger-LR scaling without warmup, and gated-residual stability that removes loss spikes at production scale.
tags: [qwen3.8-flash-next, muon, optimizer, scaling-laws, batch-size, learning-rate, training-stability, gated-residual]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T04:58:13Z }
sources:
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: 'On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability'
---

Qwen3.8-Flash-Next trains with Muon on true linear maps, refitted larger batch-size and learning-rate scaling without batch warmup, and stress-verified stability where the gated residual supplies missing rescaling[^qwen38-next-report].

## Muon optimizer scope and numerics

- Muon orthogonalizes Nesterov momentum (`mu=0.95`) with 8 Newton–Schulz steps using Polar Express per-step coefficients; update scaled by `0.2*sqrt(max(A,B))` so RMS is shape-independent; Frobenius pre-normalization epsilon `1e-14`; 8 steps chosen for accuracy plus fewer/smaller gradient-norm spikes under stress[^qwen38-next-report].
- Muon applies to genuine 2D linear maps: attention q/k/v/o, GDN in/out, routed plus shared expert fc1/fc2, and n-gram key/value projections[^qwen38-next-report].
- AdamW retained for input embeddings, output head, MoE router, and GR low-rank projections; n-gram tables use Adam without weight decay[^qwen38-next-report].
- Router stays on AdamW because Muon worsens early fluctuation without mid-late gain, plausibly because router output dims are independent expert scores with no shared linear structure; very elongated GR projections also favor AdamW; attention/GDN output gates are par-or-better on AdamW[^qwen38-next-report].

## Split fused parameters and distribution

- Megatron fused qkv, SwiGLU fc1, and GDN input matrices are split before orthogonalization and gathered afterward; otherwise NS mixes singular directions across unrelated blocks and uses the wrong concatenated shape for scaling[^qwen38-next-report].
- qkv and GDN inputs split at per-head granularity (loss plus benchmark gain); fc1 split into gate/up halves (loss flat, benchmarks slightly up); GDN decay/beta vector projections are excluded as non-matrix[^qwen38-next-report].
- Distribution via Canzona: whole-tensor alpha-balanced static partition equalizes estimated NS FLOPs (`~4K*max(A,B)*min(A,B)^2`) across DP ranks instead of Megatron equal-element sharding; async micro-group pipeline reconstructs each Muon matrix via fused All-to-All across TP ranks for single-device-equivalent steps while preserving ZeRO-1 bucket geometry and backward overlap[^qwen38-next-report].
- After splitting, one layer contributes O(100) sub-matrices whose step is launch-overhead bound, so the whole optimizer step is captured in a CUDA graph[^qwen38-next-report].

## Hyperparameter scaling

- Architecture plus optimizer shift refitted scaling-law optima toward substantially larger batch size and learning rate with slower LR decay versus Qwen3.5[^qwen38-next-report].
- Batch-size check on 20-layer 10.8B-A0.89B MoE over 4T tokens: new optimum `B=25.2M` loss 1.5702 vs `B=37.7M` 1.5707 vs prior `B=12.6M` 1.5774; gain `7.2e-3` over prior, steep rise below prediction and flat plateau above[^qwen38-next-report].
- Batch warmup rejected: ramping 6.3M to 25.2M by 524B tokens ends `2.5e-4` to `3.5e-4` worse than constant batch within run variance while costing 18.8% more optimizer steps; small-batch early phase adds gradient noise, transient step-count advantage fades as LR decays; stability unaffected with no `>0.1`-over-median loss steps and p99.9 pre-clip norms 0.088–0.190 vs 0.5 threshold[^qwen38-next-report].
- Larger batch also aids MoE expert token diversity and preserves Muon data efficiency where AdamW degrades[^qwen38-next-report].
- LR check on 48-layer 156B-A7B MoE over 419B tokens: predicted `B=8.4M, eta=1.76e-3` sits in flat bowl with `eta/sqrt(2)`, `eta*sqrt(2)`, and `B*1.25` within `7e-4`, while Qwen3.5 recipe ends `7.8e-3` above; predicted optimum has best average accuracy with best-or-tied on most suites, prior recipe clearly behind[^qwen38-next-report].
- That run stays stable: clipping never engages after warmup; max pre-clip norm only 28% of threshold at optimum vs 51% on prior recipe; no loss spike exceeds local median by >0.1 even at `sqrt(2)` higher LR[^qwen38-next-report].

## Stability stress tests

- Design: constant LR at 2x and 4x optimum on 28-layer 25B-A3B MoE to simulate prolonged peak-LR production stress at moderate scale; pass criterion is at least as stable as Qwen3.5 plus AdamW; shared batch size and 0.5 grad-norm clip; metrics are loss spikes (`>0.1` over 201-step median), p99.9 pre-clip norm plus threshold crossings, and per-block max activation[^qwen38-next-report].
- At 2x: AdamW 4.3 spikes/10k steps vs both Muon configs 0.2/10k[^qwen38-next-report].
- At 4x: AdamW 183 spikes/10k with 213/19932 clip crossings and continuous clipping; both Muon runs never cross threshold; Muon plus GR records zero loss spikes[^qwen38-next-report].
- Muon runs have higher median norm and larger max activations than AdamW at 2x yet far fewer spikes; adding GR reduces spike frequency/magnitude and activation outliers[^qwen38-next-report].
- Gate isolation with AdamW fixed at 3x optimum: enabling GatedNorm cuts spikes 32.0 to 3.2/10k and crossings 256 to 20; ungated outlier level grows almost proportionally with LR while spike rate grows faster; gated high-LR outlier level drops below ungated low-LR level, supporting the claim that the multiplicative gate supplies rescaling directly instead of forcing the network to grow fragile outliers[^qwen38-next-report].

## Production-run verification

- First 276B tokens with shared data order, schedule, and optimizer: adding GR lowers loss 0.026 at 276B; full Flash-Next recipe lowers another 0.032 for 0.058 total over Muon-only Qwen3.5 structure[^qwen38-next-report].
- Muon-only median norm ~2x and p99.9 ~4.2x either gated run (0.097/0.298 vs 0.053/0.071 and 0.043/0.066); only Muon-only crosses clip; gated runs have 4.3–4.7x lower 1000-step norm std; fusing residual read with final LM-head norm into one gated read likely explains much of Flash-Next vs Muon-plus-GR gap; GR markedly lowers residual maxima at every probed depth[^qwen38-next-report].
- Full-scale training proceeded with zero loss spikes or anomalous grad-norm fluctuations and without qk-clip or SwiGLU-clip[^qwen38-next-report].

## Relationships

- Related to [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — GDN/QSA, gated residual, and n-gram structures whose scaling and stability are established here.
- Uses [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — serving stack that inherits the stable checkpoint produced by this recipe.
- Related to [Qwen3.8-2.4T-A95B Architecture and Evaluation](qwen3.8-2.4t-a95b-architecture.md) — prior Qwen3.8 flagship family whose hyperparameter recipe this work refits and surpasses.

## Coverage limits

- Figure JPGs under `raw/Qwen3.8-Flash-Next-tech_report/images/` were not visually inspected; dynamics claims follow prose loss/norm/activation values.
- Scaling and stress numbers are report snapshots at stated 10.8B/25B/156B scales and token budgets, not universal optima; narrow benchmark margins among top LR settings are observational within evaluation noise as the report notes.
- No credentials, PII, or disclosure markings found.

[^qwen38-next-report]: On the Design of Qwen3.8-Next Architecture — `../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md`, Sec. 3.1–3.3 plus Sec. 5 covering Muon scope with 8-step Polar Express and split/Canzona/CUDA-graph engineering, refitted batch/LR scaling with warmup rejection and 4T/419B validations, constant-LR stress tests with gate isolation, and 276B production verification with zero-spike full run.
