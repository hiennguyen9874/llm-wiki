---
type: Model System
title: Xiaomi-OCR-0
description: Xiaomi-OCR-0 is a 0.8B Qwen3.5-based vision-language model for document parsing, OCR-centric question answering, and key information extraction.
tags: [ml, ocr, document-parsing, vision-language-models, information-extraction]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T05:12:52Z }
stale_after: 2027-04-29
sources:
  - id: xiaomi-card
    resource: ../raw/Xiaomi-OCR-0.md
    kind: model-card
    title: Xiaomi-OCR-0 model card
---

# Xiaomi-OCR-0

**Reported:** Xiaomi-OCR-0 is a 0.8B OCR-specialized vision-language model based on Qwen3.5-0.8B-Base, trained for document parsing and OCR-centric understanding. The model card lists Apache-2.0 and reports release of weights on 2026-09-30. Its [training and data engine](xiaomi-ocr-0-training.md) combines text anchoring, continued pretraining, and mixed-task reinforcement learning.[^xiaomi-card]

## Tasks and output

The whole-page prompt requests Markdown in reading order, omitting headers and footers, with tables in OTSL and formulas in LaTeX. Separate prompts request text, OTSL table or LaTeX formula recognition; KIE supplies an example JSON schema. These are prompt instructions, not guarantees of correct or valid output. The card also describes VQA and an optional two-stage layout-to-region-recognition workflow.[^xiaomi-card]

## Author-reported evaluation

| Benchmark | Xiaomi-OCR-0 | Selected comparison |
| --- | ---: | --- |
| OmniDocBench v1.6 overall | 96.83 | TeleOCR 96.87; OvisOCR2 96.58 |
| Real5 overall | 95.24 | OvisOCR2 92.29 |
| Wild-OmniDocBench overall | 87.94 | TeleOCR 88.53 |
| Five OCR-VQA benchmarks mean | 83.2 | Qwen3.5-0.8B 72.9; Qwen3.5-2B 80.9 |

The five VQA scores are DocVQA 93.1, InfoVQA 75.1, ChartQA 84.6, OCRBench 84.6, and TextVQA 78.6; their mean is an unweighted arithmetic average. The card also reports UniMER-Test 97.84, PubTabNet 92.27, and Chronicles-OCR Mature Scripts 73. These are vendor-reported, not independently reproduced; the card does not provide enough evaluation protocol or uncertainty to establish a general ranking.[^xiaomi-card]

## Deployment

The Transformers example specifies Python 3.13, `transformers==5.17.0`, `torch==2.14.0`, `torchvision==0.29.0`, and Pillow; it uses `AutoProcessor` and `AutoModelForImageTextToText`, CPU float32 or accelerator float16, greedy generation, and a 4096-token output cap. The example downloads an image and model from Hugging Face; neither installation nor inference was executed here.[^xiaomi-card]

The card calls the approximately 1.8 GB community Ollama BF16 package experimental: pulling it alone does not set the preprocessing, non-thinking prompt, and decoding settings; its linked MCP service or browser demo applies them. Region mode needs extra layout dependencies. Other community GGUF packages require a vision projector; the card explicitly says its original-checkpoint benchmark results do not establish GGUF accuracy. Contributor-reported NInfer measurements were not independently reproduced.[^xiaomi-card]

## Relationships

- **Uses:** [Xiaomi-OCR-0 training and data engine](xiaomi-ocr-0-training.md).[^xiaomi-card]
- **Addresses:** [End-to-end generative OCR](task-end-to-end-generative-ocr.md) and [structured extraction and KIE](task-structured-extraction-kie.md), with distinct task prompts.[^xiaomi-card]
- **Optionally uses:** [Layout-first modular parsing](task-layout-first-modular-parsing.md) through the reported PP-DocLayoutV3 → region recognition → page assembly path; its external implementation was not inspected.[^xiaomi-card]
- **Addresses:** [Table structure recognition](task-table-structure-recognition.md) through prompted OTSL generation, not a documented cell-box detector.[^xiaomi-card]
- **Compares with:** [OvisOCR3](ovisocr3.md), whose card also reports the 96.83 OmniDocBench figure; the two cards are not an independently controlled evaluation.[^xiaomi-card]

## Coverage and trust limits

Only the local English model card was inspected. The linked technical report, repository, model weights, license text, evaluation code, community conversions, Chinese card, and Ollama guide were not inspected. Relative `assets/` charts and data-engine diagram and `example_pics/` image/video inputs are not supplied with this standalone capture; chart trajectories and qualitative outputs cannot be independently checked. Inline text and tables were inspected; logos and badges are decorative. Exact upstream revision and capture date are unknown. All quality, training and compatibility claims are reported rather than reproduced.[^xiaomi-card]

[^xiaomi-card]: SeerRay Lab, [Xiaomi-OCR-0 model card](../raw/Xiaomi-OCR-0.md), frontmatter and §§ News, About the model, Benchmark results and comparisons, Key Findings, Usage › Task prompts, Use Examples › More code, and Citation and License (inspected 2026-10-29).
