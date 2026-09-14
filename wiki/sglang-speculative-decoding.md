---
type: Concept
title: SGLang Speculative Decoding
description: EAGLE-2/EAGLE-3 speculative decoding with draft-model tuning, torch.compile, FR-Spec, and MTP usage.
tags: [sglang, speculative-decoding, eagle, mtp]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T23:30:00Z }
sources:
  - id: sgl-spec-decode
    resource: ../raw/sglang/advanced_features/speculative_decoding.mdx
    title: Speculative Decoding
  - id: dflash-v2
    resource: ../raw/2026-06-15-next-generation-speculative-decoding-dflash-v2/index.md
    title: "The next generation of speculative decoding: DFlash and Spec V2"
  - id: dspark-sglang
    resource: ../raw/2026-07-06-dspark-sglang/index.md
    title: "DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification"
  - id: glm52-opt
    resource: ../raw/2026-07-13-glm52-optimization/index.md
    title: "Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks"
  - id: qwen38-day0
    resource: ../raw/2026-08-12-qwen3-8-day0-support/index.md
    title: 'SGLang and Miles Add Day-0 Support for Qwen3.8'
  - id: qwen38-flash-next-day0
    resource: ../raw/2026-08-26-qwen-flash-next/index.md
    title: 'Qwen3.8-Flash-Next: Day-0 Support in SGLang'
---

SGLang provides EAGLE-based speculative decoding supporting EAGLE-2 and EAGLE-3, described as among the fastest open-source implementations[^sgl-spec-decode].

## Performance

For LLaMA-Instruct 3.1 8B on MT-Bench with 1x H100[^sgl-spec-decode]:

| Method | Throughput |
| --- | --- |
| SGLang without speculation | 158.34 tokens/s |
| SGLang + EAGLE-2 | 244.10 tokens/s |
| SGLang + EAGLE-3 | 373.25 tokens/s |

This is roughly a 2.4x improvement from baseline to EAGLE-3 on the reported setup[^sgl-spec-decode].

## Shared draft parameters

The same parameters apply to EAGLE-2 and EAGLE-3[^sgl-spec-decode]:

- `speculative_draft_model_path`: draft model path; required.
- `speculative_num_steps`: autoregressive drafting depth; default `5`. Larger values widen speculation range but risk rejection cascades.
- `speculative_eagle_topk`: branching factor per step; default `4`. Higher values improve candidate diversity and acceptance rate at higher memory/compute cost.
- `speculative_num_draft_tokens`: maximum parallel verification capacity; default `8`. Larger values allow deeper tree evaluation at higher GPU-memory cost.

Use `scripts/playground/bench_speculative.py` to search parameter combinations[^sgl-spec-decode].

## Joint tuning

Tune the draft parameters together with `--cuda-graph-max-bs`, `--max-running-requests`, and `--mem-fraction-static` for the target workload[^sgl-spec-decode]. Documentation examples use a small `--cuda-graph-max-bs` for faster engine startup; production workloads should retune it[^sgl-spec-decode].

## EAGLE-2

Enable with `--speculative-algorithm EAGLE` plus a matching draft model[^sgl-spec-decode]. Example target/draft pair from the source is `meta-llama/Llama-2-7b-chat-hf` with `lmsys/sglang-EAGLE-llama2-chat-7B` using `--speculative-num-steps 3 --speculative-eagle-topk 4 --speculative-num-draft-tokens 16 --cuda-graph-max-bs 8`[^sgl-spec-decode].

### EAGLE-2 with torch.compile

Add `--enable-torch-compile` with optional `--torch-compile-max-bs` for further optimization[^sgl-spec-decode]. The source example uses steps `5`, top-k `8`, draft tokens `64`, `--mem-fraction 0.6`, and `--torch-compile-max-bs 2`[^sgl-spec-decode].

### EAGLE-2 with FR-Spec

Frequency-Ranked Speculative Sampling uses a truncated high-frequency token vocabulary in the draft model to reduce `lm_head` compute without quality degradation[^sgl-spec-decode]. Enable with `--speculative-token-map`, for example `thunlp/LLaMA3-Instruct-8B-FR-Spec/freq_32768.pt`[^sgl-spec-decode]. The source example pairs `meta-llama/Meta-Llama-3-8B-Instruct` with `lmsys/sglang-EAGLE-LLaMA3-Instruct-8B` using steps `5`, top-k `8`, draft tokens `64`, `--mem-fraction 0.7`, `--cuda-graph-max-bs 2`, and `--dtype float16`[^sgl-spec-decode].

## EAGLE-3

Enable with `--speculative-algorithm EAGLE3` plus a matching draft model[^sgl-spec-decode]. The source example pairs `meta-llama/Llama-3.1-8B-Instruct` with `jamesliu1/sglang-EAGLE3-Llama-3.1-Instruct-8B` using steps `5`, top-k `8`, draft tokens `32`, `--mem-fraction 0.6`, `--cuda-graph-max-bs 2`, and `--dtype float16`[^sgl-spec-decode].

## Multi-token prediction

SGLang supports Multi-Token Prediction through speculative decoding[^sgl-spec-decode]. The source example runs `XiaomiMiMo/MiMo-7B-RL` with `--trust-remote-code --speculative-algorithm EAGLE --speculative-num-steps 1 --speculative-eagle-topk 1 --speculative-num-draft-tokens 2 --mem-fraction 0.5`[^sgl-spec-decode].

## DFlash and Spec V2

For parallel block-diffusion drafting with per-layer KV injection on the Spec V2 overlap engine, see [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md)[^dflash-v2]. DFlash generates a whole draft block in one forward pass and beats native MTP and EAGLE baselines on the reported Qwen3-4B and Qwen3.5-397B-A17B setups, including 875 tok/s (4.31x baseline, ~1.5x MTP) at concurrency 1 on HumanEval[^dflash-v2].

## DSpark confidence-driven verification

For semi-autoregressive block drafting with per-request confidence-trimmed verify, see [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md)[^dspark-sglang]. DSpark pairs a one-forward `gamma`-token block drafter plus confidence head and STS calibration with a per-step SPS-argmax scheduler selecting `static` / `compact` / `cap-accept` ragged verify windows under full CUDA graphs, beating MTP and non-spec across a 1–256 concurrency sweep on reported DeepSeek-V4-Flash H200 DP4 setups[^dspark-sglang].

## GLM-5.2 IndexShare MTP on Spec V2

For IndexShare MTP with top-k reuse across draft steps on the Spec V2 overlap engine, see [SGLang GLM-5.2 NVFP4 Optimization](sglang-glm52-optimization.md)[^glm52-opt]. GLM-5.2 ships a strong MTP head with accept lengths frequently hitting 5+; SGLang reuses the draft-step-0 DSA indexer top-k for later draft steps to cut draft-step cost by up to ~1.9x at long context, seeding it from the prior `run_batch` draft-extend through the overlap relay buffer[^glm52-opt]. The same work makes DSA draft-extend CUDA-graphable, drops D2H/H2D syncs, and fuses `_apply_cuda_graph_metadata` ops for an 11% end-to-end TPS gain with no bubble between `run_batch` iterations[^glm52-opt].

## Qwen3.8 ReplaySSM with MTP and DSpark

Qwen3.8 GDN layers need ReplaySSM raw-input replay for speculative state recovery: record recurrence inputs instead of snapshotting full state, then fold-replay the accepted prefix from the committed checkpoint, integrated into FlashInfer's CuTe DSL GDN MTP kernel with bitwise-identical verification and no measurable regression[^qwen38-day0]. On TP8 B300 NVFP4 batch-size-1, SGLang reports 346 tok/s with MTP at accept length 3.3 and 378 tok/s with DSpark at accept length 4.0 including the bonus token; on a matched dual-PP6 backbone MTP adds +10.0% throughput and 2.33x per-user speed[^qwen38-day0]. Full PP+MTP placement and Pareto context are maintained in [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md).

## Qwen3.8-Flash-Next IndexShare MTP for QSA

Qwen3.8-Flash-Next reuses the QSA indexer top-k across MTP draft steps instead of recomputing it: each MTP iteration opens with a draft-extend over target-accepted tokens that runs the indexer anyway, captures each request's last accepted row, and reuses it for the whole draft loop with `N+1` extra columns for in-flight drafted positions, cutting draft indexer work from `N` invocations to one with unchanged accept length[^qwen38-flash-next-day0]. At TP4 on B200, the NVFP4 checkpoint decodes at 540 tok/s batch-size-1 with MTP at accept length 3.3 including the bonus token[^qwen38-flash-next-day0]. Full QSA scoring, 512-block/2051-token selection, and PLE offload context are maintained in [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md).

## How EAGLE drafting works

The draft model predicts the next feature vector — the target LLM's last hidden state — from the feature sequence and token sequence, samples the next token through `LMHead`, then extends both sequences in tree form with per-step branching controlled by `speculative_eagle_topk`[^sgl-spec-decode]. EAGLE-2 scores branch probabilities, prunes unlikely branches dynamically, and reranks down to the top `speculative_num_draft_tokens` final nodes[^sgl-spec-decode]. EAGLE-3 drops the feature-prediction objective, uses low- and mid-layer features, and trains on-policy; operating on features plus next-timestep tokens reduces sampling randomness, while dynamic tree adjustment plus reranking raises acceptance rate[^sgl-spec-decode].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — listed Speculative Decoding entry compiled here.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — joint tuning of `--cuda-graph-max-bs`, `--max-running-requests`, and memory fraction alongside speculation parameters.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical launch and configuration reference for the speculation and memory flags used here.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — vLLM's `eagle`/`eagle3` counterpart with independent draft tensor parallelism and Hub speculator collections.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — vLLM's native-MTP `method: mtp` path versus SGLang's MTP-via-EAGLE-parameters usage.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — DeepSeek-V4 single-layer SWA-only MTP head with in-graph hybrid metadata preparation and doubled ShadowRadix ring sizes.
- Uses [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — parallel block-diffusion drafter with KV injection on Spec V2; beats MTP/EAGLE baselines on reported Qwen setups.
- Uses [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — semi-autoregressive block drafter with confidence-scheduled ragged verify; best throughput/latency trade-off across reported 1–256 concurrency sweep.
- Uses [SGLang GLM-5.2 NVFP4 Optimization](sglang-glm52-optimization.md) — IndexShare MTP with draft-step top-k reuse on Spec V2; zero-overhead DSA draft-extend and sync-removal path.
- Related to [SGLang Qwen3.8 Inference](sglang-qwen3.8-inference.md) — Qwen3.8 ReplaySSM GDN recovery with MTP 346 tok/s and DSpark 378 tok/s batch-1 rates plus matched-backbone MTP gain.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — QSA IndexShare MTP reusing draft-extend top-k across draft steps with 540 tok/s TP4 B200 batch-1 rate.

## Coverage limits

- The referenced DeepSeek MTP usage page (`../basic_usage/deepseek_v3`) was not present under `raw/` and was not inspected; DeepSeek-specific MTP detail is not compiled here[^sgl-spec-decode].
- The linked `bench_speculative.py` playground script, EAGLE/EAGLE-3/FR-Spec papers, Hugging Face draft-model and token-map IDs, and EAGLE training repository were not inspected beyond the source's description; exact benchmark setup and training steps beyond the summary above are not compiled here[^sgl-spec-decode].
- Example launch commands use small `--cuda-graph-max-bs`, reduced `--mem-fraction`, and `float16` values chosen for documentation startup speed; they are starting points, not workload-optimal defaults[^sgl-spec-decode].

[^sgl-spec-decode]: Speculative Decoding — `../raw/sglang/advanced_features/speculative_decoding.mdx`.
[^dflash-v2]: The next generation of speculative decoding: DFlash and Spec V2 — `../raw/2026-06-15-next-generation-speculative-decoding-dflash-v2/index.md`.
[^dspark-sglang]: DSpark in SGLang: Speculative Decoding with Confidence-Driven, Variable-Length Verification — `../raw/2026-07-06-dspark-sglang/index.md`.
[^glm52-opt]: Serving GLM5.2 NVFP4 Agentic Workload with SGLang: Reaching 500 TPS in 2 Weeks — `../raw/2026-07-13-glm52-optimization/index.md`.
[^qwen38-day0]: SGLang and Miles Add Day-0 Support for Qwen3.8 — `../raw/2026-08-12-qwen3-8-day0-support/index.md`, covering ReplaySSM GDN recovery with MTP/DSpark batch-1 rates and matched-backbone gain.
[^qwen38-flash-next-day0]: Qwen3.8-Flash-Next: Day-0 Support in SGLang — `../raw/2026-08-26-qwen-flash-next/index.md`, covering QSA IndexShare MTP reuse with 540 tok/s TP4 B200 batch-1 rate at accept length 3.3.
