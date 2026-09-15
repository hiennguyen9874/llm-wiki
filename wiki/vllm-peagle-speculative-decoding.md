---
type: Concept
title: vLLM P-EAGLE Speculative Decoding
description: Parallel EAGLE drafting that predicts K tokens per forward pass in Speculators 0.6.0 with COD sampling, learnable masks, and flex-attention masking.
tags: [vllm, speculative-decoding, peagle, speculators, eagle]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: peagle
    resource: ../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md
    title: Speeding up LLM inference with P-EAGLE in vLLM Speculators
---

P-EAGLE (Parallel EAGLE) extends EAGLE-3 with parallel drafting: at each position it predicts the next K tokens in one forward pass instead of autoregressively predicting token 1, feeding it back, then predicting token 2, reducing drafting latency and improving hardware utilization while preserving the verifier model's output distribution[^peagle].

## Relation to EAGLE-3

EAGLE-3's draft model is a small model — described as a single Llama 3 layer — that proposes tokens ahead for parallel target verification; rejected tokens discard the remainder of the speculative sequence[^peagle]. P-EAGLE keeps the same propose-then-verify guarantee but introduces prediction depths: the target verifies all K parallel predictions in one forward pass and accepts the correct prefix[^peagle].

The parallel strategy is particularly beneficial for long reasoning traces, where cumulative sequential-draft cost otherwise limits speculative-decoding speedup[^peagle].

In Speculators v0.6.0, `PEagleDraftModel` inherits from `Eagle3DraftModel` and remains compatible with the existing EAGLE-3 framework[^peagle].

## Training optimizations

### COD sampling

Direct multi-depth training would need memory proportional to depths by sequence length. Conditional Drop-token (COD) sampling applies geometric decay: depth 0 keeps all positions, depth 1 keeps 0.7, depth 2 keeps 0.49, and so on, with a 0.2 floor so the deepest levels are not starved[^peagle]. Deeper predictions therefore train on progressively fewer positions per batch[^peagle].

### Learnable mask representation

Deeper depths have no real input token yet, so P-EAGLE fills them with a dedicated `mask_token_id` placeholder[^peagle]. `resolve_mask_token_id` resolves it in order: explicit CLI argument first, then the verifier tokenizer's built-in mask token, then dynamically adding a `<|MASK|>` special token when unused embedding slots exist, then `pad`, `eos`, or `unk`, and raises an error when none succeed[^peagle]. The guidance is to choose a mask ID without semantic or special-character meaning in the vocabulary[^peagle].

Token-level masking is paired with a learnable `mask_hidden` tensor of shape `[1, 1, 3*hidden_size]` that fills hidden states at unsampled positions, replacing EAGLE-3's fixed padding with a learned "empty, look around me" signal that lets attention pull from real depth-0 positions[^peagle]. Unlike EAGLE-3, which freezes its embedding table because every position has a real token, P-EAGLE unfreezes the table so the mask-token entry can learn a meaningful empty-position representation[^peagle].

### Flex-attention mask

Standard causal masking does not apply to multi-depth single-pass prediction. P-EAGLE builds a custom flex-attention mask[^peagle]:

- Depth-0 positions attend causally to each other as normal autoregressive base context with real tokens and hidden states.
- Deeper positions attend to their own rollout chain: for example a depth-2 token at anchor 5 sees the depth-1 and depth-0 tokens at the same anchor, but not rollouts starting at anchor 3.
- All positions attend to preceding depth-0 context up to their anchor position.

In short, each position sees all causal base context plus its own rollout chain, never sideways rollouts or forward base-sequence positions[^peagle].

> Architecture diagram inspected at `../raw/speeding-llm-inference-p-eagle-vllm-speculators/assets/image1_13.jpg.webp`: Step 1 shows the frozen N-layer target emitting a new token plus `(h_prompt, h_context)`; Step 2 shows Pos 1 as NTP with `emb(new)` plus target hidden states and Pos 2–4 as MTP with `emb(mask)` plus learnable `h_shared`, concatenated to a `2d` combined input through N attention plus feed-forward blocks and the target `lm_head` to emit `t1`–`t4`.

## End-to-end training pipeline

The source demonstrates Qwen3-8B; the process is stated to work the same for other supported models[^peagle]:

1. Prepare data:
    ```bash
    python scripts/prepare_data.py \
      --model Qwen/Qwen3-8B --data sharegpt \
      --output ./output/peagle_qwen3_8b \
      --max-samples 5000 --seq-length 4096
    ```
    Takes about 30 seconds and outputs tokenized Arrow files plus a token-frequency distribution[^peagle].
2. Extract hidden states with vLLM:
    ```bash
    CUDA_VISIBLE_DEVICES=0,1 python scripts/launch_vllm.py Qwen/Qwen3-8B \
      --hidden-states-path ./output/peagle_qwen3_8b/hidden_states \
      -- --data-parallel-size 2 --port 8000

    python scripts/data_generation_offline.py \
      --preprocessed-data ./output/peagle_qwen3_8b \
      --endpoint http://localhost:8000/v1 \
      --output ./output/peagle_qwen3_8b/hidden_states \
      --max-samples 5000 --concurrency 32 --validate-outputs
    ```
    For Qwen3-8B, hidden states come from layers 2, 18, and 33 — early, mid, and late representations of the 41-layer model — concatenated into a 3 × 4096 input tensor[^peagle].
3. Train:
    ```bash
    CUDA_VISIBLE_DEVICES=0,1 torchrun --standalone --nproc_per_node 2 \
      scripts/train.py \
      --verifier-name-or-path Qwen/Qwen3-8B \
      --data-path ./output/peagle_qwen3_8b \
      --hidden-states-path ./output/peagle_qwen3_8b/hidden_states \
      --save-path ./output/peagle_qwen3_8b/checkpoints \
      --speculator-type peagle \
      --num-layers 4 --num-depths 4 \
      --down-sample-ratio 0.7 --down-sample-ratio-min 0.2 \
      --no-norm-before-residual \
      --mask-token-id 151669 \
      --scheduler-type cosine --epochs 5 --lr 6e-4 --total-seq-len 4096
    ```
    On 4× H100s with 5K samples, training takes about 50 minutes end-to-end[^peagle].
4. Deploy:
    ```bash
    vllm serve ./output/peagle_qwen3_8b/checkpoints/checkpoint_best
    ```
    Every checkpoint is directly servable in vLLM, which reads the config and enables speculative decoding automatically[^peagle].

## Example model quality

The published [RedHatAI/Qwen3-8B-speculator.peagle](https://huggingface.co/RedHatAI/Qwen3-8B-speculator.peagle) reports per-position acceptance and mean accepted length[^peagle]:

| Dataset | Pos 1 | Pos 2 | Pos 3 | Pos 4 | Pos 5 | Pos 6 | Pos 7 | Avg length |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HumanEval | 81.3% | 59.0% | 41.1% | 27.9% | 18.8% | 12.8% | 8.9% | 3.500 |
| math_reasoning | 83.3% | 63.5% | 47.0% | 34.3% | 24.4% | 17.2% | 11.8% | 3.820 |
| qa | 70.5% | 44.7% | 27.6% | 17.1% | 10.8% | 7.1% | 4.8% | 2.830 |
| question | 74.6% | 49.6% | 31.6% | 20.2% | 13.1% | 8.5% | 5.6% | 3.030 |
| rag | 73.6% | 48.4% | 29.8% | 18.4% | 11.3% | 6.9% | 4.1% | 2.930 |
| summarization | 68.0% | 39.0% | 21.0% | 10.8% | 5.4% | 2.6% | 1.2% | 2.480 |
| tool_call | 73.7% | 47.6% | 28.7% | 17.1% | 10.3% | 6.2% | 3.7% | 2.870 |
| translation | 73.8% | 47.7% | 28.7% | 17.3% | 10.4% | 6.5% | 4.1% | 2.890 |
| writing | 75.0% | 50.0% | 32.1% | 20.6% | 13.3% | 8.7% | 5.7% | 3.050 |
| Average | 74.9% | 49.9% | 31.9% | 20.4% | 13.1% | 8.5% | 5.5% | 3.044 |

Reasoning-heavy workloads accept best (`math_reasoning` 3.820, HumanEval 3.500); summarization is lowest at 2.480[^peagle]. Pretrained alternatives are available in the [Red Hat AI speculator-models collection](https://huggingface.co/collections/RedHatAI/speculator-models); the source recommends training a workload-specific speculator when the target or data distribution differs[^peagle].

## Relationships

- Uses [vLLM Speculators Library](vllm-speculators.md) — P-EAGLE training, evaluation, and deployment are the Speculators v0.6.0 parallel-drafting path in that library.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — P-EAGLE inherits the EAGLE-3 draft definition and replaces sequential autoregressive drafting with single-pass multi-token prediction depths.
- Related to [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — target hidden-state extraction supplies the P-EAGLE drafter inputs concatenated with token embeddings.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — both predict multiple future tokens per step; P-EAGLE uses a separate parallel draft model while MTP uses native prediction heads.

[^peagle]: Helen Zhao, Speeding up LLM inference with P-EAGLE in vLLM Speculators — `../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md` (Red Hat Developer, 2026-09-03), covering Amazon P-EAGLE parallel drafting, Speculators v0.6.0 `PEagleDraftModel` implementation, COD sampling, learnable mask token plus `mask_hidden` and unfrozen embeddings, flex-attention rules, four-step Qwen3-8B pipeline with layers 2/18/33 and training cost, `vllm serve` deployment, and Qwen3-8B acceptance table.
