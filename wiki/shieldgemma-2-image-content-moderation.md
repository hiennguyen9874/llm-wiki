---
type: Concept
title: ShieldGemma 2 image content moderation
description: A 4B Gemma 3-based image-safety classifier that applies an input policy to natural or synthetic images, with thresholdable violation scores for sexual, dangerous, and violence/gore content.
tags: [multimodal-safety, content-moderation, vision-language-models, image-classification, synthetic-data]
status: stable
created: 2026-08-16
generated: { by: llm-wiki-agent/1, at: 2026-08-17T00:00:00Z }
sources:
  - id: zeng-2025-shieldgemma2
    resource: ../raw/2504.01081_ShieldGemma2/main.tex
    title: ShieldGemma 2: Robust and Tractable Image Content Moderation
---

# ShieldGemma 2 image content moderation

ShieldGemma 2 (SG2) is a 4B-parameter image-content moderation model fine-tuned from Gemma 3 4B IT. Given one image and a supplied safety policy, it classifies both natural and generated images; its default policies address sexually explicit material, dangerous content, and violence/gore. The source reports benchmark results under its own policy definitions, so they should not be treated as policy-independent measures of general safety performance.[^zeng-2025-shieldgemma2]

## Policy-conditioned classification

- A default sexual-content policy prohibits explicit or graphic sexual acts, including pornography, erotic nudity, rape, or sexual assault; the dangerous-content policy prohibits content facilitating or encouraging real-world harm, such as firearms or explosive construction, terrorism promotion, or suicide instructions; and the violence/gore policy prohibits shocking, sensational, or gratuitous violence.[^zeng-2025-shieldgemma2]
- Users may supply one or more default policies or a bespoke policy. The model is prompted to decide only whether the image violates the stated policy, rather than a fixed, implicit taxonomy.[^zeng-2025-shieldgemma2]
- SG2 derives a continuous predicted violation probability from the next-token log likelihoods of `Yes` and `No`, with temperature and uncertainty hyperparameters. This permits downstream threshold selection to trade precision and recall; the paper recommends context caching when evaluating several policies for the same image.[^zeng-2025-shieldgemma2]

## Training data and method

- For each policy, the paper’s synthetic-data pipeline produces tree-structured taxonomies spanning dimensions such as topic, demographic, context, region, and image style; it combines leaf nodes into image prompts and iteratively refines generation. The authors report generating about 10,000 Imagen images per policy.[^zeng-2025-shieldgemma2]
- For real-image coverage, the authors sampled WebLI, used caption-based text-safety scores to retain images with a violation probability above 0.1 for at least one category, and selected 120,000 filtered images for training.[^zeng-2025-shieldgemma2]
- Borderline Adversarial Data Generation (BADG) searches for prompts on which ShieldGemma 1 disagrees with a Gemini-based auto-rater, generating both false-positive and false-negative cases to improve boundary classification.[^zeng-2025-shieldgemma2]
- Gemini 2 Flash produces labels with in-context prompts, few-shot examples, and Tree-of-Thoughts-style decomposition. Supervised fine-tuning splits data evenly between binary answers and JSON answers with simplified rationales derived from a separate model’s reduction of the detailed reasoning.[^zeng-2025-shieldgemma2]

## Reported evaluation and limits

- On the authors’ internal benchmark, SG2’s reported F1 was 88.6% for sexual content, 93.7% for dangerous content, and 85.0% for violence/gore; the paper reports these exceeded the tested LlavaGuard 7B, GPT-4o mini, and base Gemma 3 comparisons under its policies.[^zeng-2025-shieldgemma2]
- On a 603-example, policy-reannotated subset of UnsafeBench, SG2 reported 64.2 sexual F1, 88.7 dangerous-content 1−FPR, and 95.9 violence/gore 1−FPR. Relabeling substantially reduced positive examples for danger and violence, so the metrics and comparisons are contingent on the authors’ reannotation and policy alignment.[^zeng-2025-shieldgemma2]
- Removing BADG reduced the reported internal F1 by 2.6 points for dangerous content and 2.7 points for violence/gore; this is ablation evidence within the paper’s data and evaluation setup.[^zeng-2025-shieldgemma2]
- The authors identify three limits: it does not address harmful meaning arising from text overlaid on an otherwise benign image; it is designed for single-image rather than interleaved conversation inputs; and it is not specifically fine-tuned beyond the three default policy categories.[^zeng-2025-shieldgemma2]

## Evidence coverage

The complete TeX manuscript was reviewed, including all sections, appendix, contributor list, and local figures. The figures corroborate the described synthetic-data pipeline and show policy-reannotation examples; this concept makes no claim based only on their pixels. Bibliographic entries and branding assets were not independently reviewed because they do not add material evidence for these claims.

[^zeng-2025-shieldgemma2]: ShieldGemma Team, “ShieldGemma 2: Robust and Tractable Image Content Moderation” (2025), [source](../raw/2504.01081_ShieldGemma2/main.tex).
