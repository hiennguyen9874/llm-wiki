---
type: Concept
title: Minimal Tensorwise FP8 Training
description: Tensorwise-dynamic FP8 Linear that replaces torchao with a ~150-line autograd wrapper around torch._scaled_mm using E4M3 forward and E5M2 gradients.
tags: [fp8, quantization, training, pytorch, nanochat]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: fp8-src
    resource: ../raw/fp8.py
    title: Minimal FP8 training for nanochat — tensorwise dynamic scaling only
---

A ~150-line nanochat module replaces torchao `Float8Linear` (~2000 lines) for the tensorwise recipe only: one scalar scale per tensor, full-precision weights with FP8 matmul via PyTorch built-in `torch._scaled_mm` and float8 dtypes[^fp8-src].

## Scope and non-goals

Supports only the `tensorwise` recipe; rowwise/axiswise scaling, FSDP float8 all-gather, DTensor, and tensor-subclass dispatch tables are explicitly out of scope[^fp8-src].

`Float8LinearConfig.from_recipe_name` accepts only `"tensorwise"` and raises `ValueError` otherwise, preserving torchao API compatibility for that path[^fp8-src].

## Three-GEMM wrapping

A standard `Linear` does one matmul forward and two backward[^fp8-src]:

- forward: `output = input @ weight.T`
- backward: `grad_input = grad_output @ weight`
- backward: `grad_weight = grad_output.T @ input`

Each is wrapped as: compute `scale = FP8_MAX / max(|tensor|)` per operand, quantize with `clamp(tensor * scale).to(fp8)`, run `torch._scaled_mm` (cuBLAS FP8 kernel, ~2x faster than bf16 per source), and dequantize internally via inverse scales[^fp8-src].

The stated key insight is that `torch._scaled_mm` plus float8 dtypes are PyTorch built-ins; torchao is orchestration around those primitives that can be called directly[^fp8-src].

## Dtype choice

| Tensor | Format | Reason in source |
| --- | --- | --- |
| input, weight | `float8_e4m3fn`, 4-bit exponent / 3-bit mantissa, range `[-448, 448]` | higher precision (more mantissa bits) |
| gradients | `float8_e5m2`, 5-bit exponent / 2-bit mantissa, range `[-57344, 57344]` | wider range for large gradients |

Both formats follow the standard forward-E4M3 / backward-E5M2 convention[^fp8-src].

## Tensorwise quantization (`_to_fp8`)

Tensorwise means one scalar scale for the whole tensor, unlike rowwise per-row scales; tensorwise is faster because cuBLAS handles the scaling while rowwise needs the CUTLASS kernel[^fp8-src].

Procedure returns `(fp8_data, inverse_scale)` for `_scaled_mm`[^fp8-src]:

- `amax = x.float().abs().max()` over the entire tensor.
- `scale = fp8_max / amax.double().clamp(min=EPS)` with `EPS=1e-12` to avoid division by zero on all-zeros tensors.
- Division uses `float64` then `.float()` to keep torch.compile and eager numerics consistent; the source notes torchao does the same upcast.
- Quantize as `(x.float() * scale).clamp(-fp8_max, fp8_max).to(fp8_dtype)`; clamp matters because PyTorch cast wraps on overflow rather than saturating.
- `_scaled_mm` takes the inverse scale and multiplies back during the matmul.

## Layout requirements for `torch._scaled_mm`

The cuBLAS FP8 kernel requires first operand row-major (contiguous) and second operand column-major (`B.t().contiguous().t()`)[^fp8-src].

Layout tricks used[^fp8-src]:

- `weight_fp8.t()` from a contiguous `[N, K]` weight is already column-major `[K, N]` with strides `(1, K)` — no copy.
- Otherwise `_to_col_major(x) = x.t().contiguous().t()` gives the same logical shape with column-major strides, e.g. `[M, N]` gets strides `(1, M)` instead of `(N, 1)`.
- A transposed gradient for the first argument needs `.contiguous()` because transpose yields column-major while the first argument needs row-major.

## Forward and backward GEMMs (`_Float8Matmul`)

A single `torch.autograd.Function` takes full-precision inputs, quantizes internally, calls `_scaled_mm`, and returns full-precision outputs; it is marked `@torch._dynamo.allow_in_graph` so torch.compile treats it as one opaque node rather than tracing inside[^fp8-src].

Forward `output = input @ weight.T` quantizes both operands to E4M3, saves quantized tensors plus inverse scales, and calls `_scaled_mm` with `out_dtype=input_2d.dtype` and `use_fast_accum=True`[^fp8-src].

Backward uses `use_fast_accum=False` for more precise gradients; `True` accumulates dot products in lower precision and is measurably faster but slightly less accurate, described as standard practice for forward[^fp8-src]:

- `grad_input = grad_output @ weight`, shapes `[B, N] @ [N, K] -> [B, K]`; `grad_output` quantized to E5M2, saved E4M3 weight reused after `_to_col_major`.
- `grad_weight = grad_output.T @ input`, shapes `[N, B] @ [B, K] -> [N, K]`; `go_fp8.t().contiguous()` supplies row-major `[N, B]` first argument, `_to_col_major(in_fp8)` supplies column-major second argument.

## `Float8Linear` wrapper

`Float8Linear(nn.Linear)` keeps weights and biases in original precision (e.g. fp32/bf16); only the matmul runs in FP8[^fp8-src].

Forward casts input to `COMPUTE_DTYPE` (typically bf16) because `_scaled_mm` expects reduced-precision input and the module no longer relies on autocast; it flattens batch dims to 2D because `_scaled_mm` only supports 2D, reshapes back, then adds `bias.to(output.dtype)` if present[^fp8-src].

`from_float(mod)` shares storage with the source `nn.Linear`: it builds the shell on `meta` device (shapes/dtypes only, no memory) to avoid a temporary weight allocation, then points `.weight` and `.bias` at the original parameters[^fp8-src].

`convert_to_float8_training(module, config=None, module_filter_fn=None)` walks the tree post-order (children before parents) and swaps each `nn.Linear` that is not already `Float8Linear` and passes the optional `module_filter_fn(child, fqn)`; replacement shares weight/bias tensors with no copies or extra memory[^fp8-src].

The documented filter use is skipping layers whose dims are not divisible by 16, described as a hardware requirement for FP8 matmuls on H100[^fp8-src].

## How this differs from torchao

torchao uses a tensor-subclass architecture: `Float8TrainingTensor` bundles FP8 data plus scale and metadata and implements `__torch_dispatch__` with handlers for every aten op (`mm`, `t`, `reshape`, `clone`, ...) so `input @ weight.T` routes through `aten.mm` interception to `_scaled_mm` behind the scenes[^fp8-src].

Compile visibility differs[^fp8-src]:

- torchao: compile decomposes the subclass via `__tensor_flatten__` and sees `amax`, scale, cast, and `_scaled_mm` as separate graph nodes, letting Inductor fuse glue ops with surrounding ops (e.g. `amax` with the preceding activation).
- This module: compile sees one opaque call; it can optimize everything around the FP8 linear (attention, norms) but cannot fuse across the boundary.

Both call the same cuBLAS `_scaled_mm` kernel, so the GPU matmul is identical; only small glue ops (`amax`, scale, cast) differ[^fp8-src].

The source reports this version is slightly faster in practice (less compilation overhead, no subclass dispatch cost) but can produce subtly different floating-point rounding paths under torch.compile because Inductor generates a different graph; eager-mode numerics are bitwise identical[^fp8-src].

## Relationships

- Related to [DeepSeek-V3 FP8 Training and Deployment Systems](deepseek-v3-systems.md) — fine-grained FP8 mixed-precision counterpart contrasting block/tile scaling and FP32 accumulation with this tensorwise scalar-scale recipe.
- Related to [vLLM Quantization Methods and Toolchains](vllm-quantization-methods.md) — inference quantization-format context for placing FP8 training versus FP8 serving.
- Related to [SGLang Quantization](sglang-quantization.md) — serving-side FP8/AWQ/GPTQ context contrasting with this FP8 training matmul.
- Related to [FlashAttention-3 Asynchronous Low-Precision Attention](flashattention-3.md) — Hopper FP8 attention with block quantization that shares FP8 dtype and accumulation-precision concerns.
- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — Dynamo/Inductor background for the opaque-`allow_in_graph` versus decomposed-subclass compile trade-off.

## Coverage limits

- Single-file source only; `nanochat.common.COMPUTE_DTYPE`, training loop, loss scaling beyond `EPS` handling, and measured speedup or convergence numbers are not in this file.
- H100 divisibility-by-16, ~2x cuBLAS speedup, and bitwise-eager equivalence are source-reported claims without independent reproduction here.
- `raw/` attachment references beyond `fp8.py` were not enumerated because the file has no local imports beyond `torch` and `nanochat.common`.

[^fp8-src]: Minimal FP8 training for nanochat — tensorwise dynamic scaling only — `../raw/fp8.py`.
