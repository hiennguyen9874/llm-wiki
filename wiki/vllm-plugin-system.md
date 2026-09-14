---
type: Concept
title: vLLM Plugin System
description: Discovery, loading, and plugin groups for extending vLLM out-of-tree via Python entry points and VLLM_PLUGINS filtering.
tags: [vllm, plugins]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:46:46Z }
sources:
  - id: plugin-system
    resource: ../raw/vllm/design/plugin_system.md
    title: Plugin System
---

vLLM plugins are user-registered code that adds custom features without modifying the vLLM codebase[^plugin-system]. Because distributed inference spans multiple processes, every vLLM-created process must load the plugin, via `load_plugins_by_group` in `vllm.plugins`[^plugin-system].

## Discovery via entry points

Discovery uses the standard Python `entry_points` mechanism[^plugin-system]. A package registers a callable under a vLLM group; the canonical general-plugin example registers `register_dummy_model = vllm_add_dummy_model:register`, whose `register()` calls `ModelRegistry.register_model("MyLlava", "vllm_add_dummy_model.my_llava:MyLlava")`[^plugin-system].

Every plugin has three parts[^plugin-system]:

1. **Plugin group**: entry-point group name; general plugins always use `vllm.general_plugins`.
2. **Plugin name**: entry-point name (e.g. `register_dummy_model`); this is what `VLLM_PLUGINS` filters on.
3. **Plugin value**: fully qualified function or module reference (e.g. `vllm_add_dummy_model:register`).

Set `VLLM_PLUGINS` to a plugin name to load only that plugin[^plugin-system].

## Supported plugin groups

| Group | Purpose | Registered value |
| --- | --- | --- |
| `vllm.general_plugins` | Register custom out-of-tree models via `ModelRegistry.register_model`[^plugin-system] | Callable; official model example is `bart-plugin` adding `BartForConditionalGeneration` |
| `vllm.platform_plugins` | Register custom out-of-tree platforms[^plugin-system] | Callable returning `None` when unsupported in the current environment, else the platform class fully qualified name |
| `vllm.io_processor_plugins` | Register custom pre-/post-processing for pooling models[^plugin-system] | Callable returning the `IOProcessor` class fully qualified name |
| `vllm.stat_logger_plugins` | Register custom out-of-tree loggers[^plugin-system] | Class subclassing `StatLoggerBase` |
| `vllm.endpoint_plugins` | Register custom out-of-tree HTTP routes on the OpenAI-compatible server[^plugin-system] | Zero-argument factory; unlike other groups, loaded only in the API-server frontend process and **not loaded by default** |

Endpoint and IO-processor detail lives in [vLLM Endpoint Plugins](vllm-endpoint-plugins.md) and [vLLM IO Processor Plugins](vllm-io-processor-plugins.md).

## Authoring rules

The entry-point function must be re-entrant — callable multiple times without side effects — because it may be invoked repeatedly in some processes[^plugin-system].

## Platform plugin implementation checklist

Scaffold an out-of-tree package (e.g. `vllm_add_dummy_platform` with `my_dummy_platform.py`, `my_dummy_worker.py`, `my_dummy_attention.py`, `my_dummy_device_communicator.py`, `my_dummy_custom_ops.py`), register `my_dummy_platform = vllm_add_dummy_platform:register` under `vllm.platform_plugins`, and have `register()` return the platform class fully qualified name[^plugin-system].

The platform class inherits `vllm.platforms.interface.Platform` and must at minimum implement[^plugin-system]:

- `_enum`: usually `PlatformEnum.OOT` for out-of-tree platforms.
- `device_type`: PyTorch device type such as `"cpu"` or `"cuda"`.
- `device_name`: usually the same as `device_type`; mainly for logging.
- `check_and_update_config`: runs very early in initialization to update vLLM config (e.g. block size, graph mode); most importantly it sets `worker_cls`.
- `get_attn_backend_cls`: returns the attention backend class fully qualified name.
- `get_device_communicator_cls`: returns the device communicator class fully qualified name.

The worker class inherits `WorkerBase` (`vllm.v1.worker.worker_base.WorkerBase`)[^plugin-system]. Core methods to implement:

- `init_device`, `initialize_cache`, `load_model`, `get_kv_cache_spec`, `determine_available_memory`, `initialize_from_config`, `execute_model` (called every inference step)[^plugin-system].

Optional worker capabilities[^plugin-system]:

- `sleep` / `wakeup` for sleep mode.
- `compile_or_warm_up_model` for graph mode.
- `take_draft_token_ids` for speculative decoding.
- `add_lora`, `remove_lora`, `list_loras`, `pin_lora` for LoRA.
- `execute_dummy_batch` for data parallelism.

The attention backend inherits `AttentionBackend` (`vllm.v1.attention.backend.AttentionBackend`); `vllm.v1.attention.backends` holds in-tree examples[^plugin-system].

Custom ops for performance[^plugin-system]:

- PyTorch communicator ops (all-reduce, all-gather, etc.): implement a `DeviceCommunicatorBase` subclass.
- PyTorch common ops (matmul, softmax, etc.): register out-of-tree via the `CustomOp` class.
- C++ (`csrc`) ops: follow the `csrc` module and `vllm._custom_ops` pattern.
- Triton ops: the custom out-of-tree path does not currently work.

Other modules (LoRA, graph backend, quantization, Mamba attention backend, etc.) can optionally be made pluggable[^plugin-system].

## Compatibility guarantee

vLLM guarantees the interface of documented plugin entry points such as `ModelRegistry.register_model` remains available[^plugin-system]. Plugin authors own version compatibility of their registered targets (e.g. `"vllm_add_dummy_model.my_llava:MyLlava"` against the targeted vLLM version); model/module interfaces may change during development, so a deprecation log means the plugin should be upgraded[^plugin-system].

## Deprecations

- `use_v1` parameter in `Platform.get_attn_backend_cls`: deprecated, removed in v0.13.0[^plugin-system].
- `_Backend` in `vllm.attention`: deprecated, removed in v0.13.0; use `vllm.v1.attention.backends.registry.register_backend` to add new backends to `AttentionBackendEnum`[^plugin-system].
- `seed_everything` platform interface: deprecated, removed in v0.16.0; use `vllm.utils.torch_utils.set_random_seed`[^plugin-system].
- `prompt` in `Platform.validate_request`: deprecated, removed in v0.18.0[^plugin-system].

## Coverage limits

- The architecture overview (`arch_overview.md`) was compiled separately; multi-process rationale here is summarized, not re-derived[^plugin-system].
- The endpoint-plugin interface and security posture (`endpoint_plugins.md`, `../usage/security.md#endpoint-plugins`) were not recompiled here; see [vLLM Endpoint Plugins](vllm-endpoint-plugins.md)[^plugin-system].
- The `bart-plugin` example, `vllm.plugins` / `Platform` / `WorkerBase` / `AttentionBackend` / `CustomOp` source, and in-tree backend examples were cited but not inspected beyond the design-doc excerpts[^plugin-system].

## Relationships

- Uses [vLLM V1 Process Architecture](vllm-v1-process-architecture.md) — every vLLM-created process loads plugins via `load_plugins_by_group`, except endpoint plugins which are frontend-only.
- Uses [vLLM Engine, Worker, and Model Hierarchy](vllm-engine-worker-hierarchy.md) — platform plugins supply `worker_cls` and worker/communicator implementations consumed by the engine.
- Uses [vLLM Attention Backends](vllm-attention-backends.md) — platform plugins contribute backends via `get_attn_backend_cls` / `register_backend`.
- Uses [vLLM CustomOp Dispatch and Registration](vllm-custom-op.md) — OOT common-op overrides via `CustomOp.register_oot` / `forward_oot`.
- Uses [vLLM Endpoint Plugins](vllm-endpoint-plugins.md) — endpoint group detail and its opt-in, frontend-only trust model.
- Uses [vLLM IO Processor Plugins](vllm-io-processor-plugins.md) — pooling pre-/post-processing group detail.

[^plugin-system]: Plugin System — `../raw/vllm/design/plugin_system.md`.
