# Phiên tra cứu: kiến trúc LLM, attention và Kimi K3

## Phạm vi

Phiên này trả lời các câu hỏi về diễn tiến kiến trúc LLM, các biến thể attention, và kiến trúc Kimi K3. Nguồn truy xuất chính là các concept trong `wiki/`; phần Kimi K3 được đối chiếu trực tiếp với [nguồn raw](../raw/2026-07-27-from-gpt2-to-kimi-k3.md).

## Kết luận đã trao đổi

### Diễn tiến kiến trúc LLM

- Transformer gốc là encoder–decoder với self-attention, cross-attention và FFN.
- GPT chuyển sang decoder-only, causal language modeling; đây là backbone phổ biến của LLM sinh văn bản.
- GPT-2/GPT-3 chủ yếu mở rộng quy mô, context và cải thiện ổn định huấn luyện.
- LLaMA giữ decoder-only nhưng dùng RMSNorm, SwiGLU và RoPE.
- Các nhánh sau đó tối ưu KV cache (MQA/GQA), tăng capacity thưa (MoE), hoặc kết hợp trạng thái hồi quy và truy xuất attention.

### Attention đã thay đổi như thế nào

- Công thức cốt lõi scaled dot-product multi-head attention vẫn được giữ rộng rãi.
- Positional encoding chuyển từ sin/cos cộng vào embedding sang RoPE (xoay Q/K) hoặc ALiBi (bias theo khoảng cách).
- FlashAttention đổi cách thực thi và di chuyển dữ liệu GPU, không đổi công thức exact softmax attention hay bậc hai số phép tính theo độ dài chuỗi.
- MQA/GQA giảm kích thước/băng thông KV cache khi decode bằng cách chia sẻ K/V heads.
- PagedAttention đổi quản lý cache khi serving, không đổi attention toán học.
- Linear attention/KDA đổi trade-off cơ bản: nén lịch sử vào state cố định, tránh cache tăng theo context nhưng có rủi ro nhiễu và mất truy xuất token riêng lẻ.

### Kimi K3 — attention và MoE

Nguồn raw mô tả 92 decoder layer, tổ chức thành 23 macrocycle, mỗi macrocycle gồm ba Kimi Delta Attention (KDA) và một Multi-head Latent Attention (MLA). Layer đầu dùng dense FFN; các layer còn lại dùng latent-space MoE.

- **KDA:** bộ nhớ hồi quy fixed-size, phát triển từ linear attention/DeltaNet. Delta rule sửa association tại key hiện tại; fine-grained decay cho từng channel kiểm soát quên.
- **MLA định kỳ:** giữ đường truy xuất full softmax tới token context để bù cho thông tin có thể bị nén hoặc mất trong KDA.
- **Gated MLA:** gate chiếu từ input nhân theo phần tử với feature đã truy xuất trước khi đưa vào residual stream.
- **Attention Residuals:** attention trên biểu diễn residual theo chiều sâu model, áp dụng theo block 12 layer; chọn/trộn các residual state thay vì cộng đồng đều.
- **MoE:** nguồn nói model có 898 experts: hai shared experts luôn chạy, 896 routed experts và router chọn 16 routed experts cho mỗi token.
- **Latent-space MoE và SiTU:** expert hoạt động trong không gian nén; SiTU thay activation gate SiLU thông thường. Nguồn có pseudocode SiTU nhưng không có đặc tả chính thức đầy đủ.

### Lineage các module được nêu

| Module | Công trình/lineage nêu hoặc ám chỉ | Mức độ chứng cứ trong kho |
|---|---|---|
| Delta rule / fast-weight memory | *Linear Transformers Are Secretly Fast Weight Programmers* (Schlag et al.) | Bài raw nhắc “Schlag’s paper”; primary paper không có trong kho. |
| Chunked DeltaNet | *Parallelizing Linear Transformers with the Delta Rule over Sequence Length* | Tựa đề được raw nêu trực tiếp; primary paper không có trong kho. |
| Gated decay | Mamba-2 | Raw quy phần scalar decay cho Mamba-2; primary paper không có trong kho. |
| Per-channel KDA, hybrid KDA–MLA | Kimi Linear | Raw mô tả K3 kế thừa Kimi Linear; primary paper không có trong kho. |
| MLA | Thường được liên hệ với DeepSeek-V2 | Raw không xác nhận K3 lấy trực tiếp từ DeepSeek-V2. |
| Query LoRA | *LoRA: Low-Rank Adaptation of Large Language Models* | K3 raw chỉ nói MLA query LoRA, không nêu rank/cấu hình. |
| Shared/routed MoE | Tương đồng DeepSeekMoE | Raw không xác nhận quan hệ kế thừa; thông số K3 khác. |
| Gated MLA, latent-space MoE, SiTU, AttnRes | Không có paper nguồn được raw dẫn | Không thể gán nguồn chính thức từ bằng chứng hiện có. |

## Giới hạn và mâu thuẫn cần lưu ý

- Thông tin Kimi K3 hiện xuất phát từ một bài giải thích trên X, không phải paper, model card hay code chính thức; các con số hiệu năng và chi tiết triển khai chưa được xác minh độc lập.
- Raw nói FlashAttention được phát hành năm 2020, trong khi concept wiki ghi công trình FlashAttention năm 2022. Không dùng mốc 2020 của raw như dữ kiện lịch sử.
- Các liên hệ MLA–DeepSeek-V2 và shared-expert MoE–DeepSeekMoE chỉ là lineage kỹ thuật, không phải chứng cứ K3 sao chép hay kế thừa trực tiếp.

## Liên kết wiki đã dùng

- [Transformer sequence transduction architecture](../wiki/transformer-sequence-transduction-architecture.md)
- [Scaled dot-product and multi-head attention](../wiki/scaled-dot-product-and-multi-head-attention.md)
- [FlashAttention IO-aware exact attention](../wiki/flashattention-io-aware-exact-attention.md)
- [Multi-query and grouped-query attention](../wiki/multi-query-and-grouped-query-attention.md)
- [Linear attention as fixed-state memory](../wiki/linear-attention-as-fixed-state-memory.md)
- [Delta-rule and gated associative memory](../wiki/delta-rule-and-gated-associative-memory.md)
- [Kimi K3 hybrid retrieval architecture](../wiki/kimi-k3-hybrid-retrieval-architecture.md)
- [Attention Residuals](../wiki/attention-residuals.md)
- [DeepSeekMoE expert specialization](../wiki/deepseekmoe-expert-specialization.md)
- [LoRA low-rank adaptation](../wiki/lora-low-rank-adaptation.md)
