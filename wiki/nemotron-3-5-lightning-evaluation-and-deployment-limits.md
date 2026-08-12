---
type: Concept
title: Nemotron 3.5 Lightning evaluation and deployment limits
description: Nemotron 3.5 Lightning reports broad reasoning and agentic results under NVIDIA’s harness, while model-card-only evidence, context metadata, data provenance, safety, and workload-dependent serving constrain deployment conclusions.
tags: [nemotron, evaluation, deployment, safety, data-governance, speculative-decoding]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T14:46:56Z }
sources:
  - id: nemotron-lightning-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md
    title: NVIDIA Nemotron 3.5 Lightning 30B A3B BF16 model card
  - id: nemotron-lightning-config
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json
    title: NVIDIA Nemotron 3.5 Lightning 30B A3B checkpoint configuration
---

# Nemotron 3.5 Lightning evaluation and deployment limits

NVIDIA’s model card reports broad knowledge, reasoning, coding, agentic, instruction-following, and long-context results for Nemotron 3.5 Lightning under a nominally consistent NeMo Gym/Evaluator harness. The 30B-total/3B-active model is positioned primarily as a BF16 customization checkpoint; NVIDIA recommends its separately quantized NVFP4 release for optimized deployment. The reported scores are useful release evidence, but they are author-run and do not establish independent quality, safety, or serving efficiency.[^nemotron-lightning-card]

## Reported evaluation

The card compares Lightning with Qwen 3.6 35B A3B, Gemma 4 26B A4B, two other Nemotron models, and GPT-OSS 20B. Lightning reports 81.94 on MMLU-Pro, 75.44 on GPQA Diamond without tools, 51.56 on SWE-bench Verified, 24.58 on Terminal-Bench 2.1, 71.88 on loose IFBench, and 52.00 on AA-LCR.[^nemotron-lightning-card]

Those results do not support a blanket frontier-quality claim. In the supplied table, Qwen 3.6 leads Lightning on most listed knowledge, reasoning, coding, and agentic tasks; Gemma leads some others. Lightning’s relative position is task-dependent—for example, it exceeds Qwen on loose IFBench but trails Gemma. NVIDIA states that the recipes specify prompts, containers, inference parameters, parsers, and scorers, but the linked external recipe repository was not part of this source bundle.[^nemotron-lightning-card]

## Serving envelope

The BF16 card gives three materially different vLLM profiles:[^nemotron-lightning-card]

- One H100 uses up to 128 sequences and FP16 Mamba cache for memory headroom; the summary limits this profile to 256K context.
- Eight H100s use tensor parallelism plus expert parallelism and request a 1,048,576-token maximum.
- One GB200 uses a DSpark draft with five speculative tokens and disables prefix caching in the supplied recipe.

These are recommended configurations, not measured latency or throughput results. The underlying config’s 262,144-position maximum also makes the advertised 1M context an externally asserted deployment capability rather than one fully explained by checkpoint metadata.[^nemotron-lightning-card][^nemotron-lightning-config]

Reasoning can be toggled in the chat template and the card recommends temperature 1.0/top-p 0.95. Such settings, parser choices, tool schemas, concurrency, context length, Mamba-cache precision, expert placement, and speculative strategy all affect observed behavior and cost; benchmark scores should not be detached from their harness.

## Data and governance limits

The card provides unusually extensive dataset tables, including Common Crawl, GitHub, public benchmarks, synthetic corpora, third-party private data, NVIDIA-private data, and purchased vendor data. However, many post-training dataset sizes, generators, or origins remain undisclosed, and remaining released code, math, and multilingual data require gating and approval. “Open weights, training data, and recipes” therefore does not mean every training example or governance detail is ungated and independently auditable.[^nemotron-lightning-card]

The card reports demographic under-representation and skew in sampled FinePDFs, EssentialWeb, HotpotQA, SQuAD, and HelpSteer3 data, recommends downstream bias audits, and warns that deployment requires use-case testing. It also says the model may inherit toxic language and social bias from web data. The README links separate safety, explainability, bias, and privacy subcards, but none were included in the supplied directory; their claims could not be reviewed.[^nemotron-lightning-card]

Use is governed by OpenMDW 1.1 rather than a standard permissive software license. The card calls the checkpoint commercially usable, but deployment must still follow that license and applicable law.[^nemotron-lightning-card]

## Relationships

- **Evaluates:** [Nemotron 3.5 Lightning architecture and training](nemotron-3-5-lightning-architecture-and-training.md).
- **Can use:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md), [DSpark parallel-draft speculative decoding](dspark-parallel-draft-speculative-decoding.md), or native MTP.
- **Qualified by:** [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md), because the card recommends strategies by hardware and concurrency without reporting end-to-end gains for these checkpoints.
- **Depends on:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) for expert-parallel memory and communication constraints.

## Evidence limits

All capability, data-processing, compatibility, and safety statements are NVIDIA-authored. No independent reproduction, weights-level test, or benchmark execution was performed. Missing local attachments limit coverage of visual comparisons and Model Card++ governance details. The model card’s benchmark table and prose were available and are the basis of this synthesis.[^nemotron-lightning-card]

[^nemotron-lightning-card]: NVIDIA, “NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md), Benchmarks, Quick Start Guide, training-data disclosures, and Ethical Considerations.

[^nemotron-lightning-config]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning checkpoint configuration,” [config](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json).
