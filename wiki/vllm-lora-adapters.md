---
type: Concept
title: vLLM LoRA Adapters
description: Per-request LoRA serving offline and online, including static serving, dynamic loading, MoE format mixing, lineage, multimodal defaults, and tuning.
tags: [vllm, lora, serving]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:12:47Z }
sources:
  - id: lora-feature
    resource: ../raw/vllm/features/lora.md
    title: LoRA Adapters
---

vLLM serves LoRA adapters per request with minimal overhead on any model implementing `SupportsLoRA`, both offline via `LoRARequest` and online via the OpenAI-compatible server with static, dynamic, and resolver-based loading[^lora-feature].

## Offline per-request use

Download the adapter locally, enable LoRA on the `LLM` class, then pass a `LoRARequest(name, unique_id, path)` to `llm.generate`[^lora-feature]:

```python
from vllm import LLM, SamplingParams
from vllm.lora.request import LoRARequest

llm = LLM(model="meta-llama/Llama-3.2-3B-Instruct", enable_lora=True)
outputs = llm.generate(
    prompts,
    sampling_params,
    lora_request=LoRARequest("sql_adapter", 1, sql_lora_path),
)
```

The three `LoRARequest` fields are human-readable name, globally unique adapter ID, and local adapter path[^lora-feature].

## Static online serving

Start the server with LoRA enabled and declare each module[^lora-feature]:

```bash
vllm serve meta-llama/Llama-3.2-3B-Instruct \
  --enable-lora \
  --lora-modules sql-lora=jeeejeee/llama32-3b-text2sql-spider
```

The server accepts shared LoRA configuration such as `max_loras`, `max_lora_rank`, and `max_cpu_loras`[^lora-feature]. `/v1/models` lists the base model plus each LoRA name, and clients select an adapter through the normal `model` request field[^lora-feature]. Base-model and multiple-LoRA requests run in parallel when `max_loras` permits[^lora-feature].

## Dynamic runtime updating

Setting `VLLM_ALLOW_RUNTIME_LORA_UPDATING=True` enables loading and unloading adapters without restart[^lora-feature]:

```bash
export VLLM_ALLOW_RUNTIME_LORA_UPDATING=True
```

This carries security risk and should be used only in an isolated, fully trusted environment[^lora-feature].

- Load: `POST /v1/load_lora_adapter` with `lora_name` and `lora_path`; success returns `200 OK` plus `Success: LoRA adapter '<name>' added successfully`[^lora-feature].
- Unload: `POST /v1/unload_lora_adapter` with `lora_name`; success returns `200 OK` plus `Success: LoRA adapter '<name>' removed successfully`[^lora-feature].
- In-place reload: pass `load_inplace: true` to `/v1/load_lora_adapter` to replace an existing same-name adapter with new weights without interrupting inference, used for continuously updated adapters in asynchronous RL setups[^lora-feature].

## Resolver-based on-demand loading

`LoRAResolver` plugins resolve unknown `model` names on request from filesystem, Hugging Face Hub, or custom backends such as S3; vLLM tries configured resolvers in order and keeps the first successful load[^lora-feature]. This requires runtime updating plus resolver-specific configuration, for example `VLLM_PLUGINS=lora_filesystem_resolver` with `VLLM_LORA_RESOLVER_CACHE_DIR`, or `VLLM_PLUGINS=lora_hf_hub_resolver` with `VLLM_LORA_RESOLVER_HF_REPO_LIST` as a comma-separated Hub repo list where the requested subpath must contain `adapter_config.json`[^lora-feature]. Remote Hub downloads are insecure and not intended for production[^lora-feature]. Custom resolvers implement `resolve_lora(base_model_name, lora_name)` returning a `LoRARequest` and register via `LoRAResolverRegistry.register_resolver`[^lora-feature]. Resolver layout, validation, ordering, and troubleshooting detail lives in [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md).

## Module declaration format and lineage

The legacy `--lora-modules name=path` form remains supported but leaves `base_model_name` unspecified[^lora-feature]. The newer JSON form records lineage[^lora-feature]:

```bash
--lora-modules '{"name": "sql-lora", "path": "jeeejeee/llama32-3b-text2sql-spider", "base_model_name": "meta-llama/Llama-3.2-3B-Instruct"}'
```

With lineage, the `/v1/models` card sets the LoRA entry `parent` to the base model and `root` to the adapter artifact location, while the base-model entry has `parent: null`[^lora-feature].

## Mixed 2D and 3D MoE adapters

To serve megatron-style 2D per-expert adapters and peft-style 3D fused adapters from one engine, start with `--enable-mixed-moe-lora-format` and declare each adapter layout explicitly with `is_3d_lora_weight`[^lora-feature]:

```bash
vllm serve Qwen/Qwen3.6-35B-A3B \
  --enable-lora \
  --enable-mixed-moe-lora-format \
  --lora-modules \
    '{"name": "lora-2d", "path": "...", "is_3d_lora_weight": false}' \
    '{"name": "lora-3d", "path": "...", "is_3d_lora_weight": true}'
```

The same field is accepted by `/v1/load_lora_adapter`[^lora-feature]. vLLM trusts the declared flag without inspecting the checkpoint; a wrong declaration loads weights into the wrong stacked buffers and silently produces garbage with no load-time error[^lora-feature]. 2D adapters have per-expert keys such as `...experts.{idx}.gate_proj.lora_A.weight`, while 3D adapters have fused keys such as `...experts.gate_up_proj.lora_A.weight`[^lora-feature]. Without `--enable-mixed-moe-lora-format`, `is_3d_lora_weight` is ignored and the adapter must match the base model `is_3d_moe_weight`; it is also ignored for non-MoE models[^lora-feature].

## Multimodal LoRA

- Tower and connector LoRA is experimental and requires implementing the corresponding token helper functions for the tower and connector; extended model coverage is tracked upstream and contributions are invited[^lora-feature].
- Default multimodal LoRAs automatically apply a mapped adapter when that modality is present, avoiding manual `LoRARequest` filtering for models such as Granite Speech and Phi-4-multimodal-instruct[^lora-feature]. Only one LoRA per prompt is allowed; if several present modalities each map to an adapter, none is applied[^lora-feature]. Configure offline with `LLM(..., default_mm_loras={"audio": model_id})` or serving with `--default-mm-loras '{"audio":"ibm-granite/granite-speech-3.3-2b"}'`[^lora-feature]. This currently applies only to `.generate` and chat completions[^lora-feature]. Multimodal input handling detail lives in [vLLM Multimodal Data Processing](vllm-multimodal-processing.md).

## Tuning tips

- Set `--max-lora-rank` to the maximum rank among planned adapters; a much larger value wastes memory and hurts performance[^lora-feature].
- Use `--lora-target-modules` with module suffixes such as `o_proj qkv_proj down_proj` to restrict LoRA to selected layers; when unset, LoRA applies to all supported modules[^lora-feature].

## Coverage limits

- The referenced `examples/features/lora/multilora_offline.py` async-engine example was not present in `raw/` and was not inspected[^lora-feature].
- Tower/connector helper implementation, upstream PR rationale, and current model-support status were cited but not inspected beyond this feature doc[^lora-feature].
- `SupportsLoRA` model coverage and server-wide LoRA capacity sizing beyond the named flags were not recompiled here[^lora-feature].

## Relationships

- Uses [vLLM LoRA Resolver Plugins](vllm-lora-resolver-plugins.md) — on-demand adapter discovery backing dynamic serving.
- Uses [vLLM Plugin System](vllm-plugin-system.md) — `VLLM_PLUGINS` filtering and out-of-tree `LoRAResolver` registration.
- Uses [vLLM Entrypoints](vllm-entrypoints.md) — offline `LLM.generate` versus online `vllm serve` paths for LoRA requests.
- Uses [vLLM Multimodal Data Processing](vllm-multimodal-processing.md) — modality inputs that trigger default multimodal LoRAs.

[^lora-feature]: LoRA Adapters — `../raw/vllm/features/lora.md`.
