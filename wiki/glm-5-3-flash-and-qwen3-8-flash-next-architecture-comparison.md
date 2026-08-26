---
type: Synthesis
title: GLM-5.3-Flash and Qwen3.8-Flash-Next architecture comparison
description: GLM-5.3-Flash and Qwen3.8-Flash-Next converge on recurrent-majority hybrid MoE backbones with periodic pooled sparse attention and four residual streams, but differ in delta memory, attention core, residual constraints, conditional memory, scale, and context strategy.
tags: [comparison, glm-5-3-flash, qwen3-8-flash-next, hybrid-attention, sparse-attention, mixture-of-experts, long-context]
status: stable
created: 2026-08-26
generated: { by: llm-wiki-agent/1, at: 2026-08-26T15:34:23Z }
sources:
  - id: glm53-config
    resource: ../raw/GLM-5.3-Flash/config.json
    title: GLM-5.3-Flash checkpoint configuration
  - id: glm53-modeling
    resource: ../raw/GLM-5.3-Flash/modeling_glm5_next.py
    title: GLM-5.3-Flash Transformers modeling implementation
  - id: glm53-blog
    resource: ../raw/GLM-5.3-Flash/blog.md
    title: GLM-5.3-Flash release blog
  - id: qwen38-next-config
    resource: ../raw/Qwen3.8-Flash-Next/config.json
    title: Qwen3.8-Flash-Next checkpoint configuration
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: Qwen4-Exp Transformers modeling implementation
  - id: qwen38-next-blog
    resource: ../raw/Qwen3.8-Flash-Next/blog.md
    title: Qwen3.8-Flash-Next release blog
---

# GLM-5.3-Flash and Qwen3.8-Flash-Next architecture comparison

Hai model hội tụ trên cùng một công thức cấp cao: backbone đa phương thức MoE dùng ba lớp recurrent delta-memory cho mỗi lớp sparse token-addressable attention, kèm residual bốn luồng. Đây là đồng quy có điều kiện nhằm giảm compute và state dài-ngữ-cảnh mà vẫn giữ đường truy hồi token định kỳ; nó không có nghĩa hai cơ chế tương đương hoặc đã chứng minh một kiến trúc tối ưu phổ quát.[^glm53-config][^glm53-modeling][^qwen38-next-config][^qwen38-next-modeling]

## So sánh kiến trúc

| Chiều | GLM-5.3-Flash | Qwen3.8-Flash-Next |
|---|---|---|
| Quy mô công bố | 320B tổng / 18B active; 45 lớp; width 4,096 | 125B / 6B active cho backbone, ngoài ra công bố 51B N-gram và 4B MTP; 48 lớp; width 2,560 |
| Lịch token mixer | 34 KDA + 11 pooled DSA; xấp xỉ 3:1 | 36 Gated DeltaNet + 12 QSA; đúng 3:1 |
| Recurrent memory | KDA: delta correction với decay theo channel | Gated DeltaNet: delta correction với decay scalar |
| Sparse attention | Nhóm bốn token bằng learned weighted pooling; chọn tối đa 512 nhóm; core NoPE MLA/DSA | Lấy mean index-key cho block bốn token; chọn tối đa 512 block; core partial-RoPE GQA có output gate |
| Cache dài-ngữ-cảnh | KDA fixed-state; 11 lớp DSA vẫn giữ cache/index tăng theo token | Gated DeltaNet fixed-state; 12 lớp QSA vẫn giữ KV/index tăng theo token |
| Residual | mHC bốn luồng với ma trận trộn doubly stochastic xấp xỉ qua Sinkhorn | Gated Residual bốn luồng, feature-wise read gate và scalar write gate; không có ràng buộc Sinkhorn |
| MoE | 288 routed + một shared expert; top-8; ba FFN đầu dense | 512 routed + một gated shared expert ở mỗi lớp; top-10 |
| Conditional memory | Không có N-gram table trong bundle | PLE layer 2: hashed bigram/trigram memory khoảng 51.2B tham số |
| Context | Config khai báo 1,048,576 token | Native 262,144; một triệu qua static YaRN factor 4, có cảnh báo giảm chất lượng input ngắn |
| Multimodal | Vision encoder 24 block, width 1,024 | Vision encoder 27 block, width 1,152 |

## Điểm đột phá và tác động hiệu năng

1. **Hybrid không còn chỉ là linear + dense attention.** Cả hai đặt fixed-state delta memory ở 3/4 độ sâu, nhưng lớp truy hồi định kỳ cũng được sparse hóa theo micro-block. Main attention chỉ đọc tối đa khoảng 2,048 token đã chọn thay vì toàn prefix, trong khi recurrent layers không nối dài KV cache.[^glm53-modeling][^qwen38-next-modeling]
2. **Sparse selection chuyển từ token rời rạc sang block bốn token.** Cách này giảm số ứng viên index và cải thiện locality so với token-level DSA, đổi lại selection thô hơn và vẫn phải giữ state tăng theo context. GLM học phép pooling; Qwen dùng mean key đơn giản hơn.[^glm53-modeling][^qwen38-next-modeling]
3. **Residual path trở thành một trục kiến trúc.** GLM chọn mHC để ràng buộc linear carried path không giãn; Qwen chọn gate dữ liệu linh hoạt hơn nhưng không thừa hưởng bảo đảm phổ của mHC. Hiệu quả chất lượng và ổn định riêng của hai lựa chọn chưa có ablation đối đầu.[^glm53-modeling][^qwen38-next-modeling]
4. **Qwen thêm trục sparse capacity thứ ba.** Ngoài sparse compute của MoE và sparse reads của QSA, bảng N-gram cung cấp conditional lookup dung lượng lớn mà không kích hoạt toàn bộ tham số mỗi token; chi phí thật chuyển sang table memory, hash collision, bandwidth và prefetch.[^qwen38-next-config][^qwen38-next-modeling]
5. **Co-design mở rộng sang training và serving.** Qwen công bố lịch Muon/AdamW và kernel QSA; GLM công bố Encode–Prefill–Decode disaggregation, cache quantization và worker pools. Vì các bundle không cung cấp đầy đủ kernel, telemetry hay matched ablation, đây là bằng chứng hệ thống do vendor báo cáo chứ chưa phải hiệu quả có thể suy trực tiếp từ config.[^glm53-blog][^qwen38-next-blog]

## Bằng chứng hiệu năng và giới hạn so sánh

Qwen báo cáo kernel QSA nhanh hơn tối đa 7.6× ở prefill và 4.9× ở decode tại một triệu token; con số throughput 8.6× so với Qwen3.7-Plus dùng online serving với 90% prefix-cache hit. GLM báo cáo phép tính chuẩn hóa thấp hơn GLM-5.3 3.0× về attention compute và 4.4× về cache mỗi layer, cùng cải thiện serving end-to-end 3× so với baseline nội bộ. Các mẫu số, hardware, kernel, cache policy và workload khác nhau, nên không thể dùng các tỷ lệ này để tuyên bố model nào nhanh hơn.[^glm53-blog][^qwen38-next-blog]

Tương tự, hai release đều báo cáo điểm coding/agentic/multimodal mạnh nhưng dùng harness, judge, context budget và comparator khác nhau. Không có benchmark head-to-head được kiểm soát hay ablation tách riêng tác động của recurrent mixer, sparse attention, residual, MoE, N-gram memory và dữ liệu huấn luyện.

## Relationships

- **Synthesizes:** [GLM-5.3-Flash hybrid multimodal architecture](glm-5-3-flash-hybrid-multimodal-architecture.md) and [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md).
- **Qualified by:** [GLM-5.3-Flash evaluation, serving, and evidence limits](glm-5-3-flash-evaluation-serving-and-evidence-limits.md) and [Qwen3.8-Flash-Next evaluation and deployment limits](qwen3-8-flash-next-evaluation-and-deployment-limits.md).
- **Contrasts:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) with [Qwen Sparse Attention](qwen-sparse-attention.md), and [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) with [Qwen Gated Residual](qwen-gated-residual.md).
- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) as the common recurrent-memory foundation.

## Evidence limits

Đây là so sánh thiết kế, không phải xếp hạng hiệu năng. Cấu hình và reference code hỗ trợ các mô tả cơ chế; speedup, cost, quality và production claims đến từ blog của nhà cung cấp. Reference implementations không chứng minh hiệu năng của optimized kernels, và cả hai hệ vẫn có cache tăng theo context ở các lớp sparse attention.

[^glm53-config]: Z.ai, “GLM-5.3-Flash checkpoint configuration,” [source](../raw/GLM-5.3-Flash/config.json).
[^glm53-modeling]: Z.ai and Hugging Face, “GLM-5.3-Flash Transformers modeling implementation,” [source](../raw/GLM-5.3-Flash/modeling_glm5_next.py).
[^glm53-blog]: Z.ai, “GLM-5.3-Flash,” [release blog](../raw/GLM-5.3-Flash/blog.md), architecture and serving sections.
[^qwen38-next-config]: Qwen Team, “Qwen3.8-Flash-Next checkpoint configuration,” [source](../raw/Qwen3.8-Flash-Next/config.json).
[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py).
[^qwen38-next-blog]: Qwen Team, “Qwen3.8-Flash-Next,” [release blog](../raw/Qwen3.8-Flash-Next/blog.md), architecture, optimization, and performance sections.
