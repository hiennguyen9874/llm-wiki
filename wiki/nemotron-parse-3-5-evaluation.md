---
type: Concept
title: Nemotron 3.5 Parse evaluation
description: Nemotron 3.5 Parse evaluation reports vendor-run ParseBench pass tradeoffs and Indic and synthetic multilingual OCR results with protocol limits.
tags: [ml, ocr, benchmarks, multilingual, document-parsing]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T14:47:22Z }
stale_after: 2027-05-02
sources:
  - id: nemotron-35-card
    resource: ../raw/Nemotron-3.5-Parse.md
    kind: model-card
    title: Nemotron 3.5 Parse model card
  - id: nemotron-20-card
    resource: ../raw/NVIDIA-Nemotron-Parse-2.0.md
    kind: model-card
    title: NVIDIA Nemotron Parse 2.0 model card
---

# Nemotron 3.5 Parse evaluation

**Reported, not reproduced:** NVIDIA evaluates [Nemotron 3.5 Parse](nemotron-parse-3-5.md) on ParseBench document parsing, IndicVisionBench OCR, and synthetic multilingual MOSCAR OCR. Differences in pass count, page preparation, metrics and postprocessing constrain comparisons with other systems.[^nemotron-35-card]

## ParseBench and throughput

The card reports 2,078 unique pages. Single pass parses the whole page; double pass refines predicted table/chart crops; triple pass adds detection and refines the union of detection and parser regions. Differing crop and full-page alternatives are retained in the merge and included in scoring.[^nemotron-35-card]

| Configuration | Overall score ↑ | Pages/s ↑ |
| --- | ---: | ---: |
| Single | 72.74 | 15.42 |
| Double | 74.92 | 11.65 |
| Triple | 75.20 | 10.62 |

The triple-pass component scores are tables 84.67, charts 64.40, content faithfulness 87.96, semantic formatting 68.28, and visual grounding 70.67. The speed test uses prepared page images on one H100 per model and includes passes and dependent crop work, but excludes preparation, startup, warmup, final rendering and writes. Thus the double-to-triple gain of 0.28 points costs about 9% throughput under those conditions, not necessarily end-to-end service throughput.[^nemotron-35-card]

## Multilingual OCR

IndicVisionBench reports 83.73 ANLS-char and 16.00% character error rate (CER) over 876 pages in 10 languages; the same card reports 72.12 and 52.67% respectively for Parse 2.0. MOSCAR reports 99.51 character-bag F1 and 1.35% CER over 8,111 simply rendered synthetic pages, covering 163 language/script entries; the same card reports 97.44 and 11.55% for 2.0. It says both comparisons use identical page sets, greedy decoding and the same scorer, but each model's own default prompt; token-limited outputs are included. Character-bag F1 ignores order and simple synthetic pages do not demonstrate accuracy on degraded scans, handwriting or complex real-world documents.[^nemotron-35-card]

**Comparison limit:** The earlier [Parse 2.0](nemotron-parse-2-0.md) card reports 72.03 ANLS-char and 91.02 MOSCAR BoC F1 for its 2.0 checkpoint, unlike the 72.12 and 97.44 values in the 3.5 card. These are separate reported results, not a demonstrated contradiction under an identical protocol: the older card describes an equal-weight checkpoint soup and its full evaluation conditions and comparability to the newer test are not established.[^nemotron-20-card][^nemotron-35-card]

## Evidence limits

All figures are model-card claims. Linked ParseBench reproduction scripts, timing details and metrics, full per-language results, and regression outputs were unavailable locally and not inspected; no model, benchmark, or throughput test was run. The card reports a separate 500-page regression score of 74.49% overall and 83.38% table quality and explicitly says these are not official ParseBench or OmniDocBench TEDS scores.[^nemotron-35-card]

[^nemotron-35-card]: NVIDIA, [Nemotron 3.5 Parse model card](../raw/Nemotron-3.5-Parse.md), §§ Benchmark highlights and Evaluation Results (ParseBench, IndicVisionBench OCR, MOSCAR multilingual OCR).
[^nemotron-20-card]: NVIDIA, [NVIDIA Nemotron Parse 2.0 model card](../raw/NVIDIA-Nemotron-Parse-2.0.md), § Evaluation Results and checkpoint comparison.
