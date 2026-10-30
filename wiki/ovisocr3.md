---
type: Model System
title: OvisOCR3
description: OvisOCR3 is a 0.8B Qwen3.5-based multimodal model that handles document parsing, general OCR, key-information extraction, document-figure captioning, and cross-page table reconstruction through task-specific prompts.
tags: [ocr, document-parsing, vision-language-models, multimodal, key-information-extraction, table-reconstruction, figure-captioning, qwen3-5]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:23:54Z }
stale_after: 2027-04-25
sources:
  - id: ovisocr3-model-card
    resource: ../raw/ATH-MaaS-OvisOCR3.md
    kind: model-card
    title: OvisOCR3 model card
  - id: ovisocr3-overview-img
    resource: ../raw/ocr-benchmark-assets-2026-10-30/ovisocr3_performance_overview.png
    kind: figure
    title: OvisOCR3 performance overview figure
---

# OvisOCR3

OvisOCR3 is a 0.8B multimodal model from ATH-MaaS, built on Qwen3.5-0.8B, that combines document parsing, general OCR, key-information extraction (KIE), document-figure captioning, and cross-page table reconstruction in one checkpoint. Its capabilities are selected by task-specific prompt files rather than separate model deployments. The card describes a four-stage training pipeline—continued pretraining, mid-training, on-policy distillation, and reinforcement learning—and claims state-of-the-art results among comparable-size models across all five domains; those results are author-reported and were not independently reproduced here.[^ovisocr3-model-card]

## Identity and capability map

| Property | Card value |
|---|---|
| Publisher | ATH-MaaS |
| Base model | `Qwen/Qwen3.5-0.8B` |
| Size | 0.8B (card) |
| License | Apache-2.0 |
| Serving path | Local model directory with vLLM 0.22.1; Transformers metadata also present |
| Inputs | One or two images plus a task prompt; optional region, references, fields, schema, target language, or candidate labels |
| Outputs | Markdown, structured/layout JSON, KIE JSON, localized figure captions and Mermaid, or cross-page HTML tables |

| Capability | Input | Output contract |
|---|---|---|
| Document parsing | Page image plus parsing-mode prompt | Structured JSON, layout-only JSON, or Markdown with LaTeX formulas and HTML tables |
| General OCR | Image, optionally with a region, references, question, target language, or candidate labels | Text, boxes, LaTeX, chart data, one label, or an answer |
| Key information extraction | Image, optionally with fields or a JSON output template | Key-value records or JSON following the supplied template |
| Document figure captioning | Full page image plus caption-mode prompt | Structured page content with localized visual captions and Mermaid for flowcharts |
| Cross-page table reconstruction | Consecutive page images plus their parsed Markdown | Complete HTML table with source-page associations, or a no-continuation prediction |

The card reports no architecture details beyond the Qwen3.5-0.8B base and no training-data volumes, reward definitions, compute, or ablations. Its citation block names an “OvisOCR3 Technical Report” but says the report link will be added later, so no technical report is available locally.[^ovisocr3-model-card]

## Document parsing

OvisOCR3 adds structured document parsing and layout detection to the Markdown parsing described for [OvisOCR2](ovisocr2.md). The card exposes three modes:[^ovisocr3-model-card]

| Mode | Prompt | Output |
|---|---|---|
| Markdown | `document_markdown.txt` | Natural reading order with LaTeX formulas, HTML tables, and image-region references |
| Structured | `document_structured.txt` | JSON array with `bbox`, `category`, and `content` per element |
| Layout only | `document_layout.txt` | JSON array with `bbox` and `category`, without transcription |

Bounding boxes use `[left, top, right, bottom]` order with integer coordinates in `[0, 1000)`, relative to the image supplied to the model and with a top-left origin. Pixel conversion is `x * image_width / 1000` and `y * image_height / 1000`; a cropped input is measured against that crop, not the original page. Preserve the inference image orientation when extracting crops.[^ovisocr3-model-card]

Markdown and structured outputs can reference visual regions as `<img src="images/bbox_left_top_right_bottom.jpg" />`. These paths describe crops that the caller must create; the model does not write image files. The card supplies a crop helper and warns that single-page Markdown references and reconstructed-table `page_N/` prefixes need different resolution.[^ovisocr3-model-card]

The card's Markdown postprocessing strips whitespace, optionally removes image-tag blocks (enabled by default), and applies repeated-tail cleanup regardless of the finish reason. The supplied `_clean_truncated_repeats` helper only runs above 8,000 characters, scans candidate periods from 1 to 200, and truncates when a tail repeats at least five times and spans at least 100 characters. Structured and layout JSON are left unchanged, and the helper does not recover missing content or complete a truncated response.[^ovisocr3-model-card]

## General OCR

Ten prompt files cover plain OCR, word-level text spotting, reference grounding, region OCR, formula recognition, chart parsing, text translation, image classification, visual question answering, and position-aware VQA. Image classification takes a target description and candidate labels; formula recognition and chart parsing need no template substitutions. The output contracts range from plain text and `$$...$$` LaTeX to JSON records with `bbox` and `text`, chart JSON with title/source/axis fields and string-valued data, a single candidate label, or an answer inside `\boxed{}`.[^ovisocr3-model-card]

Boxes and regions use `[x_min, y_min, x_max, y_max]` with integer coordinates in `[0, 1000)`, normalized independently by image width and height. Whole-image region OCR and translation use `[0, 0, 999, 999]`. Chart parsing uses the literal string `"None"` for missing title, source, or axis metadata, while position-aware VQA returns `"bbox": "(x1,y1,x2,y2)"` rather than a numeric array.[^ovisocr3-model-card]

The card emphasizes that these are prompt contracts, not constrained decoders. Placeholder replacement should be literal rather than Python `str.format`, because the prompts contain JSON and LaTeX braces, and callers should validate generated JSON and HTML before use.[^ovisocr3-model-card]

## Key information extraction

KIE has open, specified-field, and schema-based modes. Open extraction returns all visible key-value pairs; specified-field extraction receives a JSON array of field names; schema-based extraction receives an example of the desired JSON output. The schema is an output example rather than a formal JSON Schema declaration: empty strings are value placeholders, and nested objects and arrays define structure.[^ovisocr3-model-card]

Values retain the visible source text. Open extraction uses arrays for repeated values and empty strings for empty values; specified-field extraction additionally uses empty strings for missing fields; schema-based extraction follows the template and uses empty strings for missing values. Template adherence is prompted, not enforced by constrained decoding, so generated JSON requires validation before downstream use.[^ovisocr3-model-card]

## Document figure captioning

Figure captioning uses the full page image and returns a structured page JSON array with `bbox`, `category`, and `content`. Visual categories such as `image` and `chart` receive a concise `<caption>...</caption>` description, with a maximum of 100 words requested by the prompt; flowcharts additionally receive a Mermaid representation inside `<mermaid>...</mermaid>`. Other elements keep their text, formula, or table content.[^ovisocr3-model-card]

This is localized description of a visual element within a page, not merely transcription of a printed figure caption. The card reports DocFigCapBench localization F1 of **90.97** and caption score **6.93**; Qwen3.8-Max has a higher caption score (7.30) but lower localization F1 (86.67), while MinerU2.5-Pro reports 85.00/4.61. The caption metric's scale and evaluator are not defined in the card.[^ovisocr3-model-card]

## Cross-page table reconstruction

The same checkpoint performs both stages of [cross-page table reconstruction](task-cross-page-table-reconstruction.md): it parses each page independently, then receives two adjacent page images and their parsed Markdown to decide whether a table continues and to merge the fragments into one HTML table. The output is a JSON array whose records carry input-local, 1-based `source_pages` and a complete `html` table; images inside tables retain page-qualified references such as `page_1/images/bbox_100_200_300_400.jpg`.[^ovisocr3-model-card]

For tables spanning more than two pages, stage 2 is applied recursively from the end of each consecutive table-bearing sequence toward its beginning. After each merge, the reconstructed table is written into the earlier page and its Markdown is re-rendered before the next pair. The card gives the example of merging pages 2 and 3, then pairing the updated page 2 with page 1. Each step uses only two page images and preserves the original source-page associations.[^ovisocr3-model-card]

The card reports CrossTabBench relation F1 of **97.07** (precision 96.20, recall 97.96), reconstruction TEDS of **89.66**, and MPDocBench-Parse truncated-table TEDS of **92.04**. Qwen3.8-Max reports higher reconstruction TEDS (91.71) but lower relation F1 (94.47), so continuation detection and faithful table reconstruction are not the same capability.[^ovisocr3-model-card]

## Reported evaluation

The card's five-domain tables are author-reported. The card uses `--` for unreported values, not zero, and bold marks the best value in each column. The summary below selects the headline values and nearest comparators; the full cross-model tables are cataloged in [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md).[^ovisocr3-model-card]

| Domain | Benchmark and metric | OvisOCR3 | Comparator context |
|---|---|---|---|
| Document parsing | OmniDocBench1.6 overall ↑ | 96.74 | Xiaomi-OCR-0 96.83; OvisOCR2 96.58; PaddleOCR-VL-1.6 96.34 |
| Document parsing | MDPBench overall ↑ | 88.80 | Qwen3.8-Max 86.40; MonkeyOCRv2-B-Parsing 83.30 |
| Document parsing | PureDocBench overall ↑ | 82.31 | Qwen3.8-Max 80.56; OvisOCR2 75.10 |
| Document parsing | Real5-OmniDocBench overall ↑ | 93.63 | PaddleOCR-VL-1.6 93.19; OvisOCR2 92.29 |
| General OCR | OCRBench ↑ | 88.8 | HunyuanOCR-1.5 86.1; Qwen3.5-2B 85.4; base Qwen3.5-0.8B 79.1 |
| General OCR | OCRBench v2 EN / ZH ↑ | 65.9 / 61.3 | Qwen3.5-4B 54.1 / 61.0; HunyuanOCR-1.5 50.7 / 57.7 |
| KIE | OCRBench KIE / v2 KIE / CC-OCR KIE / in-house ↑ | 90.50 / 83.01 / 88.69 / 77.73 | GLM-OCR 79.00 / 74.22 / 68.36 / 75.25; HunyuanOCR-1.5 81.00 / 68.63 / 66.08 / 75.96 |
| Figure captioning | DocFigCapBench F1 / caption score ↑ | 90.97 / 6.93 | Qwen3.8-Max 86.67 / 7.30; MinerU2.5-Pro 85.00 / 4.61 |
| Cross-page tables | Relation F1 (P/R) / reconstruction TEDS / truncated-table TEDS ↑ | 97.07 (96.20 / 97.96) / 89.66 / 92.04 | Qwen3.8-Max 94.47 (90.19 / 99.19) / 91.71 / 89.57; MinerU2.5-Pro 59.14 (93.81 / 43.18) / 41.02 / 91.44 |

The document-parsing table is overall-only: it does not publish the text, formula, table, or reading-order components used in the OvisOCR2 OmniDocBench v1.6 table. MDPBench, PureDocBench, and Real5-OmniDocBench values are likewise single overall figures without split, prompt, preprocessing, or evaluator details. The in-house KIE benchmark's composition and size are not disclosed.[^ovisocr3-model-card]

A cross-model reading of these tables must keep four limits visible: the card's document-parsing table includes both OvisOCR3 and other systems without stating whether comparator rows were rerun or transcribed; its general-OCR and KIE tables use benchmark-specific scales; DocFigCapBench combines localization and caption quality without defining the caption metric; and CrossTabBench's relation F1 can be high while reconstruction TEDS remains much lower. The card's “state of the art among models of comparable size” claim is therefore a summary of its own selected comparisons, not a controlled ranking.[^ovisocr3-model-card]

## Operation

The example requires a GPU environment supported by vLLM and installs `vllm==0.22.1` plus Pillow. It loads the local model directory with tensor parallelism 1, 0.8 GPU-memory utilization, the Triton GDN prefill backend, and at most two images per prompt; sampling uses `max_tokens=16384` and `temperature=0.0`.[^ovisocr3-model-card]

The chat template disables thinking, images are converted to RGB, and the multimodal processor is bounded between `448 × 448` and `2880 × 2880` pixels. `infer` returns raw generated text and warns only when `finish_reason == "length"`; it does not strip image tags, trim repetitions, repair JSON, or otherwise rewrite the response. Passing two images creates one cross-page request, while independent pages should be separate calls.[^ovisocr3-model-card]

The card explicitly calls these usage settings, not benchmark reproduction settings. It also says prompts, preprocessing, generation parameters, and postprocessing must be frozen for evaluation.[^ovisocr3-model-card]

## Output handling and security

Raw outputs should be preserved before parsing, rendering, or cleanup because JSON, HTML, LaTeX, and Mermaid can be malformed and generation can stop early. Markdown needs HTML-table and LaTeX support; captions and Mermaid inside structured JSON need their own handling. Generated HTML and Mermaid should be treated as untrusted content and sanitized or isolated before browser rendering.[^ovisocr3-model-card]

## Coverage

- **Inspected:** `raw/ATH-MaaS-OvisOCR3.md` in full, including frontmatter, capability tables, all five performance tables, inference and task-specific usage examples, output-handling guidance, and limitations.
- **Later downloaded:** `assets/ovisocr3_performance_overview.png` (2026-10-30); its 12 panels match the card's text tables, so it adds no new values.[^ovisocr3-overview-img]
- **Referenced but absent:** the `prompts/` task files, `document_crosspage.py`, the other `assets/` figure, `LICENSE`, and the model weights, configuration, tokenizer, and processor files. These were not inspected or executed.
- **Unavailable:** the technical report named in the citation block; the card says its link will be added later.
- **Excluded:** the external Hugging Face CDN logo is decorative and was not used.

## Limitations and trust limits

- The local bundle is only the model card. It lacks weights, configuration, tokenizer and processor files, the `prompts/` directory, `document_crosspage.py`, one of the two `assets/` figures (the performance overview was downloaded later), the license file, and the promised technical report. The card's procedures and scores therefore cannot be reproduced from local evidence.[^ovisocr3-model-card]
- The card names four training stages but gives no dataset composition, data volume, reward definitions, optimization details, compute, or ablations. Claims about how the stages produce the reported capabilities are author assertions.[^ovisocr3-model-card]
- All benchmark values are author-reported, and the card does not state whether comparator rows were rerun or transcribed. It provides no per-component vectors for its document-parsing benchmarks, no prompt/configuration manifests, no evaluated outputs, and no hardware-normalized latency or throughput measurements.[^ovisocr3-model-card]
- The card itself warns that OvisOCR3 can produce incorrect, incomplete, repeated, or malformed outputs; small or blurred text, severe perspective distortion, dense layouts, complex formulas, and long tables can degrade recognition and structure recovery. Captions and answers may contain unsupported details and should be checked against the source image.[^ovisocr3-model-card]
- Cross-page reconstruction inherits stage-1 parsing errors and depends on correct page order. Missing table fragments, inconsistent page context, or truncated generations can produce incorrect merges; results should be reviewed before critical use.[^ovisocr3-model-card]
- The card gives no release date, model revision, or parameter-count measurement beyond “0.8B”; `stale_after` here is an operational freshness marker, not a source claim.[^ovisocr3-model-card]

## Contradictions

- **Reported claim:** The card says OvisOCR3 achieves “state-of-the-art performance among models of comparable size across all five domains.” **Reported table:** Xiaomi-OCR-0 scores 96.83 on OmniDocBench1.6 versus OvisOCR3's 96.74, and Qwen3.8-Max scores 91.71 on CrossTabBench reconstruction TEDS versus 89.66. **Synthesis:** OvisOCR3 still leads the other document-parsing columns and the cross-page relation and truncated-table columns, so the claim holds only under an aggregate-domain definition that the card does not state. It also does not define “comparable size.”[^ovisocr3-model-card]

## Relationships

- **Compared in:** [Document OCR model benchmark comparison](document-ocr-model-benchmark-comparison.md), which places this model's reported results beside nine other document parsers per dataset.
- **Predecessor:** [OvisOCR2](ovisocr2.md) is the earlier 0.8B parser; OvisOCR3 adds structured parsing and layout detection and reports higher values where the two are compared, but the card does not explicitly state that OvisOCR2 is withdrawn.[^ovisocr3-model-card]
- **Implements:** [Task: Cross-page table reconstruction](task-cross-page-table-reconstruction.md) with the same checkpoint for page parsing and page-pair merging.[^ovisocr3-model-card]
- **Part of:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) as a prompt-conditioned page-to-structure model, extended with multi-image and multi-task modes.[^ovisocr3-model-card]
- **Related to:** [Task: Structured extraction and KIE](task-structured-extraction-kie.md) through open, field-list, and schema-example extraction modes.[^ovisocr3-model-card]
- **Evaluated by:** [End-to-end generative OCR VLM benchmarks](end-to-end-generative-ocr-vlm-benchmarks.md), [MDPBench](mdpbench.md), and [Real5-OmniDocBench](real5-omnidocbench.md), each of which preserves its own protocol qualifications.[^ovisocr3-model-card]
- **Compared with:** Qwen3.8-Max, PaddleOCR-VL-1.6, HunyuanOCR-1.5, GLM-OCR, MinerU2.5-Pro, OvisOCR2, and Xiaomi-OCR-0 in the card's author-reported tables; these are not controlled comparisons.[^ovisocr3-model-card]

[^ovisocr3-overview-img]: [ovisocr3_performance_overview.png](../raw/ocr-benchmark-assets-2026-10-30/ovisocr3_performance_overview.png), all 12 benchmark panels (fetched 2026-10-30 per `manifest.json`).
[^ovisocr3-model-card]: ATH-MaaS, *OvisOCR3 model card*, local source at [ATH-MaaS-OvisOCR3.md](../raw/ATH-MaaS-OvisOCR3.md), especially § Introduction, § Capabilities, § Performance, § Inference, § Task-Specific Usage, § Output Handling, and § Limitations (accessed 2026-10-25). The referenced `prompts/`, `document_crosspage.py`, `assets/`, model files, and technical report are absent from the local bundle.
