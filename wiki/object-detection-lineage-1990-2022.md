---
type: Concept
title: Object detection lineage from handcrafted to Transformer detectors
description: How VJ, HOG, DPM, R-CNN family, YOLO/SSD/RetinaNet, keypoint and DETR detectors plus VOC/COCO datasets and AP metrics evolved from the 1990s to 2022.
tags: [detection, lineage, datasets, metrics, survey]
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

Synthesis: the survey frames 1990s–2022 as traditional detection before 2014 versus deep-learning detection after 2014, with accuracy on VOC07/VOC12/MS-COCO rising through proposals, pyramids, one-stage designs, and finally set prediction[^zou-survey-v3-1].

## Traditional detectors

- **Reported:** Viola–Jones (2001) first real-time unconstrained face detection on 700 MHz Pentium III via sliding windows plus integral image, feature selection, and detection cascades, tens to hundreds of times faster than contemporaries[^zou-survey-v3-2].
- **Reported:** HOG (2005, Dalal–Triggs) dense grid of cells with overlapping block normalization, motivated by pedestrian detection; rescaled the image while fixing window size, and underpinned DPM and exemplar methods[^zou-survey-v3-3].
- **Reported:** DPM (2008 Felzenszwalb, extended by Girshick to mixture models) decomposed objects into parts under divide-and-conquer; winners of VOC-07/-08/-09, with durable insights on mixture models, hard-negative mining, bounding-box regression, and context priming[^zou-survey-v3-4].

## CNN two-stage detectors

- **Reported:** R-CNN (2014) used selective-search proposals rescaled into an ImageNet-pretrained CNN plus linear SVMs; VOC07 mAP rose from 33.7% (DPM-v5) to 58.5%, at ~14 s per image on GPU due to ~2,000 overlapping proposals[^zou-survey-v3-5].
- **Reported:** SPPNet (2014) added a spatial-pyramid-pooling layer for fixed-length representations of any-size regions, computing feature maps once; reported >20× faster than R-CNN at VOC07 59.2% without accuracy loss[^zou-survey-v3-6].
- **Reported:** Fast R-CNN (2015) jointly trained detector plus box regressor; reported VOC07 70.0% and >200× faster than R-CNN, still limited by external proposals[^zou-survey-v3-7].
- **Reported:** Faster R-CNN (2015) introduced the Region Proposal Network for nearly cost-free proposals; reported as first near-real-time deep detector (COCO mAP@.5 42.7%, VOC07 73.2%, 17 fps with ZF-Net), integrating proposal, feature, and regression stages[^zou-survey-v3-8].
- **Reported:** FPN (2017) added a top-down architecture with lateral connections for high-level semantics at all scales; in basic Faster R-CNN reported COCO mAP@.5 59.1%[^zou-survey-v3-9].

## CNN one-stage, keypoint, and Transformer detectors

- **Reported:** YOLO (2015) was the first one-stage deep detector: one network on the full image dividing it into regions and predicting boxes plus probabilities jointly; fast version 155 fps at VOC07 52.7%, enhanced 45 fps at 63.4%, with weaker small-object localization; later v2/v3/v4 and YOLOv7 added multi-scale focus, dynamic label assignment, and reparameterization across ~5–160 FPS[^zou-survey-v3-10].
- **Reported:** SSD (2015) introduced multi-reference and multi-resolution detection, detecting different scales on different network layers rather than only the top layer; reported COCO mAP@.5 46.5% with a fast 59 fps version[^zou-survey-v3-11].
- **Reported:** RetinaNet (2017) attributed the one-stage accuracy gap to extreme foreground–background imbalance and introduced focal loss reshaping cross-entropy toward hard examples; reported COCO mAP@.5 59.1% at high speed[^zou-survey-v3-12].
- **Reported:** CornerNet (2018) reframed detection as corner-keypoint prediction plus embedding-based regrouping to avoid anchors, imbalance, and hand-tuned hyperparameters; reported COCO mAP@.5 57.8%[^zou-survey-v3-13].
- **Reported:** CenterNet (2019, objects-as-points) treats an object as its center and regresses size, orientation, location, and pose without grouping or NMS; reported COCO mAP@.5 61.1% and a unified framing extensible to 3D, pose, flow, and depth[^zou-survey-v3-14].
- **Reported:** DETR (2020) reframed detection as set prediction with Transformers and attention-only global context, without anchors or anchor points; Deformable DETR addressed slow convergence and small objects, reported COCO mAP@.5 71.9%[^zou-survey-v3-15].

## Datasets and metrics

- **Reported:** dataset scale grew from VOC07 (5,011 trainval images, 12,608 objects, 20 classes) and VOC12 (11,540 trainval, 27,450 objects) to ILSVRC (~476,688 trainval, 534,309 objects, 200 classes), COCO-2017 (123,287 trainval, 896,782 objects, 80 classes with per-instance masks, more small <1% area and dense objects), Objects365 (~638k trainval, ~10.1M objects), and Open Images (~1.78M trainval, ~14.9M boxes, 600 classes plus visual-relationship task)[^zou-survey-v3-16].
- **Reported:** metric evolution moved from miss-rate versus false positives per window, judged flawed for full-image performance, to Caltech FPPI from 2009; VOC2007 AP averaged precision over recalls per category with mean AP over classes and IoU >0.5 as detected versus missed; COCO averages AP over IoU 0.5–0.95 to reward precise localization, relevant to grasping and similar tasks[^zou-survey-v3-17].
- **Synthesis:** VOC established comparable detection, ILSVRC scaled categories and images by ~100× over VOC, COCO added instance masks and small-object pressure to become the de facto standard, and Open Images scaled boxes and relations further.

## Relationships

- Uses [Object detection building blocks and speed-up techniques](object-detection-building-blocks-speedup.md) for the multi-scale, context, loss, and NMS mechanisms behind the milestone gains.
- Contrasts with [Real-time end-to-end detection without NMS](real-time-end-to-end-detection.md), which continues the lineage after 2022 with dense-training/sparse-inference NMS-free designs and 2024–2026 COCO numbers.
- Supports [Efficient video, edge, and small-object detection](efficient-video-edge-small-object-detection.md) as historical context for cascades, pyramids, and small-object limits.
- Precedes [Vision foundation models for detection](vision-foundation-models-for-detection.md) and [Open-vocabulary promptable perception](open-vocabulary-promptable-perception.md), which replace the backbones and fixed taxonomies assumed here.

## Contradictions

- None within this source. Reported mAP and fps values come from different papers, backbones, and protocols across 2001–2022; treat small gaps as non-comparable without a shared setup.

## Coverage limits

- All detector, dataset, and metric figures are **reported** from the survey, not reproduced; original papers, benchmarks, and external URLs in `egbib.bib` were not fetched.
- **Observed** by static inspection: entry point `main.tex` (582 lines) fully read; `egbib.bib` sampled for identity; `main.bbl` excluded as generated bibliography; `IEEEtran.cls` excluded as vendored class; author portrait images excluded as decorative; technical PDFs/PNGs in `imgs/` not visually inspected, with material trends captured only via prose, captions, and tables.
- No code was executed; survey claims to 2022 supersede v1/v2 scope but later 2024–2026 advances live in existing SOTA concepts.

[^zou-survey-v3-1]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2, Fig. mile-stones and Fig. accuracy-improvements — two-period framing and VOC/COCO trajectory.
[^zou-survey-v3-2]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.1, VJ paragraph — sliding windows, integral image/feature selection/cascades, 700 MHz CPU claim.
[^zou-survey-v3-3]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.1, HOG paragraph — dense cells, block normalization, pedestrian motivation, multiscale rescaling.
[^zou-survey-v3-4]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.1, DPM paragraph — star-model to mixture models, VOC wins, listed insights.
[^zou-survey-v3-5]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.2, RCNN paragraph — selective search plus ImageNet CNN plus SVM, VOC07 33.7% to 58.5%, 14 s and 2,000 proposals.
[^zou-survey-v3-6]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.2, SPPNet paragraph — SPP layer, compute-once, >20× faster, VOC07 59.2%.
[^zou-survey-v3-7]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.2, Fast RCNN paragraph — joint detector plus regressor, VOC07 70.0%, >200× faster, proposal bottleneck.
[^zou-survey-v3-8]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.2, Faster RCNN paragraph — RPN, COCO mAP@.5 42.7%, VOC07 73.2%, 17 fps ZF-Net.
[^zou-survey-v3-9]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.2, FPN paragraph — top-down plus lateral, all-scale semantics, COCO mAP@.5 59.1%.
[^zou-survey-v3-10]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, YOLO paragraph — first one-stage, region plus box plus probability, 155 fps/52.7% and 45 fps/63.4%, small-object drop, v2/v3/v4/v7 note.
[^zou-survey-v3-11]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, SSD paragraph — multi-reference/multi-resolution, per-layer scales, COCO mAP@.5 46.5%, 59 fps.
[^zou-survey-v3-12]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, RetinaNet paragraph — imbalance cause, focal loss, COCO mAP@.5 59.1%.
[^zou-survey-v3-13]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, CornerNet paragraph — keypoint plus embedding regrouping, COCO mAP@.5 57.8%.
[^zou-survey-v3-14]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, CenterNet paragraph — center point plus attribute regression, no grouping/NMS, COCO mAP@.5 61.1%.
[^zou-survey-v3-15]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.1.3, DETR paragraph — set prediction with Transformers, anchor-free, Deformable DETR COCO mAP@.5 71.9%.
[^zou-survey-v3-16]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.2.1 and Tab. objdet_datasets, Fig. dataset-examples — dataset statistics and qualitative shifts.
[^zou-survey-v3-17]: `raw/arXiv-1905.05055v3/main.tex`, Sec. 2.2.2 — FPPW limits, Caltech FPPI, VOC AP/mAP with 0.5 IoU, COCO multi-threshold AP.
