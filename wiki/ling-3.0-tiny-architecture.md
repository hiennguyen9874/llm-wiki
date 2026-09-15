---
type: Concept
title: Ling-3.0-tiny Architecture and Evaluation
description: InclusionAI 7.9B (1.3B active) hybrid-linear MoE with 3:1 KDA plus Gated MLA, 128-expert MoE, and edge-efficient agentic benchmark evidence.
tags: [ling, inclusionai, hybrid-attention, linear-attention, mla, moe, mtp, agentic-coding, evaluation, long-context, edge]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: ling-card
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny.md
    title: Ling-3.0-tiny model card
  - id: ling-arch
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny-architecture.png
    title: Ling-3.0-tiny architecture diagram
  - id: ling-bench
    resource: ../raw/Ling-3.0-tiny/Ling-3.0-tiny-benchmark.png
    title: Ling-3.0-tiny benchmark comparison table
---

Ling-3.0-tiny is InclusionAI's 7.9B-total lightweight hybrid-reasoning MoE that pairs 3:1 Kimi Delta Attention with Gated MLA plus 128-expert MoE and MTP training to deliver agentic and reasoning capability at 1.3B active parameters for local and edge deployment[^ling-card][^ling-arch].

## Model identity and scale

- Native hybrid-reasoning model from inclusionAI; `inclusionAI/Ling-3.0-tiny`[^ling-card].
- 7.9B total parameters; card states 1.3B activated per token (see Contradictions for the diagram's 1.4B label)[^ling-card][^ling-arch].
- BF16, FP8, and INT4 weights provided for hardware and deployment coverage[^ling-card].
- Vocabulary 157k; embedding dimension 1,536; first block dense FFN hidden size 4,608[^ling-arch].
- Context posture: RoPE with supported content length of 1M tokens in the diagram; SGLang recipe serves 256K via YaRN; Ollama default context 8,192[^ling-arch][^ling-card].
- Training objective: next-token prediction plus Multi-Token Prediction (MTP)[^ling-arch].
- For launch paths and edge performance, see [Ling-3.0-tiny Inference and Serving](ling-3.0-tiny-inference.md).

## Hybrid-linear architecture

- 3:1 alternating stacking: 3 KDA layers followed by 1 MLA layer per 4-layer block; diagram groups this as 6 groups × (3 KDA + 1 Gated MLA), implying 18 KDA + 6 Gated MLA layers[^ling-card][^ling-arch].
- KDA side is labeled linear-time complexity; diagram details Conv plus Swish (δ) on Q/K/V paths, L2 Norm on Q/K, direct V path, and sigmoid-gated α/β branches feeding Kimi Delta Attention, then RMSNorm and sigmoid-gated output projection[^ling-arch].
- Gated MLA side: Linear → RMSNorm → Linear → RoPE Q/K branches with shared K/V linkage into Multi-head Latent Attention, then sigmoid-gated output projection[^ling-arch].
- Block pattern is RMSNorm → attention (KDA or Gated MLA) → residual add → RMSNorm → MoE/dense FFN → residual add, capped by Final RMSNorm plus Linear Output Layer[^ling-arch].
- Native hybrid reasoning: fast responses for routine tasks and multi-step reasoning for complex tasks in one model; thinking mode configurable per request through `enable_thinking` and enabled by default[^ling-card].

## MoE configuration

- 128 routed experts + 1 shared expert, 8 routed activated per token (E128A8 + 1 shared), ALF-LB load-balancing label in the diagram[^ling-card][^ling-arch].
- First 1 block uses dense FFN with hidden size 4,608 instead of MoE; remainder use MoE[^ling-arch].

## Evaluation snapshot

Vendor-reported thinking-mode results; competitors are Qwen3.5-4B (Thinking), Qwen3.5-9B (Thinking), Gemma-4-E4B-it (Thinking), and Gemma-4-12B-it (Thinking)[^ling-bench].

- Artificial Analysis Intelligence Index v4.1.1: 25; Agentic Index: 16[^ling-card].
- Artificial Analysis speed: over 160 tokens/s output with approximately 18 seconds end-to-end latency for a 500-token response including reasoning time[^ling-card].
- General Agent — GDPval v2-AA: Ling 772.00 vs Qwen-4B –, Qwen-9B 644.00, Gemma-4B 228.00, Gemma-12B 645.00[^ling-bench].
- General Agent — TAU3-Banking-AA: Ling 20.80 vs 6.80 / 7.00 / 5.40 / 8.70[^ling-bench].
- General Agent — BFCL-v4 (FC): Ling 62.72 vs 62.47 / 65.83 / 41.64 / 59.68[^ling-bench].
- Coding Agent — Terminal-Bench 2.1: Ling 27.70 vs 25.80 / 29.20 / 1.90 / 27.30[^ling-bench].
- Coding Agent — ArtifactsBench: Ling 47.93 vs 30.61 / 38.80 / 45.14 / 48.08[^ling-bench].
- Coding — SciCode: Ling 24.20 vs 16.10 / 27.50 / 24.40 / 38.20[^ling-bench].
- Long Context — AA-LCR: Ling 58.70 vs 61.00 / 65.30 / 33.00 / 61.70[^ling-bench].
- Knowledge — AA-Omniscience Accuracy: Ling 8.52 vs 15.12 / 16.42 / 8.58 / 15.62; Non-Hallucination rate: Ling 69.54 vs 13.45 / 16.39 / 69.06 / 19.02[^ling-bench].
- Reasoning — GPQA Diamond: 73.40 vs 77.10 / 80.60 / 57.60 / 75.30; HLE: 9.30 vs 9.90 / 14.90 / 3.80 / 15.70; HMMT-Feb26: 70.31 vs 72.87 / 71.21 / 33.85 / 67.95; IMO-AnswerBench: 71.03 vs 63.69 / 70.00 / 31.75 / 64.09[^ling-bench].
- Instruction Following — IFBench: 63.61 vs 52.00 / 66.70 / 44.20 / 73.50; LIFEBench: 62.30 vs 63.30 / 63.90 / 52.80 / 65.30; Multi-IF: 83.15 vs 79.84 / 83.03 / 80.92 / 88.44[^ling-bench].

## Evaluation methodology

- Recommended sampling: thinking on by default, `temperature=1.0, top_p=0.95, top_k=20`[^ling-card].
- Terminal-Bench 2.1: Artificial Analysis protocol using default Terminus 2 harness, unified 2-hour timeout, provided JSON parser in preserve-thinking mode, 3 runs per task (mean); decoding `temperature=1.0, max_new_tokens=32K` with 256K context window[^ling-card].

## Relationships

- Related to [Ling-3.0-flash Architecture and Evaluation](ling-3.0-flash-architecture.md) — larger 124B/5.1B Ling-3.0 sibling with 5:1 KDA plus Gated MLA, 512-expert MoE, and the same NTP+MTP plus RoPE/1M-context posture.
- Related to [Ling-3.0-tiny Inference and Serving](ling-3.0-tiny-inference.md) — SGLang, vLLM, and Ollama/MLX recipes plus DGX Spark and Apple Silicon performance for this checkpoint.
- Uses [SGLang Reasoning Parser](sglang-reasoning-parser.md) — `ling3` parser context behind the thinking-enabled default and per-request toggle.
- Uses [SGLang Tool Parser](sglang-tool-parser.md) — `ling3` tool-call parsing context behind the serving recipes.

## Contradictions

- Activated parameters per token: model card states 1.3B[^ling-card], while the architecture diagram resource-saving label states 1.4B activated per inference step[^ling-arch]. Both values are preserved here without choosing one; the frontmatter description follows the card's 1.3B.

## Coverage limits

- All benchmark, index-score, speed, latency, memory, and hardware-validation claims are vendor-reported and not independently verified[^ling-card][^ling-bench].
- Remote model-card images hosted on CDN/Hugging Face upload URLs were not fetched; architecture and benchmark evidence comes from the card prose plus the two inspected local PNGs[^ling-card][^ling-arch][^ling-bench].
- No credentials, private keys, tokens, or PII were found; the serving placeholder token pattern is documented in the companion serving concept without value.

[^ling-card]: Ling-3.0-tiny model card — `../raw/Ling-3.0-tiny/Ling-3.0-tiny.md`, 7.9B/1.3B hybrid-reasoning identity with 3:1 KDA–MLA and 128-expert MoE (8+1 active), BF16/FP8/INT4 weights, DGX Spark plus Apple Silicon validation with FP8 throughput and 8K-context memory figures, AA Intelligence/Agentic indexes with speed/latency snapshot, thinking-on sampling defaults with Terminal-Bench 2.1 protocol, and SGLang plus vLLM plus Ollama quickstarts.
[^ling-arch]: Ling-3.0-tiny architecture diagram — `../raw/Ling-3.0-tiny/Ling-3.0-tiny-architecture.png`, 6-group 3×KDA+1×Gated-MLA layout with 1 dense-first block (hidden 4,608), E128A8+1-shared ALF-LB MoE, 157k vocab, 1,536 embedding, 1M RoPE support, linear-time KDA, NTP+MTP objective, and Gated-MLA versus KDA internal blocks with sigmoid/swish/conv/L2-Norm detail.
[^ling-bench]: Ling-3.0-tiny benchmark table — `../raw/Ling-3.0-tiny/Ling-3.0-tiny-benchmark.png`, thinking-mode comparison across GDPval v2-AA, TAU3-Banking-AA, BFCL-v4, Terminal-Bench 2.1, ArtifactsBench, SciCode, AA-LCR, AA-Omniscience accuracy/non-hallucination, GPQA Diamond, HLE, HMMT-Feb26, IMO-AnswerBench, IFBench, LIFEBench, and Multi-IF against Qwen3.5-4B/9B and Gemma-4-E4B/12B thinking variants.
