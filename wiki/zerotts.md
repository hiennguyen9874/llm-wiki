---
type: Concept
title: ZeroTTS
description: Vietnamese-oriented 202M-parameter ONNX TTS with reported CPU streaming, latent-conditioned voices, and a voice encoder unavailable in the public release.
tags: [tts, vietnamese, streaming, onnx, voice-cloning]
status: draft
created: 2026-10-28
generated: { by: llm-wiki-agent/1, at: 2026-10-28T03:17:22Z }
stale_after: 2027-10-28
sources:
  - id: zerotts
    resource: ../raw/ZeroTTS/README-github.md
    scope: ../raw/ZeroTTS/
    kind: documentation
    title: ZeroTTS GitHub README capture
---

ZeroWeight AI reports ZeroTTS as a 202M-parameter Vietnamese-oriented ONNX text-to-speech system with CPU streaming and speaker-latent conditioning. On its own ZeroBench-TTS it reports 1.03% WER and ~70 ms CPU time to first audio; these are **Reported**, not independently verified. Crucially, the public release accepts prepared voices but cannot create them from reference audio because the voice encoder is unpublished.[^zerotts]

## Voices and responsible use

- **Reported:** eight preset voices ship with the weights; speaker conditioning is a latent array, e.g. `(1, 10, 768)`, without reference transcript or in-context audio. The README claims 3–30 seconds of reference audio can produce a voice, but the encoder is not included. The provider's separate platform requires uploading a clip to obtain latents; the GitHub capture documents `tts.add_voices("my-voice.zip")` for importing the result. This is not fully local cloning and uploading carries a privacy boundary.[^zerotts]
- **Reported:** the model card says not to impersonate or attribute speech to a person without consent, and to disclose synthetic speech when listeners might otherwise assume it is real. Preset voices are described as evaluation/demo voices. It is built for Vietnamese and English code-switching, not evaluated as an English TTS system.[^zerotts]

## Inference and deployment

**Reported:** `pip install zerotts` installs ONNX Runtime and related dependencies; approximately 900 MB of fp32 weights download from Hugging Face on first use. `ZeroTTS.from_pretrained("zeroweight-ai/ZeroTTS")` exposes `synthesize`, `synthesize_stream`, and `save_audio`; streamed example chunks are float32 `(1, n)` at 48 kHz. Browser inference uses onnxruntime-web with a one-time ~900 MB download; the captured README says audio is not uploaded by that browser demo. Optional web UI and evaluation extras exist; evaluation requires PyTorch.[^zerotts]

**Reported:** `synthesize()` does not automatically normalize Vietnamese dates, numbers and acronyms; `normalize_vi_text` is separate, while CLI and web UI normalize by default (`--no_text_norm` disables it). Long text should be segmented since training uses utterances. Default `cfg_scale=1.0`; above 1 costs twice as much per frame. Defaults include temperature 0.8, top-k 25, top-p 0.95, repetition penalty 1.2 and one trailing end-of-audio frame; the source says zero trailing frames can clip the last phone. An int8 conversion script is claimed to roughly halve RTF on a DDR4 desktop, without an accompanying quality table.[^zerotts]

## Reported evaluation

The vendor's ZeroBench-TTS comparison feeds raw text without a frontend. ZeroTTS reports WER 1.03%, UTMOS 2.91, WavLM speaker cosine 0.936 and excess silence 0.029 s; the same table reports OmniVoice WER 4.13%, UTMOS 2.76 and similarity 0.950. Thus the vendor's fourfold WER claim is specific to its compared systems and protocol, not a universal quality ranking. Model-card subsets report WER 0.16% Vietnamese, 0.97% code-switch, 1.42% cross-lingual voice prompt and 1.75% challenging dates/numbers/acronyms. PhoWhisper is identified as the ASR scorer; the underlying test data and full methodology were not inspected.[^zerotts]

For CPU timing the vendor reports one request, eight inference threads pinned to dedicated cores, and 26-, 77-, and 227-character samples, each repeated six times with the first two discarded. ZeroTTS RTF is 0.51, 0.47 and 0.53 respectively, with first audio at 53, 66 and 89 ms. The source states baselines lack a working CPU streaming path, so their TTFA measures full utterances rather than a first streaming frame; hardware model and full measurement methodology are unavailable in these captures. These results are not end-to-end voice-agent latency or concurrency measurements.[^zerotts]

## License and coverage limits

**Reported:** code and weights are MIT; bundled MOSS-Audio-Tokenizer-Nano decoder is Apache-2.0; the separate ZeroBench-TTS dataset is CC-BY-NC-4.0. Actual license files and data rights were not inspected.[^zerotts]

**Coverage:** both `README-github.md` (entry point) and `README-hf.md` were read in full as a single package; the latter adds subset results and responsible-use limits. Neither gives an immutable revision or capture date. The relative model-card banner is absent; remote samples, benchmark documentation and dataset, voice-pack documentation, browser code, implementation, model weights, license texts and external voice-encoding service were not inspected. No install, audio playback, inference, quantization or benchmark was run. The page remains draft because implementation and detailed benchmark evidence are unavailable. Promotional highlights and duplicate sample links were excluded.[^zerotts]

## Relationships

- **Compared with:** [OmniVoice](omnivoice.md) is a baseline in the vendor's raw-text benchmark, not a cross-study ranking.[^zerotts]
- **Related:** [TTS Model Survey](tts-model-survey.md) catalogs ZeroTTS alongside other voice synthesis options.

[^zerotts]: [GitHub README](../raw/ZeroTTS/README-github.md) — Install; Python; Generation settings; Voices — and voice cloning; Benchmarks; Speed — CPU; Quantization; Credits; License; [Hugging Face model card](../raw/ZeroTTS/README-hf.md) — frontmatter model-index; Benchmarks; Voices, and voice cloning; Intended use and limitations; License. Snapshot revision unavailable.
