---
type: Concept
title: BLIP-2 bootstrapping frozen vision–language models
description: A two-stage vision–language pre-training method that connects frozen image encoders and LLMs through a lightweight Q-Former trained for representation alignment and generation.
tags: [vision-language-pretraining, multimodal-learning, frozen-models, image-to-text-generation, parameter-efficiency]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T03:43:14Z }
sources:
  - id: li-2023-blip2
    resource: ../raw/2301.12597_BLIP-2/main.tex
    title: "BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models"
---

# BLIP-2 bootstrapping frozen vision–language models

BLIP-2 connects a frozen image encoder to a frozen LLM through a 188M-parameter Querying Transformer (Q-Former). It first trains Q-Former to select text-relevant visual features, then projects those features as soft visual prompts for the LLM; this lets the paper’s models support zero-shot instructed image-to-text generation without end-to-end pre-training of the large unimodal backbones.[^li-2023-blip2]

## Architecture and training

- Q-Former begins from BERT-base and has shared self-attention for an image-transformer and a text-transformer, plus cross-attention to frozen image features every other block. Its learned queries compress the paper’s ViT-L/14 feature array from $257 \times 1024$ to 32 query vectors of dimension 768, creating an information bottleneck.[^li-2023-blip2]
- Stage 1 attaches Q-Former to the frozen image encoder and jointly trains image-text contrastive (ITC), image-grounded text-generation (ITG), and image-text matching (ITM) objectives. The objectives use unimodal, multimodal causal, and bidirectional query-text attention masks, respectively; ITM uses hard negatives.[^li-2023-blip2]
- Stage 2 linearly projects the query outputs into the LLM embedding dimension and prepends them to text embeddings as soft visual prompts. A frozen decoder-only OPT is trained with language modeling; a frozen encoder-decoder FlanT5 is trained with prefix language modeling.[^li-2023-blip2]
- The reported pre-training uses 129M image-text pairs from BLIP’s corpus, including 115M LAION-400M images. It runs 250k first-stage and 80k second-stage steps; the largest ViT-g/FlanT5-XXL configuration took under six and under three days for those stages, respectively, on one 16-A100 (40GB) machine.[^li-2023-blip2]

## Reported evidence

- In zero-shot VQA, ViT-g/FlanT5-XXL reported 65.0 on VQAv2 test-dev, versus 56.3 for Flamingo-80B, while the table lists 108M versus 10.2B trainable parameters. These are the paper’s reported results under different data and model configurations, not a controlled cost-equivalence comparison.[^li-2023-blip2]
- On Flickr30K zero-shot retrieval after COCO fine-tuning, the ViT-g first-stage model reported text-retrieval and image-retrieval R@1 of 97.6 and 89.7. Adding ITG to ITC+ITM improved the corresponding COCO R@1 values from 84.5/67.2 to 85.4/68.3 in the reported ablation.[^li-2023-blip2]
- The paper reports that removing first-stage representation learning substantially lowers zero-shot VQA and can cause the OPT variant’s performance to degrade during generative training. It also reports stronger VQA with ViT-g rather than ViT-L, larger LLMs within a family, and instruction-tuned FlanT5 rather than OPT; these are configuration-specific findings rather than guarantees for arbitrary substituted backbones.[^li-2023-blip2]

## Limits

- The training samples contain one image-text pair, and the authors did not observe VQA gains from in-context examples. They attribute this to the absence of multi-pair sequences during pre-training; the method therefore does not establish few-shot in-context visual learning.[^li-2023-blip2]
- The supplied examples and limitations section show inaccurate factual knowledge, incorrect reasoning, and stale product knowledge. The authors also state that frozen LLM risks, including offensive output, social bias, and private-information leakage, carry into BLIP-2.[^li-2023-blip2]

## Relationships

- Extends: [BLIP bootstrapping language–image pre-training](blip-bootstrapping-language-image-pre-training.md) supplies the ITC, ITM, ITG, CapFilt-derived data recipe, and 129M-image corpus, while BLIP-2 keeps pretrained image and language backbones frozen and inserts Q-Former as their bridge.[^li-2023-blip2]
- Related: [LiT locked-image tuning](lit-locked-image-tuning.md) also freezes a pretrained image tower, but trains a text encoder with contrastive alignment rather than connecting vision features to a frozen generative LLM.[^li-2023-blip2]

## Evidence scope

The complete manuscript source, appendix, active figure and table inputs, and four rendered supplied PDFs (two architecture diagrams plus example and limitation figures) were inspected. `table/param_count.tex` was not included by `main.tex` and conflicts with the manuscript’s active 129M-image and 188M-Q-Former description; it is excluded as an unused draft artifact rather than treated as evidence.[^li-2023-blip2]

[^li-2023-blip2]: Li et al., “BLIP-2: Bootstrapping Language-Image Pre-training with Frozen Image Encoders and Large Language Models” (2023), [complete manuscript source](../raw/2301.12597_BLIP-2/main.tex).
