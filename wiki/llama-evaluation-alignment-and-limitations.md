---
type: Concept
title: LLaMA evaluation, alignment, and limitations
description: The reported LLaMA 1 evaluation shows strong but task-dependent base-model results, while leaving instruction following, safety alignment, long-context use, bias, toxicity, hallucination, and contamination as material limits.
tags: [llama, evaluation, alignment, safety, benchmark-contamination, limitations]
status: draft
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-07-31T23:20:06+07:00 }
sources:
  - id: llama-summary
    resource: ../raw/LLaMA.md
    title: "LLaMA overview (Vietnamese summary)"
---

# LLaMA evaluation, alignment, and limitations

The supplied LLaMA overview reports zero- and few-shot results across roughly 20 benchmarks, including commonsense reasoning, closed-book question answering, reading comprehension, mathematics, code generation, MMLU, truthfulness, toxicity, and bias. It also makes clear that original LLaMA is a pretrained base model, not a fully aligned or safety-hardened chat assistant.[^llama-summary]

## Reported evaluation profile

The source reports particularly strong LLaMA-65B results on several commonsense, closed-book QA, reading-comprehension, and code benchmarks. For example, it reports LLaMA-65B at 23.7 HumanEval and 37.7 MBPP pass@1, below PaLM-540B on HumanEval but above it on MBPP; it also reports lower MMLU performance than Chinchilla-70B and PaLM-540B.[^llama-summary]

These comparisons are conditional on the reported benchmarks, prompting, scoring, and model variants. The summary notes that contamination was checked through train/benchmark overlap searches, but some datasets had meaningful overlap and incomplete public training-data disclosure limits independent verification.[^llama-summary]

## Base model versus chat assistant

Original LLaMA is trained for causal next-token prediction. The summary therefore distinguishes it from an instruction-following, multi-turn assistant optimized to give structured helpful responses or refuse unsafe requests. It mentions a small instruction-tuning experiment, LLaMA-I, but says this was not the work’s main focus; supervised instruction tuning, preference alignment, and conversational safety require additional work.[^llama-summary]

## Safety and capability limits

The source identifies the following material limits:

- **Hallucination:** truthfulness evaluation does not eliminate plausible-sounding false answers.
- **Bias and toxicity:** web-scale pretraining data can reproduce social bias, harmful content, and misinformation; the cited benchmarks cover only part of the deployment risk.
- **Uneven language coverage:** the corpus is strongly English-weighted, particularly through English CommonCrawl.
- **Short context:** the reported 2,048-token training context makes direct long-document use dependent on chunking or retrieval techniques.
- **Environmental cost:** the summary reports substantial GPU-hour, energy, and normalized-emissions estimates for final training and broader research activity; these estimates are workload- and methodology-specific rather than a universal footprint for LLM development.[^llama-summary]

## Relationships

- **Evaluates:** [LLaMA efficient pre-trained language models](llama-efficient-pre-trained-language-models.md).
- **Compared with:** [GPT-3 limitations and social risk](gpt-3-limitations-and-social-risk.md); both source summaries identify hallucination, bias, toxicity, and evaluation limits for web-trained base models, without making their reported risk measurements directly interchangeable.[^llama-summary]

[^llama-summary]: “LLaMA overview” (Vietnamese summary), [raw source](../raw/LLaMA.md), Sections 6–9. This is secondary-source evidence that links to arXiv:2302.13971 and a Llama 2 publication; neither primary source has been independently ingested here.
