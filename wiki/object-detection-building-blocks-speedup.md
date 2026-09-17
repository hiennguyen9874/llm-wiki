---
type: Concept
title: Object detection building blocks and speed-up techniques
description: How multi-scale detection, context priming, hard-negative mining, loss design, NMS, and pipeline, backbone, and numerical acceleration evolved through 2022.
tags: [detection, building-blocks, loss, nms, speedup]
status: draft
created: 2026-09-17
generated: { by: llm-wiki-agent/1, at: 2026-09-17T12:00:00Z }
sources:
  - id: zou-survey-v3
    resource: ../raw/arXiv-1905.05055v3/main.tex
    scope: ../raw/arXiv-1905.05055v3/
    kind: paper
    revision: v3
    title: 'Object Detection in 20 Years: A Survey'
---

Synthesis: durable gains came from four reusable mechanisms — where to look at multiple scales, what surrounding context to fuse, which negatives and losses to optimize, and how to deduplicate and accelerate — rather than from any single detector[^zou-survey-v3-1].

## Multi-scale detection

- **Reported:** feature pyramids plus sliding windows (VJ through HOG/DPM) slid a fixed window over rescaled images, handling aspect variation via mixture models or per-exemplar models[^zou-survey-v3-2].
- **Reported:** object proposals avoided exhaustive search, shifting from bottom-up grouping to top-down learned proposals such as BING and RPN, then receding after one-stage detectors rose[^zou-survey-v3-3].
- **Reported:** deep regression and anchor-free designs predicted boxes directly from features (DNN detection, YOLO), then split into group-based keypoint detection plus grouping (CornerNet, ExtremeNet, CenterNet-keypoints, RepPoints) versus group-free points plus attribute regression (FCOS, CenterNet objects-as-points)[^zou-survey-v3-4].
- **Reported:** multi-reference plus multi-resolution detection became the default: anchors or points at every location plus detecting different scales on different layers (Faster R-CNN, YOLOv2, SSD, FPN, RetinaNet, FCOS, YOLOv4)[^zou-survey-v3-5].

## Context priming

- **Reported:** local context enlarges the window or receptive field around the object (facial contour for faces, background for pedestrians, MultiPath, GBDNet, MultiRegion, CoupleNet)[^zou-survey-v3-6].
- **Reported:** global context uses scene configuration, either via large receptive fields from deep, dilated, deformable, or pooled convolutions, now via non-local and Transformer full-image attention, or via recurrent sequential modeling such as ION[^zou-survey-v3-7].
- **Reported:** context interaction models object–object relations versus object–scene dependencies (DPM parts, layout, context SVM, RelationNet, spatial memory, structure-inference and rescoring networks)[^zou-survey-v3-8].

## Hard-negative mining and loss design

- **Reported:** detector training can face background-to-object imbalance around 10^7:1; early bootstrap started from few backgrounds and iteratively added misses to save compute (face/Haar/VJ, HOG/DPM)[^zou-survey-v3-9].
- **Reported:** 2014–2016 detectors largely dropped bootstrap and balanced positive/negative weights (R-CNN through Faster R-CNN/YOLO), found insufficient; after 2016 bootstrap returned (SSD, FasterPed, OHEM, RefineDet) alongside focal loss reshaping cross-entropy toward hard examples[^zou-survey-v3-10].
- **Reported:** general loss is `L(p,p*,t,t*) = L_cls + β·I(t)·L_loc` with `I=1` when `IoU{a,a*}>η` (e.g. 0.5); classification moved L2/MSE (YOLOv1/v2) to cross-entropy for probabilistic cost and gradients, plus label smoothing for overconfidence/noise and focal loss for imbalance and difficulty[^zou-survey-v3-11].
- **Reported:** localization moved L2 to Smooth-L1 (`0.5x²` if `|x|<1` else `|x|−0.5`) for outlier and explosion robustness, then to IoU loss (`−log IoU`) because equal Smooth-L1 can mean very different IoU, then G-IoU for non-overlapping boxes, DIoU adding center distance, and CIoU adding aspect ratio — three geometric criteria of overlap, distance, and ratio[^zou-survey-v3-12].

## Non-maximum suppression

- **Reported:** greedy NMS keeps the max-score box and removes neighbors by overlap threshold; limits are suboptimal top score, suppression of nearby objects, and unremoved false positives, addressed by Soft, Fitness, Softer, Adaptive, and DIoU variants[^zou-survey-v3-13].
- **Reported:** bounding-box aggregation combines or clusters overlaps into one detection (VJ, Overfeat, message-passing and weighted-fusion variants), exploiting spatial layout[^zou-survey-v3-14].
- **Reported:** learning-based NMS rescores raw detections end-to-end or imitates NMS behavior, improving occlusion and dense cases; NMS-free designs enforce one-to-one assignment with the highest-quality box (CenterNet, DETR, POTO) toward human-like end-to-end inference[^zou-survey-v3-15].

## Speed-up taxonomy

- **Reported:** three levels are detection pipeline, backbone, and numerical computation; feature-map shared computation (compute whole-image features once as in Fast HOG/Fast/Faster R-CNN) gives tens to hundreds of times acceleration[^zou-survey-v3-16].
- **Reported:** cascaded coarse-to-fine detection filters easy backgrounds cheaply and reserves heavy compute for hard windows, especially small objects in large scenes for face and pedestrian tasks[^zou-survey-v3-17].
- **Reported:** backbone savings come from iterative pruning from 1980s optimal-brain-damage onward and quantization/binarization turning floats into logical ops; lightweight design uses fewer channels with more layers, filter factorization (7×7 to 3×3 stacks or 1×k/k×1), channel factorization, group convolution (1/m cost for m groups), depthwise separable (`O(dk²c)` to `O(ck²)+O(dc)` in MobileNet/TinyDSOD), bottleneck compression at input or feature stages, and NAS for backbones and anchors (DetNAS, Auto-FPN, Hit-Detector)[^zou-survey-v3-18].
- **Reported:** numerical acceleration uses integral images from integral-differential separability (integral HOG maps gave dozens of times speedup without accuracy loss), FFT via `I∗W = F⁻¹(F(I)⊙F(W))`, and vector quantization approximating distributions with prototype vectors for inner-product acceleration[^zou-survey-v3-19].

## Recent advances to 2022 and future directions

- **Reported:** beyond sliding windows via corner/center/extreme/representative keypoints and DETR set prediction; rotation robustness via augmentation, per-orientation detectors, invariant losses, geometric transformers, and polar ROI pooling; scale robustness via SNIP image pyramids backpropagating selected scales and SNIPER crop-rescale subregions, plus adaptive zoom-in and scale-distribution rescaling[^zou-survey-v3-20].
- **Reported:** better backbones (ResNet, CSPNet, Hourglass, Swin) dominate the accuracy–speed tradeoff, with the survey noting top-10 COCO methods as Transformer-based; localization improves via iterative box refinement with non-guaranteed monotonicity, IoU-family losses, and probabilistic LocNet confidences for NMS; segmentation helps either as fixed auxiliary features or as a training-only multitask branch requiring pixel labels (Mask R-CNN/HTC)[^zou-survey-v3-21].
- **Reported:** GANs narrow small-versus-large feature gaps and synthesize feature-level occlusion; weakly supervised detection with image-level labels uses multi-instance bags, class-activation mapping, proposal ranking, masking, and GANs; domain adaptation under non-i.i.d. data uses feature regularization, adversarial image/category/object alignment, cycle-consistent transforms, or combined progressive schemes[^zou-survey-v3-22].
- **Reported:** future directions listed are lightweight edge detection, end-to-end one-to-one assignment preserving accuracy and efficiency, small objects in large scenes with attention and high-resolution lightweight nets, 3D and multi-view/multi-source fusion, video spatial-temporal reasoning under compute limits, cross-modality RGB-D/lidar/flow/sound/text/video fusion, and open-world discovery with zero-shot, incremental, and prompt-based cues[^zou-survey-v3-23].

## Relationships

- Uses [Object detection lineage from handcrafted to Transformer detectors](object-detection-lineage-1990-2022.md) for the detector and dataset timeline these mechanisms explain.
- Uses [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md) as the post-2022 continuation of NMS-free, dense-supervision, and distributional-localization ideas.
- Constrained by [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) Pareto, temporal, and small-target limits.
- Precedes [Vision foundation models for detection](vision-foundation-models-for-detection.md) and [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md), which change backbones and taxonomies but reuse these scale, context, loss, and dedup patterns.

## Contradictions

- None within this source. Refinement monotonicity is explicitly qualified as not guaranteed, and backbone or NMS variants are presented as alternatives rather than universal wins.

## Coverage limits

- All mechanisms and results are **reported** survey claims with original-paper citations, not reproduced; ablations, variance, and external evidence were not checked.
- **Observed** by static inspection: same bundle limits as the lineage concept — `main.tex` fully read, `main.bbl` and `IEEEtran.cls` excluded as generated/vendored, portraits decorative, `imgs/` evolution and speedup diagrams not visually inspected beyond prose and captions.
- No execution performed; post-2022 foundation-model, open-vocabulary, and video/edge details remain with existing SOTA concepts.

[^zou-survey-v3-1]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3–4 — building blocks plus speed-up plus recent-advances framing.
[^zou-survey-v3-2]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.1, feature-pyramids paragraph and Fig. evol-multiscale — fixed window, rescaling, mixture and exemplar solutions.
[^zou-survey-v3-3]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.1, proposals paragraph — bottom-up to learned BING/RPN, later recession.
[^zou-survey-v3-4]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.1, deep-regression paragraph — direct regression then group-based versus group-free keypoint split.
[^zou-survey-v3-5]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.1, multi-reference paragraph — anchors/points everywhere plus per-layer scales as current blocks.
[^zou-survey-v3-6]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.2, local-context paragraph and Fig. evol-context — contour, background, enlarged receptive/proposal examples.
[^zou-survey-v3-7]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.2, global-context paragraph — Gist, large-kernel/attention, non-local/Transformer, RNN/ION.
[^zou-survey-v3-8]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.2, interactive paragraph — object–object versus object–scene groupings.
[^zou-survey-v3-9]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.3 and Fig. evol-hardnegmining — 10^7:1 imbalance, bootstrap for compute in face/Haar/VJ/HOG/DPM.
[^zou-survey-v3-10]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.3, deep-learning HNM paragraph — 2014–2016 weight balancing, post-2016 OHEM/SSD/RefineDet and focal loss.
[^zou-survey-v3-11]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.4, Eq. loss_sum and classification paragraph — general form with IoU gate η, L2 to CE, label smoothing, focal loss.
[^zou-survey-v3-12]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.4, localization paragraph — Smooth-L1 formula, IoU/G-IoU/DIoU/CIoU with overlap/distance/ratio criteria.
[^zou-survey-v3-13]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.5 and Fig. evol-nms, greedy paragraph — max-score rule, three limits, Soft/Fitness/Softer/Adaptive/DIoU fixes.
[^zou-survey-v3-14]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.5, aggregation paragraph — combine/cluster overlaps, VJ/Overfeat, layout-aware variants.
[^zou-survey-v3-15]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.3.5, learning and NMS-free paragraphs — rescoring end-to-end, one-to-one highest-quality-box rule.
[^zou-survey-v3-16]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 3 and Fig. speedup, shared-computation subsection — three levels, compute-once acceleration.
[^zou-survey-v3-17]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 3.2 — coarse-to-fine cascades for backgrounds and small-in-large scenes.
[^zou-survey-v3-18]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 3.3–3.4 and Fig. conv-speedup — pruning/quantization, factorizing/group/depthwise/bottleneck/NAS with complexity formulas.
[^zou-survey-v3-19]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 3.5 and Fig. integral-HOGmap — integral separability and HOG maps, FFT theorem, VQ prototypes.
[^zou-survey-v3-20]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 4.1–4.2 and Fig. snip — keypoint/DETR liberation, rotation and SNIP/SNIPER plus adaptive scale cures.
[^zou-survey-v3-21]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 4.3–4.5 and Fig. engine-acc — backbone tradeoff and Transformer top-10 note, refinement/IoU/LocNet, segmentation-as-feature versus training-only branch.
[^zou-survey-v3-22]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 4.6–4.8 — GAN small/occluded, WSOD MIL/CAM/ranking/masking/GAN, domain image/category/object plus cycle transforms.
[^zou-survey-v3-23]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 5 — seven future directions from lightweight to open-world detection.
