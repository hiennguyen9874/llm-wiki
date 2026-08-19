---
type: Benchmark
title: MMEB v3 ranking snapshot
description: An 89-entry multimodal embedding ranking snapshot whose reported overall leader is Tianmu-Emb-Uni at 52.83 and whose 13 nonzero v3 entries are also led by Tianmu-Emb-Uni at 40.50.
tags: [benchmark, embedding, multimodal, mmeb, leaderboard]
status: stable
created: 2026-08-19
generated: { by: llm-wiki-agent/1, at: 2026-08-19T09:52:44Z }
sources:
  - id: mmeb-v3-ranking
    resource: ../raw/mmeb_v3_ranking.csv
    title: MMEB v3 ranking CSV
---

# MMEB v3 ranking snapshot

This supplied CSV lists 89 multimodal embedding entries. Tianmu-Emb-Uni is reported first with Overall 52.83 and Overall-V3 40.50, followed by Ovis-Omni-Embedding-v0.1-3B with 52.55 and 39.90. Only 13 entries have nonzero Overall-V3 and component scores; the other 76 use zero in every v3-related field. Because the artifact gives no metric definitions, task composition, publisher, capture date, evaluation configuration, inclusion criteria, or explanation of whether zero means missing or measured zero, it supports only comparisons of values as reported within this snapshot—not general or time-stable performance claims.[^mmeb-v3-ranking]

## Highest reported entries

| Reported rank | Model | Size (B) | Date | Overall | Overall-V3 | Text | Audio | Agent |
|---:|---|---:|---|---:|---:|---:|---:|---:|
| 1 | Tianmu-Emb-Uni | 8.0 | 26-08-06 | 52.83 | 40.50 | 41.77 | 38.94 | 39.42 |
| 2 | Ovis-Omni-Embedding-v0.1-3B | 3.0 | 26-08-03 | 52.55 | 39.90 | 41.81 | 47.82 | 35.90 |
| 3 | UEmbed-9B (hybrid) | 9.0 | 26-08-13 | 51.54 | 37.27 | 43.08 | 0.00 | 39.46 |
| 4 | UEmbed-9B (dense) | 9.0 | 26-08-12 | 51.50 | 37.25 | 43.09 | 0.00 | 39.39 |
| 5 | UEmbed-9B (sparse) | 9.0 | 26-08-12 | 50.95 | 36.83 | 42.23 | 0.00 | 39.36 |
| 6 | UEmbed-4B (dense) | 4.0 | 26-08-12 | 50.10 | 35.86 | 42.00 | 0.00 | 37.33 |
| 7 | UEmbed-4B (sparse) | 4.0 | 26-08-12 | 49.98 | 36.12 | 41.92 | 0.00 | 38.04 |
| 8 | UEmbed-2B (dense) | 2.0 | 26-08-12 | 47.82 | 34.71 | 40.46 | 0.00 | 36.34 |
| 9 | UEmbed-2B (sparse) | 2.0 | 26-08-12 | 46.93 | 33.85 | 39.40 | 0.00 | 35.52 |
| 10 | e5-omni-7B | 7.0 | 26-07-20 | 46.53 | 31.56 | 24.65 | 43.04 | 36.67 |
| 11 | e5-omni-3B | 3.0 | 26-07-23 | 44.03 | 30.29 | 24.38 | 30.76 | 36.85 |
| 12 | omni-embed-nemotron-3b | 3.0 | 26-07-20 | 42.83 | 36.35 | 36.15 | 36.52 | 36.53 |
| 13 | LCO-Embedding-Omni-7B | 7.0 | 26-07-23 | 39.81 | 31.01 | 31.31 | 43.17 | 27.84 |

These are the 13 rows with nonzero Overall-V3 values, and they also occupy the first 13 reported Overall ranks. Overall-V3 is not monotonically ordered by the supplied rank: for example, rank 12 reports 36.35, above ranks 8–11. This indicates that the `Rank` column follows `Overall`, not `Overall-V3`.[^mmeb-v3-ranking]

## Relationships

- **Evaluates:** [e5-omni](e5-omni.md), with separately listed reported entries for its 3B and 7B variants. [^mmeb-v3-ranking]

## Data-quality limits

- The CSV uses dates such as `26-08-06` without declaring the date convention; they are retained verbatim and not normalized.
- Rank 70 appears twice, after which the sequence resumes at 72; there is no rank 71.
- Several models have `unknown` size or date values.
- HTML links embedded in model names point to model repositories, project pages, papers, or API documentation, but the CSV does not establish that those linked parties produced or verified the reported scores.
- Zero-filled v3 columns are preserved as source values; they must not be interpreted as evaluated failures without additional evidence.

[^mmeb-v3-ranking]: [MMEB v3 ranking CSV](../raw/mmeb_v3_ranking.csv). This is an unauthenticated supplied ranking artifact; names, metadata, ranks, and scores are reproduced as reported.
