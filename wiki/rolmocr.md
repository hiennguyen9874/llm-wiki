---
type: Model System
title: RolmOCR
description: RolmOCR is Reducto AI's Apache-2.0 Qwen2.5-VL-7B document-OCR model that omits PDF metadata inputs and trains with rotated pages for off-angle robustness.
tags: [ocr, document-parsing, vision-language-models, qwen, open-source]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:24:32Z }
sources:
  - id: rolmocr-model-card
    resource: ../raw/RolmOCR.md
    title: RolmOCR model card
---

# RolmOCR

RolmOCR is Reducto AI's Apache-2.0 document-OCR model, fine-tuned from Qwen2.5-VL-7B-Instruct on the `allenai/olmOCR-mix-0225` dataset. Its authors present it as a drop-in olmOCR alternative that is faster and uses less memory, but the retained card provides no measurements or evaluation results for those claims.[^rolmocr-model-card]

## Design changes

The model card identifies three changes relative to the original olmOCR approach:

- It uses Qwen2.5-VL-7B as its base model.
- It omits PDF-extracted metadata from the prompt. The authors say the shorter prompt lowers processing time and VRAM use without hurting accuracy in most cases.
- It rotates about 15% of training examples to improve robustness to off-angle documents; the card says the rest of the training set is unchanged.[^rolmocr-model-card]

## Operation and outputs

The documented deployment path serves `reducto/RolmOCR` with vLLM and sends an image plus an instruction to an OpenAI-compatible chat-completions endpoint. The example asks for a plain-text natural-reading representation and sets temperature to 0.2 with a 4,096-token maximum. The card uses both `reducto/RolmOCR` and `reducto/RolmOCR-7b` identifiers in its commands and client example; confirm the applicable model identifier before deployment.[^rolmocr-model-card]

## Limitations and trust limits

- Like other VLM-based OCR systems, RolmOCR can hallucinate or omit content.[^rolmocr-model-card]
- It cannot return layout bounding boxes; the source contrasts this with Reducto's Parsing API.[^rolmocr-model-card]
- The authors have not evaluated quantized variants.[^rolmocr-model-card]
- This synthesis covers the retained model card only. The linked weights, base-model card, training dataset, olmOCR project, vLLM documentation, and Reducto Parsing API were not retained or inspected; their contents, versions, and licenses are unverified here.[^rolmocr-model-card]
- No benchmark scores, hardware configuration, throughput figures, or independent reproductions are included in the retained source. Its speed, memory, and accuracy statements are author claims rather than controlled deployment evidence.[^rolmocr-model-card]

## Relationships

- **Related to:** [olmOCR-2-7B-1025](olmocr-2-7b-1025.md) is a later documented olmOCR-family release. RolmOCR's source describes an earlier olmOCR approach, so this link is lineage context rather than evidence of matched performance or interchangeability.[^rolmocr-model-card]

[^rolmocr-model-card]: Reducto AI, [RolmOCR model card](../raw/RolmOCR.md) (accessed 2026-08-17).
