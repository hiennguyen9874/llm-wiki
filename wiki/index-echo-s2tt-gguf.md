---
type: Concept
title: Index-Echo S2TT GGUF
description: GGUF packaging of Index-Echo S2TT 2B and 9B for audio.cpp Chinese-to-English/Spanish/Japanese speech translation with C++/Python parity figures and RTX 5090 performance.
tags: [ml, s2tt, speech-translation, audio-cpp, gguf]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: index-echo-s2tt-gguf
    resource: ../raw/Index-Echo-S2TT-GGUF.md
    kind: documentation
    title: Index-Echo-S2TT GGUF
---

Index-Echo S2TT GGUF is a GGUF port of the IndexTeam Index-Echo-S2TT 2B and 9B speech-to-text translation models for native use with [audio.cpp](https://github.com/0xShug0/audio.cpp), where Chinese speech produces timestamped source transcripts plus English, Spanish, or Japanese translations, with five weight files, a 20-clip FLEURS-based C++/Python parity report, and RTX 5090 long-form performance figures (**Reported**).[^index-echo-s2tt-gguf]

## Package identity and capabilities

- Card title is "Index-Echo-S2TT GGUF"; frontmatter declares `license: apache-2.0`, `base_model: IndexTeam/Index-Echo-S2TT-2B` and `IndexTeam/Index-Echo-S2TT-9B`, `library_name: audio.cpp`, `pipeline_tag: automatic-speech-recognition`, and tags `audio.cpp`, `gguf`, `speech-translation`, `subtitles`, `chinese` (**Reported**).[^index-echo-s2tt-gguf]
- This port supports **S2TT only**; it does not generate translated speech (**Reported**).[^index-echo-s2tt-gguf]
- Upstream checkpoints are the official [2B checkpoint](https://huggingface.co/IndexTeam/Index-Echo-S2TT-2B/tree/72fd8bdc9bf8251f1c35f6d6289a950eda154395) at `72fd8bdc9bf8251f1c35f6d6289a950eda154395` and [9B checkpoint](https://huggingface.co/IndexTeam/Index-Echo-S2TT-9B/tree/05f86cb7a38684916e193282b6cc02462ace4043) at `05f86cb7a38684916e193282b6cc02462ace4043` (**Reported**).[^index-echo-s2tt-gguf]
- Each GGUF embeds the audio tower, connector, text decoder, tokenizer, configuration, and audio.cpp model spec; unused vision weights are not included (**Reported**).[^index-echo-s2tt-gguf]
- Architecture note: 2B and 9B use the same C++ translation path, including prompt, audio encoder, decoder implementation, and greedy sampler; 2B original is described as parity-safe while 9B original has drifts; 2B has 24 layers and tied token/output embeddings while 9B has 32 layers and a separate LM head, which the card suggests could change sensitivity to numerical differences but explicitly states is unproved (**Reported**).[^index-echo-s2tt-gguf]
- The card notes there is room to improve 9B output parity and quantized quality and welcomes focused PRs with reproducible C++/Python comparisons (**Reported**).[^index-echo-s2tt-gguf]

## Files and recommendations

- File layout with size and card recommendation (**Reported**):[^index-echo-s2tt-gguf]

| File | Size | Recommendation |
| --- | ---: | --- |
| `index-echo-s2tt-2b-orig.gguf` | 4.76 GiB | Default 2B package; original checkpoint precision |
| `index-echo-s2tt-2b-q8_0.gguf` | 2.97 GiB | 2B Q8_0; same WER/CER as original on the 20-clip diagnostic set |
| `index-echo-s2tt-2b-q4_k.gguf` | 2.14 GiB | Experimental 2B Q4_K; linear-attention QKV projections remain Q8_0 |
| `index-echo-s2tt-9b-orig.gguf` | 17.95 GiB | Original 9B precision and quality reference |
| `index-echo-s2tt-9b-q8_0.gguf` | 10.44 GiB | Recommended 9B quantization in these tests |

- **9B Q4_K is not provided**: it repeated or omitted speech on short clips and failed a long-form request with incomplete subtitle cues, despite passing the short smoke test (**Reported**).[^index-echo-s2tt-gguf]
- The 2B Q4_K package completed the 20 clips below, but that small set does not establish general reliability (**Reported**).[^index-echo-s2tt-gguf]
- Guidance: use Q8_0 or original precision when transcript quality matters; the underlying model can also repeat on some audio even at original precision, so inspect subtitles before using them as ground truth (**Reported**).[^index-echo-s2tt-gguf]

## Usage

- CLI S2TT uses `audiocpp_cli --task asr --family index_echo --model /path/to/Index-Echo-S2TT-GGUF/index-echo-s2tt-9b-q8_0.gguf --backend cuda --audio input.wav --request-option target_language=en --text-out subtitles.txt --log`; select the GGUF with `--model` (**Reported**).[^index-echo-s2tt-gguf]
- Set `target_language` to `en`, `es`, or `ja` (**Reported**).[^index-echo-s2tt-gguf]
- For long input, audio.cpp uses windowed inference and carries the previous five windows of transcript and translation as context; its default quiet-energy windowing is not identical to the official Python Silero VAD, so boundaries and output may differ (**Reported**).[^index-echo-s2tt-gguf]
- The card points to the [model guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/index_echo.md) for conversion and request options (**Reported**).[^index-echo-s2tt-gguf]

## C++ vs Python output comparison

- Protocol: 20 distinct Chinese clips from the public [FLEURS Chinese test split](https://huggingface.co/datasets/google/fleurs), with speech windows trimmed using the official Python Silero VAD, holding the input window fixed across implementations; source Chinese lines, not translations, were scored against FLEURS references; WER uses Jieba word segmentation and CER uses normalized characters (**Reported**).[^index-echo-s2tt-gguf]
- Scope disclaimer: this is a small diagnostic slice, **not** a broad model-quality benchmark; the WER/CER table measures source transcription only and does not measure translation quality (**Reported**).[^index-echo-s2tt-gguf]

| Checkpoint and setting | Completed clips | Python WER / CER | C++ WER / CER |
| --- | ---: | ---: | ---: |
| 2B original, greedy | 20/20 | 16.23% / 17.26% | 16.23% / 17.26% |
| 2B Q8_0, greedy | 20/20 | 16.23% / 17.26% | 9.55% / 12.12% |
| 2B Q4_K, greedy | 20/20 | 16.23% / 17.26% | 9.07% / 11.87% |
| 9B original, greedy | 19/20 | 7.77% / 11.02% | 8.27% / 11.28% |
| 9B Q8_0, greedy | 19/20 | 7.77% / 11.02% | 8.27% / 11.41% |

Table values are source-reported measurements as listed in the card's WER/CER table (**Reported**).[^index-echo-s2tt-gguf]

- Clip `zh_016` caused repetition for both Python 9B and C++ 9B variants and is excluded from their scores (**Reported**).[^index-echo-s2tt-gguf]
- With BF16 decoder activation rounding, C++ 2B original follows Python's five-cue output on `zh_000`, including its repeated ending; the lower Q8_0/Q4_K WER is mostly due to those variants ending after two cues on that clip and is not evidence of better transcription quality (**Reported**).[^index-echo-s2tt-gguf]
- Saved-subtitle comparison method: the 2B original row uses all 20 clips, the 2B quantized rows exclude `zh_000`, and all 9B rows exclude `zh_016`; each pair has the same cue count and is matched in order; text agreement ignores case, spaces, and punctuation; timestamp agreement counts start and end points within 0.1 seconds (**Reported**).[^index-echo-s2tt-gguf]

| C++ package vs official Python | Source cues identical | Translation cues identical | Timestamp points within 0.1 s |
| --- | ---: | ---: | ---: |
| 2B original | 52/52 | 49/52 | 103/104 |
| 2B Q8_0 | 47/47 | 42/47 | 93/94 |
| 2B Q4_K | 41/47 | 26/47 | 89/94 |
| 9B original | 45/48 | 42/48 | 94/96 |
| 9B Q8_0 | 47/48 | 42/48 | 96/96 |

Table values are source-reported agreement counts as listed in the card's cue-agreement table (**Reported**).[^index-echo-s2tt-gguf]

- Interpretation: these are output-agreement checks, not an independent translation-quality score or a claim of byte-identical parity; with the same VAD-trimmed inputs and greedy decoding, the 2B original package's 52/52 matching source cues and 103/104 close timestamp endpoints provide strong evidence that the main model math and decoding logic agree with Python, while its translations still differ in 3/52 cues, so this does not establish identical intermediate calculations; in particular, 2B Q4_K's similar source WER hides more translation changes (**Reported**).[^index-echo-s2tt-gguf]
- For 9B original and the `zh_004` test case, Python keeps the second phrase in one cue while C++ splits it into two; the largest timestamp difference reflects that boundary shift, not missing audio (**Reported**).[^index-echo-s2tt-gguf]

## Ordinary CUDA performance

- Test conditions: NVIDIA RTX 5090 with audio.cpp Debug build and official PyTorch inference; one 6.2-second request warmed the loaded model, followed by **one 180.3-second request**; the long WAV concatenates the 20 distinct Chinese FLEURS speech clips above and is a long-form workload, not a natural continuous recording (**Reported**).[^index-echo-s2tt-gguf]
- The table times only that second, long request, excluding model loading and warmup; RTF is its wall time divided by 180.3 seconds; C++ uses quiet-energy windowing while official Python uses Silero VAD, so window boundaries and generated cue counts are not identical (**Reported**).[^index-echo-s2tt-gguf]
- Python used its packaged default BF16 loading; C++ used each GGUF's stored weight type, with original-precision packages also rounding decoder activations to BF16 while quantized packages retain their existing execution path; neither run forced TF32 or used parity-only controls; both used greedy decoding (**Reported**).[^index-echo-s2tt-gguf]
- Peak VRAM was sampled with `nvidia-smi` every 50 ms across loading, warmup, and the long request, with no other GPU process running; it is device memory used, not just the PyTorch allocator's tensor count (**Reported**).[^index-echo-s2tt-gguf]

| Path | Long request wall | RTF | Peak VRAM |
| --- | ---: | ---: | ---: |
| Official Python 2B | 29.5 s | 0.164 | 7,138 MiB |
| audio.cpp 2B original | 9.56 s | 0.053 | 7,818 MiB |
| audio.cpp 2B Q8_0 | 7.12 s | 0.039 | 5,987 MiB |
| audio.cpp 2B Q4_K | 6.44 s | 0.036 | 5,120 MiB |
| Official Python 9B | 40.9 s | 0.227 | 20,632 MiB |
| audio.cpp 9B original | 32.46 s | 0.180 | 21,781 MiB |
| audio.cpp 9B Q8_0 | 20.94 s | 0.116 | 13,996 MiB |

Table values are source-reported measurements as listed in the card's performance table (**Reported**).[^index-echo-s2tt-gguf]

- All completed C++ runs produced subtitle cues through approximately 03:00; these figures describe this input and machine, not a general latency or accuracy guarantee (**Reported**).[^index-echo-s2tt-gguf]

## License

- The weights retain the upstream Apache-2.0 license; conversion does not replace the upstream license terms (**Reported**).[^index-echo-s2tt-gguf]

## Coverage and limits

- Source inspected statically only; no commands executed, no GGUFs loaded, and no WER/CER, cue-agreement, or performance figures reproduced (**Synthesis**).[^index-echo-s2tt-gguf]
- Referenced local artifacts (the five GGUF files and `LICENSE`) were not present in `raw/` and were not inspected; linked external pages (audio.cpp repository, upstream IndexTeam 2B/9B checkpoint trees, FLEURS dataset, audio.cpp model guide) were not fetched (**Synthesis**).[^index-echo-s2tt-gguf]
- All parity figures, quantization characterizations, performance measurements, and quality guidance are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `ml` domain rule (**Synthesis**).[^index-echo-s2tt-gguf]

[^index-echo-s2tt-gguf]: [Index-Echo-S2TT GGUF](../raw/Index-Echo-S2TT-GGUF.md) — locators: frontmatter (`license`, `base_model`, `library_name`, `pipeline_tag`, `tags`); title plus intro paragraphs (audio.cpp target, S2TT-only scope, 9B/quantized-quality note, same-C++-path / 24-layer vs 32-layer / tied-vs-separate-head architecture note); section `Upstream and Packages` (2B `72fd8bd…` and 9B `05f86cb…` checkpoint revisions, embedded audio-tower/connector/decoder/tokenizer/config/spec contents, vision-weights exclusion, 5-row file/size/recommendation table); paragraphs `9B Q4_K is not provided` and underlying-model repetition guidance; section `C++ vs Python: Output Comparison` (20-clip FLEURS + Silero-VAD-trimmed protocol, Jieba-WER / normalized-character-CER scoring, diagnostic-slice disclaimer, 5-row WER/CER table, `zh_016` exclusion, `zh_000` five-cue vs two-cue note, cue-count/matching/0.1-s method paragraph, 5-row cue-agreement table, agreement-vs-quality interpretation, `zh_004` cue-split note); section `Ordinary CUDA Performance` (RTX 5090 Debug-build/PyTorch setup, 6.2-s warmup + 180.3-s concatenated-FLEURS request, wall-only/RTF/VAD-vs-quiet-energy note, BF16-loading/weight-type/TF32/greedy note, 50-ms `nvidia-smi` VRAM note, 7-row wall/RTF/VRAM table, 03:00-cues and no-general-guarantee note); section `Usage` (CLI code fence with `--task asr --family index_echo --model --backend cuda --audio --request-option target_language --text-out --log`, `en`/`es`/`ja` paragraph, five-window context + windowing-difference paragraph, model-guide link); section `License` (Apache-2.0 retention paragraph). Linked model-guide, checkpoint, and dataset URLs have no locator available in `raw/` (external pages not fetched).
