---
type: Model System
title: MinerU2.5
description: MinerU2.5 is a 1.2B two-stage vision-language document parser that performs low-resolution global layout analysis before native-resolution crop recognition.
tags: [ocr, document-parsing, vision-language-models, layout-analysis, table-recognition, formula-recognition]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:17:06Z }
sources:
  - id: mineru2-5-model-card
    resource: ../raw/MinerU2.5-2509-1.2B.md
    title: "MinerU2.5-2509-1.2B model card"
  - id: mineru2-5-pro-model-card
    resource: ../raw/MinerU2.5-Pro-2604-1.2B.md
    title: "MinerU2.5-Pro: Pushing the Limits of Data-Centric Document Parsing at Scale"
---

# MinerU2.5

MinerU2.5 is a 1.2B-parameter vision-language model for document parsing. It uses a coarse-to-fine, two-stage process: global layout analysis on downsampled page images, followed by text, formula, and table recognition on native-resolution crops.[^mineru2-5-model-card]

## Claimed capabilities

The model card says MinerU2.5 preserves headers, footers, and page numbers; uses a more granular layout-labeling scheme for lists, references, and code blocks; and targets complex or long formulas, mixed Chinese–English equations, and rotated, borderless, or partially bordered tables.[^mineru2-5-model-card]

It attributes robustness across document types to a large-scale, diverse pretraining and fine-tuning data engine, and describes its accuracy as state of the art with low computational overhead. These are author claims: the local card supplies no textual benchmark values, protocols, training-data details, or independent evaluation.[^mineru2-5-model-card]

## Operation and integrations

The documented local interface is `mineru-vl-utils`. It supports a Transformers backend using `Qwen2VLForConditionalGeneration`, and vLLM synchronous and asynchronous engines that use a MinerU logits processor. The card recommends vLLM and reports concurrent asynchronous inference of **2.12 fps on one A100**; hardware configuration, workload, and measurement protocol are otherwise unspecified.[^mineru2-5-model-card]

The card presents a self-hosted GPU deployment track, with an A100 recommended, and a cloud API track. Its Flash API mode is described as free without a token for up to 20 pages and 10 MB per file; Precision mode requires authentication. It also documents loaders for LangChain and LlamaIndex and an MCP server for compatible clients. These interfaces are described but not exercised here.[^mineru2-5-model-card]

## Relationships

- **Compared with:** [MinerU2.5-Pro](mineru2-5-pro.md), whose card calls MinerU2.5 its previous baseline and reports an overall OmniDocBench v1.6 score of 92.98 for it versus 95.69 for Pro. This comparison is author-reported; the evaluation protocol was not inspected.[^mineru2-5-pro-model-card]

## Scope and trust limits

This synthesis is based only on the local model card, which declares an AGPL-3.0 license. The linked technical report, package repositories, model weights, API documentation, and external demo were not inspected locally.[^mineru2-5-model-card]

The card embeds remote architecture, performance, benchmark, and example images. Because those assets are not retained as local attachments, their graphical results and architectural details were not independently inspected; in particular, the card's "Performance on OmniDocBench" section does not expose numerical values in text.[^mineru2-5-model-card]

[^mineru2-5-model-card]: OpenDataLab, [*MinerU2.5-2509-1.2B model card*](../raw/MinerU2.5-2509-1.2B.md) (accessed 2026-08-17). Remote image assets referenced by the card were not inspected.
[^mineru2-5-pro-model-card]: OpenDataLab, [*MinerU2.5-Pro: Pushing the Limits of Data-Centric Document Parsing at Scale*](../raw/MinerU2.5-Pro-2604-1.2B.md) (accessed 2026-08-17). The card’s remote performance images and linked external resources were not inspected.
