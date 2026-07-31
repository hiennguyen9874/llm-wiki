---
type: Concept
title: GPT-2 zero-shot multitask evaluation and overlap auditing
description: GPT-2 uses natural-language task cues and demonstrations for zero-shot evaluation, while auditing n-gram overlap to qualify possible training-data contamination.
tags: [gpt-2, zero-shot-learning, prompting, evaluation, data-contamination]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T15:33:02Z }
sources:
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
---

# GPT-2 zero-shot multitask evaluation and overlap auditing

The GPT-2 report evaluates a causal language model without task-specific parameter or architecture changes by expressing task cues, inputs, and demonstrations as text in its context. It reports that larger models improve across its zero-shot evaluations, but treats data overlap, prompt design, and task-specific metric limits as material qualifications rather than proof of general task competence.[^radford-gpt-2-2019]

## Text-conditioned task behavior

The report frames a general task as modeling $p(\text{output}\mid\text{input}, \text{task})$, with language providing the task specification and examples. For example, it conditions translation on `english sentence = french sentence` demonstrations, prompts summarization with `TL;DR:`, and conditions CoQA on a document, dialogue history, and `A:`. These are evaluation prompting schemes, not supervised adaptation.[^radford-gpt-2-2019]

The 1.542B-parameter model reported contemporary zero-shot state-of-the-art results on 7 of 8 tested language-modeling datasets. It achieved 55 F1 on CoQA development with no use of the baselines’ 127,000+ training examples, but only 4.1% exact-match accuracy on Natural Questions. Its CNN/Daily Mail summaries qualitatively resembled summaries while scoring only slightly above selecting three random sentences, and its WMT-14 translation results remained far below the report’s cited best unsupervised system.[^radford-gpt-2-2019]

These are historical, prompt- and benchmark-specific results. The report explicitly characterizes zero-shot performance as far from usable for many practical tasks, and notes that task behavior may depend on natural-language hints.[^radford-gpt-2-2019]

## Overlap and memorization audit

To measure overlap between WebText and evaluation data, the authors built Bloom filters over normalized, lower-cased alphanumeric token 8-grams from WebText. Their stated false-positive-rate bound is $10^{-18}$, and a test of one million generated strings found no matches. Across common language-model test sets, they reported a mean WebText overlap of 3.2%, versus 5.9% overlap with those datasets’ own training splits.[^radford-gpt-2-2019]

Overlap produced a small but consistent reported benefit. For LAMBADA, excluding every example with any detected overlap changed the reported perplexity from 8.6 to 8.7 and accuracy from 63.2% to 62.9%. The authors recommend n-gram-overlap de-duplication as a verification step when constructing NLP train/test splits, while noting that fuzzy matching could better measure highly similar text.[^radford-gpt-2-2019]

The appendix also documents exact memorization on frequently repeated material: an argmax decode conditioned on the opening of the Gettysburg Address, which occurred about 40 times in WebText, reproduced the speech before typically drifting after 100–200 tokens. This example and the aggregate overlap analysis show that low average overlap does not rule out memorization of repeated sequences.[^radford-gpt-2-2019]

## Relationships

- **Evaluates:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md) under zero-shot prompts and contamination checks.
- **Extends:** [GPT generative pre-training and task adaptation](gpt-generative-pre-training-and-task-adaptation.md) from supervised fine-tuning to task cues and demonstrations supplied in context.

[^radford-gpt-2-2019]: Alec Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), bundled [PDF](../raw/gpt2.pdf), especially Sections 2, 3–4, 6–7, and Appendix A.