---
type: Concept
title: vLLM Hidden State Extraction
description: Saving intermediate target-model layer activations to .safetensors via method extract_hidden_states for EAGLE-style training, distillation, and analysis.
tags: [vllm, speculative-decoding, hidden-states]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: extract-hidden-states
    resource: ../raw/vllm/features/speculative_decoding/extract_hidden_states.md
    title: Hidden State Extraction
  - id: extract-hidden-states-blog
    resource: ../raw/2026-03-30-extract-hidden-states/index.md
    title: Extracting hidden states from vLLM
---

vLLM saves intermediate target-model layer activations during inference for training EAGLE-style draft models, knowledge distillation, or offline analysis of model internals, configured as `speculative_config` with `method: extract_hidden_states` plus a `kv_producer` hidden-states connector[^extract-hidden-states].

The native system was introduced in PR [#33736](https://github.com/vllm-project/vllm/pull/33736) in `vllm>=v0.18.0` to replace `transformers`-based generation and patched vLLM setups for speculator training data[^extract-hidden-states-blog].

## Configuration

Select layers with `draft_model_config.hf_config.eagle_aux_hidden_state_layer_ids`, and sink files with `KVTransferConfig` using `kv_connector: ExampleHiddenStatesConnector` and `kv_role: kv_producer`[^extract-hidden-states]:

```python
llm = LLM(
    model="Qwen/Qwen3-8B",
    speculative_config={
        "method": "extract_hidden_states",
        "num_speculative_tokens": 1,
        "draft_model_config": {
            "hf_config": {
                "eagle_aux_hidden_state_layer_ids": [1, 2, 3, 4],
            },
        },
    },
    kv_transfer_config=KVTransferConfig(
        kv_connector="ExampleHiddenStatesConnector",
        kv_role="kv_producer",
        kv_connector_extra_config={"shared_storage_path": tmpdir},
    ),
)
```

Passing `num_hidden_layers` as a layer id saves the last layer's output hidden states; these are not normalized with the output norm[^extract-hidden-states].

## Offline and online paths

Offline (`LLM.generate`), the output carries the file location in `output.kv_transfer_params["hidden_states_path"]`; read it with `load_hidden_states()` from the connector module, which returns `token_ids` and `hidden_states` tensors[^extract-hidden-states].

Online (`vllm serve`)[^extract-hidden-states]:

```bash
vllm serve Qwen/Qwen3-8B \
    --speculative_config '{"method": "extract_hidden_states", "num_speculative_tokens": 1, "draft_model_config": {"hf_config": {"eagle_aux_hidden_state_layer_ids": [1, 2, 3, 4]}}}' \
    --kv_transfer_config '{"kv_connector": "ExampleHiddenStatesConnector", "kv_role": "kv_producer", "kv_connector_extra_config": {"shared_storage_path": "/dev/shm/hidden_states"}}'
```

For online use prefer a RAM-mounted filesystem such as `/dev/shm/` where the client cleans up files soon after generation[^extract-hidden-states].

## Per-request options

Both modes accept per-request `kv_transfer_params`[^extract-hidden-states]:

| Parameter | Default | Description |
| --- | --- | --- |
| `hidden_states_path` | Auto-generated as `<shared_storage_path>/<request_id>.safetensors` | Custom save path; requires `allow_custom_save_path` on the server |
| `include_output_tokens` | `False` | When `True`, save prompt plus generated tokens; when `False`, prompt tokens only |

Offline passes them through `SamplingParams.extra_args`; online passes `kv_transfer_params` as a top-level API field[^extract-hidden-states]:

```python
SamplingParams(
    max_tokens=32,
    extra_args={
        "kv_transfer_params": {
            "hidden_states_path": "/tmp/my_output.safetensors",
            "include_output_tokens": True,
        }
    },
)
```

## Server options

`kv_connector_extra_config` accepts[^extract-hidden-states]:

| Parameter | Default | Description |
| --- | --- | --- |
| `shared_storage_path` | `/tmp` | Save directory when no per-request path is set |
| `allow_custom_save_path` | `False` | Honor client `hidden_states_path`; when disabled custom paths are ignored with a warning |
| `num_writer_threads` | `8` | Thread pool size for async disk writes |
| `use_synchronization_lock` | `True` | File-lock readers until writes complete; may be disabled for batch generation without synchronization needs |

Enable `allow_custom_save_path` only with trusted clients because custom paths can write to arbitrary server locations[^extract-hidden-states].

## Output format

Each request produces one `.safetensors` file with `hidden_states` of shape `[num_tokens, num_extracted_layers, hidden_size]` and `token_ids` of shape `[num_tokens]`; use `load_hidden_states()` for synchronized reads[^extract-hidden-states].

Chunked prefill is incompatible with this feature and must be disabled[^extract-hidden-states].

## Why native extraction

Hidden states are the verifier model's intermediate per-token representations; Eagle-3, P-Eagle, DFlash, and similar draft models take hidden states from multiple verifier layers as input, so training them needs large datasets of hidden states plus verifier outputs[^extract-hidden-states-blog]. Speculative decoding pairs the large verifier with a small draft model whose proposals the verifier checks in parallel, with reported 2–5× speedups in memory-bound low-batch scenarios[^extract-hidden-states-blog].

Two pre-native paths had durable costs[^extract-hidden-states-blog]:

- `transformers`-based generation lost vLLM optimizations such as large-model and distributed support and risked subtle hidden-state mismatches with vLLM.
- Patched vLLM setups that called internals directly carried maintenance burden across vLLM updates and disabled prefix caching, auto-batching, and async serving; this was how Speculators `<0.5.0` generated hidden states.

## Design

Hidden states are large: a Qwen3-8B example with `hidden_size` 4096, 8k tokens, 4 extracted layers, and FP16 totals about 268 MB with shape `[seq_len, num_layers_to_extract, 4096]`, so returning them inline in the response body is impractical[^extract-hidden-states-blog]. The design therefore required pre-allocated VRAM management across concurrent requests including chunked prefill and preemption, zero hot-path overhead when extraction is off by reusing existing features, and extensible offline (cache full dataset to disk) versus online (stream to training without disk) sinks[^extract-hidden-states-blog].

The implementation reuses Eagle-3 hidden-state plumbing plus the KV Connector API already used for prefill/decode disaggregation, which supports NIXL, disk, and shared-memory sinks with async transfer and holds KV blocks until transfers complete[^extract-hidden-states-blog]. Because hidden states map to input tokens like KV cache entries (one value per token, valid only for its prefix), the mechanism is[^extract-hidden-states-blog]:

1. A dummy draft model receives verifier hidden states through the existing Eagle-3 path.
2. Its dummy attention layer skips attention and inserts the hidden-states input directly into its own KV cache.
3. A custom KV Connector persists or transfers that dummy KV cache content.

Storing hidden states in dummy attention layers lets vLLM allocate VRAM and reuse paged-memory machinery for prefix caching, chunked prefill, and batching; the design diagram in the source shows verifier layers feeding the dummy Eagle-3 model, then `FakeAttentionLayer` KV cache, then KV Cache Connector to disk or NCCL toward the training process[^extract-hidden-states-blog].

## History and limits at introduction

At introduction only the disk-writing `ExampleHiddenStatesConnector` existed, with blocking writes and active work toward async writes; the `speculative_config` plus `kv_transfer_config` pair had to be used together[^extract-hidden-states-blog]. Single-node `--tensor-parallel-size` and `--data-parallel-size` were supported, only prompt tokens and their hidden states were saved (hence the `v1/completions` with `max_tokens=1` recommendation), and future work targeted device-to-device connectors including multi-node transfer[^extract-hidden-states-blog]. Speculators [PR #353](https://github.com/vllm-project/speculators/pull/353) moved that library onto this native system and enabled online training, planned for `speculators v0.5.0`[^extract-hidden-states-blog]. Later per-request `include_output_tokens`, async writer threads, file locking, and custom-path controls are documented above and supersede the prompt-only limit where enabled.

> Coverage limit: the source points to a complete offline example at `examples/features/speculative_decoding/extract_hidden_states_offline.py`; that example file was not present in `raw/` and was not inspected, so details beyond the in-source snippet are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — extraction runs on the offline `LLM` class or the online `vllm serve` server with the same `speculative_config` / `kv_transfer_config` shape.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — extracted `eagle_aux_hidden_state_layer_ids` activations are the training input for EAGLE-style draft models.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — both select behavior through `speculative_config.method`, but this method produces hidden-state files rather than draft verification.
- Uses [vLLM Custom Arguments](vllm-custom-arguments.md) — offline per-request `kv_transfer_params` travel inside `SamplingParams.extra_args`.
- Related to [vLLM Speculators Library](vllm-speculators.md) — native extraction replaced Speculators `<0.5.0` patched generation and enabled online training from `speculators v0.5.0` onward.
- Uses [vLLM Disaggregated Prefill](vllm-disaggregated-prefill.md) — extraction reuses the same KV Connector transfer machinery used for disaggregated KV movement.

[^extract-hidden-states]: Hidden State Extraction — `../raw/vllm/features/speculative_decoding/extract_hidden_states.md`, `extract_hidden_states` speculative plus `ExampleHiddenStatesConnector` producer configuration, offline and online examples, per-request `hidden_states_path` and `include_output_tokens`, server `shared_storage_path`, `allow_custom_save_path`, `num_writer_threads`, and `use_synchronization_lock`, `.safetensors` `hidden_states` / `token_ids` shapes and `load_hidden_states()` reader, unnormalized last-layer note, `/dev/shm` recommendation, custom-path trust warning, and chunked-prefill incompatibility.
[^extract-hidden-states-blog]: Fynn Schmitt-Ulms, Extracting hidden states from vLLM — `../raw/2026-03-30-extract-hidden-states/index.md` (vLLM blog, 2026-03-30), PR #33736 / `v0.18.0` motivation, Eagle-3 / P-Eagle / DFlash multi-layer requirement, `transformers` versus patching costs, 268 MB sizing example, dummy Eagle-3 plus `FakeAttentionLayer` KV-cache plus KV Connector mechanism with design diagram inspected, offline versus online sinks, single-node TP/DP and prompt-only limits, and Speculators PR #353 / v0.5.0 plus async and device-to-device future work.
