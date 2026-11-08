---
type: Concept
title: Hy-Memory-30B-A3B reward and credit assignment
description: Failure-surface probes, evidence-attributed rewards, bank-growth penalty, and chunk-level GRPO for memory writing.
tags: [agent-memory, hy-memory, reinforcement-learning, reward, paper]
status: stable
created: 2026-11-08
generated: { by: llm-wiki-agent/1, at: 2026-11-08T02:52:40Z }
sources:
  - id: hy-writer
    resource: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/Hy-Memory-30B-A3B.md
    scope: ../raw/arXiv-2610.22196v1-Hy-Memory-30B-A3B/
    kind: paper
    revision: arXiv-2610.22196v1
    title: "Hy-Memory-30B-A3B: Attributed Reinforcement Learning for Long-Term Memory Writing"
---

# Hy-Memory-30B-A3B reward and credit assignment

**Reported:** The [writer's](hy-memory-30b-writer-training.md) training treats memory writing as sequential control over an external bank. Local probes give dense feedback, cross-chunk questions attribute recovered gold evidence to source chunks, and traps plus a token-growth penalty discourage storing everything. The feedback measures retrieval and answerability, not the correctness of hidden reasoning (`main.tex`, §Reward Construction, §Reward and Credit Assignment).[^hy-writer]

## Reward data and examination

- The per-chunk annotation pass sees the current chunk and extracted facts from two preceding chunks for reference resolution and novelty; only current-chunk facts earn local credit. The outcome pass sees current-window and earlier facts and constructs cross-chunk questions with evidence IDs and gold facts. Gold facts go to the outcome judge, never the bank, retrieval query or answer model; earlier-window facts cannot earn current credit (`main.tex`, §Two annotation passes, §Rubrics and gold-fact attribution).[^hy-writer]
- Probe types cover specificity, semantic precision including negation, plain recall, secondary detail, state transitions, should-not-store traps, content versus meta-summary, and casual detail. Cross-chunk questions test temporal, aggregation, multi-hop, coexistence and related behavior (`main.tex`, Table `tab:taxonomy`).[^hy-writer]
- Structural, causal-locality, rubric-independence and synthetic-answer discriminability checks filter the artifact. Reported final counts: 12,671 windows, 57,616 chunks, 164,576 positive probes, 8,599 traps, ~60.8k outcome questions, and 222,395 gold-fact references; at most three positive probes and one trap per chunk. Human agreement and leakage audits were future work (`main.tex`, §Data verification, Table `tab:assign`).[^hy-writer]
- After all chunks are written, the harness retrieves, the frozen answer model answers from the retrieved block, and the frozen judge scores against the reference and rubric. PRM is the mean of positive and trap probe scores; a chunk with no valid probes receives zero. Service failures are excluded from the denominator, unlike policy failures. ORM averages per-question recovered evidence credit for a chunk (`main.tex`, §Three-hop examination through §Attributed outcome reward).[^hy-writer]

## Score and optimization

For growth ratio `g` = bank-token growth / input-chunk tokens, harness thresholds `l` and `u` define `x = clip((g-l)/(u-l), 0, 1)` and `pen = (exp(3x)-1)/(exp(3)-1)`. Shrinking is neither penalized nor directly rewarded. The reported weights and `gamma=0` reduce the chunk score to **`s[t] = PRM[t] + 2 ORM[t] - 0.3 pen[t]`** (`main.tex`, §Bank-growth penalty, §Combined score).[^hy-writer]

Within each window, sequence, harness and chunk position, GRPO normalizes scores across valid rollouts: `A[i,t] = (s[i,t] - mean_t)/(std_t + epsilon)`. Each rollout has one baseline vote even when a write involves multiple model calls; all of its segments receive that chunk's advantage. Fewer than two valid rollouts give zero advantage. The final bank with maximal sum of chunk scores is selected for the next window, distinct from the per-chunk gradient choice; if all candidates suffer platform faults the prior bank is reused (`main.tex`, §Chunk-level GRPO, §Bank carry-forward).[^hy-writer]

## Trust and operational caveats

Gold-evidence attribution is not a counterfactual proof of causation; retrieval and the fixed reader can also affect the score. The paper reports no controlled component ablations or human-judge agreement and leaves training/evaluation near-duplicate and sequence-level leakage audits to future work. Engineering checks distinguish invalid policy actions (low reward) from service failures (retry/exclude), verify bank persistence and rollout isolation, and reject missing teacher outputs or chunk mappings (`main.tex`, §Data verification, §Engineering Lessons: Silent Failures, §Limitations and Future Work).[^hy-writer]

[^hy-writer]: Tencent Hunyuan, arXiv 2610.22196v1, `main.tex`; section and table locators inline. Claims are Reported; no training or evaluation was reproduced. Package coverage is recorded in [writer and training](hy-memory-30b-writer-training.md).
