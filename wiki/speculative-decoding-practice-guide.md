---
type: Concept
title: Speculative Decoding Workload Fit and Tuning
description: When speculative decoding helps, acceptance-rate and draft-token tuning, and vLLM deployment with reported cost evidence.
tags: [speculative-decoding, vllm, inference-tuning]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-16T12:00:00Z }
sources:
  - id: spec-practice
    resource: ../raw/how-speculative-decoding-delivers-faster-llm-inference/index.md
    title: How speculative decoding delivers faster LLM inference
  - id: eagle3-fly
    resource: ../raw/fly-eagle3-fly-faster-inference-vllm-speculative-decoding/index.md
    title: 'Fly Eagle(3) fly: Faster inference with vLLM & speculative decoding'
---

Speculative decoding pairs a small fast draft model with a large target model that verifies several draft tokens in one parallel forward pass, preserving target output while converting memory-bound sequential decoding into better-utilized parallel verification; it pays off on predictable low-concurrency workloads and fades under saturated batch or creative workloads without domain-aligned draft models[^spec-practice].

## How it works

Autoregressive inference emits one token per full target-model forward pass, so each step waits on the previous token even on high-end GPUs[^spec-practice].

The source frames the fix as hare plus tortoise[^spec-practice]:

- **Hare (speculator):** small fast model (0.5–2B parameters in the source examples) that drafts roughly three to five tokens speculatively; fast but occasionally wrong.
- **Tortoise (target):** production model (7B, 70B, or larger) that checks all draft tokens in a single parallel forward pass.

When the draft is right, several tokens cost one large-model pass; when wrong, the system keeps the prefix before the first mistake, the verifier emits the correct token, and generation continues, so a wrong guess costs roughly the same forward pass either way[^spec-practice]. The worked example is `for → i → in → range`: all four accepted when correct, versus `for → loop → in → range` where only `for` is kept and the verifier regenerates `i`[^spec-practice].

The source describes the method as lossless unlike quantization: output matches the target-only process, with worst-case cost limited to a negligible time-to-first-token increase from draft overhead[^spec-practice]. Reported acceptance is 50–80% on predictable tasks[^spec-practice].

## When it wins

Best fit is low-concurrency interactive serving with batch sizes around one to eight, where the GPU has idle compute between sequential steps for the drafter to use: single-user chat, coding assistants, low-latency single-request APIs, and real-time applications[^spec-practice].

Workload patterns called out as strong fits[^spec-practice]:

- Code generation, where syntax constrains the next tokens.
- Structured outputs such as JSON, XML, SQL, and API responses with repeating keys and brackets.
- Repetitive template-based generation, including standard-format summarization and consistently structured Q&A.

The source claims more than three times the performance is achievable on code, structured, and other predictable non-creative workloads[^spec-practice].

## When it loses

Avoid or retune when[^spec-practice]:

- Serving high-concurrency offline batch work such as large-batch processing or overnight bulk inference (source guidance: benefits diminish at batch sizes of 32 or more because the GPU is already saturated and the drafter becomes overhead).
- Generating highly creative text such as poetry, fiction, or marketing copy, where novel token choices lower acceptance and waste draft compute while adding TTFT.
- Using a poorly aligned speculator trained on different data from the verifier, which collapses acceptance; the remedy is domain alignment, either by downloading a matched speculator or training one with the vLLM Speculators project.

## vLLM deployment path in the source

Choose a speculator roughly 10–50 times smaller than the target (for example 1B for a 70B target), trained on similar data and optimized for speed over accuracy[^spec-practice]. Starting points named are Red Hat AI EAGLE-family speculators for Gemma, Qwen, Llama, and Mistral targets, with the vLLM Speculators project as the training path when no matched speculator exists[^spec-practice].

> Version note: the source (2026-06-12) configures speculation with the older split flags `--speculative-model` / `--num-speculative-tokens` plus `--use-v2-block-manager`; current wiki reference configures all options through `--speculative-config` / `speculative_config` and treats the split flags as deprecated — see [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md)[^spec-practice].

Source-era vLLM example (historical flag shape)[^spec-practice]:

```bash
vllm serve RedHatAI/gemma-4-31B-it-FP8-Dynamic \
  --speculative-model RedHatAI/gemma-4-31B-it-speculator.eagle3 \
  --num-speculative-tokens 5 \
  --use-v2-block-manager \
  --gpu-memory-utilization 0.9 \
  --dtype auto
```

A newer source-reported vLLM DFlash invocation uses the consolidated config shape with 15 draft tokens on Qwen3.5-9B[^spec-practice]:

```bash
vllm serve Qwen/Qwen3.5-9B \
  --speculative-config '{"method": "dflash", "model": "z-lab/Qwen3.5-9B-DFlash", "num_speculative_tokens": 15}' \
  --max-num-batched-tokens 32768
```

## Tuning

Start with four to five speculative tokens; too many wastes work rejecting bad guesses and too few leaves gains on the table[^spec-practice]. The source suggests 3 for conservative unpredictable tasks, 10 for aggressive code or structured output, and raising the count when hit rates run very high[^spec-practice].

Acceptance rate is the golden metric[^spec-practice]:

- 60–80%: sweet spot, reported as roughly two to three times faster.
- Below 50%: suspect poor draft-target alignment or too creative a workload.
- Above 85%: consider raising `num_speculative_tokens`.

Track tokens per second (should rise), time per output token (should fall), time to first token (may rise slightly from draft overhead), and cost per 1,000 tokens (should fall)[^spec-practice]. If the gain is below about 1.5 times, the source advises treating the workload as too unpredictable or the speculator as misaligned[^spec-practice]. For concurrency-varying deployments, prefer a batch-dependent draft-token schedule rather than one static K — see [vLLM Dynamic Speculative Decoding](vllm-dynamic-speculative-decoding.md).

## Eagle 3 request-rate, task, and draft-length evidence

All figures below are source-reported GuideLLM benchmarks from the Eagle 3 Red Hat source, not independently verified[^eagle3-fly]:

- **Request-rate tradeoff:** on MT-Bench two-turn chat with 1024-token cap, Llama 3.1 8B on 1×A100 cuts per-request latency up to 1.8×, and Llama 3.3 70B on 4×A100 up to 1.6× at low request rates; at higher rates the 70B case slows down as compute saturates. The source frames this as memory-bound wins at low concurrency versus compute-bound losses at high batch/throughput[^eagle3-fly].
- **Task dependence:** Eagle was trained primarily on chat data and transfers unevenly. On Llama 3.3 70B across SpecBench math, RAG, translation plus HumanEval coding, RAG and math reasoning gain up to 2.1× better latency from higher acceptance, while German-to-English translation performs poorly; the source suggests training drafters on the target dataset to close such gaps[^eagle3-fly].
- **Draft length:** optimal K depends on both rate and task because acceptance is conditional on all prior draft tokens. At low rates a longer draft can pay despite low tail acceptance; at high rates shorten K to avoid drafting likely-rejected tokens. In the source's Llama 3.3 70B tests, translation is optimal at K=1 or even 0, while RAG still improves at K=5, so measure on your own workload[^eagle3-fly].
- **Greedy versus tree:** tree decoding drafts ~64 tokens across branches with masked attention and verifies in one target pass to raise accepted length by ~1–2 tokens, but spends far more draft/verify compute than adding 1–2 greedy tokens. It wins only for synchronous low-rate latency; past that it slows generation significantly. vLLM does not currently support tree decoding[^eagle3-fly].
- **Limits:** available Eagle 3 speculators in the source era cover shorter contexts (2048-token cap noted) with few model choices; performance varies with training-data match, so benchmark your workload and consider fine-tuning[^eagle3-fly].

## Reported measurements and cost math

All figures below are source-reported single-setup numbers, not independently verified[^spec-practice]:

- Qwen3.5-9B on one H100 with `--max-num-batched-tokens 32768`: about 145 tokens/s standard versus about 424 tokens/s with the DFlash config above, nearly three times higher with slightly higher TTFT[^spec-practice].
- Cloud-cost illustration at $5/hr: 100 tokens/s costs $0.05 per 1,000 tokens versus 250 tokens/s (2.5 times) at $0.02 per 1,000 tokens, a 60% reduction, or equivalently 2.5 times more users on the same cluster[^spec-practice].
- Production illustration at 10M tokens/day: $500/day standard versus $200/day optimized, or $109,500 annual savings[^spec-practice].

## Relationships

- Uses [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — current consolidated `speculative_config` reference; source-era split flags are deprecated there.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE/Eagle3 draft-model family behind the Red Hat AI `.eagle3` speculators named in the source; Eagle 3 mechanism, v0.8.5/v0.9.1 support, and Llama-3.3-70B serve example live there.
- Related to [vLLM Speculators Library](vllm-speculators.md) — training and packaging path when no matched speculator exists.
- Related to [vLLM Dynamic Speculative Decoding](vllm-dynamic-speculative-decoding.md) — batch-size-to-K scheduling for the high-concurrency fade the source describes qualitatively.
- Related to [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md) — request-level acceptance measurement behind the source's acceptance-rate tuning guidance.
- Related to [SGLang Speculative Decoding](sglang-speculative-decoding.md) — SGLang-side EAGLE/MTP counterpart for cross-engine comparison.
- Related to [Distributed Inference Optimization Levers](distributed-inference-optimization-levers.md) — EAGLE 3.1/MTP/Medusa/n-gram selection table and constrained-decoding caution; note its measure-first warning for grammar-constrained traffic tensions with the structured-output fit above.
- Related to [vLLM Speculative Decoding on AMD GPUs](vllm-speculative-decoding-amd-gpus.md) — MI300X/MI355X per-method N optima and per-position acceptance decay grounding the K and acceptance-rate bands above.

## Coverage limits

- `assets/watch.img` and `assets/watch-2.img` are saved YouTube HTML pages, not the throughput-comparison screenshots the prose references, so the 145 versus 424 tokens/s claim rests on prose alone and was not visually verified.
- `assets/image2_182.png.webp` (1549×1018) was inspected only to confirm it shows a Hugging Face model list consistent with the Red Hat AI speculator description; no additional model IDs were compiled from the image.
- Linked AWS code-generation, structured-output, and Trainium examples plus the Red Hat AI Hub collection were not inspected beyond the source's description.
- Eagle 3 chart assets `spec_decode_mt_bench_1.png.webp`, `spec_decode_llama_3.3_70b.png.webp`, `spec_decode_draft_length.png.webp`, `spec_decode_tree.png.webp`, and `text_generation_example_-_speculative_decoding_vs_baseline_generation_example.png.webp` under `../raw/fly-eagle3-fly-faster-inference-vllm-speculative-decoding/assets/` were enumerated but not pixel-verified; quantitative claims above rest on the source prose and figure captions.

[^spec-practice]: Sawyer Bowerman, How speculative decoding delivers faster LLM inference — `../raw/how-speculative-decoding-delivers-faster-llm-inference/index.md` (Red Hat Developer, 2026-06-12), covering draft-plus-parallel-verify mechanism and lossless claim, hare/tortoise sizing, worked accept/reject example, low-concurrency versus high-batch and creative-workload fit, alignment requirement, Red Hat AI and Speculators paths, vLLM flag examples, K and acceptance-rate tuning bands, TPS/TTFT/TPOT/cost metrics, Qwen3.5-9B DFlash measurement, and cost-savings math.

[^eagle3-fly]: Alexandre Marques, Fly Eagle(3) fly: Faster inference with vLLM & speculative decoding — `../raw/fly-eagle3-fly-faster-inference-vllm-speculative-decoding/index.md` (Red Hat Developer, 2025-07-01), Eagle 3 GuideLLM evidence: MT-Bench rate/latency tradeoff (8B up to 1.8×, 70B up to 1.6× low-rate), SpecBench plus HumanEval task dependence (RAG/math up to 2.1×, de-en translation poor), draft-length tuning (translation K=1/0, RAG K=5), greedy versus 64-token tree tradeoff and vLLM non-support, and 2048-context plus model-availability limits.
