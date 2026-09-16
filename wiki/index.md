---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [Bi-IRRA multilingual text-to-image person retrieval](bi-irra-multilingual-person-retrieval.md) — Bi-IRRA extends IRRA to multilingual person retrieval with bidirectional masked reconstruction and global alignment over English and translated Chinese, French, and German descriptions.
- [CONQUER context-aware query-enhanced person search](conquer-context-aware-query-enhanced-person-search.md) — CONQUER combines training-time cross-modal representation refinement with MLLM-assisted query expansion and re-ranking for text-based person search, but its released code materially diverges from the manuscript.
- [FMFA full-mode fine-grained person retrieval](fmfa-full-mode-fine-grained-alignment.md) — FMFA augments IRRA with adaptive positive-pair weighting and sparse explicit token-patch alignment during training while retaining global-only text-to-image person retrieval at inference.
- [GA-DMS robust text-based person retrieval](ga-dms-robust-person-retrieval.md) — GA-DMS uses gradient-and-attention-derived token scores to mask suspected caption noise and reconstruct informative tokens while pretraining CLIP for text-based person retrieval.
- [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) — IRRA combines CLIP dual encoders, masked-language cross-modal relation reasoning, and similarity-distribution matching for efficient global person retrieval.
- [LDAT multilingual person-retrieval benchmark](ldat-multilingual-person-retrieval-benchmark.md) — LDAT translates four English person-retrieval datasets into Chinese, French, and German by filtering LLM translations and rewriting suspected errors with domain-adapted multimodal models.
- [MARS attribute-aware text-based person search](mars-attribute-aware-person-search.md) — MARS extends a RaSa/ALBEF person-search model with adjective–noun attribute supervision, text-guided masked image reconstruction, and deeper cross-modal attention.
- [MRA domain-aligned text-based person retrieval](mra-domain-aligned-person-retrieval.md) — MRA combines target-style synthetic pretraining data with explicit region-phrase and global image-text alignment for text-based person retrieval.
- [MVR multi-view semantic compensation for person retrieval](mvr-multi-view-semantic-compensation.md) — MVR uses LLM-generated query paraphrases and VLM-derived gallery captions to add mean-pooled text features to frozen text and image embeddings without retraining the retrieval model.
- [RDE for noisy-correspondence person retrieval](rde-noisy-correspondence-person-retrieval.md) — RDE combines dual-grained consensus filtering with a softened triplet loss to train text-to-image person retrieval models under mismatched image-text pairs.
- [TBPS-CLIP empirical person-search baseline](tbps-clip-empirical-person-search-baseline.md) — TBPS-CLIP systematically combines CLIP fine-tuning tricks, task-compatible augmentation, and complementary contrastive losses into a simple text-based person-search baseline.
- [WebPerson person-centric pretraining dataset](webperson-person-centric-pretraining-dataset.md) — WebPerson filters person images from COYO-700M and uses template-conditioned Qwen vision-language models to generate a large captioned pretraining corpus for person retrieval.
