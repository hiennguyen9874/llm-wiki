---
type: Model System
title: PaddleOCR-VL-1.6
description: PaddleOCR-VL-1.6 is a 0.9B two-stage document parser that targets residual weak regions through data mining, expert-guided label refinement, and staged CPT–SFT–GRPO post-training.
tags: [document-parsing, ocr, vision-language-models, post-training, reinforcement-learning, data-curation]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-10-29T14:03:42+07:00 }
stale_after: 2027-01-29
sources:
  - id: paddleocr-vl-1-6-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    title: "PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training"
  - id: senocr-vi-model-card
    resource: ../raw/VietAlphaLabs-SenOCR-Vi.md
    kind: model-card
    title: "SenOCR-Vi: A Vietnamese-Specialized Document OCR Model"
---

# PaddleOCR-VL-1.6

PaddleOCR-VL-1.6 is a 0.9B two-stage document parser that retains [PP-DocLayoutV3](pp-doclayoutv3.md) and [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md)'s NaViT-style encoder, adaptive MLP connector, and ERNIE-4.5-0.3B decoder. Its reported gains come instead from targeting residual weak regions, improving labels, and progressively applying continued pre-training (CPT), supervised fine-tuning (SFT), and GRPO reinforcement learning (RL).[^paddleocr-vl-1-6-report]

## Under-optimized-region data engine

The report defines under-optimized regions as parts of the data or supervision space in which the V1.5 model has not learned a reliable image-to-structured-output mapping. It mines three kinds:

- **Boundary-fragile:** samples with inconsistent predictions across eight late-stage checkpoints and 16 semantic-preserving visual distortions. The authors rank each sample by the mean of its 128 largest pairwise normalized-edit-distance discrepancies across 128 predictions, selecting the top 1% plus samples exhibiting degeneration.[^paddleocr-vl-1-6-report]
- **Coverage-sparse:** small, low-connectivity clusters in an internal document-feature similarity graph. These samples seed retrieval from an internal document pool to increase coverage of long-tail cases such as ancient books, rare characters, and industrial tables.[^paddleocr-vl-1-6-report]
- **Unreliable-supervision:** labels unsupported by external parsers. Qianfan-OCR, GLM-OCR, and MinerU2.5-Pro support a label when at least one agrees with it; when all disagree but at least two agree with each other, their consensus replaces the original label. Other cases remain unresolved.[^paddleocr-vl-1-6-report]

Retrieved or unresolved samples are labeled first through three-expert consensus. When no consensus is available, ERNIE 5.0 generates an initial label, then iteratively judges a rendering of that label against the source image and refines discrepancies; cases still unresolved after the configured limit are sent to human annotation with a pre-label.[^paddleocr-vl-1-6-report]

## Progressive post-training

CPT trains all parameters for one epoch on 16.8M samples, combining V1.5 training data with retrieved and corrected data. SFT then trains all parameters for one epoch on 7.3M hard, refined, and corrected samples. The final GRPO stage uses 49K samples (the top 8K per task) for two epochs.[^paddleocr-vl-1-6-report]

For RL selection, the SFT policy produces 16 rollouts per candidate. The report filters reward-flat, too-easy, and too-hard cases, then ranks candidates by reachable reward improvement ($r_{max}-r_{mean}$), token-likelihood-derived uncertainty, and reward variance. The task reward combines a strict validity gate, a structural penalty, and a task-specific similarity metric, so malformed or degenerate outputs receive zero reward.[^paddleocr-vl-1-6-report]

## Reported results

All results below are author-reported and not independently reproduced:[^paddleocr-vl-1-6-report]

- **OmniDocBench v1.6:** 96.33 overall; text edit distance 0.033, formula CDM 97.49, table TEDS 94.76, table TEDS-S 97.11, and reading-order edit distance 0.127. The report's staged ablation rises from the V1.5 checkpoint's 94.93 overall to 95.62 after CPT, 96.25 after SFT, and 96.33 after RL.
- **Real5-OmniDocBench:** 93.19 overall, with scores of 94.74 (scanning), 92.48 (warping), 92.78 (screen photography), 93.28 (illumination), and 92.66 (skew).
- **In-house capability tests:** 91.71 TEDS and 94.67 structural TEDS on a 1,258-sample hard-table set; 91.74 RMS-F1 on a 1,801-sample chart set; 87.47 average text-spotting accuracy across nine categories; and 0.119 normalized edit distance on a 300-image seal set.

## Comparison and protocol limits

**Reported:** the same report's OmniDocBench v1.6 table lists MinerU2.5-Pro at 95.75 overall, formula CDM 97.45, and reading-order edit 0.120 versus this model's 96.33, 97.49 and 0.127. Thus the overall lead does not imply a lead on reading order. Its Real5 table lists MinerU2.5-pro at 88.96 versus 93.19 here. The exact MinerU model revision is not specified in those rows, and the OmniDocBench values differ from its model cards; [the detailed comparison](paddleocr-mineru-docling-comparison.md#discrepancy-cần-giữ-riêng) preserves both sources without resolving the protocol difference. No corresponding Docling row appears in these two tables.[^paddleocr-vl-1-6-report]

## Trust limits

- The bundle contains the report, bibliography, and three result/architecture figures, but no weights, data, training or evaluation code, prompts, annotation outputs, or reproducible benchmark configurations. Its model, procedure, and performance claims cannot be independently reproduced from these artifacts.[^paddleocr-vl-1-6-report]
- The 16.8M CPT corpus, 7.3M SFT corpus, 49K RL set, feature encoder, mining thresholds, expert-output matching, and label-refinement stopping limit are insufficiently specified to reconstruct the reported data pipeline.[^paddleocr-vl-1-6-report]
- Hard-table, chart, text-spotting, and seal results rely on author-constructed benchmarks. Their incomplete public protocols constrain independent comparison. Although the report attributes OmniDocBench v1.6 values to an official leaderboard, this bundle does not contain a leaderboard snapshot or evaluated outputs.[^paddleocr-vl-1-6-report]

## Relationships

- **Supersedes:** [PaddleOCR-VL-1.5](paddleocr-vl-1.5.md) as the next version of the two-stage parser.
- **Uses:** [PP-DocLayoutV3](pp-doclayoutv3.md) unchanged for layout analysis, multipoint localization, and reading order before element recognition.[^paddleocr-vl-1-6-report]
- **Extended by:** [SenOCR-Vi](senocr-vi.md), a Vietnamese decoder-only LoRA fine-tune that keeps this model's architecture and prompt/pipeline interface; its card reports 82.83 versus 80.90 here on a corrected Vietnamese MDPBench page population, but the base figure is leaderboard-derived and not recomputed through the same corrected pipeline.[^senocr-vi-model-card]

[^paddleocr-vl-1-6-report]: Zhang et al., *PaddleOCR-VL-1.6: Expanding the Frontier of Document Parsing with Under-Optimized Region Refinement and Progressive Post-Training*, local LaTeX source at [main.tex](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), §Experiments → Document Parsing, tables `tab:omni16_full_performance` and `tab:real5-omnidocbench-performance`, including the [reported-metrics figure](../raw/2606.03264_PaddleOCR-VL-1.6/images/vl16img_for_overleaf/metric.png), [system overview](../raw/2606.03264_PaddleOCR-VL-1.6/images/vl16img_for_overleaf/overall.png), and [data-engine diagram](../raw/2606.03264_PaddleOCR-VL-1.6/images/vl16img_for_overleaf/data_engine.png) (accessed 2026-08-17).

[^senocr-vi-model-card]: VietAlpha Lab, *SenOCR-Vi: A Vietnamese-Specialized Document OCR Model*, local model card at [VietAlphaLabs-SenOCR-Vi.md](../raw/VietAlphaLabs-SenOCR-Vi.md), § Evaluation › Vietnamese and § Benchmark note (accessed 2026-10-25).
