---
type: Concept
title: GPT generative pre-training and task adaptation
description: GPT pre-trains a decoder-only Transformer language model on contiguous text, then transfers it through discriminative fine-tuning with serialized task inputs.
tags: [gpt, generative-pre-training, causal-language-modeling, fine-tuning, transfer-learning]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-01T05:33:53Z }
sources:
  - id: radford-generative-pre-training-2018
    resource: ../raw/gpt.pdf
    title: Improving Language Understanding by Generative Pre-Training
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# GPT generative pre-training and task adaptation

GPT first learns a causal language-model objective on long, contiguous text, then fine-tunes those parameters for a labeled discriminative task with a linear output layer. It keeps the core decoder-only Transformer architecture across tasks by converting structured inputs into ordered token sequences.[^radford-generative-pre-training-2018]

## Pre-training model and objective

For an unlabeled token corpus, the model maximizes the likelihood of each token conditioned on preceding context tokens. Its language model is a 12-layer Transformer decoder with masked self-attention, 768-dimensional states, 12 attention heads, 3072-dimensional feed-forward inner layers, learned token and position embeddings, and a 40,000-merge BPE vocabulary.[^radford-generative-pre-training-2018]

The reported pre-training corpus is BooksCorpus: over 7,000 unpublished books containing long contiguous text. The paper trained on randomly sampled 512-token spans for 100 epochs and reports token-level perplexity 18.4 on that corpus.[^radford-generative-pre-training-2018]

## Fine-tuning and task interface

For a labeled input, the final Transformer activation feeds an added linear output layer; the paper says the only new fine-tuning parameters are that output layer and task delimiter-token embeddings. It also evaluates a combined objective that adds the language-model objective on the labeled data to the discriminative objective, weighted by $\lambda=0.5$ in its experiments.[^radford-generative-pre-training-2018]

Rather than introducing separate task-specific encoders, the paper serializes structured inputs:

- **Textual entailment:** concatenate premise and hypothesis with a delimiter.
- **Similarity:** process both sentence orders independently, then add their sequence representations before classification.
- **Multiple-choice question answering and commonsense reasoning:** process each `[context; question; delimiter; answer]` sequence independently and normalize scores over answers.[^radford-generative-pre-training-2018]

The paper's ablation reports that omitting pre-training reduced its average score from 74.7 to 59.9 across its listed tasks. The auxiliary language-model objective was not uniformly beneficial: it helped some NLI and QQP results, but the reported unweighted average was slightly higher without it (75.0 versus 74.7).[^radford-generative-pre-training-2018]

## Reported evidence and limits

The source reports contemporary state-of-the-art results on 9 of 12 evaluated datasets, including 86.5% accuracy on Story Cloze and 59.0% on RACE; its overall GLUE score was 72.8. These are historical, benchmark- and setup-specific results, not evidence of current state of the art.[^radford-generative-pre-training-2018]

It also tested heuristic zero-shot scoring by average token log-probability for linguistic acceptability, sentiment, multiple-choice reading comprehension, and pronoun resolution. The observed performance increased during language-model pre-training, but these hand-designed task conversions are not a general zero-shot evaluation method.[^radford-generative-pre-training-2018]

## Reference implementation

The supplied [OpenAI GPT PyTorch reference implementation](openai-gpt-pytorch-reference-implementation.md) instantiates a configurable decoder stack with learned token and position embeddings, causal attention, four-times-width MLPs, and post-residual layer normalization. It is library-code evidence for the architecture rather than a replacement for the paper's training or evaluation evidence.[^huggingface-openai-gpt-pytorch]

## Relationships

- **Uses:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md)'s masked decoder self-attention and position-wise feed-forward computation, but not its encoder or encoder-decoder attention.
- **Implemented by:** [OpenAI GPT PyTorch reference implementation](openai-gpt-pytorch-reference-implementation.md).
- **Contrasts with:** [BERT bidirectional transfer learning](bert-bidirectional-transfer-learning.md), whose encoder represents each token with both left and right context rather than GPT's causal context.
- **Extended by:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), which scales the decoder-only language-model approach and modifies its tokenization, context length, normalization, and initialization.

[^radford-generative-pre-training-2018]: Alec Radford, Karthik Narasimhan, Tim Salimans, and Ilya Sutskever, “Improving Language Understanding by Generative Pre-Training” (2018), bundled [PDF](../raw/gpt.pdf), especially Sections 3–5 and Tables 2–5.

[^huggingface-openai-gpt-pytorch]: Hugging Face `modeling_openai.py`, “PyTorch OpenAI GPT model,” bundled [source](../raw/gpt-source.py). The supplied file has no revision or release-version metadata.
