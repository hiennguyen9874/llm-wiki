---
type: Concept
title: SGLang Advanced CUDA Graphs
description: Runner/backend split, Breakable CUDA Graphs, full prefill capture, and graph-memory management for SGLang LLM and diffusion serving.
tags: [sglang, cuda-graphs, prefill, decode, attention, memory]
status: stable
created: 2026-09-14
generated: { by: llm-wiki-agent/1, at: 2026-09-14T19:55:00Z }
sources:
  - id: sgl-adv-cg
    resource: ../raw/2026-08-17-advanced-cuda-graph/index.md
    title: Advanced CUDA Graph Techniques in SGLang
---

SGLang refactored CUDA Graph support around a runner/backend split, made Breakable CUDA Graph (BCG) the default prefill strategy, added experimental full prefill capture, and treats capture ceiling as a memory-management control[^sgl-adv-cg].

## Runner/backend split

Before the refactor, decode, prefill, and speculative decoding each had their own CUDA Graph runners with overlapping capture-shape, static-buffer, replay, and configuration logic[^sgl-adv-cg].

Refactor [#23906](https://github.com/sgl-project/sglang/pull/23906) separates two layers[^sgl-adv-cg]:

- **Runner**: execution-specific state for capture and replay — captured shapes, static input buffers, attention metadata, and padding live batches into captured shapes.
- **Backend**: how that execution is captured — one full graph, breakable segments, or compiler-generated pieces.

Because runners depend only on a common backend interface, each execution path chooses its capture strategy independently. Prefill and decode have separate runners; speculative decoding adds EAGLE draft, draft-extend, and frozen-KV MTP draft runners built on the decode runner, while target verify is the decode runner itself capturing more than one token per request[^sgl-adv-cg].

Three backends[^sgl-adv-cg]:

| Backend | Capture model |
|---|---|
| Full | One `torch.cuda.CUDAGraph` per shape, no eager regions, fewest replay-time launches. Natural for decode where the shape variable is batch-size buckets. |
| Breakable (BCG) | Graph-safe regions captured as segments with selected operations run eagerly between segments via `@eager_on_graph`. |
| TC piecewise | `torch.compile` traces forward with `fullgraph=True`, splits FX graph at registered points, compiles and captures each piece. First partial-capture answer; still ships where breakable capture is unvalidated. |

## Breakable CUDA Graph origin

BCG is an SGLang-originated serving technique: first proposed, named, implemented, and open-sourced in SGLang[^sgl-adv-cg]:

- **2026-02-21**: initial [#19102](https://github.com/sgl-project/sglang/pull/19102) commit already contained `BreakableCUDAGraph`, the eager-break decorator, and end/resume capture machinery; merged April 11.
- **2026-04**: [#22218](https://github.com/sgl-project/sglang/pull/22218), explicitly based on #19102, built BCG into a compiler-free breakable piecewise backend for prefill; merged April 24. BCG became the default prefill strategy.

SGLang also pioneered full prefill capture for FA4 and FlashInfer backends[^sgl-adv-cg].

The originality claim is scoped to this runtime breakable capture/replay mechanism for open-source LLM serving, not to broader graph-segmentation or eager-fallback concepts[^sgl-adv-cg].

## BCG mechanism

Real forwards contain operations that do not fit fixed-sequence replay without host participation: attention backends planning from live lengths, collectives with runtime coordination, and dynamically updating serving features[^sgl-adv-cg].

BCG lets developers mark the incompatible region with `@eager_on_graph`. During capture the current segment closes at the marked function, the function runs eagerly, and capture resumes in a new segment; at replay the segments and eager functions run in the same order[^sgl-adv-cg].

Boundary handling[^sgl-adv-cg]:

- During capture the marked function runs once between segments and its returned tensor is retained as a persistent boundary buffer so its device address stays fixed; the next segment captures against that address.
- On every replay the eager function runs normally and returns a fresh tensor, which BCG copies into the retained buffer so the next segment reads the updated value from its captured address.
- BCG never inspects or traces inside the eager region; the region only needs to execute correctly.

Unlike TC piecewise, which first asks the compiler to understand the full forward then splits the result, BCG places splits directly while capture happens[^sgl-adv-cg].

## BCG benefits

BCG and TC piecewise produce the same replayable structure — graph segments separated by eager regions — but differ in construction cost, compatibility, and debuggability[^sgl-adv-cg].

**Faster startup.** Compiler-based piecewise setup is dominated by compilation, not capture: `torch.compile` is 78–86% of prefill-graph preparation, reaching 90 s on a 235B MoE and 158 s on GLM-5.2. BCG removes that phase with a single capture pass, building prefill graphs 3.8–5.2× faster in roughly a quarter of the code (521 versus 1,771 lines)[^sgl-adv-cg].

TP4 on 4×GB300, 42 captured shapes per configuration, weight loading and kernel JIT excluded; compilation overhead also slowed CI test loops before removal[^sgl-adv-cg].

**Broader compatibility.** Custom CUDA, Triton, and JIT kernels needed `torch.library` wrapping plus fake implementations for tracing, and inputs/outputs crossing a registered operator boundary had to be compiler-representable — sometimes forcing a different cutting point or a larger eager region just to satisfy the compiler[^sgl-adv-cg].

BCG removes that constraint: the graph system need not understand or trace the marked function, so boundaries follow serving logic. This reduced compiler-specific work as CUDA Graphs coexisted with DP attention, MoE all-to-all backends, LoRA, PD disaggregation, hierarchical cache, and deterministic inference[^sgl-adv-cg].

**Debuggable by construction.** Captured graphs replay opaquely, so prints, assertions, and stepwise inspection are difficult; BCG leaves eager regions where normal Python still runs on every replay[^sgl-adv-cg].

`--debug-cuda-graph` (from [#19102](https://github.com/sgl-project/sglang/pull/19102)) effectively wraps the whole forward in an eager break while still going through runner, static buffers, replay path, and metadata preparation: if the problem remains it points at model/runner path, if it disappears capture is the primary suspect[^sgl-adv-cg].

## BCG in diffusion

SGLang diffusion adopted BCG in [#27436](https://github.com/sgl-project/sglang/pull/27436). Diffusion repeatedly executes the same DiT forward during denoising, so launch-bound forwards with many small kernels benefit especially[^sgl-adv-cg]:

- Capture real serving shapes: resolution, frame count, prompt-conditioning length, CFG mode, and selected transformer; warm up served shapes and fall back to eager for unseen signatures.
- Break around dynamic attention and runtime-dependent metadata preparation while capturing stable computation without requiring `torch.compile` to understand the DiT forward.
- Capture stable regions once and replay them through the denoising loop.

After warmup, Qwen-Image at 512×512 on single B200 improves 6.48 s to 2.45 s end-to-end, and Z-Image 1.231 s to 0.662 s. BCG removes launch overhead; it does not reduce FLOPs or make compute-bound kernels cheaper[^sgl-adv-cg].

## Full CUDA Graph for prefill

Full capture is natural for decode because each request contributes one token and batch size is the main variable. Prefill varies in total tokens and request count simultaneously while a captured graph needs both fixed, plus attention backends depending on runtime metadata — the reason BCG was adopted there first[^sgl-adv-cg].

More recent work in [#27988](https://github.com/sgl-project/sglang/pull/27988) restructured request slots and attention metadata so supported backends no longer stay outside the graph[^sgl-adv-cg].

Token dimension is fixed with token buckets: the live batch pads to the nearest captured token count, like decode pads batch size[^sgl-adv-cg].

Request dimension uses fixed slots: live requests occupy the first slots and unused slots become zero-length sentinels with zero sequence/extend lengths and offsets parked after real tokens. Batches with more requests than slots fall back to eager[^sgl-adv-cg].

At replay the full request table is still read by the graph, so sentinel metadata is rewritten every replay and attention metadata is rebuilt outside the graph for the padded batch. This requires backends that build extend-mode metadata that way — currently mainly FlashAttention (FA4) and FlashInfer[^sgl-adv-cg].

Full prefill capture remains experimental: it must be enabled explicitly, warns toward `breakable` or `tc_piecewise` for production, and backend/bucket/slot tuning is still open[^sgl-adv-cg].

### Padding cost

Padded tokens are real work: they become rows in the captured batch and pass through dense projections in the same GEMMs. SGLang carries the true token count separately so MoE routing, attention, and linear-attention kernels can skip much of the padded region, but dense computation still pays[^sgl-adv-cg].

Empty request slots are much cheaper: FlashAttention's variable-length scheduler derives work from actual sequence length, so a zero-length request adds essentially no attention work beyond metadata and scheduling overhead. Token padding is the expensive dimension; request-slot padding is comparatively cheap[^sgl-adv-cg].

### Prefill replay benchmark

Prefill-only latency — fixed input length, one output token, one request at a time, decode graphs disabled — on gpt-oss-120b (TP4, 4×GB300) where all four paths run[^sgl-adv-cg]:

- Full: 1.93× over eager.
- BCG: 1.70× over eager and 17% faster than TC piecewise at replay.
- TC piecewise: 1.45× over eager.

The replay gap comes from per-forward work: BCG replays recorded segments directly while TC piecewise calls back into the compiled callable, paying Torch Dynamo guard checks and dispatch before its captured pieces run[^sgl-adv-cg].

On GLM-5.2 only BCG captures at all — TC piecewise cannot trace the forward and full capture has no sparse-attention path — at 1.60× over eager. Curves are flat across a 32× prompt-length range, the signature of launch overhead rather than compute[^sgl-adv-cg].

## Memory footprint

### Reuse inside segmented capture

Every captured shape with multiple segments could multiply resident memory unless intermediates are reused. BCG uses three reuse forms[^sgl-adv-cg]:

- One shared CUDA Graph pool across segments for a captured shape, reusing intermediate storage rather than pinning per-segment memory.
- Weak references at eager breaks: tensors passed into a break are held weakly when the graph pool already owns storage, avoiding Python references that extend lifetimes. The weak-reference technique comes from vLLM [#9724](https://github.com/vllm-project/vllm/pull/9724) for sharing output buffers.
- One maximum-sized output buffer shared across capture sizes, sliced to rows needed per shape.

The exception is the tensor carrying data across an eager break: the next segment captured against its address, so that buffer must stay alive and update in place on every replay[^sgl-adv-cg].

With reuse, 42 shapes across a 78-layer MoE add 2.4 GB of graph memory on GLM-5.2[^sgl-adv-cg].

### Capture through chunked-prefill size

Graph memory is resident — allocated at capture and held for server lifetime — while eager activations are transient, with the largest supported prefill setting the peak. Capturing a shape moves much of that transient working set into the resident pool, but only for shapes that actually replay[^sgl-adv-cg].

If the capture ladder stops below maximum prefill size, the largest prefill still runs eagerly and keeps its activation peak while the server also pays for resident graphs below it. The capture ceiling therefore matters more than the number of shapes; because `chunked_prefill_size` bounds the largest single prefill forward, capturing through that size removes the worst eager peak[^sgl-adv-cg].

Measured prefill memory above the no-graph resident baseline after one prefill at exactly the chunked-prefill size: ceilings below chunk size sit slightly above baseline, while reaching chunk size collapses the peak — 0.56 GB to 0.001 GB on gpt-oss-120b, and 1.55 GB to 0.35 GB on GLM-5.2 where the sparse-attention indexer still runs eagerly at a break[^sgl-adv-cg].

This buys lower total memory — 0.51 GB below baseline on gpt-oss-120b and 1.10 GB on GLM-5.2, modest against a few-hundred-GB footprint but a saving — and predictable usage by turning a workload-dependent spike into a fixed capture-time allocation the engine can account for up front[^sgl-adv-cg].

## Standalone library

With the Meta PyTorch team, the mechanism was factored out as [meta-pytorch/breakable-cuda-graphs](https://github.com/meta-pytorch/breakable-cuda-graphs): a `breakable_graph(...)` context analogous to `torch.cuda.graph`, a `@no_graph` decorator for eager regions, and a `CUDAGraphSequence` replaying segments and eager regions in order. With no break the block is a single segment, so standard CUDA Graphs fall out as the trivial case[^sgl-adv-cg].

The library can be used directly in another engine, training loop, or prototype without SGLang's runner stack; SGLang and the standalone library are expected to converge[^sgl-adv-cg].

## Coverage limits

- Chart figures under `../raw/2026-08-17-advanced-cuda-graph/assets/` (`bcg-design.svg`, `prefill-build.svg`, `prefill-ttft.svg`, `full-prefill.svg`, `cg-memory.svg`, `diffusion.svg`) were inspected only for headline numbers already stated in prose; exact per-point values were not transcribed[^sgl-adv-cg].
- Linked SGLang PRs #19102, #22218, #23906, #27436, #27988 and vLLM PR #9724 were not re-ingested beyond what the source states[^sgl-adv-cg].
- Contributors named in acknowledgments were not compiled as people concepts[^sgl-adv-cg].

## Relationships

- Uses [SGLang Attention Backends](sglang-attention-backends.md) — full prefill capture currently needs FA4/FlashInfer-style extend metadata, and hybrid prefill/decode selection interacts with which backend the graph captures.
- Uses [SGLang ViT CUDA Graphs for Multimodal Encoders](sglang-vit-cuda-graph.md) — ViT per-sequence-length encoder graphs are orthogonal to the LLM runner/backend prefill/decode graphs compiled here.
- Uses [vLLM CUDA Graphs Modes and Dispatch](vllm-cuda-graphs.md) — vLLM full/piecewise dispatcher and nested wrappers are the companion design for comparing SGLang runner/backend separation.
- Uses [SGLang Hyperparameter Tuning](sglang-hyperparameter-tuning.md) — `--cuda-graph-max-bs`, `--mem-fraction-static`, and `--chunked-prefill-size` sizing there interacts with capture ceiling and resident-graph memory here.
- Uses [SGLang Deterministic Inference](sglang-deterministic-inference.md) — deterministic mode is one of the rapidly evolving features BCG had to coexist with without compiler-boundary changes.

[^sgl-adv-cg]: Advanced CUDA Graph Techniques in SGLang — `../raw/2026-08-17-advanced-cuda-graph/index.md`, covering runner/backend split, Breakable CUDA Graph origin/mechanism/benefits/diffusion use, full prefill static shapes/padding/benchmarks, segmented-capture reuse and chunked-prefill ceiling, and standalone BCG library.
