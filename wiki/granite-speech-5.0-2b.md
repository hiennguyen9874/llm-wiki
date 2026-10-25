---
type: Concept
title: Granite Speech 5.0 2B
description: IBM 2B-parameter speech-LLM for multilingual ASR and bidirectional speech translation in English, French, German, Spanish, Portuguese, and Japanese, built from a CTC-trained Conformer encoder, a 10 Hz q-former projector, and a granite-4.0-1b-base LoRA decoder.
tags: [stt, asr, multilingual, speech-translation, conformer, speech-llm]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T02:38:02Z }
stale_after: 2027-10-25
sources:
  - id: granite-2b-card
    resource: ../raw/ibm-granite-granite-speech-5.0-2b.md
    kind: documentation
    title: granite-speech-5.0-2b model card
---

Granite Speech 5.0 2B (`ibm-granite/granite-speech-5.0-2b`) is IBM's 2B-parameter speech-language model for multilingual ASR and bidirectional speech translation covering English, French, German, Spanish, Portuguese, and Japanese, assembled by modality-aligning an intermediate checkpoint of `granite-4.0-1b-base` to speech through a 16-block CTC-trained Conformer encoder and a 5x q-former projector that feeds the LLM 10 Hz acoustic embeddings; it is Apache-2.0, autoregressive at inference, and documented as an offline transcription/translation engine with prompt-selected task behavior rather than a native streaming recognizer (**Reported**).[^granite-2b-card]

## Identity and release

- Repository `ibm-granite/granite-speech-5.0-2b`; frontmatter declares `license: apache-2.0`, `library_name: transformers`, `pipeline_tag: automatic-speech-recognition`, `base_model: ibm-granite/granite-4.0-1b-base`, and language tags `multilingual, en, fr, de, es, pt, ja` (**Observed** by static inspection).[^granite-2b-card]
- Release date October 20, 2026; license Apache 2.0; card BibTeX lists IBM Granite Speech Team, 2026 (**Reported**).[^granite-2b-card]
- Supported languages for ASR and X↔En translation are English, French, German, Spanish, Portuguese, and Japanese; intended use adds English→Italian and English→Mandarin as additional translation targets, so Italian and Mandarin appear only as AST outputs, not as ASR source languages (**Reported**; the asymmetry is **Synthesis** from the two lists).[^granite-2b-card]
- Successor to `granite-speech-4.1-2b` at the same parameter count; the card's stated deltas are higher English short-form accuracy, better noise/reverberation/distant-microphone robustness, input language-ID prompting, improved long-form and conversational translation, and a keyword list raised to 2,000 entries (**Reported**).[^granite-2b-card]
- Training scale is stated as 390,000 hours of public-corpus and synthetic audio for ASR and AST; the card's itemized table sums to 390,483 hours (**Synthesis**, arithmetic on the reported rows).[^granite-2b-card]
- Trained on IBM's Blue Vela H100 cluster; this model took 40 days (26 encoder days + 14 projector days) on 8 H100 GPUs (**Reported**).[^granite-2b-card]

## Architecture

- **Speech encoder:** 16 Conformer blocks trained with CTC and two classification heads — characters and BPE units — on the ASR-only subset with unpunctuated transcripts. The character vocabulary is the first 256 ASCII entries for the European languages plus a 92-character phonetic Katakana set for Japanese, which reconciles with the table's 348-way character output (**Reported**, with the 256 + 92 = 348 reconciliation as **Synthesis**). BPE units come from the granite 4.0 tokenizer (**Reported**).[^granite-2b-card]
- The CTC encoder uses block attention over 4-second audio blocks and self-conditioned CTC from the middle layer; that middle layer also supplies non-blank probabilities for frame-level posterior-weighted pooling with a window of 4 for BPE classification (**Reported**).[^granite-2b-card]
- Configuration table (**Reported**):[^granite-2b-card]

| Configuration parameter | Value |
| --- | --- |
| Input dimension | 160 (80 logmels x 2) |
| Nb. of layers | 16 |
| Hidden dimension | 1024 |
| Nb. of attention heads | 8 |
| Attention head size | 128 |
| Convolution kernel size | 15 |
| Output dimension (characters) | 348 |
| Output dimension (BPE) | 100353 |

- **Modality adapter:** a 2-layer window query transformer (q-former) over blocks of 15 1024-dimensional acoustic embeddings from the last Conformer block, downsampled 5x with 3 trainable queries per block per layer, giving 15 / 3 = 5 and confirming the stated factor (**Reported**; the division is **Synthesis**). Total temporal downsampling is 10x — 2x from the encoder plus 5x from the projector — producing a 10 Hz acoustic embedding rate for the LLM. Projector and LLM LoRA adapters were trained jointly (**Reported**).[^granite-2b-card]
- **Language model:** an intermediate `granite-4.0-1b-base` checkpoint with YaRN context extension to 16k positions, finetuned on the same corpora (**Reported**).[^granite-2b-card]
- The card states the encoder contributes 2x downsampling but the configuration table's only candidate mechanism is the 160-dimensional `80 logmels x 2` input; unlike the sibling TurboCTC card it names no frame-stacking or strided-convolution mechanism, so the 100 Hz → 50 Hz encoder step is not documented in detail (**Synthesis**, gap noted).[^granite-2b-card]
- Decoding is autoregressive over the LLM head. The card describes no streaming, chunked, or partial-hypothesis mode, and its block-attention description is stated as an encoder training/inference design rather than a controllable lookahead (**Reported** for the architecture; the streaming absence is **Synthesis** from the card's silence).[^granite-2b-card]

## Training data

Task-format subtotals below are **Synthesis** (arithmetic over the card's rows); every row value is **Reported**.[^granite-2b-card]

| Task format | Rows | Hours |
| --- | ---: | ---: |
| Raw (unpunctuated) ASR | 21 | 159,163 |
| Punctuated ASR | 7 | 80,420 |
| Contextual ASR (noisy previous-segment prompt) | 1 | 59,900 |
| Keyword-biased ASR | 2 | 23,600 |
| AST | 5 | 67,000 |
| Keyword-biased AST | 1 | 400 |
| **Total** | 37 | **390,483** |

- Public corpora named in the raw-ASR rows are CommonVoice-17 (5,500 h across en/de/es/fr/pt/ja), MLS (48,400 h), LibriSpeech (1,000 h), LibriHeavy Large (45,600 h), VoxPopuli (1,100 h), VoxPopuli Granary (24,000 h), AMI (150 h), YODAS English (9,100 h) and Japanese (1,400 h), YODAS Granary long-form up to 120 s (4,900 h), Earnings-22 (105 h), Switchboard (260 h), CallHome (18 h), Fisher (2,000 h), two Voicemail parts (15 h each), ReazonSpeech (3,300 h), plus augmented Japanese and written-form sets (**Reported**).[^granite-2b-card]
- Large parts of the same audio are counted again in other task rows: LibriHeavy appears as 45,600 h raw ASR and 45,800 h punctuated ASR, and CommonVoice-17, MLS, VoxPopuli, and Earnings-22 each appear in both a raw and a punctuated row. The 390k figure is therefore a sum over task formats, not unique audio hours (**Synthesis**).[^granite-2b-card]
- Contextual ASR is one 59,900-hour row (LibriHeavy, AMI, Switchboard, Fisher, CallHome English) built by adding noisy previous-segment context to the prompt; keyword-biased ASR is 7,100 h for CommonVoice-17/MLS/YODAS en/de/es/fr/pt and 16,500 h for CommonVoice-17/YODAS/ReazonSpeech Japanese, with keyword lists derived from the transcripts (**Reported**).[^granite-2b-card]
- Synthetic generation is used for Japanese ASR (9,600 h of Fineweb-2 Japanese read by Kokoro-82M TTS, 250 h of CommonVoice-17 Japanese paraphrase TTS), multi-speaker English (2,000 h of mixtures), and written-form English (450 h of TTS over numbers, abbreviations, punctuation) (**Reported**).[^granite-2b-card]
- AST supervision is largely synthetic: CommonVoice-17 X→En was translated with Granite-3 and Phi-4 (1,200 h), En→X with Phi-4 and MADLAD (6,100 h), punctuated variants of both directions (7,300 h), plus 43,400 h of pseudo-labeled translations of ASR transcripts and 9,000 h of YODAS Granary long-form translations (**Reported**).[^granite-2b-card]
- No dataset revision pins, split definitions, filtering rules, or consent notes are given for any row, and TTS-generated audio (Kokoro-82M) means part of the ASR training distribution is itself synthetic speech (**Observed** for the omissions; **Synthesis** for the distribution implication).[^granite-2b-card]

## Benchmarks

### Punctuation and capitalization

The only numeric results in the card are a PER / Cap-F1 table comparing 5.0-2b with 4.1-2b; PER is lower-better, Cap-F1 higher-better, and bold marks the better cell per row (**Reported**; per-row comparison counts below are **Synthesis**).[^granite-2b-card]

| Test set | PER 4.1-2b | PER 5.0-2b | Cap-F1 4.1-2b | Cap-F1 5.0-2b |
| --- | ---: | ---: | ---: | ---: |
| LScln | 25.70 | **23.20** | 89.71 | **90.16** |
| LSoth | 22.27 | **21.22** | 91.26 | **91.65** |
| VoxPopuli | 24.86 | **23.70** | **95.35** | 95.07 |
| Earnings-22 | 22.87 | **21.64** | **95.19** | 94.98 |
| CV-EN | **9.13** | 9.18 | 96.75 | **96.96** |
| CV-DE | 3.66 | **3.65** | 99.50 | **99.51** |
| CV-ES | 11.61 | **11.46** | **95.68** | 95.62 |
| CV-FR | **11.00** | 11.43 | **97.25** | 97.20 |
| CV-PT | 7.86 | **7.53** | **98.51** | 98.48 |

- 5.0-2b improves PER on 7 of 9 sets (all but CV-EN by 0.05 and CV-FR by 0.43) while Cap-F1 improves on only 4 of 9 (LScln +0.45, LSoth +0.39, CV-EN +0.21, CV-DE +0.01) and regresses on the other 5 by at most 0.28 points (**Synthesis**).[^granite-2b-card]
- Metrics follow the LibriSpeech-PC definitions, but the card computes Cap-F1 on Levenshtein-aligned matching word pairs rather than fully matching sentences, so these Cap-F1 values are not comparable to sentence-level LibriSpeech-PC numbers elsewhere (**Reported** for the method; **Synthesis** for the non-comparability).[^granite-2b-card]
- German is noted as the case where noun capitalization makes Cap-F1 99.51 possible; the deltas above are within the range a single test run could plausibly produce, but no variance, seed, or significance data is given (**Synthesis**).[^granite-2b-card]

### Image-only results (no numbers recorded)

- English ASR on Open ASR Leaderboard benchmarks, official results as of October 21, 2026, and noisy/reverberant speech on the FFASR leaderboard, official results as of October 18, 2026, are each a single embedded plot (`assets/granite-5.0-2b-vs-open-english.png`, `assets/granite-speech-5.0-2b-ffasr-wer.png`) with no numeric table in the card text and no local copy in `raw/` (**Reported** claim, unread limit).[^granite-2b-card]
- Multilingual CommonVoice WER, CoVoST X→En BLEU, FLEURS En→X BLEU, and keyword-biased F1 (with and without KWB, excluding common words) are likewise plots only (`assets/...wer-cv.png`, `...bleu-x-en.png`, `...bleu-en-x.png`, `...kwb-f1.png`) (**Reported**, unread).[^granite-2b-card]
- Consequently the card's headline claim of "higher transcription accuracy for English short-form ASR" and "increased robustness to noise, reverberation and distant microphone speech" versus 4.1-2b is not numerically supported by anything in the captured card; any WER comparison must re-read the two leaderboards and name the snapshot date (**Synthesis**).[^granite-2b-card]
- No RTFx, latency, memory, or throughput figure appears anywhere in the card, so no speed claim can be attached to this model from this source (**Observed** by static inspection).[^granite-2b-card]

## Safety and limitations

- The card's stated safety property: an unfamiliar or malformed prompt is ignored and the model falls back to plain transcription, which the card argues limits adversarial audio/prompt influence compared with models that interpret audio directly (**Reported**).[^granite-2b-card]
- That fallback is also an operational failure mode: a mis-typed task or language prompt silently degrades to default transcription instead of erroring, so a voice pipeline must verify prompt construction rather than trust a raised error (**Synthesis**).[^granite-2b-card]
- IBM recommends pairing the model with Granite Guardian for prompt/response risk detection; the card states that smaller models may be more susceptible to hallucination in generation scenarios and calls this an open research question (**Reported**).[^granite-2b-card]
- The card's own limitation paragraph is generic; it reports no per-language, per-accent, code-switching, or failure-mode evaluation, and no hallucination measurement (**Observed** by static inspection).[^granite-2b-card]

## Relationships

- Sibling in the same 5.0 release: [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) is the 470M Conformer-CTC edge model with greedy non-autoregressive decoding, English-only at release and multilingual over the same six European languages plus Japanese after its 2026-10-21 revision, while this page's 2B model is a speech-LLM with translation and keyword biasing at roughly 4x the parameters; the TurboCTC card claims its 470M model beats this one on all three reported Japanese test sets, which is the main size-class argument against the 2B and is unreproduced (**Reported**; reading **Synthesis**).[^granite-2b-card]
- Same 2B size band as [Cohere Transcribe 03-2026](cohere-transcribe-03-2026.md) (14 languages, no AST, per-set WER table) and [Canary-Qwen-2.5B](canary-qwen-2.5b.md) (English-only, 418 RTFx): both publish numeric WER/RTFx tables that this card does not, so a selection decision needs those figures verified independently before comparing (**Synthesis**).[^granite-2b-card]
- Competes in the multilingual LLM-ASR slot with [Qwen3-ASR family](qwen3-asr-family.md) and [Voxtral Mini 3B 2507](voxtral-mini-3b-2507.md); Granite's distinguishing documented feature is prompt-side language ID plus keyword lists up to 2,000 entries combined with bidirectional translation in one checkpoint (**Synthesis**).[^granite-2b-card]
- Catalogued for selection in [ASR/STT Model Survey](asr-stt-model-survey.md), which holds the cross-model comparison tables this page feeds.[^granite-2b-card]
- Prompt construction and runtime routes are on [Granite Speech 5.0 2B Prompting and Serving](granite-speech-5.0-2b-prompting-and-serving.md) (**Synthesis**).[^granite-2b-card]

## Coverage and limits

- Source inspected statically and read in full (457 lines); no weight download, no installation, no inference, and no benchmark reproduction (**Synthesis**).[^granite-2b-card]
- Referenced but absent from `raw/`: all seven benchmark plots, the blog post and IBM Granite docs pages, the six linked arXiv papers (2505.08699, 2603.11243, 2604.12398, 2604.22817, 2604.11269, 2603.08397), both Colab notebooks, every linked training-dataset page, and the `ibm-granite/granite-speech-5.0-2b-GGUF` repository (**Synthesis**).[^granite-2b-card]
- The sibling GGUF capture [`raw/ibm-granite-granite-speech-5.0-2b-GGUF.md`](../raw/ibm-granite-granite-speech-5.0-2b-GGUF.md) was inspected and excluded as duplicative: it is a stub that only restates Apache-2.0, `library_name: llama.cpp`, the `granite-5.0` tag, and `base_model: ibm-granite/granite-speech-5.0-2b` before deferring to this model card, so its only durable content is already carried by the llama.cpp section of this source (**Observed**).[^granite-2b-card]
- All capability, data-scale, architecture, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-25` per the `stt` domain rule (**Synthesis**).[^granite-2b-card]

[^granite-2b-card]: [Granite-Speech-5.0-2B model card](../raw/ibm-granite-granite-speech-5.0-2b.md) — locators: YAML frontmatter (license apache-2.0, languages multilingual/en/fr/de/es/pt/ja, base_model granite-4.0-1b-base, library transformers, pipeline automatic-speech-recognition); Model Summary (390,000 h, 4.1-2b comparison bullets, modality alignment); Evaluations (Open ASR plot dated Oct 21 2026, FFASR plot dated Oct 18 2026, CommonVoice/CoVoST/FLEURS plots, KWB F1 plot, PER and Cap-F1 table with 9 rows and the Levenshtein-alignment footnote); Release Date Oct 20 2026; License Apache 2.0; Supported Languages; Intended Use (English-to-Italian and English-to-Mandarin targets); Usage preamble (transformers>=4.52.1, ~2-minute segments, split with VAD); Model Architecture items (1) encoder with dual char/BPE CTC heads, 256 ASCII plus 92 Katakana, 4-second block attention, mid-layer self-conditioned CTC, window-4 posterior pooling, 8-row configuration table; (2) 2-layer window q-former, 15 embeddings / 3 queries, total 10x / 10 Hz, joint projector and LoRA training; (3) granite-4.0-1b-base with YaRN 16k; Training Data 37-row table with all hours and sources; Infrastructure (Blue Vela, 40 days, 26 encoder + 14 projector, 8 H100); Ethical Considerations and Limitations (prompt fallback, hallucination uncertainty, Granite Guardian); Resources (blog, six arXiv papers, two notebooks, Granite docs); Citation bibtex.
