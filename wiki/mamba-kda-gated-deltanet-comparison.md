---
type: Synthesis
title: Mamba-2/3, KDA, Gated DeltaNet, and Gated DeltaNet-2 comparison
description: A mechanism and evidence comparison of four fixed-state sequence mixers, separating the SSM branch from the delta-rule branch and qualifying every ranking as configuration-bound.
tags: [mamba, deltanet, kda, linear-attention, comparison, fixed-state-memory]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T00:00:00Z }
sources:
  - id: mamba-2-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
  - id: mamba-3-2026
    resource: ../raw/2603.15569_Mamba-3/structure.tex
    title: "Mamba-3: Improved Sequence Modeling using State Space Principles"
  - id: gdn-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: kda-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: gdn2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
  - id: frontier-2026
    resource: ../raw/2607.07953_LinearAttentionArchitectures/template.tex
    title: "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing"
---

# Mamba-2/3, KDA, Gated DeltaNet, and Gated DeltaNet-2 comparison

Bốn cách xây dựng này đều là **sequence mixer fixed-state**: state có kích thước theo kiến trúc, không theo context, đổi lại loss-of-isolated-slots và interference. Chúng khác nhau chủ yếu ở **cách state được ghi đè** và **độ chi tiết của cơ chế quên**, và chia thành hai nhánh thiết kế: nhánh SSM (Mamba-2, Mamba-3) nhìn sequence qua discretization, nhánh associative-memory (Gated DeltaNet, KDA, Gated DeltaNet-2) qua delta rule cộng decay học được. Không nhánh nào thắng tuyệt đối ngoài recipe cụ thể của nó.[^mamba-2-2024][^mamba-3-2026][^gdn-2025][^kda-2025][^gdn2-2026][^frontier-2026]

## Trục cơ chế

| Trục | Mamba-2 | Mamba-3 | Gated DeltaNet | KDA | Gated DeltaNet-2 |
|---|---|---|---|---|---|
| Update | $h_t=\alpha_t h_{t-1}+B_tx_t$ (scalar transition) | 3-term exp-trapezoidal + rotary complex; optional rank-$R$ MIMO | $S_{t-1}(\alpha_t(I-\beta kk^\top))+\beta vk^\top$ | $(I-\beta kk^\top)\mathrm{Diag}(\alpha_t)S_{t-1}+\beta kv^\top$ | $(I-ke_t^\top)D_tS_{t-1}+kz_t^\top$; $e_t=b_t\odot k_t$, $z_t=w_t\odot v_t$ |
| Key-conditioned correction | Không | Không | Có (rank-one chọn key) | Có (rank-one chọn key) | Có (asymmetric rank-one, erase/write) |
| Decay | Scalar real, data-dependent | Scalar real + complex rotation | **Scalar** $\alpha_t$ | **Channel-wise** $\mathrm{Diag}(\alpha_t)$ | **Channel-wise** $D_t$ + hai gate độc lập |
| Nguồn gốc | SSM/SSD | SSM/discretization | Associative memory | Associative memory | Associative memory |
| Parallel training | SSD chunked; context-parallel | SSD chunked; MIMO giảm chunk | WY/UT, decay-aware | WY/UT | WY/UT với shared inverse |

Cơ chế phải đọc cùng nhau:

- **Delta correction** sửa đúng association mà key đang chọn thay vì cộng thêm vô hạn.[^kda-2025]
- **Scalar decay** xóa broad toàn state; **channel-wise decay** cho từng channel retention horizon khác nhau; **erase/write tách rời** chọn độc lập hướng đọc ở phía key và nội dung ghi ở phía value.[^gdn-2025][^kda-2025][^gdn2-2026]
- Mamba-2/3 không có rank-one correction: chúng cộng dồn input đã biến đổi qua decay, suy ra từ SSM chứ không phải từ objective associative-memory.[^mamba-2-2024][^mamba-3-2026]

## Lineage

DeltaNet (ungated) → Gated DeltaNet (scalar decay) → KDA (channel-wise decay) → Gated DeltaNet-2 (channel-wise decay + erase/write tách rời). Gated DeltaNet-2 **rút gọn chính xác về KDA** khi hai gate gắn cùng một scalar, và về Gated DeltaNet khi decay cũng scalar; đây là reduction đại số của recurrence, không phải claim tương đương empirical.[^gdn2-2026] Mamba đứng ở nhánh song song, dù Gated DeltaNet được mô tả là "improving Mamba2 with delta rule" và throughput của nó được so trực tiếp với Mamba-2.[^gdn-2025]

## So sánh bằng chứng (chỉ trong cùng study)

Các study đánh giá dùng **corpus, tokenizer, scale, và config khác nhau**: Mamba-2 trên Pile/GPT-NeoX 2.7B/300B; Gated DeltaNet 1.3B/100B FineWeb-Edu; Gated DeltaNet-2 1.3B/100B FineWeb-Edu; Mamba-3 1.5B/100B FineWeb-Edu (2K context, Llama-3.1 tokenizer). Do đó **số loss/token chéo giữa study là không so được**. Chỉ thứ hạng nội tại trong một bảng mới có nghĩa.[^mamba-2-2024][^gdn-2025][^gdn2-2026][^mamba-3-2026]

| Study | Thứ tự xu hướng trong bảng | Chú giải |
|---|---|---|
| Gated DeltaNet-2 (1.3B/100B) | Recurrent LAMBADA+commonsense 53.11 (cao nhất; KDA, Mamba-3 MIMO dưới); recall 29.88 (KDA 28.67; Mamba-3 MIMO 28.35); hybrid 42.28 (Mamba-3 SISO 41.01) | GDN-2 dẫn đầu nội tại bảng, nhưng throughput H100 training **KDA nhanh hơn** (39.81–38.50K vs 38.00–36.11K tok/s)[^gdn2-2026] |
| Mamba-3 (1.5B/100B) | SISO 10.35/56.4 > Gated DeltaNet 10.45/55.8 > Mamba-2 10.47/55.7 > Transformer 10.51/55.4; MIMO 10.24/57.6 | Mamba-3 vượt GDN & Mamba-2 trong recipe riêng, trái chiều thứ hạng study GDN-2[^mamba-3-2026] |
| Frontier 350M/15B | KDA/Muon/hybrid loss 2.273 (thấp nhất); GDN/AdamW/pure throughput 100% reference nhưng loss 2.433 | Muon luôn thấp loss hơn AdamW trong bảng[^frontier-2026] |

Không có ranking phổ quát: thứ tự phụ thuộc vào model scale, tokenizer, context length, kernel, hybrid stack, và optimizer trong từng bảng.[^frontier-2026]

## Đánh giá chung và giới hạn

- **Không có backbone thắng tuyệt đối.** Mỗi study chỉ chứng minh thứ tự nội tại trong recipe của nó, thường là point estimate, author-run, không variance.[^gdn2-2026][^mamba-3-2026]
- **Cơ chế quên chi tiết hơn** (scalar → channel-wise → tách erase/write) tương quan với recall/retrieval tốt hơn trong các study so-sánh, nhưng phải trả throughput (GDN-2 chậm hơn KDA) và thêm gate branches/parameters.[^gdn2-2026][^frontier-2026]
- **Mọi recurrent fixed-state vẫn mất token-addressable retrieval tuyệt đối.** Hybrid — SWA trong Gated DeltaNet/Gated DeltaNet-2/Mamba-3, MLA trong KDA/Kimi — khôi phục retrieval nhưng làm cache tăng lại theo token.[^gdn-2025][^mamba-3-2026][^kda-2025]
- **Vị trí/recency:** KDA trong Kimi designs giao positional behavior cho transition data-dependent và dùng NoPE ở các MLA layers; Mamba-3 dùng rotary complex (khác RoPE). Đây là interpretation, không phải chứng minh suy rộng.[^kda-2025][^mamba-3-2026]

## Relationships

- **Compares:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md), [Mamba-3 architecture and state-space methods](mamba-3-architecture-and-state-space-methods.md), [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md), and [Gated DeltaNet-2 decoupled delta rule and training](gated-deltanet-2-decoupled-delta-rule-and-training.md).
- **Builds on mechanism in:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), whose KDA recurrence and channel-wise decay this page synthesizes.
- **Used by the KDA designs:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Extends evaluation of:** [DeltaNet evaluation and hybrid-attention trade-offs](deltanet-evaluation-and-hybrid-attention-trade-offs.md), [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), [Gated DeltaNet-2 evaluation and hybrid trade-offs](gated-deltanet-2-evaluation-and-hybrid-trade-offs.md), [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md), and [Mamba-3 evaluation and inference trade-offs](mamba-3-evaluation-and-inference-trade-offs.md).
- **Supports workload-conditioned selection:** [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md), which recommends recurrent-plus-periodic-latent-attention MoE unless exact token-addressable retrieval dominates.

## Evidence limits

Tất cả số liệu là author-reported point estimates từ các paper/LaTeX nguồn; không có independent replication hay variance. Việc so sánh các nghiên cứu chéo về corpus, tokenizer, context length, state layout, kernel, precision và hardware — đặc biệt giữa Mamba-3 và Gated DeltaNet-2 — bị giới hạn bởi các bất đối xứng đó. Fixed-state guarantee chỉ có nghĩa bị chặn về kích thước state, không phải quality parity hay lossless retrieval.

[^mamba-2-2024]: Tri Dao and Albert Gu, "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality," [source](../raw/arXiv-2405.21060v1/structure.tex).
[^mamba-3-2026]: Aakash Lahoti et al., "Mamba-3: Improved Sequence Modeling using State Space Principles," [source](../raw/2603.15569_Mamba-3/structure.tex).
[^gdn-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, "Gated Delta Networks: Improving Mamba2 with Delta Rule," ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex).
[^kda-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," [source](../raw/arXiv-2510.26692v2/main.tex).
[^gdn2-2026]: Ali Hatamizadeh, Yejin Choi, and Jan Kautz, "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention," [source](../raw/2605.22791_GatedDeltaNet-2/main.tex).
[^frontier-2026]: Tommaso Cerruti, Tim Rieder, George Rowlands, Lingfeng Jin, and Imanol Schlag, "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing," [source](../raw/2607.07953_LinearAttentionArchitectures/template.tex).
