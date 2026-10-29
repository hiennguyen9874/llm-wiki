---
type: Model System
title: MinerU2.5-Pro
description: MinerU2.5-Pro is a 1.2B document-parsing vision-language model whose authors attribute improvements over MinerU2.5 to scaled and refined training data.
tags: [ocr, document-parsing, vision-language-models, data-engineering, table-recognition, formula-recognition]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-29T14:03:42+07:00 }
stale_after: 2027-01-29
sources:
  - id: mineru2-5-pro-model-card
    resource: ../raw/MinerU2.5-Pro-2604-1.2B.md
    title: "MinerU2.5-Pro: Pushing the Limits of Data-Centric Document Parsing at Scale"
  - id: mineru2-5-pro-2605-model-card
    resource: ../raw/MinerU2.5-Pro-2605-1.2B.md
    title: "MinerU2.5-Pro-2605-1.2B model card"
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    kind: paper
    title: PaddleOCR-VL-1.6 technical report
---

# MinerU2.5-Pro

MinerU2.5-Pro is a 1.2B-parameter PDF-to-Markdown document-parsing model. Its authors attribute its claimed gains over MinerU2.5 to data engineering rather than an architecture change: they report scaling training data, improving difficult-example coverage and annotation quality, then training in three stages.[^mineru2-5-pro-model-card]

## Author-reported results

The 2604 card reports an overall score of 95.69 on OmniDocBench v1.6, versus 92.98 for its MinerU2.5 baseline. It also claims a 1.39-point lead over the next model across five table benchmarks, a 3.06-point gain over original MinerU, Dense Formula CDM of 97.29, and text edit distance of 0.036.[^mineru2-5-pro-model-card]

The May 2026 2605 update reports an overall score of 95.72 on OmniDocBench v1.6_full, compared with 95.69 for 2604. Its table lists text edit distance at 0.036 for both versions; formula CDM at 97.15 versus 97.29; Table TEDS at 93.62 versus 93.42; Table TEDS-S at 96.01 versus 95.92; and read-order edit distance at 0.123 versus 0.120. The authors characterize these metric differences as marginal and say 2605 instead targets user-experience improvements.[^mineru2-5-pro-2605-model-card]

All of these are author-reported comparisons: the local cards provide no evaluation protocol, and their remote performance images were not inspected.

## Data engine and training

The authors report expanding the corpus from under 10 million to 65.5 million pages, emphasizing difficult long-tail samples while controlling distribution shift. For complex tables and dense formulas, they describe Cross-Model Consistency Verification (CMCV) and iterative Judge-and-Refine annotation. Their stated training sequence is large-scale pre-training, high-quality difficult-sample fine-tuning, then GRPO format alignment.[^mineru2-5-pro-model-card]

## Parsing features

The cards claim support for image and chart parsing, merging truncated paragraphs, cross-page table merging, and recognizing images within tables. The 2605 update says it reduced layout-category errors, especially missed `image_block` detections, through data cleaning, and improved chart, flowchart, and seal recognition after constructing a large-scale image-analysis training dataset.[^mineru2-5-pro-2605-model-card] However, each card's quick-start section separately says cross-page table merging is still under integration. Its availability is therefore unresolved from these sources.[^mineru2-5-pro-model-card][^mineru2-5-pro-2605-model-card]

## Operation

The documented Python interface is `mineru-vl-utils`, with Transformers and vLLM backends. The examples use `MinerUClient.two_step_extract` on a page image; `json2md` converts its JSON result to Markdown and enables truncated-paragraph merging. Image/chart analysis requires setting `image_analysis=True`. The card recommends vLLM and reports 2.12 fps concurrent asynchronous inference on one A100, without workload or measurement details.[^mineru2-5-pro-model-card]

## Contradictions

- The card lists cross-page table merging as a native capability, but says it is “currently under integration” in its quick-start section.[^mineru2-5-pro-model-card]

## Cross-source benchmark discrepancy

**Reported:** the PaddleOCR-VL-1.6 report's OmniDocBench v1.6 table instead records MinerU2.5-Pro at 95.75 overall and formula CDM 97.45, while the 2605 card gives 95.72/97.15 for 2605 and 95.69/97.29 for 2604. The report row does not identify the exact MinerU revision, and no common outputs or evaluation configuration were inspected to reconcile these differences. Preserve both rather than treating either as a verified correction. See [PaddleOCR vs MinerU vs Docling](paddleocr-mineru-docling-comparison.md) for separately scoped comparisons.[^paddleocr-vl-1-6-report][^mineru2-5-pro-2605-model-card]

## Relationships

- **Compares with:** [MinerU2.5](mineru2-5.md), which the card identifies as its previous baseline.[^mineru2-5-pro-model-card]

## Scope and trust limits

The model and operation synthesis is based on the local Apache-2.0 model cards, with a separately attributed benchmark comparison from the local PaddleOCR-VL-1.6 report. The linked technical report, model weights, utility package, and remote leaderboard, performance, and showcase images were not inspected. Accordingly, architecture details beyond the stated 1.2B size, the numerical claims above, and feature quality are unverified author claims.[^mineru2-5-pro-model-card][^mineru2-5-pro-2605-model-card]

[^mineru2-5-pro-model-card]: OpenDataLab, [*MinerU2.5-Pro: Pushing the Limits of Data-Centric Document Parsing at Scale*](../raw/MinerU2.5-Pro-2604-1.2B.md) (accessed 2026-08-17). Remote image assets and linked external resources were not inspected.
[^mineru2-5-pro-2605-model-card]: OpenDataLab, [*MinerU2.5-Pro-2605-1.2B model card*](../raw/MinerU2.5-Pro-2605-1.2B.md), §News → Comparable Performance table; §Unmatched SOTA Performance; §1 Quick Start (accessed 2026-08-17; textual comparison revisited 2026-10-29). Remote image assets and linked external resources were not inspected.
[^paddleocr-vl-1-6-report]: [PaddleOCR-VL-1.6 report](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), §Experiments → Document Parsing, table `tab:omni16_full_performance`; report attributes its values to the official leaderboard, not inspected independently here.
