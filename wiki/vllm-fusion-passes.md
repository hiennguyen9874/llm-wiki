---
type: Concept
title: vLLM torch.compile Fusion Passes
description: Custom Inductor fusion passes controlled by PassConfig that fuse collectives, norms, attention, RoPE, and quantization by token regime and platform.
tags: [vllm, torch-compile, fusion, inductor, quantization]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:00:00Z }
sources:
  - id: fusions
    resource: ../raw/vllm/design/fusions.md
    title: Fusion torch.compile passes
---

vLLM keeps model code clean by implementing kernel/operator fusions as custom `torch.compile` Inductor passes configured through `PassConfig` nested in `CompilationConfig`, with defaults set by optimization level and explicit user flags always winning[^fusions].

## Fusion catalog

Flags, fused pattern, default level, indicative end-to-end speedup, full-graph visibility need, and active `num_tokens` regime[^fusions]:

| Fusion | `PassConfig` flag | Fused operations | Default at | E2E speedup | Fullgraph | `num_tokens` |
| --- | --- | --- | --- | --- | --- | --- |
| AllReduce + RMSNorm | `fuse_allreduce_rms` | All-reduce → RMSNorm + residual-add → optional quant | O2, Hopper/Blackwell + TP>1 | 5–20% | No | Low |
| Attention + Quant | `fuse_attn_quant` | Attention output → FP8/NVFP4 quant | Off | 3–7% | Yes | Always |
| MLA Attention + Quant | `fuse_attn_quant` | MLA attention output → FP8/NVFP4 quant | Off | TBD | Yes | Always |
| RoPE + KV-cache update | `fuse_rope_kvcache` | Rotary embedding → KV-cache write | O2, ROCm/AITER only | 2–4% | No | Low |
| QK Norm + RoPE | `enable_qk_norm_rope_fusion` | Q/K RMSNorm → rotary embedding | Off | 2–3% | No | Low |
| Sequence Parallelism | `enable_sp` | AllReduce → ReduceScatter + AllGather | Off | Prereq for AsyncTP | Yes | High |
| AsyncTP GEMM + collective | `fuse_gemm_comms` | GEMM → reduce-scatter / all-gather → GEMM | Off | 7–10% | Yes | High |
| RMSNorm + Quant | `fuse_norm_quant` | RMSNorm + residual-add → FP8/FP4 quant | O1 conditional | 1–4% | No | Always |
| SiLU+Mul + Quant | `fuse_act_quant` | SiLU+Mul activation → FP8/FP4 quant | O1 conditional | 1–4% | No | Always |
| RMSNorm + Padding | `fuse_act_padding` | Residual-add + RMSNorm → padding | O1, ROCm/AITER only | TBD | No | Always |
| MLA Dual RMSNorm | `fuse_mla_dual_rms_norm` | Paired Q + KV RMSNorm + optional FP8 quant → 1 kernel | O1, ROCm/AITER only | 1–2% | No | Always |

Speedups are indicative only; exact model, batch size, and hardware dominate, so hand-tuning requires benchmarking with and without each fusion[^fusions].

## Support and applicability

- Fullgraph `Yes` means the whole model graph must be visible via Inductor partition or `splitting_ops=[]`; this applies to `fuse_attn_quant`, `enable_sp`, and `fuse_gemm_comms`[^fusions].
- Low-`num_tokens` fusions target decode/small-batch ranges; high-`num_tokens` SP/AsyncTP fusions apply above `PassConfig.sp_min_token_num`[^fusions].
- `fuse_allreduce_rms` needs NVIDIA Hopper SM90 or Blackwell SM100 with FlashInfer; TP+DP and TP+PP combinations are reported broken[^fusions].
- `fuse_attn_quant` support depends on the attention backend; not all backends support fused quantization output[^fusions].
- ROCm/AITER-only fusions are `fuse_rope_kvcache`, `fuse_act_padding`, and `fuse_mla_dual_rms_norm`; they are unavailable on CUDA/CPU[^fusions].
- `enable_qk_norm_rope_fusion` applies only to models with per-head Q/K RMSNorm before RoPE, for example Qwen; it is off by default partly because of Hopper performance issues[^fusions].
- `fuse_norm_quant` and `fuse_act_quant` are only enabled on NVIDIA when a custom `rms_norm`/`silu_and_mul` or custom quant kernel is active, because Inductor otherwise generates a faster kernel; NVFP4 models always use a custom FP4 quant op[^fusions].
- Platform/quantization support varies by SM version and ROCm: AllReduce fusion covers FP16/BF16, FP8 static, and NVFP4 on SM100 versus FP16/BF16 and FP8 static on SM90; norm/activation fusions cover FP8 static/per-token/per-group and NVFP4 subsets documented per fusion; SM80/SM89 coverage is limited or absent[^fusions].
- SP/`fuse_gemm_comms` autoconfiguration today targets SM90/H100 and models with `hidden_size >= 8192`; other architectures need explicit `sp_min_token_num`, and SM100 FP8 also needs `VLLM_DISABLED_KERNELS=FlashInferFP8ScaledMMLinearKernel`[^fusions].

## Enabling and disabling

Python[^fusions]:

```python
from vllm import LLM
from vllm.config import CompilationConfig, PassConfig

llm = LLM(
    model="...",
    optimization_level=2,
    compilation_config=CompilationConfig(
        pass_config=PassConfig(
            fuse_norm_quant=True,
            fuse_act_quant=True,
            fuse_allreduce_rms=False,
        )
    ),
)
```

CLI[^fusions]:

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct -O2 -cc.pass_config.fuse_allreduce_rms=False
vllm serve meta-llama/Llama-3.1-8B-Instruct -O2 --compilation-config '{"pass_config": {"fuse_allreduce_rms": false}}'
```

## Fusion details

- **AllReduce + RMSNorm:** fuses TP all-reduce with residual-add, RMSNorm, and optional FP8 static or NVFP4 dynamic quant into one FlashInfer/TRT-LLM communication kernel; max fused tensor size is hardware-dependent, e.g. 64 MB for TP=2 on SM90/SM100, configurable via `fi_allreduce_fusion_max_size_mb`[^fusions].
- **Attention + Quant:** removes the full-precision attention-output round-trip; standard attention supports FP8 static on TRITON_ATTN, FLASHINFER SM100+, ROCM_ATTN, and ROCM_AITER_UNIFIED_ATTN, plus NVFP4 dynamic on FLASHINFER SM100+; MLA fusion works at the `unified_mla_attention_with_output` graph level for FP8 static/per-group and NVFP4 but currently uses an intermediate buffer plus separate quantize, so no round-trip elimination or measurable speedup is expected yet[^fusions].
- **RoPE + KV-cache:** fuses rotary embedding with KV-cache scatter/write; needs ROCm + AITER, active `rotary_embedding` custom op, visible `kv_cache` update op, and by default `num_tokens <= 256` via `rope_kvcache_fusion_max_token_num`[^fusions].
- **Sequence Parallelism:** rewrites `AllReduce → RMSNorm` into `ReduceScatter → local RMSNorm → AllGather`, including fused-add and FP8-quant suffix variants; it does not directly speed up execution but enables AsyncTP; needs Inductor graph partition or piecewise compilation with static sizes divisible by TP size[^fusions].
- **AsyncTP GEMM + collective:** after SP, fuses GEMMs with surrounding reduce-scatter/all-gather using `torch.ops.symm_mem` symmetric-memory primitives to overlap communication and compute; requires `enable_sp=True` and is a no-op otherwise[^fusions].
- **QK Norm + RoPE:** fuses split-QKV, reshape, Q/K RMSNorm, reshape, and rotary embedding into one `fused_qk_norm_rope` CUDA kernel on SM80+; tested only on SM90/SM100[^fusions].
- **RMSNorm + Quant:** covers plain `rms_norm → quant_fp8` and `fused_add_rms_norm → quant_fp8` with in-place residual update; AITER variants live in a separate ROCm pass[^fusions].
- **SiLU+Mul + Quant:** covers `silu_and_mul → quant_fp8` including FP8 static, FP8 per-group 128/64 on CUDA SM89+, NVFP4 dynamic on SM100+ with FlashInfer, and FP8 per-token-group 128 on ROCm AITER; per-group CUDA fusion is inactive when DeepGEMM is used on SM100+[^fusions].
- **RMSNorm + Padding:** fuses residual-add + RMSNorm with hidden-dimension padding for downstream AITER Triton GEMMs; targeted at GPT-OSS-style hidden size 2880 when AITER Triton GEMMs are not enabled[^fusions].
- **MLA Dual RMSNorm:** fuses paired MLA `q_a_layernorm` and `kv_a_layernorm` into one AITER `fused_qk_rmsnorm` call, cutting 2 launches to 1 per layer; with per-token FP8 `q_b_proj`, the asymmetric q-quantized plus kv-BF16 pair lowers to `fused_mla_dual_rms_norm_per_token_quant`; native `rms_norm` cases are already handled by Inductor, so this pass targets active AITER custom `rms_norm`[^fusions].

## Coverage limits

- Referenced `torch_compile.md`, `optimization_levels.md`, and `attention_backends.md` context was only skimmed for pipeline/preset/backend placement; per-backend fused-quant details, full optimization-level tables, and pass source/benchmark code were not independently inspected[^fusions].
- Platform support matrix reflects the source at ingest time; latest and in-progress fusion work is tracked externally and may be stale[^fusions].

## Relationships

- Uses [vLLM Attention Backends](vllm-attention-backends.md) — `fuse_attn_quant` coverage and fused-output support depend on the selected attention backend.
- Depends on [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — fusion passes run inside the `torch.compile`/Inductor pipeline whose failures and disable flags that concept documents.
- Uses [vLLM Optimization Levels](vllm-optimization-levels.md) — preset defaults enabling each fusion per `-O0` through `-O3` level.

[^fusions]: Fusion torch.compile passes — `../raw/vllm/design/fusions.md`.
