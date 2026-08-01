---
type: Concept
title: Kimi K3 evaluation and limitations
description: Kimi K3 reports strong coding, agentic, and multimodal results but trails leading proprietary systems overall, with harness, tool, effort, internal-benchmark, and cyber-risk qualifications.
tags: [kimi-k3, evaluation, agents, multimodal, limitations]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-08-01T02:00:00Z }
sources:
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Kimi K3 evaluation and limitations

The Kimi K3 report presents the model as competitive across reasoning, coding, agents, and vision while explicitly placing it behind Claude Fable 5 and GPT-5.6 Sol overall. Its strongest evidence is breadth across public and third-party suites; interpretation is limited by maximum-effort inference, different harnesses and tools, dated leaderboard snapshots, and many internally designed tasks.[^kimi-k3-2026]

## Reported public results

At max effort and temperature 1.0, K3 reports 93.5 on GPQA Diamond, 77.8 on ProgramBench, 88.3 on Terminal-Bench 2.1, 81.2 on FrontierSWE, 91.2 on BrowseComp, 95.0 F1 on DeepSearchQA, and 91.1 on OmniDocBench. It trails the leaders on research-level reasoning (43.5/56.0 HLE without/with tools; 23.4 CritPt) and harder computer-use or knowledge-work suites such as OSWorld 2.0, GDPval-AA v2, and OfficeQA Pro.[^kimi-k3-2026]

Python tools materially change several vision results: Math-Vision rises from 94.3 to 97.8 and ZeroBench-main pass@5 from 23.0 to 41.0. These scores measure the combined model–tool agent, not unaided visual reasoning.[^kimi-k3-2026]

The report cites July 23, 2026 third-party snapshots: Artificial Analysis Intelligence Index 57.1 (#4/580), Vals Index 74.7 (#2/39), WebDev Arena 1,678 Elo (#1/99), Text Arena 1,486 (#8/200), and Agent Arena 9.1 (#4/37). Elo and ranks drift, and each source uses its own setup.[^kimi-k3-2026]

## Configuration and comparability limits

- K3 uses max effort; GPT-5.5 uses xhigh, and some proprietary results include fallback or cyberguard behavior.
- Coding and agent benchmarks use Kimi Code, Claude Code, Codex, or benchmark-specific harnesses; harness quality is entangled with model quality.
- BrowseComp uses context compaction at 300K; full 1M context without management scores 90.4 rather than 91.2.
- Some benchmark branches, hardware, performance gates, and leaderboard dates differ from final or official settings.
- Internal suites are frequently refreshed and can guide training, increasing the risk of evaluation adaptation even when they expose useful failure modes.[^kimi-k3-2026]

## Reported strengths and weaknesses

The internal suite reports particular strength in swarm orchestration, deep research, coding experience, and web development. It reports weaker behavior on long-running assistants, multi-role enterprise collaboration, agent-process discipline, and some agentic-vision and knowledge-work-vision tasks. Case studies demonstrate possible long-horizon outputs, but selected successes do not estimate population reliability.[^kimi-k3-2026]

## Cyber capability and risk

The team reports that human review confirmed about 70% of reviewed vulnerability candidates and 16 previously unknown vulnerabilities across six projects. On a 36-task exploit suite, K3 solved 14 tasks (38.9%) versus GLM-5.2’s 8, mostly in user space; neither model solved three quarters of the kernel track.[^kimi-k3-2026]

Reported failure modes include incomplete exploit chains, poor strategy choice under mitigations, long debugging loops, and weak final verification. An independent UK AISI/NIST assessment reportedly found better exploit-development results than GLM-5.2 but zero arbitrary-code-execution successes on 41 tasks. The paper calls its own evaluation a lower bound; these capabilities nevertheless create material dual-use risk beyond ordinary benchmark quality.[^kimi-k3-2026]

## Cost claims

K3 is reported near the score–cost frontier on four coding and agent suites, including BrowseComp at $2.03 per task. Cost comparisons mix internal measurements and published API prices, model-specific harnesses, and snapshot pricing, so they are operational estimates rather than architecture-normalized efficiency evidence.[^kimi-k3-2026]

## Relationships

- **Evaluates:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Evaluates:** [Kimi K3 agentic post-training](kimi-k3-agentic-post-training.md).
- **Qualifies:** [Test-time compute allocation](test-time-compute-allocation.md), because model, effort, tools, harness, and cost must be compared together.

## Evidence limits

The paper is an author report with broad but heterogeneous evidence. It includes independent results, yet baseline configurations are not uniform and many claims rely on internal benchmarks, reward models, selected case studies, or leaderboard snapshots. Full weights are reported released, but evaluation artifacts and training data are not sufficiently specified here for complete reproduction.[^kimi-k3-2026]

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 6–7 and evaluation tables.
