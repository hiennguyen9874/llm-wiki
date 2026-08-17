---
type: Model System
title: MinerU-Diffusion
description: MinerU-Diffusion is a 2.5B document-OCR model that replaces autoregressive generation with block-level parallel diffusion decoding.
tags: [ocr, document-parsing, vision-language-models, diffusion-decoding, parallel-decoding]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:14:44Z }
sources:
  - id: mineru-diffusion-model-card
    resource: ../raw/MinerU-Diffusion-V1-0320-2.5B.md
    title: "MinerU-Diffusion-V1-0320-2.5B model card"
---

# MinerU-Diffusion

MinerU-Diffusion is a 2.5B-parameter document-OCR model that frames OCR as inverse rendering and uses block-level parallel diffusion decoding rather than conventional autoregressive token generation. The model card positions the approach as reducing dependence on language priors while improving the accuracy–throughput trade-off.[^mineru-diffusion-model-card]

## Decoding and reported performance

The documented inference interface exposes a fixed number of denoising steps, generated length, and block length, with a low-confidence dynamic remasking strategy and a configurable dynamic threshold. It provides text recognition from a page image; the card does not define structured outputs, supported document element types, or task prompts beyond `Text Recognition:`.[^mineru-diffusion-model-card]

All performance figures below are author-reported and not independently reproduced from this source bundle:

- Against MinerU2.5, the card claims throughput up to **3.26×** higher through threshold control.
- It identifies operating points of **2.12×** speedup at **99.9%** relative accuracy and **3.01×** speedup at **98.8%** relative accuracy.
- The card also summarizes the release as reaching up to **3.2×** faster decoding, without specifying how that rounded figure relates to the 3.26× comparison.[^mineru-diffusion-model-card]

## Operation

The supplied Transformers example uses Python 3.12.12, CUDA 12.8 builds of PyTorch 2.8.0, Transformers 4.52.1 or later, Triton 3.4.0, FlashAttention 2.8.3, and Liger Kernel 0.6.4. It loads the tokenizer, processor, and model with `trust_remote_code=True`, runs bfloat16 on CUDA, and passes the tokenizer plus custom mask-token, denoising, remasking, and stopping-criterion parameters to `generate`.[^mineru-diffusion-model-card]

The card credits MinerU, Qwen2-VL, SDAR, and LLaDA as upstream open-source foundations, and names SGLang, Nano-vLLM, and JetEngine as acceleration-engine bases. It separately cites MDLM, DiffuLLaMA, and Block Diffusion as theoretical foundations; these acknowledgements do not establish exact architectural inheritance or tested deployment compatibility.[^mineru-diffusion-model-card]

## Scope and trust limits

This local evidence is a model card. It links to an external technical report, Hugging Face repository, GitHub repository, and license file, but none are retained or inspected here. The source declares an MIT license, but the linked license text was not verified locally.[^mineru-diffusion-model-card]

The card references local banner, training-overview, and performance-trade-off images under `assets/`, but those attachments are absent from `raw/`; this synthesis relies only on accompanying textual claims. It does not provide benchmark protocols, hardware configuration, baseline settings, model architecture details, weights, inference code, or evaluations needed to independently assess its accuracy, throughput, robustness, or claimed reduction in language-prior reliance.[^mineru-diffusion-model-card]

[^mineru-diffusion-model-card]: MinerU-Diffusion authors, [*MinerU-Diffusion-V1-0320-2.5B model card*](../raw/MinerU-Diffusion-V1-0320-2.5B.md) (accessed 2026-08-17). Referenced `assets/banner.png`, `assets/train.png`, and `assets/performance_tradeoff.jpeg` are absent from the local source directory and were not inspected.
