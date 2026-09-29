---
type: Model System
title: TeleOCR
description: TeleOCR (formerly NaviDC-OCR) is a 1.2B layout-first document parser that uses deformation-aware polygon layouts and structure-aware training for digital and camera-captured pages.
tags: [ocr, document-parsing, camera-captured-documents, layout-analysis, pseudo-labeling]
status: draft
created: 2026-09-29
generated: { by: llm-wiki-agent/1, at: 2026-09-29T15:55:00Z }
sources:
  - id: teleocr-v3
    resource: ../raw/arXiv-2608.12898v3-TeleOCR/main.tex
    scope: ../raw/arXiv-2608.12898v3-TeleOCR/
    kind: paper
    revision: arXiv:2608.12898v3
    title: "TeleOCR: Navigating Document Parsing Across Digital and Camera-Captured Documents"
---

# TeleOCR

TeleOCR, renamed from NaviDC-OCR in the bundled model README, is a reported 1.2B **decoupled/layout-first** vision-language parser: it locates page regions, then recognizes cropped content. The paper's differentiator is deformation-aware polygon layout segmentation for camera-captured documents, together with consensus pseudo-labeling, rendered-image verification, and structure-aware table/formula training. Its benchmark results are author-reported, not independently reproduced.[^teleocr-v3]

## Architecture and outputs

The paper describes a Qwen2.5-VL-derived vision encoder, Qwen3-0.6B language model, and newly trained MLP aligner. Digital layout prediction emits rectangular boxes on a 0–999 coordinate grid; camera-captured layout prediction emits variable-length polygon boundaries, classes, and orientation. Cropped elements are then prompted for text, LaTeX formulas, OTSL tables (convertible to HTML), code blocks with language labels, seals, or scientific-figure-to-table extraction. The appendix specifies eight task prompts; it does not provide a complete local document-parsing implementation. The README demonstrates direct Transformers inference and OTSL-to-HTML post-processing, while directing full-page parsing to an external repository.[^teleocr-v3]

## Data and training mechanisms

- **Multi-node consensus voting (MCV):** for each sample, heterogeneous model predictions are compared pairwise with a task-specific similarity (layout IoU, text edit distance, table TEDS, formula CDM). Select the prediction with the highest mean agreement only when its score meets threshold τ; otherwise send to automatic correction or human review. This is a proposed reliability heuristic, not a ground-truth guarantee.[^teleocr-v3]
- **Deformation awareness:** synthesize camera-captured pages using forward maps derived from Doc3D backward mappings, warping both region boundaries and a global control-point grid. Train prediction of 1,024 downsampled control points and region boundaries rather than relying on rectangular detection. Curvature-Guided Douglas–Peucker Sampling (CGDP) scores candidate contour points as `Sᵢ = dᵢ(1 + λκ̂ᵢ)` to favor creases as well as large-scale bends. The paper gives no complete sampling implementation, λ, or threshold value.[^teleocr-v3]
- **Self-judgement:** render layout, text, table, and formula pseudo-labels into images and compare these with original images. Train a Qwen2.5-VL-7B-Instruct judge on correct and deliberately perturbed renderings to filter errors; uncertain cases reach human review. The authors report under 40% recall for a zero-shot Qwen3-VL-235B verifier on an internally constructed benchmark, without enough protocol detail for independent comparison.[^teleocr-v3]
- **Four stages:** alignment/pretraining (one epoch, batch 256; frozen LM), deformation-aware full fine-tuning (one epoch, batch 128; reported 4M digital layouts, 2M synthetic captured layouts, and ~120K augmented parsing samples), content–structure decoupled learning (formula syntax labels and content-free OTSL topology), then GRPO with text `1−NED`, table TEDS, and formula CDM rewards. Stage 3/4 schedules, data splits, and isolated component ablations are not specified here.[^teleocr-v3]

## Reported evaluation

All figures below are **reported**, not reproduced. OmniDocBench-style scoring combines `(1 − TextEdit) × 100`, FormulaCDM × 100, and TableTEDS × 100 equally; reading-order edit and TEDS-S are reported separately. The appendix says Wild-OmniDocBench and PureDocBench predictions were converted to Markdown and scored with the same `quick_match` evaluator settings and 1200-second matching timeouts.[^teleocr-v3]

| Benchmark / track | TeleOCR overall | Relevant comparison or qualification |
| --- | ---: | --- |
| OmniDocBench v1.6 Full | 96.87 | OvisOCR2 96.58; TeleOCR text edit 0.027, formula CDM 96.36, table TEDS 97.05, order edit 0.122; OvisOCR2 has lower text/order edit and higher formula CDM in this table. |
| Wild-OmniDocBench v1.5 Full | 88.53 | PaddleOCR-VL-1.6 87.36; OvisOCR2 87.91; TeleOCR table TEDS 89.05, formula CDM 88.26 (OvisOCR2 90.37). |
| PureDocBench Clean / Digital Degraded / Real Degraded | 86.90 / 77.47 / 70.85 | Digital Degraded trails OvisOCR2 (77.77); Real Degraded trails Gemini-3.1-Pro (71.98). Abstract's 78.41 is the approximate mean of TeleOCR's three track overalls, not a separate track score. |
| ICDAR 2026 Sci-ImageMiner data extraction | 41.81 weighted; 66.39 TEDS | Listed first; VLMinators 40.80 weighted and 64.31 TEDS. |

On PureDocBench the authors **removed six invalid Markdown predictions** following severe repetitive generation (one Clean, five Real Degraded), stating missing predictions score zero; no Digital Degraded predictions were removed. This is a documented failure mode and scoring intervention, not evidence that all pages were parsed successfully. The visual comparisons in the appendix illustrate warped-region layouts, table reconstruction, and rotated formulas, but are selected examples, not a measured ablation.[^teleocr-v3]

## Contradictions

- The report's prose says TeleOCR "achieves the best performance in text recognition, table reconstruction, and reading order recovery," but its own OmniDocBench v1.6 table records OvisOCR2 with lower text edit distance (0.025 vs 0.027) and lower reading-order edit distance (0.111 vs 0.122). The prose ranking is not supported by the report's own table; the disagreement is recorded unresolved.[^teleocr-v3]

## Coverage and trust limits

**Observed by static inspection:** `main.tex`, `README.md`, `00README.json`, bibliography metadata and cited figure PDFs (rendered for visual review). The figures add illustrative pipeline and output comparisons; no numerical result is inferred from them beyond the source tables. The remaining bundled `.cls`, `.bst`, `.dtx`, `.ins`, font files and `.bbl` are typesetting/vendor or derived bibliography artifacts; `fig/icon.png` and root `score.png` repeat or decorate report/README material. No code, model weights, benchmark data, scoring scripts, trained judge, or experimental logs are present locally; neither training nor inference was executed. External GitHub/model links and the README's Apache-2.0 tag were not independently verified as a license for this LaTeX bundle. The paper does not report hardware/compute, variance, dataset provenance/overlap audits, detailed stage-3/4 configurations, or component-wise ablations, so causal and reproducibility claims remain limited.[^teleocr-v3]

## Relationships

- **Uses:** [Task: Layout-first modular parsing](task-layout-first-modular-parsing.md) as its page-layout-then-region-recognition paradigm; polygon segmentation modifies the region representation.[^teleocr-v3]
- **Cataloged in:** [Layout-first modular OCR benchmarks](layout-first-modular-ocr-benchmarks.md) as a retained layout-first family member; its author-reported numbers remain on this page rather than in that catalog's protocol tables.[^teleocr-v3]
- **Related to:** [Document-parser data flywheel](document-parser-data-flywheel.md) through pseudo-label filtering and synthetic captured-document generation, without demonstrating the same benchmark-driven iterative cycle.[^teleocr-v3]
- **Compared with:** [OvisOCR2](ovisocr2.md), [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md), and [MinerU2.5-Pro](mineru2-5-pro.md) in this report's benchmark tables; these are the TeleOCR authors' evaluations, not cross-paper score joins.[^teleocr-v3]

[^teleocr-v3]: Cai et al., *TeleOCR: Navigating Document Parsing Across Digital and Camera-Captured Documents*, arXiv:2608.12898v3, local [main.tex](../raw/arXiv-2608.12898v3-TeleOCR/main.tex) (§§ Data Engineering, Progressive Training, Experimental Evaluation; appendix §§ Prompt Design and Task Examples, Benchmark Evaluation Details, Qualitative Comparison; Tables OmniDocBench v1.6, Wild OmniDocBench v1.5, PureDocBench, Sci-ImageMiner, and removed predictions); bundled [README.md](../raw/arXiv-2608.12898v3-TeleOCR/README.md) (§ News, Quick Start) and [figures](../raw/arXiv-2608.12898v3-TeleOCR/fig/data.pdf) (pipeline; also TRAIN.pdf and appendix figures), inspected 2026-09-29.
