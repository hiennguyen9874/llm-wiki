---
type: Concept
title: Pyannote Community-1 Diarization Benchmarks
description: Twelve-benchmark DER table for pyannote speaker-diarization-community-1 against legacy 3.1 and cloud Precision-2, with recomputed deltas, one regression, one tie, and protocol caveats.
tags: [vad, diarization, benchmarks, pyannote]
status: stable
created: 2026-10-25
generated: { by: llm-wiki-agent/1, at: 2026-10-25T03:16:00Z }
stale_after: 2027-10-25
sources:
  - id: pyannote-community-1-card
    resource: ../raw/pyannote-speaker-diarization-community-1.md
    kind: documentation
    title: pyannote/speaker-diarization-community-1 model card
---

The [Pyannote Speaker Diarization Community-1](pyannote-speaker-diarization-community-1.md) card reports diarization error rate (DER, %) on twelve academic benchmarks for three pipelines: the legacy `speaker-diarization-3.1`, the open `community-1`, and the commercial `precision-2`. Community-1 beats 3.1 on ten benchmarks, ties on one, and is worse on one, while `precision-2` beats Community-1 on all twelve. All figures are vendor-reported with a single stated protocol and no per-benchmark configuration detail (**Reported**; counts and deltas recomputed here as **Observed**).[^pyannote-community-1-card]

## DER table

| Benchmark | legacy 3.1 | community-1 | precision-2 | Δ community-1 vs 3.1 |
| --- | ---: | ---: | ---: | ---: |
| [AISHELL-4](https://arxiv.org/abs/2104.03603) | 12.2 | 11.7 | 11.4 | −0.5 (−4.1 %) |
| [AliMeeting](https://www.openslr.org/119/) (channel 1) | 24.5 | 20.3 | 15.2 | −4.2 (−17.1 %) |
| [AMI](https://groups.inf.ed.ac.uk/ami/corpus/) (IHM) | 18.8 | 17.0 | 12.9 | −1.8 (−9.6 %) |
| [AMI](https://groups.inf.ed.ac.uk/ami/corpus/) (SDM) | 22.7 | 19.9 | 15.6 | −2.8 (−12.3 %) |
| [AVA-AVD](https://arxiv.org/abs/2111.14448) | 49.7 | 44.6 | 37.1 | −5.1 (−10.3 %) |
| [CALLHOME](https://catalog.ldc.upenn.edu/LDC2001S97) (part 2) | 28.5 | 26.7 | 16.6 | −1.8 (−6.3 %) |
| [DIHARD 3](https://catalog.ldc.upenn.edu/LDC2022S14) (full) | 21.4 | 20.2 | 14.7 | −1.2 (−5.6 %) |
| [Ego4D](https://arxiv.org/abs/2110.07058) (dev) | 51.2 | 46.8 | 39.0 | −4.4 (−8.6 %) |
| [MSDWild](https://github.com/X-LANCE/MSDWILD) | 25.4 | 22.8 | 17.3 | −2.6 (−10.2 %) |
| [RAMC](https://www.openslr.org/123/) | 22.2 | 20.8 | 10.5 | −1.4 (−6.3 %) |
| [REPERE](https://www.islrn.org/resources/360-758-359-485-0/) (phase 2) | 7.9 | 8.9 | 7.4 | **+1.0 (+12.7 %)** |
| [VoxConverse](https://github.com/joonson/voxconverse) (v0.3) | 11.2 | 11.2 | 8.5 | 0.0 (0.0 %) |

(**Reported**; Δ column computed **Observed**).[^pyannote-community-1-card]

## What the numbers support

- Unweighted mean DER across the twelve benchmarks: 24.64 (legacy 3.1), 22.57 (community-1), 17.18 (precision-2). The card prints no mean or aggregate, so these are recomputed (**Observed**).[^pyannote-community-1-card]
- Community-1 is lower on ten of twelve, identical on VoxConverse, and higher on REPERE. Relative gains span 4.1 % (AISHELL-4, 12.2 → 11.7) to 17.1 % (AliMeeting, 24.5 → 20.3); the largest absolute gain is also AliMeeting at 4.2 points, ahead of AVA-AVD's 5.1 points on a much higher base (**Observed**).[^pyannote-community-1-card]
- The regeneration is concentrated on meeting and in-the-wild sets (AliMeeting, both AMI conditions, MSDWild, AVA-AVD, Ego4D) and small on clean telephone-style data (AISHELL-4, DIHARD 3, CALLHOME, RAMC) (**Synthesis**).[^pyannote-community-1-card]
- `precision-2` improves on every row, with the largest relative drops on RAMC (20.8 → 10.5, −49.5 %) and CALLHOME part 2 (26.7 → 16.6, −37.8 %) and the smallest on AISHELL-4 (−2.6 %) (**Observed**).[^pyannote-community-1-card]
- Switching to `precision-2` is documented as a one-line change of the pipeline id plus a pyannoteAI API key, and that pipeline runs on pyannoteAI servers rather than locally; the card gives no price, quota, data-handling, or latency information for it (**Reported**).[^pyannote-community-1-card]

## Protocol and provenance

- Stated protocol: fully automatic processing, no forgiveness collar, and no skipping of overlapping speech; the metric is the `pyannote-metrics` diarization error rate (**Reported**).[^pyannote-community-1-card]
- The table header is labelled "Benchmark (last updated in 2025-09)" and the card carries no revision or publication date, so the snapshot date of the comparison is only approximately known (**Reported**; inference **Synthesis**).[^pyannote-community-1-card]
- Not stated: the scoring-tool version, per-benchmark speaker-count assumptions, whether `num_speakers` was fixed, which checkpoints of `legacy` or `precision-2` were scored, GPU versus CPU execution, and whether any benchmark audio overlaps training data (**Synthesis**).[^pyannote-community-1-card]

## Comparability

- [CrispASR Diarization and Post-Processing](crispasr-diarization-postprocessing.md) reports "7.8 %" for pyannote with a TitaNet embedder on VoxConverse dev. That figure is a different pipeline, embedder, and unstated protocol, so it cannot be compared with the 11.2 reported here for the Community-1 pipeline; neither number is reconciled (**Synthesis**).[^pyannote-community-1-card]
- The NVIDIA diarizers in this wiki ([Nemotron 3 Diarization](nemotron-3-diarization.md), [Sortformer Diarizer 4spk v1](diar-sortformer-4spk-v1.md), [Streaming Sortformer Diarizer 4spk v2](diar-streaming-sortformer-4spk-v2.md)) publish DER under their own evaluation conditions and often add SCA/MAE and RTFx, with explicit 4- or 8-speaker channels; no shared rows exist, so cross-family ranking from these tables alone is unsupported (**Synthesis**).
- DER under "no collar, overlap included" is stricter than the collared practice common in older diarization papers, so the absolute values here are not directly comparable to collared DER elsewhere (**Synthesis**).[^pyannote-community-1-card]

## Contradictions

- The prose claims Community-1 is "much better than `speaker-diarization-3.1`", while the card's own table shows a 1.0-point regression on REPERE (8.9 versus 7.9) and an exact tie on VoxConverse (11.2 versus 11.2). The two readings are recorded, neither is chosen: the claim holds as an aggregate tendency over twelve mixed benchmarks, not as a per-benchmark guarantee (**Reported**).[^pyannote-community-1-card]

## Coverage and limits

- The table is transcribed from a single static capture (227 lines) and its arithmetic was recomputed by hand; no benchmark was run, no audio scored, and no dataset downloaded (**Synthesis**).[^pyannote-community-1-card]
- The card names each benchmark but not the exact test split or scoring recipe beyond the "part 2", "full", "dev", "channel 1", "IHM/SDM", and "phase 2" labels; those datasets, their papers, and the `pyannote-metrics` implementation were not inspected (**Synthesis**).[^pyannote-community-1-card]
- All DER values are **Reported** vendor figures; unweighted means, relative deltas, and ranking counts are **Observed** arithmetic on those figures. Benchmark numbers carry `stale_after: 2027-10-25` per the `vad` domain rule.

[^pyannote-community-1-card]: [pyannote/speaker-diarization-community-1 model card](../raw/pyannote-speaker-diarization-community-1.md) — locators: `## Benchmark` preamble (out-of-the-box claim, pyannote-metrics DER definition link, "fully automatic processing, no forgiveness collar, nor skipping overlapping speech", "last updated in 2025-09" header); the 12-row three-column benchmark table (AISHELL-4 through VoxConverse v0.3) and its per-benchmark links; the `Precision-2` paragraph and `diff` fence (`speaker-diarization-precision-2`, pyannoteAI API key, "runs on pyannoteAI servers"); `# community-1 speaker diarization` improvement bullet list ("improved speaker assignment and counting").
