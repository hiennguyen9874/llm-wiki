---
type: Model System
title: Unlimited OCR
description: Unlimited OCR is a 3B-total, 500M-active end-to-end document OCR VLM that uses Reference Sliding Window Attention to bound decode-side KV-cache growth for one-shot multi-page parsing.
tags: [ocr, document-parsing, vision-language-models, long-horizon, kv-cache, mixture-of-experts]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:30:03Z }
sources:
  - id: unlimited-ocr-report
    resource: ../raw/2606.23050_Unlimited-OCR/main.tex
    title: Unlimited OCR Works
  - id: unlimited-ocr-model-card
    resource: ../raw/2606.23050_Unlimited-OCR/README.md
    title: Unlimited OCR model card
---

# Unlimited OCR

Unlimited OCR is an end-to-end document OCR model derived from DeepSeek-OCR. It retains the compressed DeepEncoder and 3B-total, 500M-active MoE decoder, but replaces every decoder attention layer with [Reference Sliding Window Attention](reference-sliding-window-attention.md) (R-SWA). This gives each generated token persistent access to the document/prompt prefix and a bounded recent-output window, so decode-side cache use and attention cost do not grow with output length for a fixed prefix.[^unlimited-ocr-report]

## Architecture and inference

R-SWA retains all reference tokens (the visual tokens and prompt) and only the most recent output tokens; the report's default output window is 128 tokens. Thus, after generating $T$ tokens, the stated cache size is $L_m + \min(n,T)$ rather than $L_m + T$, where $L_m$ is the fixed prefix length and $n$ is the output-window width.[^unlimited-ocr-report]

DeepEncoder provides 16-fold visual-token compression. For multi-page inputs, the model uses its 1024x1024 Base mode; the report states that one such page becomes 256 visual tokens. Single-page inference can instead use the cropped, dynamic-resolution Gundam configuration.[^unlimited-ocr-report][^unlimited-ocr-model-card]

The model card documents Transformers inference plus SGLang and vLLM deployment. Its examples set a 32,768-token maximum generation length and use the Base configuration for multi-image or PDF input after rendering PDF pages to images.[^unlimited-ocr-model-card]

## Training

The authors continued training from a DeepSeek-OCR checkpoint for 4,000 steps, freezing DeepEncoder and training decoder parameters. They describe about 2 million document OCR examples with a 9:1 single-page-to-multi-page ratio; multi-page examples are synthesized by concatenating 2--50 single-page samples and packed to 32K tokens.[^unlimited-ocr-report]

## Reported evaluation

All results are author-reported and have not been independently reproduced:[^unlimited-ocr-report]

- On OmniDocBench v1.5, the report gives Unlimited OCR an overall score of **93.23**, text edit distance **0.038**, formula CDM **92.61**, table TEDS **90.93**, and reading-order edit distance **0.045**. Its table gives the DeepSeek-OCR baseline 87.01 overall and 0.073 text edit distance; this is not a controlled comparison with every independently published system.
- On OmniDocBench v1.6, it reports a **93.92** overall score, 0.042 text edit distance, 95.79 formula CDM, 90.16 table TEDS, and 0.129 reading-order edit distance. The table sources non-Unlimited baselines from the OmniDocBench repository, without complete matched configurations.
- In the authors' in-house multi-page evaluation, edit distance is 0.0572 at 20 pages and 0.1069 at 40+ pages; reported Distinct-35 is 99.89% and 96.90%, respectively. The source says each page-count category has at least ten books but does not provide the test set.
- Under a reported 512-concurrency Base-mode setup, it achieves 5,580 tokens/s versus 4,951 for DeepSeek-OCR. The source attributes the 12.7% gain to bounded decode attention; its separate latency plot shows a stable R-SWA attention-kernel duration through 6,000 decode steps.[^unlimited-ocr-report]

## Limits and trust

- “Unlimited” does not mean unbounded input: R-SWA bounds only the decode-side history. The visual/prompt prefix remains resident, so the finite 32K context length still limits the number and resolution of prefetched pages.[^unlimited-ocr-report]
- The local bundle contains the report, three source figures, and model-card inference instructions. It lacks local weights, training data, evaluation data and scripts, complete prompts, and reproducible hardware/configuration details; the reported accuracy, multi-page behavior, and throughput cannot be independently verified from it.[^unlimited-ocr-report][^unlimited-ocr-model-card]
- The report proposes applying R-SWA to ASR and translation but evaluates document OCR only; broader task effectiveness is unverified.[^unlimited-ocr-report]

## Relationships

- **Builds on:** [DeepSeek-OCR](deepseek-ocr.md), retaining its DeepEncoder and MoE decoder while replacing standard decoder attention.[^unlimited-ocr-report]
- **Uses:** [Reference Sliding Window Attention](reference-sliding-window-attention.md), the persistent-reference and bounded-output attention pattern introduced by this report.[^unlimited-ocr-report]

[^unlimited-ocr-report]: Yin et al., *Unlimited OCR Works*, local LaTex source at [main.tex](../raw/2606.23050_Unlimited-OCR/main.tex), including [R-SWA attention diagram](../raw/2606.23050_Unlimited-OCR/Figs/1.pdf), [architecture diagram](../raw/2606.23050_Unlimited-OCR/Figs/3.pdf), and [attention-scaling plot](../raw/2606.23050_Unlimited-OCR/Figs/attn_scaling-2-Arial-95.pdf) (accessed 2026-08-17).
[^unlimited-ocr-model-card]: Baidu Inc., *Unlimited OCR model card*, local [README.md](../raw/2606.23050_Unlimited-OCR/README.md) (accessed 2026-08-17).
