---
type: Concept
title: vLLM Speculators DFlash Training (v0.5.0)
description: DFlash block-diffusion training and unified online/offline hidden-state training in Speculators v0.5.0 with Gemma 4 evidence and vLLM serving.
tags: [vllm, speculative-decoding, speculators, dflash, training]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T00:00:00Z }
sources:
  - id: spec050
    resource: ../raw/speculators-v050-dflash-support-and-online-training/index.md
    title: 'Speculators v0.5.0: DFlash support and online training'
---

Speculators v0.5.0 adds DFlash block-diffusion training alongside Eagle 3 and unifies online and offline training on vLLM's native hidden-states extraction, removing the prior custom pipeline and direct vLLM Python dependency[^spec050].

## DFlash versus Eagle 3

Eagle 3 generates drafts autoregressively over multiple forward passes, while DFlash uses block diffusion to generate a length-B token block in a single forward pass[^spec050].

The block structure is implemented with the attention mask, and DFlash uses a noncausal pattern where queries within a block attend to all other tokens in the same block[^spec050]. The single-pass design reduces speculative-decoding overhead for longer draft sequences[^spec050].

## Scalable training with anchors

Training predicts multiple blocks in parallel, but starting a block after every sequence position makes the attention mask impractically large in memory and compute[^spec050].

Instead v0.5.0 randomly selects a smaller set of anchor positions from locations that contribute to the training loss and attaches predicted blocks only to those anchors[^spec050]. This keeps the predicted-block count fixed regardless of sequence length, allowing longer contexts with a manageable mask[^spec050].

## Training command

DFlash follows the same online workflow as Eagle 3, with speculator-specific flags[^spec050]:

```bash
torchrun --standalone --nproc_per_node 2 scripts/train.py \
    --verifier-name-or-path "Qwen/Qwen3-8B" \
    --vllm-endpoint "http://localhost:8000/v1" \
    --speculator-type dflash \
    --draft-vocab-size 8192 \
    --block-size 8 \
    --max-anchors 3072 \
    --num-layers 5 \
    --target-layer-ids "2 18 33" \
    --epochs 5 --lr 1e-4
```

DFlash-specific parameters are `--speculator-type dflash`, `--block-size` tokens per diffusion block, and `--max-anchors` anchor points for speculation during training[^spec050]. The example uses 5 draft layers on Qwen3-8B target layers 2, 18, and 33[^spec050].

## Gemma 4 31B evidence

The release trained `RedHatAI/gemma-4-31B-it-speculator.dflash` and reports per-position acceptance and average length, strongest on reasoning and code[^spec050]:

| Dataset | Pos 0 | Pos 1 | Pos 2 | Pos 3 | Pos 4 | Pos 5 | Pos 6 | Pos 7 | Avg. Length |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HumanEval | 85.8% | 72.1% | 60.3% | 50.4% | 41.8% | 34.3% | 26.9% | 19.6% | 4.91 |
| math_reasoning | 88.7% | 76.1% | 64.8% | 54.9% | 45.5% | 36.5% | 28.8% | 21.5% | 5.17 |
| qa | 67.5% | 41% | 23.8% | 13.8% | 8.1% | 4.5% | 2.6% | 1.3% | 2.63 |
| question | 75.1% | 51.1% | 34.7% | 24.5% | 17.9% | 13% | 9.4% | 6.5% | 3.32 |
| rag | 76.1% | 54.8% | 39.8% | 28.7% | 19.9% | 12.9% | 7% | 3.8% | 3.43 |
| summarization | 67.3% | 39.9% | 22.3% | 12% | 6.4% | 3.1% | 1.5% | 0.7% | 2.53 |
| tool_call | 65.7% | 45.7% | 31.6% | 21.7% | 15% | 9.6% | 6.2% | 3.6% | 2.99 |
| translation | 73.4% | 51.4% | 35.3% | 23.6% | 15.6% | 9.3% | 5.4% | 2.6% | 3.17 |
| writing | 75.3% | 51.6% | 35.1% | 24.5% | 17.8% | 13% | 9.4% | 6.5% | 3.33 |

Gemma 4 DFlash reports better median intertoken latency than both Eagle 3 and a standalone FP8 verifier, with DFlash plus FP8 verifier best; the math-reasoning median-ITL versus requests-per-second chart orders worst to best as No Spec FP16, FP8_Block, Eagle 3, DFlash, then DFlash+FP8_Block[^spec050].

> Coverage note: chart values were inspected from `assets/figure2_32.png.webp`; quantitative claims above rest on source prose and table, with chart ordering as visual confirmation.

## Serving in vLLM

DFlash integrates with vLLM speculative decoding as of PR [#38300](https://github.com/vllm-project/vllm/pull/38300), included in `vllm>=0.20.0`[^spec050].

Like Eagle 3 models, DFlash artifacts carry `speculators_config` in `config.json`, enabling basic serving[^spec050]:

```bash
vllm serve -tp 2 RedHatAI/gemma-4-31B-it-speculator.dflash
```

## Unified online and offline training

Both modes now use vLLM's native hidden-states extraction introduced in vLLM v0.18.0[^spec050]:

- Online: extract hidden states on the fly during training.
- Offline: pregenerate and cache hidden states to disk, then train.

Prior Speculators extracted hidden states with lower-level vLLM utilities requiring vLLM as a direct Python dependency, tightly coupling training to frequently changing internal APIs and requiring manual upstream synchronization[^spec050]. The native path removes the custom data-generation pipeline and direct dependency; training talks to a running vLLM server over its standard REST API and inherits vLLM memory management, batching, and hardware acceleration, improving version stability and independent upgrades[^spec050].

Online sequence[^spec050]:

1. vLLM server initializes with the base model and special configuration.
2. Training prompts are sent for inference.
3. Hidden states are extracted and temporarily written to disk or RAM disk.
4. Training loads then deletes the file.
5. The speculator trains on the extracted states.

Offline generation uses the same extraction system and data format, with scripts that saturate the running server and write to disk[^spec050]. The modes compose: partially generate offline then train while filling missing states, or run online without clearing files so the first epoch generates and later epochs reload[^spec050].

## Documentation

The release points to updated Speculators docs with algorithm introductions, training tutorials, a guide for adding new speculative algorithms, and an API reference[^spec050].

## Relationships

- Related to [vLLM Speculators Library](vllm-speculators.md) — v0.5.0 DFlash plus unified-training release within that library.
- Related to [DFlash Block Diffusion Speculative Decoding](dflash-block-diffusion.md) — paper method behind this training and Gemma 4 serving evidence.
- Uses [vLLM Hidden State Extraction](vllm-hidden-state-extraction.md) — native `extract_hidden_states` plus KV-connector path that both online and offline modes now share.
- Related to [vLLM Speculators Eagle3 Training (v0.3.0)](vllm-speculators-eagle3-training.md) — earlier offline patched-worker Eagle3 path superseded by this unified native path.
- Related to [vLLM EAGLE Speculative Decoding](vllm-eagle-speculative-decoding.md) — autoregressive Eagle 3 baseline versus single-pass DFlash; both serve via bundled `speculators_config`.
- Related to [SGLang DFlash Speculative Decoding](sglang-dflash-speculative-decoding.md) — SGLang Spec V2 serving alternative for DFlash drafters.

[^spec050]: Helen Zhao, Speculators v0.5.0: DFlash support and online training — `../raw/speculators-v050-dflash-support-and-online-training/index.md` (Red Hat Developer, 2026-06-04), covering single-pass block diffusion versus autoregressive Eagle 3, noncausal intra-block attention, anchor-sampled parallel-block training, DFlash `train.py` flags and Qwen3-8B example, Gemma 4 31B per-position and average-length table plus median-ITL versus Eagle 3/FP8 figure, PR #38300 / `vllm>=0.20.0` `speculators_config` serving, native hidden-states online/offline unification with REST decoupling and hybrid reuse, and docs plus repository pointers; `assets/figure2_32.png.webp` inspected for curve ordering.
