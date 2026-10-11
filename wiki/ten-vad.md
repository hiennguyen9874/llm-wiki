---
type: Concept
title: TEN VAD
description: TEN framework's low-latency streaming voice activity detector with 10/16 ms hops at 16 kHz, a ~306 KB Linux library, vendor-reported precision and RTF advantages over Silero VAD and WebRTC VAD, and C, Python, JS/WASM, Java, and Go bindings under Apache-2.0 with additional conditions.
tags: [vad, endpointing, pipeline, edge, onnx, wasm, license-check]
status: stable
created: 2026-10-08
generated: { by: llm-wiki-agent/1, at: 2026-10-11T12:00:00Z }
stale_after: 2027-10-08
sources:
  - id: ten-vad
    resource: ../raw/ten-vad/README-github.md
    scope: ../raw/ten-vad/
    kind: documentation
    title: TEN VAD (TEN-framework) GitHub README and Hugging Face model card captures
---

TEN VAD (`TEN-framework/ten-vad`) is a frame-level, streaming voice activity detector from the TEN conversational-voice-agent framework. It consumes 16 kHz audio in 160- or 256-sample hops (10 or 16 ms) and returns a speech probability plus a binary flag per frame (default threshold 0.5). The vendor claims higher precision than WebRTC VAD and [Silero VAD](silero-vad.md), much faster speech-to-non-speech transition detection than Silero, and lower RTF and library size, with RTF of about 0.005–0.057 across CPUs from iPhone 8 to Android budget phones and a 277–731 KB library depending on platform. All figures are vendor-reported; the PR-curve and transition-delay figures are images that were not captured, and no independent or Vietnamese evidence exists in the source (**Reported**).[^ten-vad]

## Identity and licensing

- Publisher: TEN Team (TEN framework, 2025 citation block, contact `developer@ten.ai`); distributed as a GitHub repository with a mirrored Hugging Face model repo (**Reported**).[^ten-vad]
- License: "Apache 2.0 with additional conditions", referring to a `LICENSE` file that is not in the capture; `pitch_est.cc` contains modified [LPCNet](https://github.com/xiph/LPCNet) code under BSD-2-Clause and BSD-3-Clause, documented in a `NOTICES` file that is also not in the capture. The conditions are unknown, so check them before commercial use (**Reported**; conditions **Unverified**).[^ten-vad]
- Both captures carry the same license wording, unlike the sibling [TEN Turn Detection](ten-turn-detection.md), whose two captures disagree.[^ten-vad]
- Latest news in both captures is dated 2025/11; no release tag, commit, or capture date is recorded (**Unverified** freshness).[^ten-vad]

## Interface and operating parameters

- Input: 16 kHz audio; other rates must be resampled. Optimized hop sizes are 160 and 256 samples (10 / 16 ms) (**Reported**).[^ten-vad]
- Output per frame: a probability in [0.0, 1.0] and a 0/1 flag at a default threshold of 0.5, which the README says must be tuned per domain (**Reported**).[^ten-vad]
- Java API as documented: `new TenVad(hopSize, threshold)`, `process(short[])` returning `VadResult` with `getProbability()`, `getFlag()`, `isVoiceDetected()`, plus `getVersion()` and `destroy()` (**Reported**).[^ten-vad]
- Python: `from ten_vad import TenVad` after `pip install -U --force-reinstall -v git+https://github.com/TEN-framework/ten-vad.git`, or run `examples/test.py` on `s0724-s0730.wav`; the library depends only on numpy (**Reported**).[^ten-vad]
- Streaming semantics beyond this (state reset between turns, hysteresis, minimum-silence and speech-padding handling) are not described; unlike [Silero VAD](silero-vad.md), the README documents no `VADIterator`-style segmentation, so turn-level endpoint logic must be built on the per-frame output (**Synthesis**).[^ten-vad]

## Reported performance

**Accuracy.** A precision-recall plot compares WebRTC VAD (described as pitch-based), Silero VAD, and TEN VAD on a manually annotated test set drawn from LibriSpeech, GigaSpeech, and DNS Challenge audio; the README says TEN VAD is best and that cross-validation on large internal datasets reproduces this. The labeled `testset` directory and `examples/plot_pr_curves.py` (Linux x64) are named for reproduction. The plot itself is an image absent from the capture, so no numeric precision, recall, or F1 value is available, and sample counts and noise conditions are unknown (**Reported**).[^ten-vad]

**Latency behavior.** A second figure is described as showing TEN VAD detecting speech-to-non-speech transitions rapidly while Silero VAD lags "several hundred milliseconds" and misses a short silence in a 6.5–7.0 s segment. No millisecond figure or protocol is given (**Reported**).[^ten-vad]

**RTF and size** (GitHub capture; lower RTF is faster):[^ten-vad]

| Platform | CPU | TEN VAD RTF | Silero VAD RTF | TEN lib size |
|---|---|---:|---:|---|
| Linux | AMD Ryzen 9 5900X | 0.0150 | — | 306 KB |
| Linux | Xeon Platinum 8253 | 0.0136 | — | 306 KB |
| Linux | Xeon Gold 6348 @ 2.60 GHz | 0.0086 | 0.0127 | 306 KB |
| Windows | Intel i7-10710U | 0.0150 | — | 464 KB (x86) / 508 KB (x64) |
| macOS | Apple M1 | 0.0160 | — | 731 KB |
| Web | macOS (M1) | 0.010 | — | 277 KB |
| Android | Galaxy J6+ (32-bit) | 0.0570 | — | 373 KB (v7a) / 532 KB (v8a) |
| Android | Oppo A3s | 0.0490 | — | 373 KB (v7a) / 532 KB (v8a) |
| iOS | iPhone 6 (A8) | 0.0210 | — | 320 KB |
| iOS | iPhone 8 (A11) | 0.0050 | — | 320 KB |

- Silero VAD's size is listed once for all rows as 2.16 MB (JIT) / 2.22 MB (ONNX) (**Reported**).[^ten-vad]
- Comparison caveat (**Synthesis**): Silero RTF is given for only one machine (Xeon Gold 6348), so any "faster than Silero" claim rests on a single CPU, with unknown thread count, runtime, hop size, and audio length. Arithmetic on that row gives about 32% lower RTF for TEN (0.0086 vs 0.0127), and 306 KB vs 2.16–2.22 MB is roughly 86% smaller; these are derived values, not README statements, and they match the figures quoted in the secondary report cited from [Silero VAD](silero-vad.md).[^ten-vad]
- Absolute RTF is already small for both detectors on server CPUs, so the practical difference is footprint on edge devices and transition latency rather than CPU budget (**Synthesis**).[^ten-vad]

## Platforms and bindings

| Platform | Library | Arch | Interfaces (GitHub capture) |
|---|---|---|---|
| Linux | `libten_vad.so` | x64 | Python, C, Java, Go |
| Windows | `ten_vad.dll` | x64, x86 | C, Java, Go |
| macOS | `ten_vad.framework` | arm64, x86_64 | C, Java, Go |
| Web | `ten_vad.wasm` | — | JS |
| Android | `libten_vad.so` | arm64-v8a, armeabi-v7a | C, Java |
| iOS | `ten_vad.framework` | arm64 only (not simulator, not iPad) | C |

- Prebuilt dynamic libraries are the primary path; headers and wrappers are `ten_vad.h`, `ten_vad.py`, `ten_vad.js`, `TenVad.java`. Linux needs `libc++1`; Windows builds were verified with Visual Studio 2017/2019/2022, Android with NDK r25b, macOS/iOS with Xcode 15.2 (**Reported**).[^ten-vad]
- **ONNX path** (released 2025/06 with the preprocessing code): the model lives in `src/onnx_model`; the C ONNX demo (`examples_onnx/`) and the Python ONNX demo (`examples_onnx/python`) need ONNX Runtime ≥ 1.17.1 and a build script (`build-and-deploy-linux.sh --ort-path ...` or the macOS variant). This is what makes the detector portable beyond the prebuilt-library platforms (**Reported**).[^ten-vad]
- WASM + JS build and browser demo (`lib/Web`, `examples/test_browser.html` via `python3 -m http.server`), Node demo (`test_node.js`), Go demo (`examples/go-tenvad`, via `LD_LIBRARY_PATH`), and Java via JNA 5.13.0 (**Reported**).[^ten-vad]
- Integrated into k2-fsa `sherpa-onnx` (2025/07 news; see its `ten-vad` documentation page), and used by community projects LiveCap (Japanese sentence-end detection) and Rustpbx; testimonials are vendor-selected quotes, not measurements (**Reported**).[^ten-vad]
- Python scope is ambiguous in the GitHub README: the platform table lists Python for Linux only and the intro says bindings are "optimized for Linux x64", while news items claim Python inference on macOS and Windows with prebuilt libs and ONNX Python on Linux/macOS (**Observed** inconsistency; resolution **Unverified**).[^ten-vad]

## Capture differences

The Hugging Face card is an older body of the same README: it lists Python/C only (no Java, Go, WASM table row, or Web RTF row), has a Node-only JS section, no Python ONNX route, and a Hugging Face `git clone` install line, while its news list matches GitHub's. Prefer the GitHub capture for platform support (**Observed**).[^ten-vad]

## Relationships

- Compared against and positioned as an alternative to [Silero VAD](silero-vad.md); that page records a small community benchmark (Silero F1 91.9% vs TEN 69.2% under UrbanSound8K noise) that conflicts with this vendor claim (**Reported**; both unresolved).[^ten-vad]
- Sibling of [TEN Turn Detection](ten-turn-detection.md): the TEN ecosystem pairs frame-level VAD (this page) with a text-based finished/unfinished/wait classifier, and a Hugging Face Space demonstrates both together. See [Turn Detection Models](turn-detection-models.md) for the turn-level comparison (**Reported**).[^ten-vad]
- Part of the TEN Framework listed in [Voice Agent Frameworks](voice-agent-frameworks.md), which records the same license-with-conditions concern (**Synthesis**).[^ten-vad]
- Also compared in the [FireRedVAD](firered-vad.md) vendor table (FLEURS-VAD-102), where TEN VAD scores F1 95.19, false-alarm rate 15.47%, and miss rate 2.95% — behind Silero VAD on F1 and false alarms, but with the lower miss rate; a third vendor's own benchmark, not independent corroboration (**Synthesis**).
- Peer of NVIDIA's [Frame-VAD Multilingual MarbleNet v2.0](frame-vad-multilingual-marblenet-v2-0.md) (91.5K parameters, 20 ms frames, ROC-AUC only); the two cards share no benchmark or metric set (**Synthesis**).
- Selection use (**Synthesis**): consider it where a 10 ms hop, a tiny native library, or browser/mobile deployment matters; otherwise [Silero VAD](silero-vad.md) is the better-documented default, and the pipeline guidance in [Vietnamese Speech Pipeline Design](vietnamese-speech-pipeline-design.md) recommends measuring on in-domain audio before switching.[^ten-vad]

## Contradictions

- **TEN VAD vs Silero accuracy:** the TEN README claims the best precision-recall performance on its own annotated set; a community NOVA-VAD benchmark recorded in [Silero VAD](silero-vad.md) reports the opposite ordering. Neither is chosen (**Reported**).[^ten-vad]
- **Python platform support:** see the Python-scope note under Platforms and bindings (**Observed**).[^ten-vad]

## Coverage and limits

- Two files inspected statically: `README-github.md` (entry point) and `README-hf.md`; overlapping content was reconciled once and differences recorded above (**Observed**).[^ten-vad]
- Not captured and not inspected: the PR-curve and agent-friendliness figures, banner and iOS setup images, the demo video, `LICENSE`, `NOTICES`, the ONNX model file and its input/output shapes, the preprocessing source (`pitch_est.cc` etc.), the `testset` audio and labels, `examples/` scripts, and the sherpa-onnx documentation. Badges, community links, star prompts, and the ecosystem table were excluded as decorative or navigational.
- The architecture, parameter count, training data, and training recipe are not described in the READMEs.
- No revision or capture date is recorded. Nothing was installed, built, or run, and no accuracy, RTF, latency, or size figure was reproduced. No Vietnamese, tonal-language, or noisy-telephony evidence is present.

[^ten-vad]: [TEN VAD captures](../raw/ten-vad/README-github.md) — `README-github.md`: `Latest News`, `Introduction`, `Key Features` §1 (PR curves, threshold 0.5, `plot_pr_curves.py`), §1.1, §2 (Agent-Friendly), §3 (RTF/lib-size table), §4, §5 (16 kHz, 160/256 hop), `Developers Testimonial`, `Installation`, `Quick Start` (platform table, Python Usage incl. ONNX model, JS, Java incl. API reference, Go, C per-platform), `TEN Ecosystem`, `Citations`, `License`. `README-hf.md`: frontmatter tags, `Key Features` §3 table (no Web row), `Quick Start` (Python/C only), `License`.
