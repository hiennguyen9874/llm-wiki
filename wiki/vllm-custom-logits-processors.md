---
type: Concept
title: vLLM Custom Logits Processors
description: Authoring, loading, and invoking out-of-tree logits processors, including Adapter wrapping and FQCN, entry-point, and class-object loading.
tags: [vllm, sampling, logits-processors]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:05:35Z }
sources:
  - id: custom-logitsprocs
    resource: ../raw/vllm/features/custom_logitsprocs.md
    title: Custom Logits Processors
---

A custom logits processor is user-written code loaded into vLLM at initialization without modifying or recompiling vLLM source, the opposite of a built-in processor[^custom-logitsprocs].

Like built-ins, it operates at batch granularity on a `(num_requests) x (vocab_size)` logits tensor: it rewrites rows for requests that enable it, leaves other rows unmodified, and returns the tensor for softmax[^custom-logitsprocs].

> [!important] API stability
> The source warns logits-processor design changes are still in progress and this API may change soon[^custom-logitsprocs].

## Authoring contract

Subclass `vllm.v1.sample.logits_processor.LogitsProcessor` and implement[^custom-logitsprocs]:

| Method | Contract |
|---|---|
| `validate_params(sampling_params)` (classmethod) | Raise `ValueError` on invalid `SamplingParams`, especially custom arguments; entrypoints refuse bad requests. Required to avoid unexpected behaviour from invalid parameters. |
| `__init__(vllm_config, device, is_pin_memory)` | Receive engine `VllmConfig`, accelerator `torch.device`, and pin-memory flag. |
| `apply(logits) -> Tensor` | Transform batch-granular `(num_requests) x (vocab_size)` tensor; in-place is more memory-efficient, out-of-place is allowed. |
| `is_argmax_invariant() -> bool` | Whether the processor never changes the argmax token ID; evaluated once at startup so vLLM can skip it when all requests use greedy sampling. May be hard-coded or computed per instance. |
| `update_state(batch_update \| None)` | Reconcile internal state with persistent-batch changes; `None` means no membership/reorder change, but retained `output_token_ids` references may still have grown. |

`update_state()` must process operations in order: removes, then adds, then moves in listed order[^custom-logitsprocs]. Add indices refer to the time of the add, before moves; moves are applied after adds/removes in listed order[^custom-logitsprocs].

The full batch-construction model — replace finished slots in increasing index order, extend with consecutive indices when new outnumber finished, remove/condense/shrink plus optional swap-reorder when finished outnumber new — is maintained in [vLLM Logits Processors](vllm-logits-processors.md); the source notes this section may become irrelevant once processors no longer need to account for batch-state changes[^custom-logitsprocs].

## Per-request configuration

Unlike built-ins, custom processors may need arguments not hard-coded into `SamplingParams` or the REST API[^custom-logitsprocs]. They may use pre-existing `SamplingParams` fields or leverage [vLLM Custom Arguments](vllm-custom-arguments.md) via `SamplingParams.extra_args` / `vllm_xargs`[^custom-logitsprocs].

The worked `DummyLogitsProcessor` example masks all tokens except one `target_token` with `float('-inf')`, enabled only when the request supplies integer `target_token` in `extra_args`; it validates the type in `validate_params`[^custom-logitsprocs].

Its `update_state()` keeps a sparse `req_info: dict[int, int]` holding only enabled requests, adjusting keys/values for adds, popping removed indices, and remapping moved indices while respecting unidirectional versus `SWAP` directionality[^custom-logitsprocs]. Its `apply()` early-returns the input when `req_info` is empty, otherwise saves target values, masks selected rows to `-inf`, and restores the kept values[^custom-logitsprocs].

## Wrapping a request-level processor

vLLM v0-style request-level `Callable` processors of the form `(output_ids, logits) -> logits` or `(prompt_ids, output_ids, logits) -> logits` are explicitly not supported by the engine, but can be wrapped by subclassing `AdapterLogitsProcessor`[^custom-logitsprocs]. Non-conforming interfaces need an extra wrapper layer first[^custom-logitsprocs].

Override[^custom-logitsprocs]:

- `validate_params(params)` — validate sampling parameters.
- `is_argmax_invariant()` — accurately report whether the wrapped processor may change the max-logit token.
- `new_req_logits_processor(params) -> Optional[RequestLogitsProcessor]` — build a per-request `Callable` from `SamplingParams`, or return `None` to disable the processor for that request.

The `AdapterLogitsProcessor` base maintains the sparse request-state dictionary, disables requests returning `None`, applies the wrapped callable row-by-row and assembles the output tensor, and implements the batch short-circuit, early-exit-on-`None`, and finished-request discard optimizations by default[^custom-logitsprocs]. Re-implement as a direct `LogitsProcessor` subclass with vectorized batch operations only if the sequential default `apply()` is too slow[^custom-logitsprocs].

## Loading

The loaded set is fixed at initialization: it cannot change after the engine finishes loading, and processors cannot be loaded on demand for individual requests[^custom-logitsprocs].

| Method | Scope | Mechanism |
|---|---|---|
| 1. Fully-qualified class name (FQCN) | Offline + online | Pass `dotted.path.to.module:ClassName` to `LLM` / `AsyncLLM` `logits_processors` or `vllm serve ... --logits_processors <proc1> <proc2> ...`; `importlib.import_module()` must resolve the module, the class must be importable from it, and the target must subclass `LogitsProcessor`[^custom-logitsprocs]. |
| 2. Python entry-point auto-detection | Offline + online | Expose each processor under group `vllm.logits_processors`, e.g. `dummy_logits_processor = "your.module.path:DummyLogitsProcessor"` in `pyproject.toml` `[project.entry-points."vllm.logits_processors"]`; vLLM always loads all installed processors in this group with no explicit constructor/CLI passing[^custom-logitsprocs]. |
| 3. Class object | Offline-only | Pass the class object to `LLM` / `AsyncLLM` `logits_processors`, either imported or defined locally in the same file[^custom-logitsprocs]. |

## Invoking per request

Whether a processor needs explicit enablement and which arguments configure it are determined by its own design[^custom-logitsprocs]. For `DummyLogitsProcessor`, clients supply `target_token` to enable and steer it[^custom-logitsprocs]:

- REST: `"vllm_xargs": {"target_token": 67}` in `/v1/completions` JSON.
- OpenAI SDK: `extra_body={"vllm_xargs": {"target_token": 67}}`.
- Offline `LLM`: `SamplingParams(..., extra_args={"target_token": 67})`.
- Offline `AsyncLLM`: `sampling_params=SamplingParams(..., extra_args={"target_token": 67})` in `engine.generate()`.

## Efficiency best practices

`update_state()` and `apply()` run every engine step over the persistent batch, so both must be efficient[^custom-logitsprocs]:

- Prefer vectorized batch operations; use a sparse per-request dict when the processor is infrequently enabled[^custom-logitsprocs].
- Define per-request configuration attributes (how `SamplingParams` maps to state), per-request enable/disable conditions (e.g. default `None` or a no-op value, saving compute/memory for disabled requests), and batch-level short-circuits (return input unmodified when no running request enables the processor; exit `update_state` early on `None`)[^custom-logitsprocs].
- Always discard state for finished requests — those replaced by an add or hit by a remove[^custom-logitsprocs].

## Coverage limits

- Example implementations are summarized for their state-mapping and masking patterns; the quoted Python was not executed or verified against the tree[^custom-logitsprocs].
- `BatchUpdate` construction detail is referenced from [vLLM Logits Processors](vllm-logits-processors.md) rather than re-derived here[^custom-logitsprocs].

## Relationships

- Uses [vLLM Logits Processors](vllm-logits-processors.md) — base batch-granular lifecycle, `BatchUpdate` construction model, and argmax-invariant greedy skip.
- Uses [vLLM Custom Arguments](vllm-custom-arguments.md) — `extra_args` / `vllm_xargs` channel for per-request processor configuration validated by `validate_params`.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM` / `AsyncLLM` versus online `vllm serve` loading and invocation paths.
- Uses [vLLM Plugin System](vllm-plugin-system.md) — entry-point discovery parallels plugin loading, but logits-processor auto-loading uses the distinct always-load `vllm.logits_processors` group.

[^custom-logitsprocs]: Custom Logits Processors — `../raw/vllm/features/custom_logitsprocs.md`, covering custom versus built-in definition, `LogitsProcessor` subclass contract, `BatchUpdate` handling model, custom-argument configuration, `DummyLogitsProcessor` sparse example, `AdapterLogitsProcessor` request-level wrapping, FQCN/entry-point/class-object loading, per-request invocation, and efficiency best practices.
