---
type: Concept
title: ReAct evaluation and operational limits
description: The supplied ReAct summary reports complementary reasoning and tool-use results, while highlighting prompt sensitivity, unfaithful traces, loop risk, and production safety controls.
tags: [react, agents, evaluation, tool-use, limitations, safety]
status: stable
created: 2026-08-01
generated: { by: llm-wiki-agent/1, at: 2026-07-31T17:07:23Z }
sources:
  - id: yao-react-summary
    resource: ../raw/ReAct.md
    title: ReAct overview (Vietnamese summary)
---

# ReAct evaluation and operational limits

The supplied summary reports that ReAct was evaluated on knowledge-intensive QA and verification (HotpotQA, FEVER) plus interactive environments (ALFWorld, WebShop). Results support complementarity between reasoning and external action rather than a claim that pure ReAct uniformly beats reasoning-only methods; its use also introduces trajectory cost, tool reliability, and real-world action-risk constraints.[^yao-react-summary]

## Reported results

For PaLM-540B, the source reports pure ReAct at 27.4 exact match on HotpotQA and 60.9% accuracy on FEVER, compared with CoT self-consistency at 33.4 and 60.4 respectively. Switching between the approaches improved the reported results: ReAct→CoT-SC reached 35.1 HotpotQA EM, while CoT-SC→ReAct reached 64.6% FEVER accuracy.[^yao-react-summary]

On action-intensive tasks, the source reports a best-of-six-prompt ReAct success rate of 71% in ALFWorld versus 45% for the best Act-only prompt and 37% for the cited BUTLER baseline. In WebShop it reports 66.6 score and 40.0% success for ReAct, versus 62.3 and 30.1% for Act-only; human experts remained higher at 82.1 and 59.6%.[^yao-react-summary]

These are paper-specific, summary-reported results, not guarantees for current models, tools, prompts, or environments.[^yao-react-summary]

## Reliability and cost limits

- A plausible thought trace does not establish that it faithfully exposes the model’s internal decision process; it can be a post-hoc-looking explanation or contain false assumptions.[^yao-react-summary]
- An agent can repeat an uninformative action, so implementations need step limits, repeated-action detection, and recovery or termination rules.[^yao-react-summary]
- Each loop adds reasoning, action, observation, and history tokens, increasing latency and context pressure; behavior is also sensitive to trajectory demonstrations and prompt design.[^yao-react-summary]
- Tool output can be stale, weak, malformed, or misinterpreted. ReAct alone does not make an answer correct or grounded.[^yao-react-summary]
- Actions with external effects require permission boundaries, schema validation, sandboxing, execution logs, budgets, and human confirmation for risky operations; a mistaken tool action can have consequences beyond an incorrect text response.[^yao-react-summary]

## Relationships

- **Evaluates:** [ReAct reasoning-and-acting agent loop](react-reasoning-and-acting-agent-loop.md).
- **Qualifies:** [Chain-of-thought prompting evaluation and limitations](chain-of-thought-prompting-evaluation-and-limitations.md): action observations can correct some unsupported assumptions, but ReAct traces retain a faithfulness limit and add tool-specific failure modes.[^yao-react-summary]

[^yao-react-summary]: “ReAct overview” (Vietnamese summary), [raw source](../raw/ReAct.md), Sections 6–9 and 12–15. This is secondary-source evidence summarizing Yao et al., “ReAct: Synergizing Reasoning and Acting in Language Models” (ICLR 2023); the primary paper has not been independently ingested here.
