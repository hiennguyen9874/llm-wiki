---
type: Concept
title: Hybrid Mamba-Transformer vision backbone
description: How MambaVision redesigns the Mamba mixer and places self-attention late to reach a new accuracy-throughput Pareto for classification, detection, and segmentation.
tags: [detection, backbone, mamba, transformer, efficiency, segmentation]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T22:00:00Z }
sources:
  - id: mambavision-2407-08083-v2
    resource: ../raw/arXiv-2407.08083v2/main.tex
    scope: ../raw/arXiv-2407.08083v2/
    kind: paper
    revision: v2
    title: 'MambaVision: A Hybrid Mamba-Transformer Vision Backbone'
---

Synthesis: MambaVision makes state-space sequence modeling usable for vision by replacing causal convolution with regular convolution, adding a parallel non-SSM branch fused by concatenation, keeping CNN stages at high resolution, and placing self-attention only in the last half of low-resolution stages — reported as a new ImageNet accuracy-throughput Pareto that also transfers to COCO detection/instance segmentation and ADE20K semantic segmentation[^mambavision-2407-08083-v2-1].

## Problem and design hypothesis

- **Reported:** pure Mamba's autoregressive formulation is inefficient for spatial data and weak at single-pass global context; bidirectional SSMs (Vim) add latency and training complexity, while VMamba's four-way cross-scan remains path-constrained; the paper positions single-forward Mamba plus late attention as the fix[^mambavision-2407-08083-v2-2].
- **Reported:** EfficientVMamba puts SSMs at large resolutions and CNNs at small ones, while MambaVision does the opposite (CNNs early/high-resolution, SSM plus attention late/low-resolution); SiMBA's EinFFT channel stabilization is framed as not solving spatial understanding[^mambavision-2407-08083-v2-2].

## Macro architecture

- **Reported:** four-stage hierarchical backbone: stem of two consecutive 3×3 stride-2 convolutions to H/4×W/4×C, per-stage 3×3 stride-2 downsampler, residual CNN blocks in stages 1–2 (GELU, batch norm, 3×3 convolutions per Eq. `fused_convmb`), and hybrid MambaVision plus Transformer blocks in stages 3–4[^mambavision-2407-08083-v2-3].
- **Reported:** variant channel/layer scaling is tabulated in the appendix arch-spec table (T/S/B/L stems, stage channels, MV versus SA block counts and attention heads); representative sizes are T 31.8M/4.4G, T2 35.1M/5.1G, S 50.1M/7.5G, B 97.7M/15.0G, L 227.9M/34.9G, L2 241.5M/37.5G[^mambavision-2407-08083-v2-3].

## Micro architecture: mixer and hybrid rule

- **Reported:** SSM preliminaries follow the continuous ODE `h'(t)=Ah+Bx`, `y=Ch`, zero-order-hold discretization to `barA/barB/barC`, global convolution kernel `Kbar`, and Mamba selectivity over `B`, `C`, `Δ`[^mambavision-2407-08083-v2-4].
- **Reported:** MambaVision mixer splits a linear projection into two C/2 branches: `X1=Scan(σ(Conv(Linear(C,C/2)(Xin))))` (SSM path) and `X2=σ(Conv(Linear(C,C/2)(Xin)))` (symmetric non-SSM path with convolution plus SiLU), concatenates them, and projects back with `Linear(C/2→C)`; causal convolution is replaced by regular convolution and each branch uses half width to preserve parameter count[^mambavision-2407-08083-v2-4].
- **Reported:** PyTorch-like pseudocode (`MambaVisionMixer`: `d_state=16`, `dt_rank=ceil(dim/16)`, `in_proj`, `x_proj`, depthwise-style `conv1d_x/z`, `dt_proj`, `A_log`, `D`, `out_proj`, `selective_scan_fn`) operationalizes the mixer[^mambavision-2407-08083-v2-4].
- **Reported:** stage layers follow `Xhat^n=Mixer(Norm(X^{n-1}))+X^{n-1}`, `X^n=MLP(Norm(Xhat^n))+Xhat^n` with layer norm; given N layers, the first N/2 use the MambaVision mixer and the remaining N/2 use multihead self-attention `Softmax(QK^T/√dh)V`, optionally windowed (defaults 14 in stage 3, 7 in stage 4)[^mambavision-2407-08083-v2-4].
- **Synthesis:** the reusable rule is **Mamba early plus attention late**: SSM blocks for efficient sequential mixing first, self-attention blocks in the final N/2 layers to recover global context and long-range dependencies.

## Training and evaluation protocol

- **Reported:** ImageNet-1K classification for 300 epochs on 32 A100 GPUs; appendix adds LAMB optimizer, batch 4096, learning rate 4e-3; throughput measured on A100 with batch 128[^mambavision-2407-08083-v2-5].
- **Reported:** COCO detection/instance segmentation uses Cascade Mask R-CNN with ×3 schedule at 1280×800; ADE20K uses UPerNet at 512×512; downstream uses AdamW with batch 16; mixer/window ablations on COCO use Mask R-CNN with ×1 schedule[^mambavision-2407-08083-v2-5].

## Principal results

- **Reported:** ImageNet-1K Top-1 versus throughput (A100, batch 128): T 82.3% at 6298 img/s, T2 82.7% at 5990, S 83.3% at 4700, B 84.2% at 3670, L 85.0% at 2190, L2 85.3% at 1021; the paper claims a new Pareto front over Conv, Transformer, Conv-Transformer, and Mamba baselines in its Table `imgnet` and Fig. 1[^mambavision-2407-08083-v2-6].
- **Reported:** examples from that table: MambaVision-B 84.2% versus ConvNeXt-B 83.8%, Swin-B 83.5%, and VMamba-B 83.9% with higher reported throughput; MambaVision-B is reported at 56% fewer GFLOPs than MaxViT-B (15.0G versus 23.4G)[^mambavision-2407-08083-v2-6].
- **Reported:** COCO Cascade Mask R-CNN ×3: T 51.1 box AP / 44.3 mask AP (86M params, 740G FLOPs), S 52.3/45.2 (108M, 828G), B 52.8/45.7 (145M, 964G); reported deltas include T +0.7/+0.6 over ConvNeXt-T and Swin-T, S +0.4/+0.2 over ConvNeXt-S and Swin-S, B +0.1/+0.1 over ConvNeXt-B and +0.9/+0.7 over Swin-B[^mambavision-2407-08083-v2-7].
- **Reported:** ADE20K UPerNet: T 46.0 mIoU (55M, 945G), S 48.2 (84M, 1135G), B 49.1 (126M, 1342G); reported deltas include T +1.5 over Swin-T, S +0.6 over Swin-S, B +1.0 over Swin-B, with small leads over Focal-T/S/B at comparable sizes[^mambavision-2407-08083-v2-8].
- **Reported:** ImageNet-21K pretraining then 1K fine-tuning: B rises 84.2% to 84.9% at 224, L rises 85.0% to 86.1% at 224, and larger L3 (739.6M) reaches 87.3% at 256 and 88.1% at 512; the paper presents this as the first successful Mamba-based scaling to ImageNet-21K — treat the "first" as the authors' reported claim, not an independently verified priority fact[^mambavision-2407-08083-v2-9].

## Ablations

- **Reported:** token-mixer study on the T configuration: causal-conv1 without conv2 is weakest; regular conv1 without conv2 improves everywhere; adding conv2 with gating reaches 81.3% Top-1 / 45.3 box / 41.0 mask / 45.7 mIoU; replacing gating with concatenation reaches 82.3 / 46.4 / 41.8 / 46.0 (about +1.0 Top-1, +1.1 box, +0.8 mask, +0.9 mIoU over gating)[^mambavision-2407-08083-v2-10].
- **Reported:** hybrid-pattern study at iso-parameters (31.8M): random 81.3%, first-N/2 attention (`SSSSMMMM`) 81.5%, alternating `SMSMSMSM` 81.4%, alternating `MSMSMSMS` 81.6%, last-N/4 attention (`MMMMMMSS`) 81.9%, last-N/2 attention (`MMMMSSSS`) 82.3% best[^mambavision-2407-08083-v2-10].
- **Reported:** window-size study on T (Mask R-CNN ×1; classification throughput A100 batch 128): 7,7 gives 6318 img/s, 82.2% Top-1, 46.4 box, 41.7 mask; 14,7 gives 6298 img/s, 82.3%, 46.4, 41.8; 14,7 chosen as default because the accuracy gain costs only about 0.3% throughput[^mambavision-2407-08083-v2-11].

## Interpretability

- **Reported:** final-stage attention maps are presented as localizing semantic regions without explicit supervision (aircraft body, bird head/tail, person plus held object); the appendix extends this across containers, spiders, birds, marine life, snakes, dogs, sports, poultry, and outdoor scenes[^mambavision-2407-08083-v2-11].
- **Observed:** static visual inspection of `figures/attn_img.png` and `figures/abl_attn.png` confirms input/heatmap/overlay triplets with peak activation over the described foreground objects; this confirms presentation, not correctness of the underlying attention computation[^mambavision-2407-08083-v2-11].

## Relationships

- Supports [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) as a throughput-efficient backbone option.
- Complements [Vision foundation models for detection](vision-foundation-models-for-detection.md) as a non-foundation-model supervised backbone alternative.
- Contrasts with [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md), which optimizes detector heads and assignment while MambaVision optimizes the backbone.

## Contradictions

- Internal baseline mismatch: the mixer-ablation body text describes the original-Mamba baseline as 80.9% Top-1 with −1.8/−1.6/−1.6/−1.4 deltas, while Table `abl_study1` lists the causal-conv1-without-conv2 row as 80.5 / 44.8 / 40.4 / 44.2 — use the table row for the causal baseline and treat the body-text 80.9 as consistent instead with the regular-conv1-without-conv2 row[^mambavision-2407-08083-v2-10].
- No variance, significance, or seed reporting was found in the inspected material; cross-vendor AP/throughput comparisons use different setups and small gaps should not be treated as decisive[^mambavision-2407-08083-v2-12].

## Coverage limits

- All accuracy, AP, mIoU, parameter, FLOP, and throughput figures are **reported**, not reproduced; no code was executed.
- **Observed** by static inspection: `main.tex` fully read including abstract, introduction, related work, methodology, experiments, ablations, and conclusion; `supp_sec.tex` fully read including window ablation, arch-spec table, training details, and interpretability; `preamble.tex` checked as package macros only; `figures/attn_img.png` and `figures/abl_attn.png` visually inspected for attention-overlay presentation[^mambavision-2407-08083-v2-11].
- Excluded with reason: `sec/0_abstract.tex`, `sec/1_intro.tex`, `sec/2_formatting.tex`, `sec/3_finalcopy.tex`, `sec/X_suppl.tex` as CVPR template boilerplate not input by `main.tex`; `cvpr.sty` and `ieeenat_fullname.bst` as vendored templates; `main.bbl` as supporting bibliography; `README.md` as author-kit history; `figures/*.pdf` (`arch_mamba_vis.pdf`, `block_design.pdf`, `models_latency_torch.pdf`, `21k.pdf`) used only via captions and body-text reproduction without visual PDF inspection[^mambavision-2407-08083-v2-12].
- The paper states downstream gains came without extensive hyperparameter optimization; license terms were not found in the inspected tex; upstream code is referenced but was not fetched or run[^mambavision-2407-08083-v2-12].

[^mambavision-2407-08083-v2-1]: `raw/arXiv-2407.08083v2/main.tex`, title, author block (Hatamizadeh, Kautz, NVIDIA), `\def\confName{CVPR}` / `\def\confYear{2025}`, Abstract, Introduction contributions bullets, code URL `https://github.com/NVlabs/MambaVision`.
[^mambavision-2407-08083-v2-2]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Introduction (sequential-dependency and global-context limits of autoregressive Mamba; bidirectional latency/overfitting critique) and Sec. Related work, Mamba-Based (Vim bidirectional SSM, VMamba cross-scan module, EfficientVMamba resolution placement, SiMBA EinFFT).
[^mambavision-2407-08083-v2-3]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Methodology Macro Architecture, Eq. `fused_convmb`, Fig. `model_architecture`; `raw/arXiv-2407.08083v2/supp_sec.tex`, Sec. Architecture Details, Tab. `arch-spec-abl` (SA/MV blocks, channels, heads).
[^mambavision-2407-08083-v2-4]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Methodology Micro Architecture — Mamba Preliminaries Eqs. `ode`/`discretization`/`discretization2`, Layer Architecture Eq. `eq_layer`, MambaVision Mixer Eq. `eq_mixer1`, Self-attention Eq. `mhsa`, Algorithm `mamba_vision_mixer`, Fig. `mamba_vision`.
[^mambavision-2407-08083-v2-5]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Experiments intro (ImageNet-1K 300 epochs, 32 A100; Cascade Mask R-CNN ×3 at 1280×800; UPerNet); `raw/arXiv-2407.08083v2/supp_sec.tex`, Sec. Training Details (LAMB batch 4096 lr 4e-3; windows 14/7; AdamW batch 16) and Tab. `abl_study_window` caption (Mask R-CNN ×1 for ablations).
[^mambavision-2407-08083-v2-6]: `raw/arXiv-2407.08083v2/main.tex`, Fig. `fig1` caption (A100 batch-128 throughput), Tab. `imgnet`, Sec. Results Image classification (B versus ConvNeXt/Swin/VMamba; 56% fewer GFLOPs than MaxViT-B).
[^mambavision-2407-08083-v2-7]: `raw/arXiv-2407.08083v2/main.tex`, Tab. `cascademaskrcnn`, Sec. Results Object Detection and Segmentation (Cascade Mask R-CNN, ×3, COCO deltas versus ConvNeXt/Swin variants).
[^mambavision-2407-08083-v2-8]: `raw/arXiv-2407.08083v2/main.tex`, Tab. `ade_segmentation`, Sec. Results Object Detection and Segmentation (UPerNet, ADE20K 512×512, deltas versus Swin/Focal variants).
[^mambavision-2407-08083-v2-9]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Ablation Large-scale Training on ImageNet-21K, Fig. `21k` (B 84.2→84.9, L 85.0→86.1 at 224; L3 739.6M 87.3% at 256 / 88.1% at 512; first-scaling claim).
[^mambavision-2407-08083-v2-10]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Ablation Design of Token Mixer and Hybrid Pattern, Tab. `abl_study1` (conv1/conv2/concat rows; Mask R-CNN ×1) and Tab. `abl2` (iso-parameter 31.8M patterns `SSSSMMMM` through `MMMMSSSS`).
[^mambavision-2407-08083-v2-11]: `raw/arXiv-2407.08083v2/supp_sec.tex`, Sec. Ablation Study Tab. `abl_study_window` and Appendix Fig. `attention_viz`; `raw/arXiv-2407.08083v2/main.tex`, Sec. Ablation Interpretability, Fig. `attn_map`; `raw/arXiv-2407.08083v2/figures/attn_img.png` and `figures/abl_attn.png` visually inspected (input/heatmap/overlay triplets).
[^mambavision-2407-08083-v2-12]: `raw/arXiv-2407.08083v2/main.tex`, Sec. Results (no-extensive-tuning statement) and Abstract (code URL); coverage ledger per Gate 2: template `sec/*` (except via `supp_sec`), `cvpr.sty`, `ieeenat_fullname.bst`, `main.bbl`, `README.md` excluded with reasons; PDF figures via caption/body text only; no execution; no variance/seeds found.
