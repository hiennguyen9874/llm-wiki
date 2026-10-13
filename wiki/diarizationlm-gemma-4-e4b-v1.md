---
type: Concept
title: DiarizationLM-Gemma-4-E4B-v1
description: Gemma 4 E4B-based LLM fine-tuned to post-process speaker-tagged ASR transcripts, with Apache-2.0 bf16 and Q4 GGUF files, vendor-reported WDER gains over a USM + turn-to-diarize baseline on four benchmark corpora, and no latency or non-English evidence.
tags: [vad, diarization, speaker-tagging, stt, llm, gemma, gguf, post-processing]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T04:15:00Z }
stale_after: 2027-10-13
sources:
  - id: diarizationlm-gemma4-card
    resource: ../raw/DiarizationLM-Gemma-4-E4B-v1.txt
    kind: documentation
    title: DiarizationLM-Gemma-4-E4B-v1 model card capture (google/DiarizationLM-Gemma-4-E4B-v1)
  - id: diarizationlm-readme
    resource: ../raw/DiarizationLM.md
    kind: code
    title: DiarizationLM README (google/speaker-id repository; no revision recorded)
---

DiarizationLM-Gemma-4-E4B-v1 is an LLM post-processor, not a diarizer: it takes an ASR hypothesis already marked with `<speaker:N>` tags and rewrites where speaker turns fall. The card frames the task as fixing lexical turn boundaries and backchannels (1–5 words) while keeping speaker identity across long monologues (6+ words). The card describes a LoRA fine-tune of the 4B-dense Gemma 4 E4B on 71,825 prompt–completion pairs drawn from Fisher, Callhome, ICSI, and AMI, shipped as bf16 safetensors plus Q4_K_M (recommended) and Q4_0 GGUF files (**Reported**).[^diarizationlm-gemma4-card] The card reports paired WDER reductions of 0.60–2.82 percentage points against a USM + turn-to-diarize baseline on all four test sets, and ahead of its 8B predecessor `DiarizationLM-8b-Fisher-v2` on Fisher and Callhome (**Reported**). Its cpWER significance claim is not supported by its own table; see [Contradictions](#contradictions).

## Identity and packaging

- Model: `google/DiarizationLM-Gemma-4-E4B-v1`, base `google/gemma-4-E4B`, `library_name: transformers`, `license: apache-2.0` in frontmatter; the card states it is "not an officially supported Google product" (**Reported**).[^diarizationlm-gemma4-card]
- Architecture: Gemma 4 E4B with 42 layers, hidden size 2560, hybrid 5:1 sliding-window and global attention, 262,144-token vocabulary, described as "4B dense parameters" (**Reported**).[^diarizationlm-gemma4-card]
- Files: `model.safetensors` in bf16 (~16.0 GB); `DiarizationLM-Gemma-4-E4B-v1-q4_k_m.gguf` (~5.30 GB, recommended) and `…-q4_0.gguf` (~5.15 GB, legacy) for `llama.cpp`, Ollama, and `llama-cpp-python`; tokenizer and config files (**Reported**).[^diarizationlm-gemma4-card]
- Size check: 16.0 GB in bf16 is about 8 billion 2-byte values, twice the stated 4B. The card does not explain the gap, so the memory footprint is **Unverified** (arithmetic **Observed**).
- Namespace: the card's code uses `google/…` (**Reported**).[^diarizationlm-gemma4-card] The library README's Hugging Face badge, its Gemma link, and its GGUF demo Space all sit under `diarizers-community/` (**Observed**).[^diarizationlm-readme] The two captures disagree on the repository owner, so the publisher of these weights stays unresolved; see [Contradictions](#contradictions).

## Training

- Objective: completion-only cross-entropy on `<prompt> --> <completion> [eod]` (**Reported**).[^diarizationlm-gemma4-card]
- Data: 51,063 Fisher and 20,762 combined Callhome, ICSI, and AMI pairs; prompts segmented at 4,000 characters (maximum 2,560 tokens) (**Reported**).[^diarizationlm-gemma4-card]
- Method: "Locality-Preserving Oracle Supervision" is named and described only by its turn-boundary and monologue behavior; how oracle targets are built is not defined in the card (**Reported**; construction **Unverified**).
- Optimization: 10,000 steps, global batch 8, AdamW (β1 0.9, β2 0.99), peak LR 1.5e-4 with 500-step linear warmup and cosine decay, on 8 TPU v5p chips (**Reported**).[^diarizationlm-gemma4-card]
- Adapter: LoRA rank 256 on q/k/v/o, gate/up/down, and per-layer input projections, merged into bf16 weights before GGUF quantization (**Reported**).[^diarizationlm-gemma4-card]
- Comparative claim: the card says 2-speaker telephone-only models and naive multi-domain SFT drift in speaker identity across 4+ speaker meetings. The capture gives no evidence for the drift claim (**Reported**; **Unverified**).

## Benchmarks

Micro-averaged scores with 95% bootstrap intervals (10,000 conversation-level resamples), scored with Hungarian matching via `diarizationlm.compute_metrics_on_json_dict` (**Reported**).[^diarizationlm-gemma4-card]

| Test set | Baseline WDER % | E4B WDER % | Baseline cpWER % | E4B cpWER % | Paired ΔWDER (pp) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fisher (172 sessions) | 5.32 [4.93, 5.74] | 2.99 [2.65, 3.37] | 20.88 [19.97, 21.88] | 17.62 [16.76, 18.56] | −2.33 [−2.51, −2.16], p < 0.0001 |
| Callhome (20 calls) | 7.74 [6.07, 9.65] | 4.92 [3.46, 6.75] | 24.31 [21.27, 27.43] | 20.69 [17.98, 23.66] | −2.82 [−3.48, −2.14], p < 0.0001 |
| ICSI (3 meetings) | 14.70 [11.65, 20.29] | 14.10 [10.77, 19.94] | 43.90 [39.10, 51.67] | 43.32 [38.38, 51.20] | −0.60 [−0.88, −0.35], p < 0.0001 |
| AMI (16 meetings) | 15.68 [10.64, 21.11] | 14.89 [9.80, 20.38] | 40.32 [32.43, 48.00] | 39.57 [31.57, 47.29] | −0.79 [−1.00, −0.60], p < 0.0001 |

- The card reports one WER per set (15.37, 15.22, 29.42, 24.33 in table order) and does not say whether post-processing changes words (**Reported**).
- Speaker-count MAE falls from 0.215 to 0.093 on Fisher and from 0.050 to 0.000 on Callhome, and is unchanged on ICSI (0.333) and lower on AMI (0.500 to 0.438) (**Reported**).
- The 8B predecessor reports WDER / cpWER of 3.28 / 18.37 on Fisher and 6.66 / 23.57 on Callhome, without intervals; it is not evaluated on ICSI or AMI (**Reported**).[^diarizationlm-gemma4-card]
- Differences are percentage-point changes (5.32 → 2.99 = −2.33) (**Observed** arithmetic). The unpaired cpWER gains are 0.58–3.62 pp, but the card gives no paired test for cpWER.
- ICSI has three meetings and AMI sixteen, so conversation-level resampling yields wide intervals (ICSI WDER intervals about 9 pp wide) (**Synthesis**).
- The 4B-versus-8B comparison has no intervals or paired test for the 8B rows and covers two of four sets (**Observed**).
- The card does not state whether training and test splits are disjoint, although it trains on Callhome, ICSI, and AMI and tests on their full test sets (**Unverified**).
- The card reports no latency, real-time factor, throughput, or memory figures and no non-English evaluation (**Observed** absence).

## Usage

- Input: a hypothesis whose speaker turns carry `<speaker:N>` tags, wrapped as `<|turn>user\n{hypothesis} --> <turn|>\n<|turn>model\n` (**Reported**).[^diarizationlm-gemma4-card]
- Python path: `transformers` in bf16 on CUDA with greedy decoding (`do_sample=False`) and `max_new_tokens` set to 1.2× the prompt length. The completion is cut at ` [eod]` and mapped back onto the original text with `diarizationlm.utils.transfer_llm_completion` (**Reported**).[^diarizationlm-gemma4-card]
- GGUF path: `llama-cli` with `--temp 0.0 -n 128` and the same prompt. The example uses a fixed 128-token cap and omits the `[eod]` truncation and speaker-transfer steps (**Observed**).[^diarizationlm-gemma4-card]
- Implication: a 4,000-character segment is far longer than 128 output tokens, so GGUF use on segment-sized inputs needs a larger cap or the transfer step (**Synthesis**).
- Neither command was executed for this concept (**Unverified**).
- Tag format to verify before prompting: the library's text representation uses `<spk:N>` tags, not the `<speaker:N>` tags described above. Neither source settles which one the checkpoint expects (**Observed** difference; see [Contradictions](#contradictions)).[^diarizationlm-readme]

## Contradictions

- **Significance claim.** The Overview says the model achieves "statistically significant (p < 0.0001) WDER and cpWER improvements simultaneously across all four benchmarks." The benchmark table gives paired p-values only for ΔWDER, and the unpaired cpWER intervals overlap the baseline on Callhome, ICSI, and AMI (for example, ICSI 43.32 [38.38, 51.20] against 43.90 [39.10, 51.67]). This concept chooses neither reading; the cpWER significance claim is **Reported** and not supported by the capture.[^diarizationlm-gemma4-card]
- **Speaker tag format.** The card's input wraps speaker turns in `<speaker:N>` tags.[^diarizationlm-gemma4-card] The library README's text representation writes `<spk:N>` and presents `create_diarized_text()` as the route for building prompts.[^diarizationlm-readme] Neither source says which tag this checkpoint was trained on, so neither is chosen here; the effect on outputs is **Unverified**. See [DiarizationLM Toolkit](diarizationlm-toolkit.md).
- **Repository owner.** The card's code uses `google/DiarizationLM-Gemma-4-E4B-v1`.[^diarizationlm-gemma4-card] The README links the Gemma 4 E4B weights and GGUF demo Space under `diarizers-community/`.[^diarizationlm-readme] Neither owner is chosen; the publisher is unresolved.

## Coverage and limits

- Coverage: one model-card capture and the library README inspected statically (the card's frontmatter, Overview, training, file list, benchmark tables, usage, citation). No weights, GGUF files, code, or notebooks were fetched; the Python and `llama.cpp` commands were not run; no benchmark was reproduced (**Synthesis**).
- Not captured: the DiarizationLM paper (arXiv 2401.03506), the `diarizationlm` package source, the Hugging Face demo Space, and the GGUF weights. The library README is compiled as a second source in [DiarizationLM Toolkit](diarizationlm-toolkit.md). The "USM + turn-to-diarize" baseline is named but not defined here (**Synthesis**).
- No revision or commit is recorded in the card; all figures are tied to this capture (**Synthesis**). Model and benchmark facts carry `stale_after: 2027-10-13` per the `vad` domain rule.
- Sensitive values: none. The card contains only public links, code, and citation data (**Observed**).

## Relationships

- Depends on the base model `google/gemma-4-E4B` (Gemma 4 E4B), which has no concept in this wiki (**Reported**).[^diarizationlm-gemma4-card]
- Uses the `diarizationlm` Python package for its usage utilities and metric computation (**Reported**).[^diarizationlm-gemma4-card][^diarizationlm-readme] Package scope and metric definitions are in [DiarizationLM Toolkit](diarizationlm-toolkit.md) and [Speaker-Attributed ASR Metrics](speaker-attributed-asr-metrics.md).
- Complements speaker diarizers that emit speaker activity, such as [Nemotron 3 Diarization](nemotron-3-diarization.md) and [Streaming Sortformer Diarizer 4spk v2.1](diar-streaming-sortformer-4spk-v2-1.md). The card names neither as its input system, so the pairing is an agent inference (**Synthesis**).
- Distinct from [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md), whose listed post-ASR steps (punctuation, truecasing, alignment, hotwords) do not include LLM speaker-turn correction (**Synthesis**).

[^diarizationlm-gemma4-card]: [DiarizationLM-Gemma-4-E4B-v1 model card](../raw/DiarizationLM-Gemma-4-E4B-v1.txt) — locators: frontmatter (`license`, `base_model`, `library_name`, `tags`); `## Overview` (four benchmark corpora, "not an officially supported Google product", significance sentence); `## Training Configuration` (Gemma 4 E4B architecture, LoRA r = 256 module list, objective, 51,063 and 20,762 pair counts, 10,000 steps, AdamW/LR/schedule, TPU v5p, 4,000-character segmentation); `## Model Files Included` (safetensors ~16.0 GB, Q4_K_M ~5.30 GB, Q4_0 ~5.15 GB); `## Benchmark Performance (with 95% Bootstrap Confidence Intervals)` (Fisher, Callhome, ICSI, and AMI rows with WER, WDER and cpWER intervals, SpkCntMAE, paired ΔWDER with p-value; `DiarizationLM-8b-Fisher-v2` rows for Fisher and Callhome); `## Usage` `### 1. Python` (prompt template, `do_sample=False`, `max_new_tokens` factor, `[eod]` truncation, `transfer_llm_completion`) and `### 2. GGUF (llama.cpp)` (`--temp 0.0`, `-n 128`); `## Citation` (Interspeech 2024 BibTeX). Unavailable: no revision or commit recorded; linked GitHub, Hugging Face, and arXiv pages were not fetched.

[^diarizationlm-readme]: [DiarizationLM README](../raw/DiarizationLM.md) — locators: badges (PyPI, GitHub Actions, Hugging Face, arXiv); `## Overview` (paper link, Gemma 4 E4B, Llama 3 8B, and Llama 2 13B links, GGUF demo Space, `diarizers-community/` Gemma link); `## Disclaimer`; `## Instructions` > `### Install the package`, `### Data format`, `### Conversion between representations`, `### Transcript-preserving speaker transfer (TPST)`, `### Training data preparation`, `### LLM finetuning and inference (OpenAI)`, `### LLM finetuning and inference (Gemma & Llama)`, `### Completion parser`, `### Metrics`; `## Citation`. Unavailable: no revision or commit recorded; `resources/` figures, the `diarizationlm` source, and linked pages were not captured or fetched.
