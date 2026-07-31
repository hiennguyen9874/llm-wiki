---
type: Concept
title: The Pile training corpus
description: The Pile is a 22-source, predominantly English pretraining mixture whose static sampling weights favor a deliberately diverse mix of web, scientific, code, legal, book, and conversational text.
tags: [training-data, datasets, data-mixtures, provenance, the-pile]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:09:26Z }
sources:
  - id: the-pile-summary
    resource: ../raw/ThePile.md
    title: "The Pile: An 800GB Dataset of Diverse Text for Language Modeling (summary)"
---

# The Pile training corpus

The Pile is a reported 825-GiB English-oriented language-model pretraining corpus assembled from 22 sources. Its central design choice is a static, deliberately weighted mixture of web text with scientific, technical, legal, literary, and conversational sources rather than a largely undifferentiated web crawl; the supplied summary reports that models trained on it outperformed comparable Common Crawl and CC-100 baselines across most or all of its component domains.[^the-pile-summary]

## Composition and mixture

The source identifies Pile-CC, PubMed Central, Books3, OpenWebText2, arXiv, GitHub, FreeLaw, and Stack Exchange as the largest components. Other named components include Wikipedia, Project Gutenberg, BookCorpus2, OpenSubtitles, DeepMind Mathematics, Ubuntu IRC, EuroParl, Hacker News, YouTube subtitles, PhilPapers, NIH ExPorter, USPTO Backgrounds, PubMed Abstracts, and Enron Emails.[^the-pile-summary]

The component boundaries make the mixture auditable at a useful high level: web sources supply broad coverage; arXiv, PubMed, and PhilPapers supply research text; GitHub, Stack Exchange, and Ubuntu IRC supply technical and programming discourse; and FreeLaw, USPTO, and NIH ExPorter supply legal or administrative material. The source describes records as containing `text` plus source/component metadata, with train, validation, and test splits.[^the-pile-summary]

The builders do not merely concatenate the sources. They assign each component an epoch-like sampling multiplier: the summary gives Pile-CC as one epoch, PubMed Central and arXiv as two, Wikipedia as three, Project Gutenberg as 2.5, and Books3 as 1.5. This produces a reported effective mixture of about 1.25 TiB per complete pass, allowing smaller selected sources to have greater influence than their raw size alone would imply.[^the-pile-summary]

## Processing and reported evidence

The summary describes source-specific normalization and quality filtering, particularly for web sources, followed by deduplication, shuffling, and weighted interleaving. It explicitly cautions that this does not establish complete removal of duplicates or benchmark leakage.[^the-pile-summary]

The reported evaluation compares perplexity of existing GPT-2 and GPT-3 models across components and trains comparable models on The Pile, raw Common Crawl, and CC-100. It reports better perplexity and downstream results for the The-Pile-trained models, but does not isolate the individual effects of source quality, domain composition, and repeated sampling. The claimed result therefore supports the value of this particular curated mixture, not a general causal ranking of every component or preprocessing choice.[^the-pile-summary]

## Scope limits

The initial corpus is predominantly English, so its coverage is not evidence of multilingual representativeness. Sampling weights are manually selected in the described release, and source quality varies materially by component.[^the-pile-summary]

## Relationships

- **Has governance limits:** [The Pile data governance](the-pile-data-governance.md), including component-level licensing, privacy, and harmful-content concerns.
- **Relates to:** [GPT-3 benchmark contamination audit](gpt-3-benchmark-contamination-audit.md), which documents why web-scale pretraining results need explicit leakage qualification.

[^the-pile-summary]: “The Pile: An 800GB Dataset of Diverse Text for Language Modeling” (Vietnamese summary), [raw source](../raw/ThePile.md), citing the original paper, dataset card, and project repository. This is secondary-source evidence; its quantitative and historical claims have not been independently verified here.
