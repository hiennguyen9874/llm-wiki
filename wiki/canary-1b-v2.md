---
type: Concept
title: Canary-1b-v2
description: NVIDIA NeMo 978M-parameter multitask ASR and speech-translation model covering 25 European languages with punctuation, timestamps, and published FLEURS, CoVoST2, MLS, and Open ASR Leaderboard benchmarks.
tags: [stt, asr, speech-translation, multilingual]
status: stable
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-06T00:00:00Z }
stale_after: 2027-10-06
sources:
  - id: canary-1b-v2-card
    resource: ../raw/canary-1b-v2.md
    kind: documentation
    title: Canary-1b-v2 model card
---

Canary-1b-v2 (`nvidia/canary-1b-v2`) is NVIDIA NeMo team's 978M-parameter encoder-decoder speech model for transcription and bidirectional speech translation across 25 European languages, with automatic punctuation and capitalization plus word/segment timestamps for ASR and segment timestamps for translation, released under CC-BY-4.0 and reported as state-of-the-art among similar-size models with quality comparable to 3x larger models at up to 10x speed (**Reported**).[^canary-1b-v2-card]

## Model identity and lineage

- Card title is `Canary-1b-v2`; Hugging Face release date is 08/14/2025; license is CC-BY-4.0; deployment geography is Global; intended use covers conversational AI, voice assistants, transcription, subtitles, and voice analytics for developers, researchers, academics, and industry (**Reported**).[^canary-1b-v2-card]
- Frontmatter declares `pipeline_tag: automatic-speech-recognition`, `library_name: nemo`, and tags including `automatic-speech-recognition`, `automatic-speech-translation`, `FastConformer`, `Conformer`, `Transformer`, `NeMo`, `pytorch`, and `hf-asr-leaderboard`; training-data frontmatter names `nvidia/Granary` and `nvidia/nemo-asr-set-3.0` (**Observed** by static inspection).[^canary-1b-v2-card]
- Scaled/enhanced Canary-family successor expanding from 4 languages in `canary-1b` / `canary-1b-flash` to 21 additional languages (25 total); first NeMo-team model to leverage the full Granary dataset; technical report is `Canary-1b-v2 Technical Report` (arXiv 2509.14128); companion pointers are the NeMo multitask-speech tutorial, NeMo repository, and Hugging Face demo space (**Reported**).[^canary-1b-v2-card]

## Supported languages and tasks

- 25 languages: Bulgarian (bg), Croatian (hr), Czech (cs), Danish (da), Dutch (nl), English (en), Estonian (et), Finnish (fi), French (fr), German (de), Greek (el), Hungarian (hu), Italian (it), Latvian (lv), Lithuanian (lt), Maltese (mt), Polish (pl), Portuguese (pt), Romanian (ro), Slovak (sk), Slovenian (sl), Spanish (es), Swedish (sv), Russian (ru), Ukrainian (uk) (**Reported**).[^canary-1b-v2-card]
- Three task directions: ASR transcription in all 25 languages; speech translation from 24 non-English languages to English (X->En); speech translation from English to 24 languages (En->X) (**Reported**).[^canary-1b-v2-card]
- Output includes punctuation and capitalization; ASR supports word-level and segment-level timestamps; translated outputs support segment-level timestamps only, recommended as the intuitive alignment for translation (**Reported**).[^canary-1b-v2-card]

## Architecture and I/O

- Encoder-decoder with FastConformer encoder and Transformer decoder guided by task tokens such as `<source language>` and `<target language>`; unified SentencePiece tokenizer with 16,384 tokens across all 25 languages; 32 encoder layers plus 8 decoder layers totaling 978M parameters (**Reported**).[^canary-1b-v2-card]
- Input is 16 kHz monochannel audio in `.wav`/`.flac` (1D audio signal); output is 1D text string with punctuation and capitalization; card notes NVIDIA GPU-accelerated training/inference via CUDA versus CPU-only (**Reported**).[^canary-1b-v2-card]
- Software/hardware envelope: runtime is NeMo main branch until NeMo 2.5; supported microarchitectures are Ampere, Hopper, and Blackwell; preferred OS is Linux; minimum 6 GB RAM to load; test hardware lists A10, A100, A30, A5000, H100, L4, and L40 (**Reported**).[^canary-1b-v2-card]

## Training data and procedure

- 3-stage NeMo-toolkit procedure: initialized from a 4-language ASR model; Stage 1 trained 150,000 steps on X->En plus English ASR using 64 A100 GPUs; Stage 2 added 115,000 steps on the full ASR plus X->En plus En->X set; Stage 3 fine-tuned 10,000 steps on a language-balanced high-quality Granary plus NeMo ASR Set 3.0 subset; all stages weight languages and corpora with temperature sampling (tau = 0.5); training script is `examples/asr/speech_multitask/speech_to_text_aed.py` and tokenizer script is `scripts/tokenizers/process_asr_text_tokenizer.py` (**Reported**).[^canary-1b-v2-card]
- Training data combines Granary (improved pseudo-labels plus filtered YTC, MOSEL, and YODAS corpora; pseudo-labeling pipeline and paper arXiv 2505.13404 referenced) with in-house NeMo ASR Set 3.0 human-labeled transcriptions from MLS, Mozilla Common Voice v7.0, AMI (70 hrs), Fleurs, LibriSpeech (960 hrs), Fisher, National Speech Corpus Part 1, VCTK, and Europarl-ASR (**Reported**).[^canary-1b-v2-card]
- Total is 1.7M hours: ASR 660,000 hrs, X->En 360,000 hrs, En->X 690,000 hrs, non-speech 36,000 hrs; all transcripts carry punctuation and capitalization; collection and labeling are each described as Hybrid (Automated plus Human; Synthetic plus Human) (**Reported**).[^canary-1b-v2-card]

## Inference and usage

- NeMo path: `pip install -U nemo_toolkit['asr']` (latest PyTorch recommended), then `ASRModel.from_pretrained(model_name="nvidia/canary-1b-v2")`; transcribe with `transcribe([...], source_lang='en', target_lang='en')`; translate by setting `target_lang` (example `source_lang='en', target_lang='fr'`); long-form dynamic chunking with 1-second overlap is automatic for a single file or `batch_size=1` batches over 40 s (**Reported**).[^canary-1b-v2-card]
- Timestamps need NeMo main branch until NeMo 2.5: ASR uses `transcribe(..., timestamps=True)` yielding `timestamp['word']` and `timestamp['segment']`; translation yields only `timestamp['segment']`; omitting timestamps can save memory by repackaging the `.nemo` file without `timestamps_asr_model` files (**Reported**).[^canary-1b-v2-card]
- Transformers path (until an official release, install from source): `pipeline("automatic-speech-recognition", model="nvidia/canary-1b-v2")`; or `AutoProcessor` plus `AutoModelForSpeechSeq2Seq` with `apply_transcription_request(audio=..., source_language="en")` and optional `target_language` (example `de`), batch lists with per-item `target_language`, and a training form using `apply_chat_template(..., processor_kwargs={"output_labels": True})` with transcript in the assistant turn and padding masked (**Reported**).[^canary-1b-v2-card]

## Benchmarks

All numbers below are source assertions from the card; nothing was executed or reproduced for this wiki (**Synthesis**).[^canary-1b-v2-card]

- Aggregate ASR WER (lower better, excludes punctuation/capitalization errors): Fleurs 25-language average 8.40%, CoVoST2 13-language average 8.85%, MLS 6-language average 7.27% (**Reported**).[^canary-1b-v2-card]
- Hugging Face Open ASR Leaderboard (WER down): mean 7.15 at RTFx 749; AMI 16.01, GigaSpeech 10.82, LibriSpeech Clean 2.18, LibriSpeech Other 3.56, Earnings22 11.79, SPGISpeech 2.28, Tedlium 4.29, VoxPopuli 6.25 (**Reported**).[^canary-1b-v2-card]
- Aggregate AST (BLEU/COMET up): X->En Fleurs-24 COMET 79.30 / BLEU 29.08 and CoVoST-13 COMET 77.48 / BLEU 40.48; En->X Fleurs-24 COMET 84.56 / BLEU 29.4 and CoVoST-5 COMET 80.29 / BLEU 32.33 (**Reported**).[^canary-1b-v2-card]
- Noise robustness on LibriSpeech Clean with MUSAN music/noise (WER down): 2.18% at 100 dB, 2.29% at 10 dB, 2.80% at 5 dB, 5.08% at 0 dB, 19.38% at -5 dB; hallucination robustness is 134.7 characters per minute on the 48-hour MUSAN eval set (**Reported**).[^canary-1b-v2-card]
- Long-form WER down (excludes punctuation/capitalization errors): Earnings-22 13.78%, This American Life 9.87% (**Reported**).[^canary-1b-v2-card]
- Per-language extremes for triage (full tables live in the source frontmatter `model-index`): Fleurs ASR best is Spanish 2.90% and Italian 3.07%, worst is Maltese 18.31%, Slovenian 13.32%, and Hungarian 12.90%; CoVoST2 ASR best is Spanish 3.81%, worst is Estonian 18.28% and Ukrainian 18.15%; MLS ASR spans Spanish 2.94% to Dutch 11.27%; Fleurs X->En BLEU best is Portuguese->English 39.43 and German->English 36.03, worst is Polish->English 22.30; CoVoST2 X->En BLEU best is Portuguese->English 50.38 and Russian->English 48.78, worst is Estonian->English 25.52; Fleurs En->X BLEU best is English->Portuguese 44.75 and English->French 43.42, worst is English->Polish 17.98 and English->Hungarian 20.75 (**Reported**).[^canary-1b-v2-card]
- Evaluation notes: comparison figures use two settings — all supported languages (24, excluding Latvian because `seamless-m4t-v2-large`/`medium` lack it) and 6 common languages (en, fr, de, it, pt, es); Portuguese gaps may partly reflect European-Portuguese training data versus Brazilian-Portuguese benchmarks; ASR comparison figure excludes punctuation/capitalization errors (**Reported**).[^canary-1b-v2-card]

## Trust, ethics, and limits

- Ethical framing is NVIDIA Trustworthy AI shared responsibility plus Model Card++ explainability/bias/safety/privacy subcards and a security-vulnerability reporting link (**Reported**).[^canary-1b-v2-card]
- Stated bias posture: no participation considerations from adversely impacted groups and no mitigation measures; stated technical limits: transcripts/translations are not 100% accurate and vary by language pair, domain, accent, noise, speech type, and context; out-of-vocabulary words are unlikely to be recognized; not recommended for word-for-word or incomplete-sentence use (**Reported**).[^canary-1b-v2-card]
- Stated privacy/safety posture: no generatable personal data and no personal data used; provenance exists for all training datasets; labeling complies with privacy laws; externally sourced data cannot honor correction/removal requests; life-critical impact none; use restricted by CC-BY-4.0 with least-privilege dataset/model access (**Reported**).[^canary-1b-v2-card]

## Relationships

- Benchmarked alongside [Qwen3-ASR family](qwen3-asr-family.md), [Fun-ASR-MLT-Nano-2512](fun-asr-mlt-nano-2512.md), and [Fun-ASR-Nano-2512](fun-asr-nano-2512.md): cross-read those concepts when comparing multilingual ASR coverage and WER tables; Canary-1b-v2's differentiator in this wiki is joint ASR plus bidirectional X<->En speech translation over 25 European languages with published BLEU/COMET aggregates (**Synthesis**).[^canary-1b-v2-card]
- Compared with [Index-Echo S2TT GGUF](index-echo-s2tt-gguf.md): that concept covers Chinese-to-English/Spanish/Japanese speech translation packaging, while Canary-1b-v2 covers European-language X<->En translation natively; use both when scoping translation language pairs (**Synthesis**).[^canary-1b-v2-card]

## Coverage and limits

- Source inspected statically only; no NeMo or Transformers install, no model download, no audio transcribed, and no WER, BLEU, COMET, RTFx, SNR, hallucination, or long-form figure reproduced (**Synthesis**).[^canary-1b-v2-card]
- Referenced but unfetched and absent from `raw/`: `plots/asr.png`, `plots/x_en.png`, `plots/en_x.png`; Hugging Face model page, demo space, and Canary collection; arXiv 2509.14128 technical report; NeMo repository, multitask tutorial, training/tokenizer scripts, and NeMo-speech-data-processor Granary pipeline; Granary, MOSEL, YODAS, YouTube-Commons, MLS, Common Voice, AMI, Fleurs, LibriSpeech, Fisher, NSC, VCTK, Europarl-ASR, CoVoST2, Open ASR Leaderboard, Earnings-22, This American Life, and MUSAN datasets; NVIDIA Riva/NeMo/NIM portals and Model Card++ subcards; all install and inference fences are transcribed, not executed (**Synthesis**).[^canary-1b-v2-card]
- Full per-language WER/BLEU/COMET evidence is the source frontmatter `model-index` (25 Fleurs ASR, 6 MLS ASR, 13 CoVoST2 ASR, 24+11 Fleurs/CoVoST2 X->En, 24+5 Fleurs/CoVoST2 En->X entries); this concept keeps aggregates, leaderboard, robustness, long-form, and extremes for retrieval and points to the card for the complete matrix (**Synthesis**).[^canary-1b-v2-card]
- All capability, data-scale, procedure, compatibility, and accuracy claims are source assertions without independent verification in this wiki; model-release and benchmark figures carry `stale_after: 2027-10-06` per the `stt` domain rule (**Synthesis**).[^canary-1b-v2-card]

[^canary-1b-v2-card]: [Canary-1b-v2 model card](../raw/canary-1b-v2.md) — locators: frontmatter (`license`, `pipeline_tag`, `library_name`, `language` list, `datasets`, `metrics`, full `model-index` per-language WER/BLEU/COMET matrix); header intro (1B params, 25 languages, ASR plus En<->24 AST bullets, language list, demo link, commercial-use line); `License/Terms`, `Release Date` (08/14/2025), `Deployment Geography` (Global), `Use case`; `Key Features` (4-to-25 expansion, SOTA/3x-quality/10x-speed claim, PnC, word/segment timestamps incl. translation segments, CC BY 4.0, Granary-first claim, technical-report and NeMo-tutorial links); `Model Architecture` (FastConformer encoder plus Transformer Decoder, `<source/target language>` tokens, SentencePiece 16,384, 32 plus 8 layers, 978M params); `Input`/`Output` (16 kHz mono `.wav`/`.flac`, 1D text with PnC, GPU/CUDA note); `How to Use` (NeMo install, `from_pretrained`, transcribe/translate fences, timestamps fences plus main-branch and `.nemo`-repack notes; Transformers source install, pipeline/transcription/translation/batch/training fences); `Software Integration` (NeMo main-to-2.5, Ampere/Blackwell/Hopper, Linux, 6 GB RAM); `Training and Evaluation Datasets` (3-stage steps/GPUs, tau 0.5, script paths; Granary YTC/MOSEL/YODAS plus NeMo ASR Set 3.0 corpus list; 1.7M-hour split; hybrid collection/labeling; eval sets Fleurs/MLS/CoVoST/Leaderboard/Earnings-22/TAL/MUSAN); `Benchmark Results` (ASR aggregate table; HF Leaderboard table with RTFx 749 and mean 7.15; AST X->En and En->X COMET/BLEU tables; MUSAN SNR table; 134.7 chars/min hallucination row; Earnings-22 13.78% and TAL 9.87% long-form rows with chunking note); `Inference` engine/hardware list; `Ethical Considerations`/`Bias`/`Explainability`/`Privacy`/`Safety` tables; `References [1]-[16]`.
