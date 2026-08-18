---
tags:
- ColBERT
- multi-vector
- PyLate
- sentence-transformers
- sentence-similarity
- feature-extraction
- multilingual
- code search
- arxiv:2607.27178
pipeline_tag: sentence-similarity
library_name: PyLate
license: apache-2.0
language:
- en
- fr
- de
- it
- es
- pt
- sv
- 'no'
- ar
- code
base_model:
- lightonai/mLateOn-unsupervised
base_model_relation: finetune
---

<div align="center">
<img src="https://cdn-uploads.huggingface.co/production/uploads/609bbe2f4932693ca2009d6a/D2x1Tlj0fMgn2Y9IwHlUx.png" alt="LightOn" width="512">

[![Website](https://img.shields.io/badge/LightOn-Website-blue?logo=google-chrome)](https://lighton.ai)
[![LinkedIn](https://img.shields.io/badge/LightOn-LinkedIn-0A66C2?logo=linkedin)](https://www.linkedin.com/company/lighton/)
[![X](https://img.shields.io/badge/@LightOnIO-X-black?logo=x)](https://x.com/LightOnIO)

  📚 [Collection](https://huggingface.co/collections/lightonai/mdenseon-and-mlateon) | 📝 [Multilingual Blog](https://huggingface.co/blog/lightonai/mdenseon-mlateon) | 📝 [English Blog](https://huggingface.co/blog/lightonai/denseon-lateon) | 📝 [Paper](https://arxiv.org/abs/2607.27178)

</div>

<h1 align="center">mLateOn</h1>

<h3 align="center">State-of-the-Art Multilingual ColBERT Retrieval Model by LightOn</h3>

<p align="center">
<a href="https://huggingface.co/lightonai/mDenseOn">mDenseOn</a> |
<a href="https://huggingface.co/lightonai/mLateOn">mLateOn</a> |
<a href="https://huggingface.co/lightonai/DenseOn">DenseOn</a> |
<a href="https://huggingface.co/lightonai/LateOn">LateOn</a> |
<a href="https://github.com/lightonai/pylate">PyLate</a> |
<a href="https://github.com/lightonai/fast-plaid">FastPlaid</a>
</p>

> 🎯 **TL;DR**: A 307M-parameter multilingual ColBERT (multi-vector) retrieval model achieving state-of-the-art results across **multilingual retrieval (MIRACL), long-document retrieval (MLDR), English general-domain retrieval (BEIR), and code retrieval (MTEB Code)**. Trained on nine languages only, yet generalizes to unseen languages and scripts, demonstrating that **late interaction enables translate-train viability** for broad multilingual coverage without exhaustive translation.

## About the mDenseOn / mLateOn Family

With [DenseOn](https://huggingface.co/lightonai/DenseOn) and [LateOn](https://huggingface.co/lightonai/LateOn), we demonstrated that an open, carefully curated data recipe can match closed-data retrieval models on English. mDenseOn and mLateOn extend this recipe to multilingual, long-context, and code retrieval.

Rather than independently collecting multilingual corpora from scratch (which would be expensive, uneven across languages, and hard to curate at the same quality), we applied the **translate-train** approach: machine-translating our validated English data into eight target languages (French, German, Italian, Spanish, Portuguese, Swedish, Norwegian, and Arabic) and adding cross-lingual pairs for cross-lingual alignment.

For more information, please read our [multilingual models blog post](https://huggingface.co/blog/lightonai/mdenseon-mlateon), our [English models blog post](https://huggingface.co/blog/lightonai/denseon-lateon) and our [paper](https://arxiv.org/abs/2607.27178).

## mLateOn

**mLateOn** is a multilingual ColBERT (multi-vector) retrieval model built on mmBERT-base (307M parameters), trained by [LightOn](https://lighton.ai) using [PyLate](https://github.com/lightonai/pylate). It supports context lengths of up to **8,192 tokens** for documents and queries, using MaxSim scoring.

mLateOn notably:
- **Achieves the highest BEIR score among all evaluated models** at 57.56 NDCG@10, surpassing even the English-only LateOn (57.22) and dense baselines up to twice its size, showing that multilingual training can actually *improve* English performance.
- **Leads all models on MIRACL target languages** at 65.61, and remains competitive on the full benchmark (67.04) despite being trained on only nine languages, outperforming most models trained on many more languages.
- **Opens a massive gap on MLDR** at 87.69 on target languages, more than 9 points ahead of the next-best model (LFM2.5-ColBERT-350M at 78.39), combining the multilingual generalization of late interaction with ColBERT's affinity for long-context retrieval.
- **Generalizes to unseen languages**, including scripts not seen during retrieval training (Cyrillic, Japanese, etc), demonstrating that multi-vector representations can transfer to languages absent from retrieval training.
- **Achieves strong code retrieval** at 73.48 on MTEB Code, using only fine-tuning-stage code data.

Perhaps the most important finding: the translate-train recipe applied to a dense encoder produces limited generalization beyond target languages, but applying it to a late-interaction architecture lifts this restriction. With mLateOn, you don't need to exhaustively translate to all target languages, a handful of representative languages is sufficient for broad multilingual coverage.

Alongside mLateOn, we also trained [mDenseOn](https://huggingface.co/lightonai/mDenseOn), a dense (single-vector) variant using the same setup. If your setup does not allow multi-vector, mDenseOn is a strong single-vector alternative, but trades off generalization to unseen languages and long-context performance.

See our [multilingual blog post](https://huggingface.co/blog/lightonai/mdenseon-mlateon) for full results and analysis.


## Results

### Headline Results (NDCG@10)

**MIRACL<sub>tgt</sub>** and **MLDR<sub>tgt</sub>** include only the languages overlapping with our target languages; **MIRACL** and **MLDR** include all benchmark languages.

| Model | Size | BEIR | MIRACL<sub>tgt</sub> | MIRACL | MLDR<sub>tgt</sub> | MLDR | Code |
|---|---|---|---|---|---|---|---|
| **Our models** | | | | | | | |
| mLateOn | 307M | **57.56** | **65.61** | 67.04 | **87.69** | **77.92** | 73.48 |
| mDenseOn | 307M | 56.70 | 59.61 | 58.02 | 64.98 | 51.59 | 71.53 |
| **Dense baselines** | | | | | | | |
| pplx-embed-v1-0.6b | 596M | 56.70 | 63.18 | 68.20 | 57.08 | 43.98 | 75.18 |
| jina-v5-text-small | 677M | 56.70 | 61.03 | 66.56 | 53.00 | 43.83 | 73.01 |
| jina-v5-text-nano | 239M | 56.08 | 60.86 | 65.84 | 56.71 | 47.20 | 70.75 |
| arctic-embed-l-v2 | 568M | 55.55 | 60.78 | 66.53 | 57.01 | 48.03 | 53.17 |
| Qwen3-Embedding-0.6B | 596M | 55.33 | 57.64 | 60.62 | 59.11 | 50.06 | 73.75 |
| harrier-oss-v1-0.6b | 596M | 55.04 | 57.41 | 63.68 | 53.84 | 44.23 | 70.97 |
| harrier-oss-v1-270m | 268M | 50.82 | 48.95 | 57.11 | 52.31 | 42.63 | 63.79 |
| embeddinggemma-300m | 308M | 53.69 | 58.72 | 64.58 | 49.11 | 40.89 | 68.81 |
| gte-multilingual-base | 305M | 51.08 | 57.39 | 64.14 | 66.41 | 56.65 | 57.46 |
| voyage-4-nano | 340M | 49.96 | 49.29 | 58.65 | 62.10 | 51.97 | **76.43** |
| BGE-M3 | 568M | 48.78 | 62.22 | **69.62** | 61.16 | 52.47 | 51.49 |
| granite-311m-r2 | 312M | 49.24 | 53.38 | 59.74 | 50.53 | 41.86 | 63.50 |
| **Late-interaction baselines** | | | | | | | |
| pplx-embed-v1-late-0.6b | 596M | 56.11 | 63.67 | 69.55 | 68.69 | 55.51 | 63.29 |
| LFM2.5-ColBERT-350M | 353M | 54.50 | 57.40 | 42.45 | 78.39 | 61.05 | 51.62 |
| jina-colbert-v2 | 559M | 52.96 | 62.19 | 65.65 | 13.97 | 11.54 | 49.88 |
| GTE-ModernColBERT | 149M | 54.23 | 43.96 | 36.35 | 67.68 | 45.95 | 54.37 |
| ColBERT-Zero | 149M | 55.82 | 43.89 | 39.36 | 71.32 | 49.50 | 53.59 |


### Key Findings

**English quality improved.** mLateOn reaches 57.56 on BEIR, *higher* than the English-only LateOn (57.22). Multilingual training does not degrade English performance; it can enhance it.

**Strongest multilingual retrieval on target languages.** mLateOn leads all models at 65.61 on MIRACL target languages, ahead of pplx-embed-v1-late-0.6b (63.67) and bge-m3 (62.22), both roughly twice its size and trained on substantially more languages.

**Exceptional long-document retrieval.** On MLDR target languages, mLateOn achieves 87.69, a gap of around 9 points over the next-best model. This advantage stems from two complementary sources: the stronger multilingual generalization of late interaction, and ColBERT-style models' well-documented affinity for long-context retrieval, where fine-grained token-level matching exploits longer documents more effectively than a single pooled vector.

**Late interaction generalizes beyond the retrieval-training languages.** On the full MIRACL, mLateOn actually gains from target to full (67.04 vs. 65.61), highlighting exceptional performance on languages never seen during retrieval training. This is in contrast to mDenseOn, which drops about 1.6 points. Even though we trained mostly on Romance languages (plus Arabic), we observe very strong performance on other scripts such as Cyrillic and Japanese.

**For practitioners:** with a late-interaction model, you don't need to exhaustively translate to all target languages. Translating to a handful of representative languages is sufficient for strong multilingual coverage.

## Related Checkpoints

| Model | Description | Link |
|:---|:---|:---|
| **mLateOn** *(this card)* | Multilingual late-interaction retriever (strongest multilingual) | [`lightonai/mLateOn`](https://huggingface.co/lightonai/mLateOn) |
| mLateOn-unsupervised | Multilingual late-interaction, pre-training only | [`lightonai/mLateOn-unsupervised`](https://huggingface.co/lightonai/mLateOn-unsupervised) |
| mDenseOn | Multilingual dense retriever | [`lightonai/mDenseOn`](https://huggingface.co/lightonai/mDenseOn) |
| mDenseOn-unsupervised | Multilingual dense, pre-training only | [`lightonai/mDenseOn-unsupervised`](https://huggingface.co/lightonai/mDenseOn-unsupervised) |
| LateOn | English-only late-interaction retriever | [`lightonai/LateOn`](https://huggingface.co/lightonai/LateOn) |
| LateOn-unsupervised | English-only late-interaction, pre-training only | [`lightonai/LateOn-unsupervised`](https://huggingface.co/lightonai/LateOn-unsupervised) |
| DenseOn | English-only dense retriever | [`lightonai/DenseOn`](https://huggingface.co/lightonai/DenseOn) |
| DenseOn-unsupervised | English-only dense, pre-training only | [`lightonai/DenseOn-unsupervised`](https://huggingface.co/lightonai/DenseOn-unsupervised) |

## Training Data

We release all datasets used to train our English and multilingual embedding models.

### Pre-training Data

* [**Multilingual pre-training curated data**](https://huggingface.co/datasets/lightonai/multilingual-embeddings-pre-training-curated) — **2.16B pairs**
* [**English pre-training curated data**](https://huggingface.co/datasets/lightonai/embeddings-pre-training-curated) — **665M pairs**

Together these form the **2.8B-pair** ready-to-train pre-training mixture. The multilingual corpus spans the eight target languages and includes a **220M-pair cross-lingual split**. The curated English corpus is built after filtering and deduplicating the raw English data. The complete **1.4B-pair** annotated parent dataset is released as [English pre-training unfiltered data](https://huggingface.co/datasets/lightonai/embeddings-pre-training).

### Fine-tuning Data

A ready-to-train fine-tuning mixture of **16.3M samples**, filtered with NV-Retriever methodology to remove false negatives: any mined candidate scoring above **95% of the positive's relevance** is discarded, and the **top 10** surviving hard negatives are kept per sample. The mixture is then annotated with the [mxbai-rerank-large-v2](https://huggingface.co/mixedbread-ai/mxbai-rerank-large-v2) cross-encoder for distillation. We release one dataset per language, plus two code splits:

* [**English**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-en) 
* [**French**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-fr)
* [**Spanish**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-es)
* [**Italian**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-it)
* [**German**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-de)
* [**Portuguese**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-pt)
* [**Arabic**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-ar)
* [**Norwegian**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-no)
* [**Swedish**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-sv)
* [**Code**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-code)
* [**Code Edit**](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-filtered-code-edit)

**Multilingual data.**
**MIRACL and MLDR** hard-negatives were mined directly in the available datasets with [snowflake-arctic-embed-l-v2.0](https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0) (**2,048 mined negatives per sample**) and the full unfiltered set is available at  [embeddings-fine-tuning-multilingual-unfiltered](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-multilingual-unfiltered). **All other splits** follow the translate-train recipe: we apply the mentioned NV-Retriever filtering to the [English fine-tuning unfiltered data](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning), then machine-translate the filtered samples into the eight target languages, carrying the original relevance scores. The unfiltered English fine-tuning parent corpus contains **1.88M examples** with **2,048 mined negatives**, scored with [GTE-ModernBERT](https://huggingface.co/Alibaba-NLP/gte-modernbert-base).


**Code data.**
The **Code** dataset is derived from [LateOn-Code data](https://huggingface.co/datasets/lightonai/nv-embed-supervised-distill-dedup-code), where 2,048 negatives are mined with [GTE-ModernBERT](https://huggingface.co/Alibaba-NLP/gte-modernbert-base). The **Code Edit** dataset had no existing training set, so we built one from [CommitPackFT](https://huggingface.co/datasets/bigcode/commitpackft), decontaminated against the CodeEditSearch evaluation set by removing shared commit SHAs, exact normalized-text matches, and examples with **≥50% 13-gram containment overlap**. Hard-negatives are likewise mined with GTE-ModernBERT, and its unfiltered mined set is released alongside the multilingual data in [embeddings-fine-tuning-multilingual-unfiltered](https://huggingface.co/datasets/lightonai/embeddings-fine-tuning-multilingual-unfiltered).


For more information, please read our [multilingual blog post](https://huggingface.co/blog/lightonai/mdenseon-mlateon) and our [English blog post](https://huggingface.co/blog/lightonai/denseon-lateon).
Training scripts can be found [here](https://github.com/lightonai/mdenseon-mlateon).

## Model Details

### Model Description
- **Model Type:** PyLate ColBERT model
- **Base model:** [mmBERT-base](https://huggingface.co/jhu-clsp/mmBERT-base)
- **Query/Document Length:** 8,192 tokens
- **Output Dimensionality:** 128 dimensions
- **Similarity Function:** MaxSim
- **Languages:** English, French, German, Italian, Spanish, Portuguese, Swedish, Norwegian, Arabic
- **License:** Apache 2.0

### Model Sources

- **Documentation:** [PyLate Documentation](https://lightonai.github.io/pylate/)
- **Repository:** [PyLate on GitHub](https://github.com/lightonai/pylate)
- **Hugging Face:** [PyLate models on Hugging Face](https://huggingface.co/models?library=PyLate)

### Full Model Architecture

```
ColBERT(
  (0): Transformer({'max_seq_length': 8192, 'do_lower_case': False, 'architecture': 'ModernBertModel'})
  (1): Dense({'in_features': 768, 'out_features': 1536, 'bias': False, 'activation_function': 'torch.nn.modules.linear.Identity', 'use_residual': True})
  (2): Dense({'in_features': 1536, 'out_features': 768, 'bias': False, 'activation_function': 'torch.nn.modules.linear.Identity', 'use_residual': True})
  (3): Dense({'in_features': 768, 'out_features': 128, 'bias': False, 'activation_function': 'torch.nn.modules.linear.Identity', 'use_residual': False})
)
```

## Usage

### Sentence Transformers

This model can be used with [Sentence Transformers](https://www.sbert.net/) as a multi-vector (ColBERT-style late interaction) retriever via the `MultiVectorEncoder`:

```bash
pip install "sentence-transformers>=6.0.0"
```

```python
from sentence_transformers import MultiVectorEncoder

model = MultiVectorEncoder("lightonai/mLateOn")

query = "Which planet is the Red Planet?"
documents = [
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",
    "Mars, connu pour son apparence rougeâtre, est souvent appelé la planète rouge.",
    "Mars, bekannt für sein rötliches Erscheinungsbild, wird oft als der Rote Planet bezeichnet.",
    "Venus is often called Earth's twin because of its similar size and proximity.",
]

query_embeddings = model.encode_query(query)
document_embeddings = model.encode_document(documents)
print(query_embeddings.shape, document_embeddings[0].shape)
# (10, 128) (20, 128)

# MaxSim late-interaction scoring (higher is more relevant)
scores = model.similarity(query_embeddings, document_embeddings)
print(scores)
# tensor([[9.6029, 9.5838, 9.5877, 9.4578]])
```

### PyLate

First install the PyLate library:

```bash
pip install -U pylate
```

### Retrieval

Use this model with PyLate to index and retrieve documents. The index uses [FastPlaid](https://github.com/lightonai/fast-plaid) for efficient similarity search.

#### Indexing documents

Load the ColBERT model and initialize the PLAID index, then encode and index your documents:

```python
from pylate import indexes, models, retrieve

# Step 1: Load the ColBERT model
model = models.ColBERT(
    model_name_or_path="lightonai/mLateOn",
)

# Step 2: Initialize the PLAID index
index = indexes.PLAID(
    index_folder="pylate-index",
    index_name="index",
    override=True,  # This overwrites the existing index if any
)

# Step 3: Encode the documents (supports multilingual content)
documents_ids = ["1", "2", "3", "4"]
documents = [
    "Mars, known for its reddish appearance, is often referred to as the Red Planet.",
    "Mars, connu pour son apparence rougeâtre, est souvent appelé la planète rouge.",
    "Mars, bekannt für sein rötliches Erscheinungsbild, wird oft als der Rote Planet bezeichnet.",
    "Venus is often called Earth's twin because of its similar size and proximity.",
]

documents_embeddings = model.encode(
    documents,
    batch_size=32,
    is_query=False,  # Ensure that it is set to False to indicate that these are documents, not queries
    show_progress_bar=True,
)

# Step 4: Add document embeddings to the index by providing embeddings and corresponding ids
index.add_documents(
    documents_ids=documents_ids,
    documents_embeddings=documents_embeddings,
)
```

Note that you do not have to recreate the index and encode the documents every time. Once you have created an index and added the documents, you can re-use the index later by loading it:

```python
# To load an index, simply instantiate it with the correct folder/name and without overriding it
index = indexes.PLAID(
    index_folder="pylate-index",
    index_name="index",
)
```

#### Retrieving top-k documents for queries

Once the documents are indexed, you can retrieve the top-k most relevant documents for a given set of queries — including cross-lingual retrieval:

```python
# Step 1: Initialize the ColBERT retriever
retriever = retrieve.ColBERT(index=index)

# Step 2: Encode the queries (can be in any supported language)
queries_embeddings = model.encode(
    [
        "Quelle planète est connue comme la planète rouge ?",  # French query
        "Which planet is the Red Planet?",                      # English query
    ],
    batch_size=32,
    is_query=True,  # Ensure that it is set to True to indicate that these are queries
    show_progress_bar=True,
)

# Step 3: Retrieve top-k documents (returns matches across all languages)
scores = retriever.retrieve(
    queries_embeddings=queries_embeddings,
    k=10,  # Retrieve the top 10 matches for each query
)
```

### Reranking

If you only want to use the ColBERT model to perform reranking on top of your first-stage retrieval pipeline without building an index, you can simply use the rank function and pass the queries and documents to rerank:

```python
from pylate import rank, models

queries = [
    "Quelle planète est la planète rouge ?",
    "What is the largest planet in the solar system?",
]

documents = [
    ["Mars ist der Rote Planet.", "Venus ist der Zwilling der Erde."],
    ["Jupiter is the largest planet.", "Saturn is known for its rings.", "Mars is the Red Planet."],
]

documents_ids = [
    [1, 2],
    [1, 3, 2],
]

model = models.ColBERT(
    model_name_or_path="lightonai/mLateOn",
)

queries_embeddings = model.encode(
    queries,
    is_query=True,
)

documents_embeddings = model.encode(
    documents,
    is_query=False,
)

reranked_documents = rank.rerank(
    documents_ids=documents_ids,
    queries_embeddings=queries_embeddings,
    documents_embeddings=documents_embeddings,
)
```

### Framework Versions
- Python: 3.11.10
- Sentence Transformers: 5.1.1
- PyLate: 1.3.4
- Transformers: 4.57.5
- PyTorch: 2.9.0+cu128
- Accelerate: 1.12.0
- Datasets: 3.6.0
- Tokenizers: 0.22.1

## Citation

### BibTeX

#### mDenseOn and mLateOn

```bibtex
@misc{sourty2026denseonlateonfullyopen,
  title         = {DenseOn with the LateOn: Fully Open Dense and Late-Interaction Models for Multilingual, Long-Context, and Code Search},
  author        = {Raphaël Sourty and Antoine Chaffin and Paulo Roberto Moura Junior and Amélie Chatelain},
  year          = {2026},
  eprint        = {2607.27178},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/2607.27178},
}
```

#### DenseOn and LateOn
```bibtex
@misc{sourty2026denseonlateon,
  title={DenseOn with the LateOn: Open State-of-the-Art Single and Multi-Vector Models},
  author={Sourty, Raphael and Chaffin, Antoine and Weller, Orion and Moura Junior, Paulo Roberto and Chatelain, Amelie},
  year={2026},
  howpublished={\url{https://huggingface.co/blog/lightonai/denseon-lateon}},
}
```

#### PyLate

```bibtex
@inproceedings{DBLP:conf/cikm/ChaffinS25,
  author       = {Antoine Chaffin and
                  Rapha{\"{e}}l Sourty},
  editor       = {Meeyoung Cha and
                  Chanyoung Park and
                  Noseong Park and
                  Carl Yang and
                  Senjuti Basu Roy and
                  Jessie Li and
                  Jaap Kamps and
                  Kijung Shin and
                  Bryan Hooi and
                  Lifang He},
  title        = {PyLate: Flexible Training and Retrieval for Late Interaction Models},
  booktitle    = {Proceedings of the 34th {ACM} International Conference on Information
                  and Knowledge Management, {CIKM} 2025, Seoul, Republic of Korea, November
                  10-14, 2025},
  pages        = {6334--6339},
  publisher    = {{ACM}},
  year         = {2025},
  url          = {https://github.com/lightonai/pylate},
  doi          = {10.1145/3746252.3761608},
}
```

#### Sentence Transformers

```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084"
}
```

## Acknowledgements


We thank Eugene Yang for his feedback on adapting our English study to multilinguality through translate-train. We again thank Xin Zhang, Zach Nussbaum, Tom Aarsen, Bo Wang, Eugene Yang, Benjamin Clavié, Nandan Thakur, Oskar Hallström and Iacopo Poli for their valuable contributions and feedback on the original English study. We thank Orion Weller for building the FineWeb-derived Common Crawl split as well as for his feedback and help. We are grateful to the teams behind Sentence Transformers, BEIR, and MIRACL, and to the open-source retrieval community, in particular the authors of Nomic Embed.

This work was granted access to the HPC resources of [IDRIS](http://www.idris.fr/) under [GENCI](http://www.genci.fr/) allocations AS011016449, A0181016214, and A0171015706 (Jean Zay supercomputer). We also acknowledge the [Barcelona Supercomputing Center (BSC-CNS)](https://www.bsc.es/) for providing access to MareNostrum 5 under EuroHPC AI Factory Fast Lane project EHPC-AIF-2025FL01-445. This project is also supported by the OpenEuroLLM project, co-funded by the Digital Europe Programme under GA no. 101195233.