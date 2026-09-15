---
type: Concept
title: vLLM FastMTP Fine-Tuning
description: FastMTP-style recursive fine-tuning of a single native MTP head in Speculators 0.6.0 to restore multi-step acceptance for vLLM speculative decoding.
tags: [vllm, speculative-decoding, mtp, speculators, fine-tuning]
status: stable
created: 2026-09-15
generated: { by: llm-wiki-agent/1, at: 2026-09-15T12:00:00Z }
sources:
  - id: fastmtp
    resource: ../raw/optimize-vllm-speculative-decoding-fastmtp-heads/index.md
    title: Optimize vLLM speculative decoding with FastMTP heads
---

Speculators 0.6.0 adapts one shipped native MTP head for the recursive multi-step drafting vLLM performs in production, using teacher-forced recursive training with exponential-decay position weighting to counteract the train/serve mismatch of reusing a single-step head autoregressively[^fastmtp].

## Background: MTP as training objective

Autoregressive decoding is memory-bandwidth bound because every token costs one full forward pass over billions of parameters, so hardware time goes to moving weights rather than computing[^fastmtp].

Multi-token prediction (MTP) is a training objective, not a serving mode: the model learns to predict several future tokens at each position, which sharpens representations and improves data efficiency[^fastmtp]. The DeepSeek-V3 variant adds *D* sequential MTP modules, one per additional future token, chained causally so each module conditions on the previous module's output rather than predicting positions in parallel[^fastmtp].

The module at depth *k* takes the hidden state from depth *k-1* plus the embedding of ground-truth token *t_{i+k}* and predicts *t_{i+k+1}*; each module has its own transformer block and input projection but shares the embedding layer and output head with the main model[^fastmtp]. Consequences called out in the source[^fastmtp]:

- Every MTP module trains on ground-truth context (teacher forcing).
- Engines can repurpose the modules at inference as a ready-made draft head with no added parameters.

Most open-weight models do not ship these modules; the source names DeepSeek-V3 and the Qwen3-Next family as exceptions[^fastmtp].

## Train/serve mismatch

In training, DeepSeek-V3 uses *D* distinct modules, each responsible for one specific future position[^fastmtp]. In production, providers rarely ship the full stack, and even when several modules ship, engines typically keep only the first to avoid memory overhead; to speculate multiple tokens the engine applies that single module autoregressively, feeding its drafted token and output hidden state back in for the next step[^fastmtp].

The shipped module was trained to predict the immediate next token from ground-truth input, never to consume its own outputs, so small errors compound and acceptance drops for the second and third speculative tokens[^fastmtp]. FastMTP-style fine-tuning trains that single module the way the server uses it: recursively[^fastmtp]. The recipe follows Cai et al., FastMTP (2025)[^fastmtp].

## How Speculators implements it

The Speculators MTP speculator (`MTPDraftModel`) is a single transformer layer with an input projection fusing the verifier's last hidden state with the target token's embedding[^fastmtp]. Training runs a teacher-forced recursive loop mirroring serving; at step *k*[^fastmtp]:

1. Fuse the token embedding for `input_ids[t+k+1]` with the current hidden state.
2. Run the MTP layer to produce an output hidden state; `lm_head` produces logits.
3. Score against loss target `input_ids[t+k+2]`.
4. Feed the output hidden state back as input for step *k+1*.

Per-step losses use normalized exponential decay[^fastmtp]:

```python
def compute_step_weights(beta: float = 0.6, num_steps: int = 3) -> list[float]:
    """alpha_k = beta^(k-1) / sum(beta^(j-1) for j=1..K)"""
    raw = [beta**k for k in range(num_steps)]
    total = sum(raw)
    return [w / total for w in raw]
# beta=0.6, num_steps=3 -> [0.51, 0.31, 0.18]
```

Default β = 0.6 over 3 steps gives step 0 roughly half the loss, because verifiers accept early speculative tokens more often[^fastmtp].

Implementation properties[^fastmtp]:

- **Native weight extraction:** `MTPConverter` lifts native `mtp.*` weights directly from the verifier checkpoint; no training from scratch.
- **Full-vocabulary draft head:** shares the verifier's `embed_tokens` and complete `lm_head`, so there is no vocabulary reduction and no separate output projection to reconcile; the draft stays numerically identical to the target output distribution.
- **vLLM-ready stitching:** the stitcher emits weights in the exact `mtp.*` key format vLLM expects, deploying with a standard `vllm serve`.

Planned FR-Spec-style frequency-ranked vocabulary reduction would shrink recursive step costs but is future work in the source[^fastmtp].

## When to use it

1. **Verifier already ships an MTP head.** Fine-tuning starts from native `mtp.*` weights; 0.6.0 supports Qwen3-Next and Qwen3.5 including MoE[^fastmtp]. Without an MTP head, the source directs to EAGLE-3, DFlash, or P-EAGLE instead.
2. **Limited training budget.** MTP is the lightest speculator to train because it reads only the last layer's hidden states, giving smaller offline datasets and faster online training via vLLM's hidden-state extraction[^fastmtp].
3. **Specialized workload.** Shipped heads train on general data; fine-tuning on domain data (math, code) sharpens predictions where they matter[^fastmtp].

## Fine-tune, stitch, and serve workflow

Example fine-tunes Qwen/Qwen3.5-9B on GSM8K in about 443 seconds on 2× NVIDIA H200; training data must be generated by the target model itself[^fastmtp].

Prepare self-generated data[^fastmtp]:

```bash
python scripts/prepare_data.py \
  --model Qwen/Qwen3.5-9B \
  --data ./output/dataset/gsm8k.jsonl \
  --max-samples 5000 --seq-length 8192 --output ./output
```

Serve the verifier for online hidden-state generation[^fastmtp]:

```bash
python scripts/launch_vllm.py Qwen/Qwen3.5-9B --target-layer-ids 32 -- --port 8000
```

Fine-tune the extracted native head recursively[^fastmtp]:

```bash
python scripts/train.py \
  --verifier-name-or-path Qwen/Qwen3.5-9B \
  --data-path ./output \
  --vllm-endpoint http://localhost:8000/v1 \
  --save-path ./output/checkpoints \
  --speculator-type mtp \
  --num-speculative-steps 3 \
  --target-layer-ids 32 \
  --step-weight-beta 0.6 \
  --epochs 3 --lr 1e-4 --total-seq-len 8192 \
  --on-missing generate --on-generate delete
```

Stitch back into the verifier checkpoint and serve[^fastmtp]:

```bash
vllm serve ./output/stitched \
  --speculative-config '{"method":"mtp","num_speculative_tokens":3}' \
  --no-enable-chunked-prefill
```

Install via `uv pip install speculators==0.6.0` or from source, with a ready example at `examples/train/mtp_qwen3_5_9b_gsm8k_online.sh`[^fastmtp].

## Reported performance

Mean accepted length via GuideLLM is the metric; higher means more tokens per forward pass[^fastmtp]. Source-reported results for Qwen/Qwen3-Next-80B-A3B-Instruct trained on ~8,000 GSM8K samples and evaluated on the test split[^fastmtp]:

| Position | Base | Fine-tuned |
| --- | --- | --- |
| pos 0 | 0.897 | 0.912 |
| pos 1 | 0.719 | 0.776 |
| pos 2 | 0.476 | 0.616 |

Gains concentrate at later positions, consistent with fixing recursive error compounding; the source notes longer training might improve further[^fastmtp]. Median inter-token latency versus requests per second (GuideLLM 0.16.0, vLLM 0.24.0) shows consistently lower latency after fine-tuning, up to ~1.25× speedup[^fastmtp].

All figures are source-reported single-setup numbers, not independently verified. Future work named is FR-Spec-style draft-vocabulary reduction, verifier families beyond Qwen3-Next/Qwen3.5, and FastMTP benchmarking across DeepSeek-V3 and Llama 3 families[^fastmtp].

## Relationships

- Uses [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — fine-tuned heads deploy through the native `method: mtp` path with no separate draft model.
- Uses [vLLM Speculators Library](vllm-speculators.md) — `MTPConverter`, `MTPDraftModel`, online hidden-state generation, and stitching are the 0.6.0 MTP implementation of that library.
- Uses [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — MTP training reads last-layer hidden states, including online via a live vLLM server.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — domain-aligned fine-tuning is the remedy that guide prescribes for collapsed acceptance.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — EAGLE-3 is the named fallback when the verifier ships no MTP head.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — DFlash is another named fallback for non-MTP verifiers.

## Coverage limits

- `assets/image1_288.png.webp` was inspected to confirm it plots median ITL versus RPS for base versus fine-tuned with a speedup color scale; numeric claims rest on the article prose and table, not independent chart digitization.
- The Cai et al. FastMTP paper, Gloeckle et al. MTP paper, DeepSeek-V3 report, and linked Speculators docs, example script, and companion Red Hat articles were not inspected beyond the source's description.

[^fastmtp]: Rahul Tuli, Optimize vLLM speculative decoding with FastMTP heads — `../raw/optimize-vllm-speculative-decoding-fastmtp-heads/index.md` (Red Hat Developer, 2026-09-08), covering memory-bandwidth-bound autoregressive decoding, MTP objective and sequential causal-chain modules, single-head recursive reuse and acceptance drop, Speculators 0.6.0 FastMTP loop with β=0.6 weighting, MTPConverter full-vocabulary shared-head design and mtp.* stitching, Qwen3-Next/Qwen3.5 support and EAGLE-3/DFlash/P-EAGLE fallback, last-layer-only training economy, GSM8K fine-tune/serve commands, per-position acceptance table and up-to-1.25× ITL speedup, and FR-Spec plus broader-family future work.
