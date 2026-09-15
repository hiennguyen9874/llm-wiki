---
type: Concept
title: vLLM P-EAGLE Speculative Decoding
description: Parallel EAGLE drafting that predicts K tokens per forward pass with vLLM parallel_drafting serving and Speculators training.
tags: [vllm, speculative-decoding, peagle, speculators, eagle]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T17:00:00Z }
sources:
  - id: peagle
    resource: ../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md
    title: Speeding up LLM inference with P-EAGLE in vLLM Speculators
  - id: peagle-vllm
    resource: ../raw/2026-03-13-p-eagle/index.md
    title: "P-EAGLE: Faster LLM inference with Parallel Speculative Decoding in vLLM"
---

P-EAGLE (Parallel EAGLE) extends EAGLE-3 with parallel drafting: at each position it predicts the next K tokens in one forward pass instead of autoregressively predicting token 1, feeding it back, then predicting token 2, reducing drafting latency and improving hardware utilization while preserving the verifier model's output distribution[^peagle].

## Relation to EAGLE-3

EAGLE-3's draft model is a small model — described as a single Llama 3 layer — that proposes tokens ahead for parallel target verification; rejected tokens discard the remainder of the speculative sequence[^peagle]. P-EAGLE keeps the same propose-then-verify guarantee but introduces prediction depths: the target verifies all K parallel predictions in one forward pass and accepts the correct prefix[^peagle].

The parallel strategy is particularly beneficial for long reasoning traces, where cumulative sequential-draft cost otherwise limits speculative-decoding speedup[^peagle].

In Speculators v0.6.0, `PEagleDraftModel` inherits from `Eagle3DraftModel` and remains compatible with the existing EAGLE-3 framework[^peagle].

## vLLM serving integration

P-EAGLE serving landed in vLLM starting from v0.16.0 via Unified Parallel Drafting PR#32887, with companion vLLM-Speculators RFC#292 / PR#343[^peagle-vllm].

Enable with a single flag in `SpeculativeConfig`[^peagle-vllm]:

```python
# vllm/config/speculative.py
parallel_drafting: bool = True
```

```bash
vllm serve openai/gpt-oss-20b \
 --speculative-config '{"method": "eagle3", "model": "amazon/gpt-oss-20b-p-eagle", "num_speculative_tokens": 5, "parallel_drafting": true}'
```

This `method: eagle3` plus `parallel_drafting: true` shape is distinct from the PARD path, which uses `method: draft_model` plus `parallel_drafting` — see [vLLM Parallel Draft Model Speculative Decoding](vllm-parallel-draft-model.md).

Pre-trained parallel-capable heads are published on Hugging Face as `amazon/gpt-oss-120b-p-eagle`, `amazon/GPT-OSS-20B-P-EAGLE`, and `amazon/Qwen3-Coder-30B-A3B-Instruct-P-EAGLE`[^peagle-vllm].

> Version note: serving GPT-OSS-20B with EAGLE drafters currently requires a one-line vLLM patch (PR#36684); the source expects it to land in an upcoming vLLM release[^peagle-vllm].

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

The vLLM post shows the same two-step architecture: Step 1 prefilling is identical to autoregressive EAGLE and captures `h_prompt` per prompt position plus `h_context` for the newly generated token; Step 2 constructs parallel inputs where prompt positions pair `emb(p)` with `h_prompt` shifted by one, position 1 (NTP) pairs `emb(new)` with `h_context` exactly as in EAGLE, and positions 2–K (MTP) fill missing inputs with shared learnable `emb(mask)` plus `h_shared`, then pass together through N transformer layers and the LM head to emit `t1`–`t4` in one forward pass[^peagle-vllm]. Architecture figure inspected at `../raw/2026-03-13-p-eagle/assets/fig2_architecture.png` confirms this NTP plus MTP input construction and `2d` concatenated layout.

### Long-sequence training memory

Reasoning models need long-context draft training: GPT-OSS 120B produces median 3,891 and P90 10,800 tokens (prompt plus generation) on UltraChat at Medium reasoning, so draft models must train on matching lengths[^peagle-vllm]. Sequence-length histogram inspected at `../raw/2026-03-13-p-eagle/assets/fig3_sequence_length.png` shows the long tail with 4K and 8K cutoffs.

Parallel drafting amplifies training memory: K parallel groups on length-N sequences create N × K positions, so N=8,192 and K=8 gives 65,536 positions and 65K × 65K attention over 4B elements costing 8GB in bf16[^peagle-vllm]. Position sampling reduces memory but degrades draft quality when too aggressive, while gradient accumulation splits across different examples and cannot help when a single sequence exceeds memory[^peagle-vllm]. P-EAGLE introduces a sequence-partition algorithm for intra-sequence splitting into contiguous chunks that preserves cross-chunk attention dependencies and accumulates gradients across chunks of the same sequence; the source defers details to the P-EAGLE paper (arXiv 2602.01469)[^peagle-vllm].

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

## vLLM implementation

Parallel drafting breaks the usual draft/verify token-layout consistency: predicting K tokens in one pass appends MASK placeholders (for example `[token, MASK, MASK, …]`) that exist only for drafting, so the draft batch shape no longer matches verification and batch metadata must be rebuilt by expanding input IDs, hidden states, and positions and recomputing slot mapping plus per-request start indices[^peagle-vllm].

A fused Triton kernel keeps this setup cheap by populating the drafter input batch on-GPU in one pass: it copies previous token IDs and positions, inserts the per-request bonus token sampled by the target, fills extra parallel slots with a MASK token ID, and emits a rejected-token mask, masked-token mask, new-token sampling indices, and hidden-state mapping[^peagle-vllm]. Fusing avoids many separate copy/scatter plus insert plus fill plus mask plus remap ops and their launch overhead and memory traffic[^peagle-vllm].

Hidden states are handled separately because they are much larger: the Triton kernel outputs a mapping and a dedicated copy kernel broadcasts the learned placeholder into mask slots[^peagle-vllm]:

```python
# Copy target hidden states to their new positions
self.hidden_states[out_hidden_state_mapping] = target_hidden_states
# Fill masked positions with the learned Parallel Drafting hidden state
mask = self.is_masked_token_mask[:total_num_output_tokens]
torch.where(
    mask.unsqueeze(1),
    self.parallel_drafting_hidden_state_tensor,
    self.hidden_states[:total_num_output_tokens],
    out=self.hidden_states[:total_num_output_tokens],
)
```

The placeholder tensor is loaded from the model's `mask_hidden` buffer[^peagle-vllm]. For KV cache, valid tokens get normal slot assignment while rejected tokens map to `PADDING_SLOT_ID` (-1) to prevent spurious writes; for CUDA graphs the capture range is extended by K × max_num_seqs to fit the larger draft batch[^peagle-vllm].

## Serving benchmarks

The vLLM post trains a lightweight 4-layer P-EAGLE drafter for GPT-OSS-20B predicting up to 10 tokens in parallel and sweeps speculation depths K ∈ {3,5,7} across concurrency C ∈ {1,2,4,8,16,32,64} with linear drafting, selecting per-method peak TPS at each serving condition[^peagle-vllm]. Baseline is the public vanilla EAGLE-3 checkpoint `RedHatAI/gpt-oss-20b-speculator.eagle3`; benchmarks are MT-Bench (multi-turn instruction), SPEED-Bench Code (long code generation), and HumanEval (function synthesis), all on one NVIDIA B200[^peagle-vllm].

Headline: 55–69% higher throughput at low concurrency (c=1) and 5–25% sustained at high concurrency (c=64) versus vanilla EAGLE-3, up to 1.69× overall[^peagle-vllm]. Figure 1 inspected at `../raw/2026-03-13-p-eagle/assets/fig1_speedbench_overview.png` shows SPEED-BENCH concurrency-1 absolute TPS of 456 baseline, 507 vanilla EAGLE-3 best config, and 858 P-EAGLE best config. Concurrency sweeps inspected at `fig4_mtbench.png`, `fig5_humaneval.png`, and `fig6_speedbench.png` show Best P-EAGLE above Best EAGLE-3 and baseline at every concurrency level.

P/E speedup ratios (best P-EAGLE vs best EAGLE-3)[^peagle-vllm]:

| Concurrency | MT-Bench | HumanEval | SPEED-Bench |
| --- | --- | --- | --- |
| 1 | 1.55× | 1.55× | 1.69× |
| 2 | 1.29× | 1.53× | 1.61× |
| 4 | 1.35× | 1.45× | 1.54× |
| 8 | 1.28× | 1.35× | 1.45× |
| 16 | 1.27× | 1.31× | 1.40× |
| 32 | 1.09× | 1.37× | 1.22× |
| 64 | 1.05× | 1.23× | 1.25× |

A consistent tuning pattern emerges: P-EAGLE peaks at K=7 across all concurrency levels while vanilla EAGLE-3 peaks at K=3, because parallel single-pass drafting adds no sequential overhead for deeper speculation while autoregressive drafting does[^peagle-vllm].

Gains come from lower drafting overhead plus higher acceptance length (AL), the mean accepted draft tokens per speculation round[^peagle-vllm]:

| Config | HumanEval | SPEED-Bench | MT-Bench |
| --- | --- | --- | --- |
| P-EAGLE K=3 | 3.02 | 2.87 | 2.87 |
| P-EAGLE K=7 | 3.94 | 3.38 | 3.70 |
| EAGLE-3 K=3 | 2.65 | 2.24 | 2.70 |
| EAGLE-3 K=7 | 3.03 | 2.59 | 3.27 |

At K=7 P-EAGLE beats EAGLE-3 by 30% on HumanEval (3.94 vs 3.03), 31% on SPEED-Bench (3.38 vs 2.59), and 13% on MT-Bench (3.70 vs 3.27); from K=3 to K=7 P-EAGLE AL rises 0.92 on HumanEval versus 0.38 for EAGLE-3[^peagle-vllm].

> Serving config used for these numbers: `--max-num-seqs 1024`, `--max-model-len 100000`, `--max-num-batched-tokens 100000`, `--max-cudagraph-capture-size 4096`, `--no-enable-prefix-caching`, `--no-enable-chunked-prefill`, `--kv-cache-dtype fp8`, `--async-scheduling`, `--stream-interval 20` with `VLLM_USE_FLASHINFER_MOE_MXFP4_MXFP8=1`[^peagle-vllm]. Reproduction uses `vllm bench serve` with 80 MT-Bench prompts and 164 HumanEval prompts in the source examples[^peagle-vllm].

## Relationships

- Uses [vLLM Speculators Library](vllm-speculators.md) — P-EAGLE training, evaluation, and deployment are the Speculators v0.6.0 parallel-drafting path in that library.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — P-EAGLE inherits the EAGLE-3 draft definition and replaces sequential autoregressive drafting with single-pass multi-token prediction depths.
- Related to [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — target hidden-state extraction supplies the P-EAGLE drafter inputs concatenated with token embeddings.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — both predict multiple future tokens per step; P-EAGLE uses a separate parallel draft model while MTP uses native prediction heads.
- Related to [vLLM Parallel Draft Model Speculative Decoding](vllm-parallel-draft-model.md) — alternative parallel-drafting path using a PARD proposer with `method: draft_model`, contrasted with P-EAGLE's `method: eagle3` plus `parallel_drafting` serving shape.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — P-EAGLE's K=7 peak versus EAGLE-3's K=3 peak is concrete evidence for tuning draft depth by drafter cost model rather than using one static K.

[^peagle]: Helen Zhao, Speeding up LLM inference with P-EAGLE in vLLM Speculators — `../raw/speeding-llm-inference-p-eagle-vllm-speculators/index.md` (Red Hat Developer, 2026-09-03), covering Amazon P-EAGLE parallel drafting, Speculators v0.6.0 `PEagleDraftModel` implementation, COD sampling, learnable mask token plus `mask_hidden` and unfrozen embeddings, flex-attention rules, four-step Qwen3-8B pipeline with layers 2/18/33 and training cost, `vllm serve` deployment, and Qwen3-8B acceptance table.

[^peagle-vllm]: Amazon plus NVIDIA teams, P-EAGLE: Faster LLM inference with Parallel Speculative Decoding in vLLM — `../raw/2026-03-13-p-eagle/index.md` (vLLM Blog, 2026-03-13), covering single-pass K-token drafting, NTP plus MTP input construction with shared mask embedding and hidden state, long-sequence partition training, v0.16.0 PR#32887 serving with `parallel_drafting` flag and Triton plus hidden-state plus KV/CUDA-graph implementation, Amazon pre-trained heads, GPT-OSS-20B B200 throughput ratios and acceptance-length tables, and PR#36684 patch note.
