---
type: Concept
title: QLoRA memory, evaluation, and deployment trade-offs
description: QLoRA reduces parameter-related fine-tuning memory, but activation peaks, dequantization overhead, data-task fit, and limited reported evaluations constrain its practical and quality claims.
tags: [qlora, lora, peft, fine-tuning, gpu-memory, evaluation, limitations]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:33:43Z }
sources:
  - id: qlora-summary
    resource: ../raw/QLoRA.md
    title: "QLoRA overview (Vietnamese summary)"
---

# QLoRA memory, evaluation, and deployment trade-offs

QLoRA reduces parameter-related fine-tuning memory by quantizing frozen base weights and training only LoRA adapters, but it does not similarly quantize activations. Sequence length and batch size can therefore still cause large VRAM peaks; dequantization can also make training slower than BF16 LoRA in some systems.[^qlora-summary]

## Reported memory and quality results

The source reports that the QLoRA paper fine-tuned LLaMA 65B on a 48-GB GPU, contrasting this with an estimate exceeding 780 GB for 16-bit full fine-tuning. It also reports an experiment in which NF4 with double quantization achieved mean 5-shot MMLU of 53.1 versus 53.0 for BF16 LoRA across the stated LLaMA 7B–65B setup. These are setup-specific reported results, not evidence that QLoRA universally matches full fine-tuning or BF16 LoRA.[^qlora-summary]

The reported Guanaco chatbot scores use GPT-4 judging on a particular Vicuna benchmark and prompt set; the source notes wide confidence intervals and the limits of chatbot benchmarks and AI judging. A reported 99.3%-of-ChatGPT score for Guanaco 65B must therefore not be read as general capability equivalence.[^qlora-summary]

## Data and configuration choices

The source attributes QLoRA's outcome strongly to data quality and task fit: its cited OASST1 instruction data, though much smaller than a sampled FLAN v2 set, performed better for chatbot evaluation, whereas FLAN v2 could better fit knowledge-oriented evaluation. No instruction dataset is consequently established as best for every target behavior.[^qlora-summary]

Its example configuration uses NF4, double quantization, BF16 compute, rank 16, and adapters across attention and MLP projections. These are starting choices, not a guaranteed configuration: the source reports that broad placement across suitable linear layers mattered more than rank increases in the reported experiments.[^qlora-summary]

## Decision boundary

QLoRA is suited to supervised or instruction fine-tuning and domain adaptation when BF16 LoRA will not fit available GPU memory, or when many small adapters must share an unchanged base model. BF16 LoRA can be preferable when memory is sufficient and training speed or avoiding dequantization overhead is more important. Full fine-tuning remains a candidate when resources and data permit and adapter methods do not meet the required quality; these are practical inferences from the source's memory, performance, and limitation discussion.[^qlora-summary]

## Limitations of the reported evidence

The source reports that the underlying work did not directly compare 16-bit full fine-tuning with QLoRA at 33B and 65B, did not comprehensively assess all benchmarks, bit widths, or alternative PEFT methods, and treated AI judging as imperfect. Reported results should remain qualified by those coverage limits.[^qlora-summary]

## Relationships

- **Qualifies:** [QLoRA quantized adapter fine-tuning](qlora-quantized-adapter-fine-tuning.md).
- **Extends:** [LoRA training and deployment trade-offs](lora-training-and-deployment-trade-offs.md); QLoRA adds frozen-base quantization and its related memory and runtime consequences.[^qlora-summary]

[^qlora-summary]: “QLoRA overview” (Vietnamese summary), [raw source](../raw/QLoRA.md), Sections 5–11. This is secondary-source evidence summarizing Dettmers et al., “QLoRA: Efficient Finetuning of Quantized LLMs,” NeurIPS 2023; the primary paper has not been independently ingested here.
