---
library_name: transformers
tags:
- XProvence
- RAG
- Multilingual
- Provence
license: cc-by-nc-nd-4.0
language:
- ar
- en
- fr
- es
- bn
- fa
- fi
- hi
- id
- ja
- ko
- ru
- sw
- te
- th
- zh
base_model:
- BAAI/bge-reranker-v2-m3
pipeline_tag: text-ranking
---

# Model Card for XProvence-reranker

<img src="https://cdn-uploads.huggingface.co/production/uploads/6273df31c3b822dad2d1eef2/4n-bxYfiMPC2LoLM2m7pg.png" alt="image/png" width="600">

XProvence is a Zero Cost **context pruning model** that seamlessly integrates with reranker for retrieval-augmented generation, 
particularly **optimized for question answering**. Given a user question and a retrieved passage, XProvence **removes sentences 
from the passage that are not relevant to the user question**. This **speeds up generation** and **reduces context noise**, in 
a plug-and-play manner **for any LLM**. 

XProvence is a multilingual version of [Provence](https://huggingface.co/naver/provence-reranker-debertav3-v1) supporting 16 languages natively. It also supports 100+ languages through cross lingual transfer, since 
it is based on BGE-m3 which is pretrained on 100+ languages. 


*Paper*: [XProvence: Zero-Cost Multilingual Context Pruning for Retrieval-Augmented Generation](https://arxiv.org/abs/2601.18886) (ECIR'26)  
*Developed by*: Naver Labs Europe  
*License*: XProvence is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 license [CC BY-NC-ND 4.0 license]. 
[License file](https://huggingface.co/naver/xprovence-reranker-bgem3-v1/blob/main/xProvence%20LICENSE.txt)
* *Model*: `XProvence` 
* *Backbone model*: [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3)
* *Model size*: 568 million parameters  
* *Context length*: 8192 tokens
* *Developed by*: Naver Labs Europe  

Training and evaluation code & data are available in the [Bergen repo](https://github.com/naver/bergen/blob/main/scripts/xprovence/)

## Usage

XProvence uses `spacy`:

```bash
pip install spacy
python -m spacy download xx_sent_ud_sm
```

Pruning a single context for a single question:

```python
from transformers import AutoModel

xprovence = AutoModel.from_pretrained("naver/xprovence-reranker-bgem3-v2", trust_remote_code=True)

context = "Shepherd’s pie. History. In early cookery books, the dish was a means of using leftover roasted meat of any kind, and the pie dish was lined on the sides and bottom with mashed potato, as well as having a mashed potato crust on top. Variations and similar dishes. Other potato-topped pies include: The modern ”Cumberland pie” is a version with either beef or lamb and a layer of bread- crumbs and cheese on top. In medieval times, and modern-day Cumbria, the pastry crust had a filling of meat with fruits and spices.. In Quebec, a varia- tion on the cottage pie is called ”Paˆte ́ chinois”. It is made with ground beef on the bottom layer, canned corn in the middle, and mashed potato on top.. The ”shepherdess pie” is a vegetarian version made without meat, or a vegan version made without meat and dairy.. In the Netherlands, a very similar dish called ”philosopher’s stew” () often adds ingredients like beans, apples, prunes, or apple sauce.. In Brazil, a dish called in refers to the fact that a manioc puree hides a layer of sun-dried meat."
question = 'What goes on the bottom of Shepherd’s pie?'

xprovence_output = xprovence.process(question, context)
# print(f"XProvence Output: {xprovence_output}")
# XProvence Output: {'pruned_context': 'In early cookery books, the dish was a means of using leftover roasted meat of any kind, and the pie dish was lined on the sides and bottom with mashed potato, as well as having a mashed potato crust on top. It is made with ground beef on the bottom layer, canned corn in the middle, and mashed potato on top.. The ”shepherdess pie” is a vegetarian version made without meat, or a vegan version made without meat and dairy..', 'reranking_score': 3.260809, 'compression_rate': 59.50334288443171}
```

You can also pass a list of questions and a list of lists of contexts (multiple contexts per question to be pruned) for batched processing.

Setting `always_select_title=True` will keep the first sentence "Shepherd’s pie". This is especially useful for Wikipedia articles where the title is often needed to understand the context.
More details on how the title is defined are given below.

```python
xprovence_output = xprovence.process(question, context, always_select_title=True)
# print(f"XProvence Output: {xprovence_output}")
# XProvence Output: {'pruned_context': 'Shepherd’s pie. In early cookery books, the dish was a means of using leftover roasted meat of any kind, and the pie dish was lined on the sides and bottom with mashed potato, as well as having a mashed potato crust on top. It is made with ground beef on the bottom layer, canned corn in the middle, and mashed potato on top.. The ”shepherdess pie” is a vegetarian version made without meat, or a vegan version made without meat and dairy..', 'reranking_score': 3.260809, 'compression_rate': 57.97516714422159}
```

## Model interface

Interface of the `process` function:
* `question`: `Union[List[str], str]`: an input question (str) or a list of input questions (for batched processing)
* `context`: `Union[List[List[str]], str]`: context(s) to be pruned. This can be either a single string (in case of a singe str question), or a list of lists contexts (a list of contexts per question), with `len(contexts)` equal to `len(questions)`
*  `title`: `Optional[Union[List[List[str]], str]]`, _default: “first_sentence”_: an optional argument for defining titles. If `title=first_sentence`, then the first sentence of each context is assumed to be the title. If `title=None`, then it is assumed that no titles are provided. Titles can be also passed as a list of lists of str, i.e. titles shaped the same way as contexts. Titles are only used if `always_select_title=True`.
* `threshold` _(float, \\(\in [0, 1]\\), default 0.3)_: which threshold to use for context pruning. We recommend 0.3 for more conservative pruning (no performance drop or lowest performance drops) and 0.7 for higher compression, but this value can be further tuned to meet the specific use case requirements.
* `always_select_title` _(bool, default: True)_: if True, the first sentence (title) will be included into the selection each time the model select a non-empty selection of sentences. This is important, e.g., for Wikipedia passages, to provide proper contextualization for the next sentences.
* `batch_size` (int, default: 32)
* `reorder` _(bool, default: False)_: if True, the provided contexts for each question will be reordered according to the computed question-passage relevance scores. If False, the original user-provided order of contexts will be preserved.
* `top_k` _(int, default: 5)_: if `reorder=True`, specifies the number of top-ranked passages to keep for each question.
* `enable_warnings` _(bool, default: True)_: whether the user prefers the warning about model usage to be printed, e.g. too long contexts or questions.

## Model features

* **XProvence natively supports 16 languages**.
* **XProvence supports 100+ languages via cross lingual transfer**.
* **XProvence encodes all sentences in the passage together**: this enables capturing of coreferences between sentences and provides more accurate context pruning.
* **XProvence automatically detects the number of sentences to keep**, based on a threshold. We found that the default value of a threshold works well across various domains, but the threshold can be adjusted further to better meet the particular use case needs.
* **XProvence works out-of-the-box with any LLM**.


## Model Details

* Input: user question (e.g., a sentence) + retrieved context passage (e.g., a paragraph). Training data consisted of monolingual examples (query and context in the same language), but we expect the model to perform well on cross-lingual pairs too, due to cross-lingual transfer. 
* Output: pruned context passage, i.e., irrelevant sentences are removed + relevance score (can be used for reranking)
* Model Architecture: The model was initialized from [bge-reranker-v2-m3](https://huggingface.co/BAAI/bge-reranker-v2-m3) and finetuned with two objectives: (1) output a binary mask which can be used to prune irrelevant sentences; and (2) preserve initial reranking capabilities. 
* Training data:
    * English [MS Marco](https://microsoft.github.io/msmarco/Datasets.html) + a translation of its subset into 16 languages
    * Training data can be found  in the [Bergen repo](https://github.com/naver/bergen/blob/main/scripts/xprovence/)
* Languages in the training data: Arabic, Bengali, English, Spanish, Persian, Finnish, France, Hindi, Indonesian, Japanese, Korean, Russian, Swahili, Telugu, Thai, Chinese
* Context length: 8192 tokens (similar to the pretrained BGE-m3 model). However, training data only included paragraph-sized examples.
* Evaluation: we evaluate XProvence on 26 languages from 6 different datasets. We find that XProvence is able to prune irrelevant sentences with little-to-no drop in performance, on all languages, and outperforms existing baselines on the Pareto front.


## License

This work is licensed under CC BY-NC-ND 4.0. 

## Cite

```
@misc{mohamed2026xprovence,
      title={XProvence: Zero-Cost Multilingual Context Pruning for Retrieval-Augmented Generation}, 
      author={Mohamed, Youssef and Elhoseiny, Mohamed and Formal, Thibault and Chirkova, Nadezhda},
      year={2026},
      eprint={2601.18886},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2601.18886}, 
}
```