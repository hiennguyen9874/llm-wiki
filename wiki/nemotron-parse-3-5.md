---
type: Model System
title: NVIDIA Nemotron 3.5 Parse
description: NVIDIA Nemotron 3.5 Parse is a 0.631B image-to-structured-text document parser with a C-RADIO vision encoder and an mBART visual-prefix decoder.
tags: [ml, ocr, document-parsing, multilingual, layout-analysis]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:47:22Z }
stale_after: 2027-05-02
sources:
  - id: nemotron-35-card
    resource: ../raw/Nemotron-3.5-Parse.md
    kind: model-card
    title: Nemotron 3.5 Parse model card
---

# NVIDIA Nemotron 3.5 Parse

**Reported:** NVIDIA's Nemotron 3.5 Parse converts an RGB document-page image and a task prompt into ordered text, semantic layout classes, and normalized bounding boxes; it targets document extraction, indexing, and data curation. The card dates the release October 17, 2026 and reports 630,800,496 unique trainable parameters including its auxiliary head.[^nemotron-35-card]

## Architecture and output

**Reported:** Dynamic rectangular NaViT preprocessing feeds a C-RADIOv4-SO400M vision encoder, a sequence-compressing 1D-convolution/normalization adapter, and a 10-layer mBART decoder consuming the visual sequence as a causal prefix. Grouped-query self-attention uses 16 query and 8 key/value heads; the multilingual tokenizer has 72,505 entries and the shared decoder embedding/output matrix is padded to 72,512 rows. A trained one-step multi-token prediction (MTP) head is bundled; standard Transformers generation does not use it, while the vLLM plugin uses it for one-token speculation.[^nemotron-35-card]

The default task prompt is `</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>`. The card recommends at most 1664 × 2048 pixels (width × height) and says output boxes are content-normalized: scale x by image width and y by image height. `<class_Chart>` identifies chart regions. Postprocessing can emit Markdown with HTML tables and ordered blocks; HTML and hierarchical JSON retain merged-cell structure whereas flat Markdown, CSV and record JSON flatten spans.[^nemotron-35-card]

## Training and use limits

**Reported:** Training combines millions of document/table image-text items, automated OCR and layout labels, human annotation, and synthetic renderings. The card supplies broad aggregate size ranges rather than named constituent datasets or detailed splits. It warns that input images may contain personal, confidential, or copyrighted material that the model can reproduce; users need appropriate rights and application-specific testing. The model is governed by OpenMDW 1.1; the tokenizer is separately MIT-licensed according to the card. License texts and third-party notices were not independently reviewed.[^nemotron-35-card]

## Relationships

- **Related release:** [NVIDIA Nemotron Parse 2.0](nemotron-parse-2-0.md) — an earlier model compared in the card; the different default prompts and evaluation conditions matter. This does not establish retirement of 2.0.[^nemotron-35-card]
- **Uses:** [Task: End-to-end generative OCR](task-end-to-end-generative-ocr.md) for full-page parsing; multi-pass benchmark configurations additionally refine predicted regions.[^nemotron-35-card]
- **Evaluated in:** [Nemotron 3.5 Parse evaluation](nemotron-parse-3-5-evaluation.md); **deployed via:** [Nemotron 3.5 Parse deployment](nemotron-parse-3-5-deployment.md).[^nemotron-35-card]

## Coverage and trust

The local model card was inspected in full; its architecture, licenses, performance, and software behavior are vendor reports, not independently verified. The linked tokenizer attribution, third-party notices, ParseBench pipeline and results, benchmark environment inventory, multilingual results, regression references, serving and postprocessing guides, model code/weights, and Model Card++ subcards are not included alongside the local card and were not inspected. External links were not fetched. Example commands were not executed. Draft status records these missing material artifacts and reproducibility limits.[^nemotron-35-card]

[^nemotron-35-card]: NVIDIA, [Nemotron 3.5 Parse model card](../raw/Nemotron-3.5-Parse.md), §§ Description, License/Terms of Use, Model Architecture, Input(s), Output(s), Postprocessing, Training Dataset, Evaluation Results, and Ethical Considerations.
