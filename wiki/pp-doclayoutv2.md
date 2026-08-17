---
type: Model
title: PP-DocLayoutV2
description: PP-DocLayoutV2 is an RT-DETR-based document-layout model with a six-layer relation-aware pointer network that predicts reading order from detected elements.
tags: [layout-analysis, reading-order, document-parsing, object-detection]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T10:38:17Z }
sources:
  - id: paddleocr-vl-report
    resource: ../raw/2510.14528_PaddleOCR-VL/main.tex
    title: "PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model"
---

# PP-DocLayoutV2

PP-DocLayoutV2 is the layout-analysis stage of [PaddleOCR-VL](paddleocr-vl.md). It localizes and classifies document elements, then predicts their reading order before the VLM recognizes the resulting crops; this isolates layout structure from costly long-sequence page-level decoding.[^paddleocr-vl-report]

## Architecture and decoding

An RT-DETR detector emits element boxes and classes. Per-class confidence thresholds select foreground proposals for a six-layer pointer network, which combines absolute 2D position and class embeddings with a Relation-DETR-style geometric attention bias. A pairwise relation head projects element states to queries and keys, producing an $N×N$ relative-order logit matrix. Deterministic win-accumulation decoding derives a topologically consistent order from those pairwise relations.[^paddleocr-vl-report]

## Reported training

The detector is initialized from PP-DocLayout-Plus-L and trained for 100 epochs on over 20,000 author-constructed layout samples. The detector is then frozen while the pointer network trains for 200 epochs with AdamW, a constant $2×10^{-4}$ learning rate, and generalized cross-entropy against pairwise ordering labels.[^paddleocr-vl-report]

## Trust limits

- The source asserts better performance with fewer parameters than LayoutReader but does not provide a PP-DocLayoutV2 results table, parameter count, data release, or evaluation implementation in this bundle.[^paddleocr-vl-report]
- The training set is described only as more than 20,000 high-quality samples; domains, labels, splits, and annotation process are not detailed enough for reproduction.[^paddleocr-vl-report]

## Relationships

- **Superseded by:** [PP-DocLayoutV3](pp-doclayoutv3.md), which jointly predicts regions, masks, and reading order for PaddleOCR-VL-1.5.
- **Part of:** [PaddleOCR-VL](paddleocr-vl.md), where it provides layout coordinates and reading order for element-level recognition.
- **Related approach:** [PP-StructureV3](pp-structurev3.md) also uses an explicit layout-analysis and reading-order stage, but its earlier pipeline describes PP-DocLayout-plus and X-Y Cut rather than this pointer-network design.

[^paddleocr-vl-report]: Cui et al., *PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model*, local LaTeX source at [main.tex](../raw/2510.14528_PaddleOCR-VL/main.tex), including [PP-DocLayoutV2 architecture](../raw/2510.14528_PaddleOCR-VL/images/PP-DocLayoutV2.png) (accessed 2026-08-17).