---
license: apache-2.0
pipeline_tag: text-ranking
language:
- zh
- en
- es
- fr
- de
- ru
- ko
- ja
library_name: transformers
---
# Querit-Reranker

## HighLights
Querit-Reranker is the first self-developed model released by the Querit family, specifically designed for text ranking tasks. This model is based on Querit’s self-developed MoE foundation model, and inherits the foundation model’s excellent multilingual capabilities, long text comprehension, and reasoning abilities. It has also undergone post-training customization for ranking tasks using a vast amount of open-source and proprietary data, achieving a technological breakthrough in multilingual text ranking tasks.

### Model Description

<!-- Provide a longer summary of what this model is. -->


- **Model type:** Text Reranking
- **Language(s) (NLP):** Multilingual (Chinese, English, Spanish, French, German, Russian, Korean, Japanese)
- **Training Stage:** Pretraining & Post-training
- **Number of Total Parameters:** 4.92B-A0.43B
- **Number of Paramaters (Non-Embedding):** 4.79B
- **Number of Layers:** 24
- **Number of Attention Heads:** 16
- **Context Length:** 128k

## Citation

If you find Querit-Reranker useful for your research or applications, please cite our paper:

**Querit-Reranker: Training Compact Multilingual Rerankers via Efficient Label-Free Distribution Adaptation**
Yunfei Zhong, Jun Yang, Wei Huang, Yinqiong Cai, Haosheng Qian, Yixing Fan, Ruqing Zhang, Lixin Su, Daiting Shi, and Jiafeng Guo.
arXiv:2606.19037, 2026.

```bibtex
@misc{zhong2026queritrerankertrainingcompactmultilingual,
      title={Querit-Reranker: Training Compact Multilingual Rerankers via Efficient Label-Free Distribution Adaptation}, 
      author={Yunfei Zhong and Jun Yang and Wei Huang and Yinqiong Cai and Haosheng Qian and Yixing Fan and Ruqing Zhang and Lixin Su and Daiting Shi and Jiafeng Guo},
      year={2026},
      eprint={2606.19037},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2606.19037}, 
}
```
