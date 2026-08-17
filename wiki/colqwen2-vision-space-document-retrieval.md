---
type: Concept
title: ColQwen2 vision-space document retrieval
description: A Qwen2-VL-based late-interaction page retriever that improved the paper’s ViDoRe score over its PaliGemma-based ColPali reference.
tags: [document-retrieval, multimodal-retrieval, late-interaction, vision-language-models, rag]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T02:45:00Z }
sources:
  - id: faysse-2025-colqwen2
    resource: ../raw/2407.01449_ColQwen2.md
    title: Efficient Document Retrieval with Vision Language Models
  - id: faysse-2025-colpali-camera-ready
    resource: ../raw/2407.01449_ColPali/iclr2025_conference.tex
    title: ColPali: Efficient Document Retrieval with Vision Language Models
---

# ColQwen2 vision-space document retrieval

ColQwen2 adapts the Qwen2-VL 2B vision-language model to ColPali’s vision-space, late-interaction document-retrieval approach. Using the same reported training data and strategy as ColPali but 768 image patches per page, it achieved 86.6 aggregate nDCG@5 on ViDoRe, 5.3 points above the paper’s 1,024-patch ColPali reference; this is a benchmark-specific result, not a general deployment guarantee.[^faysse-2025-colpali-camera-ready]

## Design and reported result

- The model encodes document-page images into multi-vector representations and applies late interaction between text-query and page vectors, following the retrieval approach introduced for ColPali.[^faysse-2025-colpali-camera-ready]
- Its Qwen2-VL backbone has two billion parameters. The authors limit its page representation to 768 image patches to approximately match ColPali’s memory requirements.[^faysse-2025-colpali-camera-ready]
- In the reported ViDoRe ablation table, ColQwen2 scored 86.6 aggregate nDCG@5, versus 81.3 for the 1,024-patch ColPali reference. This supports an association in the tested adaptation, not causation or a universal backbone-selection rule.[^faysse-2025-colpali-camera-ready]

## Relationships

- Builds on: [ColPali vision-space document retrieval](colpali-vision-space-document-retrieval.md) by retaining vision-space multi-vector late interaction while changing the VLM backbone.[^faysse-2025-colqwen2]
- Evaluated by: [ViDoRe visual document retrieval benchmark](vidore-visual-document-retrieval-benchmark.md).[^faysse-2025-colqwen2]

[^faysse-2025-colpali-camera-ready]: Faysse et al., “ColPali: Efficient Document Retrieval with Vision Language Models” (2025 camera-ready manuscript), [source](../raw/2407.01449_ColPali/iclr2025_conference.tex).
[^faysse-2025-colqwen2]: Faysse et al., “Efficient Document Retrieval with Vision Language Models” (2025 version), [source](../raw/2407.01449_ColQwen2.md).
