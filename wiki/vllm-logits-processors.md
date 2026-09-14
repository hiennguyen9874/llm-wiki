---
type: Concept
title: vLLM Logits Processors
description: Stateful batch-granular logits transforms, BatchUpdate lifecycle, argmax-invariant sampling shortcut, and built-in versus custom extension model.
tags: [vllm, sampling, logits-processors]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:40:14Z }
sources:
  - id: logits-processors
    resource: ../raw/vllm/design/logits_processors.md
    title: Logits Processors
---

vLLM logits processors are stateful, batch-granular transforms on the `(num_requests) x (vocab_size)` model-output logits tensor before softmax, kept in sync with the persistent batch via `update_state(BatchUpdate)` each step and applied via `apply(logits)` inside the sampler, with argmax-invariant processors skipped when the whole batch is greedy-sampling[^logits-processors].

> [!important] API stability
> The source warns logits-processor design changes are still in progress and the API may change soon[^logits-processors].

## Background

A logits processor steers decoding by adjusting the next-token distribution. For requests that enable it, it rewrites that request's row of the logits tensor and leaves other rows unmodified[^logits-processors].

Each processor may keep per-request configuration, so it is stateful and must track adds, removals, and reordering as the persistent batch changes[^logits-processors].

## Engine lifecycle

Each engine step does two phases[^logits-processors]:

1. **Update state.** After the persistent batch reorganizes for scheduler output, `InputBatch.refresh_metadata()` builds a `BatchUpdate` and calls `logit_proc.update_state(batch_update)` for every loaded processor.
2. **Apply to logits.** After model forward, the sampler applies processors to the output logits. `apply()` may modify in place (more memory-efficient) or out of place.

`SamplingMetadata.logitsprocs` carries the processor lists from the persistent batch into the sampler; the sampler splits them into `non_argmax_invariant` (applied before `sample()`) and `argmax_invariant` (applied inside `sample()` after the all-greedy early-exit check)[^logits-processors].

## Argmax-invariant optimization

- **Argmax-invariant** (e.g. Min-P): never changes the highest-logit token ID, e.g. masking only lowest-probability tokens. Skippable for greedy sampling, which always picks the argmax[^logits-processors].
- **Non-argmax-invariant** (e.g. forcing EOS after N steps): may mask the max-logit token and change the argmax, so it cannot be skipped for greedy requests[^logits-processors].

Because the abstraction is batch-granular, argmax-invariant processors are only skipped when the *entire* batch uses greedy sampling[^logits-processors].

## `LogitsProcessor` programming model

Subclass `LogitsProcessor` (`vllm/v1/sample/logits_processor/interface.py`) and implement[^logits-processors]:

| Method | Contract |
|---|---|
| `__init__(vllm_config, device, is_pin_memory)` | Receive engine config, accelerator device, and pin-memory flag. |
| `apply(logits) -> Tensor` | Transform `(num_requests) x (vocab_size)` tensor at batch granularity. |
| `is_argmax_invariant() -> bool` | Whether the processor never changes argmax; evaluated once at startup to enable the greedy skip. May be hard-coded or computed per instance. |
| `update_state(batch_update \| None)` | Reconcile internal state with batch changes; `None` means no membership/reorder change, but `output_token_ids` references may still have grown. |
| `validate_params(sampling_params)` (classmethod) | Raise `ValueError` on invalid `SamplingParams`; entrypoints use it to refuse bad requests. |

## `BatchUpdate` data structure

```python
@dataclass(frozen=True)
class BatchUpdate:
    batch_size: int
    removed: Sequence[int]  # RemovedRequest
    added: Sequence[AddedRequest]  # (index, SamplingParams, prompt_tok_ids, output_tok_ids)
    moved: Sequence[MovedRequest]  # (src, dst, UNIDIRECTIONAL | SWAP)
```

Semantics[^logits-processors]:

- **Remove `i`:** discard request at `i`, leaving an empty slot.
- **Add `(i, params, prompt_ids, output_ids)`:** place or replace request at `i`; out-of-bounds `i` extends the batch. `output_tok_ids` is passed by reference, so growth each step is visible to the processor — important for history-dependent processors. Subclasses digest only the fields they need.
- **Move `(s, d, directionality)`:** `UNIDIRECTIONAL` moves `s -> d`, leaving `s` empty and discarding any occupant of `d`; `SWAP` exchanges `s` and `d`.
- `batch_size` is the persistent-batch size at the start of the step.

`update_state()` must process operations in order: removes, then adds, then moves in listed order. Add indices refer to the time of the add, before moves[^logits-processors].

## How the engine builds `BatchUpdate`

Assumed runner model[^logits-processors]:

1. Identify finished and new requests.
2. Replace finished slots with new requests in increasing index order from the lowest finished index.
3. If counts match, done. If more new than finished, extend the batch with consecutive indices from `max_index+1`. If fewer new than finished, remove unreplaced finished indices (necessarily above the replaced ones), then condense by moving the highest non-empty slot into the lowest empty slot with `UNIDIRECTIONAL` moves until contiguous, then shrink `batch_size` so trailing empties fall outside the batch.
4. Optionally apply `SWAP` moves to reorder for attention-backend efficiency.

If there are no new/finished requests and no reordering, the update is `None`[^logits-processors].

Example — fewer new than finished (`[A,B,C,D]`, finish `A,C`, add `E`, then swap `0<->1`): add `E@0` → remove `@2` → unidirectional move `3->2` and shrink to size 3 → swap `0<->1`, yielding `added=[(0,E,...)]`, `removed=[2]`, `moved=[(3,2,UNIDIRECTIONAL),(0,1,SWAP)]`[^logits-processors].

Example — more new than finished (`[A,B,C,D]`, finish `C`, add `E,F`, then swap `0<->1`): add `E@2` → add `F@4` extending batch to size 5 → swap `0<->1`, yielding `added=[(2,E,...),(4,F,...)]`, `removed=[]`, `moved=[(0,1,SWAP)]`; no condensation because removes left no holes[^logits-processors].

## Authoring guidance

- Prefer vectorized `apply()` / `update_state()` over the whole batch; for rarely used processors consider sparse per-request dicts storing only enabled requests[^logits-processors].
- Decide per-request configuration attributes (possibly new `SamplingParams`/API fields), per-request enable/disable conditions (e.g. default `None` or no-op value), and batch-level short-circuits (return input unmodified when no running request enables the processor; early-exit `update_state` on `None`)[^logits-processors].
- Always discard state for requests replaced by an add or hit by a remove[^logits-processors].

Built-ins are always loaded; current examples using this model are Min-P, logit bias, and min-tokens (see `vllm/v1/sample/logits_processor/builtin.py`)[^logits-processors].

Still hard-coded in the sampler and pending refactor to this model: allowed token IDs, bad words, repetition/frequency/presence penalties, temperature, top-k, and top-p[^logits-processors].

Custom out-of-tree processors subclass the same `LogitsProcessor` base and are covered separately in `raw/vllm/features/custom_logitsprocs.md` (not ingested here)[^logits-processors].

## Coverage limits

- `builtin.py` implementations and the custom-processor feature doc were not ingested; only referenced for extension context[^logits-processors].
- Pseudocode paths (`gpu_model_runner.py`, `gpu_input_batch.py`, `sampler.py`, `interface.py`) are as quoted in the source, not verified against the tree.

## Relationships

- Uses [vLLM Model Runner V2](vllm-model-runner-v2.md) — persistent-batch reorganization, `SamplingMetadata` handoff, and sampler invocation are the execution context for `update_state()` / `apply()`, including its per-logit index-mapping note for sampling state.

[^logits-processors]: Logits Processors — `../raw/vllm/design/logits_processors.md`, covering batch-granular semantics, `update_state`/`apply` lifecycle, argmax-invariant skipping, `LogitsProcessor`/`BatchUpdate` interfaces, batch-construction model with worked examples, and built-in versus custom guidance.
