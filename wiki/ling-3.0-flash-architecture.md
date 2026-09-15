---
type: Concept
title: Ling-3.0-flash Architecture and Evaluation
description: InclusionAI 124B (5.1B active) hybrid-linear MoE with 5:1 KDA plus Gated MLA, 512-expert MoE, MTP training, and agentic benchmark evidence.
tags: [ling, inclusionai, hybrid-attention, linear-attention, mla, moe, mtp, agentic-coding, evaluation, long-context]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: ling-card
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash.md
    title: Ling-3.0-flash model card
  - id: ling-arch
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash-architecture.png
    title: Ling-3.0-flash architecture diagram
  - id: ling-bench
    resource: ../raw/Ling-3.0-flash/Ling-3.0-flash-benchmark.png
    title: Ling-3.0-flash benchmark comparison chart
---

Ling-3.0-flash is InclusionAI's 124B-total / 5.1B-active native hybrid-reasoning model that pairs 5:1 Kimi Delta Attention with Gated MLA plus 1/64 sparse MoE and MTP training to match or exceed the prior 1T-class Ring-2.6-1T flagship at roughly one-eighth the active parameters[^ling-card][^ling-arch].

## Model identity and scale

- Native hybrid-linear reasoning model from inclusionAI; `inclusionAI/Ling-3.0-flash`[^ling-card].
- 124B total / 5.1B active, described as ~12.4% total and ~8.1% active versus Ring-2.6-1T, with parity-or-better claims across key benchmarks[^ling-card][^ling-bench].
- Vocabulary 157,184 (diagram labels 157k); embedding dimension 2,560; hidden 2560; 32 attention heads[^ling-card][^ling-arch].
- Context training schedule 8K → 32K → 256K; diagram labels RoPE with supported content length of 1M tokens[^ling-card][^ling-arch].
- Training objective: next-token prediction plus Multi-Token Prediction (MTP)[^ling-arch].
- For production launch paths, see [Ling-3.0-flash Inference and Serving](ling-3.0-flash-inference.md).

## Hybrid-linear architecture

- Native hybrid linear attention from start of pretraining: 5:1 alternating stacking of Kimi Delta Attention (KDA) and MLA, upgraded with KDA fine-grained diagonal gating[^ling-card].
- Layer count: 35 KDA + 7 Gated MLA in 5:1 ratio; diagram groups them as 5× KDA block plus 1× Gated MLA block repeated in 7 groups[^ling-card][^ling-arch].
- KDA side is linear-time; diagram details Conv plus Swish (δ), L2 Norm on Q/K, direct V path, and sigmoid-gated α/β branches feeding Kimi Delta Attention, then RMSNorm and sigmoid-gated output projection[^ling-card][^ling-arch].
- Gated MLA side: Linear → RMSNorm → Linear → RoPE Q/K branches with shared K/V linkage into Multi-head Latent Attention, then sigmoid-gated output projection[^ling-arch].
- First 2 blocks use dense FFN instead of MoE; remainder use MoE[^ling-arch].

## MoE configuration

- 1/64 sparse MoE: 512 routed experts + 1 shared expert, 8 activated per token (E512A8), ALF-LB load balancing label in diagram[^ling-card][^ling-arch].
- Expert intermediate size 768; dense intermediate size 6144; 2 dense layers[^ling-card].
- Block pattern is RMSNorm → attention (KDA or Gated MLA) → residual add → RMSNorm → MoE/dense FFN → residual add, capped by Final RMSNorm plus Linear Output Layer[^ling-arch].

## Agentic evolution and efficiency

- Tailored for Coding, General, and Deep Research Agent closed-loop execution with 10,000+ interactive training environments[^ling-card].
- Natively integrates SGLang HiCache + Mooncake hierarchical caching with physical dual-pools and cluster-shared L3, claimed to cut Time to First Token by 60% to over 80% in long-input scenarios by removing redundant recomputation in long-horizon interactions[^ling-card].
- Activating only 5.1B parameters per token is positioned for reasoning, instruction following, long-context, and complex agentic workflows in production[^ling-card].

## Evaluation snapshot

Vendor-reported chart with thinking mode enabled by default; competitors are Ring-2.6-1T (xhigh), MiniMax-M2.7, Step-3.7-Flash (high), Deepseek-V4-Flash-Preview (max), Nemotron-3-Super-120B-A12B, GPT-5.4-mini (high), Claude-Sonnet-4.6 (max)[^ling-bench].

- SWE-Bench Pro: Ling 56.6 vs Ring 53.9, MiniMax 56.2, Step 56.3, DeepSeek 52.6, Nemotron 34.1, GPT 47.9, Claude 48.3[^ling-bench].
- SWE-Bench Multilingual: Ling 72.4 vs Ring 56.7, MiniMax 76.5, Step 72.4, DeepSeek 73.3, Nemotron 42.7, GPT 71.0, Claude 75.9[^ling-bench].
- Terminal-Bench 2.1: Ling 57.0 vs Ring 43.1, MiniMax 55.0, Step 39.3, DeepSeek 62.0, Nemotron 39.0, GPT 55.8, Claude 71.2[^ling-bench].
- Tau3-banking-AA: Ling 28.0 vs Ring 14.6, MiniMax 8.9, Step 11.3, DeepSeek 22.9, Nemotron 10.1, GPT 11.3, Claude 30.5[^ling-bench].
- MCP-Atlas (500-task public set): Ling 65.5 vs Ring 61.2, MiniMax 53.6, Step 52.6, DeepSeek 69.0, Nemotron 49.4, GPT 55.2, Claude 66.7[^ling-card][^ling-bench].
- SkillsBench (87 tasks): Ling 44.8 vs Ring 11.9, MiniMax 28.4, Step 24.9, DeepSeek 53.5, Nemotron 20.3, GPT 44.8, Claude 54.4[^ling-card][^ling-bench].
- WideSearch: Ling 73.6 vs Ring 62.2, MiniMax 75.2, Step 56.8, DeepSeek 74.4, Nemotron 19.5, GPT 70.2, Claude 79.5[^ling-bench].
- BrowseComp single-agent with context / multi-agent: Ling 72.2 / 82.0 vs Claude 74.0 / 82.1; others single-point Ring 71.7, MiniMax 76.3, Step 75.8, DeepSeek 73.2, Nemotron 31.3[^ling-bench].
- IFBench: Ling 74.5 vs Ring 44.6, MiniMax 75.7, Step 67.3, DeepSeek 79.2, Nemotron 72.6, GPT 69.0, Claude 56.6[^ling-bench].
- SysBench: Ling 93.6 vs Ring 86.5, MiniMax 86.2, Step 91.4, DeepSeek 93.9, Nemotron 90.7, GPT 93.3, Claude 94.9[^ling-bench].
- MRCR-256k: Ling 81.1 vs Ring 76.5, Step 25.7, DeepSeek 84.3, Nemotron 35.8, GPT 50.5, Claude 92.7; MiniMax bar not legible in inspected chart[^ling-bench].
- Multi-IF: Ling 87.7 vs Ring 89.3, MiniMax 82.9, Step 84.6, DeepSeek 86.2, Nemotron 82.3, GPT 84.6, Claude 84.8[^ling-bench].
- Card also claims strong user experience in Claude Code, Kilo Code, Qwen Code, Hermes Agent, and OpenClaw, plus general knowledge, math reasoning, instruction following, and long-context strength[^ling-card].

## Evaluation methodology

- Default sampling unless noted: thinking on, `temperature=0.6, top_p=0.95, top_k=20`[^ling-card].
- SWE-Bench series: OpenHands harness with tailored prompts; `temperature=0.6, top_p=0.95, max_new_tokens=32K`, 256K context[^ling-card].
- Terminal-Bench 2.1: Artificial Analysis protocol, Terminus 2 harness, 2-hour timeout, preserve-thinking JSON parser, 3 runs mean; `temperature=0.6, top_p=1.0, max_new_tokens=32K`, 256K context[^ling-card].
- MiniAppBench: 500 tasks turning single requests into interactive HTML apps; `temperature=1.0, top_p=1.0, max_tokens=128K`[^ling-card].
- AntSWEBench: internal software-engineering suite over Java/JavaScript/Python covering features, bug fixes, refactoring[^ling-card].
- Tau3-banking-AA: AA leaderboard alignment with GPT-5.4-mini medium-reasoning user simulator and assertion judge[^ling-card].
- MCP-Atlas: official v1 harness, 20-turn limit, Gemini-2.5-Pro claim-coverage judger[^ling-card].
- SkillsBench: kilo-code, 87 non-external-API tasks, mean of 3 runs[^ling-card].
- GDPval v2-AA: 220-task public set, Stirrup harness, 250-turn limit, 5-hour timeout[^ling-card].
- Search-agent: internal harness; single-agent ReAct, multi-agent for BrowseComp; pass@1 mean; WideSearch uses official prompt plus GPT-4.1 judge on corrected dataset; Draco uses official rubrics with Claude Opus 4.6 scorer; BrowseComp single-agent resumes from 64K-token summary; multi-agent uses SearchSwarm/Tongyi DeepResearch harness at `temperature=0.85, top_p=0.95, max_tokens=8K` with 128K main / 64K sub-agent windows[^ling-card].

## Relationships

- Uses [SGLang HiCache Best Practices](sglang-hicache-best-practices.md) — hierarchical KV-cache tuning context for the claimed HiCache plus Mooncake TTFT reduction.
- Uses [SGLang HiCache System Design](sglang-hicache-design.md) — three-tier HiRadixTree plus prefetch/write-back design behind the physical dual-pool and shared-L3 claim.
- Related to [GLM-5.3-Flash Architecture and Evaluation](glm-5.3-flash-architecture.md) — another Flash-class hybrid linear-sparse MoE at 320B/18B with 1M-context and Flash-cost positioning.
- Related to [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) — DeepSeek-V4-Flash-Preview appears as a direct chart competitor on the same agentic and long-context suites.
- Related to [Ling-3.0-flash Inference and Serving](ling-3.0-flash-inference.md) — production SGLang and vLLM recipes for this checkpoint.

## Coverage limits

- All benchmark, TTFT-reduction, Ring-2.6 comparison, and framework-experience claims are vendor-reported and not independently verified[^ling-card][^ling-bench].
- Remote model-card images hosted on intranet/CDN URLs were not fetched; architecture and benchmark evidence comes from the two inspected local PNGs[^ling-arch][^ling-bench].
- MRCR-256k MiniMax value was illegible in the inspected benchmark PNG and is omitted rather than estimated[^ling-bench].
- No credentials, private keys, tokens, or PII were found; the serving placeholder token pattern is documented in the companion serving concept without value.

[^ling-card]: Ling-3.0-flash model card — `../raw/Ling-3.0-flash/Ling-3.0-flash.md`, 124B/5.1B hybrid-reasoning identity with Ring-2.6-1T comparison, 5:1 KDA+MLA with diagonal gating and 1/64 MoE, 35+7 layer and 512+1-expert config with 8K→32K→256K schedule, 10k+ agentic environments, HiCache+Mooncake 60–80%+ TTFT claim, benchmark suite list with harness/decoding protocols, and SGLang plus vLLM quickstarts.
[^ling-arch]: Ling-3.0-flash architecture diagram — `../raw/Ling-3.0-flash/Ling-3.0-flash-architecture.png`, 7-group 5×KDA+1×Gated-MLA layout with 2 dense-first blocks, E512A8+1-shared ALF-LB MoE, 157k vocab, 2560 embedding, 1M RoPE support, NTP+MTP objective, and Gated-MLA versus KDA internal blocks with sigmoid/swish/conv/L2-Norm detail.
[^ling-bench]: Ling-3.0-flash benchmark chart — `../raw/Ling-3.0-flash/Ling-3.0-flash-benchmark.png`, 12-panel vendor comparison across SWE-Bench Pro/Multilingual, Terminal-Bench 2.1, Tau3-banking-AA, MCP-Atlas, SkillsBench, WideSearch, BrowseComp single/multi, IFBench, SysBench, MRCR-256k, and Multi-IF with thinking-on note.
