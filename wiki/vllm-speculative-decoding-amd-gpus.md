---
type: Concept
title: vLLM Speculative Decoding on AMD GPUs
description: Five-method vLLM draft-and-verify comparison on MI300X/MI355X with throughput, acceptance, tuning, and speculator-training guidance.
tags: [vllm, speculative-decoding, amd, mtp, eagle, dflash, dspark]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T16:00:00Z }
sources:
  - id: amd-spec
    resource: ../raw/2026-08-23-speculative-decoding-amd-gpus/index.md
    title: Exploring Speculative Decoding in vLLM on AMD GPUs
---

vLLM speculative decoding keeps the target model responsible for final output and adds a faster draft stage that proposes candidates for single-pass verification; on AMD MI300X/MI355X with ROCm, the tested Native MTP, Gemma 4 MTP, EAGLE-3, DFlash, and DSpark paths varied with model family, draft checkpoint, workload, proposal length, and acceptance, so proposal length must be tuned per workload rather than fixed[^amd-spec].

## Draft-and-verify mechanics

Standard autoregressive decoding commits one token per target decode step, so long generations are dominated by sequential steps[^amd-spec]. Speculative decoding separates proposal from verification: the draft proposes `T1..Tk`, the target verifies left to right, accepted prefix tokens are committed, the first rejection is replaced by the target's token, and later candidates are discarded[^amd-spec].

Worked example from the source: context `The weather today is`, draft `sunny and warm outside`; `sunny` and `and` verify accept, `warm` is rejected in favor of target token `clear`, `outside` is discarded, and decoding continues from `The weather today is sunny and clear`[^amd-spec].

## Five drafting methods

All five use one target verification pass with left-to-right acceptance until the first rejection; they differ in draft architecture, target information used, and sequential versus parallel generation[^amd-spec].

| Method | Draft component | Target information used | Generation |
| --- | --- | --- | --- |
| Native MTP | Model-native auxiliary MTP path | Target-model or previous-MTP hidden state plus current/latest-token embedding, fused then projected to draft logits | Sequential reuse of the MTP path |
| Gemma 4 MTP | Separate paired assistant checkpoint | Target activations plus shared target KV cache | Sequential through the paired component |
| EAGLE-3 | Dedicated autoregressive draft network | Early, middle, and late target hidden states concatenated and projected, plus sampled-token embedding | Sequential with feedback from prior drafted tokens |
| DFlash | Dedicated parallel draft network | Fused target hidden states as extra Key/Value in every draft layer | Whole masked block predicted together in one pass |
| DSpark | DFlash-style parallel backbone plus lightweight Markov head | Same target-conditioned K/V as DFlash | One parallel pass plus left-to-right logit-bias correction |

Native MTP physical layer count and `num_speculative_tokens` are separate: vLLM can reuse the MTP path with extra forward passes when N exceeds checkpoint depth, adding sequential drafting work[^amd-spec]. Gemma 4 MTP reuses target context instead of re-encoding the accepted prefix, but still drafts sequentially[^amd-spec]. EAGLE-3 fuses three target-layer states once at the input, then continues from prior draft outputs because later speculative positions have no target hidden states yet[^amd-spec]. DFlash starts each block from a confirmed anchor token with remaining positions masked, predicts them together, and therefore has no token-by-token feedback within a pass; later-position quality depends on checkpoint and workload[^amd-spec]. DSpark keeps that parallel backbone for base logits and hidden states, then applies a Markov bias from token `k-1` to position `k` during left-to-right selection, avoiding a full draft-network rerun per position; its confidence-head prefix selection was not active in the tested vLLM path, so results reflect backbone plus Markov correction only[^amd-spec].

## Enabling in vLLM

All paths configure through `--speculative-config`; vLLM supports `mtp`, `eagle3`, `dflash`, and `dspark` method values in the tested build[^amd-spec].

| Method | Separate checkpoint | Typical config |
| --- | --- | --- |
| Native MTP | No | `{"method":"mtp","num_speculative_tokens":N}` |
| Gemma 4 MTP | Yes, matching assistant | `{"method":"mtp","model":"<assistant>","num_speculative_tokens":N}` |
| EAGLE-3 | Yes, matching speculator | `{"method":"eagle3","model":"<speculator>","num_speculative_tokens":N}` |
| DFlash | Yes, matching speculator | `{"method":"dflash","model":"<speculator>","num_speculative_tokens":N}` |
| DSpark | Yes, matching speculator | `{"method":"dspark","model":"<speculator>","num_speculative_tokens":N}` |

```bash
vllm serve <target-model> \
  --speculative-config '{"method":"mtp","num_speculative_tokens":<N>}'
```

```bash
vllm serve <target-model> \
  --speculative-config '{"method":"<method>","model":"<matching-draft-checkpoint>","num_speculative_tokens":<N>}'
```

Check installed vLLM support for the method plus architecture, checkpoint-to-target compatibility, N compatibility with the checkpoint, and model-card hardware/backend support before enabling[^amd-spec]. Native MTP needs no separate weights and may share embedding/output components, keeping extra memory modest; Gemma 4 MTP, EAGLE-3, DFlash, and DSpark load extra draft weights plus runtime buffers sized by draft size, precision, tensor parallelism, and buffers[^amd-spec].

## Pretrained draft publishers

| Publisher | Methods | Targets named |
| --- | --- | --- |
| Google | Gemma 4 MTP | Assistants for Gemma 4 E2B, E4B, 12B, 26B-A4B, 31B |
| LightSeek Foundation | EAGLE-3, EAGLE-3.1 | Kimi-K2.5, K2.6, K2.7-Coder incl. MLA variants |
| Red Hat AI | EAGLE-3, DFlash, DSpark | Llama, Qwen, Gemma, GPT-OSS, GLM, Nemotron, Mistral; `-speculator.eagle3/.dflash/.dspark` suffixes |
| Z-Lab | DFlash | Qwen3/3.5/3.6, Gemma 4, Kimi, MiniMax, GPT-OSS, Llama; `<target>-DFlash` pattern |
| DeepSeek AI DeepSpec | EAGLE-3, DFlash, DSpark | Qwen3-4B/8B/14B and Gemma 4 12B; e.g. `eagle3_qwen3_8b_ttt7`, `dflash_qwen3_8b_block7`, `dspark_qwen3_8b_block7` |
| Inferact | EAGLE-3, DSpark | MiniMax-M3-EAGLE3 plus GQA variants, Kimi-K3-DSpark |

All publisher rows and naming patterns are source-reported[^amd-spec].

## AMD measurements

Task-grounded GSM8K, MATH500, HumanEval, and MBPP prompts were used because acceptance depends on real output structure; headline signals are output-token throughput and speedup over the autoregressive baseline, mean accepted length, acceptance rates, and quality relative to baseline[^amd-spec].

Coverage tested (check = benchmarked)[^amd-spec]:

| Target | Native MTP | Gemma 4 MTP | EAGLE-3 | DFlash | DSpark |
| --- | --- | --- | --- | --- | --- |
| gemma-4-26B-A4B-it | — | ✓ Google | ✓ Red Hat AI | ✓ Z-Lab | — |
| gemma-4-31B-it | — | ✓ Google | ✓ Red Hat AI | ✓ Z-Lab | ✓ Red Hat AI |
| Qwen3-8B | — | — | ✓ Red Hat AI | ✓ Z-Lab | ✓ DeepSeek |
| Qwen3.5-27B | ✓ built-in | — | — | ✓ Z-Lab | — |
| Qwen3.5-122B-A10B | ✓ built-in | — | — | ✓ Z-Lab | — |
| Qwen3.6-27B | ✓ built-in | — | — | ✓ Z-Lab | — |
| Qwen3.6-35B-A3B | ✓ built-in | — | — | ✓ Z-Lab | — |
| Kimi-K2.5 | — | — | ✓ LightSeek | ✓ Z-Lab | — |
| MiniMax-M3-MXFP8 | — | — | ✓ Inferact | — | — |

Largest measured throughput ratios within the tested sweeps, all source-reported and config-specific[^amd-spec]:

- gemma-4-26B-A4B-it: Gemma 4 MTP 2.74x GSM8K and 2.62x MBPP; DFlash 2.87x MATH500 and 2.79x HumanEval; EAGLE-3 2.11–2.27x across the four suites.
- gemma-4-31B-it: Gemma 4 MTP 2.00x GSM8K and 1.99x MBPP; DFlash 2.34x MATH500 and 2.05x HumanEval; EAGLE-3 and DSpark above baseline.
- Qwen3-8B: DSpark 1.15x MATH500 to 1.63x GSM8K; DFlash 1.08–1.27x; EAGLE-3 above baseline on GSM8K/HumanEval/MBPP but its best MATH500 point stayed below baseline.
- Qwen3.5-27B, Qwen3.5-122B-A10B, Qwen3.6-27B: best native-MTP point beat best DFlash point in each comparison; group maximum 2.20x for Qwen3.5-122B-A10B on MATH500; best native-MTP N ranged 4–7 by model and dataset.
- Qwen3.6-35B-A3B: DFlash 1.77–2.06x with best at N=7 on all four suites; native MTP 1.28–1.49x with best at N=6; differs from Qwen3.6-27B, showing intra-family variance.
- MiniMax-M3-MXFP8: EAGLE-3 2.09x on HumanEval at N=4. Kimi-K2.5: EAGLE-3 up to 2.33x, DFlash up to 2.68x; best EAGLE-3 generally at N=4, best DFlash at N=7.
- General shape: best N was not constant; sequential methods often rose over the first few N then plateaued, while DFlash/DSpark N=7 was frequently among the best and larger N did not consistently help.

Per-position acceptance falls along the proposal: early positions accept at high rates and later positions contribute progressively less, so longer proposals raise mean accepted length while overall acceptance rate declines[^amd-spec]. Throughput and acceptance can diverge: cheap drafting can win on throughput with lower acceptance, while high acceptance with expensive drafting need not win[^amd-spec].

Hardware and software behind all ratios: 8x MI300X plus 2x EPYC 9654, except MiniMax-M3-MXFP8 on 8x MI355X plus 2x EPYC 9575F; Ubuntu 22.04.5, ROCm/HIP 7.2.53211, vLLM 0.23.1rc1.dev1120+g0f0f28b53, PyTorch 2.11.0+gitd0c8b1f, Transformers 5.13.1, Python 3.12.13; results may vary with configuration, drivers, and vLLM version[^amd-spec].

## Tuning

Treat proposal length as a runtime optimum over accepted tokens versus draft-plus-verify cost, seeded by the checkpoint recommendation and fixed by representative end-to-end measurement[^amd-spec].

- Native MTP: start N=1 for least extra sequential work, then sweep 2–7. Tested best N varied: Qwen3.5-27B best at N=5 GSM8K/MATH500, N=4 HumanEval/MBPP, N=3 MT-Bench; Qwen3.5-122B-A10B best at N=7 on the four reasoning/code suites; Qwen3.6-27B best at N=4–5 while Qwen3.6-35B-A3B rose through N=6[^amd-spec].
- Gemma 4 MTP and EAGLE-3: short sweep even with a recommended N; tested throughput generally rose over the first few N then plateaued[^amd-spec].
- DFlash: start from checkpoint block size; with `block_size=16` the supported maximum is `num_speculative_tokens=15` because position 0 is the anchor and 15 are candidates, but the maximum is not necessarily the fastest — test e.g. N=3,7,11,15. N=7 was frequently among the fastest with some workload maxima at N=11[^amd-spec].
- DSpark: compare configured proposal sizes such as N=3 versus N=7 on end-to-end throughput; the tested vLLM path submitted the full proposal for verification[^amd-spec].

Monitor throughput versus baseline, mean accepted length, overall acceptance rate, and per-position acceptance; use per-position decay to decide whether trimming N removes mostly wasted draft work[^amd-spec]. GSM8K/MATH500 often favored medium or deeper N within the sweeps while HumanEval/MBPP often peaked at moderate N, consistent with predictable local code structure but divergent identifiers and formatting[^amd-spec].

Workflow: start from a supported checkpoint config, benchmark representative prompts and generation settings, record throughput plus accepted length and acceptance, sweep smaller and larger N, and select on the workload's primary metric — here end-to-end serving throughput, which need not coincide with longest proposal, highest acceptance, or largest accepted length[^amd-spec].

## Training a speculator

Typical workflow: prepare representative prompts, generate responses with the exact target model, choose a hidden-state mode, collect required target hidden states, train, then test acceptance and serving throughput[^amd-spec].

Use prompts matching the expected workload and hold out an evaluation set; responses must come from the exact deployment target with matching tokenizer, chat template, thinking mode, and generation config, since re-templating existing responses does not make data target-specific[^amd-spec]. Hidden-state sourcing modes[^amd-spec]:

| Mode | Behavior | Trade-off |
| --- | --- | --- |
| Online | vLLM server generates hidden states on demand, then discards | No large disk cache but needs inference plus training resources together |
| Offline | Hidden states generated and stored before training | Frees GPUs for training after, but needs substantial storage |
| Hybrid | Generated and cached during first epoch, reused after | Pays generation once without a separate preprocessing stage |

Custom target-layer choices must match between extraction and training configs; method-specific hidden size, vocabulary, tokenizer, draft depth, block size, sequence length, and learning rate must also match[^amd-spec]. Judge the checkpoint by accepted length, acceptance rate, draft latency, GPU memory, and end-to-end throughput, not training loss alone; on weak workload acceptance, adjust prompt mixture or training config and repeat[^amd-spec].

Future directions named are non-learned n-gram and suffix decoding for repetitive code/agentic loops, broader concurrency plus prompt/output-length plus batch plus sampling sweeps, training-data mixture effects across code/math/chat/multilingual/tool/structured tasks, and deeper draft/verify/KV-cache/graph/scheduling profiling[^amd-spec].

## Relationships

- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — native-MTP `method: mtp` reference; this concept adds Gemma 4 assistant wiring and AMD N-sweep evidence.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE/Eagle3 draft-target reference; this concept adds EAGLE-3 fusion detail plus LightSeek, Red Hat AI, and Inferact checkpoint evidence.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — workload-fit and acceptance-band tuning; this concept adds AMD per-method N optima and per-position decay evidence.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — generic separate-draft verification framing behind the non-MTP rows.
- Related to [vLLM Speculators Library](vllm-speculators.md) — training and packaging path for the train-a-speculator workflow above.
- Related to [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md) — request-level acceptance measurement behind the monitor-acceptance guidance.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — SGLang block-diffusion plus KV-injection counterpart to the vLLM DFlash path here.
- Related to [SGLang DSpark Speculative Decoding](sglang-dspark-speculative-decoding.md) — SGLang confidence-scheduled DSpark counterpart; the vLLM path tested here lacked active confidence prefix selection.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — speculative-method selection table this AMD evidence can ground per target family.

## Coverage limits

- The three local SVGs were inspected as text and match the prose: draft-to-verify-to-commit flow, sunny/and/clear accept-reject-discard example, and the five-method structure/generation-pattern summary[^amd-spec].
- The appendix per-position heatmaps were sampled, not compiled row by row: exact per-N speedup, tok/s, MAL, AR, and per-position percentages for every target/method/workload live in the raw source; only headline maxima, best-N patterns, and the decay shape are synthesized above[^amd-spec].
- Per-model `vllm serve` commands in the raw appendix were sampled for flag shapes (tensor parallel, reasoning/tool parsers, attention backends, ROCm env vars such as `VLLM_ROCM_USE_AITER`); full commands are not reproduced here[^amd-spec].
- Hugging Face publisher collections, the EAGLE-3/DFlash/DSpark papers and repos, Gemma 4 MTP blog, vLLM Speculators/DeepSpec docs, and the method-summary table's underlying checkpoints beyond the names above were not inspected beyond the source's description[^amd-spec].

[^amd-spec]: AMD and Embedded LLM, Exploring Speculative Decoding in vLLM on AMD GPUs — `../raw/2026-08-23-speculative-decoding-amd-gpus/index.md` (vLLM blog, 2026-08-23), covering autoregressive baseline and draft-and-verify mechanics, five-method architectures and target conditioning, `--speculative-config` enablement and memory notes, draft-publisher catalog, MI300X/MI355X throughput plus MAL/AR and per-position acceptance appendix, proposal-length tuning workflow, speculator-training modes, and hardware/software disclaimer.
