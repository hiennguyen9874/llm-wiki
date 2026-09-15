---
type: Concept
title: GLM-5 Post-Training and Agentic RL
description: SFT thinking modes, GRPO-IcePop reasoning RL, asynchronous agent RL with TITO and double-sided clipping, scaled SWE/terminal/search/slide environments, slime infra, and cross-stage distillation.
tags: [glm-5, post-training, sft, rl, grpo, agentic-rl, async-rl, slime, search-agent, slide-generation]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: glm5-post
    resource: ../raw/arXiv-2602.15763v2/3_posttrain.tex
    title: GLM-5 Post-Training — SFT, reasoning/general RL, distillation, slime
  - id: glm5-agent
    resource: ../raw/arXiv-2602.15763v2/3.1_agenticRL.tex
    title: GLM-5 Agentic RL — async training, environments, search/slide agents
---

GLM-5 post-training runs multi-task SFT with interleaved/preserved/turn-level thinking, then sequential Reasoning, Agentic, and General RL closed by on-policy cross-stage distillation, supported by decoupled asynchronous rollout infrastructure[^glm5-post].

## SFT

- Corpus triples General Chat, Reasoning, and Coding/Agent with enlarged Agent/Coding share; context extended to 202,752 tokens plus new chat template[^glm5-post].
- Three thinking modes: Interleaved (think before every response/tool call for following/quality); Preserved (retain thinking blocks across multi-turn coding to avoid re-derivation and drift); Turn-level (per-turn on/off for latency vs accuracy)[^glm5-post].
- General Chat tuned more logical/concise vs GLM-4.5; broader multilingual role-play filtered on following, expressiveness, creativity, coherence, long-dialogue consistency by automatic plus human review[^glm5-post].
- Reasoning deepened with verifiable logical problems plus rejection sampling and math/science difficulty filtering keeping only GLM-4.7-hard problems[^glm5-post].
- Coding/Agent built from many execution environments emphasizing real-world long-horizon trajectories, expert-RL plus rejection sampling; erroneous spans kept but loss-masked to teach correction without reinforcing errors[^glm5-post].

## Reasoning RL backbone

- GRPO plus IcePop without KL: separates train policy `π^train` from inference policy `π^infer`; `pop(ρ,1/β,β)` zeroes tokens whose train/infer mismatch `ρ` leaves `[1/β,β]`; PPO-style clip `[1−ε_low,1+ε_high]` on group-normalized advantage; reported `β=2, ε_low=0.2, ε_high=0.28`, fully on-policy group 32 batch 32[^glm5-post].
- DSA stability: Top-K `k=2048` retrieval critical; MoE-style routing replay would cost too much storage/communication at this `k`; deterministic `torch.topk` beats non-deterministic CUDA/SGLang/TileLang Top-K (which caused rapid degradation plus entropy collapse); indexer frozen by default in RL for speed/stability[^glm5-post].
- Mixed math/science/code/tool-integrated reasoning kept roughly balanced; math/science mined from open plus vendor data filtered to GLM-4.7-rarely-solved but GPT-5.2-xhigh/Gemini-3-Pro-Preview-solvable; code covers Codeforces/TACO/SYNTHETIC-2-RL plus internal minimal-impl science coding; TIR reuses hard math/science plus vendor tool-required STEM; domain-specific judges give binary outcome rewards[^glm5-post].

## Asynchronous agentic RL

- Group-mean baseline objective over `K` traces per problem; only model tokens enter loss, environment feedback excluded[^glm5-agent].
- Train and inference engines live on different GPUs; inference streams trajectories, ships batches at threshold, resyncs weights every `K` training updates, and resets optimizer after inference-weight pushes to bound lag-induced objective shift[^glm5-agent].
- Server-based Multi-Task Rollout Orchestrator registers per-task rollout/reward microservices, balances per-task ratio/speed, unifies trajectories as message lists, supports >1K concurrent rollouts with dynamic sampling and fine-grained monitoring[^glm5-agent].
- Token-in-Token-out gateway records exact token IDs plus metadata at generation time, avoiding text-round-trip re-tokenization mismatches in boundaries, whitespace/normalization, truncation, and special tokens[^glm5-agent].
- Direct double-sided importance sampling reuses rollout log-probs as behavior proxy `r_t=π_θ/π_rollout`, drops separate `π_old` tracking, and masks tokens outside `[1−ε_ℓ,1+ε_h]` to zero instead of asymmetric PPO clipping[^glm5-agent].
- Stale/noisy-sample control: record rollout weight versions `(w_0…w_k)`, drop if `w'−w_0>τ`; exclude environment-collapse failures (not model failures); for GRPO pad incomplete groups by repeating valid samples when valids exceed half, else drop group[^glm5-agent].
- DP-aware routing pins each rollout ID to a fixed DP rank by consistent hashing plus light rebalancing, preserving KV-cache locality so multi-turn prefill scales with incremental tokens rather than full context[^glm5-agent].

## Environment scaling

- SWE: RepoLaunch-based pipeline auto-builds install/deps/test commands and LLM-parses logs into Fail-to-Pass/Pass-to-Pass sets; >10K verifiable environments over thousands of repos in Python/Java/Go/C/C++/JS/TS/PHP/Ruby across bug-fix/feature/refactor tasks[^glm5-agent].
- Terminal seed synthesis: LLM brainstorms drafts from real SWE/terminal seeds, construction agent materializes Harbor-format Docker plus tests, refine agent iterates to >90% Docker-build accuracy with exploit/shortcut checks[^glm5-agent].
- Terminal web-corpus synthesis: quality-classified code-bearing pages, terminal-task suitability filter, stratified topic/difficulty sampling, coding-agent construction plus Harbor self-verification repair loop[^glm5-agent].
- Search Web Knowledge Graph: >2M deduped high-information pages from early-agent trajectories, LLM entity/noise/structured extraction with alignment/normalization/consolidation; low/mid-frequency seeds expanded to multi-hop subgraphs turned into implicit-chain questions; three filters drop tool-free-solvable (1/8), early-agent few-step-solvable, and unverifiable/non-unique Q-A pairs[^glm5-agent].
- Search inference context: `Keep-recent-k` folds only observations older than `k` rounds (`o_i` replaced by omission notice); `k=5` lifts BrowseComp 55.3% to 62.0%; hierarchical `Keep-recent + Discard-all` at `T=32K` frees space for more steps and reaches 75.9%, best reported open result; judge standardized to official OpenAI prompt with `o3-mini` after finding open-judge bias[^glm5-agent].
- Slide generation self-improving loop: SFT start, then RL with Level-1 static HTML attributes (position/spacing/color/typography/hallucinated-duplicate-image rules), Level-2 runtime DOM geometry via distributed renderer with anti-hacking fixes for truncation/spacing exploits, Level-3 perceptual whitespace; dynamic dropping of trivial pages, token-level policy gradient, cross-batch outcome balancing; Best-of-N rejection plus defective-page masking; 16:9 compliance 40% to 92% and human wins vs GLM-4.5 of 60% content / 57.5% layout / 65% aesthetics / 67.5% overall[^glm5-agent].

## slime RL infrastructure

- slime reused as unified stack: customizable multi-turn/tool/environment/verifier rollout logic plus HTTP server/router APIs so external agent frameworks call serving directly without training forks[^glm5-post].
- Tail-latency focus: multi-node inference (e.g. EP64/DP64 over 8 nodes) for KV capacity; DP-attention avoids KV copies; FP8 rollouts plus MTP help small-batch long-tail stragglers; Prefill-Decode disaggregation isolates heavy multi-turn prefills from decodes; heartbeat monitoring deregisters bad servers and reroutes retries[^glm5-post].

## General RL and distillation

- General RL splits foundational correctness (instruction/logic/factual/hallucination/fluency usable baseline), emotional intelligence (empathetic human-like style), and task-specific quality (writing/processing/QA/role/translation)[^glm5-post].
- Hybrid rewards mix precise rule rewards, efficient but hackable outcome reward models, and robust but higher-variance generative reward models; high-quality human exemplars anchor style against verbose/formulaic model-like drift[^glm5-post].
- Final on-policy cross-stage distillation recovers SFT plus Reasoning/General skills: prior final checkpoints teach, prompts sampled from teachers' RL mixes, advantage replaced by `sg[log π_teacher^infer/π_θ^train]`; GRPO group 1 batch 1024; future move to training-engine MQA-mode teacher logits[^glm5-post].

## Relationships

- Depends on [GLM-5 Architecture and Pre-training](glm-5-architecture-pretraining.md) — base scale, DSA indexer, and MTP substrate that reasoning/agentic RL must keep stable.
- Uses [SGLang for RL Systems](sglang-for-rl.md) — colocated rollout, weight-sync, and deterministic-inference concerns overlapping slime's async design.
- Uses [vLLM Adaptive Verification for Speculative Decoding](vllm-adaptive-verification.md) — acceptance/stability lens for MTP-assisted FP8 rollouts.
- Related to [vLLM Interleaved Thinking](vllm-interleaved-thinking.md) — chained tool-use reasoning mode comparable to GLM-5 interleaved/preserved thinking.
- Related to [GLM-5 Evaluation and Deployment](glm-5-evaluation-deployment.md) — ARC/CC-Bench/search-harness evidence for these training choices.

## Coverage limits

- Exact orchestrator thresholds, `τ`, clipping epsilons for agentic stage, task-mix ratios, and slide-reward weights are not stated in the inspected tex.
- Search/slide gains and >1K-rollout throughput are source-reported without inspectable logs.

[^glm5-post]: Post-training — `../raw/arXiv-2602.15763v2/3_posttrain.tex`, SFT corpus/thinking taxonomy, GRPO-IcePop equations plus `β/ε/group/batch` settings, DSA `torch.topk`/freeze insight, four-domain mix, async/orchestrator/TITO/double-sided-sampling summary, general-RL triad plus hybrid/human-anchor rewards, distillation equation/settings, and slime scale-up/robustness mechanisms.
[^glm5-agent]: Agentic engineering — `../raw/arXiv-2602.15763v2/3.1_agenticRL.tex`, group objective plus async weight-sync/optimizer-reset design, orchestrator/TITO/clipping/stale-drop/DP-routing details, RepoLaunch SWE/terminal/Web-KG environment pipelines, Keep-recent/hierarchical context numbers, and three-level slide-generation rewards plus rejection/masking results.
