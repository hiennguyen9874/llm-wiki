---
type: Concept
title: Swift-Qwen3.8-27B GGUF
description: Reasoning-efficient Swift derivative of Qwen3.8-27B with a 24-tier GGUF ladder, KLD fidelity, 64 KiB/token KV cache, and llama.cpp/Ollama/MTP serving.
tags: [qwen3.8, swift, gguf, quantization, llama-cpp, ollama, mtp, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T15:00:00Z }
stale_after: 2027-04-05
sources:
  - id: swift-gguf
    resource: ../raw/Swift-Qwen3.8-27B-GGUF.md
    title: Swift-Qwen3.8-27B GGUF model card
---

UkisAI publishes `ukisai/Swift-Qwen3.8-27B-GGUF` as a reasoning-efficient GGUF distribution of `Swift-Qwen3.8-27B`, claiming 58.3% fewer thinking tokens at under 1% score loss and about 1.95× speed-up, with a 24-tier 9.1–29.1 GB quant ladder measured by KL divergence against BF16, a 64 KiB/token KV cache from 16 full-attention blocks, and llama.cpp/Ollama plus Q8_0 MTP speculative and vision-projector serving[^swift-gguf]. **Reported** throughout; no weights, commands, or benchmarks were executed here.

## Release identity

- Repository is `ukisai/Swift-Qwen3.8-27B-GGUF`; base is `ukisai/Swift-Qwen3.8-27b` with `base_model_relation: quantized`; frontmatter declares `pipeline_tag: image-text-to-text`, `library_name: gguf`, `swift-open-license-1.0`, and tags for `gguf`, `llama.cpp`, `qwen3_8`, `qwen3_5`, efficient-thinking, reasoning, and token-efficient[^swift-gguf]. **Reported**, with static frontmatter presence **Observed**.
- Evaluation scope is explicitly the Qwen3.8-27B BF16 base versus the same base plus the Swift adapter[^swift-gguf]. **Reported**.
- This card is the original Swift-line GGUF release, distinct from the later [Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF](swift-1.5-qwen3.8-27b-gsq-rco-gguf.md), which reports 58.5% fewer tokens, +0.35%, and 9.18× speed-up on a different four-tier GSQ-RCO ladder (**Synthesis** from the two cards' headlines).
- Demo video `swift-speed-demo.mp4` and banner `ukisai-banner.png` are referenced but absent from `raw/`; only the LiveCodeBench-v6-sample caption is preserved, and visual content is otherwise excluded as decorative[^swift-gguf]. **Reported** with that limit.

## Thinking-efficiency headline and BF16 benchmarks

Headline figures compare BF16 base with and without the Swift adapter; per the SCOPE benchmark rule they state no hardware and stay **Reported** (**Synthesis** on the rule application)[^swift-gguf].

- 58.3% fewer thinking tokens, under 1% performance loss, about 1.95× speed-up on several tasks[^swift-gguf]. **Reported**; tasks and timing method are unstated.
- Nine-benchmark score plus mean/median token table (Base versus Swift)[^swift-gguf]. **Reported**.

| Benchmark | Base score | Swift score | Base mean | Swift mean | Mean reduction | Median reduction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPQA-Diamond | 88.38% | 88.28% | 15,014 | 8,855 | ↓ 41.0% | ↓ 58.3% |
| MMLU-Pro | 85.47% | 84.95% | 2,980 | 1,603 | ↓ 46.2% | ↓ 28.3% |
| C-Eval | 90.00% | 90.62% | 1,492 | 804 | ↓ 46.1% | ↓ 19.3% |
| IFBench | 73.53% | 71.80% | 8,052 | 4,657 | ↓ 42.2% | ↓ 50.5% |
| AIME 2026 | 98.67% | 94.00% | 22,014 | 16,143 | ↓ 26.7% | ↓ 50.2% |
| HMMT (Nov 2025) | 99.33% | 96.00% | 22,032 | 15,189 | ↓ 31.1% | ↓ 45.9% |
| ERQA (multimodal) | 67.45% | 66.30% | 4,137 | 2,045 | ↓ 50.6% | ↓ 54.6% |
| Terminal-Bench 2.1 | 66.74% | 65.84% | 37,086 | 27,272 | ↓ 26.5% | ↓ 38.7% |
| LiveCodeBench v6 | 76.76% | 81.55% | 11,374 | 8,615 | ↓ 24.3% | ↓ 45.8% |

- Negative deltas preserved: AIME −4.67pp, HMMT −3.33pp, IFBench −1.73pp, Terminal-Bench −0.90pp, ERQA −1.15pp, GPQA −0.10pp, MMLU-Pro −0.52pp; C-Eval +0.62pp and LiveCodeBench +4.79pp favor Swift[^swift-gguf]. **Reported** (**Synthesis** on the arithmetic).

## Reproduction protocol

- Serving: BF16, vLLM 0.27.1, Qwen3 parser, 262,144 context, thinking `xhigh`[^swift-gguf]. **Reported**; engine-version snapshot covered by `stale_after`.
- Sampling: temperature 1.0, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, repetition_penalty 1[^swift-gguf]. **Reported**.
- Runs: averages over five seeds 0–4 per model; five trials per Terminal-Bench task[^swift-gguf]. **Reported**.
- Output caps: GPQA-Diamond 100,000; MMLU-Pro 100,000; C-Eval 16,384; IFBench 81,920; AIME 2026 250,000; HMMT Nov 2025 250,000; ERQA 100,000; Terminal-Bench agent/task limits; LiveCodeBench v6 32,768[^swift-gguf]. **Reported**.

## Quantized evaluations (W4A16 and AWQ, not this GGUF)

The card states quantized deployment is Swift's intended use and cites INT4 results from the source model card `ukisai/Swift-Qwen3.8-27b`, run on W4A16 and AWQ checkpoints rather than this F16 GGUF; they retain token savings and on AIME match or improve accuracy while cutting output-cap failures by 31–33%[^swift-gguf]. **Reported** with that checkpoint mismatch as a limit.

| Benchmark / quantization | Base accuracy | Swift accuracy | Mean reduction | Median reduction |
| --- | ---: | ---: | ---: | ---: |
| GPQA-Diamond, mixed-precision W4A16, thinking tokens | 88.69% | 88.38% | ↓ 32.1% | ↓ 50.2% |
| IFBench, mixed-precision W4A16, completion tokens | 72.58% | 71.25% | ↓ 30.1% | ↓ 38.0% |
| AIME 2026, mixed-precision W4A16, completion tokens | 84.00% | 84.00% | ↓ 19.0% | ↓ 37.5% |
| AIME 2026, AWQ INT4, completion tokens | 82.67% | 84.00% | ↓ 22.8% | ↓ 34.8% |

- Each row compares the same quantized base with and without the Swift adapter; GPQA and AIME use five seeds, IFBench uses four samples per prompt with strict scoring[^swift-gguf]. **Reported**.
- Caps: GPQA 100,000; IFBench 81,920; AIME 32,768; GPQA and IFBench use saved historical base runs; AIME uses template-default effort and counts truncated answers as incorrect, with a shorter cap making it a separate comparison from the BF16 table[^swift-gguf]. **Reported**.

## GGUF quantizations

Mean KL divergence against the BF16 source; lower is better. Tiers marked `new tier` were added 2026-09-13 and carry only wikitext-@512 plus 512-token top-token agreement; their 32k columns fill as those runs complete[^swift-gguf]. **Reported**.

| File | Size | KLD wikitext @512 | KLD wikitext @32k | KLD held-out @32k | Top-p @32k |
| --- | ---: | ---: | ---: | ---: | ---: |
| Q8_0 | 29.1 GB | 0.0009 | 0.0035 | 0.0579 | 97.92% |
| Q6_K_L (new tier) | 25.2 GB | 0.0015 | — | — | 98.24% |
| Q6_K_S (new tier) | 23.1 GB | 0.0018 | — | — | 98.09% |
| Q6_K | 22.9 GB | 0.0020 | 0.0069 | 0.0782 | 96.85% |
| Q5_K_M | 20.2 GB | 0.0056 | 0.0135 | 0.1251 | 95.60% |
| Q5_K_S (new tier) | 19.8 GB | 0.0057 | — | — | 96.70% |
| Q4_K_L (new tier) | 19.0 GB | 0.0102 | — | — | 95.77% |
| Q4_K_M | 18.0 GB | 0.0120 | 0.0211 | 0.1496 | 94.30% |
| IQ4_NL (new tier) | 17.6 GB | 0.0141 | — | — | 95.11% |
| Q4_1 (new tier) | 17.5 GB | 0.0194 | — | — | 94.09% |
| Q4_K_S (new tier) | 16.6 GB | 0.0150 | — | — | 94.95% |
| Q4_0 (new tier) | 16.0 GB | 0.0278 | — | — | 92.59% |
| IQ4_XS (new tier) | 15.7 GB | 0.0165 | — | — | 94.66% |
| IQ3_M (new tier) | 15.1 GB | 0.0390 | — | — | 91.76% |
| Q3_K_L (new tier) | 14.3 GB | 0.0412 | — | — | 91.26% |
| Q3_K_M (new tier) | 13.6 GB | 0.0552 | — | — | 89.91% |
| IQ3_XS (new tier) | 13.0 GB | 0.0555 | — | — | 89.91% |
| Q3_K_S (new tier) | 12.9 GB | 0.0631 | — | — | 89.30% |
| IQ3_XXS (new tier) | 12.5 GB | 0.0724 | — | — | 88.81% |
| Q2_K (new tier) | 11.0 GB | 0.1617 | — | — | 84.05% |
| IQ2_M (new tier) | 10.7 GB | 0.1469 | — | — | 84.47% |
| IQ2_S (new tier) | 9.9 GB | 0.2060 | — | — | 81.29% |
| IQ2_XS (new tier) | 9.3 GB | 0.2354 | — | — | 80.04% |
| IQ2_XXS (new tier) | 9.1 GB | 0.2852 | — | — | 78.09% |

- `wikitext` is wikitext-2 test; `held-out` is the vendor's own chat plus long-document set, reserved before the importance matrix was fitted; `Top-p` is top-token agreement with BF16 at 32k on the held-out set[^swift-gguf]. **Reported**.
- Long-context reading rule: read the two 32k columns together. On this hybrid architecture (48 of 64 blocks recurrent), about 0.1% of positions diverge sharply at long context for every tier including Q8_0, and the same holds for the public Q4_K_M and Q8_0 builds of base Qwen3.8-27B on the same harness; those rare positions dominate the held-out mean while median divergence at 32k stays within 10% of the 512-token value, so typical-token quality does not degrade with context[^swift-gguf]. **Reported**.
- Picks follow the 99th-percentile tail on the held-out set: 2.60 for Q4_K_M, 1.75 for Q5_K_M, 0.46 for Q6_K, 0.23 for Q8_0[^swift-gguf]. **Reported**.

Card use-case picks[^swift-gguf]. **Reported**.

| Use case | Pick |
| --- | --- |
| 24 GB cards, everyday use | Q4_K_M |
| Long agentic runs, strict tool-call formatting | Q6_K or higher |
| Maximum fidelity | Q8_0 |

## Quantization recipe

- Same importance matrix for all tiers: 8,016 chunks of domain, prompt, and long-document text; recurrent gate projections `ssm_alpha` and `ssm_beta` pinned to F32 and the MTP head to Q8_0[^swift-gguf]. **Reported**.
- `Q4_K_M` additionally lifts `ssm_out`, `attn_gate`, `output`, and `token_embd` to Q6_K; `Q5_K_M` and `Q6_K` lift `attn_gate` to Q8_0; the lifts cost about 1.1 GB on `Q4_K_M` and cut its KL divergence by roughly 20% versus a plain llama.cpp `Q4_K_M` of the same model[^swift-gguf]. **Reported**.
- Tiers added 2026-09-13 (`IQ2_XXS` through `Q6_K_L`) reuse the same matrix and F32/Q8_0 pins, with per-tensor layouts computed for this model by bartowski's `quantization-config` instead of llama.cpp's built-in heuristic (`--tensor-type-file`); `Q4_K_L`, `Q6_K_S`, and `Q6_K_L` are the large/small layouts of `Q4_K_M` and `Q6_K`[^swift-gguf]. **Reported**; external config repo uninspected.
- All files were built with llama.cpp release b10896 from a BF16 conversion of the published safetensors and checked against BF16 on the harness above[^swift-gguf]. **Reported**; build and harness uninspected.

## KV cache

Only 16 of 64 blocks are full attention, giving 16 × 4 kv-heads × 256 head_dim × 2 (K+V) × 2 bytes = 64 KiB per token[^swift-gguf]. **Reported**.

| Context | KV cache |
| --- | ---: |
| 8k | 0.5 GB |
| 32k | 2.0 GB |
| 64k | 4.0 GB |
| 128k | 8.0 GB |

- Full 262,144 context costs 16 GB of KV cache, so lower `-c` when it does not fit[^swift-gguf]. **Reported**.

## Training approach

- Swift was built by identifying reasoning-marker tokens that in the vendor's analysis trigger overthinking in Qwen reasoning rollouts, then fine-tuning Qwen while penalizing those tokens during reasoning; the result is shorter traces and, in the vendor's testing, fewer overthinking errors[^swift-gguf]. **Reported**.
- For maximum gains Swift adds a transfer component derived from BottleCap AI's `ThinkingCap-Qwen3.6-27B`[^swift-gguf]. **Reported**; upstream transfer checkpoint uninspected.

## How to use

Recipes are **Reported** and unrunnable here; engine versions are snapshots covered by `stale_after`[^swift-gguf].

### llama.cpp

Install via `llama.app`, then run the vLLM-counterpart configuration: full 262,144 context, thinking on at effort `xhigh`, Qwen3.8 thinking-mode sampling, and the embedded chat template with reasoning plus tool-call parsing[^swift-gguf]. **Reported**.

```bash
curl -LsSf https://llama.app/install.sh | sh

llama-server -hf ukisai/Swift-Qwen3.8-27B-GGUF:Q4_K_M \
  --jinja -fa on -ngl 99 \
  -c 262144 \
  --temp 1.0 --top-p 0.95 --top-k 20 --min-p 0 \
  --presence-penalty 0 --repeat-penalty 1.0 \
  --port 8000
```

- `llama-server` exposes an OpenAI-compatible API plus built-in chat web UI on that port; swap `Q4_K_M` for any tier through `IQ2_XXS`–`Q8_0` or `F16`; `-hf` fetches the tier and vision projector automatically[^swift-gguf]. **Reported**.
- Same sampling values are stored in the GGUF header and `xhigh` is the template default; flags make the configuration explicit; use a recent llama.cpp with Qwen3.5/Qwen3.8 architecture support[^swift-gguf]. **Reported**.
- Also runs in LM Studio, koboldcpp, and Jan AI; there set the same sampling values by hand with context of at least 65,536 tokens because the default 4,096-token window overflows on long reasoning and looks like an endless loop[^swift-gguf]. **Reported**.

#### Multimodal

- Image input pairs any tier with `mmproj-Swift-Qwen3.8-27B-F16.gguf`; `-hf` downloads it automatically, otherwise pass `--mmproj` when loading files manually[^swift-gguf]. **Reported**; projector binary uninspected.

#### MTP

- Every tier includes MTP (Multi-Token Prediction) layers at Q8_0 as a built-in draft model for llama.cpp speculative decoding; add `--spec-type draft-mtp --spec-draft-n-max 3`, the counterpart of vLLM `--speculative-config '{"method":"mtp","num_speculative_tokens":3}'`[^swift-gguf]. **Reported**; no acceptance-length figures are given, so per the speculative-decoding domain rule no speedup claim is recorded.

### Ollama

```bash
ollama create swift -f <(curl -fsSL https://huggingface.co/ukisai/Swift-Qwen3.8-27B-GGUF/resolve/main/Modelfile) && ollama run swift
```

- Requires Ollama 0.33 or newer; the repo `Modelfile` pulls the `Q4_K_M` tier with vision projector, applies the sampling values, and sets Ollama's built-in Qwen3.8 renderer and parser that separate reasoning from the answer and parse tool calls; the embedded chat template is identical to Qwen3.8's[^swift-gguf]. **Reported**.
- For another tier, download the Modelfile, change the tag after `FROM`, and rerun `ollama create`[^swift-gguf]. **Reported**.
- `ollama run hf.co/ukisai/Swift-Qwen3.8-27B-GGUF:Q4_K_M` also works without a Modelfile through llama.cpp plus the repo `params` file, but without Ollama's renderer/parser reasoning may appear inline[^swift-gguf]. **Reported**; `Modelfile` and `params` uninspected.
- Ollama sizes context from VRAM: 262,144 tokens with 48 GB or more, 32,768 with 24 GB, and 4,096 below that, which is too short for long reasoning; raise with `OLLAMA_CONTEXT_LENGTH=65536 ollama serve` or `/set parameter num_ctx 65536`; MTP via `/set parameter draft_num_predict 3`[^swift-gguf]. **Reported**.

### UkisAI API

- Hosted OpenAI-compatible endpoint `https://ukisai.com/api/swift/v1` with model id `swift`, free for research with no API key[^swift-gguf]. **Reported**.

```bash
curl https://ukisai.com/api/swift/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "swift", "messages": [{"role": "user", "content": "Hello, Swift."}]}'
```

## Validation

- Converted files passed a finite-tensor check and CPU text-generation smoke test; multimodal generation and the full benchmark suite were not re-evaluated on this GGUF release, and results above plus the source model card come from the BF16 and INT4 checkpoints named there, not these files[^swift-gguf]. **Reported**.

## License and access

- Gated access under Swift Open License v1.0; free personal, research, educational, evaluation, and commercial use up to US$1,000,000 annual recurring revenue including affiliates, with a separate Swift Enterprise License above that threshold via UkisAI contact[^swift-gguf]. **Reported**.
- No credentials, keys, or PII were found in the source; the no-key research API and gated-download notes are access boundaries, not sensitive values (**Observed**).

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense-family local path; this page is the thinking-efficient Swift GGUF alternative with its own 9.1–29.1 GB ladder, vision projector, and MTP builds.
- Related to [Swift 1.5 Qwen3.8-27B GSQ-RCO GGUF](swift-1.5-qwen3.8-27b-gsq-rco-gguf.md) — later Swift 1.5 four-tier GSQ-RCO release reusing ISTA allocations with its own BF16 reference; keep the two KLD tables separate because their BF16 references and harnesses differ.
- Uses [Quantization Fidelity Evaluation](quantization-fidelity-evaluation.md) — mean/median KLD-against-BF16 plus held-out and top-token agreement design used here is the same fidelity signal that page recommends over accuracy or perplexity alone.
- Uses [Unsloth MTP Local Inference](unsloth-mtp-local-inference.md) — Q8_0 MTP-head speculative shape shared with the MTP local runs documented there, though acceptance and speed are unevaluated here.

## Coverage limits

- Entry point `../raw/Swift-Qwen3.8-27B-GGUF.md` inspected statically (**Observed**); no commands executed, so install/run recipes, token counts, scores, KLD figures, and picks are **Reported**, not reproduced.
- Referenced local artifacts absent from `raw/` and uninspected: `ukisai-banner.png`, `swift-speed-demo.mp4`, `mmproj-Swift-Qwen3.8-27B-F16.gguf`, `Modelfile`, `params`, importance matrix, and built GGUF bytes.
- External evidence uninspected: `ukisai/Swift-Qwen3.8-27b` BF16 source card and safetensors, W4A16/AWQ checkpoints, `bottlecapai/ThinkingCap-Qwen3.6-27B`, bartowski `quantization-config`, llama.cpp b10896, vLLM 0.27.1, Ollama releases, LM Studio/koboldcpp/Jan AI builds, and UkisAI site plus API.
- No file revision or snapshot hash is stated; the only dates are the 2026-09-13 new-tier addition and pending 32k runs; hardware, harness version beyond the stated serving/sampling/caps, variance, and significance are unstated, so benchmark-rule figures stay **Reported**.

[^swift-gguf]: Swift-Qwen3.8-27B GGUF model card — `../raw/Swift-Qwen3.8-27B-GGUF.md` (UkisAI; Swift Open License v1.0; base `ukisai/Swift-Qwen3.8-27b`; frontmatter plus sections Benchmarks / How to reproduce / Quantized evaluations / GGUF quantizations / Recipe / KV cache / Training approach / How to use incl. llama.cpp, Multimodal, MTP, Ollama, UkisAI API / Validation / License and access / Citation): thinking-efficiency headline (58.3% fewer thinking tokens, <1% loss, 1.95× speed-up) with nine-benchmark Base-vs-Swift score plus mean/median token table; vLLM 0.27.1 / 262,144 / xhigh / temp-1.0-top_p-0.95-top_k-20 reproduce protocol with per-benchmark output caps and five-seed method; W4A16/AWQ quantized-evaluation table from the source BF16 card with 31–33% AIME cap-failure reduction and checkpoint-mismatch caveat; 24-tier 9.1–29.1 GB GGUF table with wikitext-@512 plus 32k KLD and top-p agreement, 2026-09-13 new-tier pending-columns note, hybrid 48/64-recurrent tail explanation with 99th-percentile picks, and Q4_K_M / Q6_K+ / Q8_0 use-case picks; 8,016-chunk imatrix with ssm_alpha/ssm_beta-F32 plus MTP-Q8_0 pins, Q4_K_M/Q5_K_M/Q6_K lifts with 1.1 GB / ~20% KL note, bartowski-layout new tiers, and b10896 build; 16/64-attention 64 KiB/token KV formula with 8k–128k plus full-262k cache table; reasoning-marker-penalty plus BottleCap-ThinkingCap transfer training with fewer-overthinking-errors observation; llama-server / -hf / mmproj / draft-mtp-n-max-3 / Modelfile-params / context-sizing / research-API recipes; finite-tensor plus CPU-smoke validation with no-GGUF-benchmark-re-eval limit; $1M-threshold gated licensing.
