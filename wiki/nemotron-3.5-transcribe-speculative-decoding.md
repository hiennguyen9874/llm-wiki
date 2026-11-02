---
type: Concept
title: Nemotron 3.5 Transcribe Speculative Decoding
description: MTP versus DFlash2 serving tradeoffs for Nemotron 3.5 Transcribe, including throughput conditions and the vLLM timestamp incompatibility.
tags: [stt, asr, nemotron, inference, speculative-decoding]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:30:00Z }
stale_after: 2027-05-02
sources:
  - id: nemotron-dflash-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2.md
    kind: documentation
    title: NVIDIA Nemotron 3.5 Transcribe DFlash2 model card
  - id: nemotron-transcribe-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B.md
    kind: documentation
    title: NVIDIA Nemotron 3.5 Transcribe model card
---

[Nemotron 3.5 Transcribe](nemotron-3.5-transcribe-30b-a4b.md) supports native multi-token prediction (MTP) or a separate DFlash2 drafter, but not both at once. DFlash2 is not a standalone ASR model; the target verifies proposed tokens, with greedy output matching the target apart from possible numerical differences (**Reported**).[^nemotron-dflash-card]

## Choosing a mode

- DFlash2 is an approximately 570M-parameter BF16 six-layer block-diffusion drafter conditioned on six target hidden layers, trained on greedy outputs of the main model. It supports the BF16, FP8 and NVFP4 target variants; draft length is at most 15, with 7 the recommended start (**Reported**).[^nemotron-dflash-card]
- On one H100 80 GB, tuned batched English ASR with BF16 and reasoning off gives approximately 410 RTFx for MTP2, 270 for MTP8, 340 for DFlash2 K=7 and 260 for K=15. This excludes startup, varies with workload and is throughput, not single-request latency. The card says DFlash2 gave lowest single-request latency on one RTX PRO 6000 Blackwell, whereas MTP can have higher throughput for 10-minute recordings (**Reported**).[^nemotron-transcribe-card][^nemotron-dflash-card]
- MTP8 reuses a repeated layer; it does not imply eight independently trained MTP depths. DFlash2 acceptance falls with longer recordings (**Reported**).[^nemotron-transcribe-card][^nemotron-dflash-card]

## vLLM configuration boundary

For the documented vLLM 0.32.0 integration, DFlash2 requires the V2 model runner, removes the timestamp middleware, and sets `--hf-overrides '{"ctc_timestamps":{"enabled":false}}'`; replace the MTP speculative configuration with `{"method":"dflash","num_speculative_tokens":7,"model":"nvidia/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2"}`. It cannot provide CTC word timestamps; use MTP or no speculation with the documented V1 alignment path when those are needed (**Reported**).[^nemotron-dflash-card][^nemotron-transcribe-card]

The card provides a patch to installed vLLM source to prevent a request-completion failure in version 0.32.0; it writes into the installed package and is version-sensitive. Review and validate the patch and external dependencies before use; it was not executed here. The patch is described as Apache-2.0 third-party code, separate from the card-declared OpenMDW-1.1 model terms (**Reported**).[^nemotron-dflash-card]

## Coverage and relationships

Both local model cards were read statically. Their linked technical report, code, weights, licenses and absent local `THIRD_PARTY_NOTICES.md` and `CONTRIBUTING.md` were not inspected; no server, patch, inference or benchmark was run. Neither card specifies a source revision or local capture time. Draft reflects these limits.

- Depends on [Nemotron 3.5 Transcribe](nemotron-3.5-transcribe-30b-a4b.md); the draft checkpoint cannot transcribe on its own (**Reported**).[^nemotron-dflash-card]

[^nemotron-dflash-card]: [DFlash2 model card](../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B-DFlash2.md), Model Summary; Quick Start; Limitations.
[^nemotron-transcribe-card]: [Main model card](../raw/NVIDIA-Nemotron-3.5-Transcribe-30B-A4B.md), Inference Setup and Prompts → Speculative Decoding and Word Timestamps and Speaker Diarization.
