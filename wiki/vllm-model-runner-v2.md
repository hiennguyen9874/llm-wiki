---
type: Concept
title: vLLM Model Runner V2
description: Cleaner, async-first, GPU-native reimplementation of the vLLM model runner with decoupled persistent batches, staged writes, Triton sampling, and explicit CUDA-graph management.
tags: [vllm, model-runner, async, sampling, cuda-graphs]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T00:00:00Z }
sources:
  - id: mrv2
    resource: ../raw/vllm/design/model_runner_v2.md
    title: Model Runner V2 Design Document
---

Model Runner V2 (MRV2) is a from-first-principles rewrite of the vLLM model runner intended to be cleaner, more efficient, and more modular than V1 by assuming async execution, keeping bulk state on GPU, and moving input preparation and sampling into GPU/Triton kernels[^mrv2].

## Motivation and status

- V1 accumulated fundamental design mistakes and technical debt as features were bolted on without being in the original design[^mrv2].
- Newer insights — sampling techniques such as Gumbel-max sampling, Triton, and CUDA features such as UVA — motivated a rewrite rather than another retrofit[^mrv2].
- Per the source, MRV2 is a substantial improvement over V1 but is not yet feature-complete, not rigorously tested, and still has open design decisions[^mrv2].

## Persistent batch

- V1 introduced persistent batches to avoid rebuilding large contiguous input tensors (for example block tables and per-request temperatures) from scratch in Python each step, instead applying incremental diffs because consecutive-step batches are mostly identical[^mrv2].
- V1's problem was coupling persistent state tensors directly to model and sampler inputs, imposing strict layout and ordering requirements, forcing complex tensor-wide reordering when requests join or finish, requiring a redundant `CachedRequestState` backup because persistent rows could be overwritten while requests were still active, and complicating async scheduling[^mrv2].
- MRV2 decouples persistent state from per-step inputs: it pre-allocates fixed-size tensors with `max_num_reqs` rows (1024 by default on most platforms), assigns each request a permanent row for its active lifetime, treats preemption as completion (re-adding resumed request data as fresh state), and gathers per-step inputs on GPU in the order requested (usually set by the attention backend), removing `CachedRequestState` and simplifying bookkeeping at low GPU gather cost[^mrv2].

## Async-first execution

- vLLM overlaps CPU and GPU work by having the scheduler and worker prepare inputs for step `N+1` while the GPU executes step `N`; V1 gained this through retrofitted behavior and hacks, while MRV2 assumes from the start that the core model execution loop is a CUDA stream with no CPU synchronization points and that CPU entrypoints only queue work onto the stream[^mrv2].

## Removing the async barrier

- Async execution requires avoiding both explicit synchronization (for example `torch.accelerator.synchronize`) and implicit synchronization (for example unpinned `.to("cuda")`); the unsafe pattern is CPU writes to a pinned buffer racing with an in-flight async GPU copy from that same buffer[^mrv2].
- V1's async barrier around critical sections avoids the race but is bug-prone (easy to miss a protected buffer), inflexible (all CPU work must stay inside the barrier), and can reduce overlap[^mrv2].
- MRV2 eliminates the race structurally: persistent CPU state stays unpinned while each step copies through a temporary `pin_memory()` buffer, so the CPU writes to `self.states` while the GPU reads from the temporary `tmp_states`, with no explicit synchronization[^mrv2].

## StagedWriteTensor

- For large tensors such as block tables, MRV2 avoids full CPU-to-GPU copies each step: the base tensor lives on GPU, diffs are staged on CPU, packed into contiguous buffers, copied to GPU, and applied with one kernel launch[^mrv2].
- The API sketch is `StagedWriteTensor(size, dtype, device)` plus `stage_write(row, start, value)` and `apply_write()`; it supports ragged updates with no CPU-GPU synchronization and minimal kernel launches, and is also used for mixed CPU/GPU-written state such as `num_computed_tokens`[^mrv2].

## GPU-native input preparation and UVA

- MRV2 prepares inputs such as `input_ids`, `positions`, `query_start_loc`, and `seq_lens` with Triton kernels, which improves async behavior (the GPU can derive values the CPU may not yet know, for example under speculative decoding) and lowers CPU overhead by avoiding Python bottlenecks[^mrv2].
- In some paths MRV2 uses Universal Virtual Addressing (UVA) so GPU kernels directly access large CPU-resident tensors such as `prefill_token_ids` without duplicating them into GPU memory[^mrv2].

## Triton-native sampler

- MRV2 reimplements sampling mostly in Triton for better numeric and memory control[^mrv2].
- A Triton Gumbel sampling kernel avoids explicit softmax materialization and uses stateless in-kernel RNG from a seed input[^mrv2].
- Efficient top-k logprobs: where V1 materializes full-vocabulary logprobs before top-k, MRV2 identifies top-k tokens from logits first and computes logprobs only for the selected tokens, reducing peak GPU memory[^mrv2].
- Memory-efficient prompt logprobs support finer-grained chunking, including chunking inside a single prompt, to avoid memory spikes on long prompts[^mrv2].
- For speculative decoding, MRV2 uses `idx_mapping` indirection inside kernels to map each logits vector to the right request state instead of expanding per-request sampling states to per-logit shapes, simplifying complex sampling parameters and logits processors[^mrv2].

## Modularity

- Against V1's large entangled `gpu_model_runner.py`, MRV2 splits feature logic across dedicated files (for example `mrope_utils.py` and `penalties.py`), consolidates model inputs into an `InputBatch` class, and reduces direct model-runner attribute coupling[^mrv2].

## No abuse of `dummy_run`

- In V1, `dummy_run` absorbed too many jobs: initial memory profiling and `torch.compile`, CUDA-graph capture, warmups, and empty data-parallel forward passes for expert-parallel plus data-parallel (EP+DP)[^mrv2].
- MRV2 simplifies this: `execute_model` supports dummy runs without affecting state, `dummy_run` delegates to `execute_model` for profiling, warmup, and empty DP forward passes, and CUDA-graph capture uses a separate dedicated path — reducing complexity and bugs from `execute_model` / `dummy_run` divergence[^mrv2].

## Explicit CUDA-graph management

- V1's CUDA-graph handling is implicit and hard to reason about; MRV2 introduces a `CUDAGraphManager` that explicitly captures and launches full CUDA graphs through standard PyTorch APIs, making lifecycle and execution-mode decisions clearer and easier to extend — for example, capturing multiple draft-model forward passes into one CUDA graph[^mrv2].

## Fused multi-step draft decoding

- Autoregressive speculative decoding runs several dependent draft steps per scheduler step; the fused path captures all post-prefill draft steps in one full CUDA graph instead of replaying a separate graph per draft token, building attention metadata once before the loop while step-dependent tensors keep stable addresses and are updated in place between draft steps[^mrv2].
- Attention backends with derived state (for example scheduler metadata or sparse indices) must implement `AttentionMetadataBuilder.update_draft_decode_metadata()` before opting in; the hook runs during CUDA-graph capture, so only the GPU operations it issues are recorded and replayed while its Python body is not rerun — implementations must therefore be capture-safe and keep replayed tensor state in persistent storage[^mrv2].
- The fused path is enabled only when every draft attention group declares `supports_draft_decode_metadata_update`; otherwise MRV2 falls back to rebuilding attention metadata between draft steps, while draft models with fixed positions do not need the update; developers must audit all derived metadata, including state inherited from parent builders or owned by auxiliary attention backends, before enabling a backend[^mrv2].

## Development philosophy

- MRV2 changes should meet a higher code-quality bar: as V1 feature gaps are filled, features should be reconsidered from first principles in the MRV2 design context rather than quickly ported, preserving modularity and clean abstraction boundaries even at the cost of more upfront design iteration[^mrv2].

## Coverage limits

- Five referenced diagrams (`persistent_batch_v1.png`, `persistent_batch_mrv2.png`, `async_sched.png`, `async_race_condition.png`, `async_no_race_condition.png`) are absent from `raw/` and were not inspected; the gather/barrier/timeline claims above rest on the design-doc prose and code sketches[^mrv2].
- The source itself marks MRV2 as incomplete, under-tested, and subject to open design decisions, so implementation details may have changed since this document revision[^mrv2].

## Relationships

- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — MRV2 is the next-generation implementation of the per-worker model-runner role described there.

[^mrv2]: Model Runner V2 Design Document — `../raw/vllm/design/model_runner_v2.md`.
