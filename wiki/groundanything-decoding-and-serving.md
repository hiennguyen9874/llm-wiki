---
type: Concept
title: GroundAnything decoding and serving
description: GroundAnything serves one shared backbone through entropy-guided blockwise denoising or self-speculative decoding on a pinned custom SGLang stack, with CUDA Graph and selective FP8 left as unevaluated-by-default infrastructure layers.
tags: [visual-grounding, parallel-decoding, diffusion-decoding, inference-infrastructure, sglang, speculative-decoding]
status: draft
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T10:37:15+07:00 }
stale_after: 2027-04-25
sources:
  - id: groundanything-card
    resource: ../raw/GroundingPI-GroundAnything.md
    kind: model-card
    title: GroundAnything (DLM) model card
---

# GroundAnything decoding and serving

GroundAnything's parallel-decoding claim rests on two decoders over the same converted weights: entropy-guided blockwise denoising, which commits several response tokens per forward pass with no verification, and an optional self-speculative mode that drafts bidirectionally and verifies causally. Both run on a custom SGLang integration shipped inside the source bundle, because upstream SGLang alone does not reproduce the model adapter or the decoding integration.[^groundanything-card]

## Entropy-guided blockwise denoising

Image/query prefill creates a causal prefix cache plus a known anchor token. The release recipe uses block size 32, sub-block size 4, and entropy threshold 0.8: a physical block is the anchor plus 31 masked positions, and sub-blocks are completed left to right while each forward pass still evaluates the whole physical block.[^groundanything-card]

For every still-masked position in the active sub-block the decoder computes entropy from the unmodified token distribution over the generatable vocabulary, excluding the mask token. All positions at or below the threshold are committed together; if none qualifies, the single lowest-entropy position is committed so decoding advances. Committed tokens stay fixed. Once a block completes, one causal forward rebuilds its authoritative KV cache and supplies the next anchor — that pass does **not** verify or reject the block. A block needing D denoising passes therefore costs D + 1 model forwards, excluding the initial prefill.[^groundanything-card]

## Self-speculative decoding

The same shared weights draft with bidirectional attention and verify with causal attention. Verification accepts the longest consecutive matching prefix, stops at the first mismatch, applies the causal correction, and discards KV states for the rejected suffix.[^groundanything-card]

- The shipped route is the linear shared-weight schedule started by `--decoder speculative`; the card's figure also depicts a quadratic schedule that is not exposed as a documented service.[^groundanything-card]
- Verification is greedy, not a general stochastic speculative sampler.[^groundanything-card]
- "Exact" verification is exact relative to the converted model's causal branch, so accepted output need not equal the separately trained autoregressive checkpoint.[^groundanything-card]

At the paper's operating point this mode is reported at 4.51× over the autoregressive counterpart with a 0.74-percentage-point COCO F1-mIoU drop; that is a **reported** result, not a reproduced measurement.[^groundanything-card]

## Serving stack

| Aspect | GroundAnything (DLM) | GroundAnything-VLM |
|:---|:---|:---|
| Engine | Custom SGLang service, plus a native Transformers reference route | Custom SGLang service with its own config |
| Endpoint / model ID | `http://127.0.0.1:8101/v1`, `groundinganything` | `http://127.0.0.1:8102/v1`, `groundinganything-vlm` |
| Runtime record | `outputs/sglang/<decoder>/engine_runtime.json` | `outputs/sglang/vlm/engine_runtime.json` |

The documented environment is Linux x86_64 with Python 3.12. `python3 run.py setup serve` verifies and extracts the bundled frameworks, creates `.venv-serve`, prepares the custom SGLang implementation in the profile's dependency order, records resolved packages, and applies a required cuDNN compatibility selection; its dependency report carries a known Torch/cuDNN metadata exception. Serving and evaluation use separate environments.[^groundanything-card]

The serving profile pins Torch 2.9.1, Transformers 5.5.4, Triton 3.5.1, sgl-kernel 0.3.20, and FlashInfer 0.5.3, and is tested on NVIDIA B300, B200, H200, H800, and PPU. The provided installer is a CUDA/GPU recipe, so PPU needs its own platform runtime and is not selected by it.[^groundanything-card]

Default DLM settings are BF16, Triton attention, eager execution, one GPU, one active request, and two queued requests. Client concurrency queues work; it does not turn the default queue into continuous multi-request batching, so higher throughput requires independent replicas with distinct devices, ports, and output directories. The published DLM demo is not supported on ZeroGPU.[^groundanything-card]

Model-specific cache semantics must survive optimization: denoising attends bidirectionally inside the active block while completed history stays as causal KV, and self-speculation additionally verifies proposals and drops rejected suffix states.[^groundanything-card]

## CUDA Graph and selective FP8

The paper's progressive infrastructure sequence is native PyTorch eager (reference), SGLang eager (the default serving path), CUDA Graph replay, then selective FP8. Only the first two are active in the supplied recipe; the graph replay and FP8 layers are **evaluated in the paper and disabled by the default launcher**.[^groundanything-card]

- CUDA Graph changes how compatible GPU work is submitted and defines no new commitment or verification rule; captured shapes and state updates must stay compatible with the active decoder. No public `run.py serve --cuda-graph` switch exists in this release.[^groundanything-card]
- The graph implementation captures fixed-shape block work: a FlashInfer path with persistent attention masks and device-resident buffers for bidirectional drafting and causal verification, and a Triton verifier path that separates draft/verification metadata and input buffers while sharing parameters and the real KV pool. Its only supported capture case is block size 32 with one request and no tensor, pipeline, or data parallelism; prefill and other shapes fall back to eager, and optional shadow checks compare cache states, logits, and token choices against eager.[^groundanything-card]
- Selective FP8 applies to eligible language-model linear operations while other components stay BF16. Because it can change logits and later decoding decisions, it is a distinct numerical configuration rather than a pure speedup.[^groundanything-card]
- The paper's cumulative infrastructure speedups compare execution implementations *within* one decoding mode and are separate from the self-speculation-versus-autoregressive headline.[^groundanything-card]

## Client usage

A thin HTTP client holds no weights: `GroundingAnything(base_url=..., model="groundinganything")` followed by `predict(image, prompt, task="bbox"|"point")`, with `result.valid` gating visualization and `result.to_dict()` exposing parsed predictions and the raw text. Switching between the denoise and speculative decoders reuses the same DLM weights and endpoint, but the existing service must be stopped first.[^groundanything-card]

## Coverage and trust limits

- Every runtime statement here is **observed** from the card's static text; no command in this repository was executed, and no engine, kernel, or latency measurement was reproduced.
- The card documents no throughput, latency, memory, or accuracy numbers per serving configuration — neither for the default eager path nor for the optional graph and FP8 layers — so the infrastructure claims cannot be compared numerically from this source.[^groundanything-card]
- The source bundle retains only the model card; the source repository, `run.py`, the SGLang patch, the configs, the license text, and the arXiv paper are linked but absent from `raw/`, so configuration precedence and platform-specific behaviour in the installed recipe are unverified.[^groundanything-card]
- The pinned dependency set and hardware list are time-sensitive: treat the environment matrix as a snapshot of the card at capture time.[^groundanything-card]

## Relationships

- **Part of:** [GroundAnything](groundanything.md), which holds the architecture, output protocol, tasks, and reported benchmark results.
- **Contrasts with:** [MinerU-Diffusion](mineru-diffusion.md), which exposes denoising steps, generated length, block length, and a low-confidence remasking threshold through Transformers `generate` rather than a custom SGLang service.
- **Related to:** [HunyuanOCR-1.5](hunyuanocr-1.5.md) and [LightOnOCR-3 deployment](lightonocr-3-deployment.md) as other document-model releases where decoding acceleration and serving configuration decide practical usability.

[^groundanything-card]: GroundingPI, *GroundAnything (DLM) model card*, local capture at [GroundingPI-GroundAnything.md](../raw/GroundingPI-GroundAnything.md), § Software Integration, § Model Version(s), § Inference, § Generation Modes (Entropy-guided decoding; Self-speculative decoding), § Inference Infrastructure, and § Ethical Considerations (accessed 2026-10-25).
