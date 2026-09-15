---
type: Concept
title: QLoRA Quantized Low-Rank Adaptation
description: Memory-efficient LLM fine-tuning that freezes 4-bit NF4 base weights and trains only BF16 LoRA adapters with double quantization and paged optimizers.
tags: [finetuning, lora, quantization, memory]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: qlora-src
    resource: ../raw/QLoRA.md
    title: QLoRA là gì?
---

QLoRA freezes a 4-bit quantized base model, dequantizes weights to BF16 on the fly for compute, and trains only small LoRA adapters; with double quantization and paged optimizers it fine-tuned LLaMA 65B on one 48 GB GPU instead of the 780+ GB needed for 16-bit full fine-tuning[^qlora-src].

The source compiles the NeurIPS 2023 paper "QLoRA: Efficient Finetuning of Quantized LLMs" by Tim Dettmers and colleagues[^qlora-src].

## How it combines quantization and LoRA

A linear layer `Y = XW` becomes `Y = XW + s·X·L1·L2`, where `W` is frozen, `L1 (h×r)` and `L2 (r×o)` are the only trainable weights, and `r` is much smaller than `h` and `o`[^qlora-src].

Example: a 4096×4096 matrix has ~16.8M parameters, while rank-16 LoRA adds only `4096×16 + 16×4096 = 131,072` parameters, under 1%[^qlora-src].

In QLoRA[^qlora-src]:

- **Storage:** base weights in NF4 4-bit.
- **Compute:** weights dequantized to BF16 for matmul, then `Y(BF16) = X(BF16)·dequant(W(NF4)) + X(BF16)·L1(BF16)·L2(BF16)`.
- **Gradients and optimizer:** only for LoRA weights; base-weight gradients are not stored or used for updates.
- **Common misconception:** this is not full 4-bit arithmetic training; 4-bit is primarily a storage format while compute stays in BF16 or another 16-bit type.

## Three technical contributions

### NF4 NormalFloat

Standard INT4 uses uniform levels such as `-8..7`, which fits LLM weights poorly because weights cluster near zero in an approximately zero-centered normal distribution[^qlora-src].

NF4 uses 16 non-uniform levels with denser coverage near zero so each bin holds roughly equal probability mass under a normal distribution, plus an exact zero representation needed for padding and zeros[^qlora-src].

Per-block procedure: split tensor into blocks, store one scale per block (often from max absolute value), normalize to `[-1,1]`, map each weight to the nearest of 16 NF4 values, and store the 4-bit code plus scale[^qlora-src].

Reported mean perplexity on Pile Common Crawl, lower is better[^qlora-src]:

| Format | Mean perplexity |
| --- | ---: |
| INT4 | 34.34 |
| FP4 E2M1 | 31.07 |
| FP4 E3M0 | 29.48 |
| NF4 + Double Quantization | **27.41** |

### Double Quantization

Block-wise quantization must also store scales. With block size 64 and FP32 scales, the overhead is `32/64 = 0.5` bit per parameter, so "4-bit" really costs ~4.5 bits[^qlora-src].

Double Quantization quantizes the first-level scales themselves: weights in NF4 with block 64, first-level scales in FP8, second-level FP32 scales shared over a larger group such as 256 scales[^qlora-src].

New cost is approximately `8/64 + 32/(64×256) ≈ 0.127` bit per parameter, saving `0.373` bit per parameter or about 3 GB on a 65B model[^qlora-src].

### Paged Optimizers

Training memory spikes — for example long sequences in one mini-batch, especially with gradient checkpointing — can cause transient CUDA OOM even when average use fits[^qlora-src].

Paged Optimizers use NVIDIA Unified Memory to spill optimizer states from GPU VRAM to CPU RAM when nearly full and bring them back for the update, analogous to OS paging between RAM and disk[^qlora-src].

The goal is avoiding spike-driven OOM rather than lowering average memory; the source calls this important for fitting 33B and 65B fine-tunes on 24/48 GB GPUs[^qlora-src].

## Forward and backward flow

Forward per layer: read NF4 weights, dequantize second-level scales, dequantize first-level scales, dequantize weights to BF16, compute base and LoRA branches, and sum them as `Y = X·W(dequantized) + X·A·B`[^qlora-src].

Backward: gradients flow through the frozen base branch to compute layer-input and LoRA gradients, but `dL/dW` is not used to update `W`; only `dL/dA` and `dL/dB` go to the optimizer[^qlora-src].

## Where memory is saved

Total training memory splits as `M = M(weights) + M(gradients) + M(optimizer) + M(activations)`[^qlora-src].

- **Full fine-tuning:** weights, gradients, and optimizer states for the whole model, plus activations.
- **LoRA:** base weights still in FP16/BF16; gradients and optimizer only for adapters; activations unchanged.
- **QLoRA:** base weights in NF4 plus metadata; gradients and optimizer only for adapters with optional paging; activations still BF16, usually with gradient checkpointing[^qlora-src].

Activations are not compressed the same way, so sequence length and batch size can still sharply increase VRAM[^qlora-src].

## Reported results and limits

The paper trained over 1,000 models from ~80M to 65B across architectures and eight instruction-tuning datasets[^qlora-src].

On LLaMA 7B–65B with Alpaca and FLAN v2, mean 5-shot MMLU was 53.0 for BF16, 52.2 for FP4, and 53.1 for NF4 with double quantization — parity between NF4+DQ and BF16 LoRA in that setup, not a proof that QLoRA always matches full fine-tuning[^qlora-src].

The authors fine-tuned LLaMA on OpenAssistant OASST1 to produce Guanaco, with reported inference footprints around 5 GB for 7B, 10 GB for 13B, 21 GB for 33B, and 41 GB for 65B[^qlora-src].

On the Vicuna benchmark with GPT-4 judging, Guanaco 65B reached 99.3% of ChatGPT, 33B reached 97.8%, and 7B reached 87.0%; interpret this only as that dialogue benchmark, prompt set, and judge, with wide confidence intervals and author caveats that chatbot benchmarks of that era were not yet trustworthy[^qlora-src].

A notable data finding was that fit and quality beat raw quantity: 9,000-sample OASST1 gave better chatbot behavior than a 450,000-sample FLAN v2 subset, while FLAN v2 could suit knowledge benchmarks such as MMLU better — there is no single best instruction set for chatbot naturalness, exam knowledge, and enterprise workflow compliance simultaneously[^qlora-src].

## What QLoRA is not

- Not full-model quantization-aware training: base weights stay frozen[^qlora-src].
- Not everything in 4-bit: base weights NF4, LoRA adapters usually BF16, activations usually BF16, some optimizer states and scale metadata in 8/16/32-bit[^qlora-src].
- Not necessarily faster: it optimizes memory, and per-step dequantization can make it slower than BF16 LoRA on some systems[^qlora-src].
- Not a way to make a small model capable like a large one: it lets smaller hardware fine-tune larger base models but does not remove base-model capability limits[^qlora-src].

## Paper-stated limitations

- No direct 33B/65B comparison between 16-bit full fine-tuning and QLoRA because full fine-tuning was too resource-intensive[^qlora-src].
- Only selected benchmarks such as MMLU and chatbot tests; no BigBench, RAFT, or HELM coverage[^qlora-src].
- No comprehensive study of other bit widths such as 3-bit, and no full comparison against non-LoRA PEFT adapters[^qlora-src].
- Chatbot quality depends strongly on data and evaluation method, and GPT-4-as-judge correlates with humans overall but has cases of substantial disagreement[^qlora-src].

## Typical configuration and selection

Starting-point Hugging Face stack uses 4-bit NF4 with double quantization and BF16 compute, plus LoRA on all suitable linear layers[^qlora-src]:

```python
from transformers import BitsAndBytesConfig
from peft import LoraConfig

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype="bfloat16",
)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
)
```

The paper found placing LoRA on all suitable linear layers mattered more than only raising rank, and rank mattered less than expected once coverage was broad[^qlora-src].

Use QLoRA when GPU memory cannot hold BF16 LoRA, when fine-tuning 7B–70B models on one or few GPUs, when producing many per-customer or per-domain adapters, when keeping the base model fixed and distributing small adapters, or for supervised, instruction, and domain-adaptation fine-tuning[^qlora-src].

Prefer BF16 LoRA when memory allows, training speed matters, dequantization overhead should be avoided, or maximum numeric stability is wanted; prefer full fine-tuning with sufficient resources, very large data, deep whole-model behavior change, or when LoRA/QLoRA quality is insufficient[^qlora-src].

## Relationships

- Uses [vLLM LoRA Adapters](vllm-lora-adapters.md) — serving-time counterpart that loads per-request LoRA adapters of the kind QLoRA trains.
- Uses [SGLang LoRA Serving](sglang-lora-serving.md) — multi-LoRA serving backend for adapters produced by QLoRA-style training.
- Uses [SGLang Quantization](sglang-quantization.md) — inference quantization context contrasting with QLoRA training-time base-weight storage.
- Uses [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — format and toolchain context for placing NF4 base-weight quantization.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — evaluation discipline for interpreting NF4 perplexity and MMLU parity claims.

[^qlora-src]: QLoRA là gì? — `../raw/QLoRA.md`.
