---
type: Concept
title: Strata MTP and Prompt-Lookup Speculation
description: Strata's lossless speculation for Qwen3.8-Flash-Next — the model's MTP layer drafting up to 3 tokens with a restricted draft vocabulary, plus cost-gated prompt lookup up to 5 tokens — and its acceptance, language, and penalty effects.
tags: [strata, speculative-decoding, mtp, prompt-lookup, ngram, draft-vocabulary, qwen3.8-flash-next, local-inference]
status: stable
created: 2026-10-04
generated: { by: llm-wiki-agent/1, at: 2026-10-04T17:00:00Z }
stale_after: 2027-04-04
sources:
  - id: strata-docs
    resource: ../raw/Strata/README.md
    scope: ../raw/Strata/
    kind: documentation
    title: Strata repository documentation (README, HOW_IT_WORKS, MODELS, DETAILS; engine up to 0.1.39b)
  - id: strata-thread-5090
    resource: ../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md
    scope: ../raw/strata-on-a-power-limited-5090-and-96gb-of/
    kind: discussion
    title: "Strata on a power limited 5090 and 96GB of DDR5-6400 (r/LocalLLaMA)"
  - id: strata-video-6x
    resource: ../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md
    kind: video
    title: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata) (YouTube transcript)"
---

Strata speeds up decoding of Qwen3.8-Flash-Next by 1.6–1.8× with draft-then-verify speculation: the model's own MTP layer drafts up to 3 tokens and one pass over all 48 layers verifies them, averaging 2.4–3.2 tokens per pass, so output matches non-speculative decoding (**Reported**)[^strata-docs]. Speculation matters more on a [tiered offload engine](strata-tiered-moe-offload.md) because each verify pass amortizes CPU expert compute and PCIe traffic over several tokens (**Synthesis**). Background theory is in [Speculative Decoding Foundations](speculative-decoding-foundations.md).

## Draft sources

- **MTP layer:** the checkpoint's built-in multi-token-prediction head, held on the GPU; drafts up to 3 tokens; `--spec-min-p` sets how confident it must be to add another guess, tunable via `--calibrate`[^strata-docs].
- Corroborating instance from a video explainer (**Reported**)[^strata-video-6x]: the same machine wrote 47–57 tok/s without the trick versus 82–92 tok/s with it; deliberately forced wrong guesses verified the output comes out token-for-token identical without MTP; on builds whose name starts with IQ, GPU-vs-CPU rounding can still diverge to a different (stated equally good) answer, with the same token chosen at 97.5–99% of positions against llama.cpp on the same 4-bit file — consistent with the UD-Q4_K_XL agreement figures in [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md).
- **Prompt lookup (0.1.7):** when the reply repeats context (code edits, quoted text), drafts up to 5 tokens from the earlier copy, enabled only where measured acceptance and cost say it pays; code edits 6–11% faster, other text unchanged (**Reported**)[^strata-docs]. Compare [vLLM N-gram Speculative Decoding](vllm-ngram-speculative-decoding.md) and [vLLM Suffix Speculative Decoding](vllm-suffix-speculative-decoding.md).
- Short answers run below long-output speed because the first rounds have no draft yet[^strata-docs].
- Reported MTP on/off shape (4070 Ti Super + 64 GB DDR4, Linux, IQ3, **Reported**): ~60 tok/s on characters the MTP head did not predict before a fix, versus ~80 tok/s story and up to ~120 tok/s code with MTP working (average ~90); one deployment snapshot in the same thread pairs MTP drafts up to 3 tokens with prompt lookup on[^strata-thread-5090].

## Draft vocabulary (`--draft-vocab`)

The MTP draft head proposes only from a vocabulary subset (`mtp/rt/draft_vocab.bin`), trading VRAM and English speed against non-English acceptance[^strata-docs]:

| Subset | Ids | Effect (Reported) |
| --- | ---: | --- |
| default since 0.1.27 (English/code + all CJK) | 106,299 | CJK answers 15–38% faster (Q2_0, RTX 5070); head ~180 MiB VRAM[^strata-docs] |
| `en` | 40,525 | ~110 MiB less VRAM, English 1–2% faster, CJK gets almost no drafts; suggested on cards <14 GB[^strata-docs] |
| `cyrillic` | 58,963 | Ukrainian/Russian 1.4 → 2.1 tokens per round, 83 → 109 tok/s (RTX 5090, NVFP4 fork)[^strata-docs] |
| `fr` (0.1.39, #597) | 46,211 | French out-of-subset tokens 23.6% → 0.7%; acceptance 0.51 → 0.60 (IQ3_XXS, RTX 5070, 8 prompts × 2), English and code unchanged; 141 → 158 tok/s on RTX 5090 IQ3_S (reporter)[^strata-docs] |

- `tools/draft_vocab.py --corpus` builds subsets; on a 12 GB card with long context the start can fail with "the draft head does not fit", and the engine names a smaller subset that fits (#474)[^strata-docs].
- **Synthesis:** acceptance depends on the language mix, so draft-vocab coverage is a workload-fit knob analogous to choosing a speculator trained on matching data ([Speculative Decoding Workload Fit and Tuning](speculative-decoding-practice-guide.md)).

## Interactions

- **Penalties:** since 0.1.19 presence/frequency/repetition penalties apply to every verified token as in sequential decoding; because drafts are unpenalized, more are rejected and penalized requests are 1–11% slower (**Reported**)[^strata-docs].
- **Determinism:** verify-window grouping changes CPU kernel choice and rounding, so drafts can alter greedy output unless `STRATA_IQ_MT_MIN=1` (#152)[^strata-docs].
- **Metrics:** `/metrics` reports per-request `drafts_offered` / `drafts_accepted` and totals (#457)[^strata-docs]; compare [vLLM Per-Request Speculative Decoding Acceptance Metrics](vllm-per-request-spec-decode-metrics.md).

## llama.cpp convergence (video-reported, October 2026)

- On October 1st llama.cpp merged multi-token prediction for this exact model: on a full-VRAM machine decoding rose 28 → 44 tok/s (~1.55x), but on spill-to-RAM machines (most viewers) the feature initially slowed things down, because each extra guess pulls its own experts from RAM — Strata's 1.6–1.8x holds specifically because its expert cache absorbs that cost (**Reported**)[^strata-video-6x].
- The expert cache itself is an open llama.cpp draft PR (since August 28th), measured 18.4 → 24.2 tok/s on the PR author's hardware (transcript says "2390s"); Strata is stated to be built partly from llama.cpp code, so the gap is two features — one landed, one pending — framed as a lead being chased in public rather than a replacement (**Reported**)[^strata-video-6x].

## Relationships

- Uses [Qwen3.8-Flash-Next Architecture and Evaluation](qwen3.8-flash-next-architecture.md) — the MTP head that Strata uses as its drafter.
- Related to [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — the llama.cpp MTP path for local MTP drafting.
- Related to [SGLang Qwen3.8-Flash-Next Inference](sglang-qwen3.8-flash-next-inference.md) — datacenter MTP for the same model.
- Related to [Strata Qwen3.8-Flash-Next Quants and Measured Speed](strata-qwen3.8-flash-next-quants-performance.md) — output tables measured with this speculation on.

## Coverage limits

- Acceptance figures come from small project or reporter runs; per-workload acceptance distributions and the paper's analysis (`Strata-Paper.pdf`) were not available. A video explainer cites "Strata's paper" for the lossless and 1.6–1.8x claims secondhand; the paper itself was not inspected[^strata-video-6x].

[^strata-thread-5090]: r/LocalLLaMA thread "Strata on a power limited 5090 and 96GB of DDR5-6400" — `../raw/strata-on-a-power-limited-5090-and-96gb-of/index.md` (comments 2026-10-02–2026-10-04): MTP-missing vs MTP-working decode band and an MTP-≤3 plus prompt-lookup deployment snapshot.

[^strata-video-6x]: "The New Way to Run 125B Models 6x Faster Than llama.cpp (Strata)" — `../raw/the-new-way-to-run-125b-models-6x-faster-than-llama.cpp-(strata).md` (YouTube transcript, English; channel, URL, and publish date not captured — content places it after the 2026-10-01 llama.cpp MTP merge): MTP 47–57 → 82–92 tok/s band with forced-wrong-guess lossless check, IQ-build GPU/CPU rounding at 97.5–99% agreement, llama.cpp October-1st MTP merge (28 → 44 tok/s full-VRAM, slower on spill) with open expert-cache PR (18.4 → 24.2 tok/s), and Strata-partly-from-llama.cpp framing.

[^strata-docs]: Strata docs — `../raw/Strata/HOW_IT_WORKS.md` "Guess, then check"; `../raw/Strata/DETAILS.md` "Speed (measured)" ("The draft layer's tokens (0.1.27, `--draft-vocab`)", reproducible greedy output, output-speed variability), "Tuning for your PC" (`--spec-min-p`), "How much came from where" (drafts metrics), "Current limits (v1)" (penalties), "Speed with images on" (short-answer note), and "How it works" (Speculation); `../raw/Strata/README.md` "How does it work?".
