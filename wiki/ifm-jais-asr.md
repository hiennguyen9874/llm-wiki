---
type: Concept
title: IFM Jais-ASR
description: IFM's Jais-3-based Arabic ASR model for MSA and 19 dialects with code-switching, diacritization, language and dialect identification, and explicit non-speech refusal, reporting 22.85% WER and 8.37% CER average on the Open Universal Arabic ASR Leaderboard.
tags: [stt, asr, arabic, multilingual, code-switching, diacritization]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T10:20:00Z }
stale_after: 2027-10-25
sources:
  - id: jais-asr-card
    resource: ../raw/IFM-Jais-ASR.md
    kind: documentation
    title: IFM Jais-ASR model card
---

`IFM/Jais-ASR` is IFM's open-weights Arabic speech recognition model, built on Jais-3, covering Modern Standard Arabic plus dialects from 19 Arab countries with natural code-switching into English, French, Spanish and Italian. It adds optional diacritization, built-in language/dialect identification, and an explicit `[IFM-NoTranscript]` refusal when audio has no speech, and ships Transformers and vLLM serving paths. IFM reports the best macro-average on the Open Universal Arabic ASR Leaderboard at 22.85% WER and 8.37% CER (**Reported**).[^jais-asr-card]

## Model identity and lineage

- Model id `IFM/Jais-ASR`; byline "IFM" (IFM Team in the card BibTeX); license Apache 2.0; frontmatter declares `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, and tags `jais`, `ifm`, `arabic`, `arabic-dialects`, `speech-to-text`, `code-switching`, `diacritization`, `language-identification`, `open-weights`, `custom_code` (**Observed** by static inspection).[^jais-asr-card]
- The prose states the model is "based on Jais-3-4B", but frontmatter declares no `base_model` or `base_model_relation`, unlike the Cohere cards that do (**Observed**); the lineage is therefore prose-only evidence here.[^jais-asr-card]
- Weight budget: bf16 weights are 11.4 GB and the card advises planning for roughly 12 GB of GPU memory (**Reported**). 11.4 GB at 2 bytes per parameter implies about 5.7B parameters, which does not reconcile with the "Jais-3-4B" base naming; the card prints no parameter count, so treat both "4B" and the implied ~5.7B as unresolved (**Observed** arithmetic, **Unverified** size).[^jais-asr-card]
- `custom_code` plus `trust_remote_code=True` in every snippet means the model requires remote repository code at load time; that code is not in `raw/` and was not inspected (**Observed**; risk **Unverified**).[^jais-asr-card]
- Quantized checkpoints are said to be published in the linked "Jais Speech" Hugging Face collection, which is unfetched, so no quantization scheme, size, or quality delta is recorded here (**Reported**; unverified).[^jais-asr-card]

## Capabilities and controls

- **Code-switching:** `code_switch=True` keeps English, French, Spanish or Italian spans in their original script alongside Arabic; the card motivates this with interviews and everyday conversation (**Reported**).[^jais-asr-card]
- **Diacritization:** `diacritics=True` adds Arabic vowel marks to the transcript; it can be combined with code-switching (**Reported**).[^jais-asr-card]
- **Language and dialect identification:** every transcript carries a recognized language or dialect label (for example `msa`, `EG`, `en`), so no separate identification model is needed for routing (**Reported**).[^jais-asr-card]
- **Non-speech handling:** on audio without speech (music, noise) the model emits `[IFM-NoTranscript]` with `refused=True` and post-processing returns an empty transcript instead of hallucinated text (**Reported**).[^jais-asr-card]
- **Faithfulness claims:** transcripts are said to avoid memorized boilerplate, repetition loops, and translating speech instead of transcribing it; no metric, test set, or measurement protocol is given for these claims, so they are vendor assertions only (**Reported**; **Unverified**).[^jais-asr-card]
- **Batch:** one call can transcribe files of different durations and sample rates (**Reported**).[^jais-asr-card]

## Language and dialect settings

- Automatic language/dialect detection is on by default. An explicit setting overrides it: `ar` accepts MSA and all 19 dialects, `msa` forces Modern Standard Arabic, and a dialect code such as `EG` forces that dialect; separate settings exist for `en`, `fr`, `es` and `it` (**Reported**).[^jais-asr-card]
- The 19 dialect codes are `DZ`, `BH`, `EG`, `AE`, `IQ`, `JO`, `KW`, `LB`, `LY`, `MR`, `MA`, `OM`, `PS`, `QA`, `SA`, `SD`, `SY`, `TN`, `YE` (**Reported**).[^jais-asr-card]
- The frontmatter `language` list has 20 codes — `ar`, `arb`, `arz`, `apd`, `ary`, `arq`, `aeb`, `ayl`, `mey`, `apc`, `acm`, `afb`, `ars`, `acw`, `acx`, `ayn`, `en`, `fr`, `es`, `it` — so it names only 16 Arabic entries for 19 advertised dialects and uses ISO-639-3 dialect codes that do not appear in the documented setting table (**Observed**; the mapping is unresolved).[^jais-asr-card]

## Benchmarks

All figures below are the card's leaderboard table; the card says Jais-ASR was scored with the leaderboard's own evaluation script, other open-weight scores were taken from the leaderboard, and the two commercial APIs were measured by IFM. Nothing was executed or reproduced for this wiki (**Synthesis**).[^jais-asr-card]

The leaderboard covers six public test sets spanning read speech, broadcast media, and conversational dialects in clean and noisy conditions; the average is a macro-average over those six sets (**Reported**).[^jais-asr-card]

| Model | Avg WER % ↓ | Avg CER % ↓ |
| --- | ---: | ---: |
| IFM Jais-ASR | **22.85** | **8.37** |
| Audar-ASR-V1-Turbo (open weights) | 23.17 | 9.23 |
| Speechmatics Melia 1 (commercial) | 23.51 | 10.62 |
| ElevenLabs Scribe v2 (commercial) | 24.54 | 9.96 |
| Cohere Transcribe Arabic 07-2026 (open weights) | 25.87 | 11.80 |
| omniASR-LLM-7B (open weights) | 28.32 | 12.52 |
| Qwen3-Omni-30B-A3B (open weights) | 30.71 | 13.67 |
| Qwen3-ASR-1.7B (open weights) | 33.36 | 12.33 |
| Voxtral-Small-24B (open weights) | 34.47 | 15.29 |

Per-set results for Jais-ASR, with the best cell in the card's table noted (**Reported** cells; best-cell reading **Observed**):[^jais-asr-card]

| Test set | WER % | CER % | Best in table |
| --- | ---: | ---: | --- |
| SADA (Saudi dialectal broadcast) | 30.85 | 14.33 | No — Audar-ASR-V1-Turbo 28.92 / 13.40 |
| Common Voice 18 (MSA read speech) | 8.56 | 2.70 | No — Melia 1 5.19 / 1.62 |
| MASC clean (MSA lectures) | 16.12 | 3.76 | Yes |
| MASC noisy (MSA lectures) | 25.44 | 7.51 | Yes |
| MGB-2 (MSA broadcast news) | 9.59 | 3.92 | Yes |
| Casablanca (8 dialects, conversational) | 46.56 | 18.02 | CER only — WER best is Melia 1 46.41 |
| Macro-average | 22.85 | 8.37 | Yes |

- The "lowest ... ahead of every open-weight model compared" highlight holds for the macro-average only: on SADA it trails Audar-ASR-V1-Turbo on both WER and CER, on Common Voice 18 it trails Melia 1 on both, and on Casablanca its WER is 0.15 points behind Melia 1 although its CER leads (**Synthesis** from the table cells).[^jais-asr-card]
- The commercial rows are IFM-measured rather than vendor-published, and the card gives no per-set protocol detail for them (hardware, batch, normalization, reference text), so the 0.66-point WER lead over Melia 1 is a vendor-run comparison (**Synthesis**).[^jais-asr-card]
- The Cohere Transcribe Arabic cells here (25.87 WER / 11.80 CER, SADA 37.47 / 23.53, Common Voice 5.82 / 1.62, MASC clean 19.60 / 6.45, MASC noisy 27.07 / 10.13, MGB-2 15.54 / 8.40, Casablanca 49.71 / 20.66) reproduce that model's own card verbatim, so the two captures corroborate each other even though the leaderboard order changed (**Observed** by comparison with [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md)).[^jais-asr-card]

## Inference and serving

- Transformers path: install `pip install 'transformers==5.16.1' accelerate soundfile soxr`, then either `pipeline("automatic-speech-recognition", model="IFM/Jais-ASR", trust_remote_code=True, device_map="auto", dtype=torch.bfloat16)` with `max_new_tokens=256`, or `AutoProcessor` + `AutoModelForCausalLM` for batches (**Reported**).[^jais-asr-card]
- The batch recipe sets `processor.tokenizer.padding_side = "left"`, builds the prompt with `processor.tokenizer.apply_chat_template([{"role": "user", "content": [{"type": "audio"}]}], tokenize=False, add_generation_prompt=True)`, passes `text=[prompt] * n` with the waveform list and its per-file `sampling_rate`, then calls `model.generate(..., do_sample=False, max_new_tokens=256)` and `processor.post_process_transcription(output, input_lengths=inputs["input_ids"].shape[1])`, which returns `text`, `language` and `refused` per item (**Reported**).[^jais-asr-card]
- `code_switch` and `diacritics` are passed as extra arguments to `apply_chat_template` (shown commented), and `language="EG"`-style overrides are passed to `generate` (also commented), so the exact keyword surface is demonstrated rather than documented (**Observed**).[^jais-asr-card]
- The processor resamples each recording from its own sample rate to 16 kHz; `max_new_tokens` must be raised for long recordings, and a result with `truncated=True` means generation stopped before the transcript was complete — the card documents no chunking, no length limit, and no long-form assembly (**Reported**; absence **Observed**).[^jais-asr-card]
- vLLM path: install `vllm==0.23.0` with `transformers==5.5.4` in a separate environment, fetch only `vllm_plugin/*` via `hf download IFM/Jais-ASR --include "vllm_plugin/*" --local-dir Jais-ASR`, `pip install ./Jais-ASR/vllm_plugin`, then `vllm serve IFM/Jais-ASR --trust-remote-code --reasoning-parser jais_asr_tag --max-model-len 2048`; transcription uses the OpenAI-compatible `POST /v1/audio/transcriptions` form endpoint with `file` and `model` (**Reported**).[^jais-asr-card]
- The two paths pin different Transformers versions (`5.16.1` for inference, `5.5.4` for vLLM), and the serving command requires a custom `--reasoning-parser jais_asr_tag`, so a single shared environment is not demonstrated (**Observed**).[^jais-asr-card]
- No RTFx, latency, throughput, concurrency, or VRAM figure beyond "about 12 GB GPU memory" is printed, and no streaming, partial-hypothesis, timestamp, or diarization interface appears anywhere in the card (**Observed** absence).[^jais-asr-card]

## Relationships

- Leaderboard successor to [Cohere Transcribe Arabic 07-2026](cohere-transcribe-arabic-07-2026.md): both report the same six-set Open Universal Arabic ASR Leaderboard, both are Apache-2.0 2–6B-class offline Arabic/dialect recognizers, and Jais-ASR now holds the macro-average lead at 22.85 / 8.37 against 25.87 / 11.80 while the Cohere model stays ahead on Common Voice 18 (5.82 / 1.62 against 8.56 / 2.70) — this is a newer leaderboard entry, not a supersession of the Cohere weights (**Synthesis**).[^jais-asr-card]
- Baseline column in the same table: [Qwen3-ASR family](qwen3-asr-family.md) (1.7B, 33.36 / 12.33), [Voxtral Small 24B 2507](voxtral-small-24b-2507.md) (34.47 / 15.29), and Qwen3-Omni-30B-A3B (30.71 / 13.67). Those models are multilingual and much larger or broader in scope, but they lose the Arabic macro-average; use them when non-Arabic coverage or streaming matters more than Arabic dialect accuracy (**Synthesis**).[^jais-asr-card]
- Streaming counterpart on a non-comparable suite: [Voxtral Mini 4B Realtime Arabic](voxtral-mini-4b-realtime-arabic.md) reports 8.82% average CER at 480 ms delay over seven Arabic benchmarks under MTNRA normalization; Jais-ASR documents no streaming clock at all, so choose between them on latency requirement first and never rank the two CER figures together (**Synthesis**).[^jais-asr-card]
- Capability peer: unlike the Cohere pair, Jais-ASR performs its own language/dialect identification and emits an explicit no-speech refusal, which removes a separate LID model and gives the voice loop a VAD-independent skip signal; both properties are card claims, not measured here (**Synthesis**).[^jais-asr-card]
- Catalogued in the [ASR/STT Model Survey](asr-stt-model-survey.md), which carries its row and the Arabic selection guidance (**Synthesis**).[^jais-asr-card]

## Contradictions and unresolved points

- The card's headline says Jais-ASR is "ahead of every open-weight model compared" on the leaderboard, while its own table shows Audar-ASR-V1-Turbo ahead on SADA and Melia 1 (commercial) ahead on Common Voice 18 and on Casablanca WER. Both readings are kept: the claim holds for the macro-average, not per subset (**Reported** claim; conflict **Observed** in the same table).[^jais-asr-card]
- Advertised coverage (19 dialects) versus declared `language` codes (16 Arabic entries) versus the documented setting table (`ar`, `msa`, seven non-Arabic-or-general codes, and 19 dialect codes) do not line up; no mapping between ISO-639-3 frontmatter codes and the country-style dialect codes is given (**Observed**; unresolved).[^jais-asr-card]
- "Based on Jais-3-4B" versus an 11.4 GB bf16 weight file that implies roughly 5.7B parameters; the card prints no parameter count, so neither figure can be confirmed from this capture (**Observed**; unresolved).[^jais-asr-card]

## Coverage and limits

- The single card capture (`raw/IFM-Jais-ASR.md`, 211 lines) was read in full and inspected statically; it prints no revision, commit hash, release date, or capture date, and its BibTeX carries only `year = 2026` (**Observed**).[^jais-asr-card]
- Not in `raw/` and uninspected: the `vllm_plugin/` source, remote modeling code loaded through `trust_remote_code`, the Jais Speech quantized collection, the benchmark figure asset `assets/jais-asr-benchmarks.png`, the Open Universal Arabic ASR Leaderboard repository and Space, the six evaluation datasets (SADA, Common Voice 18, MASC clean/noisy, MGB-2, Casablanca), and the Jais-3 base model card (**Synthesis**).[^jais-asr-card]
- No package was installed, no weights downloaded, no audio transcribed, and no WER, CER, latency, or memory figure reproduced; every capability and benchmark statement here is a vendor claim (**Synthesis**).[^jais-asr-card]
- The card documents no streaming, timestamps, diarization, long-form chunking, or hotword/context biasing; absence of documentation is not proof of absence in the weights, but nothing in the capture supports those capabilities (**Observed** absence).[^jais-asr-card]
- Model-release and benchmark details carry `stale_after: 2027-10-25` per the `stt` domain rule, because the leaderboard order moves with each new Arabic checkpoint (**Synthesis**).[^jais-asr-card]

[^jais-asr-card]: [IFM Jais-ASR model card](../raw/IFM-Jais-ASR.md) — locators: frontmatter (`license: apache-2.0`, `library_name`, `pipeline_tag`, 20-code `language` list, `tags` incl. `custom_code`); intro paragraph (Jais-3-4B base, 19 countries, code-switching into en/fr/es/it, 11.4 GB bf16); `Jais-ASR Highlights` (leaderboard 22.85 WER / 8.37 CER, ~12 GB GPU, vLLM plugin); `Benchmark Results` intro and `leaderboard` table (WER and CER blocks: Average, SADA, Common Voice 18, MASC clean, MASC noisy, MGB-2, Casablanca for nine models) with the note that other open-weight scores come from the leaderboard and the two commercial APIs were measured by IFM; `Capabilities` bullets (`code_switch`, `diacritics`, language/dialect label, `[IFM-NoTranscript]` + `refused=True`, mixed-rate batch); `Language and Dialect Settings` table and 19-dialect code list; `Quickstart` install fence (`transformers==5.16.1`), `Transformers Pipeline` fence, `Batch Transcription` fence (`padding_side="left"`, `apply_chat_template`, `post_process_transcription`, `truncated`), TIP callout (16 kHz resampling, `max_new_tokens`); `Serving with vLLM` fences (`vllm==0.23.0`, `transformers==5.5.4`, `hf download --include "vllm_plugin/*"`, `--reasoning-parser jais_asr_tag`, `/v1/audio/transcriptions` curl); `Citation` BibTeX (IFM Team, 2026).
