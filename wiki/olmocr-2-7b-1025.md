---
type: Model System
title: olmOCR-2-7B-1025
description: olmOCR-2-7B-1025 is a 7B Qwen2.5-VL-based document OCR model fine-tuned with supervised and GRPO training for structured PDF-page extraction.
tags: [ocr, document-parsing, vision-language-models, qwen, structured-output]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:22:54Z }
sources:
  - id: olmocr-2-7b-1025-model-card
    resource: ../raw/olmOCR-2-7B-1025.md
    title: olmOCR-2-7B-1025 model card
---

# olmOCR-2-7B-1025

olmOCR-2-7B-1025 is a BF16 document-OCR model fine-tuned from Qwen2.5-VL-7B-Instruct on the olmOCR-mix-1025 dataset, followed by GRPO reinforcement-learning training that its authors say targets equations, tables, and other difficult OCR cases. The model card recommends its FP8 counterpart for practical use except further fine-tuning.[^olmocr-2-7b-1025-model-card]

## Operation

The documented input is one rendered document-page image whose longest dimension is 1,288 pixels. The prompt also requires document-derived text-block and image metadata; the authors recommend the olmOCR toolkit, which renders PDF pages and builds that prompt rather than hand-building it.[^olmocr-2-7b-1025-model-card]

The model card describes the toolkit's vLLM inference path as able to process millions of documents at scale. In its manual Transformers example, the model is loaded in bfloat16 with the Qwen2.5-VL processor, an image rendered by `olmocr>=0.4.0`, and a no-anchoring v4 YAML prompt; the sampled output contains YAML page metadata followed by extracted text.[^olmocr-2-7b-1025-model-card]

## Reported evaluation

These are author-reported olmOCR-Bench scores using olmOCR toolkit v0.4.0, which the card says automatically renders, rotates, and retries pages as needed; they are not independently reproduced results.[^olmocr-2-7b-1025-model-card]

| Variant | ArXiv | Old Scans Math | Tables | Old Scans | Headers and Footers | Multi-column | Long Tiny Text | Base | Overall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BF16 `olmOCR-2-7B-1025` | 82.9 | 82.1 | 84.3 | 48.3 | 95.7 | 84.3 | 81.4 | 99.7 | **82.3 ± 1.1** |
| FP8 `olmOCR-2-7B-1025-FP8` | 83.0 | 82.3 | 84.9 | 47.7 | 96.1 | 83.7 | 81.9 | 99.7 | **82.4 ± 1.1** |

## License and trust limits

- The card labels this release Apache 2.0 and says it is intended for research and educational use under Ai2's Responsible Use Guidelines. Confirm the linked license and guidelines before a deployment decision.[^olmocr-2-7b-1025-model-card]
- This synthesis covers the retained model card only. It links to external weights, toolkit code, paper, datasets, and a demo, none of which were retained or inspected; their contents, versions, licenses, training details, and evaluation configuration are unverified here.[^olmocr-2-7b-1025-model-card]
- The score table does not provide full benchmark composition, inference hardware, prompt settings, or independent reproductions. Its cross-model comparisons should not be treated as controlled deployment evidence.[^olmocr-2-7b-1025-model-card]

[^olmocr-2-7b-1025-model-card]: Ai2, [olmOCR-2-7B-1025 model card](../raw/olmOCR-2-7B-1025.md) (accessed 2026-08-17).
