---
type: Concept
title: 'Text Classification Lineage: From Bag-of-Words to Transformers'
description: Evolution of text classifiers from bag-of-words baselines through RNNs, CNNs, and BERT/GPT/T5 adaptations with IMDb reference results.
tags: [text-classification, transformers, baselines]
status: stable
created: 2026-10-02
generated: { by: llm-wiki-agent/1, at: 2026-10-02T23:59:00Z }
sources:
  - id: raschka-jevl-2026-09-29
    resource: ../raw/classifier-history-and-jev/index.md
    scope: ../raw/classifier-history-and-jev/
    kind: article
    title: 'Language Models for Text Classification: From Bag-of-Words to Jev'
  - id: reddit-jev-hype-2026-09
    resource: ../raw/i-really-dont-understand-jev-hype/index.md
    scope: ../raw/i-really-dont-understand-jev-hype/
    kind: thread
    title: I really don't understand Jev hype
  - id: reddit-jev-marketing-2026-09
    resource: ../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md
    scope: ../raw/jev-isnt-new-tech-its-marketing-targets-people/
    kind: thread
    title: Jev isn't new tech. Its marketing targets people who think AI started with LLMs
---

# Text Classification Lineage: From Bag-of-Words to Transformers

Synthesis: cheap bag-of-words plus linear models remain the baseline to beat; RNNs added order-sensitivity but were hard to train; text CNNs added parallelism; pre-trained transformers replaced both via fine-tuning, with encoder, decoder, and encoder-decoder variants using different classification adaptations (§1–§2)[^raschka-jevl-2026-09-29].

## Bag-of-words baselines

- Representation: build vocabulary of unique training words, optionally drop stopwords, then encode each document as fixed-size word-count vector; TF-IDF is a normalization variant (§1.1, Fig. 3)[^raschka-jevl-2026-09-29].
- Compatible classifiers: naive Bayes, logistic regression, SVMs, random forest, XGBoost (§1.1)[^raschka-jevl-2026-09-29].
- Strengths: computationally cheap; effective when individual words are strong label clues, e.g. spam filtering and news classification; reported Gmail spam-filter and 1961 computer-abstract sorting antecedents are **reported**, not independently verified (§1.1)[^raschka-jevl-2026-09-29].
- Limitation: loses word order — “the dog bites the man” vs “the man bites the dog” collide; word-pair or longer n-grams preserve local order at vocabulary-size cost (§1.1)[^raschka-jevl-2026-09-29].
- Reference result: logistic regression plus bag-of-words achieves about 89.9% on balanced IMDb in the author’s minimally tuned tutorial (Fig. 4); author retains this as go-to baseline (§1.1)[^raschka-jevl-2026-09-29].

## Word embeddings

- Contrast: bag-of-words counts whole-document word frequencies; embeddings map each word to a dense learned vector (§1.2.1, Fig. 5)[^raschka-jevl-2026-09-29].
- Sources: external Word2Vec or GloVe, or an embedding layer learned with the network; analogous to LLM embedding layers except classic word tokens vs LLM subword tokens (§1.2.1)[^raschka-jevl-2026-09-29].
- Limit: classic lookups are context-independent — “bank” shares one vector in “river bank” and “bank account”; attention later addresses this (§1.2.1)[^raschka-jevl-2026-09-29].

## RNN classifiers

- Mechanism: read one embedding at a time, combine with fixed-size hidden state summarizing prior text; rearranged words change state updates so order matters; rolled and unrolled diagrams show the same reused layers (§1.2.2, Figs. 6–7)[^raschka-jevl-2026-09-29].
- Variants: LSTM (1997) and GRU (2014) add learned retention gates; xLSTM appeared 2024; attention was first developed for RNNs before transformers; state-space models reuse the sequential fixed-state idea with the same retention and sequential-processing bottlenecks (§1.2.2)[^raschka-jevl-2026-09-29].
- Reference results: from-scratch LSTM about 85.66% on balanced IMDb with train-test gap indicating overfitting (Fig. 8); transfer-learning ULMFiT (2018) pre-train then fine-tune reaches 95.4% IMDb (§1.2.2, Fig. 9)[^raschka-jevl-2026-09-29].

## CNN classifiers for text

- Mechanism: learned filters slide over windows of adjacent embeddings, e.g. width-3 over “the movie had surprisingly good acting” yields four windows; filter computation is parallel across positions, unlike RNN steps (§1.2.3, Figs. 10–12)[^raschka-jevl-2026-09-29].
- Length handling: flattening preserves info but varies with input length; global max-pooling yields length-agnostic vector before the classification head (§1.2.3)[^raschka-jevl-2026-09-29].
- Reference result: author experiment about 90.07% IMDb, explicitly architecture-dependent (§1.2.3, Fig. 13)[^raschka-jevl-2026-09-29].

## Transformer adaptations

- Origin: 2017 encoder-decoder transformer for translation; split into encoder-style BERT and decoder-style GPT paradigms, plus encoder-decoder T5 survivors (§2, Fig. 14)[^raschka-jevl-2026-09-29].
- Encoder (BERT): fine-tune first-position `[CLS]` token; ModernBERT (2024) is author’s go-to, about 95% IMDb with little tuning and perhaps 1–2% headroom (§2.1, Figs. 15–16)[^raschka-jevl-2026-09-29].
- Decoder (GPT): direct prompting is brittle for structured domains; preferred retrofit replaces vocab output with lean classification head; causal mask forces use of last non-padding token so it sees full context, vs BERT’s bidirectional `[CLS]` (§2.2, Figs. 17–19)[^raschka-jevl-2026-09-29].
- Decoder reference: GPT-2 124M about 92% IMDb; larger newer open-weight models expected better but possibly overkill for classification (§2.2, Fig. 20)[^raschka-jevl-2026-09-29].
- Encoder-decoder (T5, 2019): span-corruption pre-training; two classification modes — added classification head vs text-to-text decoder emitting the label ("positive"/"negative"); GPT text-to-text often works out-of-box, T5 usually needs target-domain decoder fine-tuning (§2.3, Figs. 21–23)[^raschka-jevl-2026-09-29].

## Zero-shot continuity note

- Community continuity point is **reported** in a 2026-09-21–25 skepticism thread: BERT-era zero-shot classification (with a Hugging Face `zero-shot-classification` pipeline link) already removed per-task training for amateurs and professionals alike, so Jev's "no pretraining for a specific task" claim reads as broader world knowledge plus easier natural-language task specification rather than a first zero-shot classifier[^reddit-jev-hype-2026-09].
- Usability-shift framing from the same thread is **reported**: old stacks required data preparation, vectors, and feature extraction (XGBoost/SVM/manual features; 2005 yes/no plus confidence anecdote), while the new front end accepts English questions and dynamic option sets — summarized as "same concept, more intelligent and without retraining," with scale/implementation rather than basic concept as the claimed advance[^reddit-jev-hype-2026-09].
- NLI precedent detail is **reported** in a 2026-09-23–10-01 marketing-critique thread: NLI-based zero-shot classification already handled arbitrary natural-language labels without task-specific training since 2019 (Yin et al. D19-1404 cited, uninspected), exposed as one-line Hugging Face `zero_shot_classification(text, candidate_labels)` UX plus sentence-transformer/reranker workflows, with BART-MNLI as the suggested starting model and SetFit for few-shot baselines; classic spaCy/scikit-learn stacks are distinguished as libraries needing labeled data rather than pretrained foundation behavior[^reddit-jev-marketing-2026-09].

## Relationships

- Uses [Classifier Calibration](classifier-calibration.md) for production probability adjustment after training.
- Depends on [Jev API Patterns](jev-api-patterns.md) as the generalized single-head retrofit of the BERT/GPT heads described here.
- Contrasts with [Jev Decision Model](jev-decision-model.md), which avoids per-task fine-tuning entirely.

## Coverage limits

- All IMDb numbers are author’s lightly tuned experiments on a balanced split, not independent benchmarks; cross-model ranking should not be treated as definitive.
- Figure assets under `raw/classifier-history-and-jev/assets/` were not visually re-inspected; content above follows prose captions and surrounding text.
- Historical claims (Gmail filter, 1961 naive Bayes) are **reported** from the article without primary-source verification.
- Marketing-critique thread above is single-thread Reddit anecdote (2026-09-23–10-01); NLI-2019, HF-pipeline, BART-MNLI and SetFit pointers are **reported** with linked paper and model pages uninspected[^reddit-jev-marketing-2026-09].
- Skepticism thread above is single-thread Reddit anecdote (2026-09-21–25); HF pipeline page and linked media were not inspected, and continuity/usability framings are **reported** perceptions[^reddit-jev-hype-2026-09].

[^raschka-jevl-2026-09-29]: S. Raschka, "Language Models for Text Classification: From Bag-of-Words to Jev," Ahead of AI, published 2026-09-29, canonical local entry `../raw/classifier-history-and-jev/index.md`, upstream `https://magazine.sebastianraschka.com/p/classifier-history-and-jev`. Locators in text: §1–§2, Figs. 3–23.
[^reddit-jev-hype-2026-09]: u/Manerfish plus commenters, "I really don't understand Jev hype," r/LocalLLaMA, post 2026-09-21 with comments through 2026-09-25, canonical local entry `../raw/i-really-dont-understand-jev-hype/index.md`, package scope `../raw/i-really-dont-understand-jev-hype/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1wm65le/i_really_dont_understand_jev_hype/`. Locators in text: zero-shot/BERT continuity (`vintageballs` pbcfz9i, `Thomas-Lore` pb4eay0, `PsychologicalOne752` pb4tok0); LLM-centric rediscovery (`pooquipu` pbcirb4, `thomas2385` pbbheca, `Hefty_Acanthaceae348` pb7rwpd, `Silver-Champion-4846` pb4dt42); feature-engineering contrast (`spongik` pb654rn, `stewsters` pb7ys0u, `Any_Fox5126` pb8z7is, `Equivalent-Grass-527` pb6ba6z).
[^reddit-jev-marketing-2026-09]: u/tiensss plus commenters, "Jev isn't new tech. Its marketing targets people who think AI started with LLMs," r/LocalLLaMA, post 2026-09-23 with comments through 2026-10-01, canonical local entry `../raw/jev-isnt-new-tech-its-marketing-targets-people/index.md`, package scope `../raw/jev-isnt-new-tech-its-marketing-targets-people/`, upstream `https://www.reddit.com/r/LocalLLaMA/comments/1woe70t/jev_isnt_new_tech_its_marketing_targets_people/`. Locators in text: NLI-2019 (D19-1404) and HF zero-shot-pipeline replies; BART-MNLI starter and SetFit pointers; spaCy/scikit-learn labeled-data distinction.
