Có. Sau khi tìm các paper gần đây, **“N-gram embeddings in LLM” hiện là một hướng nghiên cứu khá rõ, thường được gọi rộng hơn là *embedding scaling*, *n-gram embedding*, *over-encoding*, hoặc *conditional memory*.** Đặc biệt từ 2025–2026 có khá nhiều paper trực tiếp về nó.

### N-gram embedding trong LLM là gì?

Giả sử tokenizer cho chuỗi:

`New → York → City → is → ...`

LLM thông thường có embedding riêng cho từng token:

[
e_i = E_0(t_i)
]

Với **N-gram embedding**, tại vị trí `City`, model có thể đồng thời lấy representation cho:

* unigram: `City`
* bigram: `York City`
* trigram: `New York City`

Một dạng rất phổ biến hiện nay là:

[
e_i =
E_0(t_i)
+
\sum_{n=2}^{N}
E_n\left(
H_n(t_{i-n+1},...,t_i)
\right)
]

Trong đó (H_n) thường là **hash function**, vì nếu vocabulary có (V) token thì lưu trực tiếp mọi n-gram cần (V^n) entries — không khả thi. N-gram được hash vào một embedding table lớn rồi vector đó được cộng/fuse vào representation của token. Paper LongCat 2026 mô tả gần như chính xác formulation này. ([alphaXiv][1])

Điểm quan trọng là **n-gram embedding không phải n-gram language model cổ điển**. N-gram LM cổ điển trực tiếp ước lượng

[
P(t_i\mid t_{i-n+1},...,t_{i-1})
]

từ count/statistics. Trong n-gram embedding, chuỗi n-token chỉ đóng vai trò **key để lấy một vector học được**, rồi Transformer vẫn thực hiện phần reasoning/prediction phía sau.

Ý tưởng trực giác là: thay vì bắt Transformer dùng nhiều layer để liên tục “học lại” rằng `New York`, `machine learning`, `Hong Kong`, `for example`, một đoạn code phổ biến... là các pattern thường xuất hiện, ta đưa cho nó một **lookup memory cực rẻ** cho những pattern local đó. Embedding lookup gần như (O(1)), nên có thể thêm hàng tỷ parameter dạng sparse mà không làm FLOPs tăng tương ứng. Đây chính là động lực của Over-Encoding, SCONE, Engram và LongCat. ([Proceedings of Machine Learning Research][2])

### Các paper mình khuyên đọc

| Paper                                                                                                      | Ý chính                                                                                                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling — Huang et al., ICML 2025**            | Một trong những paper trực tiếp nhất. Đề xuất **Over-Encoding (OE)**: cộng hierarchical 1-, 2-, 3-... gram embeddings vào input. Họ tăng input vocabulary đến 12.8M và thấy scaling input embedding giúp mạnh trong khi chi phí tính toán tăng rất ít. ([Proceedings of Machine Learning Research][2])    |
| **Scaling Embedding Layers in Language Models (SCONE) — Yu et al., NeurIPS 2025**                          | **Scalable Contextualized Offloaded N-gram Embedding**. Lưu embedding cho frequent n-grams; embeddings được học bởi model phụ, precompute rồi offload khỏi accelerator. Model 1B accelerator-resident parameters vượt baseline 1.9B với khoảng một nửa inference FLOPs/memory. ([Proceedings NeurIPS][3]) |
| **Byte Latent Transformer: Patches Scale Better Than Tokens — Pagnoni et al., ACL 2025**                   | BLT sử dụng **hash byte n-gram embeddings**, thường n=3…8. Đây là ví dụ rất hay nếu muốn hiểu cơ chế hash-n-gram thực tế ở LLM byte-level. ([arXiv][4])                                                                                                                                                   |
| **Conditional Memory via Scalable Lookup — Cheng et al., 2026 (DeepSeek Engram)**                          | Đẩy ý tưởng xa hơn: n-gram embedding trở thành **conditional memory** nằm trong các layer của Transformer. Hash n-gram → lookup memory → context-aware gating → hidden state. Paper báo cáo Engram 27B memory parameters cải thiện knowledge, reasoning, math/code và long-context. ([arXiv][5])          |
| **Scaling Embeddings Outperforms Scaling Experts in Language Models — Liu et al., 2026 / LongCat**         | Nghiên cứu rất trực tiếp về **N-gram Embedding scaling vs MoE scaling**. LongCat-Flash-Lite có 68.5B total parameters, trong đó hơn 30B dành cho embeddings, nhưng chỉ khoảng 3B activated. ([arXiv][6])                                                                                                  |
| **Tensorizing Engram: Sharing Latents Across N-Gram Embeddings is Beneficial in LLMs — Zhou et al., 2026** | Giải quyết nhược điểm của Engram/OE: mỗi order có hash table riêng và hash collisions. Đề xuất **TN-gram**, factorize n-gram embeddings bằng CP decomposition để các n-gram chia sẻ latent factors và dùng ít parameter hơn. ([arXiv][7])                                                                 |
| **Lngram: N-gram Conditional Memory in Latent Space — Zheng et al., 2026**                                 | Thay vì n-gram trên token IDs, học discrete symbols từ **hidden latent states**, rồi làm n-gram memory trên latent space → bớt phụ thuộc tokenizer và có thể áp dụng ngoài text. ([arXiv][8])                                                                                                             |
| **Tokenizer-Agnostic Engram Module — Lim & Chieu, 2026**                                                   | Giải quyết việc Engram bị khóa với tokenizer cụ thể: dùng byte-equivalent sequences + polynomial hashing để reuse n-gram memory giữa tokenizer khác nhau. ([arXiv][9])                                                                                                                                    |

Nếu chỉ đọc **3 paper để nắm research direction**, mình sẽ chọn theo thứ tự:

**1. Over-Tokenized Transformer (ICML 2025)** → hiểu n-gram embedding cơ bản và Over-Encoding. [Over-Tokenized Transformer paper](https://proceedings.mlr.press/v267/huang25bb.html?utm_source=chatgpt.com)

**2. SCONE (NeurIPS 2025)** → hiểu frequent/contextualized n-gram embedding + offloading. [SCONE paper](https://proceedings.neurips.cc/paper_files/paper/2025/hash/2e067924aeeb02ae9919803fd08d8b4b-Abstract-Conference.html?utm_source=chatgpt.com)

**3. DeepSeek Engram (2026)** → hướng hiện đại hơn: coi n-gram embeddings là một loại **memory primitive** bổ sung cho attention/MoE. [Engram paper on arXiv](https://arxiv.org/abs/2601.07372?utm_source=chatgpt.com)

Có một lịch sử dài hơn phía sau. **fastText** năm 2017 đã biểu diễn word bằng tổng các **character n-gram embeddings**, tức ý tưởng “một unit được biểu diễn bằng composition của n-gram vectors” đã có từ khá lâu. ([ACL Anthology][10]) **CANINE** (TACL 2022) sau đó là một precursor quan trọng cho character/tokenizer-free representation; các paper 2026 như LongCat trực tiếp liệt kê CANINE trong lineage của n-gram embedding hiện đại. ([ACL Anthology][11])

Có một nhánh liên quan nhưng **không hoàn toàn là n-gram embedding** là **SuperBPE**: thay vì giữ `"New" "York"` rồi lookup thêm embedding cho `"New York"`, nó biến frequent multi-word expressions thành **token thực sự trong tokenizer**. SuperBPE 2025 báo cáo ít token hơn và cải thiện downstream performance, nên rất đáng đọc để so sánh “n-gram as token” với “n-gram as auxiliary embedding/memory”. ([arXiv][12])

**Tóm gọn research landscape hiện tại:**

`fastText character n-grams`
→ `CANINE / byte-level representations`
→ `BLT hash n-gram embeddings`
→ **`Over-Encoding / SCONE`**
→ **`Engram conditional memory`**
→ `LongCat embedding scaling / TN-gram / Lngram / tokenizer-agnostic Engram`.

Nếu bạn đang định **làm research về N-gram embedding cho LLM**, thì hiện tại mình thấy câu hỏi thú vị nhất không còn là “n-gram có giúp không?” mà là **lưu n-gram memory thế nào để scale đến hàng chục tỷ parameters mà tránh hash collision, không phụ thuộc tokenizer, và không bị memory-bandwidth bottleneck**. Các paper Engram, LongCat và TN-gram đang đi đúng vào ba vấn đề đó. ([arXiv][5])

[1]: https://www.alphaxiv.org/abs/2601.21204v2 "Scaling Embeddings Outperforms Scaling Experts in Language Models | alphaXiv"
[2]: https://proceedings.mlr.press/v267/huang25bb.html?utm_source=chatgpt.com "Over-Tokenized Transformer: Vocabulary is Generally Worth Scaling"
[3]: https://proceedings.neurips.cc/paper_files/paper/2025/hash/2e067924aeeb02ae9919803fd08d8b4b-Abstract-Conference.html?utm_source=chatgpt.com "Scaling Embedding Layers in Language Models"
[4]: https://arxiv.org/abs/2412.09871 "Byte Latent Transformer: Patches Scale Better Than Tokens"
[5]: https://arxiv.org/abs/2601.07372?utm_source=chatgpt.com "Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models"
[6]: https://arxiv.org/abs/2601.21204?utm_source=chatgpt.com "Scaling Embeddings Outperforms Scaling Experts in Language Models"
[7]: https://arxiv.org/abs/2606.08347?utm_source=chatgpt.com "Tensorizing Engram: Sharing Latents Across N-Gram Embeddings is Beneficial in LLMs"
[8]: https://arxiv.org/abs/2605.24869?utm_source=chatgpt.com "Lngram: N-gram Conditional Memory in Latent Space"
[9]: https://arxiv.org/abs/2607.29065?utm_source=chatgpt.com "Tokenizer-Agnostic Engram Module"
[10]: https://aclanthology.org/Q17-1010/?utm_source=chatgpt.com "Enriching Word Vectors with Subword Information - ACL Anthology"
[11]: https://aclanthology.org/2022.tacl-1.5/ "Canine: Pre-training an Efficient Tokenization-Free Encoder for Language Representation - ACL Anthology"
[12]: https://arxiv.org/abs/2503.13423?utm_source=chatgpt.com "SuperBPE: Space Travel for Language Models"
