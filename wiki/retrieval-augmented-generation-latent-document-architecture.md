---
type: Concept
title: Retrieval-augmented generation latent-document architecture
description: Lewis et al.’s RAG model combines a DPR-retrieved non-parametric document memory with a BART generator by marginalizing generated-answer likelihood over top-ranked latent documents.
tags: [rag, retrieval-augmented-generation, dense-retrieval, dpr, bart, latent-variables]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T16:55:07Z }
sources:
  - id: rag-summary
    resource: ../raw/RAG.md
    title: "RAG overview (Vietnamese summary)"
---

# Retrieval-augmented generation latent-document architecture

Lewis et al.’s 2020 RAG architecture pairs parametric language-model memory with a searchable, replaceable non-parametric document memory. A dense retriever gives a distribution over relevant passages and a generator conditions on each selected passage; the answer likelihood marginalizes over those retrieved documents, which are latent variables rather than a single assumed ground-truth context.[^rag-summary]

## Retrieval and generation

For an input $x$, the retriever assigns each passage $z$ a probability $p_\eta(z\mid x)$. The reported system uses Dense Passage Retrieval (DPR): separate BERT encoders embed the question and passage, their inner product scores relevance, and maximum-inner-product search returns the top $K$ passages. This is semantic dense retrieval rather than lexical BM25 retrieval.[^rag-summary]

The generator is BART-large, an encoder–decoder model reported at roughly 400 million parameters. It receives the question concatenated with a retrieved passage and predicts output token $y_i$ conditioned on $x$, $z$, and the preceding generated tokens:

$$
p_\theta(y_i\mid x,z,y_{1:i-1}).
$$

The source describes a December 2018 Wikipedia memory split into roughly 100-word passages (about 21 million passages), embedded and indexed with FAISS.[^rag-summary]

## Documents as latent variables

RAG-Sequence uses one retrieved document for the whole answer sequence:

$$
p_{\mathrm{RAG\text{-}Seq}}(y\mid x)
\approx \sum_{z\in\operatorname{top\text{-}k}}p_\eta(z\mid x)
\prod_{i=1}^{N}p_\theta(y_i\mid x,z,y_{1:i-1}).
$$

RAG-Token instead marginalizes documents independently at each output position:

$$
p_{\mathrm{RAG\text{-}Token}}(y\mid x)
\approx \prod_{i=1}^{N}\sum_{z\in\operatorname{top\text{-}k}}p_\eta(z\mid x)
p_\theta(y_i\mid x,z,y_{1:i-1}).
$$

The former favors a single-document explanation for a response; the latter can combine evidence across passages but is more computationally complex and can mix inconsistent material.[^rag-summary]

## Joint learning and update boundary

The retriever and generator are optimized from input–target pairs with negative log-likelihood, without requiring labels for the correct retrieved passage. The reported training fine-tunes the DPR query encoder and BART while leaving the document encoder and corpus index fixed, because changing the document encoder would require re-embedding the corpus.[^rag-summary]

External memory makes temporal updates possible by replacing the document index rather than retraining the language model. In the source’s summary of the paper’s office-holder experiment, matching 2016 or 2018 Wikipedia indexes answered questions about their respective years at roughly 70% or 68%, while mismatched indexes fell to roughly 12% or 4%; this is reported experimental evidence, not a general update guarantee.[^rag-summary]

## Relationships

- **Simplified by:** [Retrieval-augmented generation operational pipeline and trust limits](retrieval-augmented-generation-operational-pipeline-and-trust-limits.md), whose common application pattern concatenates retrieved chunks in an LLM context rather than explicitly marginalizing answer probabilities over documents.[^rag-summary]

[^rag-summary]: “RAG overview” (Vietnamese summary), [raw source](../raw/RAG.md), Sections 1–10 and 14–15. It cites Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks” (NeurIPS 2020); the primary paper has not been independently ingested here.
