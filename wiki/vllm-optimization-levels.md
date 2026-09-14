---
type: Concept
title: vLLM Optimization Levels
description: Preset -O0 through -O3 flags trading startup time for performance via compilation, CUDA-graph, fusion, and autotune defaults.
tags: [vllm, optimization-levels, compilation, cudagraphs, fusion]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T10:00:00Z }
sources:
  - id: opt-levels
    resource: ../raw/vllm/design/optimization_levels.md
    title: Optimization Levels
---

vLLM provides four `-O0` through `-O3` presets that trade startup time for performance; every preset default can be reproduced with explicit flags, and any user-set flag takes precedence over the preset[^opt-levels].

## Usage

CLI[^opt-levels]:

```bash
vllm serve RedHatAI/Llama-3.2-1B-FP8 -O1
```

Python API, where `optimization_level=2` is equivalent to `-O2`[^opt-levels]:

```python
from vllm.entrypoints.llm import LLM

llm = LLM(
    model="RedHatAI/Llama-3.2-1B-FP8",
    optimization_level=2
)
```

## Levels

- **`-O0`: No optimization.** Fastest startup, lowest performance; no autotuning, compilation, or CUDA graphs. Good for early development and debugging[^opt-levels].
  - `-cc.cudagraph_mode=NONE`
  - `-cc.mode=NONE`, also resulting in `-cc.custom_ops=["none"]`
  - `-cc.pass_config.fuse_...=False` for all fusions
  - `--kernel-config.enable_flashinfer_autotune=False`
- **`-O1`: Fast optimization.** Prioritizes fast startup while enabling basic compilation and CUDA graphs; a balance for development that still exercises cudagraph/compile compatibility[^opt-levels].
  - `-cc.cudagraph_mode=PIECEWISE`
  - `-cc.mode=VLLM_COMPILE`
  - `--kernel-config.enable_flashinfer_autotune=True`
  - `-cc.pass_config.fuse_norm_quant=True` — only when either op uses a custom kernel, otherwise Inductor fusion is better[^opt-levels].
  - `-cc.pass_config.fuse_act_quant=True` — same custom-kernel condition as above[^opt-levels].
  - `-cc.pass_config.fuse_act_padding=True` — ROCm-only, requires AITER[^opt-levels].
  - `-cc.pass_config.fuse_mla_dual_rms_norm=True` — ROCm-only, requires AITER[^opt-levels].
- **`-O2`: Full optimization, default.** Prioritizes performance at extra startup cost; recommended for production. Adds on top of `-O1`, with fusions that may take longer from additional compile ranges[^opt-levels].
  - `-cc.cudagraph_mode=FULL_AND_PIECEWISE`
  - `-cc.pass_config.fuse_allreduce_rms=True`
  - `-cc.pass_config.fuse_rope_kvcache=True` — ROCm-only, requires AITER[^opt-levels].
- **`-O3`: Aggressive optimization.** Currently identical to `-O2`; reserved for future time-consuming or experimental optimizations[^opt-levels].

## Troubleshooting

- Startup too long: drop to `-O0` or `-O1`[^opt-levels].
- Compilation errors: use `debug_dump_path` for additional debugging information[^opt-levels].
- Performance issues: ensure `-O2` for production[^opt-levels].

## Relationships

- Uses [vLLM torch.compile Integration](vllm-torch-compile.md) — `-cc.mode` selects `NONE` versus `VLLM_COMPILE` compilation behavior.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — `cudagraph_mode` selects `NONE`, `PIECEWISE`, or `FULL_AND_PIECEWISE` capture behavior.
- Uses [vLLM torch.compile Fusion Passes](vllm-fusion-passes.md) — `PassConfig` fusion flags enabled per level, with platform and token-regime conditions detailed there.
- Depends on [Debugging vLLM-torch.compile Integration](vllm-debug-torch-compile.md) — `debug_dump_path` and per-stage disable flags are the entry point for compilation errors surfaced under these presets.

[^opt-levels]: Optimization Levels — `../raw/vllm/design/optimization_levels.md`, covering -O0 through -O3 settings, usage examples, and troubleshooting.
