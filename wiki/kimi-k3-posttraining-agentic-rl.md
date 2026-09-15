---
type: Concept
title: Kimi K3 Post-Training and Agentic RL
description: SFT cold start, nine domain-effort RL experts, MOPD unification, MXFP4 QAT, EAGLE-3 draft, and white-box agentic environments.
tags: [kimi-k3, post-training, reinforcement-learning, sft, distillation, mopd, reasoning-effort, mxfp4, eagle3, xtml, agent-environments]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: k3-post
    resource: ../raw/arXiv-2607.24653v1/4-post-training.tex
    title: Kimi K3 Technical Report — post-training
  - id: k3-chat
    resource: ../raw/arXiv-2607.24653v1/appendix/4-post-training-chat-template.tex
    title: Kimi K3 Technical Report — chat template appendix
---

Three-stage pipeline initializes agent capability with supervised fine-tuning, trains domain-effort RL experts, then consolidates them into one model with multi-teacher on-policy distillation; quantization-aware training and draft-model tuning run throughout for deployment-aware post-training[^k3-post].

## Supervised fine-tuning

SFT builds a high-quality cold-start policy on an expanded complex-agentic dataset synthesized by prior Kimi-series domain specialists, followed by multi-stage verification and human-in-the-loop annotation, all serialized in XTML chat template; result is adaptive reasoning, precise tool calling, and robust long-horizon execution[^k3-post].

- Quantization-aware training starts at SFT onward with MXFP4 weights and MXFP8 activations[^k3-post].

## Reinforcement learning

RL spans three broad domains, each with wide subtasks, training one expert per domain per reasoning effort in `{low, high, max}` for nine experts total[^k3-post]:

- General tasks: general experience, vision, reasoning, faithfulness, search, knowledge work.
- General agents: long-horizon assistant tasks, deep research, paragraph-level writing.
- Coding agents: software engineering, coding experience, kernel tasks, web development.

Scaling RL FLOPs consistently raises tool-call steps and broad capability across knowledge, reasoning, vision, general-agent, and coding curves[^k3-post].

### Algorithm

Extends synchronous partial-rollout scheme to curb long-tail latency: sample `K` completions for each of `N` prompts (`N*K` active), pause generation once fraction `lambda` completes, optimize without stragglers, enqueue paused rollouts first next iteration via sandbox infra; dispatch for optimization once all `K` for a prompt complete following Kimi 2.5 algorithm[^k3-post].

- Long trajectories span iterations, creating extreme off-policy staleness handled by per-token regularization constraining updates to a localized neighborhood[^k3-post].

### Reasoning-effort RL

Per-problem budget control maximizes token efficiency: initial budget `b0(x)` from cold-start model, override task reward with `-1` when total budget `T(y)` exceeds `tau*b0(x)`; `T` counts thinking tokens for general tasks and cumulative output including reasoning plus tool-call arguments for agentic tasks[^k3-post].

- Stage-wise curriculum over multiplier `tau`: train max-budget variant with large `tau` plus cap against overthinking, then anneal to high and low experts; `tau` set per domain with human-in-the-loop; all-effort trajectories feed SFT and distillation[^k3-post].

### Agentic generative reward model

Non-verifiable general tasks use tournament-style group reward with binary comparisons; agentic judge must follow mandatory protocol: read outcome/product/text, generate rubric, score each candidate, record in scorepad[^k3-post].

- Budget-based verbosity control mirrors effort control: output exceeding `sigma*l0` (initial verbosity from cold start) automatically loses comparison, mitigating verbose reward hacking[^k3-post].

## Multi-teacher on-policy distillation

MOPD consolidates nine specialists: for domain `d` and sampled effort `e`, teacher `pi_teacher^(d,e)` guides student via per-token clipped OPD reward `clip(sg(log pi_teacher/pi_theta), -Rmax, Rmax)`; dense signal integrates with RL framework and partial rollouts; finer top-k distillation showed no clear convergence or final-performance advantage[^k3-post].

## Deployment-aware post-training

### MXFP4 quantization-aware post-training

MoE expert weights dominating parameter memory are quantized to MXFP4 with MXFP8 activations; attention projections, latent MoE projections, shared experts, and routers stay higher precision; QAT covers all post-training (SFT plus RL) so model adapts to precision loss; rollout and training share same scheme, removing train-inference mismatch[^k3-post].

### Draft-model fine-tuning

Pretrained MTP layer mirroring a backbone block is fine-tuned into EAGLE-3-style draft (single decoder layer shape match) with target frozen, only draft layer plus feature-fusion projection updated; 7-step unrolled training-time test uses own outputs after first step, mirroring recurrent inference drafting[^k3-post].

- Draft input fuses low-, mid-, high-level target features from 1st, 4th, and final AttnRes blocks via bias-free `W_E3` initialized `[0 0 I]` so initial fused state equals high-level feature `h_h` used in MTP pretraining, then learns to incorporate lower features[^k3-post].
- Directly optimizes likelihood-based LK loss `-log sum_x min(p(x),q(x))` (negative log acceptance rate at temperature 1, no ground-truth CE), since minimizing KL surrogate does not guarantee maximizing acceptance for capacity-limited draft[^k3-post].
- Follows post-training QAT config (MXFP4 experts, MXFP8 inputs, higher-precision non-experts)[^k3-post].

## XTML chat template

Redesigned around extensibility (backward-compatible message formats, one template for whole generation), low alignment tax (learnable with minimal SFT so lightly tuned model can go straight to RL), and decoding friendliness (simple encoders, streaming parsers, grammar enforcers); XTML replaces XML angle brackets with `[open]`, `[sep]`, `[close]`, plus `[end_of_msg]` stop marker, making every structural boundary an explicit special token and removing tokenization ambiguity[^k3-chat].

- Messages: input messages serialize request `messages` (system/user/assistant/tool); option messages translate request options into in-context instructions; global options (tool-declare, reasoning effort) precede inputs; one-shot options (`tool_choice`, `response_format`) follow inputs so per-request changes preserve history KV cache; input option messages interleave mid-session for dynamically loaded tools without rebuilding context[^k3-chat].
- Channels in assistant body inspired by Harmony: `think` trace, `response` answer, `tools` calls; generation mode selected by prefix (`[open]think[sep]` vs `[open]response[sep]`); only preserved thinking supported (think channel retained even when empty in thinking mode; instruct-mode history has response plus tools only)[^k3-chat].
- Tool calling: each call carries `tool` plus `index` for parallel calls, results repeat same pair in call order; typed arguments (strings raw, other JSON compactly serialized, code first-class not escaped JSON); pure-JSON fallback only in input tokens with masked loss[^k3-chat].
- Reasoning effort is global `thinking-effort` option after tool declaration, stated in natural language not prefix or token budget; schema reserves `low/medium/high/max`, K3 supports subset (`low/high/max` in RL/distillation); `tool_choice`, `response_format`, and effort all become short NL instructions the pretrained model already follows, enabling new options with little/no training[^k3-chat].

## Task synthesis and environments

RL quality depends on rich, diverse, robustly verifiable environments[^k3-post].

### Unified white-box environment

Single fixed harness risks overfitting to one tool schema/prompt/context/protocol; unified environment composes configurable modules (tool interfaces, system prompts, context strategies, skills, memories, subagents) to instantiate Kimi Code, Claude Code, Codex, OpenClaw, Hermes, or entirely new harnesses; different task groups train under different harness configs for cross-harness generalization across domains[^k3-post].

### Knowledge-graph-guided synthesis

Fine-grained concept retrieval surfaces specialized knowledge while diverse sampling broadens coverage; self-evolving hierarchical DAG starts from coarse seeds, agent per node does web searches, reuses equivalent nodes to minimize duplication, directs edges coarse-to-fine, stops when atomic; sampled nodes plus ancestor context form queries, retrieved real materials feed synthesis agent producing varied task types[^k3-post].

### Verifiable agentic problems

Includes multi-step web research with verifiable answers; professional work (investment banking, data analysis, legal) decomposing requests and operating domain tools over dozens to hundreds of steps to deliverables; multi-step visual reasoning over STEM, puzzles, charts in Python-sandbox agent loop (crop/zoom/transform/compute/verify, generated images as observations), where more image operations and observations steadily improve performance[^k3-post].

### Kernel optimization tasks

Suite from single operators to fused mega-kernels sourced from high-quality repos such as Flash Linear Attention, spanning CUDA, Triton, CuTe DSL, Gluon, ThunderKittens, TileLang across GPU architectures and BF16/FP8/FP4; PyTorch reference gives zero reward above error threshold; performance scored 0.5 for matching expert rising toward 1 near roofline; hacking-detection penalizes graph replay, input caching, precision reduction and evolves as new hacks appear[^k3-post].

### Personal assistant tasks

Realistic mocks of Gmail, Notion, Slack, Canvas preserve core semantics without external APIs/rate limits; complex HR/legal/finance workflows run in persistent evolving multi-day environments with dozens of interdependent cross-app events; single rollout up to thousands of tool calls and millions of tokens; per-event deterministic or LLM evaluators; initial workspace agent-built from web materials; RL framework models living event streams and world-state transitions[^k3-post].

### Autonomous execution tasks

Verify-in-the-loop paradigm: initial state, constrained goal, tool action space, budgets, independent verifier; no reference trajectories; agent must decompose, select tools, plan, recover, terminate; reward from verifier on final state not self-report; verifiers include black-box replication (e.g. Camera Repair Management System completion curves), quantitative factor discovery, tax auditing; public diagnostic plus hidden held-out verifiers, isolation from verifier, penalty rewards under limited submissions curb hacking[^k3-post].

### Web development tasks

Expert-curated suite from one-line scenes to multi-paragraph specs producing websites, games, 3D/WebGL, dataviz, SVGs, full-stack apps; containerized sandbox rolled out under diverse scaffolds; reward combines deterministic checks (build/run must pass, fakes zeroed, functional plus structural/pixel similarity) with model judging via source inspection and live artifact interaction[^k3-post].

## Relationships

- Depends on [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md) — MTP layer, AttnRes block features, and 1M-context foundation tuned here.
- Uses [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md) — partial-rollout persistence, external KV retention, throttling, and resumable AgentENV sandboxes that make million-token RL tractable.
- Related to [Kimi K3 Evaluation](kimi-k3-evaluation.md) — effort levels, harnesses, and environments here explain eval configs and cost-efficiency analysis.

## Coverage limits

- RL algorithm follows Kimi 2.5 and MOPD cites external distillation work; those external papers were not inspected beyond this report.
- Sandbox performance numbers for AgentENV lifecycles belong to systems compilation; post-training section cites the capability without repeating all infra metrics.
- Chat-template figure layout was read from text description; TikZ source was not rendered.

[^k3-post]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/4-post-training.tex`, SFT cold start plus QAT, three RL domains with nine low/high/max experts and step-scaling curve, partial-rollout lambda plus per-token regularization, budget curriculum tau plus verbosity sigma, tournament GRM rubric/scorepad protocol, MOPD clipped OPD reward, MXFP4/MXFP8 deployment QAT, MTP-to-EAGLE-3 fine-tune with 1st/4th/final fusion and LK loss, white-box harness abstraction, KG DAG synthesis pipeline, verifiable/kernel/assistant/AET/webdev environments.
[^k3-chat]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/appendix/4-post-training-chat-template.tex`, XTML goals plus special tokens, global/one-shot/input-option placement plus dynamic tools, think/response/tools channels plus preserved thinking plus prefix-selected modes, indexed typed tool calls plus JSON fallback masking, NL thinking-effort low/medium/high/max option design.
