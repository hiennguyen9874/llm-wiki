---
type: Model System
title: Unlimited OCR 2
description: Unlimited OCR 2 is a document OCR VLM that combines sparse visual-reference attention and overlapping page chunks for long-document parsing.
tags: [ml, ocr, document-parsing, vision-language-models, long-context]
status: draft
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T10:01:00Z }
stale_after: 2027-04-27
sources:
  - id: report
    resource: ../raw/Unlimited-OCR-2.pdf
    kind: paper
    title: Unlimited OCR Works 2
  - id: model-card
    resource: ../raw/Unlimited-OCR-2.md
    kind: model-card
    title: Unlimited OCR 2 model card
  - id: github-readme
    resource: ../raw/Unlimited-OCR-github.md
    kind: documentation
    title: Unlimited OCR GitHub README capture
---

# Unlimited OCR 2

Unlimited OCR 2 is Baidu ERNIE Team's successor to [Unlimited OCR](unlimited-ocr.md), retaining its DeepEncoder and MoE decoder while replacing R-SWA with [Sparse Reference Sliding Window Attention](sparse-reference-sliding-window-attention.md) (SR-SWA). **Reported:** overlapping page-chunk decoding additionally bounds resident visual cache, enabling hundred-page parsing; “unlimited” describes an intended scaling regime, not a demonstrated guarantee for arbitrary lengths or global document understanding.[^report]

## Training and architecture

**Reported:** the backbone is 3B total and 500M active parameters per token. One epoch of post-training starts from Unlimited OCR, freezes the encoder and aligner, and trains the LLM on 2M multi-page and 10M single-page documents. Pseudo-label teachers include MinerU2.5-Pro and PaddleOCR-VL-1.6, supplemented by synthetic data and cross-page refinement. Training uses 200 H800 GPUs, batch 1,600, 64K maximum sequence length and AdamW with initial learning rate 2.5e-4.[^report]

## Inference and deployment

**Reported:** Transformers `infer_multi` accepts ordered page images and constructs `<PAGE><image>` per page followed by `Multi page parsing.`; it uses one global view per page. Single-page `infer` defaults to dynamic tiled Gundam mode. The model-card environment is Python 3.10 on A800-80GB with specified Torch and Transformers versions; loading uses `trust_remote_code=True`, so review remote code before use.[^model-card]

**Reported:** the SGLang example needs a custom wheel and configures 10-page windows, a 20,000-token per-page cap and reuse of the previous window's KV tail. Smaller windows reduce peak memory but may harm cross-boundary merging. The example sets `SGLANG_UOCR_EANABLE_DOC_LIMIT` (spelling as published), uses `/dev/shm` for crop tensors and binds the server to `0.0.0.0`; secure the endpoint before exposing it. Its sample PDF client renders pages to a temporary directory and sends base64 images to an OpenAI-compatible server. Configuration, wheel and remote model code were not executed or audited.[^github-readme]

## Reported results and limitations

The authors report MPDocBench overall **84.59**, cross-page text edit **0.100**, and cross-page table TEDS **89.54**; [MarathonDocBench](marathon-doc-bench.md) overall **77.06**, 0.123 and 71.11 respectively. OmniDocBench v1.6 overall is **94.02**, below TeleOCR's 96.91 and OvisOCR2's 96.47 in the same table. These are vendor-reported rather than independently reproduced results; the report does not fully specify comparator inference configurations.[^report]

For hundred-page testing, the paper reports peak KV memory 47.00 → 1.77 GB at batch 1 and throughput 360 → 1,315 tokens/s at batch 16 for standard versus chunked decoding; hardware and other measurement details are not fully specified. Figure 6's latency test uses Gundam mode, batch 3, and 1,024 generated tokens/page: at 100 pages it reports 7.0× versus full attention and 5.6× versus R-SWA. These are per-step numbers, not total-document constant time.[^report]

**Reported limitations:** sparse attention does not retain global document information and can limit heading hierarchy understanding; training diversity is limited. The paper's prose says 500M active parameters but Figure 3 labels the decoder A570M; no reconciliation is provided. Its figure plots the original Unlimited OCR as zero on MarathonDocBench, whereas Table 2 explicitly says it was not reported due to a 40-page input limitation: zero should not be interpreted as a measured score.[^report]

## Coverage and trust

The supplied PDF was text-extracted and key figures on pages 5, 6, 9 and 12 visually inspected; the two Markdown captures were read statically. They are separate local source identities with no pinned upstream revision. The Markdown captures largely duplicate inference instructions; the GitHub capture additionally documents benchmark client and post-processing entry points. The referenced `infer.py`, `utils/process_unlimitedOCR2.py`, `utils/README.md`, custom wheel, model weights, datasets and local image assets are not supplied with these captures and were not inspected; decorative badges and replay were excluded. The model card declares MIT, but no separate license text was supplied. Neither training nor inference nor benchmark evaluation was run. The README citation points to the earlier *Unlimited OCR Works* paper, not this PDF's author list.[^report][^model-card][^github-readme]

## Relationships

- **Builds on:** [Unlimited OCR](unlimited-ocr.md) and its checkpoint.[^report]
- **Uses:** [Sparse Reference Sliding Window Attention](sparse-reference-sliding-window-attention.md) and chunked cache reuse.[^report]
- **Evaluated on:** [MarathonDocBench](marathon-doc-bench.md), a benchmark introduced in the same report.[^report]

[^report]: Baidu ERNIE Team, [Unlimited OCR Works 2](../raw/Unlimited-OCR-2.pdf), §§3.2–3.4, 4–6, Tables 1–4, Figures 3, 5–6 and §8.
[^model-card]: Baidu, [Unlimited OCR 2 model card](../raw/Unlimited-OCR-2.md), frontmatter, §§ Release, What's New in 2, Inference and Citation.
[^github-readme]: Baidu, [Unlimited OCR GitHub README capture](../raw/Unlimited-OCR-github.md), §§ Inference and Evaluation.
