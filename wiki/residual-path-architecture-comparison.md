---
type: Synthesis
title: So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path
description: So sánh các hướng mở rộng đường residual từ gating và multi-stream đến constrained mixing, depth retrieval, và cross-layer routing, với trọng tâm là information flow, ổn định và chi phí hệ thống.
tags: [comparison, residual-connections, hyper-connections, gated-residual, attention-residuals, training-stability, macro-architecture]
status: stable
created: 2026-08-27
generated: { by: llm-wiki-agent/1, at: 2026-08-27T00:00:00Z }
sources:
  - id: transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: "Attention Is All You Need"
  - id: qwen38-next-report
    resource: ../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md
    title: "On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability"
  - id: qwen38-next-modeling
    resource: ../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py
    title: "Qwen4-Exp Transformers modeling implementation"
  - id: mhc-2025
    resource: ../raw/2512.24880_mHC/main.tex
    title: "mHC: Manifold-Constrained Hyper-Connections"
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: "Attention Residuals"
  - id: linear-attention-architectures-2026
    resource: ../raw/2607.07953_LinearAttentionArchitectures/template.tex
    title: "Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing"
---

# So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path

**Gated Residual (GR), mHC và Attention Residuals (AttnRes) không phải ba biến thể trên cùng một trục.** mHC và GR mở rộng residual stream thành nhiều nhánh; AttnRes giữ các representation theo **độ sâu** làm các nguồn có thể truy hồi. Vì vậy, câu hỏi đúng không phải “cái nào thay thế cái nào”, mà là model đang thiếu **dung lượng residual**, **khả năng chọn đường truyền**, **truy hồi representation cũ theo depth**, hay **ổn định/hiệu quả I/O**. Đây là synthesis về hướng phát triển residual-path; các con số chất lượng bên dưới là các thí nghiệm author-run, khác setup và không tạo thành leaderboard.[^qwen38-next-report][^mhc-2025][^attnres-2026]

## 1. Hướng phát triển chung

Residual chuẩn của Transformer là một identity highway đơn giản:

$$
h_{l+1}=h_l+F_l(\operatorname{Norm}(h_l)).
$$

Nó có gradient path trực tiếp và ít state, nhưng mọi update trước đó bị gộp vào một running sum.[^transformer-2017] Các nghiên cứu gần đây làm residual trở nên “có topology” hơn theo bốn nhánh. Sơ đồ dưới đây là **bản đồ khái niệm**, không phải genealogy lịch sử đầy đủ:

```text
standard residual: một stream + cộng đều
        │
        ├── gate đọc/ghi trên stream hiện có
        │     └── Highway-style gate / GatedNorm
        │
        ├── mở rộng residual stream thành nhiều nhánh
        │     ├── AltUp-style static widening
        │     ├── HC: read + write + branch mixing động
        │     ├── mHC: HC với branch mixing doubly stochastic
        │     └── GR: read gate theo feature + write gate theo nhánh,
        │              bỏ branch-mixing matrix
        │
        ├── lưu nguồn theo depth rồi truy hồi có chọn lọc
        │     └── Full/Block Attention Residuals
        │
        └── route một tín hiệu nội bộ sang residual chung
              └── CLVR cho write value của delta memory
```

Qwen mô tả trực tiếp hai họ chính: làm read/write giàu hơn, hoặc mở rộng stream thành nhiều nhánh; hai hướng này có thể kết hợp. mHC và GR là các nhánh khác nhau trong họ HC, còn AttnRes là một nhánh depth-retrieval khác.[^qwen38-next-report]

### Hai trục cần tách riêng

- **Sequence/token axis:** attention thông thường chọn thông tin giữa các vị trí token và quyết định token nào còn addressable trong KV state.
- **Depth/residual axis:** residual design quyết định representation nào của **cùng token** được giữ, trộn, chọn hoặc đưa tới layer sau.

Do đó, đổi GR, mHC hay AttnRes **không tự động** làm KV cache theo context thành fixed-size, không đổi causal mask và không làm mất autoregressive decode. Qwen/GLM/Kimi đều ghép residual design với recurrent memory, sparse attention hoặc MLA vì các component giải quyết các bottleneck khác nhau.[^qwen38-next-modeling][^attnres-2026]

## 2. Bảng so sánh cốt lõi

| Cơ chế | Đơn vị được mở rộng/chọn | Công thức ý tưởng | State residual | Điểm mạnh chính | Chi phí/rủi ro chính |
|---|---|---|---|---|---|
| **Standard residual** | Một stream, mọi update cộng đều | $h\leftarrow h+y$ | $O(d)$ | identity path đơn giản, dễ debug | không chọn riêng update cũ; contribution dễ bị dilution |
| **Highway / GatedNorm** | Feature hoặc branch trên stream hiện có | $h\leftarrow g(h)\odot\operatorname{Norm}(h)$ hoặc gate update | $O(d)$ | kiểm soát amplitude/outlier với ít topology mới | không tạo thêm nguồn depth; gate có thể thêm kernel/độ nhạy |
| **AltUp-style static widening** | Nhiều branch; read scalar tĩnh, write round-robin | $x=\sum_i h_iR_i$; ghi $y$ vào một branch | $O(n d)$ | test rẻ cho giả thuyết “width residual tự nó có ích” | memory traffic tăng theo $n$, read/write kém linh hoạt |
| **HC** | Nhiều branch + read/write + branch mixing | $X' = H_{res}X + H_{post}^{\top}F(H_{pre}X)$ | $O(nd)$ | topology và trao đổi giữa branch giàu | $H_{res}$ không bị ràng buộc; tích qua depth có thể khuếch đại/triệt tiêu signal; I/O lớn |
| **mHC** | Nhiều branch + constrained branch mixing | như HC, nhưng $H_{res}$ thuộc Birkhoff polytope | $O(nd)$ | giữ tương tác branch nhưng có bound cho linear carried path | Sinkhorn và activation/communication overhead; bound không áp dụng tự động cho toàn network |
| **Gated Residual (GR)** | Nhiều branch; read theo từng feature, write theo scalar branch | $x=\frac1n\sum_iG_i\odot\hat R_i$; $R_i'=R_i+s_i y$ | $O(nd)$ | expressive read, direct carried branches, bỏ một lần đọc/ mixing $H_{res}$ | không có spectral guarantee của mHC; vẫn phải mang nhiều branch |
| **Full AttnRes** | Mọi output trước đó theo depth | $h_l=\sum_{i<l}\operatorname{softmax}(w_l^\top\operatorname{RMSNorm}(v_i))_i v_i$ | giữ $O(Ld)$ nguồn/layer | layer mới truy hồi representation cũ có chọn lọc | depth state và scoring tăng; Full có $O(L^2d)$ depth arithmetic |
| **Block AttnRes** | Summary của $N$ block thay vì mọi layer | depth softmax trên embedding + block summaries + partial block | $O(Nd)$ theo số block | gần quality của Full hơn với state/communication bounded | mất resolution trong block; vẫn cần state theo token khi prefill |
| **CLVR** | Tín hiệu nội bộ của recurrent layer | $h\leftarrow h+P_l s_l$, thường $s_l=v_l$ | thêm side route, không lưu toàn bộ depth history | đưa write value hữu ích vào shared stream | không phải multi-stream/depth retrieval; lợi ích còn nhỏ và single-run |

`n` là số residual branches, `d` là hidden width, `L` là số sublayer và `N` là số block. Các bậc tăng trưởng là accounting cấu trúc, không phải cam kết latency end-to-end; memory layout, fusion và hardware có thể đảo thứ tự thực tế.[^qwen38-next-report][^mhc-2025][^attnres-2026][^linear-attention-architectures-2026]

## 3. GR, mHC và AttnRes khác nhau ở đâu?

### 3.1 mHC: mở rộng capacity rồi ràng buộc topology

Với state $X_l\in\mathbb{R}^{n\times d}$, mHC dùng ba map:

$$
X_{l+1}=H_l^{res}X_l+(H_l^{post})^\top F(H_l^{pre}X_l).
$$

- $H^{pre}$ đọc nhiều stream vào interface width-$d$ của layer.
- $H^{post}$ phân phối output của layer trở lại các stream.
- $H^{res}$ trộn carried state giữa các stream.

Điểm đặc biệt là $H^{res}$ được chiếu vào ma trận **doubly stochastic**: không âm, tổng mỗi hàng và cột bằng một. Với ma trận exact, $\lVert H^{res}\rVert_2\le1$ và tích của các ma trận như vậy vẫn doubly stochastic. Đây là lý do mHC có lập luận ổn định cho **linear residual mixing map**. Implementation dùng số hữu hạn Sinkhorn iterations, nên map runtime chỉ xấp xỉ constraint; điều này không chứng minh toàn bộ mạng nonlinear ổn định.[^mhc-2025]

Nói ngắn gọn, mHC đặt expressive capacity vào **branch-to-branch topology**, rồi dùng constraint để giữ identity-like signal propagation. DeepSeek-V4 dùng mHC cùng compressed attention, MoE và Muon; GLM-5.3-Flash cũng công bố bốn stream mHC trong backbone. Headline của hai model không thể gán riêng cho mHC.[^mhc-2025][^qwen38-next-modeling]

### 3.2 GR: bỏ phần topology đắt, đầu tư vào read gate

GR cũng dùng bốn stream trong Qwen3.8-Flash-Next, nhưng không phải mHC “đổi tên”. Qwen code thực hiện:

1. RMSNorm từng branch $R_i$;
2. dự đoán gate $G_i\in\mathbb{R}^d$ theo từng feature qua bottleneck rank 320 trong cấu hình width 2,560;
3. lấy trung bình các $G_i\odot\hat R_i$ để tạo input width-$d$;
4. ghi output bằng một scalar $s_i$ cho mỗi branch;
5. giữ carried state cũ, không có ma trận branch-mixing $H^{res}$ và không có Sinkhorn.[^qwen38-next-modeling]

Vì vậy:

- **mHC:** read/write tương đối coarse theo branch, nhưng có $H^{res}$ để trao đổi branch và có constraint phổ.
- **GR:** read fine-grained theo feature, write coarse theo branch, branch không trộn trực tiếp; expressive power nằm ở chỗ layer **đọc** residual thế nào.

GR là một nhánh tối giản hóa có chủ ý: bỏ một full read của residual state và nguồn bất ổn riêng của $H^{res}$, nhưng đổi lại mHC’s spectral argument không được kế thừa. Sigmoid gate và direct carry có thể giúp ổn định thực nghiệm, song đó là evidence thực nghiệm chứ không phải bound toán học cho toàn mạng.[^qwen38-next-report][^qwen38-next-modeling]

### 3.3 AttnRes: không mở rộng lane, mở rộng danh sách nguồn theo depth

AttnRes không duy trì bốn channel song song để layer trộn; nó giữ embedding và các output trước đó như các **depth sources**. Pseudo-query học theo layer chấm điểm các source sau RMSNorm rồi softmax:

$$
h_l=\sum_{i<l}\alpha_{i\to l}v_i.
$$

- **Full AttnRes:** mỗi sublayer thấy mọi source trước đó; resolution cao nhất nhưng giữ $O(Ld)$ source và có depth-attention arithmetic lớn.
- **Block AttnRes:** tổng hợp các sublayer thành block summaries; chỉ truy hồi giữa các block và partial current block. $N=L$ gần Full, còn $N=1$ gần standard accumulation với embedding source riêng.[^attnres-2026]

AttnRes giải quyết **residual dilution / thiếu addressability theo depth**, còn mHC/GR giải quyết **capacity và đường truyền trong residual stream tại một depth**. Hai ý tưởng có thể kết hợp về mặt khái niệm, nhưng các nguồn hiện có không cung cấp thí nghiệm controlled chứng minh tổ hợp GR+mHC+AttnRes là tốt hơn.

## 4. Các kiến trúc tương tự và vị trí của chúng

### 4.1 GatedNorm / Highway-style gate

GatedNorm áp dụng một self-gate sau RMSNorm:

$$
\operatorname{GatedNorm}(u)=\operatorname{RMSNorm}(u)\odot\sigma\!\left(W_2\operatorname{SiLU}(W_1\operatorname{RMSNorm}(u))\right).
$$

Đây là **gate của representation**, không phải một topology multi-stream hoàn chỉnh. Trong Qwen report, GatedNorm được dùng như nguyên liệu để đi tới GR; một test AdamW ở 3× learning rate tối ưu báo cáo giảm loss-spike rate từ 32.0 xuống 3.2 trên mỗi 10K step và giảm threshold crossings từ 256 xuống 20. Đây là kết quả của setup cụ thể, không phải guarantee rằng mọi residual gate đều ổn định.[^qwen38-next-report]

### 4.2 AltUp-style widening

AltUp-style simplified variant là control quan trọng: có $n$ branch, read bằng $n$ scalar tĩnh và mỗi block ghi output vào branch round-robin. Nó gần như không thêm matrix compute nhưng vẫn tốn memory traffic để mang $n$ branch. Qwen report cho biết width-only variant giảm loss khoảng 0.01 trong một 25B-A3B/400B-token comparison. Điều này tách được một insight: **mở rộng state tự nó đã có thể có giá trị**, trước khi thêm dynamic gates hay branch mixing.[^qwen38-next-report]

### 4.3 HC: tiền thân trực tiếp của mHC và họ hàng của GR

HC dùng dynamic $H_{pre}$, $H_{post}$ và $H_{res}$; các map được dự đoán từ residual state, ban đầu có static terms và scale nhỏ. Điểm mà mHC nhắm tới là tích của các $H_{res}$ unconstrained qua nhiều layer: mHC report quan sát Amax gain gần 3,000 ở HC trong 27B run, so với khoảng 1.6 ở mHC approximate. Đây là evidence author-run của propagation map, không phải một định lý rằng mọi HC đều nổ.[^mhc-2025]

### 4.4 VWN và các macro-design lân cận

Qwen report đặt GR cùng họ với **VWN**: VWN giữ read/write scalar nhưng mở rộng token embedding thành nhiều segment hẹp, cũng nhằm tạo read/write granularity tốt hơn. mHC report còn liệt kê **Residual Matrix Transformer (RMT)** và **MUDDFormer** trong nhóm macro-design mở rộng residual topology. Trong bundle hiện tại, các phương pháp này chỉ có mô tả citation-level, chưa có concept page và matched evidence đủ để đưa vào bảng xếp hạng. Vì vậy chúng được giữ như retrieval leads, không bị đánh đồng với GR, mHC hay AttnRes.[^qwen38-next-report][^mhc-2025]

### 4.5 CLVR: route tín hiệu của sequence mixer vào stream chung

CLVR không mở rộng residual stream thành nhiều branch và cũng không truy hồi toàn bộ layer history. Nó chiếu internal write value của DeltaNet-style layer qua projection zero-initialized rồi cộng vào shared residual stream:

$$
\varepsilon_{l,t}=P_ls_{l,t},\qquad h_{l,t}\leftarrow h_{l,t}+\varepsilon_{l,t}.
$$

Trong các single-run matched comparisons được lưu, CLVR có loss thấp hơn host DeltaNet/Gated DeltaNet một lượng nhỏ, nhưng effect giảm ở training dài hơn và chưa có inference-speed benchmark. Nó là ví dụ của hướng **cross-layer signal routing**, không phải một đối thủ trực tiếp của mHC/GR về residual topology.[^linear-attention-architectures-2026]

## 5. Stability, quality và hệ thống: nên đọc evidence thế nào?

### 5.1 Stability claim mạnh nhất thuộc về phần nào?

| Cơ chế | Điều có thể nói | Điều không thể suy ra |
|---|---|---|
| HC | dynamic residual topology giàu hơn; unconstrained product có thể khuếch đại signal | không phải mọi HC run đều bất ổn với cùng mức độ |
| mHC | exact doubly stochastic $H^{res}$ là non-expansive và đóng qua phép nhân; report đo composite gain bounded hơn HC | không chứng minh nonlinear branch, optimizer và toàn model đều stable |
| GR | sigmoid read gate/direct carry liên quan tới giảm outlier trong Qwen tests; không có $H^{res}$ nên ít một nguồn instability hơn | không có spectral bound của mHC; gate không bảo đảm stability ở scale khác |
| AttnRes | zero-init pseudo-query làm initial depth weights uniform; softmax tạo cạnh tranh dương giữa depth sources | không biến depth state thành free memory, không đảm bảo benchmark gain phổ quát |

### 5.2 Kết quả trong các setup khác nhau

Các điểm sau hữu ích để hiểu trade-off, **không được dùng để xếp hạng cross-paper**:

- **mHC report:** ở comparison 27B, mHC có final-loss gap $-0.021$ so với baseline và vượt baseline trên tám task được liệt kê; mHC với $n=4$ báo cáo thêm 6.7% training time. Đây là author-run và gồm nhiều chi tiết hệ thống của recipe.[^mhc-2025]
- **Qwen residual ablation:** trong 25B-A3B, table residual report ghi `Pre-norm` loss 1.617 / average 50.91, `mHC static` 1.596 / 52.49, `mHC dynamic` 1.594 / 54.47 và `GR` 1.590 / 54.66. Nhưng trong một loss comparison khác, `Full AttnRes + GatedNorm` đạt 1.758 so với GR 1.762; GR vì vậy không uniformly superior.[^qwen38-next-report]
- **AttnRes report:** ở một 436M MoE ablation, baseline 1.766, Full AttnRes 1.737, Block AttnRes 1.746 và mHC-lite 1.747. Một comparison 48B Kimi Linear báo cáo AttnRes cao hơn hoặc hòa ở 15 benchmark, nhưng vẫn là model/recipe/evaluation của tác giả.[^attnres-2026]

Các số trên khác model size, data, optimizer, layer allocation, definition của variant, benchmark harness và implementation. Chênh lệch không hỗ trợ kết luận “GR thắng mHC” hay “AttnRes thắng GR” nói chung.

### 5.3 Memory wall và serving

- **mHC/HC/GR:** state hiện tại rộng $n$ lần về activation/residual traffic. HC cần đọc/ghi và tạo cả $H^{res}$; mHC thêm projection/Sinkhorn nhưng có fused kernels; GR bỏ branch mixing để giảm traffic, song vẫn phải mang bốn branch. Qwen báo cáo FP8 residual state có thể giảm một nửa bytes so với BF16, nhưng bundle chưa có deployable kernel hay independent measurement.[^mhc-2025][^qwen38-next-report]
- **Full AttnRes:** giữ source theo depth và có dependency theo depth; đây là chi phí khác với KV cache theo token. Block AttnRes giảm persistent source/communication theo số block, nhưng long-context prefill vẫn lưu block representations theo token. Kimi report/implementation dùng block summaries và đo overhead workload-specific.[^attnres-2026]
- **Không cơ chế nào trong ba cơ chế tự giảm token KV cache.** Muốn xử lý context dài phải ghép chúng với KDA/SSM, MLA, sparse attention hoặc compression; đó là lý do Kimi, DeepSeek, GLM và Qwen phân công các mechanism theo các axes khác nhau.[^attnres-2026][^qwen38-next-modeling]

## 6. Kết luận thực dụng

| Nếu bottleneck chính là… | Nên thử trước | Vì sao |
|---|---|---|
| activation outlier hoặc muốn gate nhẹ trên baseline | GatedNorm / Highway-style gate | thay đổi nhỏ, dễ làm ablation trên cùng stream |
| muốn kiểm tra multi-stream với chi phí logic thấp | AltUp-style static widening | tách effect của residual width khỏi dynamic topology |
| muốn branch interaction có stability rationale rõ | mHC | giữ $H^{res}$ nhưng ràng buộc doubly stochastic; phải profile Sinkhorn/fusion |
| muốn multi-stream với I/O và topology đơn giản hơn | GR | feature-wise read, scalar write, không có $H^{res}$; cần đo stability riêng |
| nghi ngờ layer cũ bị gộp/dilute trong stack sâu | Full AttnRes ở scale nhỏ, sau đó Block AttnRes | kiểm tra depth retrieval trước, rồi giảm state bằng block sweep |
| có recurrent mixer tạo ra signal hữu ích cần đi vào backbone | CLVR-style side route | route một tín hiệu cụ thể thay vì lưu toàn bộ depth history |

Protocol tối thiểu cho so sánh công bằng: giữ token mixer, MoE, data order, optimizer, depth/width và budget cố định; dùng baseline residual làm control; đo loss **và** task metrics; plot activation/gradient norms và gate entropy; đo peak activation, bytes qua pipeline, prefill, one-token decode, batch/concurrency; lặp seed. Không dùng headline của Qwen, DeepSeek, GLM hay Kimi để gán causal effect cho residual module riêng lẻ.

**Tóm tắt một câu:** `mHC` là *widen + constrain the carry topology*; `GR` là *widen + gate the read, simplify the write*; `AttnRes` là *keep depth sources + retrieve selectively*. Chúng cùng đẩy residual từ một phép cộng cố định thành một hệ thống information-flow có thể thiết kế, nhưng tối ưu các bottleneck khác nhau.

## Relationships

- **Synthesizes:** [Qwen Gated Residual](qwen-gated-residual.md), [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md), [Attention Residuals](attention-residuals.md), and [Cross-layer value routing for delta memories](cross-layer-value-routing-for-delta-memories.md).
- **Explains the residual axis in:** [Depth and residual-path design — khóa học cho người mới](depth-and-residual-path-design-beginners-course.md).
- **Connects to model deployments:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), [GLM-5.3-Flash hybrid multimodal architecture](glm-5-3-flash-hybrid-multimodal-architecture.md), [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md).
- **Contrasts:** residual/depth information flow with [Multi-head Latent Attention](multi-head-latent-attention.md) and fixed-state [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), which operate primarily on token-sequence memory.

## Evidence limits

The comparison combines primary or source-level evidence from the Transformer, Qwen3.8-Next, mHC, Attention Residuals and Linear Attention Architectures bundles, plus maintained wiki concepts. The main quality, stability and systems numbers are author-run, configuration-bound and mostly single-study point estimates; there is no independent replication or common head-to-head benchmark across GR, mHC and AttnRes in the available evidence. VWN, RMT, MUDDFormer, xHC and related macro-designs are mentioned only where the supplied reports expose enough information to identify the research neighborhood; they are not ranked here.[^qwen38-next-report][^mhc-2025]

[^transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex), architecture and residual sublayers.
[^qwen38-next-report]: Qwen Team, “On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability,” [technical report](../raw/Qwen3.8-Flash-Next-tech_report/qwen3.8-flash-next-tech_report.md), Section 2.2 and Tables 5–6.
[^qwen38-next-modeling]: Qwen Team and Hugging Face, “Qwen4-Exp Transformers modeling implementation,” [source](../raw/Qwen3.8-Flash-Next/modeling_qwen4_exp.py), Gated Residual implementation.
[^mhc-2025]: Xie et al., “mHC: Manifold-Constrained Hyper-Connections,” [source](../raw/2512.24880_mHC/main.tex), Sections 1–5 and Appendix.
[^attnres-2026]: Kimi Team, “Attention Residuals,” [source](../raw/arXiv-2603.15031v1/main.tex), mechanism, block form, systems analysis and evaluation.
[^linear-attention-architectures-2026]: Cerruti et al., “Linear Attention Architectures: Mechanisms, Trade-offs, and Cross-Layer Routing,” [source](../raw/2607.07953_LinearAttentionArchitectures/template.tex), Sections 4.3 and 5.6–5.7.
