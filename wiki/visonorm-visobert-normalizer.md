---
type: Concept
title: ViSoNorm (visobert-normalizer)
description: ViSoBERT-based multi-task Vietnamese lexical normalizer (NSW detection, mask prediction, normalization heads) that rewrites informal social-media text into standard Vietnamese via HuggingFace remote code, with README examples but no benchmarks, license, latency, or revision.
tags: [pipeline, stt, tts, vietnamese, text-normalization, bert]
status: draft
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-08T12:00:00Z }
stale_after: 2027-10-08
sources:
  - id: visobert-normalizer-readme
    resource: ../raw/visobert-normalizer-mix100.md
    kind: documentation
    title: ViSoNorm / visobert-normalizer model card capture (mix100)
---

ViSoNorm (README repo id `hadung1802/visobert-normalizer`) is a Vietnamese lexical normalization model on a ViSoBERT (Vietnamese social-media BERT) base that converts informal, abbreviated, or diacritic-less text such as `sv dh gia dinh chua cho di lam :))` into standard Vietnamese (**Reported**).[^visobert-normalizer-readme] It is a neural, written-to-written cleanup model, the opposite direction from the rule-based written-to-spoken [VietNormalizer](vietnormalizer.md); in a voice loop it is a candidate for cleaning chat-style text or diacritic-poor text before an LLM or TTS, not an ASR post-processor (**Synthesis**). Nothing here has been run or verified.

## Mechanism

- Base: ViSoBERT with three heads: NSW (Non-Standard Word) detection, mask prediction (how many `<mask>` tokens to insert for multi-token expansion), and lexical normalization (predicts the normalized tokens).[^visobert-normalizer-readme]
- Multi-token expansion examples: `sv` → `sinh viên`, `ctrai` → `con trai`, `t vs b` → `tôi với bạn`.[^visobert-normalizer-readme]
- Loaded through `AutoModelForMaskedLM.from_pretrained(repo, trust_remote_code=True)`; the custom methods `normalize_text` and `detect_nsw` ship in the remote code, which is why `trust_remote_code=True` is required (**Reported**; the code itself was not inspected, so executing it carries an unreviewed-code risk).[^visobert-normalizer-readme]
- Install: `pip install transformers torch`.[^visobert-normalizer-readme]

## Interface

| Call | Returns |
| --- | --- |
| `model.normalize_text(tokenizer, text, device='cpu')` | `(normalized_text, source_tokens, predicted_tokens)` |
| `model.detect_nsw(tokenizer, text, device='cpu')` | list of dicts: `index`, `start_index`, `end_index`, `nsw`, `prediction`, `confidence_score` (0.0–1.0, "combined") |

Example README output: `cung` → `cũng` (confidence 0.9415) and `long` → `lòng` (0.7056) in `nhìn thôi cung thấy đau long quá đi :))`; emoticons such as `:))` pass through unchanged.[^visobert-normalizer-readme] The lower 0.7056 case shows confidence varies on diacritic restoration, so a threshold would be needed to gate automatic replacement (**Synthesis**). Batch processing is a plain Python loop over `normalize_text`; no batched tensor API is documented.

## Claims and limits

- README calls it "state-of-the-art", "production ready", and free of "hardcoded patterns"; no benchmark, dataset, metric, or comparison backs these (**Reported**, **Unverified**).[^visobert-normalizer-readme]
- Not stated: license, training data, what "mix100" in the capture filename means, model size, CPU/GPU latency, maximum sequence length, handling of numbers/dates/named entities, streaming or chunk-boundary behavior, and failure modes (e.g. over-correcting valid words).
- The model rewrites tokens and may alter meaning or entities; for ASR output, entity accuracy should be checked before use (**Synthesis**).

## Coverage and limits

- Inspected statically: the single capture `raw/visobert-normalizer-mix100.md` (116 lines; sections Model Architecture, Features, Installation, Usage, Expected Output, NSW Detection Output Format). No revision, version, or upstream URL is recorded (**Observed**).[^visobert-normalizer-readme]
- Not inspected: weights, tokenizer, remote modeling code, training data, paper, and Hub page. No install or execution; all example outputs and confidences are unreproduced.

## Relationships

- Complements [VietNormalizer](vietnormalizer.md): this restores standard written Vietnamese from informal text; VietNormalizer then expands standard text to spoken form for TTS (**Synthesis**, untested chain).
- Candidate text-cleanup step ahead of the normalizer in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) (**Synthesis**).

[^visobert-normalizer-readme]: [ViSoNorm README capture](../raw/visobert-normalizer-mix100.md) — locators: `## Model Architecture`; `## Features`; `## Installation`; `## Usage` (Basic Usage, NSW Detection, Batch Processing); `### Expected Output`; `### NSW Detection Output Format`.
