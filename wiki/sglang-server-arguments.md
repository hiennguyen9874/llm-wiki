---
type: Concept
title: SGLang Server Arguments
description: Canonical launch and configuration reference for SGLang covering config-file precedence, parallelism, memory, quantization, backends, and disaggregation flags.
tags: [sglang, server, configuration, deployment]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T15:00:00Z }
sources:
  - id: sgl-server-args
    resource: ../raw/sglang/advanced_features/server_arguments.mdx
    title: Server Arguments
---

SGLang configures serving through `python -m sglang.launch_server` flags, a YAML `--config` file, and `server_args.py`; CLI flags override config-file values and `python3 -m sglang.launch_server --help` lists the full set[^sgl-server-args].

## Discovery and config precedence

- Full argument list: `python3 -m sglang.launch_server --help`[^sgl-server-args].
- Canonical implementation reference: `server_args.py`[^sgl-server-args].
- YAML config: create `config.yaml` with dashed keys such as `model-path`, `host`, `port`, `tensor-parallel-size`, `enable-metrics`, and `log-requests`, then launch with `python -m sglang.launch_server --config config.yaml`; CLI arguments override config-file values[^sgl-server-args].

## Common launch patterns

- Tensor parallelism: `--tp 2`; if peer access fails between devices, add `--enable-p2p-check`[^sgl-server-args].
- Data parallelism: `--dp 2`, optionally combined with `--tp 2` for 4 GPUs total; DP favors throughput when memory allows, and the source recommends SGLang Model Gateway (former Router) for DP[^sgl-server-args].
- Serving OOM: lower `--mem-fraction-static` (prose default `0.9`, e.g. to `0.7`) to shrink weights plus KV-cache pool[^sgl-server-args].
- Prefill OOM on long prompts: lower `--chunked-prefill-size` (e.g. to `4096`) or set `-1` to disable chunked prefill[^sgl-server-args].
- `torch.compile`: `--enable-torch-compile` helps small models at small batch sizes; default Inductor cache is `/tmp/torchinductor_root`, overridable with `TORCHINDUCTOR_CACHE_DIR`[^sgl-server-args].
- Quantization shortcuts: `--torchao-config int4wo-128`, `--quantization fp8` on FP16 checkpoints (FP8 checkpoints load without flags), and `--kv-cache-dtype fp8_e5m2` for FP8 KV cache[^sgl-server-args].
- Deterministic inference: `--enable-deterministic-inference`[^sgl-server-args].
- Chat templates: use a custom template when the HF tokenizer lacks one; select a named tokenizer template with `--hf-chat-template-name tool_use`[^sgl-server-args].
- Multi-node TP: `--nnodes 2` with `--dist-init-addr host:port`, `--node-rank`, and matching `--tp`; add `--disable-cuda-graph` on deadlock[^sgl-server-args].
- Containers: set up shared memory for inter-process communication (`--shm-size` for Docker, `/dev/shm` sizing for Kubernetes)[^sgl-server-args].

## Model, tokenizer, and loading

- `--model-path` / `--model`: local folder or HF repo ID, default `None`[^sgl-server-args].
- `--tokenizer-path`, `--tokenizer-mode auto|slow` (default `auto`), `--tokenizer-worker-num` (default `1`), `--skip-tokenizer-init` for direct `input_ids` requests[^sgl-server-args].
- `--load-format`: `auto`, `pt`, `safetensors`, `npcache`, `dummy`, `sharded_state`, `gguf`, `bitsandbytes`, `layered`, `flash_rl`, `remote`, `remote_instance`, `fastsafetensors`, `private`; default `auto`[^sgl-server-args].
- `--trust-remote-code`, `--revision`, `--context-length` (default `None`, else model `config.json`), `--is-embedding`, `--enable-multimodal`, `--model-impl auto|sglang|transformers` (default `auto`)[^sgl-server-args].

## HTTP server and runtime

- `--host` default `127.0.0.1`, `--port` default `30000`, plus `--fastapi-root-path`, `--grpc-mode`, `--skip-server-warmup`, `--warmups`, `--nccl-port`, and `--checkpoint-engine-wait-weights-before-ready`[^sgl-server-args].
- Runtime: `--device cuda|xpu|hpu|npu|cpu` (default auto-detect), `--tensor-parallel-size` / `--tp-size` default `1`, `--pipeline-parallel-size` / `--pp-size` default `1`, `--pp-max-micro-batch-size`, `--pp-async-batch-depth`, `--stream-interval` default `1`, `--stream-output`, `--random-seed`, `--watchdog-timeout` default `300`, plus download, checksum, GPU-selection (`--base-gpu-id` default `0`, `--gpu-id-step` default `1`), `--sleep-on-idle`, and constrained-JSON whitespace controls[^sgl-server-args].

## Quantization and dtype

- `--dtype`: `auto`, `half`, `float16`, `bfloat16`, `float`, `float32`; default `auto` (FP16 for FP32/FP16 models, BF16 for BF16 models)[^sgl-server-args].
- `--quantization`: `awq`, `fp8`, `gptq`, `marlin`, `gptq_marlin`, `awq_marlin`, `bitsandbytes`, `gguf`, `modelopt`, `modelopt_fp8`, `modelopt_fp4`, `petit_nvfp4`, `w8a8_int8`, `w8a8_fp8`, `moe_wna16`, `qoq`, `w4afp8`, `mxfp4`, `auto-round`, `compressed-tensors`, `modelslim`, `quark_int4fp8_moe`; default `None`[^sgl-server-args].
- `--kv-cache-dtype`: `auto`, `fp8_e5m2`, `fp8_e4m3`, `bf16`, `bfloat16`, `fp4_e2m1`; default `auto`[^sgl-server-args].
- Related: `--quantization-param-path` for FP8 KV scaling factors, `--enable-fp32-lm-head`, ModelOpt checkpoint paths (`--modelopt-quant`, `--modelopt-checkpoint-restore-path`, `--modelopt-checkpoint-save-path`, `--modelopt-export-path`, `--quantize-and-serve`), and `--rl-quant-profile` required with `--load-format flash_rl`[^sgl-server-args].

## Memory and scheduling

- Pool sizing: `--mem-fraction-static`, `--max-running-requests`, `--max-queued-requests`, `--max-total-tokens`, `--page-size` default `1`[^sgl-server-args].
- Prefill control: `--chunked-prefill-size`, `--prefill-max-requests`, `--max-prefill-tokens` default `16384`, `--enable-dynamic-chunking` for pipeline parallelism[^sgl-server-args].
- Policies: `--schedule-policy lpm|random|fcfs|dfs-weight|lof|priority|routing-key` default `fcfs`, `--schedule-conservativeness` default `1.0`, `--radix-eviction-policy lru|lfu` default `lru`[^sgl-server-args].
- Priority scheduling: `--enable-priority-scheduling`, `--abort-on-priority-when-disabled`, `--schedule-low-priority-values-first`, `--priority-scheduling-preemption-threshold` default `10`[^sgl-server-args].
- SWA/hybrid memory: `--swa-full-tokens-ratio` default `0.8`, `--disable-hybrid-swa-memory`[^sgl-server-args].
- Prefill delayer for DP attention: `--enable-prefill-delayer`, `--prefill-delayer-max-delay-passes` default `30`, plus token-usage watermark and histogram-bucket controls[^sgl-server-args].

## Parallelism and distributed serving

- DP: `--data-parallel-size` / `--dp-size` default `1`, `--load-balance-method auto|round_robin|follow_bootstrap_room|total_requests|total_tokens` default `auto` (`total_tokens` needs DP attention)[^sgl-server-args].
- Multi-node: `--dist-init-addr` / `--nccl-init-addr`, `--nnodes` default `1`, `--node-rank` default `0`[^sgl-server-args].
- Model overrides: `--json-model-override-args`, `--preferred-sampling-params`[^sgl-server-args].

## Logging, metrics, and tracing

- Levels: `--log-level` default `info`, `--log-level-http`, `--show-time-cost`, `--decode-log-interval` default `40`, `--enable-request-time-stats-logging`, `--gc-warning-threshold-secs` default `0.0`[^sgl-server-args].
- Request logging: `--log-requests`, `--log-requests-level 0|1|2|3` default `2`, `--log-requests-format text|json` default `text`, `--log-requests-target` for stdout and/or directories[^sgl-server-args].
- Metrics/tracing: `--enable-metrics`, `--enable-metrics-for-all-schedulers` (per-rank metrics, useful with DP attention), tokenizer-metric label controls, TTFT/ITL/E2E buckets, token histograms, `--enable-trace`, `--otlp-traces-endpoint`, file export, `--kv-events-config` for Dynamo KV events, and `--crash-dump-folder` for pre-crash request dumps[^sgl-server-args].

## API, templates, and parsers

- Auth and naming: `--api-key`, `--admin-api-key`, `--served-model-name`, `--weight-version`[^sgl-server-args].
- Templates: `--chat-template`, `--hf-chat-template-name`, `--completion-template`, `--file-storage-path`, `--enable-cache-report`[^sgl-server-args].
- Structured behavior: `--reasoning-parser`, `--tool-call-parser`, `--tool-server`, `--sampling-defaults`[^sgl-server-args].

## LoRA

- Enablement: `--enable-lora` (auto-true when `--lora-paths` is given), `--lora-paths` as names/paths or JSON with pinning, `--enable-lora-overlap-loading`[^sgl-server-args].
- Capacity and eviction: `--max-lora-rank`, `--lora-target-modules`, `--max-loras-per-batch` default `8`, `--max-loaded-loras`, `--lora-eviction-policy lru|fifo` default `lru`[^sgl-server-args].
- Kernels: `--lora-backend triton|csgmv|ascend|torch_native` default `csgmv`, `--max-lora-chunk-size` default `16` for `csgmv`[^sgl-server-args].

## Kernel backends

- `--attention-backend` with per-stage overrides `--prefill-attention-backend` and `--decode-attention-backend`; listed options include `triton`, `torch_native`, `flex_attention`, `nsa`, `cutlass_mla`, `fa3`, `fa4`, `flashinfer`, `flashmla`, `trtllm_mla`, `trtllm_mha`, `dual_chunk_flash_attn`, `aiter`, `wave`, `intel_amx`, `ascend`[^sgl-server-args].
- `--sampling-backend flashinfer|pytorch|ascend`, `--grammar-backend xgrammar|outlines|llguidance|none`, `--mm-attention-backend sdpa|fa3|fa4|triton_attn|ascend_attn|aiter_attn`[^sgl-server-args].
- NSA/GEMM: `--nsa-prefill-backend`, `--nsa-decode-backend`, `--fp8-gemm-backend auto|deep_gemm|flashinfer_trtllm|cutlass|triton|aiter` default `auto`, `--fp4-gemm-backend`, and `--disable-flashinfer-autotune`[^sgl-server-args].

## Speculative decoding

- Draft setup: `--speculative-algorithm`, `--speculative-draft-model-path` / `--speculative-draft-model`, revision, load format, quantization, token map, and per-backend overrides for attention and MoE[^sgl-server-args].
- Sampling: `--speculative-num-steps`, `--speculative-eagle-topk`, `--speculative-num-draft-tokens`, accept thresholds `--speculative-accept-threshold-single` and `--speculative-accept-threshold-acc` (both default `1.0`), and `--speculative-attention-mode prefill|decode` default `prefill`[^sgl-server-args].
- N-gram: window, BFS breadth, match-type, branch-length, and capacity controls under `--speculative-ngram-*`[^sgl-server-args].
- Multi-layer EAGLE: `--enable-multi-layer-eagle`[^sgl-server-args].

## MoE, Mamba, and extended caches

- MoE/EP: `--expert-parallel-size` / `--ep-size` / `--ep`, `--moe-a2a-backend`, `--moe-runner-backend`, DeepEP/EPLB controls (`--deepep-mode`, `--enable-eplb`, rebalance options, expert-distribution recording/metrics), plus dense-TP, elastic-EP, and Mooncake IB-device options[^sgl-server-args].
- Mamba: `--max-mamba-cache-size`, `--mamba-ssm-dtype`, `--mamba-full-memory-ratio`, `--mamba-scheduler-strategy`, `--mamba-track-interval`[^sgl-server-args].
- Hierarchical cache: `--enable-hierarchical-cache`, `--hicache-ratio`, `--hicache-size`, `--hicache-write-policy write_back|write_through|write_through_selective` default `write_through`, `--hicache-io-backend direct|kernel|kernel_ascend`, `--hicache-mem-layout`, `--hicache-storage-backend file|mooncake|hf3fs|nixl|aibrix|dynamic|eic`, prefetch policy, and extra config[^sgl-server-args].
- Other serving extensions: hierarchical sparse attention config, `--enable-lmcache`, KTransformers (`--kt-*`), diffusion-LLM (`--dllm-*`), double sparsity (`--enable-double-sparsity` plus `--ds-*`), CPU offload (`--cpu-offload-gb` plus `--offload-*`), and multi-item scoring delimiter[^sgl-server-args].

## Optimization and debugging

- Cache/graphs: `--disable-radix-cache`, `--cuda-graph-max-bs`, `--cuda-graph-bs`, `--disable-cuda-graph`, padding/GC/profile controls, and piecewise CUDA-graph options[^sgl-server-args].
- Overlap/scheduling: `--disable-overlap-schedule`, `--enable-mixed-chunk`, `--enable-dp-attention`, `--enable-dp-lm-head`, `--enable-two-batch-overlap`, `--enable-single-batch-overlap`, `--tbo-token-distribution-threshold`[^sgl-server-args].
- Compile/quant/debug: `--enable-torch-compile`, `--torch-compile-max-bs`, `--torchao-config`, Triton attention tuning, `--num-continuous-decode-steps`, memory-saver/weight-backup flags, `--allow-auto-truncate`, custom logit processors, MLA/chunked-prefix/fast-image controls, hidden-state and routed-expert returns, NUMA pinning, deterministic inference, NSA context-parallel and fused QK-norm/RoPE flags[^sgl-server-args].
- Tokenizer batching: `--enable-dynamic-batch-tokenizer` plus batch-size/timeout controls; tensor-dump debugging uses `--debug-tensor-dump-*`[^sgl-server-args].

## Disaggregation and multiplexing

- PD: `--disaggregation-mode null|prefill|decode`, `--disaggregation-transfer-backend mooncake|nixl|ascend|fake` default `mooncake`, `--disaggregation-bootstrap-port` default `8998`, decode TP/DP and prefill PP sizing, IB device, decode KV offload, fake-auto testing, reserved decode tokens, and polling interval[^sgl-server-args].
- Encoder/prefill: `--encoder-only`, `--language-only`, `--encoder-transfer-backend`, `--encoder-urls`[^sgl-server-args].
- PD multiplexing: `--enable-pdmux`, `--pdmux-config-path`, `--sm-group-num`[^sgl-server-args].

## Multimodal, loading, and hooks

- Multimodal: `--mm-max-concurrent-calls` default `32`, `--mm-per-request-timeout` default `10.0`, broadcast/process configs, `--mm-enable-dp-encoder`, per-request data limits, and `--enable-prefix-mm-cache`[^sgl-server-args].
- Custom loading: `--custom-weight-loader`, `--weight-loader-disable-mmap`, remote-instance loader addresses/ports/backend, checkpoint-decryption configs (`--decrypted-config-file`, `--decrypted-draft-config-file`)[^sgl-server-args].
- Forward hooks: `--forward-hooks` takes a JSON list with `target_modules` glob patterns, `hook_factory` import path, optional `name`, and optional `config` dict[^sgl-server-args].

## Deprecated mappings

- `--enable-ep-moe` is deprecated in favor of setting `--ep-size` to `--tp-size`; `--enable-deepep-moe` in favor of `--moe-a2a-backend deepep`[^sgl-server-args].
- MoE runner flags `--enable-flashinfer-cutlass-moe`, `--enable-flashinfer-cutedsl-moe`, `--enable-flashinfer-trtllm-moe`, `--enable-triton-kernel-moe`, and `--enable-flashinfer-mxfp4-moe` are deprecated in favor of the corresponding `--moe-runner-backend` values; `--nsa-prefill` / `--nsa-decode` alias the newer `--nsa-prefill-backend` / `--nsa-decode-backend` stage options[^sgl-server-args].

## Relationships

- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — tuning procedure for `--mem-fraction-static`, `--chunked-prefill-size`, `--cuda-graph-max-bs`, `--schedule-conservativeness`, and DP/TP selection named in launch guidance.
- Uses [SGLang Observability](sglang-observability.md) — enablement detail for `--enable-metrics`, `--log-requests`, and `--crash-dump-folder` summarized here.
- Uses [SGLang Quantization](sglang-quantization.md) — method detail behind `--quantization`, `--torchao-config`, and ModelOpt flags summarized here.
- Uses [SGLang Quantized KV Cache](sglang-quantized-kv-cache.md) — format and scaling-factor detail behind `--kv-cache-dtype` and `--quantization-param-path` summarized here.
- Uses [SGLang Attention Backends](sglang-attention-backends.md) — backend-selection detail behind `--attention-backend` and prefill/decode overrides summarized here.
- Uses [SGLang Expert Parallelism](sglang-expert-parallelism.md) — EP/EPLB and backend detail behind MoE flags summarized here.
- Uses [SGLang Pipeline Parallelism](sglang-pipeline-parallelism.md) — PP and micro-batch detail behind pipeline flags summarized here.
- Uses [SGLang PD Disaggregation](sglang-pd-disaggregation.md) — deployment detail behind `--disaggregation-*` flags summarized here.
- Uses [SGLang LoRA Serving](sglang-lora-serving.md) — adapter-management detail behind LoRA flags summarized here.
- Uses [SGLang Deterministic Inference](sglang-deterministic-inference.md) — guarantee and backend detail behind `--enable-deterministic-inference` summarized here.
- Uses [SGLang Forward Hooks](sglang-forward-hooks.md) — hook-specification detail behind `--forward-hooks` summarized here.
- Uses [SGLang Data-Parallel Multimodal Encoder](sglang-dp-multimodal-encoder.md) — encoder-parallel detail behind `--mm-enable-dp-encoder` summarized here.
- Uses [SGLang Checkpoint Engine Integration](sglang-checkpoint-engine.md) — weight-loading context for `--checkpoint-engine-wait-weights-before-ready` summarized here.

## Coverage limits

- This is a durable synthesis, not an exhaustive dump of all ~310 flags; exact defaults, types, and newly added options should be verified with `python3 -m sglang.launch_server --help` and `server_args.py`[^sgl-server-args].
- Linked SGLang Model Gateway (former Router), hyperparameter-tuning, torch.compile cache, custom chat-template, and deterministic-inference pages were not re-inspected beyond what this source states[^sgl-server-args].
- No measured performance numbers, workload-specific recommendations beyond the launch recipes above, or Docker/Kubernetes manifest detail beyond shared-memory sizing were in this source[^sgl-server-args].

[^sgl-server-args]: Server Arguments — `../raw/sglang/advanced_features/server_arguments.mdx`.
