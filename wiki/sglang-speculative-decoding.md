---
type: Concept
title: SGLang Speculative Decoding
description: EAGLE-2/EAGLE-3 speculative decoding with draft-model tuning, torch.compile, FR-Spec, and MTP usage.
tags: [sglang, speculative-decoding, eagle, mtp]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T16:00:00Z }
sources:
  - id: sgl-spec-decode
    resource: ../raw/sglang/advanced_features/speculative_decoding.mdx
    title: Speculative Decoding
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

## How EAGLE drafting works

The draft model predicts the next feature vector — the target LLM's last hidden state — from the feature sequence and token sequence, samples the next token through `LMHead`, then extends both sequences in tree form with per-step branching controlled by `speculative_eagle_topk`[^sgl-spec-decode]. EAGLE-2 scores branch probabilities, prunes unlikely branches dynamically, and reranks down to the top `speculative_num_draft_tokens` final nodes[^sgl-spec-decode]. EAGLE-3 drops the feature-prediction objective, uses low- and mid-layer features, and trains on-policy; operating on features plus next-timestep tokens reduces sampling randomness, while dynamic tree adjustment plus reranking raises acceptance rate[^sgl-spec-decode].

## Relationships

- Uses [SGLang Advanced Features Overview](sglang-advanced-features-overview.md) — listed Speculative Decoding entry compiled here.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — joint tuning of `--cuda-graph-max-bs`, `--max-running-requests`, and memory fraction alongside speculation parameters.
- Uses [SGLang Server Arguments](sglang-server-arguments.md) — canonical launch and configuration reference for the speculation and memory flags used here.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — vLLM's `eagle`/`eagle3` counterpart with independent draft tensor parallelism and Hub speculator collections.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — vLLM's native-MTP `method: mtp` path versus SGLang's MTP-via-EAGLE-parameters usage.

## Coverage limits

- The referenced DeepSeek MTP usage page (`../basic_usage/deepseek_v3`) was not present under `raw/` and was not inspected; DeepSeek-specific MTP detail is not compiled here[^sgl-spec-decode].
- The linked `bench_speculative.py` playground script, EAGLE/EAGLE-3/FR-Spec papers, Hugging Face draft-model and token-map IDs, and EAGLE training repository were not inspected beyond the source's description; exact benchmark setup and training steps beyond the summary above are not compiled here[^sgl-spec-decode].
- Example launch commands use small `--cuda-graph-max-bs`, reduced `--mem-fraction`, and `float16` values chosen for documentation startup speed; they are starting points, not workload-optimal defaults[^sgl-spec-decode].

[^sgl-spec-decode]: Speculative Decoding — `../raw/sglang/advanced_features/speculative_decoding.mdx`.
