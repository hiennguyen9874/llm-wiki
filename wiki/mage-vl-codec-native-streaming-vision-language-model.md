---
type: Concept
title: Mage-VL codec-native streaming vision-language model
description: A 4B Qwen3-based VLM that uses a codec-guided sparse visual tokenizer and event gate for efficient offline and proactive streaming video understanding.
tags: [vision-language-models, video-understanding, streaming, efficient-inference, visual-tokenization]
status: draft
created: 2026-08-18
generated: { by: llm-wiki-agent/1, at: 2026-08-18T10:30:22Z }
sources:
  - id: microsoft-mage-2026
    resource: ../raw/2607.24904_Mage-VL/main.tex
    title: "Mage-VL: An Efficient Codec-Native Streaming Multimodal Foundation Model"
---

# Mage-VL codec-native streaming vision-language model

Mage-VL is a 4B vision-language model that replaces dense uniform video-frame encoding with Mage-ViT, a codec-guided sparse visual tokenizer. It retains all anchor-frame patches and allocates predicted-frame patches by local temporal coding difficulty, then uses an event gate to decide when a streaming decoder should respond. The technical report’s accuracy, efficiency, and streaming claims are author-reported; its direct comparisons are most informative where Mage-VL and Qwen3-VL-4B share the stated language backbone.[^microsoft-mage-2026]

## Architecture

- **Mage-ViT:** A 24-layer, 1024-hidden-dimension ViT with 16 attention heads processes variable-length sequences of 16×16-pixel patches. Shared 3D rotary positions retain each selected patch’s original spatial-temporal coordinate.[^microsoft-mage-2026]
- **Codec-native patchification:** The reported default HEVC/H.265 selector retains every I-frame patch and ranks P-frame patches with a weighted combination of motion-vector magnitude and residual energy. For DCVC-RT, it instead uses the neural codec’s per-patch coding likelihood; Mage-ViT consumes the resulting importance map, not codec syntax or latents.[^microsoft-mage-2026]
- **Language interface:** A two-layer MLP projects Mage-ViT features to Qwen3-4B-Instruct-2507. Images are one visual block; video windows are concatenated chronologically, without a separate video decoder.[^microsoft-mage-2026]
- **Proactive streaming:** A cognition gate predicts `silent` or `speak` from rolling visual features. On `speak`, the frozen base VLM generates from a recent local codec-window context; the report describes the gate, visual backbone, event-preserving feature extractor, and language model as frozen during the fifth training stage.[^microsoft-mage-2026]

## Training recipe

Mage-ViT is trained from scratch with a cluster-discrimination objective: MetaCLIP features label joint image/video samples by K-means cluster, and Mage-ViT learns against those prototypes. The report states approximately 560M unlabeled images and 100M video frames, variable-resolution image pretraining followed by joint image/video pretraining; its 64-frame codec mode uses a 4,096-token budget, about 75% below a dense 64-frame grid.[^microsoft-mage-2026]

For Mage-VL, the report describes five supervised stages: dense image and short-video captions; image instruction tuning and medium-video captions; longer temporal contexts; codec-native long-video adaptation; and gate-only streaming alignment. Its stated training corpus includes about 350M image-caption pairs, 54M image-instruction samples, 7.95M unique video-caption samples, and 3.35M streaming samples. The claimed AI-assisted caption pipeline scores captions for completeness, redundancy, coherence, and OCR fidelity, proposes prompt or harness-code changes, and requires human approval; this is a reported internal workflow rather than independently evaluated tooling guidance.[^microsoft-mage-2026]

## Reported evidence

- At a fixed 4,096-token video-representation budget, the report gives Mage-ViT 64-frame codec-mode versus 16-frame chunk-mode accuracies of 64.14 versus 60.45 on Diving-48 and 85.17 versus 85.13 on HMDB-51. These probe results use the paper’s backbone, data, and evaluation setup.[^microsoft-mage-2026]
- Against Qwen3-VL-4B, which the report says shares its 4B language backbone but uses a dense visual front-end, Mage-VL-tc32 reports higher scores on VideoMME (64.0 versus 59.7), MLVU-dev (68.7 versus 61.5), TimeLens-ActivityNet (45.4 versus 28.4), and VSI-Bench (64.3 versus 53.3). It is lower on some tasks, including MV-Bench (65.1 versus 66.7), VideoMME with subtitles (66.3 versus 70.2), and VideoMME-V2 (24.3 versus 24.4).[^microsoft-mage-2026]
- In the reported cross-codec table, replacing HEVC selection with DCVC-RT at inference gives an average score of 57.7 versus 58.0 while reducing average canvas size from 33.4 to 30.8. This supports compatibility with the two tested selectors, not codec-agnostic performance generally.[^microsoft-mage-2026]
- The tc8 configuration is reported to score 80.8 on NextQA in 415 seconds versus 79.8 in 1,460 seconds for Qwen3-VL-4B, on a single eight-B200 node. The table says Mage-VL uses full measured wall-clock time while Qwen3-VL time excludes estimated video-loading time, so the reported 3.5× ratio is not a fully symmetric end-to-end comparison.[^microsoft-mage-2026]
- For proactive streaming, the report gives Mage-VL-4B a 55.54 TimVal, 16.35 F1, 83.14 ROC-AUC, and 9.30 PR-AUC on SoccerNet-Caption under its strict position-matching setup. It also reports a 64.00 overall OVO-Bench score under a four-recent-frame, 1-fps protocol; baseline frame counts and methods vary.[^microsoft-mage-2026]

## Limits and evidence boundaries

- This is a supplied July 2026 Microsoft technical report. Its manuscript source, tables, and rendered figures were inspected, but no weights, code, training data, or independent replication are included in this source bundle. Consequently, all reported results and claims remain unverified here.[^microsoft-mage-2026]
- Comparisons across tables vary in visual budget, frame count, resolution, task metric, baseline size, and timing treatment. The source itself identifies dense-per-frame tasks such as MV-Bench and TempCompass as cases where Qwen3-VL can be stronger.[^microsoft-mage-2026]
- The report’s “Zero-Vision SFT” result is an ancillary LLaVA-OneVision-1.5 Quick Start experiment, not a controlled ablation of Mage-VL. It reports that replacing visual SFT with text reasoning SFT before multimodal RL improves its selected 24-benchmark average, but this does not establish a general post-training rule.[^microsoft-mage-2026]

## Relationships

- Related: [DINOv3 self-supervised visual foundation model](dinov3-self-supervised-visual-foundation-model.md) also studies a vision-first encoder trained from scratch, but Mage-ViT uses codec-guided temporal sparsity and visual-to-LLM integration rather than DINOv3’s self-distillation and Gram regularization.[^microsoft-mage-2026]
- Used by: [Vision-language task-to-model map](vision-language-task-to-model-map.md) for codec-native offline and proactive streaming video understanding.
- Synthesized by: [Recent vision-language research directions](recent-vision-language-research-directions.md) and [From unified pretraining to modern vision-language models](from-unified-pretraining-to-modern-vision-language-models.md) as evidence for efficient, streaming-native assistant-style VLMs.

[^microsoft-mage-2026]: Microsoft Mage Team, “Mage-VL: An Efficient Codec-Native Streaming Multimodal Foundation Model” (technical report, July 2026), [complete supplied manuscript source](../raw/2607.24904_Mage-VL/main.tex).
