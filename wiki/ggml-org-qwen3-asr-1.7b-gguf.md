---
type: Concept
title: ggml-org Qwen3-ASR-1.7B GGUF
description: ggml-org GGUF conversion of Qwen3-ASR-1.7B served with llama.cpp's llama-server, whose model card names no quantization, revision, license, or audio request format.
tags: [stt, asr, gguf, llama-cpp, qwen3-asr]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:35:20Z }
stale_after: 2027-10-13
sources:
  - id: ggml-org-qwen3-asr-1.7b-gguf-card
    resource: ../raw/ggml-org-Qwen3-ASR-1.7B-GGUF.md
    kind: documentation
    title: ggml-org Qwen3-ASR-1.7B-GGUF model card
---

ggml-org publishes `ggml-org/Qwen3-ASR-1.7B-GGUF`, a GGUF conversion of the upstream 1.7B checkpoint in the [Qwen3-ASR family](qwen3-asr-family.md), and its only usage path is a `llama-server -hf` launch command (**Reported**).[^ggml-org-qwen3-asr-1.7b-gguf-card] Against the CrispASR-served [CSTR GGUF set](cstr-qwen3-asr-1.7b-gguf.md), this is a different runtime and publisher. The card is minimal and records no quantization list, file sizes, revision, license, or audio request format, so its transcription behavior and quality are unverified here (**Synthesis**).

## Conversion and lineage

- The frontmatter declares `base_model: Qwen/Qwen3-ASR-1.7B`, and the body says the GGUF was converted from that checkpoint with `convert_hf_to_gguf.py` (**Reported**).[^ggml-org-qwen3-asr-1.7b-gguf-card]
- The card does not name the converter's repository or version. The script name matches llama.cpp's converter, so the llama.cpp lineage is an inference (**Synthesis**).
- Language coverage, architecture, and benchmarks belong to [Qwen3-ASR family](qwen3-asr-family.md); this card neither restates nor confirms them for the GGUF (**Synthesis**).
- The card has no license field. The family concept records an Apache-2.0 declaration on the upstream checkpoint; whether that covers this repository is not established (**Observed** for the missing field; **Synthesis** for the scope).

## Usage

```bash
llama-server -hf ggml-org/Qwen3-ASR-1.7B-GGUF
```

- Card-reported launch command, not executed (**Reported**).[^ggml-org-qwen3-asr-1.7b-gguf-card]
- The command has no quantization suffix. The card names no default file, companion file, endpoint, audio input format, language option, or timestamp support (**Observed** from the absence; consequences **Synthesis**).

## Relationships

- Uses: [Qwen3-ASR family](qwen3-asr-family.md) for the 1.7B checkpoint the card converts (**Reported** via `base_model`).[^ggml-org-qwen3-asr-1.7b-gguf-card]
- Sibling GGUF package: [CSTR Qwen3-ASR-1.7B GGUF](cstr-qwen3-asr-1.7b-gguf.md) packages the same base checkpoint for CrispASR as Q4_K, Q8_0, and F16 files. No shared file or quality evidence exists, so no comparison is asserted (**Synthesis**).
- Sibling GGUF package: [handy-computer Qwen3-ASR-1.7B GGUF](handy-computer-qwen3-asr-1.7b-gguf.md) packages the same base checkpoint for transcribe.cpp in six quantizations; the two cards share no file evidence, so no file or quality comparison is asserted (**Synthesis**).
- Catalog context: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists another `Qwen3-ASR-1.7B-GGUF` row. This card does not establish whether the two share files (**Synthesis**).

## Coverage and limits

- Entry point: one model-card capture, `raw/ggml-org-Qwen3-ASR-1.7B-GGUF.md`, inspected statically (**Observed**). No revision, commit, or upload date is recorded.
- Not captured or executed: the GGUF files, the converter, the llama.cpp build or version, the Hugging Face repository listing, and any audio request. Nothing was downloaded, converted, served, or transcribed.
- Status is `draft` because the quantization, license, revision, and invocation questions are open. The other `Qwen3-ASR-1.7B` GGUF capture, now compiled as [handy-computer Qwen3-ASR-1.7B GGUF](handy-computer-qwen3-asr-1.7b-gguf.md), shares no file evidence with this card, so no cross-package comparison is asserted (**Synthesis**).
- `stale_after` follows the `stt` domain rule for model packaging.

[^ggml-org-qwen3-asr-1.7b-gguf-card]: [ggml-org Qwen3-ASR-1.7B-GGUF model card](../raw/ggml-org-Qwen3-ASR-1.7B-GGUF.md) — locators: frontmatter (`base_model: Qwen/Qwen3-ASR-1.7B`; no license field); `# Qwen3-ASR-1.7B-GGUF` heading and intro paragraph (conversion with `convert_hf_to_gguf.py`); `To use it` fence (`llama-server -hf ggml-org/Qwen3-ASR-1.7B-GGUF`).
