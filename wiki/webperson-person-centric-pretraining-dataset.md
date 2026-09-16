---
type: Concept
title: WebPerson person-centric pretraining dataset
description: WebPerson filters person images from COYO-700M and uses template-conditioned Qwen vision-language models to generate a large captioned pretraining corpus for person retrieval.
tags: [dataset, synthetic-captions, web-data, person-reidentification, cross-modal-retrieval]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:13:46Z }
sources:
  - id: arxiv-2509.09118v1
    resource: ../raw/papers/arXiv-2509.09118v1/main.tex
    title: Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval
---

# WebPerson person-centric pretraining dataset

WebPerson is a web-derived, person-centric pretraining corpus built by filtering COYO-700M images and generating descriptions with Qwen2.5-VL models. The appendix reports 5,002,723 images and 10,005,446 descriptions, implying two descriptions per image, while the abstract and main text repeatedly call it “5M image-text pairs.” The source therefore establishes approximately 5M images but is internally inconsistent about pair count. The data itself was not included in the inspected source bundle, so quality, licensing, consent, duplication, and demographic coverage claims remain unaudited.[^arxiv-2509.09118v1]

## Construction pipeline

### Person-image filtering

COYO-700M, sourced from Common Crawl, provides the initial web image-caption pool. YOLOv11 detects people; YOLOv11-Pose then checks pose completeness. The prose says retained images have a shorter dimension above 90 pixels, a person aspect ratio between 1:2 and 1:4, detection confidence above 85%, at least eight visible keypoints, at least one hip keypoint, and two head keypoints.[^arxiv-2509.09118v1]

The pipeline figure does not exactly match that wording: it says width above 90 and uses strict `>8`, `>1`, and `>2` keypoint thresholds. These differences matter for exact reproduction and should be resolved against released construction code.[^arxiv-2509.09118v1]

### Template-conditioned captions

1. Qwen2.5-72B-Instruct converts captions from CUHK-PEDES, ICFG-PEDES, and RSTPReid into attribute-placeholder templates.
2. OpenCLIP ViT-bigG/14 embeds the templates; $k$-means groups similar templates. Each cluster contributes its centroid-nearest template and five random templates.
3. Qwen2.5-72B-Instruct synthesizes additional templates. The authors state that generated templates were reviewed to remove bias and stereotypes, yielding 1,000 templates, but do not specify reviewers, protocol, rejection counts, or measured outcomes.
4. Each retained image receives a random template; Qwen2.5-VL-7B-Instruct and Qwen2.5-VL-32B-Instruct generate descriptions constrained to visible person attributes and instructed to omit background and uncertain details. vLLM accelerates generation.[^arxiv-2509.09118v1]

**Synthesis:** the captions are synthetic annotations of real web images, not original alt text. Their vocabulary and sentence structures are shaped by three downstream benchmarks, the selected templates, and Qwen models. This likely improves task alignment but weakens claims that downstream transfer is independent of benchmark-derived language priors.

## Reported evidence

In direct transfer after GA-DMS pretraining, the source reports:[^arxiv-2509.09118v1]

| Pretraining data | CUHK-PEDES R1 | ICFG-PEDES R1 | RSTPReid R1 |
|---|---:|---:|---:|
| WebPerson 0.1M | 58.95 | 38.18 | 47.10 |
| WebPerson 1M | 66.26 | 51.99 | 55.35 |
| WebPerson 5M | 68.34 | 54.64 | 57.60 |
| LUPerson-MLLM 1M | 56.01 | 37.00 | 50.60 |
| SYNTH-PEDES 1M | 57.29 | 57.13 | 42.20 |

Thus WebPerson 1M does not dominate every comparator: SYNTH-PEDES reports higher ICFG-PEDES direct-transfer Rank-1. The source's fine-tuning table reports that WebPerson 1M improves over LUPerson-MLLM 1M on in-domain Rank-1 by 0.43, 1.89, and 0.85 points across the three benchmarks.[^arxiv-2509.09118v1]

These are author-reported downstream comparisons, not direct audits of caption correctness or image quality. The paper does not clearly establish that all external corpus comparisons share identical construction, pretraining compute, model objectives, and data-cleaning conditions. WebPerson and [GA-DMS](ga-dms-robust-person-retrieval.md) are introduced together, so corpus quality cannot be inferred from the strongest end-to-end result alone.[^arxiv-2509.09118v1]

## Governance and limitations

- The source says the data resources are public and that the work follows the ACL Code of Ethics, but public accessibility does not itself establish redistribution rights, subject consent, or fitness for surveillance-related use.[^arxiv-2509.09118v1]
- Images depict people gathered from web pages via COYO/Common Crawl. The manuscript does not report face or identity handling, opt-out or takedown processes, minors policy, source-domain distribution, license filtering, or privacy-risk review.
- The paper proposes “intelligent surveillance” and retail as applications without analyzing misuse, biometric tracking, disparate impact, or deployment safeguards.
- Filtering favors detectable, sufficiently large, pose-complete people and can systematically exclude occluded, seated, mobility-aid-using, culturally diverse, or otherwise atypical presentations. No subgroup-retention audit is reported.
- Template review, caption accuracy, stereotypes, hallucination rates, duplicates, train-test contamination, and demographic balance are not quantitatively evaluated.
- The only limitation stated by the authors is compute-limited scale; that does not cover the corpus's principal provenance, privacy, and representational risks.

## Source inconsistencies

- The appendix reports **5,002,723 images and 10,005,446 descriptions**, while the abstract and main text describe **5M image-text pairs**.
- The prose requires the shorter image dimension to exceed 90 pixels; the pipeline figure says image width exceeds 90.
- The prose uses “at least” for pose thresholds, while the figure displays strict greater-than thresholds.

## Relationships

- **Used by:** [GA-DMS robust text-based person retrieval](ga-dms-robust-person-retrieval.md) uses WebPerson for large-scale CLIP pretraining.
- **Related approach:** [MRA domain-aligned text-based person retrieval](mra-domain-aligned-person-retrieval.md) instead generates target-style synthetic person images, recaptions them, and adds region-phrase boxes; WebPerson retains filtered real web images and generates captions only.

[^arxiv-2509.09118v1]: Tianlu Zheng, Yifan Zhang, Xiang An, Ziyong Feng, Kaicheng Yang, and Qichuan Ding, “Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval,” arXiv:2509.09118v1, [`main.tex`](../raw/papers/arXiv-2509.09118v1/main.tex). All included sections and tables were inspected; the filtering pipeline, dataset examples, and scale plots were also visually inspected. The released dataset and construction code were not inspected.
