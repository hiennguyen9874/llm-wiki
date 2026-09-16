---
type: Concept
title: GA-DMS robust text-based person retrieval
description: GA-DMS uses gradient-and-attention-derived token scores to mask suspected caption noise and reconstruct informative tokens while pretraining CLIP for text-based person retrieval.
tags: [cross-modal-retrieval, clip, token-masking, noisy-captions, person-reidentification]
status: stable
created: 2026-09-16
generated: { by: llm-wiki-agent/1, at: 2026-09-16T08:44:13Z }
sources:
  - id: arxiv-2509.09118v1
    resource: ../raw/papers/arXiv-2509.09118v1/main.tex
    title: Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval
  - id: ga-dms-code-2026-03-11
    resource: ../raw/codes/GA-DMS/README.md
    title: Official GA-DMS code snapshot, updated 2026-03-11
---

# GA-DMS robust text-based person retrieval

GA-DMS adapts CLIP ViT-B/16 to text-based person retrieval with two score-guided masking branches. A gradient-attention similarity score (GASS) estimates each caption token's contribution to global image-text similarity. Low-scoring tokens are preferentially masked before similarity-distribution matching (SDM), while high-scoring tokens are masked and reconstructed through a cross-modal decoder. The model is pretrained on [WebPerson](webperson-person-centric-pretraining-dataset.md), then evaluated by direct transfer or IRRA-style downstream fine-tuning. Reported gains support the combined data-and-training pipeline, but do not cleanly separate WebPerson's contribution from GA-DMS and have not been independently reproduced. The released implementation exposes the core mechanism but does not reproduce the manuscript configuration as shipped.[^arxiv-2509.09118v1][^ga-dms-code-2026-03-11]

## Gradient-attention token scoring

For each of the final $L$ text-transformer layers, GASS combines three signals:[^arxiv-2509.09118v1]

1. the gradient of global cosine similarity between image `[CLS]` and text `[EOS]` representations with respect to the layer's `[EOS]` state;
2. normalized `[EOS]`-to-token attention, with multi-scale average pooling over adjacent query and key features at scales 1 and 2;
3. the layer's token value features.

The layer-wise gradient and attention terms are combined, averaged across selected layers, and passed through ReLU to produce token scores. The paper uses the final eight of twelve text layers after an author-reported sweep. This mechanism requires backward-gradient information during training; the source does not report its incremental time or memory cost.[^arxiv-2509.09118v1]

## Dual-masking objectives

- **Noise Token Masking:** lower GASS values produce higher sigmoid masking probabilities, capped by $\alpha_n=0.2$. Masked captions train bidirectional SDM against image embeddings. The intended effect is to suppress hallucinated or mismatched caption details rather than discard the whole pair.[^arxiv-2509.09118v1]
- **Masked Informative Token Prediction:** higher GASS values produce higher masking probabilities, capped by $\alpha_i=0.3$. Image states act as queries and masked text states as keys and values in a cross-modal interaction encoder; an MLP predicts the original tokens.[^arxiv-2509.09118v1]
- **Objective:** $\mathcal{L}=\mathcal{L}_{sdm}+0.4\mathcal{L}_{mtp}$. The source uses separate masked caption views for SDM and token prediction, rather than asking one masking policy to serve both noise removal and semantic reconstruction.[^arxiv-2509.09118v1]

**Synthesis:** the two branches encode opposite assumptions about the score: low-score tokens are treated as unreliable supervision, while high-score tokens are treated as useful reconstruction targets. This is token-level robustness to caption content, unlike methods that identify entire mismatched image-caption pairs.

## Released implementation

The pretraining code computes GASS from the final eight text-transformer blocks, writes each minibatch's detached token scores back into an in-memory dataset, and rebuilds the masking loader each epoch. `FilterDataset` applies sigmoid sampling with the documented caps of 0.2 and 0.3, using complementary score directions for SDM and masked-token prediction. Fine-tuning switches to a conventional IRRA-style model with random 15% token masking rather than retaining GASS.[^ga-dms-code-2026-03-11]

The shipped launcher and data path materially limit reproducibility:[^ga-dms-code-2026-03-11]

- `webreid.py` ignores `--root_dir`, hard-codes an author-local `/mnt/tianluzheng/dataset/WebReid` path, and loads only `100w.json`; the released command therefore does not directly configure the paper's 5M run.
- `run_ddp.sh` sets learning rate $10^{-5}$ and masked-token loss weight 0.3, versus $10^{-4}$ and 0.4 in the manuscript. Its batch size is 128 per each of eight processes, yielding an apparent global batch of 1,024 rather than the reported 512.
- In distributed pretraining, token scores are retained only in each process's local Python dataset and are not synchronized. Because `DistributedSampler` reshuffles ownership each epoch, a sample can move to a rank that does not hold its latest score.
- `requirements.txt` lists only `prettytable` and `easydict`, although the code imports additional packages including NumPy, torchvision, Pillow, PyYAML, `ftfy`, `regex`, `tqdm`, and TensorBoard support. The separate README command installs PyTorch but not all remaining dependencies.
- `test.py` expects `best.pth`, while training saves dataset-specific `best0.pth`, `best1.pth`, and `best2.pth`; it also builds the pretraining model rather than the fine-tuning model. Evaluation is therefore not wired to the documented training outputs without manual changes.

**Implementation caution:** the GASS routine normalizes the aggregated map globally across the whole minibatch, not independently per sample, and divides EOS attention by the sum of raw importance values rather than by an attention sum. These choices differ from the most direct reading of the paper's normalization description and make one sample's mask scores batch-dependent.[^ga-dms-code-2026-03-11]

## Reported evidence

After 5M-scale WebPerson pretraining and downstream fine-tuning, the paper reports:[^arxiv-2509.09118v1]

| Dataset | Rank-1 | Rank-5 | Rank-10 | mAP |
|---|---:|---:|---:|---:|
| CUHK-PEDES | 77.60 | 91.40 | 94.78 | 69.82 |
| ICFG-PEDES | 69.51 | 83.47 | 87.67 | 42.30 |
| RSTPReid | 71.25 | 87.25 | 92.90 | 55.43 |

The paper's own comparison table does not support best-on-every-metric wording: ProPOT reports higher ICFG-PEDES mAP (42.93), and the 1M GA-DMS variant reports higher RSTPReid Rank-5 (88.00) than the 5M variant (87.25). The strongest 5M results are therefore metric-specific.[^arxiv-2509.09118v1]

Ablations use 0.5M WebPerson samples. Against a no-masking/no-objective baseline, GASS-guided SDM increases Rank-1 from 56.75 to 63.87 on CUHK-PEDES, 34.63 to 44.02 on ICFG-PEDES, and 45.50 to 52.30 on RSTPReid. Adding GASS-guided token prediction raises these to 64.25, 44.39, and 52.70. GASS outperforms cosine-score masking in the compared configurations, although cosine-guided MTP alone slightly underperforms the baseline on two datasets. The experiment varies coupled components rather than independently testing every scoring, masking, and objective choice.[^arxiv-2509.09118v1]

The source also reports that direct-transfer Rank-1 rises with WebPerson scale from 0.1M to 5M by 9.39, 16.46, and 10.50 points on the three benchmarks. Because the scale study retains the same pipeline and takes nested or differently sampled subsets without reported variance, it supports a scale association within this setup, not a general data-scaling law.[^arxiv-2509.09118v1]

## Training and limitations

Pretraining uses $384\times128$ images, text sequences up to 77 tokens, Adam with learning rate $10^{-4}$, cosine scheduling after five warm-up epochs, batch size 512, and 30 epochs on eight A100 80 GB GPUs. SDM temperature is 0.02. The manuscript does not report total training time, GASS overhead, retrieval latency, repeated-run variance, or an independently audited natural-noise benchmark.[^arxiv-2509.09118v1] The code snapshot passes Python bytecode compilation, but training and evaluation were not executed because the required datasets, author-local WebPerson layout, checkpoints, and GPU environment were unavailable.[^ga-dms-code-2026-03-11]

- Evidence covers three closely related English-language person-retrieval datasets. Generalization to other retrieval domains, caption styles, languages, and modern backbones remains unknown.
- The token-score visualization contains selected examples and cannot establish score calibration or systematic hallucination detection.
- The method's benchmark gains combine a new web corpus, score-guided masking, and downstream IRRA-style training; no factorial experiment isolates all three.
- GASS treats low contribution to the current model's similarity as evidence of noise. A correct but difficult attribute could also receive a low score, creating a model-dependent feedback loop that the source does not evaluate.

## Relationships

- **Depends on:** [WebPerson person-centric pretraining dataset](webperson-person-centric-pretraining-dataset.md) supplies the paper's large-scale image-caption pretraining corpus.
- **Uses:** [IRRA for text-to-image person retrieval](irra-text-to-image-person-retrieval.md) supplies SDM and the cross-modal masked-token decoder pattern; the reported downstream protocol describes IRRA fine-tuning.
- **Compared with:** [RDE for noisy-correspondence person retrieval](rde-noisy-correspondence-person-retrieval.md) filters whole image-caption pairs under correspondence noise, whereas GA-DMS masks individual caption tokens judged unreliable.

[^arxiv-2509.09118v1]: Tianlu Zheng, Yifan Zhang, Xiang An, Ziyong Feng, Kaicheng Yang, and Qichuan Ding, “Gradient-Attention Guided Dual-Masking Synergetic Framework for Robust Text-based Person Retrieval,” arXiv:2509.09118v1, [`main.tex`](../raw/papers/arXiv-2509.09118v1/main.tex). All included sections and tables were inspected; the architecture, data pipeline, examples, token-weight visualizations, and parameter/scale plots were also visually inspected. Results were not independently reproduced.
[^ga-dms-code-2026-03-11]: Tianlu Zheng et al., [official GA-DMS code snapshot](../raw/codes/GA-DMS/README.md), README dated as updated 2026-03-11, MIT License. The README, launch and entry-point scripts, model/objective code, masking and data-loading code, training processors, checkpoint utility, dependency manifest, and both included figures were inspected. The tree passed `python3 -m compileall`; runtime behavior and reported results were not reproduced.
