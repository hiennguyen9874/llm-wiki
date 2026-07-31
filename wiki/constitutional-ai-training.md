---
type: Concept
title: Constitutional AI training
description: Constitutional AI uses natural-language principles to generate self-critiques, revisions, and AI-ranked preferences for supervised and reinforcement-learning alignment.
tags: [constitutional-ai, rlaif, rlhf, alignment, reward-modeling, safety]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T00:00:00+07:00 }
sources:
  - id: constitutional-ai-summary
    resource: ../raw/ConstitutionalAI.md
    title: "Constitutional AI overview (Vietnamese summary)"
---

# Constitutional AI training

Constitutional AI (CAI) is an alignment approach in which people specify a written **constitution** of high-level principles, then models apply those principles to produce training signals: self-critiques and revisions for supervised fine-tuning, followed by AI-generated response preferences for reward modeling and reinforcement learning. The supplied summary calls the latter feedback path RLAIF (reinforcement learning from AI feedback).[^constitutional-ai-summary]

## Constitution as supervision

The constitution contains natural-language principles about harms, rights, discrimination, honesty, and useful refusals. It is prompt-level guidance for the critic or judge rather than executable hard rules. Human input remains consequential: people choose the principles, red-team prompts, evaluation design, and how to resolve value conflicts.[^constitutional-ai-summary]

## Two-stage procedure

1. **Constitutional supervised learning:** starting from adversarial or red-team prompts, a model generates an initial answer. Given a sampled constitutional principle, it critiques the answer and revises it; revised answers become supervised fine-tuning targets. Multiple critique–revision rounds may apply different principles.[^constitutional-ai-summary]
2. **RLAIF:** the policy produces candidate answers. An AI evaluator compares them against a constitutional principle, producing winner–loser preferences. A preference/reward model learns to rank the selected answer higher, and KL-regularized reinforcement learning optimizes the policy against that learned reward.[^constitutional-ai-summary]

CAI therefore moves much of *harmlessness* labeling from direct human comparisons to AI application of human-chosen principles; it does not remove human value choices or final evaluation.[^constitutional-ai-summary]

## Relationships

- **Contrasts with:** [InstructGPT human-feedback alignment](instructgpt-human-feedback-alignment.md). The supplied CAI summary distinguishes AI-generated harmlessness preferences from InstructGPT's human-ranked feedback, while both use learned preference signals and reinforcement-learning-style policy optimization.[^constitutional-ai-summary]
- **Evaluated by:** [Constitutional AI behavior and limitations](constitutional-ai-behavior-and-limitations.md).

[^constitutional-ai-summary]: “Constitutional AI overview” (Vietnamese summary), [raw source](../raw/ConstitutionalAI.md), Sections 1–7 and 14–16. This is secondary-source evidence linking to Bai et al., “Constitutional AI: Harmlessness from AI Feedback,” arXiv:2212.08073; the primary paper has not been independently ingested here.
