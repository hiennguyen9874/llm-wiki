---
type: Concept
title: ONE-PEACE multimodal representation learning
description: A 4B representation model that combines modality-specific adapters and FFNs with shared self-attention to align and fuse vision, audio, and language.
tags: [multimodal-learning, representation-learning, contrastive-learning, masked-modeling, vision-language-pretraining, audio-language-pretraining, transformer]
status: stable
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T04:00:00Z }
sources:
  - id: wang-2023-one-peace
    resource: ../raw/2305.11172_ONE-PEACE/main.tex
    title: "ONE-PEACE: Exploring one general Representation Model toward unlimited modalities"
---

# ONE-PEACE multimodal representation learning

ONE-PEACE is a 4B-parameter representation model for vision, environmental audio, and language. It shares self-attention across modalities while retaining adapters and feed-forward networks (FFNs) per modality, then combines cross-modal contrastive alignment with masked intra-modal denoising contrastive learning (DCL).[^wang-2023-one-peace]

## Architecture and objectives

- Each modality has a separate adapter: an hMLP image patchifier, a convolutional waveform feature extractor, or BPE text embeddings. Every fusion-encoder block shares self-attention but routes features through vision, audio, or language FFNs; the resulting components can be assembled as unimodal or fused branches.[^wang-2023-one-peace]
- The reported configuration has 40 layers, 1,536 hidden dimensions, 24 attention heads, and 4B parameters. Its three FFN pools account for 1.15B parameters each, compared with 378M in shared attention; a vision-only branch activates 1.52B parameters.[^wang-2023-one-peace]
- Cross-modal contrastive loss symmetrically aligns normalized special-token embeddings from image-text and audio-text pairs using negatives gathered across devices. DCL masks modality units, encodes only the visible units, and has a lightweight decoder contrastively predict the corresponding stop-gradient features from an unmasked encoder pass.[^wang-2023-one-peace]
- The paper applies DCL to image, audio, text, image-text, and audio-text inputs. In its 20M-pair ViT-B/16 ablation, shared attention with separate FFNs yielded the strongest COCO zero-shot retrieval and ImageNet zero-shot results; adding DCL to all three vision-language input types improved COCO image-to-text/text-to-image R@1 from 35.94/23.87 to 39.94/26.94 and ImageNet fine-tuning accuracy from 82.20% to 83.75%.[^wang-2023-one-peace]

## Training and transfer

- Vision-language pretraining uses filtered LAION-2B image-text data: about 1.5B pairs after image, CLIP-score, language, and text-length filters. It runs 200,000 steps with batch size 32,768; the paper describes this as 6.4B image-text training pairs. The vision and language components are randomly initialized.[^wang-2023-one-peace]
- Audio-language pretraining uses about 2.4M environmental-sound/text pairs (about 8,000 hours), including T5-rewritten tag captions in some source datasets. It freezes the vision and language components, including shared attention, and updates audio-specific parameters, using the shared language space as the audio alignment anchor. The audio feature extractor alone is initialized from WavLM.[^wang-2023-one-peace]
- The authors report qualitative retrieval of image/audio and multimodal image queries despite not training image-audio pairs. This is a small illustrative result, rather than a quantitative guarantee that text-mediated alignment transfers across arbitrary modality pairs.[^wang-2023-one-peace]

## Reported evaluation and limits

- On the paper's task-specific protocols, ONE-PEACE reports 89.8% ImageNet-1K top-1 after ImageNet-21K intermediate fine-tuning; 63.0 multi-scale ADE20K mIoU; and 88.1% Kinetics-400 top-1 while the pretrained backbone remains frozen and temporal/spatial MLP adapters are trained.[^wang-2023-one-peace]
- For audio-language evaluation, it reports AudioCaps text-to-audio/audio-to-text R@1 of 42.5/51.0 and Clotho R@1 of 22.4/27.1 after retrieval fine-tuning; 91.8% zero-shot ESC-50 accuracy; and 69.7 FSD50K mAP after fine-tuning.[^wang-2023-one-peace]
- For image-text retrieval, it reports zero-shot COCO image-to-text/text-to-image R@1 of 64.7/48.0, and fine-tuned R@1 of 84.1/65.4. It also reports RefCOCO, RefCOCO+, and RefCOCOg test scores of 89.26, 83.23, and 89.27 respectively. These are selected 2023 comparisons with specified task heads, data, and fine-tuning protocols; they do not establish present-day state of the art or general reliability.[^wang-2023-one-peace]
- The authors identify weaker zero-shot image-text retrieval and vision-language understanding than some contemporary models, attributing this to less image-text exposure and no pure-text pretraining or language-model initialization. The training corpus also filters text to English and uses noisy web image-text data, so the results do not establish multilingual coverage, unbiased data, or reproducibility beyond the reported public-data recipe.[^wang-2023-one-peace]

## Relationships

- Related: [BEiT-3 multiway masked multimodal pretraining](beit-3-multiway-masked-multimodal-pretraining.md) likewise shares attention while separating modality FFNs, but BEiT-3 covers vision and language through masked discrete-token prediction; ONE-PEACE adds audio and uses contrastive reconstruction targets rather than an external visual tokenizer.[^wang-2023-one-peace]
- Related: [CLIP natural-language image pre-training](clip-natural-language-image-pretraining.md) provides the symmetric global image-text contrastive pattern that ONE-PEACE extends to audio-text alignment, while ONE-PEACE also trains a shared-attention fusion encoder and DCL objective.[^wang-2023-one-peace]

## Evidence scope

Claims were compiled from the complete manuscript source included by `main.tex`, its eleven supplied result and configuration tables, and all supplied architecture, ablation, grounding, and retrieval figures. The unreferenced legacy `1_intro.tex` and `3_method.tex` variants, bibliography, and TeX support files were excluded because no retained claim depends on them.[^wang-2023-one-peace]

[^wang-2023-one-peace]: Wang et al., “ONE-PEACE: Exploring one general Representation Model toward unlimited modalities” (2023), [complete manuscript source](../raw/2305.11172_ONE-PEACE/main.tex).