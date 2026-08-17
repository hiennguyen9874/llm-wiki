---
type: Model System
title: LightOnOCR
description: LightOnOCR-2-1B is a 1B end-to-end document-OCR VLM that combines a native-resolution ViT with a Qwen3 decoder and optionally emits image bounding boxes.
tags: [ocr, document-parsing, vision-language-models, multilingual, reinforcement-learning, image-localization]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T14:13:20Z }
sources:
  - id: lightonocr-2-1b-model-card
    resource: ../raw/LightOnOCR-2-1B.md
    title: LightOnOCR-2-1B model card
  - id: lightonocr-paper
    resource: ../raw/2601.14251_LightOnOCR/templateArxiv.tex
    title: "LightOnOCR: A 1B End-to-End Multilingual Vision-Language Model for State-of-the-Art OCR"
  - id: lightonocr-1b-model-card
    resource: ../raw/LightOnOCR-1B-1025.md
    title: "LightOnOCR-1B-1025 model card"
---

# LightOnOCR

LightOnOCR-2-1B is a 1B-parameter, end-to-end vision-language model that transcribes document images into naturally ordered Markdown-like text without an explicit inference prompt. Its authors build it from a native-resolution vision encoder, compact visual projector, and Qwen3 decoder; a related checkpoint can additionally emit normalized bounding boxes for embedded images.[^lightonocr-paper]

## Architecture and output

The visual path initializes a native-resolution Mistral Small 3.1 vision transformer; the paper's diagram labels it 400M parameters. A randomly initialized two-layer GELU MLP projects its features into the decoder embedding space after $2\times2$ spatial merging, reducing visual-token count fourfold. The decoder initializes from Qwen3 GQA (labeled 600M in the diagram) and generates one linearized page representation. The authors remove image-break and image-end tokens, using one contiguous block of merged visual tokens followed by text tokens.[^lightonocr-paper]

The base OCR target represents images as `![image](image_N.png)`. Bounding-box variants extend this as `![image](image_N.png)x1,y1,x2,y2`, with coordinates normalized to $[0,1000]$.[^lightonocr-paper]

## Training recipe

The authors report growing the pretraining mixture from 17M to 43M pages, increasing the maximum longest edge from 1,024 to 1,540 pixels, and moving teacher supervision from Qwen2-VL-72B-Instruct to Qwen3-VL-235B-A22B-Instruct. The mixture includes scans, French and scientific documents, GPT-4o-annotated region crops, deliberately blank pages, and arXiv supervision derived by compiling TeX with `nvpdftex`.[^lightonocr-paper]

Before mixing, the paper describes normalizing markup, image and blank-page targets, deduplicating normalized text, and validating math for KaTeX compatibility. Training uses next-token prediction with loss masked to assistant tokens. The reported configuration uses 200-DPI pages, a 1,540-pixel maximum longest edge, augmentation probability 0.22, a global batch size of 384, 6,144 tokens, and DDP on 96 H100 80 GB GPUs.[^lightonocr-paper]

The OCR-specialized model starts from an average of the final five pretraining checkpoints and applies one epoch of GRPO-based RL with verifiable rewards. These rewards extend OlmOCR-style tests with repetition detection, EOS completion, KaTeX-renderable and clean math, and rewards for retaining visible headers, footers, and page numbers. The bbox path resumes pretraining with coordinate targets, then uses an IoU reward that also penalizes missing or hallucinated image IDs.[^lightonocr-paper]

## Reported evaluation

All results below are author-reported and not independently reproduced from this source bundle:[^lightonocr-paper]

- On the authors' OlmOCR-Bench evaluation **excluding the headers/footers category**, LightOnOCR-2-1B scores **83.2 ± 0.9** overall; its OCR-soup checkpoint scores 82.4 ± 0.9. The paper's base checkpoint scores 81.8 ± 0.9 and its bbox checkpoint 80.2 ± 0.9.
- The released LightOnOCR-bbox-bench combines 290 manually reviewed OlmOCR-derived pages with 565 automatically annotated arXiv pages. The bbox checkpoint reports F1@0.5 of **0.78/0.83**, mean IoU **0.70/0.77**, and exact count accuracy **83.8/85.0** on its OlmOCR/arXiv subsets, respectively.
- On one H100 80 GB GPU, the paper reports 5.71 pages/s for the BF16 LightOnOCR-2 checkpoint on the full 1,403-page OlmOCR-Bench evaluation. Its table reports 3.28 pages/s for FP8 olmOCR-2 and 1.70 pages/s for BF16 Chandra, but cross-system speed comparisons depend on the authors' library and inference settings.
- Weight-space interpolation between bbox- and OCR-specialized checkpoints raises OCR score as OCR-task-vector strength $\alpha$ increases, while bbox score falls to zero at $\alpha \geq 0.6$ in the supplied plot. The authors select $\alpha \approx 0.1$ as a balance point rather than an across-task optimum.[^lightonocr-paper]

## Model cards and operation

The current `LightOnOCR-2-1B` card identifies this checkpoint as LightOn's RLVR-refined flagship OCR variant and lists Apache-2.0. It documents Transformers support starting with version 5.0.0, using `LightOnOcrForConditionalGeneration` and `LightOnOcrProcessor`, and a vLLM server configuration that allows one image per prompt and disables multimodal-processor and prefix caching. Its examples use 200-DPI PDF rendering with a 1,540-pixel target longest dimension and retain aspect ratio.[^lightonocr-2-1b-model-card]

The earlier 1B-1025 card describes a full-BF16 checkpoint for inference and further fine-tuning, lists Apache-2.0, and declares `lightonai/LightOnOCR-2-1B` as its newer version. It documents vLLM support from version 0.11.1 (dated 2025-11-24); its example serves the 1B-1025 checkpoint with one image allowed per prompt and disables multimodal-processor and prefix caching. The card recommends rendering each PDF page as PNG or JPEG at a 1,540-pixel longest edge while preserving aspect ratio; batching is supported by vLLM.[^lightonocr-1b-model-card]

The 2-1B card says the model supports LoRA fine-tuning, domain adaptation, and multilingual task-specific fine-tuning, and recommends the `LightOnOCR-2-1B-base` variant as the starting point. The earlier card also names 32k- and 16k-vocabulary variants as European-language-focused alternatives. Its Transformers example instead installs Transformers from source and loads `LightOnOCR-2-1B-base`, so it does not establish a Transformers inference path for 1B-1025.[^lightonocr-2-1b-model-card][^lightonocr-1b-model-card]

## Scope and trust limits

The authors position the model for printed documents, particularly scientific PDFs, typed scans, European/Latin-script languages, multi-column pages, and tables. They explicitly report weaker support for non-Latin scripts and inconsistent handwriting transcription.[^lightonocr-paper]

The local evidence includes an author manuscript, its bibliography, architecture and merging figures, qualitative examples, and two model-card snapshots. It does not include weights, released datasets or benchmark contents, preprocessing/training/evaluation code, or the complete inference implementation. The current card's locally referenced `lightonocr-banner.png` and `benchmark.png` are absent; the 1B-1025 card's local banner image is absent and its benchmark chart is remotely hosted, so these visual assets were not inspected. The earlier card's body combines 1B-1025 deployment instructions with LightOnOCR-2 announcements and code. The paper's state-of-the-art claim uses a modified OlmOCR-Bench aggregate that excludes headers/footers because the authors regard that category's reward for omission as misaligned with full-page transcription; it is therefore not directly comparable to results using the original aggregate.[^lightonocr-paper][^lightonocr-2-1b-model-card][^lightonocr-1b-model-card]

## Contradictions

- The 1B-1025 card's title, vLLM command, and model identifier refer to `LightOnOCR-1B-1025`, while its announcement and Transformers example refer to LightOnOCR-2. Its reported architecture, performance, and support claims therefore cannot be assigned to one version from this card alone.[^lightonocr-1b-model-card]

## Relationships

- **Compared with:** [DeepSeek-OCR](deepseek-ocr.md), [PaddleOCR-VL](paddleocr-vl.md), and [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) are included as document-parsing baselines in the paper's reported evaluations; cross-paper comparison requires matched benchmark versions, rendering, and inference settings.

[^lightonocr-paper]: Taghadouini, Cavaillès, and Aubertin, *LightOnOCR: A 1B End-to-End Multilingual Vision-Language Model for State-of-the-Art OCR*, local LaTeX source at [templateArxiv.tex](../raw/2601.14251_LightOnOCR/templateArxiv.tex), including `figures/model_arch.png`, `figures/model_parameter_merging.pdf`, and five qualitative example images (accessed 2026-08-17).
[^lightonocr-2-1b-model-card]: LightOn, [*LightOnOCR-2-1B model card*](../raw/LightOnOCR-2-1B.md) (accessed 2026-08-17). The referenced local `lightonocr-banner.png` and `benchmark.png` are absent and were not inspected.
[^lightonocr-1b-model-card]: LightOn, [*LightOnOCR-1B-1025 model card*](../raw/LightOnOCR-1B-1025.md) (accessed 2026-08-17). The referenced local `lightonocr-banner.png` is absent; the benchmark chart is external and was not inspected.
