---
okf_version: "0.2"
---

# LLM Wiki

The complete retrieval map for compiled knowledge. See [LLM Wiki Contract](../LLM-WIKI.md) for storage and maintenance rules.

## Concepts

- [ALIGN noisy image–text representation learning](align-noisy-image-text-learning.md) — A dual-encoder contrastive approach showing that web-scale, lightly filtered image alt-text can support transferable multimodal representations.
- [AltCLIP multilingual text-encoder alignment](altclip-multilingual-text-encoder-alignment.md) — A two-stage method that replaces CLIP's text encoder with XLM-R, distills its aligned text space from CLIP, then contrastively tunes the text tower against a frozen CLIP image encoder.
- [BridgeTower layer-wise vision–language fusion](bridgetower-layerwise-vision-language-fusion.md) — A vision–language architecture that injects successive high-level image and text encoder features into every cross-modal layer through lightweight bridge connections.
- [Chinese CLIP language-specific vision–language pre-training](chinese-clip-language-specific-vision-language-pretraining.md) — A Chinese CLIP adaptation that aligns a Chinese text encoder to a locked pretrained vision encoder before jointly tuning both towers on Chinese image–text pairs.
- [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) — A contrastive image–text pre-training method that uses language prompts to synthesize zero-shot image classifiers.
- [ColPali vision-space document retrieval](colpali-vision-space-document-retrieval.md) — A late-interaction retriever that indexes document-page images as VLM multi-vector embeddings, avoiding OCR, layout parsing, and chunking at ingestion.
- [ColQwen2 vision-space document retrieval](colqwen2-vision-space-document-retrieval.md) — A Qwen2-VL-based late-interaction page retriever that improved the paper’s ViDoRe score over its PaliGemma-based ColPali reference.
- [LiT locked-image tuning](lit-locked-image-tuning.md) — A contrastive-tuning method that freezes a pretrained image encoder and trains a text encoder to enable efficient zero-shot vision transfer.
- [Meta CLIP 2 worldwide CLIP scaling](meta-clip-2-worldwide-clip-scaling.md) — A CLIP training recipe that curates native-language worldwide web image–text pairs with per-language metadata and balancing, then scales training exposure and capacity to improve English and multilingual transfer jointly.
- [ModernVBERT small visual document retriever](modernvbert-small-visual-document-retriever.md) — A 250M-parameter early-fusion vision–language encoder and late-interaction variant designed for efficient visual document retrieval.
- [Perceiver IO structured input–output architecture](perceiver-io-structured-input-output-architecture.md) — A latent-attention architecture that maps arbitrary input arrays to query-defined structured outputs with linear scaling in input and output size.
- [PP-LCNet lightweight CPU convolutional neural network](pp-lcnet-lightweight-cpu-convolutional-neural-network.md) — A CPU-oriented lightweight CNN that combines depthwise-separable blocks with tail-localized accuracy enhancements for an Intel oneDNN/MKLDNN deployment target.
- [SigLIP 2 multilingual vision–language encoders](siglip2-multilingual-vision-language-encoders.md) — A multilingual, open-weight SigLIP successor that combines sigmoid image–text alignment with auxiliary captioning, self-supervision, and data-curation stages to improve global and dense visual representations.
- [ShieldGemma 2 image content moderation](shieldgemma-2-image-content-moderation.md) — A 4B Gemma 3-based image-safety classifier that applies an input policy to natural or synthetic images, with thresholdable violation scores for sexual, dangerous, and violence/gore content.
- [SigLIP sigmoid contrastive language–image pre-training](siglip-sigmoid-contrastive-language-image-pretraining.md) — A CLIP-style dual encoder that replaces batch-normalized contrastive softmax with an independently scored pairwise sigmoid loss.
- [TIPSv2 patch–text aligned vision–language pretraining](tipsv2-patch-text-aligned-vision-language-pretraining.md) — A vision–language encoder recipe that combines contrastive image–text learning with all-token masked-image distillation, head-only EMA, and mixed-granularity captions to improve dense patch–text alignment.
- [ViDoRe visual document retrieval benchmark](vidore-visual-document-retrieval-benchmark.md) — A page-level benchmark for visually rich document retrieval across document modalities, domains, languages, and practical retrieval tasks.
