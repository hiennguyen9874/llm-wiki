---
type: Concept
title: FastEnhancer
description: Speed-optimized streaming speech-enhancement family (Tiny to Large, 22k–1.1M parameters, 16 kHz and 48 kHz) from Seoul National University with reported VoiceBank-DEMAND and DNS-1 results and CPU real-time factors on Xeon, Apple M1 and M5, but no ASR-in-the-loop, end-to-end latency, or license evidence.
tags: [pipeline, speech-enhancement, denoising, streaming, edge, cpu, paper]
status: draft
created: 2026-10-24
generated: { by: llm-wiki-agent/1, at: 2026-10-24T20:00:00Z }
stale_after: 2027-10-24
sources:
  - id: fastenhancer-paper
    resource: ../raw/arXiv-2509.21867v1-FastEnhancer/main.tex
    scope: ../raw/arXiv-2509.21867v1-FastEnhancer/
    kind: paper
    revision: arXiv 2509.21867v1
    title: "FastEnhancer: Speed-Optimized Streaming Neural Speech Enhancement (LaTeX source)"
  - id: fastenhancer-readme
    resource: ../raw/arXiv-2509.21867v1-FastEnhancer/README-github.md
    kind: documentation
    title: aask1357/fastenhancer GitHub README (undated capture)
---

FastEnhancer (Ahn, Han, Woo, Kim; Seoul National University; accepted to ICASSP 2026) is a family of five single-channel streaming neural speech-enhancement (SE, noise-suppression) models, Tiny (T), Base (B), Small (S), Medium (M) and Large (L), designed to minimize measured CPU real-time factor (RTF, processing time divided by audio duration) rather than parameter or MAC count. The mechanism is a plain encoder–decoder with a time-GRU plus frequency-attention "RNNFormer" bottleneck; why each choice is fast is in [FastEnhancer Design Choices and Ablations](fastenhancer-design-and-ablations.md). On VoiceBank-DEMAND, FastEnhancer-B reports the best score on almost every quality metric against GTCRN, LiSenNet, FSPEN and BSRNN at the lowest RTF in the comparison (0.022 on one Xeon thread versus 0.034–0.060 for the baselines), and FastEnhancer-T reports RTF 0.012 (Xeon) and 0.013 (M1). For a voice pipeline it is a candidate CPU-only noise-suppression front end; no ASR-in-the-loop result for noisy input, no end-to-end latency figure, and no license are in the sources (**Reported**).[^fastenhancer-paper][^fastenhancer-readme]

## Model family

| Size | Hop H | Enc/dec blocks L | RNNFormer blocks K | C₁ | C₂ | F | Params (k) paper / README | MACs paper / README |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Tiny | 256 | 2 | 2 | 24 | 20 | 16 | 22 / 22 | 55M / 60M |
| Base | 256 | 2 | 3 | 48 | 36 | 24 | 92 / 91 | 262M / 262M |
| Small | 256 | 3 | 3 | 64 | 48 | 36 | 195 / 194 | 664M / 664M |
| Medium | 160 | 3 | 4 | 96 | 72 | 48 | 492 / 492 | 2.9G / 2.9G |
| Large | 100 | 4 | 5 | 128 | 96 | 64 | 1105 / 1105 | 11G / 12G |

- Configuration columns are from the paper's model-configuration table; the paper and the README disagree slightly on Tiny MACs (55M vs 60M), Base/Small parameters (92/195 vs 91/194) and Large MACs (11G vs 12G). The sources do not say which is a recount, and the MACs denominator (per second of audio or per frame) is not stated, so none is chosen (**Reported**; discrepancy **Observed**).[^fastenhancer-paper][^fastenhancer-readme]
- Front end (16 kHz): STFT size 512, hop H (256 = 16 ms; 160 = 10 ms; 100 = 6.25 ms), power compression exponent 0.3, a two-channel (real/imaginary) complex mask applied to the compressed spectrogram, highest frequency bin dropped and zero-padded back (**Reported**).[^fastenhancer-paper]
- 48 kHz variants (README only): n_fft 1024, doubled hop and larger F (Tiny 28k parameters / 177M MACs / M5 RTF 0.0122 up to Large 1132k / 32.4G / 0.4239), learnable rather than fixed pre/post-RNNFormer linear layers, and a dynamic low-pass filter during training because 48 kHz-only training hurt bandwidth-limited inputs. No 48 kHz quality metrics appear in the README (**Reported**).[^fastenhancer-readme]
- Algorithmic latency is not stated. The STFT window of 512 samples is 32 ms at 16 kHz and the hop is 16 ms (Tiny/Base/Small); a streaming port would add at least the overlap-add delay, but the paper reports only RTF (**Synthesis** from the stated STFT settings).[^fastenhancer-paper]

## Reported results: VoiceBank-DEMAND (16 kHz)

Each FastEnhancer size is the mean of five training seeds; LiSenNet (streamable variant), FSPEN and BSRNN were re-implemented or retrained by the authors with the FastEnhancer recipe; GTCRN uses its official checkpoint. Original LiSenNet is not streamable (input normalization and Griffin–Lim), so the table adds a streamable variant (**Reported**).[^fastenhancer-paper]

| Model | Params (k) | MACs | RTF Xeon | RTF M1 | RTF M5 (README) | DNSMOS P.808 | SCOREQ | SISDR | PESQ | STOI | WER % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GTCRN | 24 | 40M | 0.060 | 0.042 | 0.0264 | 3.43 | 0.330 | 18.8 | 2.87 | 0.940 | 3.6 |
| LiSenNet (streamable) | 37 | 56M | 0.034 | 0.028 | 0.0172 | 3.42 | 0.335 | 18.5 | 2.98 | 0.941 | 3.4 |
| FSPEN | 79 | 64M | 0.046 | 0.038 | 0.0244 | 3.40 | 0.324 | 18.4 | 3.00 | 0.942 | 3.6 |
| BSRNN | 334 | 245M | 0.059 | 0.062 | 0.0307 | 3.44 | 0.303 | 18.9 | 3.06 | 0.942 | 3.4 |
| FastEnhancer-T | 22 | 55M | 0.012 | 0.013 | 0.0058 | 3.42 | 0.334 | 18.6 | 2.99 | 0.940 | 3.6 |
| FastEnhancer-B | 92 | 262M | 0.022 | 0.026 | 0.0110 | 3.47 | 0.285 | 19.0 | 3.13 | 0.945 | 3.2 |
| FastEnhancer-S | 195 | 664M | 0.034 | 0.048 | 0.0189 | 3.49 | 0.265 | 19.2 | 3.19 | 0.947 | 3.2 |
| FastEnhancer-M | 492 | 2.9G | 0.101 | 0.173 | 0.0386 | 3.48 | 0.243 | 19.4 | 3.24 | 0.950 | 2.8 |
| FastEnhancer-L | 1105 | 11G | 0.313 | 0.632 | 0.1052 | 3.53 | 0.239 | 19.6 | 3.26 | 0.952 | 3.1 |

(Parameters, MACs, Xeon and M1 columns are the paper's values; the M5 column is from the README. SCOREQ is lower-is-better. The paper's table also reports DNSMOS P.835 SIG/BAK/OVL and ESTOI, omitted here. LiSenNet's non-streamable original scores 13.5 SISDR and PESQ 3.08.)[^fastenhancer-paper][^fastenhancer-readme]

Checks against the table (**Observed**, recomputed):

- Speed claim holds for T and B only. B is 2.7× faster than GTCRN and 1.5× faster than the streamable LiSenNet on Xeon (0.060 and 0.034 vs 0.022). On M1 the margin over LiSenNet is narrow (0.026 vs 0.028). S ties LiSenNet on Xeon (0.034) and is slower than GTCRN, FSPEN and LiSenNet on M1 (0.048 vs 0.042/0.038/0.028); M and L are slower than every baseline on both CPUs. The abstract's "fastest processing speed" therefore applies to the small configurations.[^fastenhancer-paper]
- Parameters and MACs do not predict speed: B has 6.5× the MACs of GTCRN (262M vs 40M) yet runs 2.7× faster on Xeon.[^fastenhancer-paper]
- Quality gaps are small in absolute terms: B versus GTCRN is +0.26 PESQ, +0.2 SISDR, +0.005 STOI. The paper itself notes that M scores slightly lower DNSMOS than S while improving every other metric, and warns that a limited metric set can mislead.[^fastenhancer-paper]
- WER (Whisper-large-v3-turbo on the enhanced output) spans only 2.8–3.6% across all models and no unprocessed-noisy-audio row is given, so the table does not show whether enhancement helps or hurts recognition (**Observed** absence).[^fastenhancer-paper]

## Reported results: DNS-Challenge-1 (16 kHz, README only)

Training used DNS-Challenge-3 wideband data (no `emotional_speech`, no `singing_voice`, VCTK-0.92 clean speech except speakers p232 and p257, no RIR convolution) with no PESQ loss and one seed; testing used the DNS-1 `dev-testset-synthetic-no-reverb` set. GTCRN is the official checkpoint trained for both denoising and dereverberation, so the README notes it may score higher when trained for denoising only (**Reported**).[^fastenhancer-readme]

| Model | DNSMOS P.808 | DNSMOS OVL | SISDR | PESQ | STOI |
| --- | --- | --- | --- | --- | --- |
| GTCRN | 3.85 | 3.05 | 14.8 | 2.26 | 0.934 |
| LiSenNet | 3.82 | 3.14 | 16.3 | 2.58 | 0.947 |
| FSPEN | 3.82 | 3.13 | 15.8 | 2.43 | 0.943 |
| BSRNN | 3.89 | 3.18 | 16.7 | 2.61 | 0.951 |
| FastEnhancer-T | 3.81 | 3.10 | 15.4 | 2.43 | 0.940 |
| FastEnhancer-B | 3.92 | 3.20 | 16.7 | 2.69 | 0.953 |
| FastEnhancer-S | 3.96 | 3.23 | 17.5 | 2.79 | 0.960 |
| FastEnhancer-M | 3.98 | 3.26 | 18.4 | 2.78 | 0.965 |
| FastEnhancer-L | 4.02 | 3.29 | 19.5 | 2.94 | 0.971 |

- On this set Tiny trails the streamable LiSenNet on SISDR (15.4 vs 16.3), PESQ (2.43 vs 2.58) and STOI (0.940 vs 0.947), so the "comparable quality at far lower RTF" Tiny result from VoiceBank-DEMAND does not carry over to DNS-1 unchanged (**Observed** from the README table).[^fastenhancer-readme]
- Base ties BSRNN on SISDR (16.7) and leads on the other listed metrics; baselines other than GTCRN were retrained by the authors, one seed each (**Observed**).[^fastenhancer-readme]

## Voice-pipeline implications

- **Fit**: RTF 0.0058 (Tiny) to 0.011 (Base) on a laptop M5 thread and 0.012–0.022 on a Xeon thread correspond to roughly 0.6–2.2% of one CPU thread per audio second for T and B, which suits a CPU-only noise-suppression stage ahead of VAD or STT without a GPU. RTFs come from ONNXRuntime streaming on a single thread; the exact per-frame measurement protocol is not detailed (**Reported**; interpretation **Synthesis**).[^fastenhancer-paper][^fastenhancer-readme]
- **ASR risk**: the evidence is perceptual and intelligibility metrics plus one Whisper WER on VoiceBank-DEMAND only. [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) records studies where enhancement before ASR raised WER, so a noisy-versus-enhanced WER A/B test in the target language is needed before placing it on the ASR branch (**Synthesis**).
- **Language and data**: 16 kHz VoiceBank-DEMAND (English) and DNS-Challenge data; the 48 kHz recipe draws on Korean, multilingual, Arabic and English clean-speech sets (the Korean sets, from AI-Hub, may not be exported outside South Korea, so their use constrains reproducing it). No Vietnamese evaluation (**Observed** absence).[^fastenhancer-readme]
- **Scope**: single-channel noise suppression; no echo cancellation, separation, or dereverberation training in the FastEnhancer models (**Reported**).[^fastenhancer-readme]

## Relationships

- Compared head to head with GTCRN, LiSenNet, FSPEN and BSRNN; the same GTCRN VoiceBank-DEMAND figures (SISDR 18.8, PESQ 2.87, STOI 0.940) appear independently in [UL-UNAS](ul-unas.md)'s paper table, which supports reuse of the GTCRN official-checkpoint figure (**Observed**). UL-UNAS reports MACS but no RTF, FastEnhancer reports RTF but argues MACs mislead; their training recipes differ, so UL-UNAS's PESQ 3.09 and FastEnhancer-B's 3.13 are not a controlled comparison (**Synthesis**).[^fastenhancer-paper]
- Alternative to [Facebook Denoiser](facebook-denoiser.md) (causal waveform model, README CPU RTF table, no quality metrics), [ClearVoice](clearvoice.md) and [Resemble Enhance](resemble-enhance.md) (larger offline-leaning enhancers); only FastEnhancer and Denoiser publish streaming CPU RTFs, with different hardware and protocols (**Synthesis**).
- Compare with [DPDFNet](dpdfnet.md), a larger (2.3–3.6M parameter) DeepFilterNet2-derived enhancer with edge-NPU rather than CPU RTFs; its VoiceBank-DEMAND GTCRN row (PESQ 2.60, SI-SNR 21.41, 70 Hz high-pass on references) differs from the GTCRN row here (2.87, 18.8), so the two papers' tables are not comparable (**Synthesis**).
- Supports the noise-preprocessing question in [Speech Enhancement Before ASR](speech-enhancement-before-asr.md) as a fast candidate, without ASR evidence on noisy input (**Synthesis**).
- Design rationale and ablations: [FastEnhancer Design Choices and Ablations](fastenhancer-design-and-ablations.md).
- Related to [Fast-ULCNet](fast-ulcnet.md): an ICASSP-2026 sibling edge-speed paper that measures RTF on Arm Cortex-A53/Pi 3 B+ (0.60–0.66) rather than Xeon/Apple silicon, and reports a long-input (90 s) hidden-state drift failure for FastGRNN layers; hardware and baselines differ, so speeds are not comparable (**Synthesis**).
- Related to [CoFi-Lite](cofi-lite.md): a 12.87M MACs/s GTCRN-comparison model reporting desktop-CPU ONNX RTF (0.033) on DNS3, not VoiceBank-DEMAND, so its numbers are not comparable with the FastEnhancer tables (**Synthesis**).

## Coverage and limits

- Ledger: entry point `main.tex` and its inputs (`0.Abstract`, `1.Introduction`, `2.Related`, `3.Model`, `4.Setting`, `5.Results`, `6.Conclusion`, `table-performance`, `table-ablation`) read in full; `00README.json` read (pdflatex toplevel; `IEEEbib.bst` and `refs.bib` ignored); `README-github.md` read in full (Tables 1–4); `fig_model.pdf`, `fig_main.pdf` and `fig_ablation.pdf` rendered and viewed. Excluded as boilerplate or cited-only: `spconf.sty`, `IEEEbib.bst`, `main.bbl` and `refs.bib` (38 references, not followed). The paper was not compiled.
- The linked documentation site (install, dataset, training, metrics, PyTorch and ONNX inference pages), GitHub releases (PyTorch checkpoints, ONNX models, logs), code and any license file were not inspected; availability, license and the exact export protocol are **Unverified**. The paper states code and weights are public.
- The README capture is undated and carries no revision; it adds M5 timings, DNS-1 results and the 48 kHz recipe absent from the paper, and its table is a later or recounted version (see the size-table discrepancies).
- All figures are self-reported on the authors' retrained baselines; none was reproduced. Absent: ASR-in-the-loop on noisy audio, algorithmic or end-to-end latency, memory footprint, quantization, 48 kHz metrics, reverberant data, and variance across seeds (averaged, not tabulated). No sensitive values were found.

[^fastenhancer-paper]: [FastEnhancer LaTeX source](../raw/arXiv-2509.21867v1-FastEnhancer/main.tex) (arXiv 2509.21867v1) — locators: Abstract; Sec. 1 (contributions, `fig_main.pdf` RTF-versus-SISDR/STOI); Sec. 3 (input/output, model configuration table); Sec. 4 (datasets, ONNXRuntime single-thread Xeon Gold 6248R and Apple M1 protocol, metrics, five seeds); Table 1 `table:performance` (VoiceBank-DEMAND with footnotes a–d); Sec. 5.1 (performance comparisons).

[^fastenhancer-readme]: [FastEnhancer GitHub README](../raw/arXiv-2509.21867v1-FastEnhancer/README-github.md) (undated capture) — locators: `Introduction` (ICASSP 2026 acceptance, documentation and releases links); `Results` › Table 1 (VoiceBank-DEMAND with M5 RTF column); `DNS-Challenge 16kHz` › Table 2 and footnotes; `48kHz` › Tables 3 and 4 (training data, model configuration comparison, M5 RTF).
