---
type: Concept
title: Qwen3-TTS-12Hz-1.7B-Vietnamese
description: Vietnamese Qwen3-TTS-1.7B-Base finetune with two-stage phonology/style training, 30 preset speakers and a vendored non-streaming usage example, without quality or latency benchmarks.
tags: [tts, vietnamese, style-control, fine-tuning]
status: stable
created: 2026-10-15
generated: { by: llm-wiki-agent/1, at: 2026-10-15T10:43:58Z }
stale_after: 2027-04-15
sources:
  - id: qwen3-tts-vi-card
    resource: ../raw/Qwen3-TTS-12Hz-1.7B-Vietnamese.md
    kind: documentation
    title: Qwen3-TTS-12Hz-1.7B-Vietnamese model card
---

This Vietnamese finetune of `Qwen/Qwen3-TTS-12Hz-1.7B-Base` reports separate phonology and instruction-style training on one H200, with only the talker stack trained and the speech tokenizer frozen. It exposes 30 built-in speakers and Vietnamese style prompts through a vendored `qwen_tts` custom-voice API; its example is explicitly non-streaming. The card declares Apache-2.0 but supplies no Vietnamese quality, latency or memory measurements (**Reported**).[^qwen3-tts-vi-card]

## Training and checkpoint selection

- **Phonology stage:** 3 epochs on TTSDistil-Phonology, without a user turn: assistant text → codec. The card identifies `phonology/checkpoint-epoch-0` and `phonology/checkpoint-epoch-2` with this stage and says the stage-1 model initializes style training; the exact role of each named stage-1 artifact is not further explained (**Reported**).[^qwen3-tts-vi-card]
- **Style stage:** 5 epochs on TTSDistil2, whose samples have an `instruct` user turn such as “nói giọng vui vẻ.” Final weights are `checkpoint-epoch-4/`; `checkpoint-epoch-2/` is a mid-training comparison, not a demonstrated quality winner (**Reported**).[^qwen3-tts-vi-card]
- The tokenizer remains identical to the base; only the talker stack was trained. Training data hours, collection/consent, licenses, splits, hyperparameters beyond epochs/hardware, checkpoint-selection metrics and ablations are not supplied (**Reported / Observed absence**).[^qwen3-tts-vi-card]

## Inference surface

- The card requires its vendored `vendor/qwen_tts`, not merely an assumed interchangeable public package. Its example adds `/path/to/repo/vendor` to `sys.path`, imports PyTorch and `Qwen3TTSModel`, then loads `/path/to/repo/checkpoint-epoch-4` with `device_map="cuda:0"`, `dtype=torch.bfloat16`, and `attn_implementation="flash_attention_2"`; a comment names `"sdpa"` as an alternative (**Reported**).[^qwen3-tts-vi-card]
- `generate_custom_voice(text=..., language="Vietnamese", speaker="Zephyr", instruct="trung tính", non_streaming_mode=True)` returns `wavs, sr`. No numeric sample rate, save-to-file recipe, dependency versions, streaming invocation or serving API is given (**Observed** example and omissions).[^qwen3-tts-vi-card]
- The 30 presets are Zephyr, Puck, Charon, Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, `lnilam` (spelling as captured), Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager and Sulafat (**Reported**).[^qwen3-tts-vi-card]
- Base lineage does not establish that this finetune supports reference-audio cloning, upstream streaming runtimes, GGUF conversion or upstream latency figures; none is demonstrated here (**Synthesis**).[^qwen3-tts-vi-card]

## Relationships

- Related to [Qwen3-TTS-12Hz-1.7B-CustomVoice](qwen3-tts-12hz-1.7b-customvoice.md) and [0.6B CustomVoice](qwen3-tts-12hz-0.6b-customvoice.md): a Vietnamese **Base-lineage** finetune, not an official CustomVoice checkpoint or evidence that the official language list has changed (**Synthesis**).[^qwen3-tts-vi-card]
- Candidate for [Vietnamese Realtime TTS Selection](vietnamese-realtime-tts-selection.md) and the [Vietnamese voice-agent stack](vietnamese-realtime-voice-agent-stack.md): style/preset evaluation candidate only until target-hardware quality, TTFA and streaming are measured; listed separately in the [TTS survey](tts-model-survey.md) (**Synthesis**).[^qwen3-tts-vi-card]

## Coverage and trust limits

- **Inspected:** the complete single Markdown capture, including metadata, training paragraphs, usage fence and speaker list. No material local includes or attachments appear in the capture. Instructions were read statically; nothing was installed or executed.
- **Uninspected dependencies:** upstream base-model URL; TTSDistil-Phonology and TTSDistil2 data; vendored implementation; final/intermediate/phonology checkpoints and tokenizer weights. These were not supplied with this single-file source; functionality, data rights and checkpoint contents remain unverified.[^qwen3-tts-vi-card]
- **Identity limits:** the capture supplies no creator, canonical finetune URL, publication/capture date or immutable upstream revision. Its title matches a previously reported community finetune, but ownership is not independently established here. Apache-2.0 is a metadata declaration, not an inspected license text or dataset-rights audit.[^qwen3-tts-vi-card]
- No audio listening, inference, quality/latency benchmark, or independent verification was performed. Stable status means the available card synthesis is complete, not that realtime readiness is verified. No contradictory measurements or supersession evidence are supplied.[^qwen3-tts-vi-card]

[^qwen3-tts-vi-card]: [Captured model card](../raw/Qwen3-TTS-12Hz-1.7B-Vietnamese.md) — locators: YAML `license`, `language`, `base_model`, `tags`; opening paragraph and numbered Phonology/Style stages; “Final weights” paragraph; `Usage` dependency sentence and Python fence (`from_pretrained`, `generate_custom_voice`); closing “30 built-in speakers” and frozen-tokenizer/talker sentences. Revision and original publication/capture date unavailable.
