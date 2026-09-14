---
type: Concept
title: vLLM LoRA Resolver Plugins
description: On-demand LoRA adapter discovery and loading at request time via LoRAResolver plugins for filesystem, Hugging Face Hub, and custom backends.
tags: [vllm, lora, plugins]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:44:01Z }
sources:
  - id: lora-resolver-plugins
    resource: ../raw/vllm/design/lora_resolver_plugins.md
    title: LoRA Resolver Plugins
---

LoRA Resolver plugins automatically discover and load LoRA adapters at request time through the `LoRAResolver` framework, eliminating manual configuration or server restarts[^lora-resolver-plugins]. When a request names an adapter that is not yet loaded, configured resolvers attempt to locate, validate, and load it from their storage locations[^lora-resolver-plugins].

This enables dynamic LoRA loading without restarts, multiple storage backends, seamless integration with existing LoRA workflows, and centralized adapter management across multiple vLLM instances[^lora-resolver-plugins].

## Required configuration

Dynamic loading requires[^lora-resolver-plugins]:

- `VLLM_ALLOW_RUNTIME_LORA_UPDATING=true` or `1`.
- `VLLM_PLUGINS` including the desired resolver plugins, for example `lora_filesystem_resolver`.
- `VLLM_LORA_RESOLVER_CACHE_DIR` set to a valid accessible directory for the filesystem resolver.
- Serving with LoRA enabled, for example `vllm serve <base-model> --enable-lora`.

`VLLM_PLUGINS` filtering follows the general plugin mechanism: if unset, all available plugins load; if set to an empty string, no plugins load[^lora-resolver-plugins].

## Available resolvers

- `lora_filesystem_resolver`: installed with vLLM by default; loads adapters from a local directory structure[^lora-resolver-plugins].
- `hf_hub_resolver`: pulls LoRA adapters from Hugging Face Hub and proceeds in the same manner[^lora-resolver-plugins].
- Custom resolvers: for example an S3 resolver must be implemented out-of-tree against the `LoRAResolver` interface[^lora-resolver-plugins].

## Filesystem resolver layout

Each adapter is a subdirectory named for the requested model[^lora-resolver-plugins]:

```text
/path/to/lora/adapters/
├── adapter1/
│   ├── adapter_config.json
│   ├── adapter_model.bin
│   └── tokenizer files (if applicable)
└── adapter2/
    ├── adapter_config.json
    ├── adapter_model.bin
    └── tokenizer files (if applicable)
```

Each adapter directory must contain `adapter_config.json` and `adapter_model.bin`[^lora-resolver-plugins]. The config requires LoRA fields such as `peft_type: "LORA"`, `base_model_name_or_path`, `r`, `lora_alpha`, `target_modules`, `bias`, `modules_to_save`, `use_rslora`, and `use_dora`[^lora-resolver-plugins].

Usage is then a normal OpenAI-compatible request naming the adapter directory as the model, for example `"model": "my_sql_adapter"`[^lora-resolver-plugins].

## Resolution flow

For a request naming `my_sql_adapter`[^lora-resolver-plugins]:

1. The filesystem resolver checks whether `<cache-dir>/my_sql_adapter/` exists.
2. It validates `adapter_config.json`.
3. If the configuration matches the base model and is valid, the adapter is loaded.
4. The request is processed normally.
5. The adapter remains available for future requests.

## Multiple and custom resolvers

Configure multiple resolvers with a comma-separated `VLLM_PLUGINS` list, for example `lora_filesystem_resolver,lora_s3_resolver`[^lora-resolver-plugins]. All listed resolvers are enabled; at request time vLLM tries them in order until one succeeds[^lora-resolver-plugins].

A custom resolver subclasses `LoRAResolver` and implements `resolve_lora(base_model_name, lora_name)`, then registers through `LoRAResolverRegistry.register_resolver`[^lora-resolver-plugins]:

```python
from vllm.lora.resolver import LoRAResolver, LoRAResolverRegistry
from vllm.lora.request import LoRARequest
```

## Troubleshooting

Common failures[^lora-resolver-plugins]:

- `VLLM_LORA_RESOLVER_CACHE_DIR must be set to a valid directory`: ensure the directory exists, is accessible, and has correct permissions.
- `LoRA adapter not found`: verify the directory name matches the requested model name and that `adapter_config.json` and `adapter_model.bin` exist with valid JSON.
- `Invalid adapter configuration`: verify `peft_type` is `LORA`, `base_model_name_or_path` matches the base model, and `target_modules` is configured.
- `LoRA rank exceeds maximum`: verify `r` does not exceed the `max_lora_rank` setting.

Debugging steps are enabling `VLLM_LOGGING_LEVEL=DEBUG`, echoing the three resolver environment variables, and validating `adapter_config.json` parses as JSON[^lora-resolver-plugins].

## Coverage limits

- The `LoRAResolver`, `LoRAResolverRegistry`, and `LoRARequest` implementations were compiled only from the excerpts in the design doc, not from inspected vLLM source[^lora-resolver-plugins].
- The S3 resolver is documented only as a custom-resolver example to implement, not as a built-in backend[^lora-resolver-plugins].
- The example Hugging Face token value in the source was treated as a placeholder and was not compiled.

## Relationships

- Uses [vLLM Plugin System](vllm-plugin-system.md) — resolver plugins are enabled and filtered through `VLLM_PLUGINS`.

[^lora-resolver-plugins]: LoRA Resolver Plugins — `../raw/vllm/design/lora_resolver_plugins.md`.
