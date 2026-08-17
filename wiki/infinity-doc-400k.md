---
type: Dataset
title: Infinity-Doc-400K
description: Infinity-Doc-400K pairs rendered document pages with structured targets using synthetic HTML rendering and cross-validated pseudo-labeling of real documents.
tags: [datasets, document-parsing, synthetic-data, pseudo-labeling]
status: draft
created: 2026-08-17
generated: { by: llm-wiki-agent/1, at: 2026-08-17T13:35:12Z }
sources:
  - id: infinity-parser-paper
    resource: ../raw/2506.03197_InfinityParser/main.tex
    title: "Infinity-Parser: Layout-Aware Reinforcement Learning for Scanned Document Parsing"
  - id: infinity-parser2-report
    resource: ../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex
    title: Infinity-Parser2 Technical Report
---

# Infinity-Doc-400K

Infinity-Doc-400K is a training corpus for end-to-end scanned document parsing. It pairs rendered document pages with structured Markdown-like targets and combines a synthetic branch designed for exact alignment with a real-world branch designed for natural layout diversity. The paper describes annotations for bounding boxes, text, tables, formulas, page and region attributes, and reading order across seven domains.[^infinity-parser-paper]

## Construction pipelines

### Synthetic documents

The synthetic branch samples text and images from Wikipedia, web crawls, and online corpora, injects them into Jinja-driven single-, double-, or triple-column HTML templates, renders the pages through a browser, filters low-quality or overlapping images, and derives aligned Markdown targets from the source HTML. The paper reports approximately 69K synthetic documents.[^infinity-parser-paper]

### Real-world documents

The real-world branch collects financial reports, medical records, academic papers, books, magazines, and web pages. Specialized models process layout, text, formulas, and tables; predictions are cross-checked against other expert models and VLMs, and only consistent regions are retained as pseudo-ground truth. The rounded domain breakdown reports approximately 331K real-world documents, dominated by magazines (180K) and academic papers (71.7K).[^infinity-parser-paper]

### Quality control

The authors report that three document-analysis experts manually inspected about 5% of the data, that screening rules were refined at least five times, and that multi-model cross-verification scaled the filtering of real-world annotations.[^infinity-parser-paper]

## Training-length profile

The appendix reports a mean target length of 1,765 tokens, a median of 1,127, and a maximum of 31,147. Its histogram totals 400,482 samples; 73.0% fall from 512 to under 4K tokens, 10.57% are at least 4K, and 0.64% are at least 8K. For model training with an 8K context limit, longer sequences are left-truncated to retain their endings.[^infinity-parser-paper]

## Contradictions and trust limits

- **Total size is internally inconsistent.** The introduction says **400,482**, the methodology says **400,066**, and the context-length histogram sums to **400,482**. The rounded domain counts sum to 400K and cannot resolve the exact total.[^infinity-parser-paper]
- **Naming is stale in parts of the appendix.** Active captions for the domain montage refer to **Infinity-Doc-55K**, while surrounding prose and tables use Infinity-Doc-400K.[^infinity-parser-paper]
- The real-world annotations are filtered pseudo-labels, not uniformly human-authored ground truth. The appendix itself characterizes their quality as relatively low because expert-model predictions can disagree.[^infinity-parser-paper]
- The source does not provide per-domain acceptance rates, inter-annotator agreement, cross-validation thresholds, deduplication details, licenses, or a contamination audit beyond stating that benchmark test data underwent text-similarity filtering.[^infinity-parser-paper]
- The paper promises a future release of the dataset. The local source bundle does not include the records, so composition, privacy filtering, licensing, and annotation quality cannot be independently audited here.[^infinity-parser-paper]

## Relationships

- **Partly reused by:** [Infinity-Doc2-5M](infinity-doc2-5m.md), which samples 57K examples for its `doc2md` task.[^infinity-parser2-report]
- **Used by:** [LayoutRL and Infinity-Parser](layout-rl-and-infinity-parser.md) uses document/reference pairs from this corpus for reinforcement-learning reward computation and model training.

[^infinity-parser-paper]: Wang et al., *Infinity-Parser: Layout-Aware Reinforcement Learning for Scanned Document Parsing*, local LaTeX source bundle at [main.tex](../raw/2506.03197_InfinityParser/main.tex), including its referenced section and figure files (accessed 2026-08-17).
[^infinity-parser2-report]: INF Team, *Infinity-Parser2 Technical Report*, local LaTeX source at [arxiv_latex.tex](../raw/2607.07836_Infinity-Parser2/arxiv_latex.tex) (accessed 2026-08-17).
