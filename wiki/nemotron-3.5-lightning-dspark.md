---
type: Concept
title: Nemotron 3.5 Lightning DSpark Speculator
description: DSpark draft checkpoint for Nemotron-3.5-Lightning-30B-A3B with 967M dense-GQA drafting, SPEED-Bench 3.75 acceptance, and vLLM serving for DGX Spark.
tags: [nemotron, dspark, speculative-decoding, vllm]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:00:00Z }
sources:
  - id: nemotron-dspark
    resource: ../raw/DSpark.md
    title: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark
---

NVIDIA `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark` is the DSpark speculative-decoding checkpoint for the Nemotron-3.5-Lightning-30B-A3B hybrid LatentMoE family, intended to be paired with the target model in vLLM to cut latency for DGX Spark and low-concurrency data-centre serving through confidence-scheduled block drafting with higher reported accepted length than the sibling DFlash path[^nemotron-dspark].

## Model identity and intended use

- Draft checkpoint: `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark`; targets are the Nemotron-3.5-Lightning-30B-A3B BF16 and NVFP4 reasoning models for reasoning, chat, RAG, and agentic workflows[^nemotron-dspark].
- This is a DSpark-assisted serving checkpoint, not a standalone target-model checkpoint[^nemotron-dspark].
- Intended deployment is lower-latency speculative decoding on DGX Spark and data-centre GPUs for workflows that benefit from speculative decoding[^nemotron-dspark].
- Nemotron-3.5-Lightning-30B-A3B supports native MTP, DFlash, and DSpark paths for DGX Spark and low-concurrency data-centre workflows; this release is the DSpark path[^nemotron-dspark].
- DSpark is designed to improve accepted length while preserving the latency benefits of block drafting on compact Blackwell systems such as DGX Spark[^nemotron-dspark].
- Release: Hugging Face 08/11/2026; deployment geography Global; ready for commercial or non-commercial use under OpenMDW-1.1[^nemotron-dspark].

## Architecture

- Draft architecture type: Dense GQA with Dense FFN MLP plus GQA attention layers; DSpark speculative-decoding attention uses causal grouped-query attention with a sliding window of size 1024 on all layers, plus per-head attention sink bias[^nemotron-dspark].
- Draft size: 967M total parameters, of which 615M are non-embedding parameters[^nemotron-dspark].
- The target family is described as a hybrid LatentMoE model for reasoning, chat, and agentic workflows[^nemotron-dspark].
- Input: text strings as 1D sequences; maximum context up to 1M tokens; supported languages English, Spanish, French, German, Italian, and Japanese[^nemotron-dspark].
- Output: text strings as 1D sequences, including natural-language responses, reasoning traces, tool-use content, and structured outputs depending on chat-template configuration and application tooling[^nemotron-dspark].
- Models are designed for NVIDIA GPU-accelerated systems with CUDA for faster training and inference versus CPU-only solutions[^nemotron-dspark].

## Training

- Quantized/exported with Model Optimizer 0.45.0; base-model references are `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` and `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-NVFP4`[^nemotron-dspark].
- Trained only on prompts from `nvidia/Nemotron-Post-Training-Dataset-v2` and the `nvidia/nemotron-post-training-v3` collection; original GPT responses were not used, and prompts were used for data synthesis to train the DSpark modules[^nemotron-dspark].
- Post-training corpus is synthetic data for reasoning, code, science, tool use, instruction following, structured outputs, and multilingual tasks; text training size 66B tokens repeated for 2 epochs[^nemotron-dspark].
- Collection method by dataset: hybrid automated, manually-collected, and synthetic; labeling method by dataset: hybrid automated, manually-labelled, and synthetic[^nemotron-dspark].

## Evaluation

Evaluated on SPEED-Bench for speculative decoding by measuring acceptance rates over responses across coding, math, writing, translation, and related tasks[^nemotron-dspark]. Reported acceptance length with draft length 7, baseline `NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`, `temperature=1.0`, `top_p=0.95`[^nemotron-dspark]:

| Category | SPEED-Bench Acceptance Length |
| --- | ---: |
| coding | 4.38 |
| humanities | 3.18 |
| math | 4.17 |
| multilingual | 4.55 |
| qa | 3.36 |
| rag | 4.25 |
| reasoning | 3.90 |
| roleplay | 3.06 |
| stem | 3.40 |
| summarization | 4.15 |
| writing | 2.83 |
| Overall Average | 3.75 |

All cells above are source-reported[^nemotron-dspark].

## Serving

- Supported runtime engine: vLLM; inference acceleration engines listed as vLLM and llama.cpp; preferred OS Linux[^nemotron-dspark].
- Supported hardware compatibility: NVIDIA Blackwell including DGX Spark (GB10), plus NVIDIA Hopper; tested hardware includes Hopper H100, Blackwell GB200, Blackwell GeForce RTX 5090, and DGX Spark (GB10)[^nemotron-dspark].
- Serve with vLLM via the DSpark recipes in the Nemotron-3.5-Lightning-30B-A3B NVFP4 model card, including the 1x DGX Spark GB10 section[^nemotron-dspark].
- The source frames integration as requiring use-case-specific testing under V-model unit and system validation for safety, technical, functional, and ethical requirements before deployment[^nemotron-dspark].

## Trust and limitations

- Speculative decoding is lossless acceleration: it does not affect the output distribution of the underlying reasoning model[^nemotron-dspark].
- Base-model limits carry over: possibly inaccurate, incomplete, or undesirable responses even on benign prompts, with biases or artifacts from training data and quality varying by domain, language, reasoning depth, and context length; developers should add application-specific safeguards and evaluate in the intended environment before production[^nemotron-dspark].
- Intended task/domain is text generation, reasoning, tool use, and agentic workflows accelerated with speculative decoding; performance metrics are accuracy, throughput, latency, and acceptance rate; quality standards reported as met[^nemotron-dspark].
- Bias subcard reports no participation considerations from adversely impacted groups, no mitigation measures, and no bias metric[^nemotron-dspark].
- Safety and security: applications are chat, instruction following, RAG, reasoning, and agentic AI; no life-critical application; use must comply with OpenMDW-1.1 and applicable laws; least-privilege access and dataset license constraints were applied[^nemotron-dspark].
- Privacy: no generatable or reverse-engineerable personal data; no personal data used to create the model; no user-interaction data used for training; dataset reviewed before release; provenance exists for all training datasets; labeling complies with privacy laws[^nemotron-dspark].

## Relationships

- Related to [Nemotron 3.5 Lightning DFlash Speculator](nemotron-3.5-lightning-dflash.md) — same Nemotron-3.5-Lightning-30B-A3B target family and SPEED-Bench draft-length-7 protocol; DSpark reports 3.75 overall acceptance versus 3.16 for DFlash.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — same confidence-scheduled block-drafting DSpark family; this checkpoint targets vLLM plus DGX Spark serving while that page documents the SGLang variable-verify mechanism and Kimi/Qwen checkpoint evidence.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — low-concurrency, small-batch fit and lossless-verify framing behind the latency use case above.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — vLLM separate-draft-model configuration surface used to pair this checkpoint with its target.
- Related to [vLLM on DGX Spark](vllm-dgx-spark.md) — DGX Spark GB10 local-serving context for the 1x GB10 recipe named in the source.

## Coverage limits

- No local attachments were referenced by the source; Hugging Face checkpoints, the NVFP4/BF16 target model cards, Nemotron post-training collections, SPEED-Bench harness, Model Optimizer export, and the DSpark paper (`2607.05147`) were not inspected beyond the source description[^nemotron-dspark].
- Acceptance lengths and hardware/runtime claims are source-reported under the stated draft-length-7 and sampling protocol; latency, throughput, and speedup numbers beyond acceptance length are not given in the source and are not compiled here[^nemotron-dspark].
- The source's Explainability subcard retains DFlash wording (`used with a DFlash draft checkpoint` and `while DFlash proposes candidate token blocks`) where the release body consistently describes DSpark; the DSpark characterization above follows the release body and this wording mismatch is preserved here rather than resolved[^nemotron-dspark].
- vLLM recipes, GB10/GB200/H100/RTX 5090 choices, and 1M-token context are workload-specific values from the source, not universal defaults[^nemotron-dspark].

[^nemotron-dspark]: NVIDIA Nemotron-3.5-Lightning-30B-A3B-NVFP4-DSpark — `../raw/DSpark.md`.
