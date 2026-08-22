---
type: Model System
title: NVIDIA Nemotron Parse 2.0
description: NVIDIA Nemotron Parse 2.0 is a sub-1B vision-encoder–decoder document parser with expanded multilingual vocabulary, chart-aware parsing, and improved table and handwriting extraction.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, table-extraction, chart-parsing, multilingual, spatial-grounding]
status: stable
created: 2026-08-22
generated: { by: llm-wiki-agent/1, at: 2026-08-22T00:00:00Z }
sources:
  - id: nemotron-parse-2-0-model-card
    resource: ../raw/NVIDIA-Nemotron-Parse-2.0.md
    title: NVIDIA Nemotron Parse 2.0 model card
---

# NVIDIA Nemotron Parse 2.0

NVIDIA Nemotron Parse 2.0 is a Transformer vision-encoder–decoder that converts RGB document images to reading-order text, layout classes, bounding boxes, and chart/table structure. It retains the sub-1B ViT-H (C-RADIO) + mBART-decoder backbone of v1.1/v1.2 while adding an approximately 20k-token vocabulary expansion (72,256 total), a `<class_Chart>` token for chart-aware parsing, and updated chart/table-heavy training coverage for document intelligence, RAG, curator/extractor, and agentic workflows.[^nemotron-parse-2-0-model-card]

## Architecture and interface

The card describes a ViT-H vision encoder based on NVIDIA C-RADIO, a 1D-convolution and normalization adapter that compresses the vision latent sequence before decoding, and a 10-block mBART decoder, with fewer than 1B parameters.[^nemotron-parse-2-0-model-card] An auxiliary prediction head is preserved separately as `auxiliary_prediction_heads.safetensors.extra` for future multi-token-prediction research; standard generation uses tied decoder input/output embeddings and does not load that head.[^nemotron-parse-2-0-model-card]

The tokenizer contains 72,256 entries, including the ~20k expansion over v1.2, plus task/control tokens `<predict_bbox>`, `<predict_classes>`, `<predict_text_in_pic>`, `<predict_no_text_in_pic>`, and the chart class token `<class_Chart>`.[^nemotron-parse-2-0-model-card] The model also includes the default tied weight `lm_head.weight` = `decoder.embed_tokens.weight`; current vLLM 0.20 builds create a separate head unless patched, and the repository includes a `vllm_tied_patch/sitecustomize.py` patch to preserve tying.[^nemotron-parse-2-0-model-card]

## Inputs and prompts

Input is an RGB image (3 channels, 2D) plus a 1D prompt string composed from supported control tokens.[^nemotron-parse-2-0-model-card] Recommended resolutions are 1,024×1,280 minimum and 1,664×2,048 maximum (width × height).[^nemotron-parse-2-0-model-card]

Documented prompts:

- Default — bounding boxes, classes, and Markdown text without figure text: `</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>`[^nemotron-parse-2-0-model-card]
- With figure text: `</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>`[^nemotron-parse-2-0-model-card]
- Boxes and classes only: `</s><s><predict_bbox><predict_classes><output_no_text><predict_no_text_in_pic>`[^nemotron-parse-2-0-model-card]

When chart content is detected the model can emit `<class_Chart>` regions.[^nemotron-parse-2-0-model-card] Documented element classes from the predecessor family include titles, paragraphs, captions, tables, charts, page headers/footers, footnotes, pictures, and bibliography entries; this card explicitly lists the chart class addition.[^nemotron-parse-2-0-model-card]

## Outputs and postprocessing

Output is a string encoding document text, semantic classes, and bounding boxes.[^nemotron-parse-2-0-model-card] Repository utilities transform boxes back to original image coordinates and convert table or chart-associated text into LaTeX, HTML, Markdown, JSON, JSON-hierarchical, or CSV where supported.[^nemotron-parse-2-0-model-card]

Postprocessing API (`postprocessing.py`) documented in the card:

- `extract_classes_bboxes(generated_text)` → `classes, bboxes, texts`[^nemotron-parse-2-0-model-card]
- `transform_bbox_to_original(bbox, width, height)`[^nemotron-parse-2-0-model-card]
- `postprocess_text(text, cls, table_format, text_format, blank_text_in_figures)` where `table_format` ∈ {latex, HTML, markdown, json, json_hierarchical, csv}, `text_format` ∈ {markdown, plain}, and `blank_text_in_figures` optionally blanks text inside `Picture` regions[^nemotron-parse-2-0-model-card]

## Deployment

Runtime engines: Transformers and vLLM; supported hardware microarchitectures: Ampere, Blackwell, Hopper, Turing; OS: Linux; acceleration noted on NVIDIA GPU systems; test hardware: H100 and A100.[^nemotron-parse-2-0-model-card]

Transformers path (pinned example): `nvcr.io/nvidia/pytorch:25.03-py3` plus `accelerate==1.12.0`, `transformers==5.6.1`, `timm==1.0.22`, `open_clip_torch==3.2.0`, `einops==0.8.1`, `beautifulsoup4`; `open_clip_torch` is needed only for the direct Transformers path due to remote-code validation of an unused OpenCLIP adaptor; Albumentations is not used.[^nemotron-parse-2-0-model-card] Inference uses `AutoModel` / `AutoProcessor` / `AutoTokenizer` with `trust_remote_code=True` and `torch.bfloat16` on CUDA, plus `GenerationConfig` from the model repository.[^nemotron-parse-2-0-model-card]

vLLM path: supported vLLM versions v0.20–v0.26, validated with v0.20.0 container builds; no `albumentations`/`open_clip_torch` required; lightweight encoder config avoids recursive C-RADIO OpenCLIP import. Recommended `vllm serve` flag on A100/A10: `--attention-backend=TRITON_ATTN`. Example serves with `--dtype bfloat16`, `--max-num-seqs`, and `--limit-mm-per-prompt '{"image": 1}'`; end-to-end Python and OpenAI-compatible server examples are documented.[^nemotron-parse-2-0-model-card] Two optional logits processors are provided: `NemotronParseRepetitionStopProcessor` (n-gram repetition → close coordinate block) and `NemotronParseTableInsertionLogitsProcessor` (force table structure); vLLM use requires adding `logitsprocs/` to `PYTHONPATH` and passing `--logits-processors`.[^nemotron-parse-2-0-model-card]

Licensing: model and config under OpenMDW License 1.1; tokenizer under CC-BY-4.0; contributions under `CONTRIBUTING.md`.[^nemotron-parse-2-0-model-card] Deployment geography: Global.[^nemotron-parse-2-0-model-card]

## Training and evaluation design

Training data described as millions of image-text items aggregated across large document, table, and layout datasets: rendered digital documents, scientific papers, PDFs, Wikipedia-style pages, and synthetic document/table/word/character renderings, paired with OCR text, boxes, and layout labels; annotations from OCR/layout models, third-party OCR services, synthetic pipelines, and human labeling.[^nemotron-parse-2-0-model-card] Data modalities: image + text; stated scales: image 1M–1B, text 1B–10T tokens; collection and labeling methods: hybrid automated/human/synthetic for both train and test.[^nemotron-parse-2-0-model-card]

Evaluation is described as internal and public document-understanding benchmarks covering OCR quality, layout structure, table parsing, reading order, and visual grounding, with hybrid collection/labeling. Named suites in the card: ParseBench (text fidelity, semantic formatting, tables, charts, grounding), IndicVisionBench (Indic OCR: Bengali, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu), MOSCAR (multilingual synthetic OCR across Latin, Arabic, Cyrillic, Chinese, Hangul, Japanese, Indic, Hebrew, Thai, Greek, etc.), and OmniDocBench Notes (Handwriting) on the `data_source: note` slice.[^nemotron-parse-2-0-model-card]

## Reported results

All results below are author-reported comparisons of 2.0 versus v1.2 using the equal-weight checkpoint soup of 58k/60k/62k/64k/66k; not independently reproduced:[^nemotron-parse-2-0-model-card]

| Benchmark | Metric | v1.2 | v2.0 | Change |
|---|---|---|---|---|
| ParseBench | Overall score (higher better) | 0.5782 | 0.6391 | ↑ +0.0609 |
| OmniDocBench Notes (Handwriting) | Text edit distance (lower better) | 0.9739 | 0.3395 | ↓ −0.6343 |
| IndicVisionBench | Overall ANLS character (higher better) | 0.0612 | 0.7203 | ↑ +0.6592 |
| MOSCAR (Multilingual) | Overall BoC F1 (higher better) | 0.4410 | 0.9102 | ↑ +0.4692 |

The card characterizes improvements as expanded multilingual OCR (notably CJK and Indic scripts), improved handwriting extraction on note-like pages, chart-to-table parsing that identifies chart regions and converts visible information to structured text, and stronger table detection/structure recovery/text extraction on table-heavy documents.[^nemotron-parse-2-0-model-card]

## Trust limits

- The local source is a Hugging Face model card, not a peer-reviewed report. It cites a Hugging Face model page (release August 3, 2026) and Hugging Face/C-RADIO/mBART references, but does not locally provide weights, training corpora, benchmark releases, generation outputs, or evaluation scripts needed to reproduce architecture, multilingual, handwriting, chart, or table claims from this bundle.[^nemotron-parse-2-0-model-card]
- Training and evaluation dataset identities, licenses, sizes, splits, and sampling proportions are described only in aggregate (“millions of items”, scale ranges); component datasets and their contribution to the reported deltas cannot be verified here.[^nemotron-parse-2-0-model-card]
- Benchmark numbers are single vendor-reported points without confidence intervals, ablations, or full protocol details; the soup checkpoint selection and any prompt or postprocessing variations beyond the stated defaults are not fully specified for controlled comparison.[^nemotron-parse-2-0-model-card]
- Referenced artifacts `auxiliary_prediction_heads.safetensors.extra`, `vllm_tied_patch/sitecustomize.py`, `logitsprocs/nemotron_parse_vllm_logitprocs.py`, `example_with_processor.py`, and Model Card++ subcards (bias, explainability, safety, privacy) were not inspected locally; linked images and remote configuration (`chat_template.jinja` equivalent) are absent from `raw/`.[^nemotron-parse-2-0-model-card]
- Use-case, compatibility, throughput, and geography claims are vendor statements. The card notes that integrating foundation models requires use-case-specific testing under a V-model and that visible personal/confidential text in input images may be extracted, with links to governance subcards.[^nemotron-parse-2-0-model-card]

## Supersession

Supersedes [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) as the current 2.0 release lineage. The source explicitly compares to v1.2 (vocabulary expansion, `<class_Chart>`, chart/table-heavy coverage); v1.2 source is not present in this bundle, so v1.1 is retained as the last inspected predecessor with its own supersession note.[^nemotron-parse-2-0-model-card]

## Relationships

- **Supersedes:** [NVIDIA Nemotron Parse v1.1](nemotron-parse-v1-1.md) — next major lineage with multilingual, chart, and table upgrades.[^nemotron-parse-2-0-model-card]
- **Uses:** NVIDIA C-RADIO ViT-H as vision encoder backbone.[^nemotron-parse-2-0-model-card]
- **Depends on:** mBART decoder (10 blocks) for generation.[^nemotron-parse-2-0-model-card]

[^nemotron-parse-2-0-model-card]: NVIDIA, [*NVIDIA Nemotron Parse 2.0 model card*](../raw/NVIDIA-Nemotron-Parse-2.0.md) (accessed 2026-08-22).
