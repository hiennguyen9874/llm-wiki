---
type: Concept
title: Nemotron 3.5 Lightning Base Model
description: BF16 reference weights for Nemotron-3.5-Lightning-30B-A3B with 30B/3B-active hybrid Mamba-MoE-attention, 1M context, MTP, and vLLM deployment recipes.
tags: [nemotron, moe, mamba, speculative-decoding, vllm]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T23:30:00Z }
sources:
  - id: nemotron-35-readme
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md
    title: NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16
  - id: nemotron-35-config
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json
    title: NemotronH config for Nemotron-3.5-Lightning-30B-A3B
---

NVIDIA `nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16` is the full-precision BF16 reference release of Nemotron 3.5 Lightning, intended primarily as a customization starting point for post-training, domain adaptation, distillation, and producing quantized variants rather than direct latency-optimized production inference[^nemotron-35-readme].

## Model identity and intended use

- Total parameters 30B with 3B active; architecture described as MoE hybrid with interleaved Mamba-2, MoE, and select attention layers[^nemotron-35-readme].
- Precision BF16; context up to 1M tokens, with 256K used for single-H100 deployment; single-GPU deployment on 1x H100 80GB or 1x A100 80GB[^nemotron-35-readme].
- Supported hardware includes Blackwell GB200 and GeForce RTX 5090, Hopper H100 and H200, and Ampere A100; preferred runtime PyTorch on Linux[^nemotron-35-readme].
- Supported languages are English plus coding languages as primary, with Spanish, French, German, Italian, and Japanese also supported; post-training adds Chinese in multilingual reasoning and translation tasks[^nemotron-35-readme].
- Recommended sampling is Temperature 1.0 and Top_P 0.95; reasoning is configurable through the chat template with `enable_thinking=True/False`[^nemotron-35-readme].
- Developer NVIDIA Corporation; model dates December 2025 to May 2026; pre-training cutoff September 2025 and post-training cutoff May 2026; GA release 08/11/2026 under OpenMDW-1.1[^nemotron-35-readme].
- For optimized deployment NVIDIA points to the NVFP4 release, including W4A16, TensorRT-LLM, SGLang, and DGX Spark recipes[^nemotron-35-readme].

## Architecture

- Architecture type `NemotronHForCausalLM` of model type `nemotron_h`; network described as Nemotron-3-Lightning plus Multi-Token Prediction[^nemotron-35-readme][^nemotron-35-config].
- Depth 52 layers with explicit block types: 23 Mamba, 23 MoE, and 6 attention layers; MTP adds 1 layer with `attention` plus `moe` block types[^nemotron-35-config].
- Hidden size 2688; 32 query heads with 2 key-value heads and head dimension 128; vocabulary 131072; MLP uses `relu2` with intermediate size 1856[^nemotron-35-config].
- MoE uses 128 routed experts plus 1 shared expert, 6 experts per token, routing scale factor 2.5, top-k probability normalization, shared-expert intermediate size 3712 with overlap enabled[^nemotron-35-config].
- Mamba-2 uses 64 heads of dimension 64, SSM state size 128, convolution kernel 4, expansion factor 2, chunk size 128, SiLU activation, 8 evolution-matrix groups, convolution bias enabled, and no projection bias[^nemotron-35-config].
- Positional configuration includes RoPE theta 10000 and `max_position_embeddings` 262144 in the shipped config, corresponding to the documented 256K single-H100 setting; 1M serving is enabled through the long-context vLLM recipe below[^nemotron-35-readme][^nemotron-35-config].
- MTP layers predict multiple future tokens to provide richer training signals and are aligned to the base distribution in continued pre-training[^nemotron-35-readme].

## Speculative decoding options

- DSpark is a semi-autoregressive drafter that proposes a whole candidate-token block in one forward pass from a parallel backbone; it is the currently recommended path for DGX Spark and low-concurrency data-centre deployment[^nemotron-35-readme].
- DFlash is a lightweight block-diffusion drafter that generates an entire draft block in one forward pass[^nemotron-35-readme].
- MTP is a modeling technique that trains the network to predict several future tokens at each position instead of only the next token[^nemotron-35-readme].

## Training methodology

- Pre-trained on more than 20T tokens with an NVFP4 recipe using crawled plus synthetic code, math, science, and general-knowledge data; software cited for pre-training is Megatron-LM[^nemotron-35-readme].
- Stage 2 is continued pre-training for MTP so the MTP heads learn multi-future-token prediction aligned with the base model[^nemotron-35-readme].
- Stage 3 is supervised fine-tuning on synthetic code, math, science, tool calling, instruction following, structured outputs, and general knowledge, including long-range retrieval and multi-document aggregation data[^nemotron-35-readme].
- Stage 4 is multi-environment reinforcement learning with GRPO across math, code, science, instruction following, multi-step tool use, multi-turn conversation, and structured-output environments, using an asynchronous architecture that decouples training from inference and uses MTP to accelerate rollouts; software cited is NeMo RL and NeMo Gym[^nemotron-35-readme].
- Pre-training corpus covers English plus 19 spoken languages and 43 programming languages across webpages, dialogue, articles, legal, math, science, finance, QA, and alignment-style data; foundation datasets include Nemotron-CC v2/v2.1, CC-Code, Pretraining-Code, CC-Math, Specialized, and Legal collections, plus public datasets and NVIDIA English, multilingual, and GitHub crawls[^nemotron-35-readme].
- Post-training applies structural, repetition, and political/nationalistic-trajectory filtering, compiler and numerical verification, license-compliance filtering, and bias-audit mitigations such as balanced fine-tuning and counterfactual augmentation; the source discloses many synthetic pre- and post-training blends rather than one closed training set[^nemotron-35-readme].

## Evaluation

NVIDIA reports the following release evaluation suite under a consistent NeMo Gym / NeMo Evaluator harness; the source notes these numbers may differ from vendors' self-reported results[^nemotron-35-readme]:

| Task | Nemotron-3.5-Lightning-30B-A3B-BF16 | Qwen 3.6 35B A3B | Gemma 4 26B A4B | Nemotron 3 Nano | Nemotron 3 Super | GPT-OSS 20B |
| --- | --- | --- | --- | --- | --- | --- |
| MMLU Pro | 81.94 | 85.63 | 85.20 | 78.46 | 83.89 | 76.40 |
| AA-Omniscience | 17.50 | 19.47 | 22.17 | 20.15 | 26.68 | 16.62 |
| GPQA Diamond, no tools | 75.44 | 83.40 | 79.61 | 74.05 | 78.60 | 71.46 |
| HLE text-only, no tools | 11.72 | 19.56 | 17.42 | 10.89 | 20.30 | 13.76 |
| SciCode | 32.60 | 35.33 | 40.28 | 30.08 | 35.11 | 38.63 |
| SWE-bench Verified | 51.56 | 70.12 | 57.40 | 34.08 | 63.08 | 52.44 |
| SWE-bench Multilingual | 39.33 | 63.40 | 43.40 | 14.07 | 49.80 | 41.93 |
| Terminal-Bench 2.1 | 24.58 | 44.38 | 37.22 | 8.29 | 39.61 | 15.17 |
| PinchBench | 85.37 | 88.07 | 74.70 | 66.11 | 80.36 | 57.20 |
| BrowseComp | 36.97 | 48.74 | 26.30 | 13.74 | 22.77 | – |
| τ³-bench Banking | 9.28 | 10.52 | 14.02 | 7.01 | 12.37 | – |
| GDPval-AA-V2 | 832 | 1015 | 807 | 473 | 746 | – |
| IFBench loose | 71.88 | 63.71 | 77.25 | 72.17 | 71.92 | 68.50 |
| AA-LCR | 52.00 | 61.06 | 57.56 | 32.75 | 58.44 | 32.88 |

All cells above are source-reported[^nemotron-35-readme].

Reproducibility recipes, containers, prompts, parser configurations, and scoring settings are published in NeMo Gym; most evaluations use NeMo Gym-native harnesses while SWE-Bench and Terminal-Bench used NeMo Evaluator natively[^nemotron-35-readme].

## Serving

- vLLM Nightly `vllm/vllm-openai:v0.27.1` is the documented BF16 path; TensorRT-LLM, SGLang, W4A16, and DGX Spark details are delegated to the NVFP4 card[^nemotron-35-readme].
- 1x H100 maximum-throughput recipe uses up to 128 sequences, prefix caching, async scheduling, FlashInfer Mamba backend, FP16 Mamba SSM cache with stochastic rounding, plus `nemotron_v3` reasoning and `qwen3_coder` tool-call parsing with automatic tool choice[^nemotron-35-readme].
- 8x H100 long-context recipe uses tensor parallelism 8 with expert parallelism, FlashInfer and CUTLASS MoE backend, aligned Mamba cache mode, prefix caching, and `--max-model-len 1048576` with `VLLM_ALLOW_LONG_MAX_MODEL_LEN=1`[^nemotron-35-readme].
- 1x GB200 recipe uses 128 sequences, 1M maximum model length, larger batched-token budget, no prefix caching, async scheduling, DSpark speculation with 5 speculative tokens, FlashInfer Mamba backend, and the same reasoning and tool-call parsers[^nemotron-35-readme].
- Memory-constrained deployments should lower `--max-model-len` and drop the long-length override to gain KV-cache headroom[^nemotron-35-readme].
- The OpenAI-compatible client uses `temperature=1.0`, `top_p=0.95`, and up to 16000 max tokens; reasoning defaults on, supports explicit off, and supports streaming[^nemotron-35-readme].
- vLLM tool calling requires automatic tool choice plus the Qwen3-Coder and Nemotron-v3 parsers; coding agents should also set `force_nonempty_content=True` in chat-template kwargs[^nemotron-35-readme].
- Tested inference hardware includes 1–8x H100/H200, GB200, and RTX 5090; inputs and outputs are 1D text sequences[^nemotron-35-readme].

## Trust and limitations

- The model is described as ready for commercial use under OpenMDW-1.1, but integration still requires use-case-specific unit and system validation under a V-model before deployment[^nemotron-35-readme].
- Base-model limits carry over to speculative deployments: possibly inaccurate, incomplete, or undesirable responses, training-data biases and artifacts, and quality variation by domain, language, reasoning depth, and context length[^nemotron-35-readme].
- NVIDIA frames Trustworthy AI as shared responsibility, advises against circumventing safety guardrails without a substantially similar replacement, and points to separate Safety, Explainability, Bias, and Privacy subcards[^nemotron-35-readme].

## Relationships

- Uses [Nemotron 3.5 Lightning DFlash Speculator](nemotron-3.5-lightning-dflash.md) — lightweight block-diffusion draft path for low-concurrency vLLM and llama.cpp serving of this base model.
- Uses [Nemotron 3.5 Lightning DSpark Speculator](nemotron-3.5-lightning-dspark.md) — recommended semi-autoregressive draft path for DGX Spark and low-concurrency data-centre serving of this base model.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — separate-draft-model configuration surface used to pair this target with DSpark.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native MTP speculation path supported alongside the external DSpark and DFlash drafters.
- Related to [vLLM on DGX Spark](vllm-dgx-spark.md) — DGX Spark GB10 local-serving context for the DSpark recipe.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — SGLang block-diffusion mechanism distinct from this vLLM/llama.cpp DFlash checkpoint path.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — SGLang confidence-driven verification mechanism distinct from this vLLM DSpark checkpoint path.

## Coverage limits

- Local `DFlash.md` and `DSpark.md` copies in this source folder are identical to the already-ingested `../raw/DFlash.md` and `../raw/DSpark.md`; no separate claims are compiled from those duplicates.
- Referenced `accuracy_plot.png`, `agentic_coding_benchmarks.png`, `safety.md`, `explainability.md`, `bias.md`, and `privacy.md` were absent from the local source folder and were not inspected[^nemotron-35-readme].
- Hugging Face BF16/NVFP4 target cards, post-training collections, SPEED-Bench harness, Model Optimizer export, NeMo Gym reproducibility recipes, cited papers, and external dataset links were not inspected beyond the README description[^nemotron-35-readme].
- Benchmark figures are source-reported NVIDIA-harness results and do not establish production latency, throughput, or speedup[^nemotron-35-readme].
- The Python implementation files were skimmed only to confirm the Nemotron-H configuration semantics; the compiled architecture values above follow `config.json` and the README[^nemotron-35-config][^nemotron-35-readme].

[^nemotron-35-readme]: NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16 — `../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/README.md`.
[^nemotron-35-config]: NemotronH config for Nemotron-3.5-Lightning-30B-A3B — `../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/config.json`.
