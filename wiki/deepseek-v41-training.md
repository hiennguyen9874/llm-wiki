---
type: Concept
title: DeepSeek-V4.1-Flash Training and Evaluation
description: 45T-token multimodal pretraining, Sinkhorn and Muon optimization, large-scale agent task synthesis with DSec and controllable reasoning effort, and base plus agentic evaluations.
tags: [deepseek-v4.1, pretraining, post-training, rl, reasoning-effort, evaluation, dsec]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: v41-report
    resource: ../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md
    title: 'DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression'
---

DeepSeek-V4.1-Flash pretrains natively multimodal on 45T tokens with 64K sparse attention from scratch and 1M extension, then follows standard SFT, RL, and on-policy distillation with essentially all gains attributed to scaled synthesized data and environments rather than algorithmic novelty[^v41-report].

## Optimization

Linear weights use Muon, with head-wise Muon for Query and Key to give per-head preconditioners for head heterogeneity; norms and non-matrix parameters use AdamW with decoupled decay; embeddings, token embedding, prediction head, and Engram tables use momentum plus Sinkhorn balancing requiring only a momentum buffer[^v41-report].

Sinkhorn finds diagonal scalings equalizing row and column RMS of the Nesterov momentum update, masking rows with norm below `tau` times the mean, scaling by `sqrt(n)` from unit row L2 to unit RMS, and correcting learning rate by `gamma=0.18`. Pretraining uses `K=11`, `tau=1e-3`, `eps=1e-20`, and 5x learning-rate scaling for Engram; Muon uses momentum 0.95, decay 0.1, and 0.18 RMS rescaling to reuse AdamW rates; AdamW uses `beta1=0.9`, `beta2=0.95`, `eps=1e-20`, decay 0.1[^v41-report]. Vision encoder stays frozen until LR decay except its final norm and projector, then trains jointly with a smaller LR[^v41-report].

## Data and pretraining setup

Text curation uses parameter/data scaling ladders, removes low-gain model-generated and low-quality translated content as implicit duplication, adds model-in-the-loop iteration, expert-defined quality dimensions, and recent code from new repositories, commits, libraries, and frameworks[^v41-report].

Multimodal data combines alt-text pairs filtered by relevance and semantic dedup, interleaved web/PDF sequences built through progressively expensive heuristic, statistical, dedup, quality-model, image-aware, and SmolVLM stages with filtered documents partly recycled to pairs, plus grounding, pointing, OCR, long-tail, image-code, and computer-use trajectories. Final union uses 7:1 text-to-multimodal tokens, replacing text versions with multimodal counterparts at the larger epoch count, joint prefetch assignment, deterministic pre-split of ultra-long documents, sample-level masking, and best-fit packing with padding at most 1e-4[^v41-report].

Batch holds 100.6M tokens; LR warms over 2,000 steps to 2.6e-4 through 28T tokens, cosine-decays to 2.6e-5 by 40T, and holds through 45T. Sequence starts at 64K dense-warmup-free and extends to 1M at 34T. Auxiliary-loss-free bias speed is 0.001 per modality plus 0.0001 sequence-level balance loss[^v41-report].

DeepSeek-ViT first trains contrastively with SigLIP sigmoid loss on about 47B pairs at max 224px, then autoregressively attached to a 4B MoE LLM on 236B caption, alt-text, chart, and OCR tokens at 544-1344px; only the encoder is retained[^v41-report].

## Base evaluations

Against V4-Flash-Base and V4-Pro-Base under one internal harness, V4.1-Flash-Base matches V4-Pro despite about 1/3 total and 1/4 active parameters, with 5-10% held-out gains. Reported highlights include MMLU-Pro 74.1 versus Pro 73.5, BigCodeBench 60.6 versus 59.2, HumanEval 79.4 versus 76.8, GSM8K 93.0, MATH 61.1 behind Pro 64.5, MGSM 80.2 behind Pro 84.4, LongBench-V2 45.2 versus Pro 51.5, plus native multimodal MMMU-Pro 56.5, CVBench 77.9, DocVQA 95.6, and RefCOCO-average 86.0[^v41-report]. Internal held-out bits-per-byte is lowest on all development, proprietary-code, documentation, and frontier-research splits[^v41-report].

## Post-training pipeline

Each task is a problem, environment, and verification triplet scored for difficulty and correctness to train task-construction itself, with RL trajectories feeding lifecycle re-audits[^v41-report].

General-agent environments mock real SaaS, enterprise, and backend tool interfaces from voluntary employee/partner workflows and reconstruct failure cases for replay and targeted RL. Coding-agent environments come from complex or poor-performance employee sessions plus star-filtered public GitHub repos through a containerized pipeline: build/run feasibility and commit selection with fail-to-pass plus pass-to-pass points, isolated setup with self-test and solution-leak removal, multi-agent attempts, independent inspection for environment, factual, description-mismatch, and hackability issues, then repair and re-verification[^v41-report].

RL scales compute within one scaffold, across scaffold variants, and across heterogeneous scaffolds with continued gains; rollout execution splits into agent sandbox plus scaffold-agnostic worker on DSec outside the preemptible GPU pool with suspend/offload preservation, while successive runs merge checkpoints across scaffolds or configs to aggregate parallel compute[^v41-report].

## DSec

Millions of concurrent sandboxes motivate sharded scale units plus a custom placement engine trading strong consistency for scalability: replicas make good-enough placements from recent measurements while nodes enforce hard admission checks. Sub-NUMA worker VMs raise density from about 1,000 to over 2,500 live containers per node; latency-sensitive execution uses `SCHED_IDLE` for non-sensitive tasks plus core scheduling to isolate sibling hyperthreads[^v41-report]. Per-sandbox AppArmor plus eBPF network policy contain reward hacking, filesystem deletion, and vulnerability exploits including XFS, AppArmor, and mirror-service cases; crashes count as failed trajectories with a repercussion signal[^v41-report].

## Controllable reasoning effort

A scalar `b` in 1-100 is prepended as `Reasoning Effort: {effort}` and trained with subgroup-centered advantages per `(x,b)` plus length penalty `-min(Cmax,k(b)*l/Lnorm)` where `k(b)=k0*exp(-(b-bmin)/tau)` and `tau=lambda*meanDeltaB`. Larger `b` multiplies penalty decay by `e^-1` per `tau`; `k0` sets overall brevity pressure while `tau` sets effort sensitivity under an exponential marginal-utility model[^v41-report].

September 2026 API tiers map max to 100, high to 75, and low to 50. Raising effort 25 to 100 lifts eight-benchmark reasoning average 67.1% to 76.3%, DeepSWE 66.0% to 74.2%, and Terminal-Bench 2.1 82.4% to 90.6% at about 2.5x output tokens; 60-80 recovers most accuracy at under half the max token budget, while 100 lengthens agent trajectories 1.6-1.8x for marginal gains[^v41-report]. Control interpolates to untrained intermediate values and transfers from single-response reasoning to multi-turn exploration and verification[^v41-report].

## Asynchronous training and distillation

Rollout and training colocate and time-share with an in-flight sample bound. Final dispatch is sample-level once completions reach the next prompt's GRPO group size; coarser batch dispatch oscillated metrics and prompt-level dispatch stalled on long tails. Training preempts rollouts and concatenates per-segment expert routing across checkpoints[^v41-report].

Length bias is mitigated by per-dataset concurrency limits and discarding early short samples; off-policy drift by bounding maximum staleness plus masking excessively stale tokens. Token-level interruption enables near-instant checkpoint switching and preemption response; KV, routing, and rollout states persist at token granularity with sample-grained GC for exact resumption[^v41-report].

Final full-vocabulary on-policy distillation spans all domains with over 40 architecturally heterogeneous teachers and efficient switching, supporting mid-training changes to mixture, concurrency, and teachers without disrupting in-flight samples[^v41-report].

## Agentic evaluations

Reasoning uses GPQA Diamond, HLE, internal Codeforces, and MathArena Apex at temperature and top-p 1.0; code agents use Terminal-Bench 2.1/3.0/4.0, DeepSWE v1.1, ProgramBench, and NL2Repo-Bench; security uses SEC-Bench Pro 260505, CyberGym, and ExploitGym; general agents use AutomationBench v1.0.6 and Agents' Last Exam CLI; visual agents use Chartography, BabyVision, and ZeroBench-main. Code-agent defaults are DeepSeek Harness Minimal with 1M context, temperature 1.0, top-p 0.95, mini-SWE for DeepSWE, Claude Code harness for SEC-Bench session compaction, and Claude Code 512K for visual tasks[^v41-report].

Anti-gaming removes internet and git history and purges Go, node, jar, and Python caches, yet decompilation-based vulnerability discovery was still observed, motivating stronger benchmark hardening[^v41-report].

Scaffold robustness holds across Claude Code, Codex, OpenCode, Pi, mini-SWE, and DeepSeek Harness Minimal/Standard/PTC with identical checkpoints and tasks; mini-SWE leads DeepSWE at 74.2 with Minimal at 72.6, while Minimal leads Terminal-Bench 2.1 at 90.6 with mini-SWE at 90.3. Four Claude Code versions average 68.9 on DeepSWE and 87.8 on Terminal-Bench[^v41-report].

Agent Team multi-agent mode uses lead-created persistent teammates in fresh or fork history modes, shared checkout, durable mailbox, shared task board with revision checks, lead-only interrupts, RL collaboration bonus plus DAG-derived critical-path latency penalty, and golden ProgramBench plus no-GPU FrontierSWE-v2 deadlines. Multi-agent Almost@1 reaches 30.04% at 8 hours versus 20.39% single-agent on ProgramBench and Mean@5 reaches 32.90% at 20 hours versus 28.20% on FrontierSWE-v2[^v41-report].

## Contradictions

- Post-training prose claims higher maxima than the extracted Table 3 cells for the same report, including Codeforces 3471 versus table 3289, MathArena Apex 65.6% versus 58.6%, GPQA 90.9% versus 89.9%, DeepSWE 74.2% versus 54.4%, Terminal-Bench 2.1 90.6% versus 82.7%, AutomationBench 54.8% versus 37.7%, and Agents' Last Exam 31.8% versus 25.2%[^v41-report]. Do not quote either side as settled without checking the report PDF/table alignment; both are preserved here as extraction uncertainty.
- Table 3 header-to-column alignment in the Markdown extraction is ambiguous for Opus-5, GPT-5.6, Kimi-K3, GLM-5.3, V4-Pro, V4-Flash, and V4.1-Flash columns; cross-model rankings from that table alone are therefore unsafe[^v41-report].

## Relationships

- Uses [DeepSeek-V4.1-Flash Architecture](deepseek-v41-architecture.md) — model whose data, optimizer, and post-training behavior is evaluated here.
- Uses [DeepSeek-V4.1-Flash Systems](deepseek-v41-systems.md) — replay simulation, DSec sandboxing, and async rollout machinery behind training.
- Related to [SGLang DeepSeek-V4.1 Inference](sglang-deepseek-v41-inference.md) — serving measurements distinct from this report's training and agent evaluations.
- Related to [Miles DeepSeek-V4.1 Verified RL](miles-deepseek-v41-rl.md) — Miles/SGLang RL validation distinct from this report's large-scale RL and distillation runs.

## Coverage limits

- Figure curves for RL scaling, effort tradeoffs, scaffold sensitivity, and multi-agent deadlines were not pixel-verified; numbers follow prose and tables.
- Author list, appendix scaffold versions, and full benchmark tables were summarized rather than exhaustively transcribed.
- Prose-versus-table agentic maxima remain unresolved for the reasons above.

[^v41-report]: DeepSeek-V4.1-Flash tech report — `../raw/DeepSeek_V41_Tech_Report/DeepSeek_V41_Tech_Report.md`, Sections 4-6 plus Appendices B-C and Tables 1-5/Figures 6-12.
