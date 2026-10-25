---
type: Concept
title: Granite Speech 5.0 470M TurboCTC
description: IBM 470M-parameter 7-language offline Conformer-CTC ASR model (multilingual since 2026-10-21) with 8x temporal downsampling, greedy non-autoregressive decoding, native punctuation, and Transformers, MLX-audio, plus transcribe.cpp GGUF edge runtimes.
tags: [stt, asr, multilingual, conformer, ctc, edge-deployment, punctuation]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-25T10:40:00Z }
stale_after: 2027-10-06
sources:
  - id: granite-turboctc-card-ml
    resource: ../raw/ibm-granite-granite-speech-5.0-470m-turboctc.md
    kind: documentation
    title: Granite-Speech-5.0-470M-TurboCTC model card, multilingual revision (2026-10-21)
  - id: granite-turboctc-card
    resource: ../raw/granite-speech-5.0-470m-turboctc.md
    kind: documentation
    title: Granite-Speech-5.0-470M-TurboCTC model card
  - id: granite-2b-card
    resource: ../raw/ibm-granite-granite-speech-5.0-2b.md
    kind: documentation
    title: granite-speech-5.0-2b model card
---

Granite Speech 5.0 470M TurboCTC (`ibm-granite/granite-speech-5.0-470m-turboctc`) is IBM's compact ~470M-parameter offline ASR model, multilingual since the October 21, 2026 revision (English, French, German, Spanish, Portuguese, Italian, Japanese, with native punctuation and capitalization). It pairs a Conformer acoustic encoder (block self-attention, self-conditioning, 8x temporal downsampling) with a 16,384-unit multilingual BPE CTC head decoded non-autoregressively and greedily, targeting low-latency/high-throughput enterprise transcription on laptops, smartphones, and other edge devices (**Reported**).[^granite-turboctc-card-ml][^granite-turboctc-card]

## Identity and release

- Hugging Face ID `ibm-granite/granite-speech-5.0-470m-turboctc`; the multilingual capture's frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: transformers`, languages `multilingual` plus `en, fr, de, es, pt, it, ja`, and license Apache-2.0 (**Observed** by static inspection).[^granite-turboctc-card-ml]
- Release history: English-only release August 25, 2026; multilingual 5.0 TurboCTC October 21, 2026; the card names revision `947f59a` as the previous English-only release it replaces (**Reported**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Supported languages are English, French, German, Spanish, Portuguese, Italian and Japanese; intended use is accurate low-latency/high-throughput multilingual speech-to-text transcription in enterprise applications (**Reported**).[^granite-turboctc-card-ml]
- Upstream pointers named in the multilingual card: technical report arXiv:2609.20104, two IBM Hugging Face blog posts (the 5.0 family post and the TurboCTC post), a custom-data finetuning notebook, and IBM Granite docs and learning resources — none fetched in this ingest (**Reported**, with unfetched-pointer limit).[^granite-turboctc-card-ml]

## Multilingual 5.0 update

- The October 21, 2026 revision adds six languages and native punctuation and capitalization while keeping the encoder and CTC training recipe, so the architecture is "unchanged from the original English-only release, apart from the multilingual output vocabulary" (**Reported**).[^granite-turboctc-card-ml]
- The card claims the multilingual update also *improves* average English WER to 5.51% from 5.78% for the English-only release, i.e. adding languages did not cost English accuracy (**Reported**).[^granite-turboctc-card-ml]
- For Japanese (absent from the Open ASR multilingual benchmark set) the card reports CER on CSJ eval1, CommonVoice-17 and FLEURS and claims the 470M model outperforms the 2B-parameter [Granite Speech 5.0 2B](granite-speech-5.0-2b.md) on all three test sets — a size-class argument for the CTC model, stated only as a claim with no numeric CER in the card text (**Reported**).[^granite-turboctc-card-ml][^granite-2b-card]
- Every benchmark and multilingual-coverage chart in this revision is referenced through relative `assets/…png` paths that are not part of the `raw/` capture, so no per-set WER, CER or RTFx value can be read from the capture (**Observed** by static inspection).[^granite-turboctc-card-ml]

## Architecture

- 16 Conformer blocks trained with Connectionist Temporal Classification (CTC) and a 16,384-multilingual-BPE classification head; inference is non-autoregressive greedy decoding (**Reported**).[^granite-turboctc-card-ml]
- Temporal subsampling by 8x reduces frame rate from 100 Hz to 12.5 Hz: first by stacking and skipping consecutive log-mel plus delta frames (2x), then strided convolutions and pooled residuals in the first two Conformer blocks (4x) (**Reported**).[^granite-turboctc-card]
- Encoder uses block self-attention with 128-frame blocks and self-conditioned CTC from the middle layer (**Reported**).[^granite-turboctc-card]
- Configuration table (**Reported**):[^granite-turboctc-card]

| Configuration parameter | Value |
| --- | --- |
| Input dimension | 320 (80 logmels + 80 deltas) x 2 |
| Nb. of layers | 16 |
| Hidden dimension | 1024 |
| Nb. of attention heads | 8 |
| Attention head size | 128 |
| Attention block size | 128 |
| Convolution kernel size | 7 |
| Output dimension (multilingual BPE) | 16384 |

## Training data

- Total claimed is approximately 153,000 hours of multilingual audio from public corpora plus synthetic data; the 23 itemized rows sum to 152,828 hours, so the headline figure reconciles with the table (arithmetic **Observed**; per-row values **Reported**).[^granite-turboctc-card-ml]
- English remains the bulk of the mix: MLS English subset 31,640 h, LibriHeavy Large 45,750 h, VoxPopuli Granary 23,730 h, YODAS Granary (fillers removed) 16,220 h, CommonVoice-17 5,660 h (shared across the seven languages), LibriSpeech-PC 950 h, YODAS 1,230 h, AMI 150 h, Earnings-22 105 h (**Reported**).[^granite-turboctc-card-ml]
- The non-English rows are small: MLS De/Es/Fr/It/Pt 3,890 h, VoxPopuli En/De/Es/Fr/It 1,170 h, YODAS Granary Es 2,290 / Fr 1,650 / De 2,130 / Pt 1,170 / It 770 h, and Japanese YODAS 1,420 h plus filtered ReazonSpeech 8,130 h (**Reported**; the imbalance is **Synthesis**).[^granite-turboctc-card-ml]
- Synthetic additions are now English-focused: 2,500 h of overlapped-speech mixtures built from AMI, CommonVoice-17 and VoxPopuli; 240 h of written-form utterances (numbers, codes, URLs) at 16 kHz and 8 kHz; 130 h of CommonVoice-17 Japanese paraphrase TTS; and 1,860 h of Japanese text read by an internal Granite-text TTS voice (**Reported**).[^granite-turboctc-card-ml]
- 43 h of MUSAN noise and music are included with empty targets, i.e. non-speech robustness training rather than a speech corpus (**Reported**; interpretation **Synthesis**).[^granite-turboctc-card-ml]
- No dataset revision pins, split definitions, filtering rules, language-balance targets, or consent/quality notes are stated in the card; the earlier English-only capture's 7-row table (57,710 h plus 2,000/500/240 h synthetic) describes the superseded mix (**Observed** by static inspection).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Infrastructure: trained on IBM's Blue Vela cluster (NVIDIA H100 GPUs); the multilingual revision completed in 24 days on 8 H100 GPUs, against 10 days for the English-only release. The card gives no reason for the longer run, so the 2.4x wall-clock increase is recorded without attribution (**Reported**; ratio and unattributed cause **Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]

## Benchmarks

- The only numeric WER printed in either capture is the multilingual revision's average English figure: 5.51% against 5.78% for the English-only release (**Reported**).[^granite-turboctc-card-ml]
- That figure's protocol is narrower than a leaderboard entry: the Pareto caption calls it an average over 9 public English short-form test sets with official results as of October 21, 2026, and marks this model's point as an *unofficial* result because the leaderboard entry was still the English-only release at capture time (**Reported**; qualification **Synthesis**).[^granite-turboctc-card-ml]
- Because 5.51 is a 9-set average, it is not inserted as a row in the 8-set ranked table of [ASR/STT Model Survey](asr-stt-model-survey.md); treat it as a card claim comparable only to the same card's 5.78 baseline (**Synthesis**).[^granite-turboctc-card-ml]
- Multilingual evaluation is described but not quantified in text: FLEURS, CommonVoice and MLS for German, Spanish, French, Italian and Portuguese against each organization's best open-weights model, and Japanese CER on CSJ eval1, CommonVoice-17 and FLEURS (**Reported**).[^granite-turboctc-card-ml]
- No RTFx, hardware, batch size, per-test-set WER, or per-language table appears in the multilingual card's text; the superseded English-only capture likewise printed only plots, with its Open ASR results dated October 2, 2026 (RTFx on 1 H200) and its FFASR results August 25, 2026 (RTFx on 1 L4) (**Reported**; absence **Observed**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- All charts in both captures remain image-only and unfetched, so any ranking or per-language comparison must re-read the leaderboards rather than this page (**Synthesis**, with image-only limit).[^granite-turboctc-card-ml][^granite-turboctc-card]

## Inference and usage

- Transformers path is unchanged by the multilingual revision and requires `transformers>=5.16.0` plus `datasets`; load with `AutoProcessor.from_pretrained(model_id)` and `AutoModelForCTC.from_pretrained(model_id, device_map="auto")`, then `processor(...)` inputs moved to the model device and dtype, `model.generate(**inputs)`, and `processor.batch_decode(outputs, skip_special_tokens=True)`; the processor's `device` argument computes the log-mel front-end on the model's accelerator to save a host-to-device copy (**Reported**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Apple Silicon path uses `mlx-audio` 0.5.1 or later: `python -m mlx_audio.stt.generate --model ibm-granite/granite-speech-5.0-470m-turboctc --verbose --audio "audio.wav" --output-path "transcript"` (**Reported**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- The transcribe.cpp path appears only in the earlier English-only capture, which runs a pre-quantized GGUF with no Python at runtime on Metal, Vulkan, CUDA, ROCm, or CPU: fetch `granite-speech-5.0-470m-turboctc-Q8_0.gguf` from `handy-computer/granite-speech-5.0-470m-turboctc-gguf`, then `build/bin/transcribe-cli -q -m models/granite-speech-5.0-470m-turboctc-Q8_0.gguf samples/love-loss.wav` (**Reported**; the multilingual card drops this section, so multilingual support in that GGUF build is unverified).[^granite-turboctc-card][^granite-turboctc-card-ml]
- No usage command was executed and no transcription output reproduced in this ingest; whether the language of the audio is auto-detected or must be selected is not stated in either capture (**Synthesis**, with an unstated-language-selection limit).[^granite-turboctc-card-ml]

## Relationships

- Greedy-CTC offline peer [Parakeet CTC 0.6B](parakeet-ctc-0.6b.md): same offline non-autoregressive CTC family shape (Conformer/FastConformer encoder, greedy decoding without an external LM), differing in vendor (NVIDIA NeMo plus Suno versus IBM), tokenizer (SentencePiece-1024 versus 16,384 multilingual BPE), language coverage (English-only versus seven languages here) and output constraint (lowercase unpunctuated Parakeet versus native punctuation and capitalization here); compare their Open ASR tables when choosing a sub-1B offline CTC checkpoint (**Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Punctuated-throughput alternative [Parakeet TDT 0.6B V3](parakeet-tdt-0.6b-v3.md): both are now multilingual ~0.6B offline models with punctuation, differing in decoder (TDT with punctuation, capitalization and timestamps versus plain CTC here) and in language breadth (25 European languages versus seven here); prefer TDT V3 for European breadth and timestamps, TurboCTC for a minimal greedy-CTC edge footprint (**Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Edge-packaging catalog [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md): that catalog already lists the `Granite-Speech-5.0-470M-TurboCTC-GGUF` row (`granite5asr` family, Q8, Apache-2.0) while this page covers the upstream checkpoint (architecture, training mix, and Python/MLX/transcribe.cpp usage); read both when choosing between the source checkpoint and the audio.cpp GGUF build (**Synthesis**).[^granite-turboctc-card]
- Same-release sibling [Granite Speech 5.0 2B](granite-speech-5.0-2b.md): both are multilingual in the 5.0 family over overlapping European languages, but the 2B model is a speech-LLM with bidirectional translation, keyword biasing and an autoregressive granite-4.0-1b decoder at roughly four times the parameters, while this page's 470M model is greedy CTC. The multilingual card claims the 470M model beats the 2B on all three reported Japanese test sets, which argues for the smaller checkpoint on latency and footprint at equal-or-better Japanese accuracy; that claim is unreproduced and the 2B card prints no comparable CER table (**Reported**; reading **Synthesis**).[^granite-turboctc-card-ml][^granite-2b-card]
- Served by [transcribe.cpp](transcribe-cpp.md): that page holds the Handy ggml runtime path (Q8_0 GGUF, Metal/Vulkan/CUDA/ROCm/CPU, `transcribe-cli`, catalog verification) while this page holds the checkpoint detail (**Synthesis**).[^granite-turboctc-card]

## Supersession

- The multilingual revision (released 2026-10-21) supersedes the English-only release (2026-08-25, revision `947f59a`) for the same checkpoint ID: same encoder and CTC head shape, new multilingual output vocabulary, new training mix at ~153,000 h, and native punctuation. Evidence is the multilingual card's own release note and its "previous English-only release" pointer.[^granite-turboctc-card-ml]
- Both captures stay declared because they are the evidence for different claims: the English-only capture is the only source for the transcribe.cpp GGUF route and the Open ASR/FFASR plot dates, while the multilingual capture is the only source for the language list, the 5.51% English average and the 153,000 h mix. This concept is not deprecated; only the model revision is replaced (**Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]

## Coverage and limits

- Both captures inspected statically only; no Transformers, mlx-audio, or transcribe.cpp install, no weight download, no audio transcribed, and no WER, CER or RTFx figure reproduced (**Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Reconciliation of the two captures: this concept already declared the English-only card, so the multilingual file is not a new source package but a later revision of the same model card. Field-level differences are the frontmatter language list, a new multilingual badge block, the training table (7 rows to 23), the release date and supported-language list, the intended-use wording, the added English-improvement and Japanese-CER text claims, relative `assets/` image paths replacing absolute CDN URLs, and the removal of the transcribe.cpp usage section; encoder, configuration table, tokenizer size and both Python/MLX recipes are otherwise unchanged (**Observed** by static comparison).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Referenced but unfetched and absent from `raw/`: every benchmark and coverage chart in both captures (now relative `assets/…png` paths), both Conformer-block diagrams, the arXiv technical report, both blog posts, the finetuning notebook, IBM Granite docs pages, all 23 linked training-dataset pages, and the handy-computer GGUF repository (**Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Limit on the supersession: the multilingual card names revision `947f59a` as the previous English-only release, but neither capture prints its own commit hash, so the earlier capture is identified with that revision only by matching its English-only content and is not byte-verified against the git tree (**Observed**; identity is **Synthesis**).[^granite-turboctc-card-ml][^granite-turboctc-card]
- Open gaps for the voice loop: no streaming or chunked-inference mode is described, no latency or first-token figure is printed, no language-ID or per-utterance language-selection control is documented, and no Vietnamese, Chinese or code-switching evidence exists, so this model stays a non-candidate for Vietnamese pipelines despite now being multilingual (**Synthesis**).[^granite-turboctc-card-ml]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^granite-turboctc-card-ml]

- Sibling card [Granite-Speech-5.0-2B](../raw/ibm-granite-granite-speech-5.0-2b.md) was inspected only to support the same-release relationship edge above; its architecture, data, and benchmark content is compiled on [Granite Speech 5.0 2B](granite-speech-5.0-2b.md) and is not re-synthesized here (**Observed**).[^granite-2b-card]

[^granite-2b-card]: [Granite-Speech-5.0-2B model card](../raw/ibm-granite-granite-speech-5.0-2b.md) — locators: Model Summary (2B multilingual ASR plus bidirectional AST, 390,000 h, 4.1-2b comparison bullets); Model Architecture items (1)-(3) (CTC Conformer encoder, q-former projector, granite-4.0-1b-base LoRA decoder); Evaluations (Open ASR and FFASR plots only, no numeric table, no RTFx anywhere in the card).
[^granite-turboctc-card-ml]: [Granite-Speech-5.0-470M-TurboCTC, multilingual revision](../raw/ibm-granite-granite-speech-5.0-470m-turboctc.md) — locators: header badges (apache-2.0; languages multilingual, en, fr, de, es, pt, it, ja; automatic-speech-recognition; transformers); October 21 2026 release badge block (7 languages, native punctuation and capitalization, 5.51% vs 5.78% English WER, previous release revision 947f59a); Model Summary (~470M, language list, 16,384 multilingual BPE head, ~153,000 h, CTC with non-autoregressive greedy inference, punctuated and capitalized output); Evaluations (English improvement paragraph; Open ASR multilingual FLEURS/CommonVoice/MLS comparison; Japanese CER on CSJ eval1, CommonVoice-17 and FLEURS versus granite-speech-5.0-2b; Pareto caption stating an average over 9 public test sets, official results as of October 21 2026, unofficial orange marker); Release Date (Oct 21 2026, original English-only Aug 25 2026); Supported Languages (En, Fr, De, Es, Pt, It, Ja); Intended Use (multilingual STT); Usage (transformers>=5.16.0 fence and mlx-audio>=0.5.1 fence only, no transcribe.cpp section); Model Architecture (unchanged apart from multilingual output vocabulary; 16 conformer blocks, 8x subsampling 100 Hz to 12.5 Hz, 128-frame block attention, mid-layer self-conditioned CTC; 8-row configuration table labelling the head multilingual BPE); Training Data (23-row table summing to 152,828 h, incl. CommonVoice-17 5,660 / MLS English 31,640 / MLS De-Es-Fr-It-Pt 3,890 / LibriSpeech-PC 950 / LibriHeavy 45,750 / VoxPopuli 1,170 / VoxPopuli Granary 23,730 / YODAS English 1,230 / YODAS Granary En 16,220, Es 2,290, Fr 1,650, De 2,130, Pt 1,170, It 770 / AMI 150 / Earnings-22 105 / YODAS Japanese 1,420 / ReazonSpeech 8,130 / synthetic mixtures 2,500 / written-form TTS 240 / Japanese paraphrase TTS 130 / Granite-text Japanese TTS 1,860 / MUSAN 43); Infrastructure (Blue Vela H100, 24 days on 8 H100); Resources (arxiv 2609.20104, granite-speech-5 family blog, turboctc blog, finetune notebook, Granite docs).
[^granite-turboctc-card]: [Granite-Speech-5.0-470M-TurboCTC](../raw/granite-speech-5.0-470m-turboctc.md) — locators: header badges (license apache-2.0, language en, pipeline automatic-speech-recognition, library transformers); Model Summary (470M params, edge deployment, conformer encoder with block self-attention/self-conditioning/temporal downsampling, 16,384 BPE head, ~60,000 h English, CTC training, non-autoregressive greedy inference); Evaluations (Open ASR Leaderboard plots, official results Oct 2 2026 RTFx on 1 H200; FFASR plots, official results Aug 25 2026 RTFx on 1 L4); Release Date Aug 25 2026; License Apache 2.0; Supported Languages English; Intended Use (enterprise low-latency/high-throughput STT); Usage (transformers>=5.16.0 fence with AutoModelForCTC/AutoProcessor/device log-mel/generate/batch_decode; mlx-audio>=0.5.1 fence; transcribe.cpp clone/build/hf-download/Q8_0/transcribe-cli fences); Model Architecture (16 conformer blocks, 8x subsampling 100 Hz to 12.5 Hz via 2x stacking/skipping plus 4x strided-conv/pooled-residual, 128-frame block attention, mid-layer self-conditioned CTC; 8-row configuration table; conformer-block diagram); Training Data (7-row dataset table CommonVoice-17 2500 / MLS 44600 / Librispeech 960 / VoxPopuli 500 / YODAS 8900 / AMI 150 / Earnings-22 100; three synthetic sets 2000 h + 500 h concatenations + 240 h gpt-oss-120b/20b plus StyleTTS2 numerics); Infrastructure (Blue Vela H100 cluster, 10 days on 8 H100); Resources (arxiv 2609.20104, blog, finetune notebook, Granite docs links); Citation bibtex.
