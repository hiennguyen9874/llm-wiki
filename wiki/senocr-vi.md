---
type: Model System
title: SenOCR-Vi
description: SenOCR-Vi is VietAlpha Lab's 0.96B Vietnamese-specialized document OCR model, produced by a decoder-only LoRA fine-tune of PaddleOCR-VL-1.6 and released as a merged Apache-2.0 checkpoint.
tags: [ocr, document-parsing, vision-language-models, vietnamese, lora, fine-tuning, low-resource-languages]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:35:00Z }
stale_after: 2027-04-25
sources:
  - id: senocr-vi-model-card
    resource: ../raw/VietAlphaLabs-SenOCR-Vi.md
    kind: model-card
    title: "SenOCR-Vi: A Vietnamese-Specialized Document OCR Model"
---

# SenOCR-Vi

SenOCR-Vi is a Vietnamese-specialized document OCR model that retains the approximately 0.96B-parameter [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) architecture and changes only its recognition behavior through a small decoder LoRA fine-tune, merged back into one FP32 checkpoint. VietAlpha Lab reports 82.83 Vietnamese document composite and 86.7% Vietnamese text recognition under `1 - Edit_dist`, 1.93 points above the PaddleOCR-VL-1.6 base on the corrected 160-page Vietnamese population.[^senocr-vi-model-card] All quantitative claims on this page are **Reported** by the model card and were not independently reproduced here.

## Identity and interface

- **Publisher and license:** VietAlpha Lab, Hugging Face model card, Apache License 2.0; the base PaddleOCR-VL-1.6 is also Apache 2.0. Declared languages are Vietnamese, English, and Chinese.[^senocr-vi-model-card]
- **Release shape:** 958,588,736 total parameters in a single merged FP32 checkpoint, with no separate adapter branch needed at inference. The cited preprint year is 2026; the card states no model revision or release date.[^senocr-vi-model-card]
- **Drop-in interface:** identical to PaddleOCR-VL-1.6. It can be called through `transformers` (`transformers>=5.0.0`) for element-level recognition with the `OCR:` prompt, or used as the VLM recognition model inside the PaddleOCR-VL 1.6 page-parsing pipeline (`paddleocr[doc-parser]>=3.6.0`, `pipeline_version="v1.6"`, `vl_rec_model_dir`).[^senocr-vi-model-card]
- **Precision caveat:** the qualified benchmark artifact was served in FP32, and the card states that lower-precision deployment should be validated separately for the target environment.[^senocr-vi-model-card]

## Training

The card describes a fresh decoder-only LoRA fine-tune: the vision encoder, vision-language aligner/projector, embeddings, and LM head stayed frozen, and LoRA was applied to seven projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`) in each of 18 decoder layers, for 126 adapted projections total.[^senocr-vi-model-card]

| Setting | Value |
|---|---:|
| Total parameters | 958,588,736 |
| Trainable parameters | 12,091,392 (1.2614%) |
| LoRA rank / alpha / scaling | 32 / 64 / 2.0 |
| Training records | 42,254 |
| Target tokens per corpus pass | 1,171,860 |
| Effective corpus passes | 3.000521 |
| Target-token exposures | ~3.516M |
| Optimizer steps | 1,981 |
| Effective batch size | 64 |
| Maximum sequence length | 4,096 |
| Learning rate (peak / minimum) | 1e-4 / 1e-5 |
| Warmup / weight decay / gradient clipping | 3% / 0.01 / 1.0 |
| Precision | BF16 |
| Final reported train loss | 0.4991 |
| Hardware and runtime | 1 x NVIDIA A10G, 7,266.56 s (~2 h 01 m) |

The final adapter was merged into the base weights in FP32. The card reports **128/128** exact decoded matches between base-plus-adapter inference and the merged model in merge-equivalence validation; this is a vendor-run check, not an independent one.[^senocr-vi-model-card]

## Training data

The corpus is Vietnamese-dominant and combines public and restricted lanes. The handwritten lane comes from [5CD-AI/Viet-Handwriting-OCR-v2](https://huggingface.co/datasets/5CD-AI/Viet-Handwriting-OCR-v2).[^senocr-vi-model-card]

| Corpus lane | Records | Target tokens |
|---|---:|---:|
| Vietnamese handwriting (Viet-Handwriting-OCR-v2) | 23,046 | 456,066 |
| VinText | 10,174 | 32,531 |
| Vietnamese text corpus | 1,539 | 491,846 |
| General OCR replay | 4,687 | 22,594 |
| Private archival corpus | 2,808 | 168,823 |
| **Total** | **42,254** | **1,171,860** |

The long-form Vietnamese text lane supplies about 42% of supervised target tokens from under 4% of records, while the handwriting lane supplies most records. Restricted archival source material is not redistributed with the model; public datasets keep their original licenses.[^senocr-vi-model-card]

## Reported evaluation

All rows below are model-card or leaderboard values, not reruns by this wiki.[^senocr-vi-model-card]

**Vietnamese document composite** on the corrected 160-page Vietnamese page population:

| Model | Parameters | Vietnamese composite |
|---|---:|---:|
| chandra-ocr-2 | 5B | 85.60 |
| MonkeyOCRv2-B-Parsing | 0.7B | 83.20 |
| Claude-Sonnet-4.6 | Undisclosed | 83.10 |
| **SenOCR-Vi** | **0.959B** | **82.83** |
| ChatGPT-5.2-2025-12-11 | Undisclosed | 82.10 |
| PaddleOCR-VL-1.6 | ~0.9B | 80.90 |

External model scores are attributed to the MDPBench official leaderboard. The card frames the result as 0.27 points behind Claude-Sonnet-4.6, 0.73 ahead of ChatGPT-5.2, and 1.93 ahead of PaddleOCR-VL-1.6, while [Chandra OCR 2](chandra-ocr-2.md) scores 2.77 points higher at about 5.2 times the parameter count.[^senocr-vi-model-card]

**Other reported slices:**

- Text recognition on the 160-page Vietnamese slice: page-level `text_block` edit distance 0.13305, equivalently 86.7% under `1 - Edit_dist`. The 82.83 document composite also includes structured document elements, so the two figures are not interchangeable.[^senocr-vi-model-card]
- Document conditions: 91.1 on digital documents and 80.8 on photographed documents, on a controlled English/Vietnamese/Simplified Chinese population.[^senocr-vi-model-card]
- Multilingual composite: English 82.08, Vietnamese 82.83, Simplified Chinese 84.03, EN/VI/ZH macro 82.98. The card reports the PaddleOCR-VL-1.6 macro at 83.43 from the corresponding MDPBench language columns.[^senocr-vi-model-card]
- Structured elements: text 86.5% under `1 - NED`, table 70.7 TEDS, formula 72.5 CDM on the controlled evaluation population.[^senocr-vi-model-card]

## Comparability caveats

- **Scorer correction:** the reported Vietnamese composite is re-aggregated over the actual page population. The original project scorer emitted three additional non-page rows because of a documented key-parsing defect, and all three fell in the Vietnamese population; removing them yields 82.83.[^senocr-vi-model-card] This identifies a page-level aggregation pitfall in model-card scoring, not an official MDPBench erratum.
- **Population mismatch risk:** the base model's 80.90 is taken from MDPBench leaderboard columns, whereas SenOCR-Vi's 82.83 is recomputed on the corrected page population. The 1.93-point gap therefore mixes a leaderboard aggregation and a corrected re-aggregation; the card does not publish a base-model score recomputed through the same corrected pipeline.[^senocr-vi-model-card]
- **Language trade-off:** the Vietnamese gain coexists with a slightly lower EN/VI/ZH macro than the base (82.98 versus 83.43), so the fine-tune is a language-specific specialization rather than a uniform multilingual improvement.[^senocr-vi-model-card]
- **Scope of the headline:** 82.98 is a three-language summary only, not the full MDPBench overall score.[^senocr-vi-model-card]

## Limitations

The card positions SenOCR-Vi for Vietnamese printed documents, photographed pages, archival material, textbooks, and document-ingestion workflows, and states that structured elements remain harder than plain text: 70.7 TEDS on tables and 72.5 CDM on formulas mean it is not a table- or formula-specialized OCR system. Named difficult cases are complex or irregular tables, formula-heavy scientific pages, dense multi-column layouts, colorful textbooks and magazines, and severe image degradation or unusual geometry.[^senocr-vi-model-card]

No controlled production benchmark yet establishes pages per second, optimized BF16 peak VRAM, or latency relative to other OCR systems, so throughput and cost claims should not be extrapolated from the single-A10G training run. The card recommends human review for legal, financial, historical, or otherwise high-stakes transcription.[^senocr-vi-model-card]

## Coverage and trust limits

The source is one standalone model card with no local weights, training or evaluation code, data manifests, prompts, scoring scripts, or leaderboard snapshot. Its banner image is an external URL rather than a local artifact. The 82.83/86.7 figures, the 128/128 merge check, and every comparison row are therefore vendor-reported and cannot be reproduced from repository evidence; release revision, evaluation prompts, and the scorer implementation behind the "documented key-parsing defect" are not identified.[^senocr-vi-model-card]

## Relationships

- **Depends on / Uses:** [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md) as base model, architecture, prompt interface, and optional page-parsing pipeline; the fine-tune changes decoder behavior only.[^senocr-vi-model-card]
- **Evaluated by:** a corrected Vietnamese slice of the [MDPBench](mdpbench.md) page population, with external baselines taken from the MDPBench leaderboard.[^senocr-vi-model-card]
- **Compared with:** [Chandra OCR 2](chandra-ocr-2.md) and [MonkeyOCRv2](monkeyocrv2.md) on Vietnamese document composite; both reported values are higher, at larger or unstated protocol distance.[^senocr-vi-model-card]

[^senocr-vi-model-card]: VietAlpha Lab, *SenOCR-Vi: A Vietnamese-Specialized Document OCR Model*, local model card at [VietAlphaLabs-SenOCR-Vi.md](../raw/VietAlphaLabs-SenOCR-Vi.md), preamble (model identity, 82.83/86.7 figures), § Highlights, § Inference examples › Transformers and PaddleOCR, § Evaluation › Vietnamese and Text recognition, § Benchmark note, § Training, § Data, § Limitations, § License (accessed 2026-10-25).
