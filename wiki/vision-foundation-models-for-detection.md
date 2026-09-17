---
type: Concept
title: Vision foundation models for detection
description: How DINOv3-class representations are distilled or adapted into small real-time detectors without paying foundation-model inference cost.
tags: [detection, foundation-models, distillation, nas, dinov3]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T04:56:58Z }
sources:
  - id: rfdetr-2511-09554-v2
    resource: ../raw/arXiv-2511.09554v2/iclr2026_conference.tex
    scope: ../raw/arXiv-2511.09554v2/
    kind: paper
    revision: v2
    title: 'RF-DETR: Neural Architecture Search for Real-Time Detection Transformers'
  - id: rtdetrv4-2510-25257-v1
    resource: ../raw/arXiv-2510.25257v1/main.tex
    scope: ../raw/arXiv-2510.25257v1/
    kind: paper
    revision: v1
    title: 'RT-DETRv4: Painlessly Furthering Real-Time Object Detection with Vision Foundation Models'
  - id: deimv2-2509-20787-v4
    resource: ../raw/arXiv-2509.20787v4/main.tex
    scope: ../raw/arXiv-2509.20787v4/
    kind: paper
    revision: v4
    title: 'Real-Time Object Detection Meets DINOv3'
  - id: reseach-2026-09-17
    resource: ../raw/reseach.md
    kind: article
    title: Tổng hợp SOTA object detection / instance segmentation 2024–2026
  - id: dinov3-2508-10104-v1
    resource: ../raw/arXiv-2508.10104v1/main.tex
    scope: ../raw/arXiv-2508.10104v1/
    kind: paper
    revision: v1
    title: DINOv3
---

Synthesis: the strongest 2025–2026 pattern is **large foundation model during training → small specialist at inference**, either by direct feature use with adapters or by semantic distillation that is removed at deploy time[^reseach-2026-09-17-1]. DINOv3 is now compiled from its primary report: a 7B self-supervised ViT whose dense-feature degradation is repaired by Gram Anchoring, then compressed by distillation into deployable ViT and ConvNeXt variants and kept frozen for downstream tasks[^dinov3-2508-10104-v1-1].

## DINOv3 scale recipe

- **Reported:** data pool is ~17B Instagram web images after platform moderation; curated LVD-1689M combines hierarchical k-means balancing (levels 200M/8M/800K/100K/25K), retrieval-based curation for task-relevant concepts, and raw ImageNet1k/22k plus Mapillary; training mixes heterogeneous batches with 10% homogeneous ImageNet1k batches[^dinov3-2508-10104-v1-2].
- **Reported:** teacher is ViT-7B with 6.7B params, 40 blocks, embed dim 4096, patch 16, RoPE with box jittering in `[-s,s]`, `s in [0.5,2]`, 4 registers, SwiGLU FFN 8192, 32 heads x128 dim; DINO head 8192-8192-512 with 256K prototypes, iBOT head 8192-8192-384 with 96K prototypes[^dinov3-2508-10104-v1-3].
- **Reported:** loss is `L_Pre = L_DINO + L_iBOT + 0.1*L_DKoleo` with Sinkhorn-Knopp replacing centering, dedicated LayerNorm on local versus global crop outputs, and distributed Koleo over 16-sample batches; reported effect is +0.2 ImageNet kNN late in training, +1 ADE20k mIoU, −0.02 NYUv2 RMSE[^dinov3-2508-10104-v1-3].
- **Observed:** optimization uses constant learning rate, weight decay, and teacher EMA momentum after linear warmup of LR and teacher temperature, AdamW, batch 4096 over 256 GPUs, 2 global 256px plus 8 local 112px crops, 1M iterations; static inspection only, no execution[^dinov3-2508-10104-v1-3].
- **Synthesis:** deploying the 7B backbone directly in a detector is impractical, so downstream work focuses on transfer rather than direct deployment.

## Gram Anchoring for dense features

- **Reported:** long training improves global accuracy but degrades dense prediction after ~200K iterations for ViT-g and ViT-7B; patch-to-patch cosine maps become noisy and CLS-to-patch similarity rises, losing locality; registers keep patch norms stable but do not prevent this[^dinov3-2508-10104-v1-4].
- **Reported:** Gram Anchoring matches Gram matrices instead of features: `L_Gram = || X_S X_S^T − X_G X_G^T ||_F^2` on L2-normalized patches, only on global crops; Gram teacher is an early iteration (100–200K) with superior dense properties, applied after 1M iterations; teacher is refreshed every 10K iterations to the main EMA teacher as refinement `L_Ref`[^dinov3-2508-10104-v1-4].
- **Reported:** high-resolution variant `L_HRef` feeds 2x resolution to the Gram teacher then bicubic 2x downsamples before the Gram matrix; 200K x2 teacher gives 88.0 IN1k linear, 55.7 ADE20k mIoU, 0.281 NYU RMSE versus 88.2/50.3/0.307 baseline, while a late 1M teacher is worse at 54.9/0.290; reported gain is almost immediate within 10K iterations plus further ADE20k gains on teacher updates[^dinov3-2508-10104-v1-5].
- **Synthesis:** the durable mechanism is **constrain similarity structure, free the features** — early-stage locality regularizes late-stage discrimination without pinning representations.

## Outliers and feature use

- **Reported:** 4 registers beat no-handling, attention bias, and value gating on high-norm patch outliers at 150K-iteration 7B ablations (86.6 IN1k linear, 53.0 ADE20k mIoU); feature-dimension outliers grow with depth and training, carry little inference signal, and are suppressed by the final LayerNorm or batch norm[^dinov3-2508-10104-v1-6].
- **Reported:** practical rule is apply final LayerNorm for last-layer features and batch norm or PCA-style scaling when reusing intermediate-layer features for segmentation or depth[^dinov3-2508-10104-v1-6].

## Post-training: resolution, distillation, text

- **Reported:** high-resolution adaptation trains 10K extra iterations with mixed global {512,768} and local {112,168,224,336} crops plus Gram from the 7B teacher; without Gram dense performance degrades; adapted features improve with image size and remain visually stable beyond 4K despite 768 max training size[^dinov3-2508-10104-v1-7].
- **Reported:** distillation fixes the 7B model as teacher with the same pre-training objective and no Gram, training 1M iterations plus 250K cosine cooldown; multi-student pipeline shares teacher inference across all GPUs via all-gather then per-group student training, adding a student only adds its training cost[^dinov3-2508-10104-v1-7].
- **Reported:** text alignment `dino.txt` follows LiT with frozen vision backbone plus two added transformer layers, matching CLS plus mean-pooled patches to a from-scratch text encoder with contrastive loss; DINOv3 ViT-L reaches 82.3 IN1k, 85.4-A/93.0-R/80.5-ObjectNet zero-shot and 24.7 ADE20k / 36.9 Cityscapes open-vocabulary segmentation, ahead of prior `dino.txt` and best on dense alignment while slightly behind SigLIP2/PE on global retrieval[^dinov3-2508-10104-v1-8].

## Distilled family and efficiency

- **Reported:** family is ViT-S 21M, S+ 29M, B 86M, L 300M, H+ 840M, 7B 6716M plus ConvNeXt Tiny 29M / Small 50M / Base 89M / Large 198M; inference GFLOPs at 256/512 are e.g. ViT-B 47/216, ViT-L 163/721, ViT-H+ 450/1903, ViT-7B 3550/14515[^dinov3-2508-10104-v1-9].
- **Reported:** distilled ViTs beat same-size DINOv2/SigLIP2/PEcore on dense tasks without losing global accuracy: ViT-L 54.9 ADE20k (+6 over DINOv2), 0.352 NYU, 79.9 DAVIS; ViT-B 51.8 ADE20k; ViT-H+ matches the 8x larger 7B teacher[^dinov3-2508-10104-v1-9].
- **Reported:** cross-architecture ViT-7B to ConvNeXt distillation is non-trivial (transformer CLS versus convolution-only) but succeeds: CNX-T 42.7 versus 24.8 supervised ADE20k (+17.9), CNX-L 47.8 versus 33.3 (+14.5), large OOD gaps on IN-R/ObjectNet, and resolution scaling to 512 where supervised ConvNeXts degrade[^dinov3-2508-10104-v1-10].
- **Synthesis:** the reusable lesson is **train very large once, distill broadly** — including across architectures — for Pareto coverage from laptop to server.

## Frozen-backbone results

- **Reported:** dense linear probe with frozen 7B reaches 55.9 ADE20k, 81.1 Cityscapes, 86.6 VOC, 0.309 NYU, 2.346 KITTI, ahead of AM-RADIOv2.5, PEspatial, SigLIP2, PEcore, DINOv2, Web-DINO, and Franca; absolute 55.9 ADE20k linear approaches 63.0 supervised SOTA[^dinov3-2508-10104-v1-11].
- **Reported:** global linear probe reaches 88.4 IN1k val, 81.4 V2, 90.4 ReaL, 91.1 R, 71.3 S, 86.9 A, 19.6 C (best), 79.0 ObjectNet — first SSL result comparable to weakly-supervised PE/SigLIP2 and supervised ViT-22B on classification and OOD robustness[^dinov3-2508-10104-v1-11].
- **Reported:** video attentive probe (4-layer transformer, per-frame patches) gives 93.5/93.5 UCF101 single/TTA, 70.1/70.8 SSv2, 87.8/88.2 K400, in PEcore/SigLIP2 range and above DINOv2/AM-RADIO, behind dedicated video model V-JEPA2 on motion-heavy SSv2[^dinov3-2508-10104-v1-11].

## Satellite domain transfer

- **Reported:** SAT-493M satellite 7B uses identical hyperparams except RGB normalization, 493M Maxar 0.6m 512px images, 100K pre-train plus 10K Gram plus 8K HR512, distilled to ViT-L; canopy-height DPT on frozen backbone sets SOTA on SatLidar val/test and Open-Canopy (MAE 2.2/3.2/2.02) with distilled ViT-L best on Neon 2.4[^dinov3-2508-10104-v1-12].
- **Reported:** frozen RGB-only DINOv3 leads 12/15 GEO-Bench plus LoveDA/iSAID/DIOR tasks against multispectral fine-tuned Prithvi-v2, DOFA, BillionFM, SkySenseV2; web 7B is competitive on semantic tasks (81.6 mean classification, 75.9 mean segmentation) while satellite excels on metric depth-like tasks — evidence for task-dependent domain pretraining[^dinov3-2508-10104-v1-12].
- **Synthesis:** for detection reuse, prefer satellite-pretrained features for metric or sensor-specific geometry and web-pretrained features for semantic boundaries, both frozen with a light decoder.

## Two transfer branches

- **Reported:** DEIMv2 (arXiv `2509.20787v4`) is now compiled from its primary paper rather than the synthesis row: X/L use official DINOv3 ViT-S+ / ViT-S (12 layers, 384-dim) while M/S distill ViT-T+ 256-dim / ViT-T 192-dim from ViT-Small, preserving 12-layer depth across S to X; ultra-light Nano/Pico/Femto/Atto instead prune HGNetv2-B0[^deimv2-2509-20787-v4-1].
- **Reported:** its Spatial Tuning Adapter converts DINOv3 single-scale 1/16 outputs from blocks such as 5th/8th/11th into multi-scale features by parameter-free bilinear interpolation plus Bi-Fusion `1x1` convolutions and a fast-downsampled fine-detail branch, explicitly compensating for DINOv3 strong semantics but weak fine-grained detail; COCO `val2017` gains therefore concentrate on AP_M/AP_L while AP_S barely moves[^deimv2-2509-20787-v4-2][^deimv2-2509-20787-v4-3].
- **Reported:** primary numbers replacing the synthesis row are X 57.8 AP (50.26M), S 50.9 AP (9.71M, first reported sub-10M above 50 AP), and Pico 38.5 AP (1.51M); full closed-set tables live in [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md)[^deimv2-2509-20787-v4-3].
- **Reported:** RT-DETRv4 (arXiv `2510.25257v1`) is now compiled from its primary paper rather than the synthesis row: a frozen DINOv3-ViT-B teacher supervises only the AIFI output `F5` through a lightweight projector with patch-wise cosine loss, while Gradient-guided Adaptive Modulation steers the auxiliary weight by AIFI gradient share; the detector architecture is unchanged at inference so S/M/L/X keep DEIM-scale params/FLOPs/latency and reach 49.7/53.5/55.4/57.0 COCO AP at 273/169/124/78 FPS T4[^rtdetrv4-2510-25257-v1-1][^rtdetrv4-2510-25257-v1-2][^rtdetrv4-2510-25257-v1-3][^rtdetrv4-2510-25257-v1-4].
- **Reported:** ablations show the transfer is position-sensitive and broadly applicable: `F5`-only alignment gains +0.5 AP where backbone or hybrid alignment gives none, linear projector beats MLP/1×1 conv, cosine beats MSE, GAM 55.4 beats best static `λ=20` 55.1, and DSI-plus-GAM improves RT-DETRv2-L, D-FINE-L, and DEIM-L alike; discussion claims the framework is agnostic to VFM type and scale and adds minimal training cost[^rtdetrv4-2510-25257-v1-5].
- **Synthesis:** DEIMv2 keeps foundation features closer to runtime via adapters, while RT-DETRv4 keeps the teacher training-only; prefer RT-DETRv4-style deep-feature distillation when inference architecture is frozen, and DEIMv2-style adapters when runtime can afford foundation backbone plus detail branch.

## NAS returns for Pareto search

- **Reported:** RF-DETR (arXiv `2511.09554v2`) is now compiled from its primary paper rather than the synthesis row: it modernizes LW-DETR by replacing CAEv2 with DINOv2, switching the projector to layer norm for consumer-GPU gradient accumulation, and training scheduler-free (EMA without warm-up, LR `1e-4`, symmetric `0.5–1.5` multiscale, batch-level resize, only horizontal-flip plus random-crop) to avoid COCO-specific scheduler/augmentation bias[^rfdetr-2511-09554-v2-1].
- **Reported:** backbone ablation (M, 60 O365 epochs, gentler hyperparameters): CAEv2 ViT/S-16 `52.3` AP, DINOv2 ViT/S-14 `54.3` AP, SigLIPv2 ViT/B-32 `50.4` AP, SAM2 Hiera-S `53.6` AP at `11.2` ms; paper attributes Hiera slowness to missing FlashAttention/TensorRT optimization and notes the lack of lightweight ViT-S/T foundation variants for real-time use[^rfdetr-2511-09554-v2-2].
- **Reported:** RF100-VL backbone trends hold on the RF20-VL subset (CAEv2 `64.4`, DINOv2 `65.2`, SigLIPv2 `62.2`, Hiera-S `65.2` AP), and Objects-365 pretraining plus SAM2 pseudo-masks for the segmentation head lifts the M baseline from `53.6` to `54.3` before NAS reaches `54.6`[^rfdetr-2511-09554-v2-2].
- **Reported:** RF-DETR-Seg reuses the same detector backbone and NAS with a lightweight mask branch (bilinearly upsampled encoder map plus projector to pixel embeddings, dot product with per-decoder-layer query embeddings); this keeps segmentation searchable by the same decoder-depth/query knobs without multi-scale backbone features[^rfdetr-2511-09554-v2-3].
- **Synthesis:** this matters most for industrial vision where CCTV, Jetson Orin, T4 server, aerial small-object, and microscopy optima differ; **DINOv2 preservation (low LR, layer decay, layer norm) plus weight-sharing NAS plus short per-dataset search/fine-tuning** is the reusable pipeline to watch, with full COCO/RF100-VL numbers in [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md).

## Relationships

- Complemented by [Hybrid Mamba-Transformer vision backbone](hybrid-mamba-transformer-vision-backbone.md) as a non-foundation-model supervised backbone alternative.
- Uses [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) as the deploy-time architecture receiving distilled signals.
- Supports [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md) where semantic quality depends on foundation representations.
- Constrained by [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) hardware and resolution limits.

## Contradictions

- None within this source. Vendor-reported AP figures should not be compared as if from one leaderboard.

## Coverage limits

- All scale, AP, parameter, and FPS figures are **reported**, not reproduced; Meta, arXiv, and GitHub evidence behind them was not fetched.
- **Observed** by static inspection: `raw/arXiv-2508.10104v1/main.tex`, `preamble.tex`, `chapters/introduction.tex`, `related_work.tex`, `system.tex`, `gram.tex`, `post_training.tex`, `results.tex`, `family.tex`, `satellite.tex`, `conclusion.tex`, `environmental_impact.tex`, plus `appendix/artifacts.tex`, `experimental_details.tex`, `implementation_details.tex`, `results.tex` fully read; `00README.json` read; `main.bbl`, `tmlr.sty`, `fancyhdr.sty` excluded as generated/vendored; `figures/**/*.tex`, `figures/**/*.pdf`, `images/**/*.jpg`, `images/**/*.png` not visually inspected beyond captions and body-text reproduction, with numeric claims tabulated in `.tex`. No code was executed.
- **Observed** by static inspection: `raw/arXiv-2509.20787v4/main.tex` plus `sec/0_abstract.tex`, `sec/1_intro.tex`, `sec/3_method.tex`, `sec/4_experiments.tex`, `sec/6_conclusions.tex`, `sec/teaser.tex`, `preamble.tex`, and `00README.json` fully read; `main.bib` checked for citation closure; `cvpr.sty` plus `ieeenat_fullname.bst` excluded as vendored templates; `figures/STA_ver3.pdf`, `figures/deimv2_coco_AP_vs_GFLOPs.pdf`, and `figures/deimv2_coco_AP_vs_Params.pdf` not visually inspected beyond captions and body-text reproduction, with AP-params-FLOPs claims tabulated in `.tex` tables. No code was executed.
- **Observed** by static inspection: `raw/arXiv-2510.25257v1/main.tex` plus `sec/0_absv2.tex`, `sec/1_intro.tex`, `sec/2_related_work.tex`, `sec/3_method.tex`, `sec/4_experiments.tex`, `sec/5_discussion.tex`, `sec/6_conclusion.tex`, `sec/exp_results.tex`, `sec/exp_results2.tex`, `sec/exp_results3.tex`, and `00README.json` fully read; `main.bib` checked for citation closure; `cvpr.sty` plus `ieeenat_fullname.bst` excluded as vendored templates; `main.bbl` excluded as generated bibliography output; `figures/*.pdf` not visually inspected beyond captions and body-text reproduction, with DSI/GAM and AP-latency claims tabulated in `.tex`. No code was executed; promised code and model URLs were not fetched.
- Carbon cost is **reported**: 61,440 H100 GPU-hours, 47 MWh, 18 tCO2eq for ViT-7B pre-training at PUE 1.1 and 0.385 kgCO2eq/kWh; ~9M GPU-hours total project ~2600 tCO2eq[^dinov3-2508-10104-v1-13].
- **Observed** by static inspection: `raw/arXiv-2511.09554v2/iclr2026_conference.tex` plus `supplement.tex` fully read for DINOv2-versus-CAEv2/SigLIPv2/Hiera-S ablations, Objects-365 plus SAM2 pseudo-mask pretraining, and scheduler-free preservation settings; figures excluded beyond captions/body text as in the detection concept. No code was executed.
- MambaVision hybrid Mamba-Transformer backbone is compiled separately in [Hybrid Mamba-Transformer vision backbone](hybrid-mamba-transformer-vision-backbone.md); the source row here remains as landscape mention only[^reseach-2026-09-17-6].

[^deimv2-2509-20787-v4-1]: `raw/arXiv-2509.20787v4/main.tex`, title/authors plus `sec/1_intro.tex` Sec. Introduction Tab. `tab:main` and `sec/3_method.tex` Sec. Method / ViT-based versus HGNetv2-based variants — official ViT-S/S+ versus distilled ViT-T/T+ depths/dims, HGNetv2 pruning scope.
[^deimv2-2509-20787-v4-2]: `raw/arXiv-2509.20787v4/sec/3_method.tex`, Sec. Method / Spatial Tuning Adapter; Fig. `fig:STA` via caption and body text — bilinear multi-block pyramidization versus ViTDet deconvolution, Bi-Fusion plus detail branch.
[^deimv2-2509-20787-v4-3]: `raw/arXiv-2509.20787v4/sec/0_abstract.tex` Abstract plus `sec/4_experiments.tex` Sec. Experiments plus `sec/3_method.tex` Tabs. `tab:XLMS`/`tab:my_sorted_label_asc` — X/S/Pico AP/params, medium/large versus small-object split, DINOv3 semantics versus detail limit.
[^reseach-2026-09-17-1]: `raw/reseach.md`, section “4. Vision Foundation Model trở thành backbone/teacher”.
[^reseach-2026-09-17-3]: `raw/reseach.md`, table row “DEIMv2” and section “9. Edge/mobile”.
[^reseach-2026-09-17-4]: `raw/reseach.md`, table row “RT-DETRv4 – ECCV 2026”.
[^reseach-2026-09-17-5]: `raw/reseach.md`, table row “RF-DETR” and section “5. NAS đang quay lại” — now superseded for RF-DETR backbone/pretraining claims by the primary paper below.
[^rfdetr-2511-09554-v2-1]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Sec. Incorporating Internet-Scale Priors plus Training Schedulers and Augmentations Bias Model Performance and `supplement.tex` Sec. Implementation Details — DINOv2 replacement, layer-norm projector, LR/batch/decay/EMA/multiscale/batch-resize scheduler-free choices.
[^rfdetr-2511-09554-v2-2]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Tab. `tab:backbone` plus `supplement.tex` Tab. `tab:backbone-rf20vl` and Tab. `tab:nas` — backbone AP/latency/FLOPs, RF20-VL replication, O365 compensation for gentler hyperparameters.
[^rfdetr-2511-09554-v2-3]: `raw/arXiv-2511.09554v2/iclr2026_conference.tex`, Sec. Real-Time Instance Segmentation plus Fig. `fig:arch` — shared low-resolution map, pixel-embedding projector, per-layer query dot product, no multi-scale backbone features, SAM2 pseudo-label O365 pretraining, YOLACT-prototype reading.
[^reseach-2026-09-17-6]: `raw/reseach.md`, table row “MambaVision – CVPR”.
[^dinov3-2508-10104-v1-1]: `raw/arXiv-2508.10104v1/main.tex`, Abstract plus `chapters/introduction.tex`, Sec. Introduction and `chapters/conclusion.tex`, Sec. Conclusion — scaling plus Gram Anchoring plus post-training claims.
[^dinov3-2508-10104-v1-2]: `raw/arXiv-2508.10104v1/chapters/system.tex`, Sec. Training at Scale Without Supervision / Data Preparation plus Tab. `table:data_ablation` — 17B pool, LVD-1689M clustering/retrieval/raw mix, 10% ImageNet1k homogeneous batches.
[^dinov3-2508-10104-v1-3]: `raw/arXiv-2508.10104v1/chapters/system.tex`, Sec. Large-Scale Training with Self-Supervision plus Tab. `tab:models_comparison` — ViT-7B arch, DINO+iBOT+DKoleo loss, Sinkhorn-Knopp, dedicated LayerNorm, RoPE-box jittering, constant schedule, AdamW batch 4096 on 256 GPUs, 2x256 plus 8x112 multi-crop.
[^dinov3-2508-10104-v1-4]: `raw/arXiv-2508.10104v1/chapters/gram.tex`, Sec. Gram Anchoring / Loss of Patch-Level Consistency plus Fig. `fig:gram:evolution` and `fig:evolution-cosines` — global up / dense down after 200K, Gram loss Eq. `eq:gram-loss` and `L_Ref` definition.
[^dinov3-2508-10104-v1-5]: `raw/arXiv-2508.10104v1/chapters/gram.tex`, Sec. Leveraging Higher-Resolution Features plus Fig. `fig:gram` / Tab. `tab:gram-teacher-res` and Fig. `fig:evolution-gram`, `fig:gram-matrices-comp` — 2x teacher plus downsampling, HRef gains.
[^dinov3-2508-10104-v1-6]: `raw/arXiv-2508.10104v1/appendix/artifacts.tex`, Sec. Artifacts and Outliers in Large-Scale Training — 4 registers versus attention bias/value gating Tab. `tab:outliers-regis-attention` and Fig. `fig:outliers`, plus feature-dimension outlier handling.
[^dinov3-2508-10104-v1-7]: `raw/arXiv-2508.10104v1/chapters/post_training.tex`, Sec. Post-Training / Resolution Scaling / Model Distillation plus Fig. `fig:distillation_diagram` — mixed-resolution HRFT with Gram, fixed-teacher distillation, multi-student sharing.
[^dinov3-2508-10104-v1-8]: `raw/arXiv-2508.10104v1/chapters/post_training.tex`, Sec. Aligning DINOv3 with Text plus `chapters/family.tex`, Sec. Zero-shot Inference with Tab. `tab:dino_txt` — LiT frozen backbone, CLS plus mean-pooled patches.
[^dinov3-2508-10104-v1-9]: `raw/arXiv-2508.10104v1/chapters/family.tex`, Sec. Evaluating the Full Family plus Tab. `tab:family-models-flops`, Tab. `tab:family:distillation`, Fig. `fig:family:vith-7b` — ViT-S/S+/B/L/H+/7B params, FLOPs, ADE20k/NYU/DAVIS and H+ versus 7B parity.
[^dinov3-2508-10104-v1-10]: `raw/arXiv-2508.10104v1/chapters/family.tex`, Sec. Efficient ConvNeXts plus Tab. `tab:family:convnext` — distilled versus supervised ConvNeXt, IN-ReAL/R/ObjectNet at 256/512, ADE20k/NYU gaps.
[^dinov3-2508-10104-v1-11]: `raw/arXiv-2508.10104v1/chapters/results.tex`, Sec. Results / Dense Linear Probing Tab. `tab:results-linear-dense`, Classification Tab. `tab:results-imagenet-classification`, Fine-grained Tab. `tab:results-classification-fine`, Video Tab. `tab:results-video-classification` — frozen-protocol SOTA claims.
[^dinov3-2508-10104-v1-12]: `raw/arXiv-2508.10104v1/chapters/satellite.tex`, Sec. DINOv3 on Geospatial Data plus Tab. `tab:canopy`, Tab. `tab:Geobench`, Tab. `tab:sat_highres` — SAT-493M training, canopy MAE/R2, GEO-Bench RGB-only frozen versus multispectral fine-tuned.
[^dinov3-2508-10104-v1-13]: `raw/arXiv-2508.10104v1/chapters/environmental_impact.tex`, Sec. Environmental Impact plus Tab. `tab:carbon` — H100 power, PUE, carbon intensity, 47 MWh and project total.
[^rtdetrv4-2510-25257-v1-1]: `raw/arXiv-2510.25257v1/main.tex`, title/authors plus `sec/0_absv2.tex` Abstract and `sec/1_intro.tex` Sec. Introduction — DSI plus GAM contributions, S/M/L/X 49.7/53.5/55.4/57.0 AP at 273/169/124/78 FPS, training-only zero-overhead thesis.
[^rtdetrv4-2510-25257-v1-2]: `raw/arXiv-2510.25257v1/sec/3_method.tex`, Sec. Method / Overview plus Deep Semantic Injector Eqs. `eq:reshape`–`eq:project` and `eq:cos_sim` — AIFI-only `S5→F5` bottleneck, ViT reshape/interpolate/project alignment, three injection configs.
[^rtdetrv4-2510-25257-v1-3]: `raw/arXiv-2510.25257v1/sec/3_method.tex`, Sec. Gradient-guided Adaptive Modulation Eqs. `eq:component`–`eq:update_method` — L1 gradient norms, AIFI ratio, `ρ`/`δ` interval, boundary-steered `λ` update.
[^rtdetrv4-2510-25257-v1-4]: `raw/arXiv-2510.25257v1/sec/4_experiments.tex`, Sec. Setup plus Comparison with SOTA and Tab. `tab:comparison` — COCO `train2017`/`val2017`, frozen DINOv3-ViT-B teacher, T4 TensorRT FP16, S/M/L/X AP/FPS and YOLO/DEIM/DEIMv2 comparisons.
[^rtdetrv4-2510-25257-v1-5]: `raw/arXiv-2510.25257v1/sec/4_experiments.tex` Ablation Study plus `sec/exp_results.tex` Tab. `tab:ablation_main`, `sec/exp_results2.tex` Tab. `tab:semantic_location`, `sec/exp_results3.tex` Tabs. `tab:ablation_projector`/`tab:ablation_loss`/`tab:ablation_gam` plus `sec/5_discussion.tex` Discussion — position/projector/loss/weighting ablations, cross-detector transfer, VFM-agnostic and minimal-training-cost claims.
