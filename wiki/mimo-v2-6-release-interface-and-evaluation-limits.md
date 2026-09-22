---
type: Concept
title: MiMo-V2.6 release interface and evaluation limits
description: MiMo-V2.6 Pro/Flash model cards expose checkpoint-specific serving recipes and broad agent scores, but the supplied bundle lacks weights, processors, harnesses, immutable revisions, and end-to-end reproduction evidence.
tags: [mimo-v2-6, deployment, evaluation, transformers, reproducibility]
status: stable
created: 2026-09-22
generated: { by: llm-wiki-agent/1, at: 2026-09-22T15:39:12Z }
sources:
  - id: mimo-v2-6-checkpoint-bundle-2026
    resource: ../raw/MiMo-V2.6-Sources/MiMo-V2.6-Flash-RL.md
    scope: ../raw/MiMo-V2.6-Sources/
    kind: code
    title: MiMo-V2.6 Pro/Flash release bundle
---

# MiMo-V2.6 release interface and evaluation limits

The MiMo-V2.6 Pro-RL and Flash-RL cards present a flagship 1.02T/42B-active checkpoint and an efficiency-oriented 309B/15B-active checkpoint, both with reported one-million-token and text/image/video/audio support. They provide SGLang and vLLM launch recipes plus a broad vendor benchmark table, but the local release bundle is a static interface snapshot rather than a runnable or reproducible checkpoint release: it has no weights, tokenizer or processor code, chat template, evaluation harness, dependency manifest, or immutable upstream revision.[^mimo-v2-6-checkpoint-bundle-2026]

## Reported evaluation

The shared table covers code agents, general agents, cybersecurity, and visual coding. Pro exceeds Flash on most listed rows—for example DeepSWE v1.1 71.9 versus 67.9, Terminal Bench 4.0 34.9 versus 28.8, and MiMo VisualCoding 72.3 versus 71.5—while Flash is higher on CyberGym (95.1 versus 94.0); Flash has no GDPval-AA 2.1 result. The cards also compare against MiMo-V2.5 Pro and named proprietary systems.[^mimo-v2-6-checkpoint-bundle-2026]

These are **reported** point estimates. The cards do not provide prompts, sampling counts, uncertainty, contamination checks, reasoning budgets, tool policies, complete harness configurations, or an explanation of the benchmark-specific units. Comparisons to proprietary systems therefore cannot be treated as controlled architecture or cost comparisons, and the final scores do not isolate mixed RL from subsequent distillation.[^mimo-v2-6-checkpoint-bundle-2026]

## Serving recipes

The cards recommend SGLang with remote code, chunked prefill, MiMo reasoning/tool parsers, and EAGLE-style multi-layer speculation. Flash is shown with tensor parallelism 8 and data parallelism 2; Pro is a two-node recipe with tensor parallelism 16, data parallelism 2, expert parallelism 16, DeepEP, and a 32,768-token prefill chunk. The vLLM examples use tensor parallelism 4 for Flash and 8 for Pro. Both recommend `temperature=1.0` and `top_p=0.95`.[^mimo-v2-6-checkpoint-bundle-2026]

These commands are vendor recommendations, not reproduced procedures. They point to MiMo-V2.5 cookbooks or images, use `--trust-remote-code`, and do not pin a model commit, container digest, SGLang version, hardware topology, or vLLM build. Stable vLLM is explicitly said to potentially lag. The supplied Transformers configs declare version 5.3.0, BF16 model dtype, and quantization metadata describing dynamic E4M3 activations with MXFP4-stored weights, but no weights are present to inspect or load.[^mimo-v2-6-checkpoint-bundle-2026]

## Reference-code boundaries

Static inspection establishes a Transformers model/config API, not parity with the optimized serving recipes:

- `MiMoV2ForCausalLM.forward` accepts token IDs or embeddings plus image/video pixels or precomputed embeddings and audio codes or embeddings. It validates that each modality embedding count exactly matches its placeholder-token count.
- The bundled code rejects paged attention caches. If an SWA attention-sink bias is configured with SDPA, it falls back to eager attention; optimized kernels may instead receive the sink as an auxiliary argument.
- The only implemented MoE route, `noaux_tc`, raises during training, making this remote implementation inference-only for the supplied configs.
- The audio-tokenizer loader requires a separate directory containing its config and weights. The top-level model forward accepts audio codes or embeddings, not raw mel inputs, and no such tokenizer artifact is included.
- The code does not instantiate the advertised speculative decoder; optimized EAGLE/DFlash behavior therefore belongs to an external serving path or omitted checkpoint implementation rather than this reference class.

Python syntax compilation and JSON parsing were reproduced locally, but imports, model construction, checkpoint loading, multimodal preprocessing, inference, and serving were not executed because dependencies and weights are absent.[^mimo-v2-6-checkpoint-bundle-2026]

## Disclosure and coverage

All six supplied files were statically inspected: two model cards, two checkpoint configs, and the shared configuration and modeling modules. The model cards declare MIT, while both Python files carry Apache-2.0 headers; the configs contain no separate license declaration, so the precise license boundary across code, configuration, and remote weights is not established by this snapshot. The cards reference `assets/architecture.png`, but that attachment is absent. No generated, vendored, binary, or hidden artifacts were found in the local directory.[^mimo-v2-6-checkpoint-bundle-2026]

## Relationships

- **Implements:** [MiMo-V2.6 omni-modal hybrid-SWA architecture](mimo-v2-6-omnimodal-hybrid-swa-architecture.md) partially through a Transformers reference path.
- **Reports results for:** [MiMo-V2.6 scaled agentic reinforcement learning](mimo-v2-6-scaled-agentic-rl.md), without isolating RL from MOPD2 or providing complete evaluation protocols.
- **Depends on:** external SGLang or vLLM integrations for the documented optimized serving and speculative-decoding paths.

[^mimo-v2-6-checkpoint-bundle-2026]: Xiaomi MiMo Team, [MiMo-V2.6-Flash-RL card](../raw/MiMo-V2.6-Sources/MiMo-V2.6-Flash-RL.md) and package, 2026. Evaluation table and Sections 4–5; Pro-specific values and commands in `MiMo-V2.6-Pro-RL.md`; checkpoint keys in `MiMo-V2.6-{Flash,Pro}-RL.config.json`; implementation at `configuration_mimo_v2.py::MiMoV2Config` and `modeling_mimo_v2.py::{MiMoV2MoEGate,MiMoV2Attention,MiMoAudioEncoder,MiMoV2ForCausalLM}`. Static syntax/JSON checks reproduced 2026-09-22; no immutable upstream revision was supplied.
