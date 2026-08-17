---
type: Model System
title: Rex-Omni
description: Rex-Omni is a 3B vision-language model that unifies detection, grounding, OCR, and keypoint tasks as quantized point-sequence generation refined with geometry-aware GRPO.
tags: [visual-grounding, object-detection, ocr, reinforcement-learning, vision-language-models]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:35:49Z }
sources:
  - id: rex-omni-paper
    resource: "../raw/2510.12798_Detect Anything via Next Point Prediction/main.tex"
    title: Detect Anything via Next Point Prediction
---

# Rex-Omni

Rex-Omni is a Qwen2.5-VL-3B-Instruct derivative that casts heterogeneous visual-perception tasks as generation of coordinate-token sequences. Its central training result is that large-scale supervised fine-tuning (SFT) teaches localization, while geometry-aware GRPO post-training primarily improves autonomous output behavior—reducing duplicate and oversized-box predictions—rather than substantially sharpening already matched coordinates.[^rex-omni-paper]

## Unified coordinate interface

The model repurposes the final 1,000 vocabulary entries as single-token relative coordinates from 0 to 999, adding no parameters. Natural-language instructions select the task, while outputs combine a phrase with coordinates:[^rex-omni-paper]

- one point for pointing and GUI interaction;
- two points (`x0, y0, x1, y1`) for bounding boxes;
- four or more points for OCR polygons;
- a box plus named points in JSON for keypoint detection.

Visual prompts are also serialized as coordinate tokens in the text interface. Compared with multi-token numeric coordinates, this representation shortens dense outputs: on 100 sampled COCO images, the paper reports 7.6 output tokens per box for Rex-Omni versus 148.8 for SEED1.5-VL; on Dense200, 5.1 versus 74.5. Generation nevertheless remains autoregressive and scales with object count, reportedly exceeding 16 seconds for 410–419 boxes on one A100 with vLLM/BF16.[^rex-omni-paper]

## Data and training

SFT uses 22 million annotated images: about 8.9 million public samples plus automatically generated grounding, referring, pointing, and OCR data. The data engines use Qwen2.5-VL-7B captions, SpaCy phrase extraction, DINO-X grounding, Molmo points, SAM masks, and PaddleOCR annotations. A notable quality-control choice removes adjective-bearing noun phrases before automatic grounding because the teacher detector may ignore modifiers and label every category instance.[^rex-omni-paper]

All parameters are updated during eight days of SFT on 64 A100 GPUs. The GRPO stage then trains on 66,000 sampled SFT examples for about 24 hours on eight A100s, using eight rollouts and three task-dependent rewards:[^rex-omni-paper]

- **Box IoU F1 reward:** combines label-aware IoU matching with penalties for over- and under-prediction.
- **Point-in-mask F1 reward:** scores category-matched points inside SAM-derived object masks.
- **Point-in-box reward:** gives binary feedback for GUI clicks inside the target element.

This separates token learning from sequence-level geometry and behavior: cross-entropy treats nearby coordinate bins as unrelated classes and teacher forcing never exposes the model to its own malformed or repetitive prefixes, whereas rollout rewards evaluate complete free-running outputs.[^rex-omni-paper]

## What the ablations support

The strongest evidence is for behavioral correction. Removing heuristic duplicates from SFT outputs improved F1@0.5 by 15.3% on VisDrone, compared with 0.1% for the GRPO model. On Dense200, oversized boxes accounted for 20.5% of SFT outputs versus 3.5% after GRPO. By contrast, among examples where both stages predicted the correct number of matched boxes, GRPO changed mIoU-averaged F1 only from 63.0 to 63.5 on COCO and 56.6 to 56.9 on LVIS. These filtered analyses support the narrower conclusion that GRPO mostly regulates output count and structure; they do not establish a large general improvement in coordinate tightness.[^rex-omni-paper]

The paper's sampling analysis qualifies that conclusion by task complexity. On COCO, selecting the best of eight high-temperature SFT samples per example reaches 72.6 F1@0.5, above GRPO's 72.0, consistent with GRPO improving the likelihood of sampling an already latent capability. The same oracle-like selection remains below GRPO on LVIS (59.8 versus 64.3) and Dense200 (50.6 versus 78.4), so the paper's evidence also supports a deeper improvement in complex outputs; the selection uses ground truth and is an analysis, not a deployable inference procedure.[^rex-omni-paper]

## Reported task coverage

Author-reported evaluations cover common, long-tailed, dense, and referring detection; visual prompting; pointing; GUI and layout grounding; OCR; spatial pointing; and human/animal keypoints. Selected results include:[^rex-omni-paper]

- **COCO detection:** claimed zero-shot F1 of 72.0 at IoU 0.5 and 52.9 averaged over IoU thresholds, versus 68.2 and 50.4 for SFT alone. At IoU 0.95, Rex-Omni scores 15.9, below several regression detectors.
- **Layout grounding:** F1 averaged over IoU thresholds is 70.7 on DocLayNet and 55.6 on M6Doc. The closed-set DocLayout-YOLO baseline scores 81.1 on DocLayNet, so the result supports strong MLLM grounding rather than dominance over specialist layout detectors.
- **OCR:** with bounding boxes and exact text matching, Rex-Omni reports mIoU-averaged F1 of 28.0 on HierText, 28.1 on ICDAR2015, 40.6 on TotalText, and 44.8 on SROIE. It leads the listed systems on ICDAR2015 and TotalText but trails PaddleOCRv5 on HierText and SROIE.

## Contradictions

- The paper says OCR receives “consistent gains” from SFT to GRPO. Its table supports this for bounding-box outputs, but polygon mIoU-averaged F1 falls from 26.2 to 20.2 on HierText and from 39.7 to 19.2 on SROIE, with a slight 25.7-to-25.6 decline on TotalText. The broader consistency claim is therefore not supported by the displayed polygon results.[^rex-omni-paper]

## Trust limits

- Results are author-reported from the local manuscript and were not independently reproduced. The bundle supplies LaTeX, tables, and figures, but not the training data, weights, code, or evaluation scripts needed to verify the claims.[^rex-omni-paper]
- Detection uses per-category F1 after supplying ground-truth categories as prompts, not ordinary end-to-end mAP. Closed/open-set detector baselines receive confidence-threshold optimization, while most MLLMs are queried one category at a time and Rex-Omni handles all categories together; comparisons should remain tied to this protocol.[^rex-omni-paper]
- The ablation’s duplicate and large-box filters are hand-defined diagnostics. Their before/after gains clarify failure modes but do not by themselves isolate GRPO from rollout compute, reward design, or other stage differences.[^rex-omni-paper]

## Relationships

- **Built on:** Qwen2.5-VL-3B-Instruct supplies the vision-language backbone and formatting tokens.
- **Compared with:** [PP-OCRv5](pp-ocrv5.md) is the specialist OCR baseline used in the paper’s text detection-and-recognition evaluation.
- **Related approach:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) also uses GRPO with structure-sensitive rewards, but optimizes complete document-to-Markdown parsing rather than coordinate-sequence perception.

[^rex-omni-paper]: Jiang et al., *Detect Anything via Next Point Prediction*, local LaTeX source bundle at [main.tex](../raw/2510.12798_Detect%20Anything%20via%20Next%20Point%20Prediction/main.tex), including referenced section and table files (accessed 2026-08-17).