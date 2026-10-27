---
type: Concept
title: LightOnOCR-3 training
description: LightOnOCR-3 training combines resampled OCR data, multi-model grounding annotation with quality gates, and GRPO with task-specific verifiable rewards.
tags: [ml, ocr, visual-grounding, training, reinforcement-learning]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:11:56Z }
sources:
  - id: lightonocr-3-blog
    resource: ../raw/lightonocr-3/index.md
    scope: ../raw/lightonocr-3/
    kind: article
    title: "LightOnOCR-3: High-Performance OCR and Layout Extraction in One Model"
---

# LightOnOCR-3 training

**Reported:** LightOn trains [LightOnOCR-3](lightonocr-3.md) using a rebalanced supervised mixture and a grounding dataset built by aligning reference transcriptions with multiple independent detectors. It then applies GRPO with different rewards for grounded pages, verifiable synthetic pages, and blank pages. These are vendor descriptions, not an independently inspected training run.[^lightonocr-3-blog]

## Supervised data and grounding

Formula pages receive 2× and tables 3× sampling weight; the mixture is cleaned and MinHash-deduplicated, with handwriting and DocDuck synthetic pages added, including 20+ languages and adversarial typography. The configured task mixture is 78.1% OCR and 21.9% grounding. The authors report Muon, sequence packing and extensive image augmentation; these are recipe choices, not individually established causal improvements.[^lightonocr-3-blog]

The annotation pipeline uses LightOnOCR-2-1B as the transcription reference, PP-OCRv6 line detection and recognition, PP-DocLayoutV3 and Docling regions, and docTR word detections. Fuzzy text matching and reading-order constraints align detector geometry to the reference's logical blocks rather than replacing its text. Automated audits reject missing, duplicated or unsupported assignments and geometry/table conflicts. The authors report retaining 55% of elements initially and recovering about 10% additional samples with intermediate checkpoints; the source uses different denominators, so these numbers should not be summed as a precise acceptance rate.[^lightonocr-3-blog]

Qwen3-VL-235B annotates each figure from a page plus tight crop, producing a kind, content and confidence. Charts become one flat HTML table; other figures receive short descriptions. Acceptance requires valid format, confidence ≥0.5, no failed or truncated outputs, and chart heuristics rejecting identical columns, three repeated values, or a value filling ≥60% of numeric cells. A page enters training only if all figures pass; failed regions are retried under the same gates. **Synthesis:** these heuristics can also reject genuinely repetitive chart data; the article does not quantify false rejection rates.[^lightonocr-3-blog]

## Reinforcement learning

Two manually verified grounding sets contain 983 pages averaging 31.5 boxes and 1,654 averaging 13.0 boxes; their prompt shares are 38% and 37%, with 23% synthetic checks and 2% empty pages. For grounding, predictions and references are greedily matched once by overlap with matching labels, and the sum of `min(IoU/0.75, 1)` is divided by the larger box count. Synthetic pages use the mean of their checks; empty pages reward immediate EOS. Each page uses just one branch.[^lightonocr-3-blog]

The reported GRPO recipe uses group size eight and verl's asynchronous one-step-off-policy trainer, with vLLM rollouts and training on separate GPU pools. Each seed uses 600 unique pages and shares only 14–15% with another seed; parameters from different seeds are averaged. The source states the intention to reduce sample sensitivity, but gives no controlled ablation establishing the gain.[^lightonocr-3-blog]

## Coverage and relationships

- **Supports:** [LightOnOCR-3](lightonocr-3.md); [evaluation](lightonocr-3-evaluation.md) records reported outcomes separately.
- The article and 11 local image assets were inspected; illustrative diagrams largely repeat the prose. The RL mixture image supplies the exact 38/37/23/2 split. External repositories, model weights, interactive example and benchmark iframes were not inspected or executed. Exact dataset provenance, training compute and independent validation are not established. Draft reflects these limits.[^lightonocr-3-blog]

[^lightonocr-3-blog]: Taghadouini, Cavaillès and Aubertin, [LightOnOCR-3 blog](../raw/lightonocr-3/index.md), §§ 3.1–3.3; `assets/1545-aP4gpn8QCBtnN5xl.png` (RL mixture), `assets/QdMr4Rre3KdF3KZ9oSHvi.png` (annotation pipeline).
