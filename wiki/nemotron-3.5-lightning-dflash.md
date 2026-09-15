---
type: Concept
title: Nemotron 3.5 Lightning DFlash Speculator
description: DFlash draft checkpoint for Nemotron-3.5-Lightning-30B-A3B with 833M dense-GQA drafting, SPEED-Bench 3.16 acceptance, and vLLM/llama.cpp low-latency serving.
tags: [nemotron, dflash, speculative-decoding, vllm]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:00:00Z }
sources:
  - id: nemotron-dflash
    resource: ../raw/DFlash.md
    title: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash
---

NVIDIA `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash` is the DFlash speculative-decoding checkpoint for the Nemotron-3.5-Lightning-30B-A3B hybrid LatentMoE family, intended to be paired with the target model in vLLM or llama.cpp to cut latency for small-batch or single-request serving by drafting more than one candidate token per verification step[^nemotron-dflash].

## Model identity and intended use

- Draft checkpoint: `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash`; targets are the Nemotron-3.5-Lightning-30B-A3B BF16 and NVFP4 reasoning models for reasoning, chat, RAG, and agentic workflows[^nemotron-dflash].
- This is a draft assistant, not a standalone target-model checkpoint[^nemotron-dflash].
- Intended deployment is lower-latency speculative decoding for low-concurrency data-centre and workstation workflows on data-centre GPUs and high-end local GPU systems[^nemotron-dflash].
- Nemotron-3.5-Lightning-30B-A3B supports native MTP, DFlash, and DSpark paths for DGX Spark and low-concurrency data-centre workflows; this release is the DFlash path[^nemotron-dflash].
- Release: Hugging Face 08/11/2026; deployment geography Global; ready for commercial or non-commercial use under OpenMDW-1.1[^nemotron-dflash].

## Architecture

- Draft architecture type: Dense GQA with Dense FFN MLP plus GQA attention layers; DFlash speculative-decoding attention uses non-causal, full-sequence grouped-query attention[^nemotron-dflash].
- Draft size: 833M total parameters, of which 481M are non-embedding parameters[^nemotron-dflash].
- The target family is described as a hybrid LatentMoE model using interleaved Mamba-2, MoE, and attention layers, while DFlash proposes candidate token blocks to improve generation speed during verification[^nemotron-dflash].
- Input: text strings as 1D sequences; maximum context up to 1M tokens; supported languages English, Spanish, French, German, Italian, and Japanese[^nemotron-dflash].
- Output: text strings as 1D sequences, including natural-language responses, reasoning traces, tool-use content, and structured outputs depending on chat-template configuration and application tooling[^nemotron-dflash].
- Models are designed for NVIDIA GPU-accelerated systems with CUDA for faster training and inference versus CPU-only solutions[^nemotron-dflash].

## Training

- Quantized/exported with Model Optimizer 0.45.0[^nemotron-dflash].
- Trained only on prompts from `nvidia/Nemotron-Post-Training-Dataset-v2` and the `nvidia/nemotron-post-training-v3` collection; original GPT responses were not used, and prompts were used for data synthesis to train the DFlash modules[^nemotron-dflash].
- Post-training corpus is synthetic data for reasoning, code, science, tool use, instruction following, structured outputs, and multilingual tasks; text training size 66B tokens repeated for 2 epochs[^nemotron-dflash].
- Collection and labeling method by dataset: hybrid automated, manually-collected/labelled, and synthetic[^nemotron-dflash].

## Evaluation

Evaluated on SPEED-Bench for speculative decoding by measuring acceptance rates over responses across coding, math, writing, translation, and related tasks[^nemotron-dflash]. Reported acceptance length with draft length 7, baseline `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`, `temperature=1.0`, `top_p=0.95`[^nemotron-dflash]:

| Category | SPEED-Bench Acceptance Length |
| --- | ---: |
| coding | 3.64 |
| humanities | 2.72 |
| math | 3.52 |
| multilingual | 3.75 |
| qa | 2.84 |
| rag | 3.60 |
| reasoning | 3.28 |
| roleplay | 2.60 |
| stem | 2.91 |
| summarization | 3.38 |
| writing | 2.49 |
| Overall Average | 3.16 |

All cells above are source-reported[^nemotron-dflash].

## Serving

- Supported runtimes: vLLM and llama.cpp; preferred OS Linux[^nemotron-dflash].
- Supported hardware compatibility: NVIDIA Blackwell GB200; tested hardware includes Hopper H100, Blackwell GB200, and Blackwell GeForce RTX 5090[^nemotron-dflash].
- Serve with vLLM via the DFlash recipes in the Nemotron-3.5-Lightning-30B-A3B NVFP4 model card, including the 1x DGX Spark GB10 section; local workflows use the model-card llama.cpp recipes on RTX 5090[^nemotron-dflash].
- The source frames integration as requiring use-case-specific testing under V-model unit and system validation for safety, technical, functional, and ethical requirements before deployment[^nemotron-dflash].

## Trust and limitations

- Speculative decoding is lossless acceleration: it does not affect the output distribution of the underlying reasoning model[^nemotron-dflash].
- Base-model limits carry over: possibly inaccurate, incomplete, or undesirable responses even on benign prompts, with biases or artifacts from training data and quality varying by domain, language, reasoning depth, and context length; developers should add application-specific safeguards and evaluate in the intended environment before production[^nemotron-dflash].
- Intended task/domain is text generation, reasoning, tool use, and agentic workflows accelerated with speculative decoding; performance metrics are accuracy, throughput, latency, and acceptance rate; quality standards reported as met[^nemotron-dflash].
- Bias subcard reports no participation considerations from adversely impacted groups, no mitigation measures, and no bias metric[^nemotron-dflash].
- Safety and security: applications are chat, instruction following, RAG, reasoning, and agentic AI; no life-critical application; use must comply with OpenMDW-1.1 and applicable laws; least-privilege access and dataset license constraints were applied[^nemotron-dflash].
- Privacy: no generatable or reverse-engineerable personal data; no personal data used to create the model; no user-interaction data used for training; dataset reviewed before release; provenance exists for all training datasets; labeling complies with privacy laws[^nemotron-dflash].

## Relationships

- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — same block-diffusion plus KV-injection DFlash family; this checkpoint targets vLLM/llama.cpp low-concurrency serving while that page documents the SGLang Spec V2 path and Qwen3.5 throughput evidence.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — low-concurrency, small-batch fit and lossless-verify framing behind the latency use case above.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — vLLM separate-draft-model configuration surface used to pair this checkpoint with its target.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — DSpark is the sibling confidence-driven block-drafting path named in the source alongside MTP and DFlash for DGX Spark and low-concurrency workflows.
- Related to [Nemotron 3.5 Lightning DSpark Speculator](nemotron-3.5-lightning-dspark.md) — sibling DSpark checkpoint for the same Nemotron-3.5-Lightning-30B-A3B family; DSpark reports 3.75 overall SPEED-Bench acceptance versus 3.16 for this DFlash checkpoint under the same draft-length-7 protocol.

## Coverage limits

- No local attachments were referenced by the source; Hugging Face checkpoints, the NVFP4/BF16 target model cards, Nemotron post-training collections, SPEED-Bench harness, Model Optimizer export, and the DFlash paper (`2602.06036`) were not inspected beyond the source description[^nemotron-dflash].
- Acceptance lengths and hardware/runtime claims are source-reported under the stated draft-length-7 and sampling protocol; latency, throughput, and speedup numbers beyond acceptance length are not given in the source and are not compiled here[^nemotron-dflash].
- vLLM and llama.cpp recipes, GB10/GB200/H100/RTX 5090 choices, and 1M-token context are workload-specific values from the source, not universal defaults[^nemotron-dflash].

[^nemotron-dflash]: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DFlash — `../raw/DFlash.md`.
