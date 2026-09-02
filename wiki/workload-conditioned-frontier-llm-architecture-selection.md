---
type: Synthesis
title: Workload-conditioned frontier LLM architecture selection
description: A general-purpose recommendation favors recurrent-plus-periodic-latent-attention MoE, while token-addressable sparse attention remains preferable when exact long-context retrieval dominates.
tags: [architecture-selection, hybrid-attention, long-context, mixture-of-experts, serving]
status: stable
created: 2026-08-15
generated: { by: llm-wiki-agent/1, at: 2026-09-02T15:06:21+07:00 }
sources:
  - id: qwen38-config
    resource: ../raw/Qwen3.8-2.4T-A95B/config.json
    title: Qwen3.8-2.4T-A95B checkpoint configuration
  - id: qwen38-modeling
    resource: ../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py
    title: Qwen3.5-MoE Transformers reference implementation
  - id: glm5-report
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: kimi-k3-report
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
---

# Workload-conditioned frontier LLM architecture selection

Không có backbone tốt nhất độc lập với workload. Nếu phải chọn **một hướng mặc định cho model general-purpose dài ngữ cảnh**, synthesis này chọn lớp thiết kế kiểu Kimi/Qwen: nhiều layer recurrent delta-memory, xen kẽ attention latent toàn cục, và sparse MoE. Nó giảm state tăng theo chuỗi ở phần lớn layer nhưng không từ bỏ hoàn toàn token retrieval. Đây là đề xuất kỹ thuật dựa trên trade-off đã tài liệu hóa, **không phải** kết quả benchmark đối chứng cho thấy nó hơn GLM-5 hay Kimi K3 ở mọi metric.[^qwen38-config][^qwen38-modeling][^glm5-report][^kimi-k3-report]

## Lựa chọn theo requirement

| Requirement quyết định | Hướng nên chọn | Lý do và điều kiện |
|---|---|---|
| Chat/agent/coding tổng quát, context dài, nhiều workload chưa biết trước | **Hybrid recurrent + periodic global MLA/GQA** | Recurrent layers giữ state bounded; periodic attention khôi phục direct global retrieval. Đo cả retrieval, TTFT và TPOT trước khi chốt tỷ lệ layer. |
| Truy xuất chính xác token cụ thể ở phần lớn layer là quan trọng nhất | **MLA + DSA kiểu GLM-5** | Duy trì token-addressable state xuyên backbone; DSA chỉ giảm tập token được đọc, không thay nó bằng fixed state. Chấp nhận cache và indexer vẫn tăng theo context.[^glm5-report] |
| Streaming/decode rất dài, memory per request là ràng buộc chính | **Tăng tỷ trọng recurrent delta-memory** | Recurrent state không tăng theo token count; vẫn cần global-attention checkpoints hoặc external retrieval để kiểm tra mất chi tiết/association interference.[^qwen38-modeling][^kimi-k3-report] |
| Ảnh/video là first-class input | **Hybrid backbone + vision encoder native** | K3 tài liệu hóa encoder MoonViT-V2 và joint text-image-video pre-training; text-only backbone không tự có năng lực thị giác.[^kimi-k3-report] |

## Kiến trúc đề xuất mặc định

1. Dùng pattern khởi đầu **ba recurrent delta-memory layers : một global latent-attention layer**. Qwen3.8 và Kimi K3 đều dùng tỷ lệ này, nhưng số layer và loại attention khác nhau; tỷ lệ phải được ablate theo context và hardware mục tiêu.[^qwen38-config][^kimi-k3-report]
2. Ưu tiên **MLA** cho global layers khi decode-cache bandwidth là vấn đề; MLA vẫn token-addressable nhưng nén representation per token. GQA là phương án đơn giản hơn để giảm số KV heads.[^glm5-report][^qwen38-config]
3. Dùng MoE như cơ chế capacity, không dùng total/active parameter count làm proxy cho latency. Expert count, top-k, placement, batch shape và all-to-all phải được chọn từ profiling; không có bằng chứng trong các nguồn này để coi 256/top-8, 512/top-10 hay 896/top-16 là optimum phổ quát.[^qwen38-modeling][^glm5-report][^kimi-k3-report]
4. Chỉ thêm DSA ở global-attention layers khi profile cho thấy long-context attention là bottleneck và retrieval evaluation giữ được chất lượng. DSA thêm indexer, sparse selection và cache riêng, nên không mặc định thắng trên context ngắn hoặc kernel không phù hợp.[^glm5-report]
5. Xem Block Attention Residuals là thành phần tuỳ chọn cho backbone rất sâu: nó thêm retrieval theo depth, nhưng không thay global token retrieval và cần ablation riêng.[^kimi-k3-report]

## Blueprint tham chiếu: Hybrid-96

Đây là **proposal** cho một text-first general-purpose model; các kích thước là điểm khởi đầu cho scaling study và không phải kết quả thực nghiệm. Nó ghép các cơ chế đã có bằng chứng riêng lẻ, chứ không tuyên bố bundle này đã được chứng minh tốt hơn Qwen3.8, GLM-5 hay Kimi K3.

| Phần | Cấu hình đề xuất | Mục đích |
|---|---|---|
| Backbone | Decoder-only, 96 layers, width 8,192, RMSNorm/pre-norm; BPE vocabulary 200K, tied input/output embeddings; target context 1,048,576 | Đủ sâu để có capacity, nhưng vẫn tổ chức thành 24 block 4-layer dễ ablate. Vocabulary/context là target training, không phải guarantee về recall. |
| Sequence schedule | Mỗi block: `Delta × 3 → Gated MLA × 1`; tổng 72 Delta + 24 MLA | Kế thừa trade-off hybrid đã dùng ở Qwen/Kimi: main path fixed state, checkpoint global retrieval.[^qwen38-config][^kimi-k3-report] |
| Delta layer | 16 Q/K heads × 128, 128 V heads × 128; depthwise causal conv width 4 → SiLU; normalized Q/K; learned sigmoid write; channel-wise negative decay có lower bound; full-rank output gate; chunk kernel khi prefill và recurrent kernel khi decode | Giữ state association + conv state không tăng theo context; lower-bound decay và output gate theo hướng K3 để ổn định tile BF16.[^qwen38-modeling][^kimi-k3-report] |
| MLA layer | 64 query heads × 128; joint per-token KV latent 512; query latent 2,048; NoPE trong MLA; Delta hidden states mang position/recency | Retain token-addressable global retrieval với cache nén. Dùng NoPE là hypothesis của blueprint, phải so với decoupled RoPE ablation.[^glm5-report][^kimi-k3-report] |
| Long-context mode | Full MLA dưới ngưỡng context được benchmark; DSA chỉ bật ở MLA layers vượt ngưỡng đó, chọn tối đa 2,048 token quá khứ cộng local window | Giới hạn prefill attention reads ở context rất dài nhưng không trả DSA overhead cho mọi request. Ngưỡng và recall phải được tune theo workload.[^glm5-report] |
| FFN/MoE | Ba layers đầu dense SwiGLU width 32,768; 93 layers sau dùng 512 routed SwiGLU experts width 2,048, top-8, một shared expert width 2,048; router scoring/bias bằng float32 và balance theo load | Với untied expert weights, riêng routed expert FFN xấp xỉ 2.4T parameters; đây là lựa chọn midpoint để thử nghiệm giữa GLM (256/top-8), Qwen (512/top-10), và K3 (896/top-16), không phải optimum đã xác lập.[^qwen38-modeling][^glm5-report][^kimi-k3-report] |
| Depth retrieval | Sau mỗi block 12 layers, cache một block representation; Block AttnRes chỉ đọc các block summaries này | Cung cấp retrieval qua depth với state nhỏ hơn cache mọi layer; cần bỏ nếu ablation không bù được overhead.[^kimi-k3-report] |
| Prediction heads | Next-token head chính; 3 depth MTP share parameter chỉ cho speculative-draft training/inference khi acceptance bù được overhead | Lấy hướng shared sequential MTP của GLM-5; không kích hoạt nếu serving measurement không có lợi.[^glm5-report] |
| Modality | Text backbone trước; nếu cần vision, thêm encoder riêng và projector vào token space thay vì buộc mọi deployment tải vision stack | Giữ text serving gọn; native multimodality là extension cần pre-training/evaluation riêng.[^kimi-k3-report] |

### Luồng một token

```text
input token
  → RMSNorm → [Delta, Delta, Delta, global Gated MLA] × 24
  → Block AttnRes ở boundary mỗi 12 layers
  → RMSNorm → LM head → next-token logits

mỗi decoder layer: token mixer → residual → RMSNorm → dense/MoE FFN → residual
```

- Context curriculum đề xuất: 8K → 32K → 128K → 512K → 1M; chỉ tăng stage sau khi retrieval, loss và numerical stability đạt gate định trước.
- Ở **prefill**, Delta layers chạy chunkwise; MLA tạo latent cache, còn DSA (nếu bật) lập index và sparse selection.
- Ở **decode**, Delta layers chỉ cập nhật recurrent/convolution state; MLA đọc latent cache theo token. Vì vậy cache vẫn không fixed-size end-to-end.
- MoE experts phải shard theo expert-parallel group, có static capacity shapes và overlap dispatch/compute/combine; nếu profile cho thấy all-to-all là bottleneck, giảm top-k/expert fan-out trước khi tăng model size.

### Thứ tự ablation bắt buộc

1. So `3:1` với `2:1`, `4:1`, và full MLA trên cùng data/compute.
2. So NoPE MLA với decoupled RoPE MLA; đo recall theo vị trí, không chỉ perplexity.
3. Chỉ bật DSA sau khi đo riêng prefill/decode ở context dài; báo cáo indexer cost, recall và kernel utilization.
4. So dense, 256/top-8, 512/top-8, và 512/top-10 MoE trên topology đích; báo total-weight memory, all-to-all time, overflow và tail latency.
5. Giữ AttnRes và MTP chỉ khi ablation cải thiện task mục tiêu và end-to-end serving metric.

## Điều không thể suy ra từ kiến trúc

- Kimi-style hybrid không được chứng minh nhanh hơn GLM-style MLA/DSA trong mọi pha. Prefill, decode, concurrency, cache policy, precision, topology và kernel có thể đảo chiều kết quả.
- Active parameters thấp không đủ để dự đoán chi phí: total-weight residency, router, expert dispatch/combine, KV/indexer state và utilization đều đáng kể.
- Context window công bố không chứng minh recall đáng tin cậy ở mọi vị trí hay mọi task. Mỗi lựa chọn phải đo long-context retrieval/copy, coding-agent, multimodal (nếu có), TTFT, TPOT, throughput và tail latency trên workload thật.

## Relationships

- **Taught by:** [Workload-conditioned architecture selection — khóa học cho người mới](workload-conditioned-architecture-selection-beginners-course.md), which turns this recommendation into a beginner-first requirement ledger, runnable toy, and matched-ablation procedure.
- **Synthesizes:** [Qwen3.8-2.4T-A95B checkpoint architecture](qwen3-8-2-4t-a95b-checkpoint-architecture.md), [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md), and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Uses framework from:** [Sequence-model architecture taxonomy](sequence-model-architecture-taxonomy.md) and [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md).
- **Depends on:** [LLM inference lifecycle: training, prefill, decode, and latency](llm-inference-lifecycle-training-prefill-decode-and-latency.md) for workload-specific serving evaluation.

[^qwen38-config]: Qwen Team, “Qwen3.8-2.4T-A95B checkpoint configuration,” [source](../raw/Qwen3.8-2.4T-A95B/config.json).
[^qwen38-modeling]: Qwen Team and Hugging Face, “Qwen3.5-MoE Transformers reference implementation,” [source](../raw/Qwen3.8-2.4T-A95B/modeling_qwen3_5_moe.py), attention, Gated DeltaNet, MoE, decoder, and cache classes.
[^glm5-report]: GLM-5 Team, “GLM-5: from Vibe Coding to Agentic Engineering,” [source](../raw/arXiv-2602.15763v2/0_main.tex), pre-training and architecture appendix.
[^kimi-k3-report]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” [source](../raw/arXiv-2607.24653v1/main.tex), Sections 1–3.
