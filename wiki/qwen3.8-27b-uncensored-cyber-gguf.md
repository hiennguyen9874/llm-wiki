---
type: Concept
title: Qwen3.8-27B Uncensored Cyber GGUF
description: llama.cpp GGUF packaging of philbert440 Qwen3.8-27B-Uncensored-Cyber (v2 recipe) with a Q4_K_M to Q8_0 weight ladder, BF16/Q8_0 vision projector, optional MTP speculative head, and card-reported cyber refusal plus capability deltas.
tags: [qwen3.8, gguf, quantization, llama-cpp, uncensored, mtp, speculative-decoding, vision, local-inference]
status: stable
created: 2026-10-05
generated: { by: llm-wiki-agent/1, at: 2026-10-05T15:00:00Z }
stale_after: 2027-04-05
sources:
  - id: cyber
    resource: ../raw/Qwen3.8-27B-Uncensored-Cyber-GGUF.md
    title: Qwen3.8-27B-Uncensored-Cyber-GGUF model card
---

This card packages **Qwen3.8-27B-Uncensored-Cyber** (v2 recipe) as llama.cpp GGUF weight quants plus a vision projector for image input and an optional MTP head for speculative decoding, with card-reported evaluation showing 100/100 on the card's held-out cyber set against 93/100 for the previous build[^cyber]. **Reported** by the card unless noted; no weights were executed here, so all size, fidelity, and benchmark figures are card claims, not reproduced.

## Identity and packaging

- Base model is `philbert440/Qwen3.8-27B-Uncensored-Cyber`; the card declares Apache-2.0, an `image-text-to-text` pipeline tag, and uncensored/abliterated/Qwen3/cyber/GGUF/llama.cpp tags[^cyber]. **Reported**.
- Weight quants shipped are `Q8_0`, `Q6_K`, `Q5_K_M`, and `Q4_K_M`, with `Q4_K_M` the smallest and `Q8_0` described as approximately lossless[^cyber]. **Reported**.
- Vision input uses `mmproj-*` projector files in `BF16` or `Q8_0`, passed via `--mmproj`[^cyber]. **Reported**.
- Speculative decoding uses optional `mtp-*` head files in `BF16`, `Q8_0`, or `Q4_0`[^cyber]. **Reported**.
- Full BF16 is not shipped as a single GGUF because it exceeds the card's stated 50 GB per-file limit; the card points to `Q8_0` as the near-lossless GGUF path or to the bf16 safetensors repo for full precision[^cyber]. **Reported**.
- The card describes the weights as uncensored/de-refused and tuned to fully answer cyber and offensive-security questions, with a use-responsibly and comply-with-applicable-law note[^cyber]. **Reported**; prompt contents and offensive procedures are excluded here and only the packaging and high-level evaluation framing are preserved.

## Evaluation

Card evaluation is stated as bf16 and Claude-judged, with the cyber column defined as 100 held-out cyber-offensive prompts under a regex refusal harness[^cyber]. **Reported**.

| Metric (arrow = better direction) | Cyber v2 (this line) | Previous Cyber build[^cyber] |
|---|---:|---:|
| cyber-open (higher) | 100/100 | 93/100 |
| confab (lower) | 0.867 | 1.00 |
| factual (higher) | 1.00 | 0.933 |
| gsm8k (higher) | 0.80 | 0.825 |
| degen (lower) | 0.00 | 0.00 |

- No hardware, harness revision, prompt text, judge prompt, variance, or per-quant serving measurement is stated for these figures, so they stay **Reported** per the SCOPE benchmark rule.
- gsm8k is the one metric where the previous build scores higher (0.825 vs 0.80); degen is tied at 0.00[^cyber]. **Reported**.

## Relationships

- Related to [Qwen3.8 Local Deployment](qwen3.8.md) — same 27B dense base family; that page covers the official Unsloth GGUF/NVFP4 path while this is a cyber-tuned uncensored community GGUF alternative with projector plus MTP packaging.
- Related to [JonathanColetti Qwen3.8-27B Uncensored GGUF](jonathancoletti-qwen3.8-27b-uncensored-gguf.md) — another uncensored 27B GGUF; JonathanColetti documents a Heretic bf16 edit with paired perplexity/KL cost evidence and measured MTP tables, while this card reports only the file ladder and high-level capability deltas.
- Related to [RVN Qwen3.8-27B Heretic Abliterated Uncensored GGUF](rvn-qwen3.8-27b-heretic-abliterated-gguf.md) — another uncensored 27B GGUF with multilingual calibration and embedded-MTP twins; this card is the thinner cyber-line counterpart with no stated calibration or verification detail.
- Related to [HauhauCS Qwen3.8-27B Aggressive MTP GGUF](hauhaucs-qwen3.8-27b-aggressive-mtp-gguf.md) — another uncensored 27B GGUF with an MTP ladder and llama.cpp serving tables; this card states the MTP file options without acceptance or throughput evidence.
- Uses [Speculative Decoding Foundations](speculative-decoding-foundations.md) — the optional `mtp-*` head here is an instance of draft-verify-accept speculation, but the card supplies no acceptance length or workload shape.

## Coverage limits

- Entry point `../raw/Qwen3.8-27B-Uncensored-Cyber-GGUF.md` inspected statically (**Observed**); no commands executed, so packaging, sizing, and evaluation claims are **Reported**, not reproduced.
- External artifacts uninspected: `philbert440/Qwen3.8-27B-Uncensored-Cyber` base weights, the linked bf16 safetensors repo, all GGUF/mmproj/mtp binaries, the Claude judge setup, and the 100-prompt cyber set plus regex harness.
- Card revision, publisher identity beyond the base-model namespace, quantization method and calibration, context length, architecture parameters, sampling/template guidance, and llama.cpp version compatibility are unstated; recorded here as limits rather than assumed.
- Harmful-prompt contents, offensive procedures, and attack-chain detail are excluded; only refusal counts, metric deltas, and the card's responsible-use note are preserved.

[^cyber]: Qwen3.8-27B-Uncensored-Cyber-GGUF model card — `../raw/Qwen3.8-27B-Uncensored-Cyber-GGUF.md` (frontmatter: Apache-2.0, base `philbert440/Qwen3.8-27B-Uncensored-Cyber`, `image-text-to-text` pipeline; Files section: `Q8_0`/`Q6_K`/`Q5_K_M`/`Q4_K_M` ladder with `Q4_K_M` smallest and `Q8_0` near-lossless, `mmproj-{BF16,Q8_0}` via `--mmproj`, `mtp-{BF16,Q8_0,Q4_0}` optional, no single-file BF16 over the 50 GB limit with safetensors pointer; Evaluation section: bf16 Claude-judged table with 100 held-out cyber-offensive prompts plus regex refusal harness, v2 vs previous rows for cyber-open/confab/factual/gsm8k/degen; Note section: uncensored/de-refused cyber/offensive-security tuning with responsible-use and legal-compliance notice).
