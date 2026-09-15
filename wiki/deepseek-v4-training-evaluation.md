---
type: Concept
title: DeepSeek-V4 Training and Evaluation
description: 32–33T pretraining with staged 1M extension, GRPO specialists plus full-vocab OPD, FP4 QAT and DSec sandbox, and base plus reasoning, agent, long-context, and real-world evaluation.
tags: [deepseek-v4, pretraining, post-training, distillation, evaluation, agents]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v4-report
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: 'DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence'
  - id: v4-base
    resource: ../raw/arXiv-2606.19348v1/tables/base_eval.tex
    title: DeepSeek-V4 base evaluation table
  - id: v4-small
    resource: ../raw/arXiv-2606.19348v1/tables/small_eval.tex
    title: DeepSeek-V4 Flash versus Pro reasoning-mode table
  - id: v4-large
    resource: ../raw/arXiv-2606.19348v1/tables/large_eval.tex
    title: DeepSeek-V4-Pro-Max versus open and closed models table
  - id: v4-code
    resource: ../raw/arXiv-2606.19348v1/tables/code_agent_dsbench.tex
    title: DeepSeek-V4 R&D coding benchmark table
  - id: v4-search
    resource: ../raw/arXiv-2606.19348v1/tables/search.tex
    title: DeepSeek-V4 agentic versus RAG search tables
  - id: v4-rag
    resource: ../raw/arXiv-2606.19348v1/tables/rag_eval.tex
    title: DeepSeek-V4 retrieval search Q&A table
  - id: v4-write
    resource: ../raw/arXiv-2606.19348v1/tables/funcwrite.tex
    title: DeepSeek-V4 Chinese writing evaluation tables
---

DeepSeek-V4 pretrains Pro on 33T and Flash on 32T tokens from a greater-than-32T corpus with staged extension to 1M, stabilizes trillion-parameter MoE training with anticipatory routing and SwiGLU clamping, merges domain specialists with full-vocabulary on-policy distillation, and evaluates Pro-Max as the strongest open model on knowledge, reasoning, long-context, and white-collar tasks with noted gaps to closed models[^v4-report].

## Pretraining data and schedule

Web data filters batched auto-generated and templated content against collapse risk; math and code stay core with added mid-training agentic code; multilingual coverage grows for long-tail knowledge; long-document curation emphasizes papers and technical reports; packing minimizes truncation across sources and sample-level attention masking replaces V3 practice[^v4-report].

Flash trains to 75.5M-token max batch with peak LR 2.7e-4 decaying to 2.7e-5; Pro trains to 94.4M-token max batch with 2.0e-4 to 2.0e-5; both warm up 2000 steps, extend 4K to 16K to 64K to 1M, warm up dense attention for the first 1T tokens with a longer dense phase for Pro, introduce sparsity at 64K after a short indexer warmup, and use aux-loss-free bias speed 0.001, sequence balance weight 0.0001, and MTP weight 0.3 falling to 0.1 at decay[^v4-report]. AdamW covers embeddings, head, and RMSNorm with `beta1=0.9/beta2=0.95/eps=1e-20/decay=0.1`; Muon uses momentum 0.95, decay 0.1, and 0.18 RMS rescaling[^v4-report].

## Stability fixes

Loss spikes correlate with MoE outliers amplified by routing; rollbacks alone do not prevent recurrence[^v4-report]. Anticipatory routing computes features with current `theta_t` but applies routing from historical `theta_{t-dt}` by prefetching data and caching indices ahead, costing about 20% wall-clock when active and auto-triggering only after spike detection with rollback before reverting to standard training[^v4-report]. SwiGLU clamps linear output to [-10,10] and gates at maximum 10 without measured performance cost[^v4-report].

## Post-training pipeline

Pipeline mirrors V3.2 except mixed RL is replaced by on-policy distillation[^v4-report]. Specialists train by SFT then GRPO with distinct length penalties and windows for Non-think, Think High, and Think Max modes, using `<think>` delimiters and an extra maximum-effort system instruction demanding exhaustive decomposition and adversarial checks[^v4-report]. Eval windows are 8K for Non-think, 128K for High, and 384K for Max on reasoning and knowledge tasks[^v4-report].

Hard-to-verify tasks use rubric-guided RL with a generative reward model where the actor itself serves as judge, jointly optimizing judging and generation from minimal diverse human labels[^v4-report]. Tool calls switch to an XML `|DSML|` schema to cut escaping failures, with full reasoning inside `<think>` before tools when thinking is enabled[^v4-report].

Interleaved thinking preserves all reasoning across user turns in tool-calling scenarios for cumulative long-horizon state but keeps discard-on-new-user behavior in general chat; frameworks simulating tools as user messages do not trigger the persistent path, so non-think models remain recommended there[^v4-report]. Quick Instruction appends dedicated tokens for action, title, query, authority, domain, and URL fetch decisions, reusing computed KV with parallel execution to cut time-to-first-token and remove a separate small-model path[^v4-report].

OPD merges more than ten teachers via weighted reverse KL on student-generated trajectories, selecting the relevant expert per context and avoiding weight-merge degradation; the report uses full-vocabulary logit distillation rather than token-level advantage reuse for lower-variance stable gradients[^v4-report].

## Post-training infrastructure

FP4 MXFP4 quantization-aware training covers MoE expert weights and CSA indexer QK paths with cached, loaded, and multiplied FP4 plus BF16 index scores; FP4-to-FP8 dequant is treated as lossless via E4M3 headroom and reuses the FP8 stack with straight-through estimation, while rollout uses native FP4 for deployment parity, memory, and speed[^v4-report].

Full-vocabulary OPD offloads all teacher weights to central storage with ZeRO-like on-demand sharding, caches last-layer hidden states instead of full logits, orders samples by teacher to keep one head resident, overlaps movement asynchronously, and computes exact KL in a TileLang kernel[^v4-report]. Rollout uses token-granular write-ahead logs plus saved KV for preemption resume and prefill rebuild, avoiding shorter-response length bias from scratch regeneration[^v4-report]. Million-token RL splits lightweight metadata from heavy per-token fields, shuffles globally, loads heavy fields via shared memory, releases per mini-batch, and sizes on-device batches dynamically[^v4-report].

DeepSeek Elastic Compute provides Function, Docker-compatible Container with EROFS on-demand layers, Firecracker microVM with overlaybd, and QEMU fullVM behind one Python SDK for command, file, and TTY ops, scaling to hundreds of thousands of sandboxes over the 3FS filesystem with page-cache, reclamation, and runtime contention fixes plus trajectory logging for fast-forward resume, provenance, and deterministic replay[^v4-report].

## Base evaluation

Internal unified base comparison shows Flash-Base beating V3.2-Base on most suites despite fewer total and activated params, especially knowledge and LongBench-V2, while Pro-Base leads nearly universally[^v4-base]. Pro-Base leads knowledge rows including MMLU 90.1, MMLU-Pro 73.5, Simple-QA verified 55.2, SuperGPQA 53.9, and FACTS Parametric 62.6; Flash-Base trails Pro but beats V3.2 on most of those rows[^v4-base]. Exceptions include BigCodeBench where V3.2-Base 63.9 beats Pro 59.2 and Flash 56.8, plus BBH and language rows near ties within the 0.3-point same-level rule[^v4-base].

## Chat reasoning modes and frontier comparison

Small-table comparison across Non-think, High, and Max shows a persistent Pro over Flash knowledge gap from larger pretraining retention, comparable reasoning when Flash gets larger thinking budgets, and a Pro lead on harder agentic tasks[^v4-small]. Examples include Pro-Max SimpleQA-Verified 57.9 versus Flash-Max 34.1, GPQA Diamond 90.1 versus 88.1, Codeforces 3206 versus 3052, MRCR 1M 83.5 versus 78.7, BrowseComp 83.4 versus 73.2, and Terminal Bench 2.0 67.9 versus 56.9[^v4-small].

Pro-Max is presented as best open model overall: it beats open baselines by about 20 points on SimpleQA-Verified, leads LiveCodeBench 93.5 and Codeforces 3206 with human rank 23, leads Apex Shortlist 90.2, and trails Gemini-3.1-Pro on several knowledge rows while matching or beating closed models on select code and reasoning rows[^v4-large]. Long-context MRCR 1M 83.5 and CorpusQA 1M 62.0 beat Gemini-3.1-Pro but trail Opus-4.6; agentic rows are near open-best but generally trail closed leaders except MCPAtlas and Toolathlon generalization strength[^v4-large]. Formal math reaches Putnam-200 Pass@8 state of the art under a minimal Lean plus LeanExplore agentic setup and 120/120 on Putnam-2025 with scaled hybrid informal-formal verification[^v4-report]. Max effort beats High on hardest tasks with better token efficiency than V3.2-Speciale on HLE in the reported effort curves[^v4-report].

## Real-world tasks

Chinese functional writing over 3170 cases favors Pro over Gemini-3.1-Pro 62.65% to 34.10% with 3.25% ties; creative writing favors Pro 60.03% on instruction following and 77.48% on quality, while complex and multi-turn writing over 196 cases favors Opus-4.5 52.0% to 45.9%[^v4-write][^v4-report].

RAG search over 956 Q&A favors V4 over V3.2 28.1% to 10.4% with 61.5% ties, strongest on single-value and planning tasks and closest on comparison and recommendation[^v4-rag]. Agentic search beats RAG 61.7% to 18.3% over 869 cases with larger hard-task gains at 16.2 tool calls, 13649 prefill tokens, and 1526 output tokens versus RAG 10453 and 1308[^v4-search].

Thirty advanced Chinese white-collar tasks across 13 industries score Pro-Max above Opus-4.6-Max with 63% non-loss rate on blind human Task Completion, Instruction Following, Content Quality, and Formatting Aesthetics, with strengths in completion, quality, proactive intent, long-form coherence, and numbering conventions against weaknesses in formatting constraints, condensing, and slide aesthetics[^v4-report]. Internal R&D coding over 30 filtered tasks scores Pro-Max 67% versus Haiku-4.5 13%, Sonnet-4.5 47%, Opus-4.5 70%, Opus-4.5 Thinking 73%, and Opus-4.6 Thinking 80%; a survey of 85 internal developers finds 52% yes, 39% lean-yes, and under 9% no on default-model readiness, noting trivial mistakes, vague-prompt misses, and over-thinking[^v4-code][^v4-report].

## Limitations

The report calls the architecture complex from retained validated tricks and plans distillation to essentials, deeper stability theory for anticipatory routing and clamping, sparser embeddings, lower-latency long-context serving, longer-horizon agents, multimodality, and better data curation[^v4-report].

## Relationships

- Related to [DeepSeek-V4 Architecture](deepseek-v4-architecture.md) — model sizes and attention, MoE, mHC, and Muon choices evaluated here.
- Related to [DeepSeek-V4 Systems and Infrastructure](deepseek-v4-systems.md) — MegaMoE, TileLang, determinism, KV-cache, FP4 QAT, OPD scheduling, rollout, and DSec stack behind this training and eval.
- Related to [SGLang DeepSeek-V4 Inference](sglang-deepseek-v4-inference.md) — serving measurements companion to these report evaluations.
- Related to [Miles DeepSeek-V4 Verified RL](miles-deepseek-v4-rl.md) — independent Day-0 RL verification companion.
- Related to [DeepSeek-V4.1-Flash Training and Evaluation](deepseek-v41-training.md) — successor pretraining and eval with scaled synthesis and DSec use.

## Coverage limits

- Numeric claims follow appendix tables and report prose; codeforces Elo method, Putnam formal verifier setup, and Terminal-Bench environment caveats above bound comparability[^v4-report][^v4-large][^v4-small].
- K2.6 and GLM-5.1 blanks reflect busy APIs rather than verified misses; Terminal-Bench 2.0 uses the original set despite noted environment issues, with about 72.0 on the Verified subset for Pro[^v4-report].
- Figure trends for MRCR, effort scaling, white-collar win rates, and case PDFs were taken from captions and prose without pixel-level chart verification[^v4-report].

[^v4-report]: DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence — `../raw/arXiv-2606.19348v1/main.tex`, covering 32–33T data and staged 1M schedule, stability fixes, GRPO specialists plus reasoning modes/GRM/tool schema/interleaved thinking/Quick Instruction/OPD, FP4 QAT/teacher scheduling/rollout/million-context/DSec, frontier and formal-math results, real-world search/white-collar/code findings, and limitations.
[^v4-base]: DeepSeek-V4 base evaluation table — `../raw/arXiv-2606.19348v1/tables/base_eval.tex`.
[^v4-small]: DeepSeek-V4 Flash versus Pro reasoning-mode table — `../raw/arXiv-2606.19348v1/tables/small_eval.tex`.
[^v4-large]: DeepSeek-V4-Pro-Max versus open and closed models table — `../raw/arXiv-2606.19348v1/tables/large_eval.tex`.
[^v4-code]: DeepSeek-V4 R&D coding benchmark table — `../raw/arXiv-2606.19348v1/tables/code_agent_dsbench.tex`.
[^v4-search]: DeepSeek-V4 agentic versus RAG search tables — `../raw/arXiv-2606.19348v1/tables/search.tex`.
[^v4-rag]: DeepSeek-V4 retrieval search Q&A table — `../raw/arXiv-2606.19348v1/tables/rag_eval.tex`.
[^v4-write]: DeepSeek-V4 Chinese writing evaluation tables — `../raw/arXiv-2606.19348v1/tables/funcwrite.tex`.
