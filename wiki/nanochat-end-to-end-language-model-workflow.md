---
type: Concept
title: nanochat end-to-end language-model workflow
description: nanochat provides one compact pipeline from BPE training and parquet pretraining through base evaluation, supervised chat tuning, optional GSM8K policy-gradient tuning, and KV-cached conversation.
tags: [nanochat, tokenization, pre-training, supervised-fine-tuning, reinforcement-learning, evaluation, inference]
status: stable
created: 2026-08-21
generated: { by: llm-wiki-agent/1, at: 2026-08-21T15:55:51Z }
sources:
  - id: nanochat-readme
    resource: ../raw/nanochat/README.md
    title: nanochat README
  - id: nanochat-speedrun
    resource: ../raw/nanochat/runs/speedrun.sh
    title: nanochat speedrun pipeline
  - id: nanochat-tokenizer
    resource: ../raw/nanochat/nanochat/tokenizer.py
    title: nanochat tokenizer and conversation rendering
  - id: nanochat-loader
    resource: ../raw/nanochat/nanochat/dataloader.py
    title: nanochat pretraining dataloader
  - id: nanochat-base-eval
    resource: ../raw/nanochat/scripts/base_eval.py
    title: nanochat base-model evaluation
  - id: nanochat-core-eval
    resource: ../raw/nanochat/nanochat/core_eval.py
    title: nanochat CORE evaluator
  - id: nanochat-sft
    resource: ../raw/nanochat/scripts/chat_sft.py
    title: nanochat supervised fine-tuning
  - id: nanochat-rl
    resource: ../raw/nanochat/scripts/chat_rl.py
    title: nanochat GSM8K reinforcement learning
---

# nanochat end-to-end language-model workflow

nanochat is organized as an inspectable lifecycle rather than only a model file: it trains a 32K BPE tokenizer, streams and packs pretraining documents, trains and evaluates a base model, supervised-fine-tunes chat and tool-use behavior, optionally applies a simplified on-policy GSM8K policy-gradient stage, and serves the result through a KV-cached CLI engine.[^nanochat-readme][^nanochat-speedrun]

## Tokenization and pretraining data

The tokenizer trains mergeable byte-pair ranks with `rustbpe` and constructs a `tiktoken` encoding for inference. Its special vocabulary marks conversation roles, Python-tool calls, and tool outputs. Conversation rendering supervises assistant text and tool-call tokens but masks user text, control prefixes, and externally produced tool-output tokens.[^nanochat-tokenizer]

Pretraining reads parquet row groups sharded by distributed rank, tokenizes text in batches, and packs each sequence row from BOS-prefixed documents. A best-fit buffer chooses the largest document that fits; when none fits, it crops the shortest buffered document to maintain 100% tensor utilization. The source estimates about 35% token loss from cropping at length 2,048, so utilization of model positions does not mean utilization of all source tokens.[^nanochat-loader]

The loader persists approximate parquet-file, row-group, and epoch position for resume. Validation reserves the final parquet shard, while all preceding shards are training data; this is an implementation split, not evidence of deduplication or contamination control.[^nanochat-loader]

## Base training and evaluation

The reference speedrun downloads shards, trains and evaluates the tokenizer, pretrains a depth-24 model on eight H100 processes with FP8 enabled, then evaluates and supervised-fine-tunes it. The script currently ends after SFT evaluation; RL is available separately rather than included in that reference run.[^nanochat-speedrun]

Base evaluation reports bits per byte, generated samples, and DCLM CORE. CORE renders multiple-choice, schema, and language-modeling prompts, scores target spans, subtracts task random baselines, and averages centered task scores.[^nanochat-base-eval][^nanochat-core-eval] A source TODO says the local SQuAD result does not match its reference, so CORE equivalence is not fully resolved.[^nanochat-core-eval]

## Supervised and reinforcement post-training

SFT mixes SmolTalk conversations with repeated MMLU auxiliary-training and GSM8K rows. It best-fit packs complete conversations, pads rather than crops when none fits, and applies cross-entropy only where the tokenizer’s assistant loss mask is one. It evaluates validation BPB plus a centered ChatCORE aggregate over ARC-Easy, ARC-Challenge, MMLU, GSM8K, and HumanEval.[^nanochat-sft]

The optional RL script is accurately described by its own comments as simpler than GRPO. For each GSM8K prompt it samples a group, computes task rewards, subtracts only the group mean, and maximizes token-normalized on-policy log probability weighted by that centered reward. It has no reference model, KL penalty, PPO importance ratio, clipping, critic, or reward-standard-deviation normalization. Prompt and forced tool-output tokens are masked from the policy-gradient objective.[^nanochat-rl]

## Evidence and trust limits

- Repository code and README establish implementation behavior, not independent benchmark replication, dataset quality, safety, or cost validation.
- The source bundle includes development notebooks, logs, images, tests, and task adapters; this ingest inspected the README and material runtime paths but did not exhaustively review every notebook, image, test, or historical development note.
- Dataset downloads and evaluation bundles are external mutable dependencies unless separately pinned and preserved; the checked-in source does not contain the resulting training data or model checkpoints.

## Relationships

- **Trains:** [nanochat modern GPT reference implementation](nanochat-modern-gpt-reference-implementation.md).
- **Uses:** [nanochat distributed Muon–AdamW training](nanochat-distributed-muon-adamw-training.md) in pretraining and SFT.
- **Implements:** [Causal language modeling: training and sampling](causal-language-modeling-training-and-sampling.md).
- **Contrasts with:** [Group Relative Policy Optimization](group-relative-policy-optimization.md), because nanochat’s optional RL removes GRPO’s PPO-style and standardized group-advantage machinery.

[^nanochat-readme]: Andrej Karpathy, [nanochat README](../raw/nanochat/README.md), stated lifecycle, setup, research workflow, and reported results.
[^nanochat-speedrun]: nanochat contributors, [speedrun pipeline](../raw/nanochat/runs/speedrun.sh), reference tokenizer, pretraining, evaluation, and SFT commands.
[^nanochat-tokenizer]: nanochat contributors, [tokenizer implementation](../raw/nanochat/nanochat/tokenizer.py), BPE construction, special tokens, conversation rendering, and supervision masks.
[^nanochat-loader]: nanochat contributors, [pretraining dataloader](../raw/nanochat/nanochat/dataloader.py), parquet sharding, resume state, and BOS-aligned best-fit cropping.
[^nanochat-base-eval]: nanochat contributors, [base-model evaluation](../raw/nanochat/scripts/base_eval.py), BPB, sample, and centered CORE orchestration.
[^nanochat-core-eval]: nanochat contributors, [CORE evaluator](../raw/nanochat/nanochat/core_eval.py), prompt rendering, target-span scoring, task evaluation, and unresolved SQuAD mismatch note.
[^nanochat-sft]: nanochat contributors, [supervised fine-tuning](../raw/nanochat/scripts/chat_sft.py), task mixture, packing, loss mask, optimizer continuation, and ChatCORE evaluation.
[^nanochat-rl]: nanochat contributors, [GSM8K reinforcement-learning script](../raw/nanochat/scripts/chat_rl.py), rollout, reward, centered advantage, objective, and pass@k evaluation.
