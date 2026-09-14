---
type: Concept
title: vLLM Hidden State Extraction
description: Saving intermediate target-model layer activations to .safetensors via method extract_hidden_states for EAGLE-style training, distillation, and analysis.
tags: [vllm, speculative-decoding, hidden-states]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T14:00:00Z }
sources:
  - id: extract-hidden-states
    resource: ../raw/vllm/features/speculative_decoding/extract_hidden_states.md
    title: Hidden State Extraction
---

vLLM saves intermediate target-model layer activations during inference for training EAGLE-style draft models, knowledge distillation, or offline analysis of model internals, configured as `speculative_config` with `method: extract_hidden_states` plus a `kv_producer` hidden-states connector[^extract-hidden-states].

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

> Coverage limit: the source points to a complete offline example at `examples/features/speculative_decoding/extract_hidden_states_offline.py`; that example file was not present in `raw/` and was not inspected, so details beyond the in-source snippet are not compiled here.

## Relationships

- Uses [vLLM Entrypoints](vllm-entrypoints.md) — extraction runs on the offline `LLM` class or the online `vllm serve` server with the same `speculative_config` / `kv_transfer_config` shape.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — extracted `eagle_aux_hidden_state_layer_ids` activations are the training input for EAGLE-style draft models.
- Related to [vLLM Draft-Model Speculative Decoding](vllm-draft-model.md) — both select behavior through `speculative_config.method`, but this method produces hidden-state files rather than draft verification.
- Uses [vLLM Custom Arguments](vllm-custom-arguments.md) — offline per-request `kv_transfer_params` travel inside `SamplingParams.extra_args`.

[^extract-hidden-states]: Hidden State Extraction — `../raw/vllm/features/speculative_decoding/extract_hidden_states.md`, `extract_hidden_states` speculative plus `ExampleHiddenStatesConnector` producer configuration, offline and online examples, per-request `hidden_states_path` and `include_output_tokens`, server `shared_storage_path`, `allow_custom_save_path`, `num_writer_threads`, and `use_synchronization_lock`, `.safetensors` `hidden_states` / `token_ids` shapes and `load_hidden_states()` reader, unnormalized last-layer note, `/dev/shm` recommendation, custom-path trust warning, and chunked-prefill incompatibility.
