---
type: Concept
title: NeuS-QA
description: A training-free neuro-symbolic LVQA pipeline that translates questions into temporal-logic specifications, model-checks a VLM-grounded video automaton, and answers from the verified segment.
tags: [video, video-llm, long-video, temporal-grounding, temporal-logic, neuro-symbolic]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-16T10:43:17+07:00 }
sources:
  - id: neus-qa-paper
    resource: ../raw/NeuS-QA/main.tex
    title: "NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning"
---

# NeuS-QA

NeuS-QA is a training-free, plug-and-play long-video question-answering pipeline. It turns a question into atomic event propositions and a temporal-logic specification, grounds those propositions over video frames with a VLM, model-checks the resulting video automaton, then supplies an extended, logic-satisfying interval to an answering VLM.[^neus-qa-paper]

## Pipeline

1. An LLM extracts question-relevant propositions and translates their logical and temporal structure into a specification, using operators such as AND, EVENTUALLY, and UNTIL.[^neus-qa-paper]
2. A frame-level VLM assigns calibrated Yes/No-derived detection probabilities to each proposition over successive frame windows. NeuS-QA incrementally builds a discrete-time Markov-chain video automaton whose states are sampled frames and whose labels are detected propositions.[^neus-qa-paper]
3. A probabilistic model checker (implemented with Stormpy under PCTL in the reported setup) computes whether the automaton satisfies the specification. The system selects a minimal satisfying interval above a calibrated threshold, extends it for preceding or following context, and asks a VLM to answer from that trimmed video.[^neus-qa-paper]

## Evidence and limits

The reported setup uses InternVL2-8B for proposition detection, GPT-o1-mini with few-shot prompting for question-to-logic translation, 3 fps video sampling, and several downstream VLMs for multiple-choice answering.[^neus-qa-paper]

On the paper's selected temporally compositional LongVideoBench categories, NeuS-QA with Qwen2.5-VL-7B reports 60.09% accuracy versus 50.44% for the base VLM; on CinePile it reports 53.66% versus 50.73%. These are author-reported results on filtered LongVideoBench questions and the stated benchmark protocol, not independent evidence of general LVQA performance.[^neus-qa-paper]

Formal verification is exact only relative to the automaton labels and specification. The source identifies missed or subtle VLM event detections as a failure mode: one missed proposition can make a multi-proposition specification unsatisfied and cause false-negative retrieval. Constructing an automaton is also computationally expensive; the authors propose amortizing that cost with a reusable automaton and coarse-to-fine retrieval for repeated queries.[^neus-qa-paper]

## Relationships

- **Instantiates:** [Video-language temporal grounding and reasoning](video-language-temporal-grounding-and-reasoning.md) through explicit temporal-logic specifications and logic-verified evidence retrieval.[^neus-qa-paper]
- **Uses:** [Long-video temporal modeling](long-video-temporal-modeling.md) as query-guided fixed-interval retrieval rather than full-video VLM prompting.[^neus-qa-paper]

[^neus-qa-paper]: [NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning](../raw/NeuS-QA/main.tex)
