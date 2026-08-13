---
type: Synthesis
title: DFlash and DSpark comparison
description: DFlash is a disclosed target-conditioned block-diffusion drafting method, while DSpark is a target-specific parallel-draft family that may extend its backbone with checkpoint-dependent heads and configurations.
tags: [speculative-decoding, dflash, dspark, comparison, inference]
status: stable
created: 2026-08-13
generated: { by: llm-wiki-agent/1, at: 2026-08-13T10:01:57Z }
sources:
  - id: dflash-2026
    resource: ../raw/arXiv-2602.06036v2/main.tex
    title: "DFlash: Block Diffusion for Flash Speculative Decoding"
  - id: kimi-k3-dspark-card
    resource: ../raw/KimiK3DSparkspeculator.md
    title: "Kimi K3 DSpark speculator (Hugging Face model card)"
  - id: nemotron-dspark-card
    resource: ../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md
    title: NVIDIA Nemotron 3.5 Lightning DSpark model card
---

# DFlash and DSpark comparison

DFlash là phương pháp **block-diffusion draft** được công bố tương đối đầy đủ: một draft nhỏ sinh cả block token song song và được điều kiện hóa bằng hidden states của target. DSpark là **họ parallel-draft target-specific**: bản Kimi K3 nói rõ nó mở rộng backbone DFlash bằng Markov logit-bias và confidence heads, nhưng bản Nemotron không công bố các chi tiết đó. Vì vậy không nên hiểu DSpark là một kiến trúc cố định hoặc mặc định nhanh hơn DFlash.[^dflash-2026][^kimi-k3-dspark-card][^nemotron-dspark-card]

| Khía cạnh | DFlash | DSpark |
|---|---|---|
| Vai trò | Phương pháp draft block song song cho speculative decoding | Họ checkpoint/draft song song theo từng target |
| Sinh proposal | Block-diffusion: dự đoán các vị trí masked trong block trong một pass song song | Dùng backbone parallel-draft kiểu DFlash theo card Kimi; chi tiết không đồng nhất giữa các checkpoint |
| Điều kiện hóa target | Trộn hidden states từ nhiều layer target thành persistent KV ở mọi layer draft | Kimi đọc các layer target phụ trợ; không đủ bằng chứng để khẳng định giữ nguyên KV injection/masking/loss của DFlash |
| Mở rộng riêng | DFlash gốc | Kimi K3: Markov logit-bias + confidence head theo vị trí; Nemotron: các head này không được công bố |
| Ví dụ kích thước | Nemotron DFlash: 833M tham số | Kimi K3: 2.25B; Nemotron: 967M — không thể coi DSpark luôn nhỏ hoặc rẻ hơn |
| Bằng chứng hiệu năng | Có speedup end-to-end: tối đa 6.09× trong đánh giá tác giả; giảm khi concurrency tăng | Chủ yếu báo cáo `acc_len`/acceptance; Kimi khoảng 4.26 ở RULER 1M; không có latency/speedup end-to-end |

## Ý nghĩa khi chọn

- Chọn **DFlash** khi cần một thiết kế đã mô tả rõ cơ chế và có số đo speedup end-to-end; vẫn cần huấn luyện draft riêng cho target và benchmark đúng workload/concurrency.
- Chọn **DSpark** khi target và runtime có checkpoint DSpark được hỗ trợ, đặc biệt Kimi K3/SGLang. Hãy đo latency thực tế: acceptance cao không tự suy ra nhanh hơn, vì draft có thể lớn và tốn hơn.
- Với Nemotron cùng draft length 7, DSpark có accepted length trung bình 3.75 so với DFlash 3.16, nhưng DSpark cũng lớn hơn (967M so với 833M). Thiếu số liệu latency, throughput, memory và concurrency nên chưa thể kết luận DSpark thắng về tốc độ.[^nemotron-dspark-card]

## Relationships

- **Compares:** [DFlash block-diffusion speculative decoding](dflash-block-diffusion-speculative-decoding.md) and [DSpark parallel-draft speculative decoding](dspark-parallel-draft-speculative-decoding.md).
- **Qualified by:** [DFlash evaluation and serving trade-offs](dflash-evaluation-and-serving-trade-offs.md), [DSpark speculator evaluation and deployment](dspark-speculator-evaluation-and-deployment.md), and [Speculative decoding performance trade-offs](speculative-decoding-performance-trade-offs.md).

## Evidence limits

DFlash speedups are author-run and workload-dependent. DSpark evidence comes from model cards and differs by target; the Kimi-specific Markov/confidence details cannot be generalized to the Nemotron release or future DSpark checkpoints. Both methods still rely on target verification for speculative decoding behavior.[^dflash-2026][^kimi-k3-dspark-card][^nemotron-dspark-card]

[^dflash-2026]: Chen, Liang, and Liu, “DFlash: Block Diffusion for Flash Speculative Decoding,” arXiv:2602.06036v2, [source](../raw/arXiv-2602.06036v2/main.tex), Sections 3–5 and Appendix C.

[^kimi-k3-dspark-card]: RadixArk, “Kimi K3 DSpark speculator,” Hugging Face model card, [source](../raw/KimiK3DSparkspeculator.md), Overview, Model Specifications, Evaluation Results, and Serving with SGLang.

[^nemotron-dspark-card]: NVIDIA, “NVIDIA Nemotron 3.5 Lightning DSpark,” [model card](../raw/NVIDIA-Nemotron-3.5-Lightning-30B-A3B/DSpark.md), Model Architecture and Evaluation.
