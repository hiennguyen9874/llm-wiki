---
type: Model System
title: lift
description: lift is Datalab's 9B structured-extraction model for producing schema-constrained JSON from PDFs and images.
tags: [document-extraction, structured-output, json-schema, vision-language-models, pdf]
status: draft
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T03:13:08Z }
sources:
  - id: lift-model-card
    resource: ../raw/lift.md
    title: lift model card
---

# lift

lift is Datalab's 9B model for extracting a JSON object from PDFs or images against a caller-provided JSON Schema. Its documented schema-constrained decoding is intended to guarantee valid, well-typed output, positioning it for field-oriented document extraction rather than general document-to-Markdown conversion.[^lift-model-card]

## Extraction contract

- The supported schema subset includes strings, numbers, integers, booleans, arrays (including arrays of objects), and nested objects. Field descriptions are recommended for ambiguous names; `required` should be limited to fields that must occur. The model returns `null` for fields genuinely absent from the document.[^lift-model-card]
- One extraction call can process multi-page documents, including values that span pages. A `page_range` option can restrict processing to a PDF-page interval.[^lift-model-card]
- The `extract` interface accepts a schema dictionary, a JSON-file path, inline JSON, or the name of a saved schema. The supplied CLI can run on one file or a directory, and Schema Studio is a Streamlit application for building, saving, and testing schemas.[^lift-model-card]

## Operation

The model can run in-process through HuggingFace Transformers with `InferenceManager(method="hf")`, which requires the `lift-pdf[hf]` extra and Torch. The documented recommended path starts `lift_vllm` and uses `InferenceManager(method="vllm")`; `VLLM_API_BASE` can target a remote vLLM server.[^lift-model-card]

Datalab also directs users to a hosted API and playground, describing API-only higher-accuracy extraction, per-field verification, and citations. The retained card does not document that API's request contract, pricing, or implementation, so those capabilities are not established for the local package.[^lift-model-card]

## Reported evaluation

The model card reports a 225-document, approximately 11,000-scored-field benchmark whose documents span 6–64 pages and include adversarial cross-page values, exhaustive lists, absent fields, distractors, and multi-source aggregation. All systems received rendered page images and processed each document in one pass.[^lift-model-card]

| System | Field accuracy | Full-document accuracy | Median latency |
| --- | ---: | ---: | ---: |
| Datalab API | 95.9% | 44.4% | 30.8 s |
| Gemini Flash 3.5 | 91.3% | 40.0% | 28.1 s |
| lift | 90.2% | 20.9% | 9.5 s |
| Azure Content Understanding | 83.4% | 22.2% | 73.7 s |
| NuExtract3 | 81.5% | 8.4% | 8.3 s |
| Qwen3.5-9B | 76.3% | 24.0% | 16.8 s |

These are source-reported measurements. Latencies are medians per document at eight concurrent requests; local models ran under vLLM on one GPU, whereas Gemini, Datalab, and Azure used APIs. The source warns that hardware and load affect latency, and supplies neither the benchmark artifacts nor full evaluation configuration in this retained card.[^lift-model-card]

## Licensing and trust limits

The card says the code is Apache 2.0 and the weights use a modified OpenRAIL-M license. It describes free use for research, personal use, and startups below $5M funding or revenue, prohibits competitive use against Datalab's API, and refers broader commercial users to Datalab pricing; consult the linked license before deployment.[^lift-model-card]

This synthesis is limited to the retained model card. Its guarantee, capability, licensing, hosted-service, and benchmark claims are vendor assertions; the card does not provide the model architecture, training data, benchmark release, evaluation scripts, or independent verification.[^lift-model-card]

## Relationships

- **Related to:** [PP-ChatOCRv4](pp-chatocrv4.md) also targets document key-information extraction, but it combines OCR-text retrieval and direct visual question answering rather than declaring schema-constrained JSON decoding.
- **Related to:** [Nanonets-OCR2](nanonets-ocr2.md) produces structured document representations, but its retained card emphasizes Markdown and tagged visual elements rather than arbitrary caller-defined JSON schemas.

[^lift-model-card]: Datalab, [lift model card](../raw/lift.md) (accessed 2026-08-21).
