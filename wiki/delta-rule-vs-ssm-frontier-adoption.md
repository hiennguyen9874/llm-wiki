---
type: Synthesis
title: Delta-rule (KDA / Gated DeltaNet) vs SSM (Mamba / SSD) trong frontier adoption
description: Các frontier model general-purpose (Kimi K3, Qwen chọn nhánh delta-rule/linear attention, GLM-5 chọn sparse attention) không chọn Mamba/SSM vì nhánh delta-rule cho phép ghi đè theo key và cơ chế quên chi tiết hơn, phù hợp hơn với recipe "bounded-state + periodic exact retrieval" — nhưng đây là convergence có điều kiện, không phải quy luật tuyệt đối.
tags: [delta-rule, mamba, ssm, kda, gated-deltanet, linear-attention, hybrid-attention, architecture-selection]
status: stable
created: 2026-08-24
generated: { by: llm-wiki-agent/1, at: 2026-08-24T16:20:51Z }
sources:
  - id: kda-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: gdn-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: gdn2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
  - id: mamba-2-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
  - id: mamba-3-2026
    resource: ../raw/2603.15569_Mamba-3/structure.tex
    title: "Mamba-3: Improved Sequence Modeling using State Space Principles"
  - id: frontier-2026
    resource: ../raw/2607.07953_LinearAttentionArchitectures/template.tex
    title: "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: glm5-report-2026
    resource: ../raw/arXiv-2602.15763v2/0_main.tex
    title: "GLM-5: from Vibe Coding to Agentic Engineering"
  - id: qwen35-config
    resource: ../raw/Qwen3.5-27B/config.json
    title: "Qwen3.5-27B checkpoint configuration"
  - id: qwen38-config
    resource: ../raw/Qwen3.8-2.4T-A95B/config.json
    title: "Qwen3.8-2.4T-A95B checkpoint configuration"
---

# Delta-rule (KDA / Gated DeltaNet) vs SSM (Mamba / SSD) trong frontier adoption

Câu hỏi "vì sao các mô hình gần đây dùng KDA / biến thể linear attention mà không dùng SSM hoặc Mamba" cần được đọc đúng ngay từ đầu: **phần lớn mô hình frontier gần đây đã chọn nhánh delta-rule/associative-memory, không phải nhánh SSM, khi xây dựng sequence mixer fixed-state** — và GLM-5 thực ra không nằm trong nhánh linear attention nào.[^kda-2025][^gdn-2025][^gdn2-2026][^mamba-2-2024][^mamba-3-2026][^frontier-2026][^kimi-k3-2026][^glm5-report-2026][^qwen35-config][^qwen38-config]

Tóm tắt một câu: nhánh delta-rule **ghi đè đúng association mà key đang chọn** và có **cơ chế quên chi tiết hơn** (scalar → channel-wise → tách erase/write), nên trong các so sánh matched nó thể hiện recall/retrieval dài ngữ cảnh mạnh hơn nhánh SSM — điều này khiến nó trở thành thành phần fixed-state phù hợp hơn để ghép với recurrent memory bounded và attention toàn cục định kỳ (periodic global retrieval), là recipe mà Kimi K3 và Qwen cùng hội tụ. Đây là **convergence có điều kiện và theo bằng chứng nội tại từng study**, không phải quy luật thắng tuyệt đối.

## Làm rõ tiền đề

- **Kimi K3** dùng **KDA** (delta-rule), trong một backbone 2.78T với 69 KDA + 24 NoPE Gated MLA + Block AttnRes + Stable LatentMoE. Thuộc nhánh delta-rule.[^kimi-k3-2026]
- **Qwen** (Qwen3.5-27B và Qwen3.8-2.4T-A95B) dùng **Gated DeltaNet** (delta-rule, scalar decay) xen kẽ global GQA theo tỷ lệ ba-một. Thuộc nhánh delta-rule, **không phải SSM**.[^qwen35-config][^qwen38-config]
- **GLM-5** dùng **MLA + DSA** — token-addressable **sparse attention**, không phải linear attention và không phải fixed-state recurrent. Vì vậy GLM-5 không "chọn KDA thay vì Mamba"; nó chọn một hướng thứ ba (giữ truy cập token nhưng giảm số token được đọc bằng indexer).[^glm5-report-2026]

## Hai nhánh sequence mixer fixed-state

| Nhánh | Cập nhật state | Ghi đè theo key | Nguồn gốc |
|---|---|---|---|
| **SSM** (Mamba-2, Mamba-3) | $h_t=\alpha_t h_{t-1}+B_tx_t$; Mamba-3 thêm exp-trapezoidal + rotary complex, MIMO | **Không** — cộng dồn input đã biến đổi qua decay | Discretization / SSD |
| **Delta-rule** (DeltaNet → Gated DeltaNet → KDA → Gated DeltaNet-2) | $S_t=(I-\beta kk^\top)\mathrm{Diag}(\alpha_t)S_{t-1}+\beta kv^\top$ | **Có** — rank-one sửa đúng association được chọn | Associative memory / fast-weight programmer |

Xem chi tiết cơ chế và bằng chứng tại [Mamba-2/3, KDA, Gated DeltaNet, và Gated DeltaNet-2 comparison](mamba-kda-gated-deltanet-comparison.md) và [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md).

## Vì sao nhánh delta-rule được frontier ưu ái hơn nhánh SSM

1. **Ghi đè có chủ đích, không chỉ cộng dồn.** Delta correction đọc association mà $k_t$ đang chọn rồi ghi phần sai số về $v_t$, khớp với ngữ nghĩa truy xuất theo nội dung (content-based) của attention. Mamba cộng $B_tx_t$ qua decay mà không xoá/ghi đè có chọn lọc, nên ít "địa chỉ hoá" hơn và dễ mất/chồng lấn thông tin hơn trong state fixed-size.[^kda-2025][^gdn-2025][^gdn2-2026][^mamba-2-2024]
2. **Cơ chế quên chi tiết hơn.** Scalar decay (Gated DeltaNet) → **channel-wise** $\mathrm{Diag}(\alpha_t)$ (KDA) → **tách erase/write** (Gated DeltaNet-2) cho từng kênh retention horizon khác nhau và kiểm soát phía key (đọc) tách khỏi phía value (ghi). Mamba-2/3 giữ transition scalar (hoặc complex rotary), thô hơn.[^gdn-2025][^kda-2025][^gdn2-2026][^mamba-3-2026]
3. **Bằng chứng matched nghiêng về delta-rule cho recall/retrieval dài ngữ cảnh.** Gated DeltaNet (1.3B/100B) báo recall ~30.6 so với Mamba2 29.8 và DeltaNet 26.2; KDA/Muon/hybrid có loss thấp nhất (2.273) trong sweep 350M/15B; Gated DeltaNet-2 dẫn đầu bảng của nó ở LAMBADA và recall, đồng thời tên gọi của paper Gated DeltaNet đã nói rõ "Improving Mamba2 with Delta Rule".[^gdn-2025][^gdn2-2026][^frontier-2026][^mamba-2-2024]
4. **Đường huấn luyện chunkwise hiệu quả.** Cả hai nhánh đều fixed-state, nhưng delta-rule có biểu diễn WY/UT cho phép biến hầu hết thành ma trận; KDA dưới dạng DPLR ràng buộc loại bỏ chunking/matmul phụ. Trong timing study, hybrid Gated DeltaNet tăng ~1.7× từ 4K→32K so với softmax ~2.9×, pure ~1.1× — cùng hướng lợi thế tỉ lệ theo độ dài như nhánh SSM.[^frontier-2026][^kda-2025]

## Điểm mấu chốt: không model nào dùng fixed-state thuần

Cả Mamba lẫn KDA đều **mất truy xuất token-addressable tuyệt đối** vì state bị chồng lấn (superposition) và can thiệp (interference). Vì vậy mọi model frontier đều **hybrid hoá** — chạy sequence mixer fixed-state ở phần lớn layer rồi chèn attention toàn cục (MLA/GQA) định kỳ để khôi phục truy cập token.[^mamba-3-2026][^kda-2025][^gdn-2025][^qwen38-config][^kimi-k3-2026]

- Kimi K3: 69 KDA + 24 Gated MLA (tỷ lệ 3:1).
- Qwen3.8: 69 Gated DeltaNet + 23 GQA (tỷ lệ 3:1).
- Mamba-3 cũng phải thêm 5:1 hybrid với NoPE-attention khi cần truy cập token.

Vì vậy câu trả lời thực chất là: **không phải "Mamba kém KDA nói chung", mà là trong recipe "bounded-state trên hầu hết layer + periodic global retrieval", nhánh delta-rule là thành phần fixed-state vừa vặn hơn và được bằng chứng nội tại của các recipe đó ủng hộ mạnh hơn.** Kimi và Qwen hội tụ ở cùng tỷ lệ ba-một (3:1 cho perplexity thấp nhất trong ablation KDA:MLA của Kimi Linear) và cùng nhánh delta-rule.[^kda-2025][^qwen38-config]

## GLM-5 và sự lựa chọn khác

GLM-5 xử lý context dài bằng **sparse token-addressable attention**: giữ MLA state (linear theo token) xuyên backbone và dùng DSA indexer chọn ≤2,048 token quá khứ trước khi attention. Đây là phương án "giữ truy cập token nhưng giảm số token được đọc", **không** chuyển sang fixed-state. Trong [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md), hướng này được khuyên dùng khi truy xuất chính xác token cụ thể chiếm ưu thế; còn hướng recurrent + periodic latent attention (Kimi/Qwen) được khuyên cho general-purpose dài ngữ cảnh chưa rõ workload.[^glm5-report-2026][^kimi-k3-2026]

## Điều kiện và giới hạn

- **Không có ranking phổ quát.** Mỗi study dùng corpus (Pile / FineWeb-Edu), tokenizer (GPT-NeoX / Llama-family), scale (1.3B/1.5B/350M/15B), context length, kernel, optimizer và hybrid stack khác nhau; số loss/token chéo giữa study là **không so được**. Trong recipe riêng của Mamba-3, Mamba-3 SISO (10.35/56.4) vượt Gated DeltaNet (10.45/55.8) — trái chiều thứ hạng study Gated DeltaNet-2.[^mamba-3-2026][^gdn2-2026][^frontier-2026]
- **Bằng chứng là author-run, point estimate, không lặp độc lập, không variance.** Các con số trên là kết quả do tác giả báo cáo trong recipe của họ, không phải khẳng định về ưu thế suy rộng.[^gdn2-2026][^mamba-3-2026][^frontier-2026]
- **Kết luận adoption là do hội tụ + hiệu quả + hệ sinh thái + bằng chứng trong từng recipe, không phải định luật.** Nếu ngữ cảnh thật sự cần truy xuất token chính xác ở hầu hết layer, hướng DSA/MLA kiểu GLM-5 vẫn là lựa chọn hợp lý; nếu ràng buộc memory per-request khi decode rất dài, tăng tỉ trọng recurrent delta-memory.[^glm5-report-2026][^qwen38-config][^kimi-k3-2026]

## Relationships

- **Compares:** [Mamba-2/3, KDA, Gated DeltaNet, và Gated DeltaNet-2 comparison](mamba-kda-gated-deltanet-comparison.md), the mechanism-and-evidence baseline for the branch split.
- **Synthesizes adoption evidence from:** [Linear-attention architecture frontier and optimizer sensitivity](linear-attention-architecture-frontier-and-optimizer-sensitivity.md), [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), and [Mamba-3 evaluation and inference trade-offs](mamba-3-evaluation-and-inference-trade-offs.md).
- **Used by the hybrid designs:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), [Qwen3.5-27B checkpoint architecture and implementation](qwen3-5-27b-checkpoint-architecture.md), and [Qwen3.8-2.4T-A95B checkpoint architecture](qwen3-8-2-4t-a95b-checkpoint-architecture.md).
- **Contrasts with:** [GLM-5 architecture, pre-training, and systems](glm-5-architecture-pretraining-and-systems.md), which keeps sparse token-addressable attention instead of fixed-state recurrence.
- **Feeds into:** [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md), for the "when to pick which branch" recommendation.

## Evidence limits

Nội dung trên là tổng hợp từ các synthesis/concept đã có trong wiki, vốn dựa trên báo cáo tác giả và implementation tham chiếu; các con số là author-reported point estimate trong recipe riêng, không được lặp độc lập và không có uncertainty. Việc so sánh chéo giữa Mamba-3 và Gated DeltaNet-2 bị giới hạn bởi corpus, tokenizer, scale, context length, kernel, precision và hardware khác nhau. Fixed-state guarantee chỉ có nghĩa về kích thước state bị chặn, không phải về chất lượng parity hay truy xuất lossless.

[^kda-2025]: Kimi Team, "Kimi Linear: An Expressive, Efficient Attention Architecture," [source](../raw/arXiv-2510.26692v2/main.tex), Sections 2–3, 6.

[^gdn-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, "Gated Delta Networks: Improving Mamba2 with Delta Rule," ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5.

[^gdn2-2026]: Ali Hatamizadeh, Yejin Choi, and Jan Kautz, "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention," [source](../raw/2605.22791_GatedDeltaNet-2/main.tex), Sections 2–3.

[^mamba-2-2024]: Tri Dao and Albert Gu, "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality," [source](../raw/arXiv-2405.21060v1/structure.tex).

[^mamba-3-2026]: Aakash Lahoti et al., "Mamba-3: Improved Sequence Modeling using State Space Principles," [source](../raw/2603.15569_Mamba-3/structure.tex), Sections 4–5.

[^frontier-2026]: Tommaso Cerruti, Tim Rieder, George Rowlands, Lingfeng Jin, and Imanol Schlag, "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing," [source](../raw/2607.07953_LinearAttentionArchitectures/template.tex), Sections 4–7.

[^kimi-k3-2026]: Kimi Team, "Kimi K3: Open Frontier Intelligence," [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2–3.

[^glm5-report-2026]: GLM-5 Team, "GLM-5: from Vibe Coding to Agentic Engineering," [source](../raw/arXiv-2602.15763v2/0_main.tex), pre-training and architecture appendix.

[^qwen35-config]: Qwen Team, "Qwen3.5-27B checkpoint configuration," [source](../raw/Qwen3.5-27B/config.json).

[^qwen38-config]: Qwen Team, "Qwen3.8-2.4T-A95B checkpoint configuration," [source](../raw/Qwen3.8-2.4T-A95B/config.json).
