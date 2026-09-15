---
type: Synthesis
title: vLLM vs SGLang vs TensorRT-LLM H100 Benchmark
description: Third-party H100 comparison of vLLM, SGLang and TensorRT-LLM on Qwen 7B–32B across ShareGPT chat and 16K long-context with TTFT, decode latency and throughput trade-offs.
tags: [vllm, sglang, tensorrt-llm, benchmark, h100, qwen]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: jarvis-h100-3way
    resource: ../raw/vllm-sglang-trtllm-comparison/index.md
    title: "SGLang vs vLLM: H100 Benchmarks, with TensorRT-LLM"
---

On the tested Qwen H100 configurations, vLLM was the strongest general default for combined first-token latency and output throughput, SGLang won decode latency on two 16K runs at the cost of higher first-token latency, and TensorRT-LLM showed stable decode kernels on chat but sharply higher first-token latency under load with the published engine builds[^jarvis-h100-3way].

## Test scope

The following is source-attributed methodology, not an independent rerun[^jarvis-h100-3way]:

- Hardware: 1×H100 for Qwen2.5-7B-Instruct; 2×H100 for Qwen3-30B-A3B and Qwen3-32B, with GPU count held constant across frameworks within each model.
- Models: Qwen2.5-7B-Instruct dense, Qwen3-30B-A3B MoE, and Qwen3-32B dense, all in BF16.
- Datasets: ShareGPT chat with fixed 256-token outputs via `--ignore-eos --output-len 256`; RULER 16K long-context prompts with ~16K inputs and default 256-token outputs from a custom 1,000-sample JSONL conversion.
- Concurrency sweep: 60, 120, 180, 240, 300, 360, 420, 480, 540, 600, plus `no_cap` saturation where the client sends as fast as possible.
- Client: `vllm bench serve` against all three servers with 1,000 prompts and seed 42.
- Metrics read together: TTFT mean, TPOT mean, ITL mean, and output throughput.

Engine setup matters for interpretation: vLLM and SGLang served Hugging Face checkpoints directly, while TensorRT-LLM required checkpoint conversion plus a per-workload `trtllm-build` engine and `trtllm-serve` runtime with explicit `max_batch_size`, `max_input_len`, `max_seq_len`, and `max_num_tokens` limits[^jarvis-h100-3way].

## Results by workload

All numbers below are selected endpoints from the source tables; full 11-point sweeps remain in raw evidence[^jarvis-h100-3way].

### Qwen2.5-7B-Instruct, ShareGPT, 1×H100

vLLM had the strongest throughput curve, 6,927 tok/s at concurrency 60 rising to 23,523 tok/s at `no_cap`; SGLang stayed competitive through capped runs but fell to 16,787 tok/s at `no_cap` with ITL spiking to 100.92 ms; TensorRT-LLM decode stayed flat around 9–12 ms capped and 6.62 ms at `no_cap`, but TTFT reached 7,838.87 ms at `no_cap` versus 2,033.66 ms for vLLM and 1,809.97 ms for SGLang[^jarvis-h100-3way].

Takeaway supported by this run: vLLM gave the best latency-throughput balance for chat; SGLang decode became expensive at high concurrency; TensorRT-LLM decoded efficiently but paid in first-token latency[^jarvis-h100-3way].

### Qwen2.5-7B-Instruct, RULER 16K, 1×H100

Prefill dominated: vLLM had the lowest TTFT at most levels, for example 1,874.08 ms at concurrency 60 versus 10,801.75 ms for SGLang and 2,629.85 ms for TensorRT-LLM; SGLang had the best decode at roughly 77–81 ms TPOT/ITL after concurrency 120 versus ~119 ms for vLLM and ~108 ms for TensorRT-LLM; throughput was close at roughly 578–582 tok/s for vLLM, 558–563 tok/s for TensorRT-LLM, and 553–562 tok/s for SGLang[^jarvis-h100-3way].

Takeaway supported by this run: vLLM when TTFT mattered most; SGLang for decode latency if slower first-token delivery was acceptable[^jarvis-h100-3way].

### Qwen3-30B-A3B, ShareGPT, 2×H100

vLLM peaked near 9,360.88 tok/s at concurrency 360 and stayed above 8,400 tok/s at higher load; SGLang was strong early at 7,287.44 tok/s at 180 but dipped near 5,728.35 tok/s at 300 with decode moving into the 40–50 ms range after concurrency 240; TensorRT-LLM stayed flatter near 5.0–5.5K tok/s with very stable ~17 ms TPOT/ITL capped, but TTFT crossed 8,926.35 ms at 600 and 13,618.20 ms at `no_cap`[^jarvis-h100-3way].

Takeaway supported by this run: vLLM strongest end-to-end for this MoE chat shape; TensorRT-LLM decode stability did not offset first-token cost under the published engine config[^jarvis-h100-3way].

### Qwen3-30B-A3B, RULER 16K, 2×H100

vLLM led TTFT at most levels and throughput at roughly 804–807 tok/s, followed by SGLang at roughly 776–781 tok/s and TensorRT-LLM at roughly 701–715 tok/s; SGLang had the lowest decode at roughly 61–63 ms versus ~70 ms for vLLM and ~84–87 ms for TensorRT-LLM[^jarvis-h100-3way].

Takeaway supported by this run: vLLM best overall because lowest TTFT plus highest throughput; SGLang attractive only when decode latency outranked first-token latency[^jarvis-h100-3way].

### Qwen3-32B, ShareGPT, 2×H100

vLLM reached the highest capped throughput, peaking above 4.2K tok/s at concurrency 600; SGLang closed the gap at higher concurrency but ran higher decode latency; TensorRT-LLM held TPOT near 30 ms and ITL near 28 ms across the sweep while TTFT rose from 180 concurrency onward to 19,384.38 ms at `no_cap`[^jarvis-h100-3way].

Takeaway supported by this run: vLLM best throughput profile; TensorRT-LLM decode-stable but less suitable for interactive chat under this engine config[^jarvis-h100-3way].

### Qwen3-32B, RULER 16K, 2×H100

All TTFTs were very large because long prefill dominated: vLLM and TensorRT-LLM tracked closely while SGLang was highest across the sweep, reaching 741,250.90 ms at `no_cap` versus 657,264.13 ms for vLLM and 664,655.94 ms for TensorRT-LLM; vLLM also had the best decode near 98 ms and throughput near 191 tok/s, versus TensorRT-LLM near 107 ms and 188 tok/s and SGLang at 100–122 ms and 166–168 tok/s[^jarvis-h100-3way].

Takeaway supported by this run: vLLM strongest overall; TensorRT-LLM a close throughput second; SGLang less competitive on both TTFT and throughput here[^jarvis-h100-3way].

## Practical reading

The following is synthesis from the source verdict, not a universal ranking[^jarvis-h100-3way]:

- Start with vLLM as the baseline when the workload mixes short chat and long prompts and predictable scaling without heavy tuning matters.
- Test SGLang when prefix reuse or decode latency dominates and slower first-token delivery is acceptable.
- Use TensorRT-LLM when the deployment is NVIDIA-specific and there is budget to tune `max_batch_size`, `max_input_len`, `max_seq_len`, and `max_num_tokens` for the exact concurrency target; several ShareGPT engine builds used `max_batch_size` values below the tested concurrency sweep, so high-concurrency TTFT in this source is configuration-sensitive.
- Read TTFT, TPOT, ITL, and throughput together: faster decode alone did not imply faster user-visible response in these runs.

## Relationships

- Compares with [SGLang and vLLM Comparison](sglang-vs-vllm.md) — architecture and cache-design comparison; this concept adds measured H100 TTFT/decode/throughput trade-offs plus TensorRT-LLM as a third engine-first path.
- Compares with [Ollama vs vLLM vs SGLang Serving Choice](ollama-vs-vllm-vs-sglang.md) — beginner three-way selection framing; this concept adds concurrency-swept Qwen evidence for the vLLM-default versus SGLang-prefix/decode guidance.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) and [SGLang Unified Radix Cache](sglang-unified-radix-cache.md) — cache designs behind the prefill/TTFT versus decode discussion summarized here.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — long-prompt scheduling context relevant to the RULER 16K TTFT behavior.

## Coverage limits

- Exact framework versions are not recorded in the source; validate against deployed versions.
- Qwen-only, H100-only, BF16-only evidence with fixed output lengths; prompt-length, concurrency, software-version, and serving-flag changes can change the outcome.
- All clients used `vllm bench serve`; server/client interaction bias was not isolated in the source.
- Six combined-metric chart images visualize the same TTFT/TPOT/ITL/throughput tables compiled here and were spot-checked rather than independently digitized; three framework logo images are decorative and carry no performance claims.
- The source's JarvisLabs GPU-rental setup steps were excluded as non-durable vendor operations.

[^jarvis-h100-3way]: Jaydev Tonde, SGLang vs vLLM: H100 Benchmarks, with TensorRT-LLM — `../raw/vllm-sglang-trtllm-comparison/index.md` (jarvislabs.ai, 2026-05-18), covering H100 setup, Qwen2.5-7B/Qwen3-30B-A3B/Qwen3-32B server and client commands, ShareGPT and RULER 16K datasets, 60–600 plus no-cap concurrency sweep, per-workload TTFT/TPOT/ITL/throughput tables, workload takeaways, and configuration-sensitive TensorRT-LLM TTFT interpretation.
