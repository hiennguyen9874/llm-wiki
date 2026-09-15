---
type: Concept
title: vLLM V1 Engine Anatomy and Request Lifecycle
description: End-to-end V1 mental model from offline LLM construction through scheduling, forward pass, advanced features, multi-GPU scale-up, DP serving, and benchmarking.
tags: [vllm, architecture, scheduling, inference-optimization]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: anatomy
    resource: ../raw/2025-09-05-anatomy-of-vllm/index.md
    title: 'Inside vLLM: Anatomy of a High-Throughput LLM Inference System'
---

vLLM V1 layers offline single-process execution, scheduler-driven paged attention with continuous batching, optional prefix / chunked / guided / speculative / disaggregated extensions, tensor-parallel scale-up, and data-parallel distributed serving behind one request lifecycle, measured with latency-throughput trade-offs[^anatomy].

## Scope and version

- Analysis targets V1 (`VLLM_USE_V1="1"`), single-process (`VLLM_ENABLE_V1_MULTIPROCESSING="0"`), offline synchronous single-GPU standard transformer as the starting point; multi-GPU, async, and online serving are layered on later[^anatomy].
- Based on commit `42172ad` (2025-08-09); V0 is treated as deprecated with concepts carrying over[^anatomy].
- Standard-transformer scope: hybrid models such as Jamba need more complex hybrid KV-cache allocation[^anatomy].
- Later posts were planned to zoom into subsystems; this concept preserves only the end-to-end model[^anatomy].

## Engine construction

Offline example is `LLM(model="TinyLlama/TinyLlama-1.1B-Chat-v1.0")` plus `SamplingParams(temperature=0.8, top_p=0.95)` and `llm.generate(prompts, sampling_params)`[^anatomy].

Constructor components[^anatomy]:

- `VllmConfig`: all model, cache, and parallelism knobs.
- Processor: raw inputs to `EngineCoreRequests` via validation, tokenization, and processing.
- Engine-core client: `InprocClient` (effectively `EngineCore`) in the single-process example, evolving toward `DPLBAsyncMPClient` at scale.
- Output processor: `EngineCoreOutputs` to user-visible `RequestOutput`.
- `StructuredOutputManager`: guided decoding; covered below.
- Scheduler: policy (`FCFS` or `priority`), `waiting` and `running` queues, and KV-cache manager with `free_block_queue` pool often holding hundreds of thousands of blocks.

Block size for a standard non-MLA transformer layer is `2 (K/V) * block_size (default 16) * num_kv_heads * head_size * dtype_num_bytes (e.g. 2 for bf16)`[^anatomy].

### Worker initialization

`UniProcExecutor` has one `Worker` on one GPU; `MultiProcExecutor` repeats the same procedures per worker[^anatomy]:

1. Init device: assign CUDA device, check dtype such as bf16, verify VRAM against `gpu_memory_utilization` (e.g. 0.8), set DP/TP/PP/EP, instantiate `model_runner` (sampler, KV cache, `input_ids` / `positions` buffers) and CPU-side `InputBatch` (buffers, block tables, sampling metadata).
2. Load model: instantiate architecture, load weights, call `model.eval()`, optionally `torch.compile()`.
3. Initialize KV cache: get per-layer spec (historically always `FullAttentionSpec`, hybrid sliding-window / Transformer-SSM needs Jenga-style handling), run profiling dummy forward plus GPU memory snapshot to size the block pool, allocate / reshape / bind KV tensors to attention layers, prepare attention metadata such as FlashAttention backend, and unless `--enforce-eager`, warm up batch sizes with dummy runs capturing CUDA graphs to cut kernel-launch overhead.

## Generate and engine step

Per prompt: create request ID plus arrival time, preprocess/tokenize to `prompt` / `prompt_token_ids` / `type` (text, tokens, embeds), pack into `EngineCoreRequest` with priority and sampling params, wrap as `Request` with status `WAITING`, and append to `waiting` for FCFS or heap-push for priority[^anatomy].

Sync example processes only initial prompts; async engines admit new requests after each step (continuous batching). Forward flattening into one super-sequence with efficient custom kernels makes continuous batching fundamentally supported even synchronously[^anatomy].

While requests remain, `step()` repeats[^anatomy]:

1. Schedule: select decode and/or (chunked) prefill for the step.
2. Forward pass: run model and sample.
3. Postprocess: append token IDs, detokenize, check stop, free KV blocks to `free_block_queue` on finish, and return finished outputs early. Streaming would emit intermediate tokens.

Stop conditions are exceeding `max_model_length` or `max_tokens`, sampling EOS unless `ignore_eos` (useful for forced-length benchmarking), matching `stop_token_ids` (present in output), or hitting stop strings (output truncated to first occurrence, strings absent)[^anatomy].

## Scheduling and paged-attention allocation

Prefill covers all prompt tokens, usually compute-bound (hardware- and length-dependent), sampling one token from the final position; decode covers one recent token with cached KVs, memory-bandwidth-bound because weights plus KV must still load[^anatomy]. V1 can mix both in one step; V0 handled only one kind at a time[^anatomy].

V1 schedules decode-first from `running`, computing new-token count (not always 1 with speculative decoding and async scheduling), calling `allocate_slots`, and subtracting from the token budget; then it schedules prefill from `waiting` via computed-block lookup (0 when prefix caching is off), `allocate_slots`, move to `running` with status `RUNNING`, and budget update[^anatomy].

`allocate_slots`[^anatomy]:

1. Compute new blocks `n` (default 16 tokens per block; e.g. 17 new tokens needs `ceil(17/16)=2`).
2. Check pool availability; on shortage attempt recompute preemption by evicting low-priority requests via `kv_cache_manager.free`, else skip scheduling. Swap preemption was V0 behavior.
3. Fetch first `n` blocks from the doubly linked `free_block_queue` coordinator pool into `req_to_blocks` mapping `request_id` to KV blocks.

## Forward pass

`execute_model` delegates model executor to `Worker` to model runner[^anatomy]:

1. Update states: prune finished requests from `input_batch`, refresh block tables and forward metadata.
2. Prepare inputs: CPU-to-GPU copies, positions, `slot_mapping`, attention metadata.
3. Forward: run paged-attention kernels over flattened concatenated super-sequence; positions and masks keep sequences isolated, avoiding right-padding.
4. Gather last-token hidden states and compute logits.
5. Sample per config (greedy, temperature, top-p, top-k).

Two execution modes are eager PyTorch forward versus replay of pre-captured CUDA-graph DAGs when eager is not enforced[^anatomy].

## Chunked prefill

Long prompts split into smaller prefill chunks so one request does not monopolize a step and inflate others' latency; e.g. chunk size 8 turns prompt `x-y-z` into at least 3 steps with sampling only on the last chunk[^anatomy]. Implementation caps new tokens per step; exceeding `long_prefill_token_threshold` resets to that value, and exceeding token budget also truncates into chunks[^anatomy]. In V1 chunked prefill is enabled by setting `long_prefill_token_threshold` to a positive integer in this source's API snapshot.

## Prefix caching

With a shared `long_prefix` longer than one block (ideally `n * block_size` aligned; otherwise `long_prefix_len % block_size` tokens recompute because incomplete blocks are not cached), the second request reuses KVs instead of recomputing `n * block_size` tokens; this helps prefill, not decode, and is enabled by default (`enable_prefix_caching=False` disables)[^anatomy].

Mechanics are `kv_cache_manager.get_computed_blocks` calling `hash_request_tokens`: split into 16-token chunks, hash each complete chunk from previous-block hash plus current tokens plus optional metadata (multimodal hash, LoRA ID, `cache_salt` injected into first block for isolation), using built-in hash or slower but less collision-prone SHA-256, storing `BlockHash` objects with hash plus token IDs in `req_to_block_hashes[request_id]`[^anatomy].

`find_longest_cache_hit` linearly searches `cached_block_hash_to_block`; first request misses, then `allocate_slots` calls `coordinator.cache_blocks` associating hashes with allocated blocks, and forward populates paged KVs[^anatomy]. Second request hits all `n` blocks and reuses them directly: reference count increments (e.g. to 2) if the first request is alive, else blocks freed to pool with count 0 are removed from `free_block_queue` again because the hash map proves validity[^anatomy].

Invalidation happens only when a block is about to be reallocated from the left of `free_block_queue` while still hashed and present in `cached_block_hash_to_block`; its hash is cleared and map entry removed so the old prefix cannot reuse it[^anatomy].

## Guided decoding FSM

Each decode step masks logits with a grammar FSM, supporting regular (Chomsky type-3, e.g. regex) through context-free (type-2, e.g. programming languages) constraints; toy `choice=["Positive","Negative"]` allows only `P`/`N` at prefill, then follows the sampled branch character by character[^anatomy].

vLLM flow[^anatomy]:

1. Engine builds `StructuredOutputManager` with tokenizer access and `_grammar_bitmask` tensor.
2. New request enters `WAITING_FOR_FSM`; `grammar_init` selects backend compiler such as `xgrammar` (third-party complexity hidden there).
3. Grammar compiles asynchronously.
4. Scheduler promotes to `WAITING` plus `structured_output_request_ids` when done, else defers to `skipped_waiting_requests` for next step.
5. After scheduling, manager prepares/updates `_grammar_bitmask`.
6. After forward, `xgr_torch_compile` expands bitmask to vocab size (32x expansion with 32-bit words; e.g. vocab 32 is one integer, larger vocabs concatenate words) and sets disallowed logits to `-inf`.
7. After sampling, `accept_tokens` advances FSM state.

API snapshot uses `GuidedDecodingParams(choice=[...])` inside `SamplingParams`; current `StructuredOutputsParams` naming postdates this source (see [vLLM Structured Outputs](vllm-structured-outputs.md)).

## Speculative decoding

One large-model pass per token reloads all weights for one token (times batch `B`); speculation proposes `k` cheap draft tokens, verifies once with the large model over context plus `k` drafts yielding `k+1` distributions, then accepts left-to-right (accept if `p_large >= p_draft`, else with probability `p_large/p_draft`), stopping at first rejection, sampling the free `(k+1)`-th token when all accept, else sampling from rebalanced `normalize(max(p_large-p_draft,0))`[^anatomy]. Accept/reject preserves the large-model distribution in expectation while yielding up to `k+1` tokens per large pass; the source points to `gpt-fast` for a simple implementation and the original speculative-sampling paper for proof[^anatomy].

At this source snapshot V1 implements faster but less accurate n-gram, EAGLE, and Medusa proposals rather than a separate LLM draft model[^anatomy]:

- n-gram: take last `prompt_lookup_max` tokens, find prior match, propose following `k` tokens, else shrink window down to `prompt_lookup_min`; source suggests reverse search for recency bias.
- EAGLE: model surgery keeping embeddings and LM head, replacing the transformer stack with a lightweight fine-tuned MLP draft.
- Medusa: auxiliary linear heads before the LM head predicting next `k` tokens in parallel.

Example config is `speculative_config={"method":"ngram","prompt_lookup_max":5,"prompt_lookup_min":3,"num_speculative_tokens":3}` on `LLM`[^anatomy]. Setup creates `drafter` (e.g. `NgramProposer`) plus Triton `rejection_sampler`; weight load is a no-op for n-gram[^anatomy]. Steady state runs regular prefill and sampling, calls `propose_draft_token_ids(k)` into `request.spec_token_ids`, reserves `len(spec_token_ids)` extra blocks in `allocate_slots` next step, copies drafts into `input_batch.token_ids_cpu`, builds `_calc_spec_decode_metadata`, runs large-model forward over drafts, uses `rejection_sampler` instead of regular sampling, and repeats[^anatomy].

## Disaggregated prefill/decode

Compute-bound prefill and bandwidth-bound decode separate into `N` prefill plus `M` decode instances with autoscaling by request mix, isolating bursty prefill from latency-sensitive decode and controlling `TTFT` and `ITL`; prefill writes KV to a KV-cache service, decode reads it[^anatomy]. Example uses debugging `SharedStorageConnector` (local filesystem as external server) with two processes on `CUDA_VISIBLE_DEVICES=0/1` and `KVTransferConfig(kv_connector="SharedStorageConnector", kv_role="kv_both", kv_connector_extra_config={"shared_storage_path":"local_storage"})`, `max_tokens=1` on prefill plus event gating before decode `generate`; the source notes `LMCache` with NIXL as fastest production connector but bleeding-edge at the time[^anatomy].

Connector lifecycle (connector interface noted as unstable)[^anatomy]:

1. Instantiate in worker init-distributed (`role="worker"`) and scheduler constructor (`role="scheduler"`).
2. Scheduler calls `get_num_new_matched_tokens` after local prefix checks (prefill sees 0, decode may hit) before `allocate_slots`.
3. Scheduler calls `update_state_after_alloc` (no-op for prefill cache cases).
4. Scheduler builds `connector.build_connector_meta`: prefill marks `is_store=True` uploads, decode marks `is_store=False` fetches.
5. Engine enters KV-connector context around forward: `start_load_kv` on enter (decode injects external KV into paged memory, prefill no-op), `wait_for_save` on exit (prefill blocks until upload, decode no-op). Layer-by-layer transfer is configuration-dependent; decode loads external KV once on its first step then works locally.

## Scale-up with MultiProcExecutor

When weights exceed one GPU, shard with tensor parallelism on one node (e.g. `TP=8`); add pipeline parallelism across nodes if still too large. Intranode bandwidth favors TP over PP even though PP moves less data; expert and sequence parallelism are out of scope for this standard-transformer walkthrough[^anatomy].

`MultiProcExecutor` (TP=8 example, driver is rank 0)[^anatomy]:

1. Initialize shared-memory `rpc_broadcast_mq`.
2. Loop over `world_size` spawning daemon workers via `WorkerProc.make_worker_process`.
3. Create per-worker reader/writer pipes.
4. Workers run `WorkerProc.worker_main` through the same device/model/KV init with TP/PP partitioning.
5. Workers learn driver versus regular roles and set up shared `rpc_broadcast_mq` for work plus `worker_response_mq` for responses.
6. Children send response-queue handles to the parent over pipes; parent unblocks when all arrive.
7. Workers busy-loop on `rpc_broadcast_mq.dequeue`, execute, and `worker_response_mq.enqueue`.
8. At runtime parent non-blocking enqueues into `rpc_broadcast_mq` and blocks on the output rank's `worker_response_mq.dequeue`.

`execute_model` abstraction is unchanged: direct worker call under `UniProcExecutor`, broadcast-queue fan-out under `MultiProcExecutor`[^anatomy].

## Distributed DP serving

Concrete shape is two H100 nodes running four engines with `TP=4`, `DP=4` (`--data-parallel-size-local 2` per node, with start-rank, address, and RPC port coordination)[^anatomy]:

```shell
vllm serve <model-name> --tensor-parallel-size 4 --data-parallel-size 4 \
  --data-parallel-size-local 2 --data-parallel-start-rank 0 \
  --data-parallel-address <master-ip> --data-parallel-rpc-port 13345 --headless
```

Second node repeats without `--headless` and with start-rank 2; networking must allow the IP/port[^anatomy].

### Headless node

`CoreEngineProcManager` launches 2 `EngineCoreProc.run_engine_core` processes per `--data-parallel-size-local`, each creating `DPEngineCoreProc` then busy-looping[^anatomy]. Each initializes parent `EngineCoreProc` with `input_queue` / `output_queue`, ZMQ `DEALER` frontend handshake for coordination addresses, NCCL DP group, `EngineCore` with `MultiProcExecutor` (`TP=4`), `ready_event`, and input/output daemon threads via `process_input_sockets`; main thread waits until all 4 cross-node input threads handshake, sends `ready` with metadata such as `num_gpu_blocks`, then all threads loop[^anatomy]:

- Input thread: block on input socket, decode routed request, `input_queue.put_nowait`, re-block.
- Main thread: `input_queue.get`, feed engine, run forward via `MultiProcExecutor`, `output_queue` results.
- Output thread: `output_queue.get`, send to API server, re-block.

Extra mechanics are DP wave counter (quiesce when idle, increment on new work), control messages beyond inference (aborts, utility/control RPCs), and dummy lockstep steps where idle replicas step to avoid blocking active ones; lockstep is strictly required for MoE EP/TP attention-DP patterns and currently always runs under DP, while non-MoE DP could instead use independent instances plus normal load balancing[^anatomy].

### API-server node

`AsyncLLM` asyncio wrapper creates `DPLBAsyncMPClient` (data-parallel, load-balancing, async, multiprocessing)[^anatomy]. Parent `MPClient.launch_core_engines` builds ZMQ handshake addresses, spawns `DPCoordinator`, and creates `CoreEngineProcManager`; `AsyncMPClient` adds `outputs_queue` plus `process_outputs_socket` draining all `DPEngineCoreProc` output threads, while `AsyncLLM` adds `output_handler` feeding `create_completion`; `DPAsyncMPClient` adds `run_engine_stats_update_task` talking to the coordinator[^anatomy]. Coordinator sends queue/waiting/running load info to the frontend, handles Ray-only `SCALE_ELASTIC_EP` resizing, and exchanges `START_DP_WAVE` events and wave-state updates[^anatomy]. Frontend runs concurrent asyncio tasks: per-client `generate` inputs, `process_outputs_socket` plus `output_handler` outputs, and coordinator polling/scaling[^anatomy]. Main process mounts FastAPI `OpenAIServingCompletion` / `OpenAIServingChat` (`/completion`, `/chat/completion`) on Uvicorn[^anatomy].

Full `curl -X POST http://localhost:8000/v1/completions` lifecycle[^anatomy]:

1. `OpenAIServingCompletion.create_completion` receives request.
2. Async tokenize plus request ID, sampling params, timestamp.
3. `AsyncLLM.generate` follows sync flow into `DPAsyncMPClient.add_request_async`.
4. `get_core_engine_for_request` picks least-loaded engine with `score = len(waiting) * 4 + len(running)` from coordinator state.
5. Send `ADD` to that engine's `input_socket`.
6. Engine input/main/output threads run `engine_core.step()` (including `MultiProcExecutor`) until stop.
7. `process_outputs_socket` plus `output_handler` propagate tokens to FastAPI.
8. FastAPI attaches finish reason, logprobs, usage, and returns `JSONResponse` via Uvicorn.

More API servers load-balance at OS/socket level without app change; Ray backend exposes `/scale_elastic_ep` for elastic replica scaling[^anatomy].

## Benchmarks and latency-throughput trade-off

Metrics are `TTFT` (submit to first token), `ITL` (token `i-1` to `i`), `TPOT` (mean ITL), end-to-end latency (`TTFT + sum(ITLs)` or submit to last token), throughput (input/output/total tokens or requests per second), and goodput (throughput meeting SLOs such as max TTFT/TPOT/e2e)[^anatomy]. Latency suits interactive use; throughput suits offline synthetic-data, cleaning/processing, and batch inference[^anatomy].

Simplified short-sequence model assumes weight I/O dominates KV I/O: shrinking batch `B` toward 1 lowers ITL with less per-step work and contention, while growing `B` raises ITL through more FLOPs but improves throughput until peak by amortizing weight I/O[^anatomy]. Roofline view uses saturation batch `B_sat`: below it HBM weight streaming dominates and step time is nearly flat (1 versus 10 tokens similar); above it kernels turn compute-bound and step time grows with `B`[^anatomy]. Rigorously, kernel auto-tuning changes achieved performance `P_kernel`, with step latency `t = FLOPs_step / P_kernel`; reaching `P_peak` makes extra compute directly raise latency[^anatomy].

`vllm bench {serve,latency,throughput}` wraps `benchmarks/{server,latency,throughput}.py`[^anatomy]:

- `latency`: short input (default 32 tokens), 128 outputs, small batch (default 8), repeated iterations reporting batch e2e latency.
- `throughput`: fixed prompts at once (default 1000 ShareGPT, `QPS=Inf`), reporting input/output/total tokens and requests per second.
- `serve`: launches a server, samples Poisson (or Gamma) inter-arrivals over a window, measures all metrics, optionally caps server concurrency with a semaphore (e.g. 64).

Example[^anatomy]:

```shell
vllm bench latency --model <model-name> --input-tokens 32 --output-tokens 128 --batch-size 8
```

CI benchmark configs live under `.buildkite/nightly-benchmarks/tests`; an auto-tune script drives `serve` to find settings meeting SLOs such as maximum throughput with p99 e2e under 500 ms[^anatomy].

## Out of scope in source

Skipped as orthogonal plugins to the main flow: diverse hardware (TPUs, AWS Neuron Trainium/Inferentia), MLA/MoE/encoder-decoder Whisper/pooling/EPLB/m-RoPE/LoRA/ALiBi/attention-free/sliding-window/multimodal/state-space Mamba/Mamba-2/Jamba, TP/PP/SP detail, Jenga hybrid KV logic, beam sampling, and experimental async scheduling[^anatomy].

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM.generate` versus `vllm serve` online paths bounding this lifecycle.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — `LLMEngine`, workers, runners, and `VllmConfig` hosting the init procedures above.
- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — API-server, engine-core, worker, and DP-coordinator counts underlying the distributed walkthrough.
- Uses [vLLM Paged Attention Kernel](vllm-paged-attention-kernel.md) — historical kernel-level counterpart to the block-table allocation compiled here.
- Uses [vLLM Chunked Prefill](vllm-chunked-prefill.md) — current default-on decode-prioritized chunking versus this source's threshold snapshot.
- Uses [vLLM Prefix Caching](vllm-prefix-caching.md) — full hash, allocation, free, eviction, and hybrid-manager detail behind the reuse sketch above.
- Uses [vLLM Structured Outputs](vllm-structured-outputs.md) — current constraint API succeeding this source's `GuidedDecodingParams` snapshot.
- Uses [vLLM N-Gram Speculative Decoding](vllm-ngram-speculative-decoding.md) — draft-free proposal method in the source's n-gram/EAGLE/Medusa trio.
- Uses [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE/Eagle3 draft-model counterpart to the source's speculation sketch.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — production connector catalog and abstractions behind the `SharedStorageConnector` walkthrough.
- Uses [vLLM Data Parallel Deployment](vllm-data-parallel-deployment.md) — internal/hybrid/external DP modes and MoE coordination behind the 2-node example.
- Uses [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — TP/PP selection, Ray/multiprocessing runtimes, and networking behind the scale-up discussion.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — current mode/dispatcher design behind the warmup-capture sketch above.
- Uses [vLLM Request Preemption](vllm-request-preemption.md) — V1 `RECOMPUTE` tuning and observability for the KV-shortage path above.
- Uses [Distributed Inference Core Concepts and Scaling Dimensions](distributed-inference-core-concepts.md) — prefill/decode trade-offs and KPI framing for the benchmark section.

## Coverage limits

- `assets/*.png` diagrams (constructor, engine loop, KV blocks, forward pass, chunked/prefix/FSM/spec-decode/P-D/multiproc/DP/server/latency/roofline figures) were not visually inspected; synthesis follows the post text and captions[^anatomy].
- Linked `basic.py` example, commit `42172ad` tree, V1 guide, deprecation issue, papers, `gpt-fast`, XGrammar, LMCache/NIXL, and contact/profile URLs were treated as identifiers and not fetched[^anatomy].

[^anatomy]: Aleksa Gordic, Inside vLLM: Anatomy of a High-Throughput LLM Inference System — `../raw/2025-09-05-anatomy-of-vllm/index.md` (vLLM blog, 2025-09-05; commit `42172ad` snapshot).
