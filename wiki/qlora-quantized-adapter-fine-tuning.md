---
type: Concept
title: QLoRA quantized adapter fine-tuning
description: QLoRA stores a frozen base model in 4-bit NF4, dequantizes it for higher-precision computation, and trains only LoRA adapters to reduce parameter-related fine-tuning memory.
tags: [qlora, lora, peft, fine-tuning, quantization, nf4]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:33:43Z }
sources:
  - id: qlora-summary
    resource: ../raw/QLoRA.md
    title: "QLoRA overview (Vietnamese summary)"
---

# QLoRA quantized adapter fine-tuning

QLoRA is a parameter-efficient fine-tuning method that stores frozen pretrained weights in 4-bit NormalFloat (NF4), temporarily dequantizes them for typically BF16 matrix computation, and trains only added LoRA adapters. It therefore reduces base-weight storage as well as the gradient and optimizer-state memory avoided by LoRA; it does not update the quantized base weights.[^qlora-summary]

## Mechanism

For a linear layer, QLoRA combines a frozen, quantized base branch with a trainable low-rank branch:

$$
Y = X\operatorname{dequant}(W_{\mathrm{NF4}}) + sX L_1L_2.
$$

The base weight is stored in NF4 but dequantized at use; the adapter matrices and activations are ordinarily held or computed in a higher-precision type such as BF16. Thus, “4-bit training” here primarily describes base-weight storage, not that every tensor or arithmetic operation is 4-bit.[^qlora-summary]

During backpropagation, gradients support the layer input and the LoRA factors, while the frozen base weight receives no optimizer update. This keeps gradients and optimizer states limited to the adapters, although activation memory still varies substantially with sequence length and batch size.[^qlora-summary]

## Quantization and memory techniques

NF4 uses a non-uniform 16-value codebook designed for approximately normally distributed, zero-centered weights; its levels are denser near zero than uniform INT4 levels. Block-wise quantization stores a scale per block, and NF4 represents zero exactly.[^qlora-summary]

Double quantization also quantizes the block scales. The source's illustrative block-size-64 calculation reduces scale metadata from $32/64=0.5$ bit per parameter for FP32 scales to about $8/64 + 32/(64\times256)\approx0.127$ bit per parameter when first-level scales are FP8 and second-level scales are shared FP32 metadata. This is a source-reported illustrative accounting, not a universal footprint.[^qlora-summary]

Paged optimizers use NVIDIA Unified Memory to move optimizer state between GPU and CPU memory when needed. Their stated purpose is handling transient memory spikes and avoiding out-of-memory failures, rather than reducing average memory use without trade-offs.[^qlora-summary]

## Relationships

- **Depends on:** [LoRA low-rank adaptation](lora-low-rank-adaptation.md); QLoRA retains LoRA's frozen-base, trainable low-rank update while changing base-weight storage.[^qlora-summary]
- **Qualified by:** [QLoRA memory, evaluation, and deployment trade-offs](qlora-memory-evaluation-and-deployment-trade-offs.md).

[^qlora-summary]: “QLoRA overview” (Vietnamese summary), [raw source](../raw/QLoRA.md), Sections 1–5. This is secondary-source evidence summarizing Dettmers et al., “QLoRA: Efficient Finetuning of Quantized LLMs,” NeurIPS 2023; the primary paper has not been independently ingested here.
