---
type: Concept
title: Looped computation and chain-of-thought monitorability
description: Looping adds hidden computation per emitted token but does not by itself remove a model's textual chain-of-thought; shorter traces have competing explanations, and no cited evidence ties looping to less faithful reasoning.
tags: [chain-of-thought, faithfulness, latent-reasoning, monitorability, recurrent-depth]
status: draft
created: 2026-10-03
generated: { by: llm-wiki-agent/1, at: 2026-10-03T10:47:00Z }
stale_after: 2027-03-09
sources:
  - id: raschka2026astra
    resource: ../raw/gpt-6-astra-looped-transformers-and/index.md
    scope: ../raw/gpt-6-astra-looped-transformers-and/
    kind: article
    title: "GPT-6 Astra, Looped Transformers, and Hidden Reasoning"
---

# Looped computation and chain-of-thought monitorability

A looped transformer passes each token's hidden state through shared blocks several times before emitting the next token. A reasoning model built on it still generates its textual chain-of-thought (CoT) one token at a time, as a non-looped model does. Looping therefore adds latent computation per token. It does not turn the visible trace into hidden reasoning. The open question is whether the extra internal computation shortens or degrades traces enough to weaken monitoring. The evidence in the one compiled source is indirect and does not isolate looping as a cause (Synthesis).[^raschka2026astra]

## The claim and the counter-argument

- **Claim (Reported):** *The Information* wrote that the technique it attributes to OpenAI's Astra "obscures some or all of the AI's reasoning." See [OpenAI GPT-6 Astra looped-architecture report](openai-astra-looped-architecture-report.md).[^raschka2026astra]
- **Counter-argument (Opinion):** extra loops are computation, not a storage or concealment mechanism. A model that computes more per token may need fewer scratch-pad tokens. Shorter traces can also come from a more capable model that makes fewer mistakes and backtracks less. Raschka's stated "only valid concern" is that a looped model presents misleading traces more often than a conventional one. He finds no strong evidence of that.[^raschka2026astra]
- **For end users** the visible change is small, because OpenAI has hidden most reasoning traces since o1. The monitorability concern applies mainly to developers.[^raschka2026astra]
- **OpenAI's position (Reported, quoted post):** chief scientist Jakub Pachocki called the reporting "confused." He said CoT monitoring is fragile and trending negatively "for reasons not contingent on architecture changes."[^raschka2026astra]

## Indirect evidence

| Observation | Basis | What it does not show |
| --- | --- | --- |
| At equal accuracy, Astra uses fewer output tokens than GPT-5.6 Sol on OpenAI-published Terminal-Bench 4.0, AA Coding Agent Index v1.4, GPQA Diamond, and FrontierMath Tier 4 plots. Across effort levels, it does not use fewer tokens overall. | Developer-reported benchmark plots (Figure 17) | That looping causes the shorter traces |
| Astra's system card reportedly notes a monitorability regression relative to Sol, associated with shorter, less informative traces | Secondhand report of the system card | That looping is the root cause; trace length alone could explain it |
| Non-looped GPT-5.6 Luna (max) used about 41k output tokens per task at index score 38, versus about 8k for Sol (medium) at score 39 | Artificial Analysis Intelligence Index v4.3 averages charted by the author (Figure 18) | Any looping effect: both are presented as non-looped comparators showing that capability alone can shorten traces |
| A "full-bandwidth transformer" feeds the previous token's final hidden state, gated with the next token's embedding, into the next forward pass. On a 1B base model, this shortened MATH500 traces (median ≈500 → ≈480 "soft" and ≈465 "fused" tokens) at similar or higher pass@1. The effect disappeared after instruction tuning. | Secondhand summary of arXiv 2608.08888 (Wang et al., Figure 6 adaptation) | Faithfulness of the shorter traces; whether conventional scaling gives the same effect. The mechanism recurs across positions, not depth |

The Luna–Sol prose says Luna uses "80% more tokens," but the charted values (41k vs 8k) imply roughly five times as many. The chart is the more specific evidence, and the prose figure appears to be an error (Observed).[^raschka2026astra]

The Huginn-style latent-reasoning model (Geiping et al.) also illustrates the point. Despite "latent reasoning" in its title, the model can still emit a textual CoT, and its loops add computation before each output token.[^raschka2026astra]

## Assessment

Synthesis: three questions remain separate. (1) Does looping shift work from visible tokens into hidden states? It is plausible, but untested at frontier scale. (2) Are the resulting traces less informative to monitors? The Astra system card reportedly says yes, partly, without attribution to architecture. (3) Are traces less faithful? No evidence is cited. Reasoning traces are not guaranteed to be faithful in any architecture, per Turpin et al. (arXiv 2305.04388) as cited by the source.[^raschka2026astra] Compiled primary studies give mixed evidence on latent depth reasoning, and none addresses monitorability directly.

## Relationships

- Concerns: [OpenAI GPT-6 Astra looped-architecture report](openai-astra-looped-architecture-report.md), whose reporting raised the concern.
- Related to: [Latent recurrence safety and faithfulness evidence](latent-recurrence-safety-and-faithfulness.md). Ouro's probe-based faithfulness claim is observational, not causal.
- Related to: [Probing depth-recurrent latent chain-of-thought](probing-depth-recurrent-latent-chain-of-thought.md). Huginn showed little rank-trajectory evidence of latent CoT and small no-CoT gains from more recurrence.
- Related to: [Difficulty-aware reasoning length control](difficulty-aware-reasoning-length-control.md). Trace length can also be shaped directly by training rewards rather than architecture.

[^raschka2026astra]: Sebastian Raschka, *GPT-6 Astra, Looped Transformers, and Hidden Reasoning*, Ahead of AI, 2026-09-09 (web capture `raw/gpt-6-astra-looped-transformers-and/index.md`), §§2 (Figure 4), 5–5.2 (Figures 17–18, Pachocki quote), 6.1, 6.4 (Figure 22), and Conclusion; assets `3faf505f-…png`, `1e048a54-…png`, `4d348be9-…png`. Primary sources (*The Information*, the OpenAI system card, the full-bandwidth transformer paper) are not captured locally.
