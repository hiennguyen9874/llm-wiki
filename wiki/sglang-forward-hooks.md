---
type: Concept
title: SGLang Forward Hooks
description: JSON-configured PyTorch forward hooks for SGLang submodules with fnmatch targeting, factory resolution, and startup registration.
tags: [sglang, hooks, debugging, observability]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T09:57:17Z }
sources:
  - id: sgl-fhooks
    resource: ../raw/sglang/advanced_features/forward_hooks.mdx
    title: Model Forward Hooks
---

SGLang attaches standard PyTorch forward hooks to selected model submodules from `ServerArgs.forward_hooks`, registered once in `ModelRunner.initialize` and invoked on every forward pass for activation logging, internal debugging, and hidden-state export[^sgl-fhooks].

## Configuration

`forward_hooks` is an optional list of hook specs on `ServerArgs`[^sgl-fhooks]:

```jsonc
{
  "forward_hooks": [
    {
      "name": "outer_linear_hooks",
      "target_modules": ["outer.0", "outer.1"],
      "hook_factory": "my_project.hooks:dummy_hook_factory",
      "config": { "tag": "outer-layer" }
    }
  ]
}
```

Each spec contains[^sgl-fhooks]:

- `name` (optional): human-readable label used only in log messages.
- `target_modules` (required): list of `fnmatch.fnmatch` patterns matched against `model.named_modules()`.
- `hook_factory` (required): Python factory path that creates the hook.
- `config` (optional): arbitrary JSON object passed as a Python `dict` to the factory.

## Module targeting

Patterns are evaluated against every name in `model.named_modules()`[^sgl-fhooks]:

- `"outer.0"` matches exactly `"outer.0"`.
- `"outer.*"` matches `"outer.0"`, `"outer.1"`, `"outer.inner"`, and similar.
- `"outer.inner.*"` matches children under `outer.inner`.

If no modules match, registration does not fail; SGLang logs a warning with the spec name and patterns and continues[^sgl-fhooks]. A spec with missing `target_modules` is skipped with a warning[^sgl-fhooks].

## Factory resolution

Supported factory paths[^sgl-fhooks]:

- `"package.module:factory_name"`
- `"package.module.submodule.factory_name"`

`resolve_callable` splits on `:` when present, otherwise splits the dotted path into module plus final attribute, imports the module with `importlib.import_module`, and returns the named attribute[^sgl-fhooks].

Failure modes[^sgl-fhooks]:

- Malformed path with no `:` and fewer than two dotted parts: `ValueError` at startup, fail-fast.
- Importable module without the named attribute: `AttributeError` with module, attribute, and original path, fail-fast.
- Missing `hook_factory` in the spec: warning and skip.
- Factory returns `None`: warning and skip; initialization continues.

## Registration lifecycle

`ModelRunner.initialize` calls `register_forward_hooks(self.model, server_args.forward_hooks)` when configured[^sgl-fhooks]. Registration logic[^sgl-fhooks]:

1. Builds a `name_to_module` map from `model.named_modules()`.
2. Validates `target_modules` and `hook_factory`, warning and skipping incomplete specs.
3. Resolves the factory and calls `hook_factory(config)`.
4. Collects all modules whose names match any pattern.
5. Calls `module.register_forward_hook(hook)` for each match and logs the registration.

Key limits[^sgl-fhooks]:

- Forward hooks only; no pre-forward or full backward-hook support through this API.
- Attached once at initialization.
- Hook handles are not stored on `ModelRunner`, so hooks cannot later be removed through this API.

## Writing a hook factory

A factory takes `config: dict` and returns a `(module, inputs, output)` forward hook[^sgl-fhooks]:

```python
HOOK_CALLS = []

def dummy_hook_factory(config):
    tag = config.get("tag", "default")

    def hook(module, inputs, output):
        HOOK_CALLS.append(
            {
                "module_type": type(module).__name__,
                "tag": tag,
                "shape": tuple(output.shape),
            }
        )
        return output

    return hook
```

The returned hook must return `output` unless it intentionally modifies the tensor[^sgl-fhooks]. In the example JSON above, `my_project.hooks:dummy_hook_factory` is called with `{"tag": "outer"}` and the resulting hook runs for modules matching `outer.0` and `outer.1`[^sgl-fhooks].

## Relationships

- Uses [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — companion mechanism for saving intermediate target-model activations for training, distillation, and analysis.

[^sgl-fhooks]: Model Forward Hooks — `../raw/sglang/advanced_features/forward_hooks.mdx`.
