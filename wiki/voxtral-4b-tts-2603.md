---
type: Concept
title: Voxtral 4B TTS 2603
description: Mistral AI 4B open-weights multilingual TTS model with 20 preset voices, 9-language 24 kHz synthesis, and vLLM-Omni serving with H200 latency/throughput figures.
tags: [tts, multilingual, voice-cloning, streaming]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: voxtral-card
    resource: ../raw/Voxtral-4B-TTS-2603.md
    kind: documentation
    title: Voxtral 4B TTS 2603 model card
---

Voxtral 4B TTS 2603 is Mistral AI's frontier open-weights text-to-speech model for production voice agents, combining expressive multilingual synthesis across 9 languages with 20 preset voices plus reference-based adaptation, 24 kHz multi-format output, and streaming plus batch inference served through vLLM-Omni on a single 16 GB+ GPU, under a CC-BY-NC-4.0 license inherited from its voice-reference datasets (**Reported**).[^voxtral-card]

## Model identity and release

- Weights are `mistralai/Voxtral-4B-TTS-2603` on Hugging Face; frontmatter declares `pipeline_tag: text-to-speech`, `library_name: vllm`, 9-code `language`, license `cc-by-nc-4.0`, `inference: false`, and `base_model: mistralai/Ministral-3-3B-Base-2512` with a `mistral-common` tag (**Reported**).[^voxtral-card]
- Upstream pointers are the Mistral console demo, the Mistral blog post, and the research paper at `arXiv:2603.25551`; the card also links a live Hugging Face Space demo and the vLLM-Omni repository (**Reported**).[^voxtral-card]
- BF16 weights ship with a set of reference voices; the card states these voices are licensed CC BY-NC 4.0 and that the model inherits that license (**Reported**).[^voxtral-card]

## Capabilities and languages

- Realistic, expressive speech with natural prosody and emotional range across 9 major languages plus dialect support: English, French, Spanish, German, Italian, Portuguese, Dutch, Arabic, and Hindi (**Reported**).[^voxtral-card]
- Text-to-speech generation with 20 preset voices and adaptation to new voices via an audio reference (the benchmark setup uses a 10-second reference; the client example uses a named `voice` such as `casual_male`) (**Reported**).[^voxtral-card]
- Output is 24 kHz audio in WAV, PCM, FLAC, MP3, AAC, and Opus formats, with fast time-to-first-audio plus streaming and batch inference support for high-throughput realtime voice-agent workflows (**Reported**).[^voxtral-card]
- Named use cases are customer support and call centers, financial services (with a banking-KYC voice-agent video demo), manufacturing and industrial operations, public services and government, compliance and risk, supply chain and logistics, automotive and in-vehicle systems, sales and marketing, and real-time translation (**Reported**).[^voxtral-card]

## Benchmarks

- Method: `vllm_omni` offline `end2end.py` recipe, 500-character text with a 10-second audio reference, single NVIDIA H200, vLLM 0.18.0 (**Reported**).[^voxtral-card]
- The card warns its recipe's RTF uses an inverted formula (higher is better) and the table below converts back to the standard RTF convention (lower is better) (**Reported**).[^voxtral-card]

| Concurrency | Latency | RTF (standard) | Throughput (char/s/GPU) |
| ---: | ---: | ---: | ---: |
| 1 | 70 ms | 0.103 | 119.14 |
| 16 | 331 ms | 0.237 | 879.11 |
| 32 | 552 ms | 0.302 | 1430.78 |

- No quality benchmark (WER/CER, speaker similarity, emotion, or multilingual-accuracy table) is printed in the card; latency, RTF, and throughput are the only numeric results (**Reported** absence).[^voxtral-card]

## Serving and usage

- Recommended stack is `vllm-omni >= 0.18.0` over `vllm >= 0.18.0` (which pulls `mistral_common >= 1.10.0`, verifiable via `python3 -c "import mistral_common; ..."`), with a ready-to-go `vllm/vllm-omni:v0.18.0` Docker image as an alternative (**Reported**).[^voxtral-card]
- Footprint fits a single GPU with 16 GB or more memory given the model size and BF16 format; serve with `vllm serve mistralai/Voxtral-4B-TTS-2603 --omni` (**Reported**).[^voxtral-card]
- Client posts `{"input", "model", "response_format": "wav", "voice"}` to OpenAI-compatible `POST /v1/audio/speech` (120 s timeout in the example) and decodes the response bytes as audio (`soundfile.read` in the example, playable e.g. via `sounddevice`) (**Reported**).[^voxtral-card]
- A Gradio online-serving demo recipe (clone `vllm-omni`, install `gradio==5.50`, run `examples/online_serving/voxtral_tts/gradio_demo.py --host/--port`) and the hosted Hugging Face Space are the listed try-out paths (**Reported**).[^voxtral-card]

## License and responsible use

- Voice references compatible with the model come from EARS, CML-TTS, IndicVoices-R, and Arabic Natural Audio datasets under CC BY-NC 4.0, which is why the model inherits that license; commercial use needs a separate assessment of those terms (**Reported**).[^voxtral-card]
- The card carries a responsible-use warning: the user is responsible for complying with applicable laws and avoiding misuse, and must not infringe, misappropriate, or otherwise violate third-party rights including intellectual property (**Reported**).[^voxtral-card]

## Relationships

- Served by [vLLM-Omni](vllm-omni.md): this concept's card names vLLM-Omni as the recommended production stack (`--omni` serve, `/v1/audio/speech` API, H200 benchmark harness), while the runtime page covers the disaggregated AR/DiT serving framework from its own README snapshot, which does not name Voxtral; consult that page for engine behavior and this page for the Voxtral recipe (**Synthesis**).[^voxtral-card]
- Listed by [SGLang-Omni](sglang-omni.md): that runtime's README support list already includes Voxtral TTS on `/v1/audio/speech` with batch, streaming, and uploaded voices, alongside Higgs Audio v3, Fish S2-Pro, Qwen3-TTS, and dots.tts; this concept covers the upstream Voxtral weights, card, and vLLM-Omni figures, not the SGLang serving path (**Synthesis**).[^voxtral-card]
- Mid-multilingual cloning contrast: [Audio8 TTS Preview 0.6B](audio8-tts-preview-0.6b.md) covers a 0.6B 11-language Apache-2.0 cloning model with Seed-TTS tables, while this concept covers a 4B 9-language non-commercial model with no quality table but H200 throughput figures; no shared codebase is asserted (**Synthesis**).[^voxtral-card]
- Same-upstream transcription siblings: [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md), [Voxtral Small 24B 2507](voxtral-small-24b-2507.md), and [Voxtral Mini 4B Realtime 2602](voxtral-mini-4b-realtime-2602.md) cover Mistral's transcription/audio-text checkpoints, while this concept covers the TTS weights; no shared checkpoint is asserted (**Synthesis**).[^voxtral-card]

## Coverage and limits

- Source inspected statically only; no checkpoint downloaded, no audio synthesized, and no latency, RTF, throughput, quality, cloning-fidelity, or streaming claim reproduced (**Synthesis**).[^voxtral-card]
- Blog post, research paper (`arXiv:2603.25551`), console demo, Hugging Face Space, vLLM-Omni repository and recipes, Docker image, checkpoint weights, tokenizer, and reference voices were linked but not fetched and were not present in `raw/` (**Synthesis**).[^voxtral-card]
- All capability, language, latency, throughput, memory, compatibility, and usage claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `tts` domain rule (**Synthesis**).[^voxtral-card]

[^voxtral-card]: [Voxtral 4B TTS 2603 model card](../raw/Voxtral-4B-TTS-2603.md) — locators: frontmatter (`pipeline_tag: text-to-speech`, `library_name: vllm`, 9-code `language`, `license: cc-by-nc-4.0`, `base_model: mistralai/Ministral-3-3B-Base-2512`, `inference: false`); header (frontier open-weights TTS, BF16 weights plus reference voices, CC BY-NC 4.0 inheritance; demo/blog/paper link list); `Key Features` (prosody/emotion, 20 preset voices plus adaptation, 9-language list, low-latency streaming/batch, 24 kHz plus 6-format list, production throughput); `Use Cases` (9 verticals incl. banking-KYC video demo) plus responsible-use `Warning`; `Benchmark Results` (vllm_omni `end2end.py`, 500-char plus 10 s reference, H200, v0.18.0, inverted-RTF note, 3-row concurrency/latency/RTF/throughput table); `Usage` (vLLM/vllm-omni install fences, `mistral_common >= 1.10.0` check, Docker Hub image, `vllm serve ... --omni`, `/v1/audio/speech` client fence with `casual_male` voice, Gradio demo fence, HF Space link); `License` (EARS/CML-TTS/IndicVoices-R/Arabic Natural Audio attribution, third-party-rights prohibition).
