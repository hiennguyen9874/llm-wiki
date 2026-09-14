---
type: Concept
title: vLLM CustomOp Dispatch and Registration
description: Platform-dispatched forward methods, compilation-config enablement, and in-tree versus out-of-tree registration for vLLM custom ops.
tags: [vllm, custom-op, compilation, plugins]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T08:46:46Z }
sources:
  - id: custom-op
    resource: ../raw/vllm/design/custom_op.md
    title: CustomOp
---

`CustomOp` is an abstract base class that dispatches an op's `forward()` to a platform-specific implementation and lets both vLLM and out-of-tree (OOT) plugins register custom operations[^custom-op].

## Registries

`CustomOp` keeps two class-level dictionaries of op classes indexed by registered name, one for vLLM and one for OOT plugins[^custom-op]:

- `@CustomOp.register("op_name")` adds the class to the in-tree `op_registry`[^custom-op].
- `@CustomOp.register_oot("op_name")` adds the class to `op_registry_oot`[^custom-op].

## Platform dispatch

When a `CustomOp` is called and enabled, it dispatches `forward()` by `current_platform`; when disabled it only calls the PyTorch-native `forward_native()`[^custom-op]:

- CPU: `forward_cpu()`[^custom-op].
- CUDA: `forward_cuda()`[^custom-op].
- ROCm: `forward_hip()`, falling back to `forward_cuda()` when `forward_hip()` is not implemented[^custom-op].
- XPU: `forward_xpu()`[^custom-op].
- TPU: `forward_tpu()`[^custom-op].
- OOT platform: `forward_oot()`, only called on OOT platforms[^custom-op].
- Default final fallback for all platforms: `forward_native()`[^custom-op].

Dispatch is not absolute because inheritance can override behavior in a derived class[^custom-op].

## Enablement and torch.compile interaction

Whether an op is enabled is decided from `compilation_config.custom_ops`[^custom-op]. An op using the default config is enabled when that list contains `all` and disabled when it contains `none`; `all` and `none` cannot coexist[^custom-op].

By default, vLLM appends `none` when `compilation_config.backend == "inductor"` and `compilation_config.mode != CompilationMode.NONE`, otherwise it appends `all`[^custom-op]. In practice this disables `CustomOp` on platforms that use inductor as the default `torch.compile` backend, letting Inductor generate fused Triton kernels for the disabled ops[^custom-op].

For multimodal models, vLLM enforces enablement of selected ops such as `MMEncoderAttention` and `ApplyRotaryEmb` to keep device-specific optimized kernels in the ViT path[^custom-op]. An op object can also force itself on with `enforce_enable=True` in `CustomOp.__init__()`; the source notes this mechanism will be removed once the multimodal part gets a separate `compilation_config`[^custom-op].

## User configuration

Users control enablement with `--compilation_config.custom_ops '["..."]'` when launching a server[^custom-op]:

- `["all"]`: enable all custom ops[^custom-op].
- `["none"]`: disable all custom ops[^custom-op].
- `["all,-op1"]`: enable all except `op1`; `-` prefix means disable[^custom-op].
- `["none,+op1,+op2"]`: enable only `op1` and `op2`; `+` prefix means enable[^custom-op].

## Supported op families

The source lists twelve families with in-tree op names: attention, activation, MM-conv, embedding, linear, logits processor, Mamba, MoE, norm, quantization, RoPE, and encoder[^custom-op]. Examples include `silu_and_mul` and `gelu_and_mul` activations, `conv2d`/`conv3d`, `vocab_parallel_embedding`/`parallel_lm_head`, row/column/replicated linears, `fused_moe`, `rms_norm` variants, `quant_fp8`, `rotary_embedding`/`apply_rotary_emb`, and encoder ops such as `mm_encoder_attn`[^custom-op].

## Implementing an in-tree op

1. Subclass `CustomOp`[^custom-op].
2. Decorate with `@CustomOp.register("op_name")`[^custom-op].
3. Implement the needed `forward_xxx()` methods[^custom-op].

The worked example is `MMEncoderAttention` registered as `"mm_encoder_attn"`, with `forward_native()`, `forward_cuda()`, `forward_cpu()`, `forward_xpu()`, and `forward_tpu()` variants calling TORCH_SDPA, FA, or PALLAS implementations as appropriate[^custom-op].

## OOT override for device plugins

`CustomOp` lets hardware vendors replace a vLLM op with deep-optimized kernels at runtime by registering an OOT subclass that implements `forward_oot()`, without modifying vLLM itself[^custom-op]. This builds on the hardware-plugin mechanism; the source lists official plugins such as vllm-ascend, vllm-spyre, vllm-gaudi, vllm-neuron, and vllm-meta, plus non-official examples such as vllm-metax, vllm-kunlun, and vllm-musa[^custom-op].

Pattern using `MMEncoderAttention`[^custom-op]:

1. Subclass it as `CustomMMEncoderAttention` and implement `forward_oot()` with device-specific kernels[^custom-op].
2. Register with `@CustomOp.register_oot("MMEncoderAttention")`, which adds `{"MMEncoderAttention": CustomMMEncoderAttention}` to `op_registry_oot`[^custom-op].
3. At init time, if the base class name appears in `op_registry_oot`, vLLM instantiates the registered replacement class instead[^custom-op].
4. When the op is called and enabled, the replacement's `forward_oot()` runs[^custom-op].

Multiple OOT ops can be registered centrally from a mapping[^custom-op]:

```python
from vllm.model_executor.custom_op import CustomOp


REGISTERED_CUSTOM_OPS = {
    "CustomOP1": YourCustomOp1,
    "CustomOP2": YourCustomOp2,
    "CustomOP3": YourCustomOp3,
}

for op_name, op_cls in REGISTERED_CUSTOM_OPS.items():
    CustomOp.register_oot(_decorated_op_cls=op_cls, name=op_name)
```

## Coverage limits

- Code excerpts embedded with `--8<--` include directives (for example `mla.py`, `activation.py`, `conv.py`, `linear.py`, `fused_moe`, `layernorm.py`, and rotary/encoder files) were cited as listed op names but not inspected beyond the design doc[^custom-op].
- The hardware-plugin design doc, linked hardware-plugin blog post, and `CustomOp` Python source were cited but not re-inspected here[^custom-op].

## Relationships

- Uses [vLLM Plugin System](vllm-plugin-system.md) — OOT `register_oot` / `forward_oot` overrides are the custom-op path for hardware device plugins.
- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — disabled ops fall back to `forward_native()` so Inductor can generate fused Triton kernels inside the default V1 compile pipeline.

[^custom-op]: CustomOp — `../raw/vllm/design/custom_op.md`, covering registries, platform dispatch, `compilation_config.custom_ops` enablement, user configuration, supported op families, in-tree implementation, and OOT device-plugin registration.
