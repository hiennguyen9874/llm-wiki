---
type: Concept
title: HyperQwen Qwen3.8-27B Serving Stack
description: vLLM-based stack serving Qwen3.8-27B on a single 24 GB GPU with single/batch modes, DFlash2/MTP speculation, and long-context options.
tags: [serving, vllm, qwen, speculative-decoding, quantization, long-context]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T12:00:00Z }
stale_after: 2027-04-05
sources:
  - id: hyperqwen-readme
    resource: ../raw/HyperQwen.md
    kind: documentation
    title: HyperQwen
---

HyperQwen is a `syv-ai/HyperQwen` patch-plus-pipeline stack around a pinned vLLM 0.30.0 that serves `Qwen/Qwen3.8-27B` on a single 24 GB consumer GPU with a 150k-token context and an OpenAI-compatible API, in a low-concurrency single-user mode and a high-concurrency batch mode; on one RTX 3090 at 250 W it reports 127 tok/s single-stream, ~1,035 tok/s aggregate decode at 64 concurrent, and 381 tok/s when the answer quotes its own prompt[^hyperqwen-readme]. All throughput figures below are **Reported** from this README capture alone under the stated card, power cap, engine pin, and workload shapes, with sampling, harness, and protocol detail living in linked docs that were not inspected here.

## Identity and distribution

- What it is: under the serving setup, a patch series against a pinned vLLM plus a model-preparation pipeline — requantized heads, a calibrated draft vocabulary, and speculation that drafts out of the prompt — rather than a standalone engine[^hyperqwen-readme].
- Today target: `Qwen3.8-27B` on one 24 GB GPU with vLLM, 150k context, OpenAI-compatible API with key auth, in two ready-made modes[^hyperqwen-readme].
- License Apache-2.0, same as the model; badges state vLLM 0.30.0, GHCR image, Docker and patch-integrity workflows[^hyperqwen-readme].
- First start pulls a 9.5 GB image and requantizes the model (~20 GB, once, into `./models`), then serves on `:18020`; one GPU runs one mode at a time[^hyperqwen-readme].
- Demo media (`docs/media/demo.avif`/`demo.mp4`, `bench/demo` method) shows one request against stock vLLM replayed from recorded token arrivals, then 64 at once; media and harness were not inspected[^hyperqwen-readme].

## Quick start and safety defaults

- Clone, copy env, pick a profile[^hyperqwen-readme]:

```bash
git clone https://github.com/syv-ai/HyperQwen && cd HyperQwen
cp .env.example .env
docker compose --profile single up -d
docker compose --profile batch up -d
```

- Auth boundary: in the container the server binds `0.0.0.0` with no auth unless a key is set; outside a container, no key means it binds `127.0.0.1` only — set `VLLM_API_KEY` before exposing[^hyperqwen-readme]:

```bash
echo "VLLM_API_KEY=$(openssl rand -hex 24)" >> .env
```

- Docker Desktop on WSL2 keeps `VLLM_WSL2_ENABLE_PIN_MEMORY=1`, or the V2 runner aborts with `RuntimeError: UVA is not available`[^hyperqwen-readme].
- Non-compose and no-Docker paths live in `docs/docker.md` and `docs/install.md`, which were not inspected[^hyperqwen-readme].

## Setup letters A–E

Three questions (who sends requests, longest prompt, whether answers quote the prompt) select one `.env` shape, starting from the shipped B setup[^hyperqwen-readme]:

| | change in `.env` | start with | what you get (**Reported**) |
|---|---|---|---|
| **A — batch** | nothing | `--profile batch` | ~1,035 tok/s aggregate at 64 concurrent |
| **B — single, default** | nothing | `--profile single` | 127 tok/s single stream, 64k context |
| **C — reproduction** | add `DFLASH_TOKENS=15` | `--profile single` | 381 tok/s while quoting, at 4 slots and 56k |
| **D — long context** | `SPEC=mtp` and `CTX=long` | `--profile single` | 150k context, ~95–100 tok/s |
| **E — huge context** | add `CTX=huge` | `--profile single` | 240k context, 67 tok/s mixed and 164 while quoting |

- B is the safe default; C only pays off when output repeats input, trading request slots and context for it[^hyperqwen-readme].
- D drops back to MTP on purpose because DFlash2 past 64k is worth it only for reproduction and loses ~2:1 to `SPEC=mtp CTX=long` on everything else; at E the KVarN cache buys the context instead, so DFlash2 stays on[^hyperqwen-readme].
- A needs no edit — batch ignores `SPEC` and says so on startup; every knob and cost lives in `single-user/README.md` and `batch/README.md`, not inspected[^hyperqwen-readme].

## Reported numbers behind the letters

| | batch | single |
|---|---|---|
| best for | API backends, pipelines, many concurrent | one or a few people chatting |
| 64 concurrent (128 in / 512 out) | **~1,035 tok/s** decode, 948 e2e — ~1,222 with every layer int8 | n/a — 8 slots |
| single stream (C1) | 46 tok/s | **127 tok/s** — 121 on the older MTP path |
| quoting its own prompt | 46 tok/s | **381 tok/s** at 25k context |
| prefill, 1k in | ~1,810 tok/s | ~1,440 — **~1,850–1,940** with `INT8_ACT=int8` |
| how | 16-bit recurrent state, int8 tensor-core GEMMs | 7 drafts proposed per pass, 15 tokens verified per step off the context |

- **Synthesis:** speculation wins below ~8 concurrent users and plain batching wins above — earlier on long sessions, where a speculating request reserves recurrent-state pages the pool has few of — per the cited measurement in `docs/long-context.md`, which was not inspected[^hyperqwen-readme].
- Full prefill matrix and per-step attribution live in `batch/README.md` and `docs/optimizations.md` (including the two speculative-decoding modes and the lookup drafter), not inspected[^hyperqwen-readme].
- **Evidence class:** **Reported** — card (RTX 3090 at 250 W), engine pin (vLLM 0.30.0), model, and workload shapes (C1 single-stream; 128-in/512-out at 64 concurrent; 1k prefill) are stated, but sampling, harness version, and repeat protocol are not in this file, so per the SCOPE benchmark rule these are not comparable benchmarks yet.

## What transfers: portable, model-specific, card-specific

- Portable already with nothing model- or card-specific in it: the vLLM patch series (`patches/`, one line each in `PATCHES.md`), the KVarN long-context backend, int8 Marlin GEMM layer selection, the SSE keep-alive, and the engine stall sentinel — described as vLLM fixes that happen to have been written here[^hyperqwen-readme].
- Model-specific work: the int8-QK prefill attention kernel is gated on this checkpoint's exact geometry (`num_heads == 24`, `num_kv_heads == 4`, `head_size == 256`) and falls back to FA2 for anything else, so a new model gets correctness without the prefill win until the gate is generalized; the 40k-token draft vocabulary is calibrated on this model's own output distribution; the DFlash2 drafter is a per-model checkpoint; `prepare/` assumes a head layout that only just learned heads in different shards (#120)[^hyperqwen-readme].
- Card-specific: Marlin tune tables measured on sm86; sm120 (RTX 5090) reproduces (#35); sm80 runs but has an open speculation fault at any k (#98, #72); multi-GPU works at TP=2 and TP=4 while TP=3 and PP=3 are invalid for this model's head count, stated as a checkpoint property rather than a missing feature[^hyperqwen-readme].
- Wanted next: smaller Qwen checkpoints for 16 GB and 12 GB cards, a larger one for 48 GB, and the EXL3 route (#103) as a second quantization path; prioritization is driven by who turns up with a reproduction[^hyperqwen-readme].

## Field-test protocol and most-wanted hardware

- About 30 minutes on one GPU, most of it unattended, through `compose exec` (venv installs drop the prefix)[^hyperqwen-readme]:

```bash
sudo nvidia-smi -pl 250
docker compose --profile single up -d
docker compose exec single bash bench/run_benchmarks.sh single
docker compose exec single bash bench/run_benchmarks.sh single
docker compose exec single venv/bin/hf download openai/gsm8k --repo-type dataset \
  --include "main/test-*" --local-dir bench/quality-data/gsm8k
docker compose exec single venv/bin/python bench/quality_battery.py mycard --gsm-only
```

- Discard the first benchmark run after a start (reads 30–50% low) and keep the second run's `ROW` lines as the report; pre-2026-09-21 images need `venv/bin/pip install pyarrow` first[^hyperqwen-readme].
- Field-report form asks for the six comparability fields — card, power cap, driver, OS or container, commit, and setup letter — without which a number cannot honestly sit next to the table rows; narrower runs or own-client runs are still posted but listed as independent reports rather than table rows, as in `docs/reproductions/`[^hyperqwen-readme].
- Most wanted, in order: sm90 (H100/H200, no datapoint at all); sm80 (A100/A30/CMP 170HX, third box would separate card from build on the #98/#72 fault); four Ampere cards (four sm120 measured in #105, but two 3090s give less aggregate than one in #135); 12 GB cards on the harness (two 3060s serve this model in #68 but with owners' own clients, so a harness run decides whether smaller Qwen checkpoints are worth preparing); vLLM 0.30.0 harness runs from any other card (0.29.0 covered in `docs/vllm-0.29.md`, pin in `docs/vllm-0.30.md`)[^hyperqwen-readme].
- What contributors get: the run published in `docs/reproductions/` with raw output and credit, platform gotchas written into `docs/gotchas.md`, and an honest account of what the hardware does badly; hardware/money offers go through an issue titled "compute offer" or Ko-fi GPU-time funding[^hyperqwen-readme].

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense family served here through a pinned-vLLM consumer-GPU stack rather than Unsloth GGUF/NVFP4 local inference.
- Uses [DFlash 2 Parallel Speculative Decoding](dflash2-parallel-speculative-decoding.md) — the per-model DFlash2 drafter and prompt-drafting path behind setups C and E, versus MTP in setup D.
- Related to [vLLM MTP Speculative Decoding](vllm-mtp-speculative-decoding.md) — the `SPEC=mtp` fallback used for 150k long-context serving.
- Related to [Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md) — the below-~8-concurrent speculation-wins versus above-~8 batching-wins crossover stated here.
- Related to [Narrow Single-Model Inference Engines](narrow-inference-engines.md) — HyperQwen as the vLLM batch/concurrency counterpart to single-model engines such as Strata and ninfer.
- Related to [KV Cache Compression and Optimization](kv-cache-compression-optimization.md) — the KVarN 4/2-bit KV backend behind the huge-context mode.
- Related to [vLLM Tensor and Pipeline Parallel Scaling](vllm-parallelism-scaling.md) — the TP=2/TP=4 allowed versus TP=3/PP=3 invalid shapes for this checkpoint.

## Coverage limits

- Only `../raw/HyperQwen.md` was inspected statically; no commands were executed.
- Linked entry points and attachments named in the source but absent from `raw/` were not inspected: `docs/media/demo.mp4`/`demo.avif`, `bench/demo`, `.env.example`, compose profiles, `docs/docker.md`, `docs/install.md`, `docs/clients.md`, `docs/multi-gpu.md`, `docs/third-party-checkpoints.md`, `single-user/README.md`, `batch/README.md`, `docs/optimizations.md`, `docs/benchmarks.md`, `docs/quality.md`, `docs/long-context.md`, `docs/reproductions/`, `docs/gotchas.md`, `PATCHES.md`, `patches/`, `docs/spec-decode-scratch-token-units.md`, `docs/vllm-0.29.md`, `docs/vllm-0.30.md`, `prepare/`, `drafter/`, `kvarn/`, the Hugging Face `Qwen3.8-27B` page, and issues #35/#68/#72/#98/#103/#105/#120/#135.
- Source revision, snapshot date, and publisher beyond `syv-ai/HyperQwen` badges are unstated in this capture; engine pin is read from the vLLM 0.30.0 badge.
- No sensitive values found; the `VLLM_API_KEY` line is a generation command, not a credential.

[^hyperqwen-readme]: HyperQwen — `../raw/HyperQwen.md` (README capture: header claim of Qwen3.8-27B on one 24 GB GPU with 150k context and keyed OpenAI API; "Today" RTX 3090 250 W figures; "Quick start" compose profiles, `:18020`, image/requant sizes, `0.0.0.0` vs `127.0.0.1` auth boundary, WSL2 pin-memory flag; "Which setup do I want?" flowchart plus A–E `.env` table; "The numbers behind that" batch-vs-single table with C1, 128-in/512-out, 25k-quote, 1k-prefill rows and sub-8-concurrent crossover; "Roadmap" portable/model-specific/card-specific transfer list with int8-QK gate, 40k draft vocab, Marlin sm86/sm120/sm80 notes, TP/PP shapes, and EXL3 item; "Field tests wanted" 30-minute harness, discard-first-run, GSM8K battery, six-field report, most-wanted table, and compute-offer/Ko-fi notes; "Documentation" map and Apache-2.0 license).
