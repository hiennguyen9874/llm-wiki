---
type: Concept
title: ROOTS multilingual training corpus and governance
description: ROOTS is BLOOM’s reported 1.6-TB multilingual and code pretraining corpus, whose documented provenance- and community-oriented construction makes remaining privacy, rights, bias, and coverage limits explicit rather than resolved.
tags: [roots, bloom, bigscience, training-data, multilingual, data-governance]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:17:43+07:00 }
sources:
  - id: bloom-summary
    resource: ../raw/BLOOM.md
    title: "BLOOM overview (Vietnamese summary)"
---

# ROOTS multilingual training corpus and governance

ROOTS (Responsible Open-science Open-collaboration Text Sources) is the reported BLOOM pretraining corpus: about 1.6 TB from hundreds of sources, spanning 46 natural languages and 13 programming languages. The supplied overview presents ROOTS as both a data mixture and a governance effort involving documentation, language-community expertise, and explicit discussion of privacy, copyright, consent, and uneven representation.[^bloom-summary]

## Reported composition and scale

The source reports approximately 350B unique tokens after preprocessing and approximately 366B tokens observed during BLOOM training. Its 59-language total includes natural-language text and source code; the overview names Java, PHP, C/C++, Python, JavaScript, C#, Ruby, Go, TypeScript, Rust, and Scala among the code languages.[^bloom-summary]

BLOOM’s byte-level BPE tokenizer was reportedly trained from multilingual samples with alpha weighting so high-resource languages would not wholly dominate the vocabulary. Byte-level representation permits broad Unicode coverage, but it does not demonstrate equal tokenization efficiency or downstream quality across languages.[^bloom-summary]

## Governance and unresolved limits

The overview says the project documented source characteristics, consulted specialists and language communities, examined imbalances, and removed some unsuitable material rather than indiscriminately crawling the web. These practices make data decisions more inspectable; they do not establish that all source permissions, personal-data concerns, or representation harms were eliminated.[^bloom-summary]

The source explicitly retains the possibility of personal information, toxic content, bias, and uncertain provenance in ROOTS. It also cautions that coverage of 46 natural languages is not evidence of comparable quality: lower-resource languages may produce weaker, unstable, or wrong-language outputs.[^bloom-summary]

## Relationships

- **Trains:** [BLOOM open multilingual language model](bloom-open-multilingual-language-model.md).
- **Relates to:** [The Pile data governance](the-pile-data-governance.md); both describe why public or documented corpus access does not remove component-level privacy, rights, harmful-content, or representation uncertainty.
- **Relates to:** [The Pile training corpus](the-pile-training-corpus.md); ROOTS is multilingual by design, whereas the initial Pile concept documents an English-oriented mixture.[^bloom-summary]

[^bloom-summary]: “BLOOM overview” (Vietnamese summary), [raw source](../raw/BLOOM.md), Sections 3–4 and 9. This is secondary-source evidence that cites the ROOTS corpus paper and model page; primary corpus documentation and component records have not been independently ingested here.
