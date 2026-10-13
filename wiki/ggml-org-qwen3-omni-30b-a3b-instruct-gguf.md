---
type: Concept
title: ggml-org Qwen3-Omni-30B-A3B-Instruct GGUF
description: ggml-org GGUF conversion of Qwen3-Omni-30B-A3B-Instruct served with llama.cpp's llama-server, whose model card names no quantization, revision, license, or modality support.
tags: [llm, gguf, llama-cpp, qwen3-omni]
status: draft
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:31:00Z }
stale_after: 2027-10-13
sources:
  - id: ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card
    resource: ../raw/ggml-org-Qwen3-Omni-30B-A3B-Instruct-GGUF.md
    kind: documentation
    title: ggml-org Qwen3-Omni-30B-A3B-Instruct-GGUF model card
---

ggml-org publishes `ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF`, a GGUF conversion of the upstream Qwen3-Omni-30B-A3B-Instruct checkpoint, and its only usage path is a `llama-server -hf` launch command (**Reported**).[^ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card] The card is a single short page. It names no quantization, file list, revision, license, modality support, or request format, so whether this package can serve the audio parts of a voice loop is unverified (**Synthesis**). The card follows the same publisher and conversion-and-launch template as the sibling [ggml-org Qwen3-ASR-1.7B GGUF](ggml-org-qwen3-asr-1.7b-gguf.md) (**Synthesis**).

## Conversion and lineage

- The frontmatter declares `base_model: Qwen/Qwen3-Omni-30B-A3B-Instruct`. The body links that upstream checkpoint and says the GGUF was converted with `convert_hf_to_gguf.py` (**Reported**).[^ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card]
- The card does not name the converter's repository or version. The script name matches llama.cpp's converter, so the llama.cpp lineage is an inference (**Synthesis**).
- The "Omni" in the name suggests a multimodal upstream, but the card states no speech input, speech output, or other modality support for this GGUF. Multimodal behavior under llama.cpp is not established by this source (**Observed** for the absence; **Synthesis** for the consequence).
- The card has no license field. Whether the upstream checkpoint's terms apply to this repository is not established (**Observed** for the missing field).

## Usage

```bash
llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF
```

- Card-reported launch command, not executed (**Reported**).[^ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card]
- The command has no quantization suffix. The card names no default file, companion file, endpoint, chat template, context length, or audio request format (**Observed** from the absence; consequences **Synthesis**).

## Relationships

- Uses: the upstream Qwen3-Omni-30B-A3B-Instruct checkpoint, linked from the card but without a dedicated concept in this wiki yet (**Reported** via `base_model`).[^ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card]
- Lineage context: the [Qwen3-ASR family](qwen3-asr-family.md) records Qwen3-Omni as its foundation (**Reported** by that family's card). This package shares no evidenced file, weight, or code with the ASR family, so the link is lineage context only (**Synthesis**).
- Voice-loop context: [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) lists Qwen3-Omni-30B-A3B with Vietnamese speech input but no Vietnamese speech output in its component table. That language coverage belongs to the upstream model in that report and is not established for this GGUF (**Synthesis**).
- Other serving paths: [SGLang-Omni](sglang-omni.md) and [vLLM-Omni](vllm-omni.md) name Qwen3-Omni among their supported models. Those are separate serving runtimes, not this llama.cpp package (**Synthesis**).
- Sibling packaging: [ggml-org Qwen3-ASR-1.7B GGUF](ggml-org-qwen3-asr-1.7b-gguf.md) comes from the same publisher and template for a different checkpoint, with no shared file evidence (**Synthesis**).

## Coverage and limits

- Entry point: one model-card capture, `raw/ggml-org-Qwen3-Omni-30B-A3B-Instruct-GGUF.md`, inspected statically (**Observed**). No revision, commit, or upload date is recorded.
- Not captured or executed: the GGUF files and any quantizations, the upstream checkpoint, the converter and llama.cpp version, the Hugging Face repository listing, license terms, and any request. Nothing was downloaded, converted, served, or prompted.
- Status is `draft` because the quantization, license, revision, modality, and invocation questions are open. The upstream Qwen3-Omni model has no dedicated concept here, so its own claims are not compiled by this page.
- `stale_after` follows the `llm` domain rule for model packaging.

[^ggml-org-qwen3-omni-30b-a3b-instruct-gguf-card]: [ggml-org Qwen3-Omni-30B-A3B-Instruct-GGUF model card](../raw/ggml-org-Qwen3-Omni-30B-A3B-Instruct-GGUF.md) — locators: frontmatter (`base_model: Qwen/Qwen3-Omni-30B-A3B-Instruct`; no license field); `# Qwen3-Omni-30B-A3B-Instruct-GGUF` heading and intro paragraph (upstream link and conversion with `convert_hf_to_gguf.py`); `To use it` fence (`llama-server -hf ggml-org/Qwen3-Omni-30B-A3B-Instruct-GGUF`).
