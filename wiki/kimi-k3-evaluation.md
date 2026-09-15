---
type: Concept
title: Kimi K3 Evaluation and Case Studies
description: Frontier-level coding, agentic, knowledge, reasoning, and vision results trailing only Fable 5 and GPT-5.6 Sol with strong cost efficiency.
tags: [kimi-k3, evaluation, benchmarks, agentic-coding, computer-use, vision, cybersecurity, cost-efficiency, case-studies]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: k3-eval
    resource: ../raw/arXiv-2607.24653v1/6-eval.tex
    title: Kimi K3 Technical Report — evaluations
  - id: k3-eval-table
    resource: ../raw/arXiv-2607.24653v1/tables/k3_eval.tex
    title: Kimi K3 Technical Report — main eval table
  - id: k3-internal
    resource: ../raw/arXiv-2607.24653v1/tables/k3_internal_eval.tex
    title: Kimi K3 Technical Report — internal eval table
  - id: k3-third
    resource: ../raw/arXiv-2607.24653v1/tables/k3_third_party_eval.tex
    title: Kimi K3 Technical Report — third-party eval table
  - id: k3-webdev
    resource: ../raw/arXiv-2607.24653v1/tables/k3_webdev_internal.tex
    title: Kimi K3 Technical Report — webdev table
  - id: k3-cases
    resource: ../raw/arXiv-2607.24653v1/7-case-study.tex
    title: Kimi K3 Technical Report — case studies
  - id: k3-concl
    resource: ../raw/arXiv-2607.24653v1/8-conclusion.tex
    title: Kimi K3 Technical Report — conclusion
---

Overall Kimi K3 closely trails the strongest proprietary models Claude Fable 5 and GPT-5.6 Sol while consistently outperforming Claude Opus 4.8, GPT-5.5, and open-weight GLM-5.2; it sits on or near the cost-efficiency frontier and is released as full open weights, described as the first open 3T-class model[^k3-eval][^k3-concl].

## Benchmark setup

Four axes: Reasoning and Knowledge (GPQA Diamond, CritPt, AA-LCR, HLE-Full with/without tools); Coding (DeepSWE, ProgramBench, Terminal-Bench 2.1, FrontierSWE, SWE-Marathon, PostTrainBench, MLS-Bench-Lite, SciCode); Agentic (BrowseComp, DeepSearchQA, ResearchRubrics, Toolathlon-Verified, MCPMark-Verified, MCP-Atlas, AutomationBench, JobBench, GDPval-AA v2, AA-Briefcase, Agents Last Exam, APEX-Agents, OfficeQA Pro, SpreadsheetBench 2, OSWorld-Verified/2.0, SaaS-Bench, tau3-Banking, Harvey Lab-AA, CorpFin v2, Finance Agent v2, Legal Research Bench); Vision (WorldVQA, OmniDocBench, PerceptionBench, Video-MME, MMVU, BabyVision with Python, plus MMMU-Pro, CharXiv RQ, Math-Vision, ZeroBench-main with/without Python)[^k3-eval].

- Baselines at max effort except GPT-5.5 xhigh; Fable 5 includes fallbacks, GPT-5.6 Sol includes potential cyberguards; open baseline GLM-5.2[^k3-eval].
- K3 uses effort max, temperature 1.0; top-p 0.95 single-step, 1.0 agentic; recommended split is 0.95 reasoning/knowledge and 1.0 coding/agentic[^k3-eval].
- Coding under Kimi Code, Claude Code, or Codex; DeepSWE v1.1 (67.3 with mini-SWE-agent on leaderboard); Terminal-Bench best harness; SWE-Marathon H20-calibrated branch as of 2026-07-09 with 35% Fable fallbacks; PostTrainBench official Harbor max effort 3-run H20 not H100; FrontierSWE dominance recomputed 2026-07-16[^k3-eval].
- Agentic notes: OfficeQA Pro gives PDF corpus as images only; MCP-Atlas 500-task public 100-turn Gemini 3.1 Pro judge; AutomationBench 600 public; BrowseComp compaction at 300K, but 90.4% with full 1M and no management[^k3-eval].
- Vision averaged over 3 runs (ZeroBench 5); MMMU-Pro preserves order and prepends images; WorldVQA answer forced via prompt due to refusals[^k3-eval].
- Third-party citations as of 2026-07-23/24: AA for GDPval, Briefcase, tau3, Harvey, APEX, SciCode, AA-LCR, CritPt; Vals AI for CorpFin, Finance Agent, Legal Research; official leaderboards for Agents Last Exam (K3/Kimi Code, GPT/Codex, Fable/Opus/GLM/Claude Code), Toolathlon-verified, JobBench[^k3-eval].

## Main results

Selected K3 (max) vs Fable 5 / GPT-5.6 Sol / Opus 4.8 / GPT-5.5 / GLM-5.2[^k3-eval-table]:

- Reasoning: GPQA 93.5 (competitive, GPT-5.6 94.1 best); CritPt 23.4 trails Fable 28.6, Sol 32.3, GPT-5.5 27.1; AA-LCR 74.7 best; HLE 43.5/56.0 without/with tools trails Fable 53.3/63.0 and Sol 44.5/58.0.
- Coding: ProgramBench 77.8 best; SWE-Marathon 42.0 best (+7 over Fable 35.0); Terminal 88.3 essentially tied with Sol 88.8; FrontierSWE 81.2 second behind Fable 86.6; DeepSWE 67.5 behind Fable 70.0 and Sol 73.0 but ahead of Opus/GPT-5.5; PostTrainBench 36.6 second behind Fable 41.4; MLS-Lite 48.3 second; SciCode 58.7 second.
- Agentic bests: BrowseComp 91.2, DeepSearchQA 95.0 F1, ResearchRubrics 76.2, MCPMark-Verified 94.5, AutomationBench 30.8, SpreadsheetBench 2 34.8, tau3-Banking 33.4, Harvey Lab-AA 94.6; Elo knowledge-work led by Fable: GDPval 1686 third (Fable 1747, Sol 1736), Briefcase 1548 second (Fable 1583); near ties CorpFin 71.6 vs 71.8 and OSWorld-Verified 84.8 vs 85.0; harder computer-use OSWorld 2.0 58.3 and SaaS-Bench 60.1 led by Fable or Sol.
- Vision: Math-Vision 94.3 rising to 97.8 with Python; ZeroBench-main ties Fable 23.0 pass@5 rising to 41.0 with Python (Fable 46.0); OmniDocBench 91.1 best; WorldVQA 51.0 second behind Fable 56.7 ahead of Sol/Opus; PerceptionBench 58.5 second, Video-MME 90.0 best, MMVU 82.1 best.

Research-level reasoning (HLE with/without tools, CritPt) remains the stated improvement direction[^k3-eval].

## Internal evaluation

In-house benchmarks refreshed to track failure modes, split into coding/general-agent/conversational experience; harness matters so table records K3 harness while Claude/GLM use Claude Code and GPT use Codex except common-harness suites (OpenClaw for ClawBench, MIRA harness for MIRA, Kimi Work for Behavior/Chat, Kimi Code for CLIF/Agentic Vision)[^k3-eval][^k3-internal].

- Coding: KCB 2.0 trails only Fable (73.7 Claude Code); Coding Experience best (59.9 Claude Code); Webdev blind-expert +31.0 overall over Opus 4.8, largest on 3D/WebGL/Shader +59.1, Games +14.9, Website/UI Clone +26.3[^k3-internal][^k3-webdev].
- General agency strengths: Swarm Bench 76.3 lead, Deep Research 90.0 lead, Finance Bench 62.6 essentially tied with Sol 62.7, marked improvement over prior generation[^k3-eval].
- Trails on Agent Behavior, MIRA (64.1 vs Fable 72.9), 24/7 ClawBench 2.0, Agentic Vision, KWV; remaining KAET, CLIF (52.4 best), Online Experience, DECK, Faithfulness (85.5, metric 1-hallucination rate), Chat All-in-One rank first or close second[^k3-eval][^k3-internal].

## Cybersecurity evaluation

Two-tier progression of rising operational risk, all in standard real-world configs; Anthropic/OpenAI frontier models refuse cyber tasks so excluded except GLM-5.2 baseline where noted[^k3-eval].

- Tier 1 vulnerability discovery plus PoC (defensive): dozens of widely deployed systems (kernels, databases, AI services, web frameworks, blockchain, VPN); ~70% of human-reviewed candidates confirmed genuine, including 16 previously unknown across six projects; examples include remotely triggerable Linux heap out-of-bounds write from incomplete upstream fix (remote DoS through latest upstream) and RDMA Dirty-COW-class missing permission check enabling kernel writes to read-only pages (deterministic local priv-esc)[^k3-eval].
- Tier 2 end-to-end exploit development: 36 human-solvable tasks (~540 expert-hours, ~15h each) with 16 user-space (PostgreSQL, XWiki, Apache, CMS/apps with source plus live instance, no extra hardening) and 20 kernel QEMU historical CVEs (unprivileged-to-root C, progressive mitigations); K3 solves 14/36 (38.9%) vs GLM-5.2 8/36, but 10/14 from user-space and neither solves three-quarters of kernel track[^k3-eval].
- Gap attributed to incomplete final exploit stage, poor strategy under mitigations (persisting control-flow hijack over simpler data-only), unproductive debug loops, insufficient final verification[^k3-eval].
- Independent UK AI Security Institute plus NIST CAISI assessment consistent: ExploitBench 32% vs 24%, 17 vs 11 steps on 32-step enterprise net (~20h human), but 0/41 arbitrary code execution, trailing frontier cyber-capable models; authors treat results as lower bound revisited per major update[^k3-eval].

## Third-party evaluation

Headlines as of 2026-07-23[^k3-eval][^k3-third]:

- Artificial Analysis Intelligence Index v4.1: 57.1, #4/580 (third if Sol effort variants single entry), behind Fable 59.9 and Sol 58.9, ahead of all others.
- Vals AI GDP-weighted Vals Index: 74.7%, #2/39, behind Fable 75.1% ahead of Sol 73.1%.
- Arena: WebDev 1678 Elo #1/99 ahead of Fable 1634, first open model to top it; Text 1486 #8/200; Agent 9.1 #4/37 behind Fable 12.7, Sol 10.1, Opus 9.8 (Elo drifts with matches).

## Cost efficiency

Score versus per-task cost on KCB 2.0, BrowseComp, GDPval, Briefcase; KCB costs internal (K3/Kimi Code, others/Claude Code), BrowseComp K3 internal while Claude/GPT from published charts, GDPval/Briefcase from AA pay-per-token pricing 2026-07-23[^k3-eval].

- KCB 2.0: 4.0 points behind Fable at 38% cost; high effort already matches Opus max at ~1/3 cost[^k3-eval].
- BrowseComp: best 91.2% at $2.03/task, half Sol and order of magnitude cheaper than Claude max[^k3-eval].
- GDPval: within 50 Elo of Sol at 13% lower cost, 2.6x cheaper than Fable; Briefcase second-best at roughly half Fable cost[^k3-eval].

## Case studies

Representative technical demonstrations, not controlled benchmarks[^k3-cases]:

- GPU kernel optimization in identical sandboxes with 24h budget over AttnRes, DSA, KDA, MLA-512 on Hopper plus alternative-vendor GPGPU: AttnRes 283.6ms to 114.4ms, DSA -55.1%, KDA -73.6%, MLA over half peak TFLOPS; matches Fable 5 with fallback and substantially outperforms Opus 4.8, Sol, GPT-5.5; early K3 checkpoint already handled most late-stage kernel work[^k3-cases].
- GPU compiler MiniTriton (`https://github.com/MoonshotAI/minitriton`): compact Triton-like compiler with tile-level Python frontend, warp-level MLIR annotation/opt, PTX codegen plus dual-mode PyTorch-like tensor lib sharing DSL compiler/runtime plus autograd, NN modules, NCCL distributed, sparse/viz; on L20 beats torch eager and `torch.compile` in geomean, from-scratch tensor-core matmul ~90% of measured roof near cuBLAS, DSL KDA prefill beats matched Triton, end-to-end GPT loss tracks torch with grad diff ≤ torch fp32 rounding (`1e-4` vs fp64), plus 2-GPU NCCL data-parallel training[^k3-cases].
- Chip design proof-of-concept: nano model with hybrid KDA plus NoPE-MLA, Block AttnRes size 2, sigmoid MoE with one shared expert, group-wise INT4 (128); single 48h Kimi Code run with open EDA and Nangate45 closes 100MHz in 4mm² analytical budget for >8700 tok/s RTL-simulated decode with 1.46M cells, 0.277MiB SRAM, INT4 MAC with fused dequant; RTL at `https://github.com/MoonshotAI/nano-kpu`[^k3-cases].
- Coding for research: I-Love-Q universal relations reproduced from 20+ papers with cross-validation, 300+ equations of state, published-formula inconsistencies found, 3000+ lines Python plus interactive HTML dashboard in ~2h versus typical 1-2 weeks[^k3-cases].
- Knowledge work in Kimi Work: 42-year AI ASIC site from 87 quarterly reports plus 99 PDFs (>11000 pages) via 2800+ web searches and 1100+ terminal queries over 120+ refinements; 391 GWTC-5 gravitational-wave events via 20+ concurrent subagents into 7 visualizations, 2 tables, 10+ paper synthesis[^k3-cases].
- Video/motion: self-architecture 3Blue1Brown-style explainer and teaser edited from 56 clips with selection, motion-matched cuts, beat sync, audio, revisions; comparable dense short video typically 1-2 editor-days[^k3-cases].

## Relationships

- Depends on [Kimi K3 Architecture and Pre-training](kimi-k3-architecture-pretraining.md) — evaluated model scale and hybrid design.
- Depends on [Kimi K3 Post-Training and Agentic RL](kimi-k3-posttraining-agentic-rl.md) — effort levels, harnesses, and environments behind these scores.
- Related to [Kimi K3 Local Deployment](kimi-k3.md) — same model with overlapping benchmark table; this report is the canonical eval source.
- Related to [Kimi K3 Systems and Infrastructure](kimi-k3-systems-infrastructure.md) — serving and cost-efficiency context.

## Coverage limits

- Numbers are report-stated under stated harnesses, efforts, dates, and calibrations (H20 branches, Harbor settings, AA/Vals/Arena snapshots); Elo and leaderboard ranks drift as matches accumulate.
- Internal-benchmark refusals/fallbacks annotated in source footnotes affect comparability and are noted but not re-adjudicated.
- Cyber results are conditioned on current version and coverage and stated as lower bound.
- Case-study trajectories and figures were read as text; kernel latencies, roofline points, and RTL simulations were not independently reproduced.

[^k3-eval]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/6-eval.tex`, four-axis suite plus max-effort/temp/top-p configs plus harness/calibration notes, reasoning/coding/agentic/vision takeaways, internal capability/experience breakdown, two-tier cyber design plus Tier1 confirmations plus Tier2 14/36 breakdown plus four failure modes plus UK-AISI/CAISI consistency, third-party headlines, four-suite cost methodology plus frontier claim.
[^k3-eval-table]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/tables/k3_eval.tex`, full public comparison K3 vs Fable 5/GPT-5.6 Sol/Opus 4.8/GPT-5.5/GLM-5.2 across reasoning/coding/agentic/vision including dual without/with-tool cells.
[^k3-internal]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/tables/k3_internal_eval.tex`, in-house results by harness with Claude/Codex/MIRA/OpenClaw/Kimi splits, refusal/fallback footnotes, faithfulness as 1-hallucination rate.
[^k3-third]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/tables/k3_third_party_eval.tex`, AA Index 57.1, Vals 74.7%, Arena WebDev/Text/Agent ranks as of 2026-07-23.
[^k3-webdev]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/tables/k3_webdev_internal.tex`, blind-expert win/tie/lose vs Opus 4.8 with +31.0 overall and domain splits.
[^k3-cases]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/7-case-study.tex`, 24h kernel optimization deltas, MiniTriton L20/cuBLAS/GPT-training claims, nano-KPU 48h 100MHz/8700-tok-s design, I-Love-Q 2h pipeline, ASIC/GW knowledge-work scale, 56-clip video editing effort analogy, GitHub links for MiniTriton and nano-kpu.
[^k3-concl]: Kimi K3 Technical Report — `../raw/arXiv-2607.24653v1/8-conclusion.tex`, open 2.8T native-vision 1M-context KDA plus AttnRes frontier claim with remaining proprietary gaps.
