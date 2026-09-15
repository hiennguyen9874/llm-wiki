---
type: Concept
title: GLM-5 Evaluation and Deployment
description: ARC and base benchmark evidence, automated CC-Bench-V2 real-world engineering results, general-ability gains, Chinese-chip adaptation, and Pony Alpha release note.
tags: [glm-5, evaluation, benchmarks, agentic-coding, cc-bench, swe-bench, browsecomp, chinese-chips, deployment]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: glm5-intro
    resource: ../raw/arXiv-2602.15763v2/1_intro.tex
    title: GLM-5 Introduction — headline ARC/Arena/AA/Vending results
  - id: glm5-eval
    resource: ../raw/arXiv-2602.15763v2/4_evaluation.tex
    title: GLM-5 Evaluation — ARC, CC-Bench-V2, SWE-rebench, general abilities
  - id: glm5-chips
    resource: ../raw/arXiv-2602.15763v2/3.2_domestic.tex
    title: GLM-5 Chinese-chip adaptation — Ascend case study
  - id: glm5-concl
    resource: ../raw/arXiv-2602.15763v2/5_conclusion.tex
    title: GLM-5 Conclusion and Pony Alpha easter egg
  - id: glm5-appendix
    resource: ../raw/arXiv-2602.15763v2/9_appendix.tex
    title: GLM-5 Appendix — base table and ARC eval settings
---

GLM-5 is reported ~20% above GLM-4.7 on eight ARC benchmarks, near Claude Opus 4.5 / GPT-5.2-xhigh and above Gemini 3 Pro, with open-leading Artificial Analysis 50, #1-open LMArena Text/Code, and $4,432 Vending-Bench 2 showing long-horizon gains[^glm5-intro].

## Base-model benchmarks

- Base faces DeepSeek-V3-Base (37B/671B), Kimi-K2-Base (32B/1043B), GLM-4.5-Base (32B/355B) at 40B/744B[^glm5-appendix].
- Reported GLM-5-Base: SimpleQA 36.0, BBH 87.4, MMLU 88.3, HellaSwag 88.1, PIQA 84.6, TriviaQA 80.9; EvalPlus 87.0, LiveCodeBench-Base 34.4; GSM8K 68.8, MATH 56.4 (math below Kimi-K2/DeepSeek-V3/GLM-4.5 bases); CLUEWSC 84.2, C-Eval 88.8, C3 80.3, Chinese-SimpleQA 74.6[^glm5-appendix].

## ARC headline table

Reasoning/general (HLE text-only unless marked, GPT-5.2-medium judge; 131K gen, 202,752 for HLE-tools)[^glm5-eval][^glm5-appendix]:

- HLE 30.5 vs GLM-4.7 24.8 / V3.2 25.1 / K2.5 31.5 / Opus 28.4 / Gemini 37.2 / GPT-5.2 35.4; HLE-with-tools 50.4 second to K2.5 51.8, above Opus/Gemini/GPT full-set marks[^glm5-eval].
- AIME 2026-I 92.7 (Opus 93.3 best); HMMT Feb 97.9 and Nov 96.9 both second to GPT-5.2 (99.4/97.1) and above Opus/Gemini; IMO-AnswerBench 82.5; GPQA-Diamond 86.0; LongBench-v2 64.5 second to Gemini 68.2[^glm5-eval].

Coding (SWE via OpenHands tailored prompt `temp 0.7/top_p 0.95/16K/200K`; Terminal-Bench via Terminus-2 and Claude Code; CyberGym in Claude Code 2.1.18)[^glm5-eval][^glm5-appendix]:

- SWE-bench Verified 77.8 (Opus 80.9, GPT-5.2 80.0) above Gemini 76.2; Multilingual 73.3 second to Opus 77.5, above Gemini 65.0 and GPT-5.2 72.0[^glm5-eval].
- Terminal-Bench 2.0 Terminus-2 56.2 (verified-instruction split 60.7) vs Opus 59.3; Claude Code 56.2 (verified 61.1) vs Opus 57.9; consistent across harnesses; verified split fixes ambiguous instructions (`zai-org/terminal-bench-2-verified`)[^glm5-eval].
- CyberGym 43.2 second to Opus 50.6, up from GLM-4.7 23.5[^glm5-eval].

Agentic (BrowseComp discard-all like V3.2/K2.5 unless hierarchical CM noted; tau2 Retail/Telecom anti-premature-termination prompt plus Airline Opus-card fixes; MCP-Atlas 500-task public set 10-min timeout Gemini-3-Pro judge; Vending by Andon Labs)[^glm5-eval][^glm5-appendix]:

- BrowseComp 62.0 best frontier; with context management 75.9 best; BrowseComp-ZH 72.7 second to GPT-5.2 76.1, above Opus/Gemini[^glm5-eval].
- tau2-Bench 89.7 vs Opus 91.6; MCP-Atlas 67.8 second to GPT-5.2 68.0; Tool-Decathlon 39.2 vs GPT-5.2 46.3; Vending-Bench 2 $4,432 vs Gemini $5,478 / Opus $4,967 / GPT-5.2 $3,591; GDPval-AA Elo 1,409 (2026-02-15) second to GPT-5.2 1,462, above Opus 1,400[^glm5-eval].
- AA Intelligence Index v4.0 50 vs GLM-4.7 42, first open-weights 50 across GDPval-AA, tau2-Telecom, Terminal-Bench Hard, SciCode, AA-LCR, AA-Omniscience, IFBench, HLE, GPQA Diamond, CritPt; LMArena #1 open in Text and Code, overall near Opus-4.5/Gemini-3-Pro[^glm5-intro].

## CC-Bench-V2 real-world engineering

- Fully automated internal suite with no human labeling: Claude Code/other harnesses plus unit tests and Agent-as-a-Judge; splits frontend, backend, long-horizon[^glm5-eval].
- Frontend covers Business Systems (42/167), Web Games (40/163), SVG/Canvas (32/166), Creative Tools (28/160), Showcase (27/115), Forms/Tables (26/93), Data Viz (25/85); stacks HTML 113/490, React 58/249, Vue 49/210; total 220 tasks after expert removal of trivial items; each task plus checklist plus dedicated environment[^glm5-eval][^glm5-appendix].
- Pipeline: static build check then GUI Judge Agent (Claude Code + Sonnet 4.5 + Playwright MCP in Docker) doing code reads, clicks/keystrokes/screenshots, terminal checks per check-item; metrics Build Success Rate, Instance Success Rate (all specs), Check-item Success Rate[^glm5-eval].
- Validation: 94% pointwise agreement on 130 check-items (gaps on subjective visual quality) and Spearman 85.7% ranking agreement across 8 frontier models[^glm5-eval].
- Results: Build React/Vue/Svelte 100%, Next.js 95% (reported 98.0% overall) vs Opus 95/100/90/80; ISR HTML 38.9 vs Opus 52.2, React 34.6 vs 39.7, Vue 32.7 vs 46.9; CSR HTML 76.3 vs 82.2, React 71.0 beats Opus 70.7, Vue 77.1 beats 74.3 — most requirements met but end-to-end gap remains[^glm5-eval].

Backend and long-horizon:

- Backend: 85 tasks in Python/Go/C++/Rust/Java/TypeScript over search/DB/web/AI-inference/KM/algo challenges (feature/bug/regression/perf); terminal-bench-style Docker plus 5–10 human unit tests; strict Pass@1 all-tests-pass 25.8 vs Opus 26.9 vs GLM-4.7 19.6[^glm5-eval].
- Large Repo Exploration: tens-of-thousands-file high-star repos, business-semantic questions with no file/class/function names and 1–2 reasoning hops, targets ≥3 levels deep with opaque/unique/non-main-surface files; Pass@1 over 3 runs for reading target file 65.6 beats Opus 64.5 vs GLM-4.7 47.8, attributed to search strategy from agentic tool-use training[^glm5-eval].
- Multi-step Chained Tasks: merged PRs with tests and 3–15 linear commits; LLM pairwise-relatedness plus DP partition into coherent groups; golden/test/auto-apply patch triage; LLM problem statements; feature/bug/refactor/test/config classification on error-elimination/critical-path/test axes; Docker zero-regression validation; sequential execution with cumulative tests 1..k; Pass@1 52.3 vs Opus 61.6 vs GLM-4.7 43.0; compounding edits framed as future long-context consistency/self-correction work[^glm5-eval].

## Freshness and general abilities

- SWE-rebench Jan 2026 (continuous fresh GitHub issues vs 2-year-old static SWE-bench Verified): GLM-5 42.1% ±1.21, Pass@5 50.0% vs Opus 4.6 52.9/70.8, GPT-5.2 51.7/58.3, Sonnet 4.5 47.1/60.4, Gemini 3 Pro 46.7/58.3, Opus 4.5 43.8/58.3, GLM-4.7 41.3/56.3, Kimi K2.5 37.9/50.0[^glm5-eval].
- Five deployment-derived general domains all improve over GLM-4.7: machine translation, multilingual dialogue, instruction following, world knowledge, tool calling[^glm5-eval].
- Translation: ZMultiTransBench 1,220 (Zh→Es 300/Ru 250/Fr 220/Ko 200/Ja 150/Ar 50/De 50, grad-verified, GPT-4.1 pairwise) plus MENT-SNS 753 En-Zh SNS/Cross-Culture/Poetry/Literature stressing slang/wordplay/idiom/history/metaphor[^glm5-eval].
- Dialogue: LMArena Elo plus ZMultiDialBench 141 native-speaker/online-failure cases scored 1–10 by humans[^glm5-eval].
- Following: IF-Badcase 450 production-failure multi-constraint checklist cases plus IF-Bench and MultiChallenge multi-turn scenarios[^glm5-eval].
- Knowledge: SimpleQA and Chinese SimpleQA (6 domains, 99 subtopics)[^glm5-eval].
- Tool calling: ToolCall-Badcase 200 production-failure cases scoring tool choice plus argument structure/semantics after multi-round review[^glm5-eval].

## Chinese-chip deployment

- Full-stack adaptation claimed across Huawei Ascend, Moore Threads, Hygon, Cambricon, Kunlunxin, MetaX, Enflame from day one, kernels through inference frameworks[^glm5-intro][^glm5-chips].
- Ascend Atlas 800T A3 case: W4A8 mixed precision via msModelSlim (Attention/MLP W8A8, MoE W4A8) with QuaRot outlier suppression and `Flex_AWQ_SSZ` calibration fits ~750B model on one machine[^glm5-chips].
- Custom NPU kernels: Lightning Indexer fusing score/ReLU/TopK with compute/memory overlap; Sparse Flash Attention parallelizing TopK KV selection plus sparse compute; MLAPO fusing 13 MLA pre-processing ops across Vector/Cube units[^glm5-chips].
- Engine work on vLLM-Ascend/SGLang: async Device-to-Host sampling overlap, RadixCache plus RAM-extended Prefix Cache, Attention-DP plus MoE-EP plus FlashComm split AllReduce, and MTP density; claimed single-Chinese-node parity with dual-GPU international clusters and −50% long-sequence deployment cost[^glm5-chips].

## Release note

- Pony Alpha anonymous OpenRouter release validated capability without brand bias; reported community guesses ~25% Claude Sonnet 5, ~20% DeepSeek, ~10% Grok, remainder GLM-5; framed as evidence for engineering-level reliability and narrowing open/proprietary gap, not a benchmark[^glm5-concl].

## Relationships

- Related to [GLM-5 Architecture and Pre-training](glm-5-architecture-pretraining.md) — model and training substrate behind these scores.
- Related to [GLM-5 Post-Training and Agentic RL](glm-5-posttraining-agentic-rl.md) — RL/environment/context-management methods behind BrowseComp, Vending, and CC-Bench gains.
- Related to [GLM-5.3-Flash Architecture and Evaluation](glm-5.3-flash-architecture.md) — later Flash cost/efficiency counterpart in the GLM-5 series.
- Related to [GLM-5.3 Local Deployment](glm-5.3.md) — deployment-size sibling for local-run context.

## Coverage limits

- All scores are source-reported; harness/judge/timeout variations above limit cross-model comparability.
- CC-Bench-V2 task/checklist distributions and Agent-as-a-Judge transcripts were not inspected beyond the tex description.
- Single-node parity, −50% cost, and Pony Alpha guess statistics are vendor-reported without inspectable logs.

[^glm5-intro]: Introduction — `../raw/arXiv-2602.15763v2/1_intro.tex`, ~20% ARC gain over GLM-4.7, AA Index 50 vs 42, #1-open LMArena Text/Code, Vending $4,432, CC-Bench-V2 narrowing-to-Opus framing, and seven-platform domestic-chip list.
[^glm5-eval]: Evaluation — `../raw/arXiv-2602.15763v2/4_evaluation.tex`, full ARC table plus reasoning/coding/agentic methodology, CC-Bench-V2 frontend/backend/long-horizon pipelines and results, SWE-rebench table, and five-domain general-ability protocols/datasets.
[^glm5-chips]: Chinese chips — `../raw/arXiv-2602.15763v2/3.2_domestic.tex`, seven-vendor scope, Atlas 800T A3 W4A8/QuaRot/`Flex_AWQ_SSZ` recipe, Lightning Indexer/Sparse-Flash/MLAPO kernels, vLLM-Ascend/SGLang scheduling/cache/parallel/MTP work, and parity/cost claims.
[^glm5-concl]: Conclusion/easter egg — `../raw/arXiv-2602.15763v2/5_conclusion.tex`, vibe-coding-to-agentic-engineering summary plus anonymous Pony Alpha OpenRouter anecdote and guess distribution.
[^glm5-appendix]: Appendix — `../raw/arXiv-2602.15763v2/9_appendix.tex`, base-model benchmark table, ARC temperature/top-p/token/context/timeout/CPU-RAM settings, tau2 prompt boxes, and frontend data/construction/validation details.
