---
type: Synthesis
title: "Residual-path extensions và cross-layer routing — khóa học cho người mới"
description: A top-down beginner course extending the depth-path stage with feature-gated multi-stream Gated Residual and CLVR side routing from recurrent memory, separating capacity widening, constrained mixing, depth retrieval, and cross-layer value injection.
tags: [learning-roadmap, residual-connections, gated-residual, hyper-connections, attention-residuals, cross-layer-routing, pytorch]
status: stable
created: 2026-09-02
generated:
  by: llm-wiki-agent/1
  at: 2026-09-02T11:22:32+07:00
sources:
  - id: residual-comparison
    resource: residual-path-architecture-comparison.md
    title: "So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path"
  - id: qwen-gr-concept
    resource: qwen-gated-residual.md
    title: "Qwen Gated Residual"
  - id: mhc-concept
    resource: manifold-constrained-hyper-connections.md
    title: "Manifold-constrained Hyper-Connections"
  - id: attnres-concept
    resource: attention-residuals.md
    title: "Attention Residuals"
  - id: attnres-eval
    resource: attention-residuals-evaluation-and-systems-trade-offs.md
    title: "Attention Residuals evaluation and systems trade-offs"
  - id: clvr-concept
    resource: cross-layer-value-routing-for-delta-memories.md
    title: "Cross-layer value routing for delta memories"
  - id: qwen38-arch
    resource: qwen3-8-flash-next-architecture-and-implementation.md
    title: "Qwen3.8-Flash-Next architecture and implementation"
  - id: depth-course
    resource: depth-and-residual-path-design-beginners-course.md
    title: "Depth and residual-path design — khóa học cho người mới"
  - id: kimi-k3-concept
    resource: kimi-k3-hybrid-retrieval-architecture.md
    title: "Kimi K3 hybrid retrieval architecture"
  - id: deepseek-v4-concept
    resource: deepseek-v4-hybrid-architecture-and-pretraining.md
    title: "DeepSeek-V4 hybrid architecture and pretraining"
---

# Residual-path extensions và cross-layer routing — khóa học cho người mới

`Residual path` (đường truyền theo chiều sâu) quyết định representation nào của **cùng một token** được mang qua các layer. Stage 8.1 đã cover `standard residual`, `Attention Residuals` (`AttnRes`) và `manifold-constrained Hyper-Connections` (`mHC`). Khóa học này mở rộng theo hai hướng mới: **feature-gated multi-stream residual** — `Qwen Gated Residual` (`GR`) — và **side routing từ recurrent memory** — `Cross-Layer Value Routing` (`CLVR`). Điểm quan trọng nhất: bốn hướng `capacity widening`, `constrained mixing`, `depth retrieval` và `cross-layer value injection` không phải bốn mức trên cùng một trục; chúng tối ưu bốn bottleneck khác nhau và có `guarantee` rất khác nhau.[^residual-comparison][^qwen-gr-concept][^clvr-concept]

> [!success] Sau bài này
> 1. Bạn trả lời được đủ năm câu — giải quyết vấn đề gì, hoạt động ra sao, tác động gì, khác baseline thế nào, dùng thực tế khi nào — **trước khi** đọc công thức.
> 2. Bạn trace được một token qua `standard residual`, `mHC`, `Gated Residual`, `Block AttnRes` và `CLVR`, kèm `ledger` về retained state, extra reads/writes, communication và `guarantee` nào có thật.
> 3. Bạn tách được bốn hướng mở rộng residual-path và hiểu vì sao `GR` không phải `mHC` đổi tên, `CLVR` không phải `AttnRes`.
> 4. Bạn chạy được PyTorch toy của `GR` và `CLVR`, kiểm chứng bằng `torch.testing.assert_close`, và đọc số ablation theo đúng evidence limits của chúng.

## 1. Trước khi đọc

Đây là stage 8.5, mở rộng trực tiếp [Depth and residual-path design — khóa học cho người mới](depth-and-residual-path-design-beginners-course.md) (stage 8.1). Bạn nên đã hiểu ở mức trực giác:

- `standard residual` cộng dồn update qua depth, và hai trục **sequence axis** (token positions) với **depth axis** (layers của cùng một token) là khác nhau;
- `AttnRes` làm các representation theo depth trở thành nguồn có thể truy hồi; `mHC` giữ nhiều residual channels và ràng buộc mixing map.

Nếu chưa, đọc stage 8.1 trước. Bài này không dạy lại derivation đầy đủ của `AttnRes`/`mHC`; nó recap ngắn ở tầng luồng và chỉ derive chi tiết phần **mới** (`GR` read/write gates, `CLVR` side route) ở tầng toán. Code không có token attention nên không có `position_ids` hay quy ước `interleaved RoPE`; đây là omission có chủ ý vì residual mixer không đụng positional mechanism.

## 2. Bức tranh toàn cảnh

### 2.1 Vấn đề: residual stream chỉ có một làn và một phép cộng

`Standard residual` cho mọi layer một identity highway: giữ input cũ, cộng update mới. Nó đơn giản nhưng mọi update trước bị gộp vào một running sum — layer trên không thể chọn riêng update nào, và toàn bộ signal phải chảy qua **một** làn có chiều rộng bằng hidden width. Khi model sâu và rộng, hai câu hỏi xuất hiện:

1. **Capacity:** một làn đủ rộng để mang các loại thông tin khác nhau của cùng một token không?
2. **Addressability:** layer trên có cách nào lấy đúng representation nó cần — theo depth, hoặc từ một component nội bộ — không?

Stage 8.1 đã trả lời câu hỏi addressability theo depth bằng `AttnRes` và câu hỏi multi-lane bằng `mHC`. Hai phần còn thiếu của bức tranh là:

- **đa làn mà không cần branch-mixing đắt và nguồn bất ổn** — `GR` đọc bằng gate theo từng feature, ghi bằng scalar theo từng stream, và bỏ hẳn ma trận trộn giữa các stream;[^qwen-gr-concept]
- **đưa tín hiệu nội bộ của một recurrent layer vào residual chung** — `CLVR` route write value của delta memory vào shared stream bằng một projection khởi đầu bằng không.[^clvr-concept]

**Ý tưởng cốt lõi trong một câu:** residual design chọn cách information được **giữ, chọn, trộn hoặc route qua depth**, và bốn hướng mở rộng — mở rộng capacity, ràng buộc mixing, truy hồi theo depth, route giá trị qua layer — tối ưu bốn bottleneck khác nhau, không thay thế nhau.[^residual-comparison]

### 2.2 Mental model: tòa nhà nhiều làn và cửa hàng phụ tùng

Nối tiếp mental model "hồ sơ đi qua tòa nhà" của stage 8.1:

```text
standard residual   một hồ sơ duy nhất, mỗi tầng ghi đè thêm vào đó

mHC                 hồ sơ chạy trên n làn; mỗi tầng có một "người điều phối"
                    (ma trận doubly stochastic) trộn các làn cho nhau trước khi
                    chuyển lên — điều phối bị ràng buộc để không dồn/mất mass

Gated Residual      vẫn n làn, NHƯNG bỏ người điều phối; mỗi tầng có một
                    "bộ lọc" (read gate theo từng ô thông tin) để đọc các làn,
                    và n cái "vòi" (write gate theo làn) để rót update vào

Block AttnRes       mỗi cụm tầng nộp một bản tóm tắt lên kệ; tầng trên chọn
                    giữa các bản tóm tắt thay vì nhận một hồ sơ tổng

CLVR                tòa nhà có một xưởng (recurrent memory) ở tầng l; xưởng
                    vừa ghi vào kho nhớ nội bộ, vừa gắn một "đường ống phụ"
                    (projection) đẩy nguyên liệu nó đang ghi vào hồ sơ chung
```

Khác biệt then chốt so với stage 8.1: `GR` và `CLVR` đại diện cho hai câu trả lời **tối giản có chủ ý**. `GR` bỏ đúng phần đắt nhất của `mHC` (branch-mixing matrix) và đầu tư vào read gate; `CLVR` không thay residual aggregation gì cả — nó **thêm một cạnh mới** vào data flow.

### 2.3 Bốn hướng phải tách riêng trước khi vào chi tiết

| Hướng | Đại diện | Câu hỏi nó trả lời | Đại diện control |
| --- | --- | --- | --- |
| `capacity widening` | AltUp-style static widening, `GR` | thêm làn residual có tự nó có giá trị không? | AltUp: read scalar tĩnh, write round-robin |
| `constrained mixing` | `mHC` | nhiều làn trộn nhau thế nào mà không nổ signal? | unconstrained HC (đối chứng âm) |
| `depth retrieval` | Full/`Block AttnRes` | layer trên chọn được representation cũ theo depth không? | fixed scalar mixing, sigmoid gating |
| `cross-layer value injection` | `CLVR` | tín hiệu nội bộ của một layer có đáng đi vào stream chung không? | CLER-H (route error vào value target của layer nhận) |

Bảng này là bản đồ đọc bài: mỗi cơ chế ở phần sau sẽ được đặt vào đúng ô của nó, và các số ablation sẽ được đọc trong ô của chính nó chứ không xếp hạng chéo.[^residual-comparison]

### 2.4 Bạn sẽ hiểu được gì

Sau bài này, khi đọc một kiến trúc mới nói "four residual streams" hay "gated residual", bạn sẽ trả lời được: đó là widening hay constrained mixing; gate nằm ở read hay write; có guarantee phổ nào không; retained state và traffic tăng bao nhiêu; và khi nào một side route kiểu CLVR là giả thuyết đáng thử.

## 3. Cách hoạt động — trace một token qua năm cơ chế

Xét lại token **"Paris"** trong câu “Paris là thủ đô của Pháp”, với các update minh họa theo depth như stage 8.1: embedding mang lexical identity, layer 1 nhấn entity type, layer 2 nhấn relation, layer 3 nhấn country link. Ta theo token này qua cả năm cơ chế và cuối mục có một `state ledger` thống nhất.

### 3.1 `Standard residual` — baseline recap

```text
h_l ────── identity ─────────────┐
 │                               │
 └─► Norm ─► branch ─► update ──► + ─► h_{l+1}
```

Token "Paris": hồ sơ sau layer 3 = embedding + update(entity) + update(relation) + update(country). Layer 4 nhận **một tổng**. Retained state: một vector width $D$ per token. Extra reads/writes: không. Guarantee: identity path và gradient trực tiếp.

### 3.2 `mHC` — nhiều làn, mixing bị ràng buộc

```text
lanes X (n streams)
   │
   ├─► READ  A ─► một layer input ─► branch ─► update ─► WRITE C ─┐
   │                                                              │
   └─► CARRY/MIX B (doubly stochastic) ────────────────────────────┴─► lanes kế tiếp
```

Token "Paris": ta hình dung một lane mang lexical identity, một lane mang relation, một lane mang context mixture (không có semantic label được bảo đảm — đây là mental model). Mỗi tầng: `A` đọc một mixture thành input width-$D$; branch xử lý; `C` ghi update về các lane; `B` — bị ràng buộc **doubly stochastic** (không âm, mỗi hàng và cột tổng bằng một) — trộn state cũ giữa các lane trước khi chuyển lên. Retained state: $n \times D$ per token. Extra reads/writes: đọc state cho `A`, tạo và áp `B` ($n\times n$), áp `C`; trong production còn có Sinkhorn iterations và fused kernels. Guarantee có thật: với `B` **exact**, $\lVert B\rVert_2\le1$ và tích qua depth vẫn doubly stochastic — nhưng chỉ cho **linear carry map**, không cho toàn nonlinear network, và implementation runtime chỉ xấp xỉ constraint bằng Sinkhorn hữu hạn.[^mhc-concept]

### 3.3 `Gated Residual` — widening + gate, bỏ mixing

```text
lanes R_1..R_n (n streams, cùng hidden width)
   │
   ├─► Norm từng lane ─► stack ─► flatten (n·D)
   │        │
   │        └─► READ-GATE bottleneck n·D → rank → n·D  (SiLU → sigmoid)
   │                 │  gate G_i theo từng FEATURE của từng lane
   │                 ▼
   │        x = mean_i ( G_i ⊙ Norm(R_i) )   ← một input width-D cho branch
   │
   ├─► branch ─► update y ─► WRITE-GATE: scalar s_i = 2σ(·) theo từng lane
   │                                  R_i ← R_i + s_i · y
   │
   └─► carried state: các lane cũ được GIỮ NGUYÊN (không có B, không Sinkhorn)
```

Token "Paris": trước branch attention, model nhìn cả bốn lane, nhưng **gate theo từng feature** quyết định ô thông tin nào của lane nào được đọc nhiều — ví dụ đọc mạnh phần relation từ lane 2 và phần identity từ lane 1, đọc yếu phần khác. Đó là một weighted mean, không phải một tổng. Sau branch, **một scalar mỗi lane** quyết định update được rót vào lane đó nhiều hay ít; lane cũ không bị trộn lẫn nhau. Vì vậy:

- **read fine-grained theo feature, write coarse theo lane** — sự bất đối xứng này là chủ đích thiết kế;[^qwen-gr-concept]
- không có ma trận $H^{res}$, nên bớt một full read của residual state và một nguồn instability, nhưng **mệnh đề phổ của mHC không được kế thừa**;[^qwen-gr-concept]
- ở Qwen3.8-Flash-Next, `GR` xuất hiện quanh **mỗi** token-mixer và MoE branch, với một read-only mixer cuối cùng thu bốn lane về width chuẩn trước output head.[^qwen38-arch]

Retained state: $n\times D$ per token (như mHC). Extra reads/writes: một lần read-gate computation + element-wise gating + mean; write scalars rất nhẹ. Không có branch-mixing pass. Ở chiều ngược lại, đây là lý do `GR` được chọn như một nhánh tối giản hóa `mHC` cho hệ thống thật.[^residual-comparison]

### 3.4 `Block AttnRes` — retrieval theo depth từ block summaries

```text
embedding ─────────────────────────┐
layers 1–12 ─► block summary 1 ────┤
layers 13–24 ─► block summary 2 ───┼─► pseudo-query chấm điểm + RMSNorm
...                                │   ─► softmax trên depth ─► mixture
block hiện tại (partial sum) ──────┘
```

Token "Paris": các update theo depth được gộp thành block summaries; một layer trong block 3 có thể đọc embedding, summary của block 1–2 và partial sum của block đang chạy, với weight softmax theo nội dung. Nó **không** tách được layer 2 ra khỏi summary đầu. Kimi K3 dùng tám block 12-layer cộng một partial final block — tính cả embedding source là chín nguồn truy hồi được.[^attnres-concept] Retained state: cỡ $N\times D$ per token theo số block (Full form là $L\times D$). Extra reads/writes: append summary tại block boundary; depth scoring mỗi sublayer. Communication: với pipeline parallelism, chỉ transfer $N$ summaries thay vì $L$ representation; report đo dưới 4% end-to-end training overhead.[^attnres-eval] Guarantee có thật: zero-init pseudo-query cho weights đều nhau lúc khởi đầu; hai limit $N=L$ (tiến về Full) và $N=1$ (tiến về standard accumulation + embedding source) — số block là compromise chất lượng–hệ thống, không phải optimum phổ quát.[^attnres-concept]

### 3.5 `CLVR` — side route từ recurrent memory vào stream chung

```text
                         ┌──────────────────────────────┐
                         │  recurrent layer (delta mem) │
h (shared stream) ──────►│  k, v từ h                   │
                         │  ghi v vào memory state W    │──► branch output y ──► h + y
                         │  s = v (write value nội bộ)  │
                         └──────────┬───────────────────┘
                                    │
                              P_l (zero-init)
                                    ▼
                          ε = P_l s  ──►  h ← h + y + ε
```

Token "Paris": một layer delta-memory của nó tính key `k` và write value `v` từ hidden state — `v` là "nguyên liệu" layer này ghi vào associative memory của nó. `CLVR` không đụng tới residual aggregation: nó cộng thêm $\varepsilon = P_l v$ vào shared residual stream, với $P_l$ khởi đầu bằng **zero** để model bắt đầu đúng bằng host baseline. Câu hỏi thiết kế là: tín hiệu nào đáng route? Trong các comparison được lưu, route **value** (`CLVR`) tốt hơn route **delta-rule error** (`CLER-H`) trong mọi hàng matched; giả thuyết của tác giả là error space của layer dưới chưa chắc khớp basis của layer nhận — đây là interpretation, không phải ablation nhân quả.[^clvr-concept]

Retained state: **không thêm** depth history — chỉ một projection per routing layer. Extra reads/writes: gần như không (một matvec trên tín hiệu đã có). Không có guarantee phổ; khởi đầu zero là guarantee duy nhất (route = baseline tại init).[^clvr-concept]

### 3.6 State ledger tổng hợp

| Cơ chế | Retained state per token | Extra reads/writes mỗi branch | Communication | Gate/mixing nằm ở đâu |
| --- | --- | --- | --- | --- |
| Standard | $D$ | 0 | baseline | không có |
| `mHC` | $nD$ | read `A`, áp `B` ($n{\times}n$) + Sinkhorn, áp `C` | widened state qua pipeline | `B` (constrained mixing giữa lane) |
| `GR` | $nD$ | read-gate bottleneck + gating + mean; write scalars | widened state qua pipeline, ít hơn mHC một mixing pass | read theo feature, write theo lane |
| Full `AttnRes` | $LD$ | depth scoring mỗi sublayer | transfer $L$ representation | softmax trên depth sources |
| `Block AttnRes` | $ND$ | depth scoring; append summary tại boundary | transfer $N$ summaries | softmax trên block summaries |
| `CLVR` | $0$ thêm (chỉ projection $P_l$) | một matvec side route | không đáng kể | gate không có — additive route |

Các bậc này là accounting cấu trúc từ tensor shapes, không phải cam kết latency end-to-end; fusion, layout và hardware có thể đảo thứ tự thực tế.[^residual-comparison] **Không cơ chế nào tự giảm token KV cache hay tăng context window** — chúng nằm trên depth axis, tách khỏi sequence axis.

## 4. Tác động

### 4.1 Hệ quả trực tiếp từ thiết kế

| Cơ chế | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
| --- | --- | --- | --- |
| `GR` | read theo feature cho phép layer chọn ô thông tin từ các lane; carried state trực tiếp (lane cũ giữ nguyên) | activation/traffic theo $n$ lane; read-gate compute mỗi branch | gate học được phải tìm được selection hữu ích; hệ thống phải chịu widened state |
| `CLVR` | tín hiệu nội bộ của recurrent layer tới được mọi layer sau và output head qua shared stream | một projection per routing layer (gần như free) | recurrent layer phải tạo write value có information layer sau cần dùng |
| `mHC` | branch interaction với bound cho linear carry map | Sinkhorn + mixing traffic theo $n$ | implementation fused; muốn branch trao đổi, không chỉ widen |
| `Block AttnRes` | depth sources có selectable weight với state bounded theo block | mất resolution trong block; scoring mỗi sublayer | learned pseudo-query phải tìm được selection hữu ích |

### 4.2 Bằng chứng ablation được báo cáo — đọc trong đúng ô của nó

Trong một matched 25B-A3B MoE comparison của Qwen, bảng residual ghi: `Pre-norm` loss 1.617 / trung bình 9 benchmark 50.91; `mHC static` 1.596 / 52.49; `mHC dynamic` 1.594 / 54.47; `GR` 1.590 / 54.66. Qwen kết luận channel-wise read gate hữu ích, scalar write gate là đủ, còn full branch-mixing matrix không giúp — đây là lý do trực tiếp cho thiết kế `GR`.[^qwen-gr-concept] Nhưng trong một loss comparison khác của cùng report, `Full AttnRes + GatedNorm` đạt 1.758 so với `GR` 1.762 — `GR` không uniformly superior.[^qwen-gr-concept]

Với `AttnRes`, ở ablation 436M: baseline 1.766, Full 1.737, Block 1.746, `mHC-lite` 1.747; và ở cùng thí nghiệm, fixed scalar mixing 1.749, sigmoid gating 1.741, softmax AttnRes 1.737 — evidence rằng phần content-dependent competitive selection có giá trị, không chỉ softmax hình thức.[^attnres-eval] Một matched 48B Kimi Linear comparison cho `AttnRes` cao hơn ở 14/15 benchmark và hòa một benchmark.[^attnres-eval]

Với `CLVR`, các single-run matched deltas so với no-routing baseline (âm = loss thấp hơn): `Gated DeltaNet 350M/1B` $-0.0103$; `GDN 350M/15B` $-0.0059$; `GDN 1.3B/40B` $-0.0019$; `DeltaNet 350M/1B` $-0.0119$; `DeltaNet 350M/15B` $-0.0016$. CLER-H (route error) thua CLVR ở mọi hàng. Effect nhỏ và **giảm khi training dài hơn hoặc scale lớn hơn**; tác giả diễn giải là possible diminishing headroom, không phải scaling law.[^clvr-concept]

> [!warning] Không xếp hạng chéo
> Các con số trên đến từ các paper khác nhau, khác model size, data, optimizer, block/variant definition và evaluation harness. Chúng minh họa trade-off trong setup của từng tác giả; không tồn tại common head-to-head benchmark giữa GR, mHC, AttnRes và CLVR trong evidence hiện có.[^residual-comparison]

### 4.3 Guarantee nào có thật, guarantee nào không chuyển

| Cơ chế | Guarantee có thật | Guarantee KHÔNG có / không chuyển |
| --- | --- | --- |
| `mHC` | exact doubly stochastic `B`: $\lVert B\rVert_2\le1$, đóng qua phép nhân — cho **linear carry map** | không áp cho `A`/`C`, nonlinear branch, optimizer; runtime `B` chỉ xấp xỉ (Sinkhorn hữu hạn); không chứng minh quality gain |
| `GR` | sigmoid gate bounded $[0,1]$, write scalar $[0,2]$; zero-init cho behavior khởi đầu biết trước (xem Section 7) | **không** kế thừa spectral bound của mHC — đã bỏ `B`; stability là observation thực nghiệm trong Qwen tests, không phải theorem |
| `Block AttnRes` | zero-init pseudo-query ⇒ weights đều lúc đầu; softmax không âm tổng 1; limits $N{=}L$/$N{=}1$ | không biến depth state thành free memory; không làm KV cache fixed; 8 block là compromise của Kimi, không optimum phổ quát |
| `CLVR` | $P_l$ zero-init ⇒ model bắt đầu **chính xác** bằng host baseline | không có inference benchmark; chưa test trên KDA/Gated DeltaNet-2; không có downstream gain rõ (mixed checks) |

Đây là phần "guarantees that do or do not transfer" của stage 8.5: khi đọc một model dùng "gated residual", hãy hỏi guarantee nằm ở cột nào trước khi tin stability claim của nó.[^mhc-concept][^qwen-gr-concept][^clvr-concept]

### 4.4 Điều residual design không tự đổi

Đổi `GR`, `mHC`, `AttnRes` hay `CLVR` **không tự động**: giảm token KV cache; bỏ autoregressive decode order; tăng context window; sửa causal mask; thay token-attention FLOPs; bảo đảm downstream quality tăng. Đây là lý do Qwen3.8-Flash-Next ghép `GR` với Gated DeltaNet + Qwen Sparse Attention, Kimi K3 ghép Block `AttnRes` với KDA + MLA + MoE: các component giải quyết các axes khác nhau.[^qwen38-arch][^kimi-k3-concept]

## 5. Sự khác biệt

### 5.1 Bảng so sánh theo bốn chiều bắt buộc

| Cơ chế | Giống nhau | Khác nhau | Trade-off | Khi nào phù hợp |
| --- | --- | --- | --- | --- |
| Standard residual | branch vẫn nhận/trả width $D$ | cộng running state, coefficient cố định | đơn giản, ít state; không selective | baseline, model nhỏ, serving ưu tiên simplicity |
| AltUp-style widening (control) | nhiều lane như mHC/GR | read scalar tĩnh, write round-robin, không gate | rẻ về logic nhưng vẫn trả traffic $n$ lane; tách được "width tự nó có ích" | ablation control trước khi đầu tư gate/mixing |
| `mHC` | nhiều lane, read/write map | giữ `B` nhưng ràng buộc doubly stochastic | branch interaction + stability rationale; tốn Sinkhorn và mixing traffic | muốn branch trao đổi với bound cho linear carry |
| `GR` | nhiều lane như mHC | **bỏ `B`**; read gate theo feature, write scalar theo lane | bớt một mixing pass và một nguồn bất ổn; mất spectral argument | muốn multi-stream với I/O/topology tối giản, tự đo stability |
| Full/`Block AttnRes` | softmax retrieval như nhau | nguồn là representation theo **depth**, không phải lane | depth addressability; state/scoring theo depth | nghi ngờ update cũ bị dilute trong stack sâu |
| `CLVR` | additive vào shared stream như residual thường | route **tín hiệu nội bộ** của một layer, không thay aggregation | gần như free; effect nhỏ, single-run, chưa deploy | recurrent mixer có write value mà layer sau cần |

### 5.2 Thay đổi nằm ở đâu trong data flow?

```text
embedding ──► [branch] ──► [RESIDUAL AGGREGATION] ──► [branch] ──► ... ──► head

standard:      aggregation = cộng
mHC / GR:      aggregation = read/mix/write trên n lane   ← thay aggregation
AttnRes:       aggregation = softmax trên depth sources   ← thay aggregation
CLVR:          aggregation giữ nguyên; THÊM cạnh (P_l · s_l) từ recurrent layer
               vào shared stream                          ← thêm cạnh mới
```

Điểm cần nhớ: `CLVR` là cơ chế duy nhất trong bài **không thay residual aggregation** — nó thêm một cạnh song song. Vì vậy CLVR có thể组合 với bất kỳ aggregation nào ở trên (về mặt khái niệm; các nguồn hiện có không có thí nghiệm controlled cho tổ hợp này).[^clvr-concept][^residual-comparison]

### 5.3 Bốn nhầm lẫn cần dẹp trước khi vào kỹ thuật

1. **`GR` không phải `mHC` đổi tên.** Cùng bốn stream, nhưng `GR` không có ma trận branch-mixing doubly stochastic và không có Sinkhorn; mệnh đề phổ của mHC không chuyển sang `GR` và ngược lại, tính tối giản I/O của `GR` không phải của mHC.[^qwen-gr-concept]
2. **`CLVR` không phải `AttnRes`.** `AttnRes` thay thế uniform aggregation bằng retrieval theo depth; `CLVR` cộng thêm một tín hiệu route vào stream và giữ aggregation nguyên vẹn.[^clvr-concept]
3. **Widening không phải depth retrieval.** AltUp-style control cho thấy widening tự nó cũng có thể có giá trị (khoảng $-0.01$ loss trong một 25B/400B-token comparison của Qwen), nên phần "đáng giá" của `GR`/`mHC` phải so với control này, không chỉ với single-stream baseline.[^residual-comparison]
4. **Gate không phải constraint.** Gate (sigmoid `GR`) là cơ chế **học** kiểm soát amplitude/thông lượng; constraint (doubly stochastic `mHC`) là **bất đẳng thức** đúng với mọi giá trị học được của map đó. Hai loại guarantee khác loại nhau.

## 6. Trong thực tế

### 6.1 Cơ chế nằm ở đâu trong model thật?

- **Qwen3.8-Flash-Next** dùng `GR` quanh **mỗi** token-mixer và MoE branch của backbone 48-layer: bốn stream width 2,560, read-gate bottleneck rank 320, write scalar per stream, và một read-only mixer cuối trước head. Report còn ghi: lưu bốn stream residual bằng FP8 giảm một nửa residual-state bytes so với BF16 với gần như không mất chất lượng; và việc chỉ đọc hai branch có gate cao nhất trông trung tính ở pre-training nhưng **suy giảm sau post-training** nên bị từ chối — một negative result đáng giá cho ai định "tối ưu" bằng cách bớt lane lúc serving.[^qwen38-arch][^qwen-gr-concept]
- **DeepSeek-V4** dùng `mHC` $n=4$ với fused mixed-precision kernels, selective activation recomputation và communication overlap; report 6.7% extra training time ở $n=4$. GLM-5.3-Flash cũng công bố bốn stream mHC trong backbone. Ở cả hai model, mHC đi cùng compressed/sparse attention, MoE và optimizer changes — headline không thể gán cho mHC riêng.[^mhc-concept][^deepseek-v4-concept]
- **Kimi K3** dùng Block `AttnRes` (8 block × 12 layer + partial final block) bên cạnh KDA, periodic MLA và sparse MoE. Systems numbers của report: dưới 4% training overhead dưới pipeline parallelism, dưới 2% inference-latency overhead trên typical workloads, I/O residual-mechanism amortized $5.5d$/layer so với $3d$ của standard; ví dụ 128K-token prefill cần 15GB block representations trước sharding, giảm còn ~1.9GB per device với sequence sharding và dưới 0.3GB với 16K chunked prefill — tất cả là configuration-specific claims.[^attnres-concept][^attnres-eval][^kimi-k3-concept]
- **`CLVR`** còn ở giai đoạn research: single-run matched comparisons trong một paper, chưa thấy trong checkpoint triển khai nào trong evidence của wiki, chưa có inference-speed benchmark, chưa test trên KDA hay Gated DeltaNet-2 (nơi erase/write tách riêng khiến tín hiệu route ít rõ hơn).[^clvr-concept]

### 6.2 Walkthrough: chọn hướng residual cho một hybrid recurrent-majority model

Giả sử bạn thiết kế một model kiểu Qwen3.8-Flash-Next (ba recurrent layer + một sparse-attention layer mỗi group, MoE sau mỗi mixer):

1. **Bắt đầu với standard residual làm control.** Đo validation loss, activation/gradient norms, peak memory, prefill và one-token decode riêng.
2. **Test giả thuyết widening rẻ trước:** AltUp-style static widening (n lane, read tĩnh). Nếu widening tự nó đã giảm loss, bạn biết có "capacity headroom" trong residual stream.
3. **Nếu muốn branch interaction:** thêm `mHC` — nhưng profile Sinkhorn, mixing traffic và fused kernels; bound của nó chỉ có nghĩa nếu bạn giữ `B` exact hoặc xấp xỉ đủ tốt.
4. **Nếu muốn tối giản I/O:** `GR` — kiểm tra stability riêng (activation outliers, loss spikes) vì không còn spectral argument; đo gate entropy theo depth để thấy lane có thực sự được dùng khác nhau không.
5. **Nếu nghi update cũ bị dilute theo depth:** thử `AttnRes` ở scale nhỏ trước (Full), rồi sweep block count nếu state quá lớn; đừng lấy 8 block vì Kimi dùng 8.
6. **Nếu recurrent layer của bạn tạo write value mà layer sau không thấy:** thử `CLVR` như một additive hypothesis gần như free; đo matched loss với và không với route; nhớ effect nhỏ và có thể giảm theo training dài.
7. **Chỉ đổi một biến mỗi ablation.** Ghép GR + AttnRes + CLVR cùng lúc trong một run mới khiến bạn mất khả năng attribution hoàn toàn.

### 6.3 Khi nào nên và không nên dùng?

**Cân nhắc `GR` khi:** đã có evidence widening có ích nhưng mixing pass của mHC đắt hoặc bất ổn; có thể đo activation outliers và gate behavior; serving stack chịu được $n$-lane state (hoặc FP8 cho nó). **Không** khi model nhỏ, latency budget chặt, hoặc khi bạn định trích stability guarantee của mHC cho nó.

**Cân nhắc `CLVR` khi:** host là DeltaNet-style recurrent layer; bạn có matched-ablation culture (nó là hypothesis một-nhánh, rẻ để thử, dễ để sai—effect nhỏ); muốn toàn bộ depth sau và output head thấy tín hiệu này. **Không** khi cần một mechanism bù capacity lớn, hoặc khi host là KDA/GDN-2 mà chưa có ai chọn được routed signal tương đương.

### 6.4 Measurement bắt buộc và claim không suy ra được từ lý thuyết

| Nhóm | Measurement |
| --- | --- |
| Quality | matched validation loss, task metrics, seed repeats nếu có |
| Behavior | gate values/entropy (GR), depth weights (AttnRes), routed-signal norm (CLVR), activation/gradient norms |
| Memory | peak activation ($n$ lane), retained block summaries, FP8 bytes nếu dùng |
| Latency | prefill và one-token decode riêng; concurrency sweep |
| Distributed | bytes qua pipeline stage, Sinkhorn/fusion overhead (mHC) |

Claim **không** suy ra được chỉ từ cơ chế: benchmark gain của model dùng GR/AttnRes (cần ablation isolate); FP8 an toàn cho residual state ở model khác (single author claim); một trong bốn branch "chuyên" long-range (mechanistic probe trên 5 checkpoint của Qwen, không phải law); CLVR có lợi ở scale lớn hơn (effect đang giảm dần trong các run có sẵn).[^qwen-gr-concept][^attnres-eval][^clvr-concept]

> [!warning] Gate trước phần toán
> Đến đây bạn phải trả lời được: (1) bốn hướng mở rộng giải quyết bốn bottleneck khác nhau; (2) `GR` đọc theo feature/ghi theo lane và bỏ mixing, `CLVR` thêm cạnh route từ recurrent memory vào stream chung; (3) chi phí là widened state (GR/mHC), depth state (AttnRes) hoặc gần như không (CLVR); (4) guarantee phổ chỉ có ở mHC và chỉ cho linear carry map; (5) deployment cần matched ablation vì các số hiện có là author-run và không có head-to-head chung. Nếu chưa chắc, đọc lại Sections 2–6 trước khi zoom in.

## 7. Toán học — zoom in sau trực giác

Stage 8.1 đã derive standard sum, softmax depth mixture, block summaries và doubly stochastic constraint đầy đủ; phần dưới chỉ recap kết quả đó ở mức cần dùng, rồi derive chi tiết hai phần mới: `GR` và `CLVR`.

### 7.1 Bảng ký hiệu

| Ký hiệu | Nghĩa | Shape ví dụ |
| --- | --- | --- |
| $B,T,D$ | batch, sequence length, hidden width | 2, 5, 8 |
| $n$ | số residual streams (`GR`/mHC) | 4 |
| $r$ | rank của read-gate bottleneck | 320 (Qwen), 8 (toy) |
| $L$ | số sublayers | 96 |
| $N$ | số block trong Block `AttnRes` | 8 |
| $h_l$ | hidden representation tại depth $l$ (shared stream) | $(B,T,D)$ |
| $X_l$ / $R$ | widened residual state | $(B,T,n,D)$ |
| $G_i$ | read gate của stream $i$, theo feature | $(B,T,D)$ |
| $s_i$ | write scalar của stream $i$ | $(B,T)$ |
| $y$ | branch output (update) | $(B,T,D)$ |
| $v_{l,t}$ | write value nội bộ của recurrent layer $l$ tại token $t$ | $(B,T,D_v)$ |
| $P_l$ | projection của CLVR ($D_v\to D$), zero-init | $(D, D_v)$ |
| $A_l,B_l,C_l$ | mHC read / carry-mix / write maps | — |

### 7.2 Recap: standard accumulation và hai kết quả stage 8.1

Standard residual với $v_0$ = embedding và $v_{i+1}=F_i(h_i)$ cho $h_l=\sum_{i=0}^{l-1}v_i$: layer trên nhận tổng, không nhận selector từng $v_i$. Hai kết quả sẽ dùng lại:

- **Block `AttnRes`** thay tổng bằng softmax mixture $\alpha_{i\to l}$ trên embedding, các block summary $b_n=\sum_{j\in\mathcal{B}_n}F_j(h_j)$ và partial block; limit $N=L$ tiến về Full, $N=1$ tiến về standard accumulation với embedding source riêng.
- **`mHC`** update $X_{l+1}=B_lX_l+C_lF(A_lX_l)$ với $B_l$ doubly stochastic: $B_l\ge0$, $B_l\mathbf{1}=\mathbf{1}$, $\mathbf{1}^\top B_l=\mathbf{1}^\top$, suy ra $\lVert B_l\rVert_2\le1$ (Birkhoff–von Neumann) — chỉ cho linear carry map.

Chi tiết derivation: xem [Depth and residual-path design](depth-and-residual-path-design-beginners-course.md) Sections 7.2–7.5.[^depth-course]

### 7.3 `Gated Residual`: read gate theo feature

**Trực giác.** Layer nhìn toàn bộ $n$ stream nhưng lọc theo từng ô thông tin trước khi lấy trung bình.

**Công thức.** Với normalized streams $\hat R_i=\operatorname{Norm}(R_i)$ và flattened state $\tilde X=[\hat R_1;\dots;\hat R_n]\in\mathbb{R}^{nD}$:

$$
G=\sigma\!\left(W_{\text{up}}\operatorname{SiLU}\!\left(W_{\text{down}}\tilde X\right)\right),\qquad
G\in\mathbb{R}^{n\times D},
$$

$$
x=\frac{1}{n}\sum_{i=1}^{n}G_i\odot\hat R_i. \tag{1}
$$

**Ý nghĩa ký hiệu.** $W_{\text{down}}\in\mathbb{R}^{r\times nD}$ và $W_{\text{up}}\in\mathbb{R}^{nD\times r}$ là bottleneck rank-$r$ (Qwen dùng $r=320$ với $D=2{,}560$, $n=4$); $\sigma$ là sigmoid nên $G_i\in(0,1)$ theo từng feature; trung bình $1/n$ giữ scale của một stream.[^qwen-gr-concept]

**Shape flow.**

```text
R                         (B,T,n,D)
Norm từng stream          (B,T,n,D)
flatten n·D               (B,T,n·D)
W_down                    (n·D, r)      → (B,T,r)
SiLU → W_up               (r, n·D)      → (B,T,n·D)
sigmoid                   G             (B,T,n,D)
G_i ⊙ R̂_i, mean trên n   x             (B,T,D)
```

**Ví dụ số.** Hai stream width 2, normalized: $\hat R_1=[1,0]$, $\hat R_2=[0,1]$; gates $G_1=[0.9,0.1]$, $G_2=[0.2,0.8]$. Gated: $[0.9,0]$ và $[0,0.8]$; trung bình $x=[0.45,0.4]$. Nếu bỏ gate (all-ones), $x$ sẽ là $[0.5,0.5]$ — gate đã thiên position 0 về stream 1 và position 1 về stream 2.

**Kết luận.** Read là **weighted mean theo feature**, content-dependent qua bottleneck rank-$r$; nó rẻ hơn một full $n{\times}n$ mixing pass vì chỉ đi qua một hẹp channel.

### 7.4 `Gated Residual`: write gate theo stream và carried state

**Trực giác.** Update được rót vào từng lane với cường độ riêng; lane cũ giữ nguyên.

**Công thức.**

$$
s_i=2\sigma\!\left(u_i^\top\operatorname{Norm}(\tilde X)\right)\in(0,2),\qquad
R_i'=R_i+s_i\,y. \tag{2}
$$

**Ý nghĩa ký hiệu.** $u_i$ là vector trọng số của write projection cho lane $i$; hệ số $2\sigma$ cho phép vừa attenuate ($<1$) vừa amplify ($>1$) so với carried state; $y$ là branch output width $D$.

**Shape flow.**

```text
Norm(R).flatten       (B,T,n·D)
write projection      (n·D, n)      → logits (B,T,n)
2·sigmoid             s             (B,T,n)
R                     (B,T,n,D)
R' = R + s[...,None]·y[...,None,:]  (B,T,n,D)
```

**Ví dụ số.** $y=[2,-1]$; $s=[1.5,0.5]$; $R_1=[1,1]$, $R_2=[2,0]$. Khi đó $R'_1=[1,1]+1.5[2,-1]=[4,-0.5]$ và $R'_2=[2,0]+0.5[2,-1]=[3,-0.5]$. Lane 1 nhận update mạnh gấp ba lane 2.

**Kết luận.** Write coarse theo lane nhưng có dải $(0,2)$; carried path là identity thuần ($R_i$ xuất hiện nguyên vẹn trong $R_i'$), khác mHC nơi carried state đi qua $B_l$. Đây chính là chỗ guarantee của mHC bị bỏ: tích của các write map **không** bị ràng buộc doubly stochastic nên không có bound $\le1$ cho carried path ở dạng tổng quát.

> [!note] Zero-init của toy so với production
> Với $W_{\text{down}}=W_{\text{up}}=0$, mọi gate bằng $\sigma(0)=0.5$ nên $x=\tfrac12\operatorname{mean}_i\hat R_i$; với write projection zero, $s_i=2\sigma(0)=1$ nên mọi lane nhận nguyên update. Đây là behavior của **toy implementation** dưới đây (chọn để kiểm chứng được), không phải claim về initialization của checkpoint Qwen thật, mà wiki không ghi chi tiết.

### 7.5 `CLVR`: side route với zero-init projection

**Trực giác.** Đưa write value của recurrent layer vào stream chung, nhưng khởi đầu bằng không để không phá host baseline.

**Công thức.** Với write value nội bộ $s_{l,t}=v_{l,t}$:

$$
\varepsilon_{l,t}=P_l\,s_{l,t},\qquad
h_{l,t}\leftarrow h_{l,t}+y_{l,t}+\varepsilon_{l,t}, \tag{3}
$$

với $P_l$ zero-initialized (tùy chọn low-rank), nên $\varepsilon\equiv0$ tại init.[^clvr-concept]

**Ý nghĩa ký hiệu.** $v_{l,t}$ là giá trị layer $l$ ghi vào associative memory của nó tại token $t$; $P_l\in\mathbb{R}^{D\times D_v}$; $y_{l,t}$ là branch output bình thường của layer; phép cộng vào $h$ đưa route tới **mọi** layer sau và output head vì chúng đều đọc shared stream.

**Shape flow.**

```text
h                     (B,T,D)
Norm(h) → k,v         (B,T,D_k), (B,T,D_v)
delta memory update   W ← W + φ(k)(v − Wφ(k))ᵀ-style   (state nội bộ)
branch output y       (B,T,D)
P_l v                 ε (B,T,D)
h' = h + y + ε        (B,T,D)
```

**Ví dụ số.** $h=[1,2]$, $v=[0.5,-1,3]$ ($D_v=3$), $P=\begin{bmatrix}0.1&0&0\\0&0.2&0\end{bmatrix}$. $\varepsilon=[0.05,-0.2]$; nếu $y=[0.1,0.1]$ thì $h'=[1.15,1.9]$. Chỉ hai thành phần đầu của $v$ được route — $P$ chọn "cạnh nhìn" nào của write value đi vào stream.

**Kết luận.** Route là một linear map một-nhánh: thêm capacity thông tin cho stream mà **không** thêm depth state và gần như không thêm compute.

**Vì sao route value tốt hơn route error (CLER)?** Phiên bản CLER đổi value target của layer nhận: $\tilde v_{l,t}=v_{l,t}+\Gamma_l r_{p(l),t}$ với $r=v-\bar v$ là delta-rule error. Trong mọi matched row có sẵn, CLER-H thua CLVR; tác giả diễn giải bằng **basis mismatch** — error space của layer dưới học độc lập, chưa chắc khớp value space của layer nhận — còn residual stream là "không gian chung" mà mọi layer sau đều đã đọc. Đây là interpretation, không phải ablation nhân quả.[^clvr-concept]

**Derivation ngắn: zero-init là exact baseline.** Tại init, $\varepsilon_{l,t}=P_ls_{l,t}=0$ với mọi $l,t$ vì $P_l=0$. Do đó $h'_{l,t}=h_{l,t}+y_{l,t}$ đúng bằng forward của host model không có route; gradient ban đầu đẩy $P_l$ lớn lên theo hướng giảm loss (vì $\partial\varepsilon/\partial P_l = s_{l,t}\neq0$ nói chung), nhưng model không bao giờ "bắt đầu tệ hơn" baseline. Đây là cùng một pattern zero-init dùng ở pseudo-query của AttnRes và các projection residual khác.[^clvr-concept][^attnres-concept]

### 7.6 Đặt CLVR cạnh các cơ chế còn lại (tổng hợp)

| | Aggregation bị thay? | State thêm | Tín hiệu đến đâu |
| --- | --- | --- | --- |
| `GR`/mHC | có — read/mix/write trên $n$ lane | $nD$ per token | lane được carry qua depth |
| `AttnRes` | có — softmax theo depth | $ND$ hoặc $LD$ | layer sau chọn source |
| `CLVR` | **không** — cộng thêm cạnh | ~0 | mọi layer sau + head, qua shared stream |

## 8. Implementation — PyTorch tối thiểu và inspectable

Code cụ thể hóa đúng ba data flow mới: read gate + write gate của `GR` (Sections 3.3, 7.3–7.4) và zero-init side route của `CLVR` (Sections 3.5, 7.5), kèm một delta-memory stub tạo write value. `GR` toy dùng một `RMSNorm` dùng chung cho mọi stream (Qwen dùng grouped RMSNorm) và zero-init weights để behavior khởi đầu kiểm chứng được — cả hai đều ghi rõ là teaching simplification. Production cần fused kernels, FP8 layout và read-only mixer cuối stack.[^qwen-gr-concept][^qwen38-arch]

```python
import torch
import torch.nn as nn
import torch.nn.functional as F


class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        # chấp nhận (..., D) hoặc (..., n, D): normalize trên chiều cuối
        rms = x.square().mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight


class PreNormResidual(nn.Module):
    """Section 3.1: baseline identity + normalized branch update."""

    def __init__(self, d, branch):
        super().__init__()
        self.norm = RMSNorm(d)
        self.branch = branch

    def forward(self, h):                      # h: (B,T,D)
        return h + self.branch(self.norm(h))   # (B,T,D)


class GatedResidual(nn.Module):
    """Sections 3.3 / 7.3-7.4: feature-wise read gate, per-stream scalar write gate.

    Toy simplifications so với Qwen4-Exp (ghi rõ):
      - một RMSNorm dùng chung cho mọi stream (Qwen: grouped RMSNorm);
      - read/write weights zero-init để khởi đầu kiểm chứng được
        (không claim sao chép init của checkpoint thật).
    """

    def __init__(self, d, n_streams=4, rank=8):
        super().__init__()
        self.n, self.d = n_streams, d
        self.norm = RMSNorm(d)
        self.gate_down = nn.Linear(n_streams * d, rank, bias=False)
        self.gate_up = nn.Linear(rank, n_streams * d, bias=False)
        self.write_proj = nn.Linear(n_streams * d, n_streams, bias=False)
        nn.init.zeros_(self.gate_down.weight)
        nn.init.zeros_(self.gate_up.weight)
        nn.init.zeros_(self.write_proj.weight)

    def read(self, x):
        # x: (B,T,n,D) -> branch input (B,T,D)
        normed = self.norm(x)                              # (B,T,n,D)
        flat = normed.flatten(start_dim=-2)                # (B,T,n*D)
        gates = torch.sigmoid(
            self.gate_up(F.silu(self.gate_down(flat)))     # (B,T,n*D)
        ).view(*x.shape)                                   # (B,T,n,D)
        return (gates * normed).mean(dim=-2)               # (B,T,D)

    def write(self, x, y):
        # x: (B,T,n,D); y: (B,T,D) -> (B,T,n,D)
        normed = self.norm(x)
        flat = normed.flatten(start_dim=-2)                # (B,T,n*D)
        s = 2.0 * torch.sigmoid(self.write_proj(flat))     # (B,T,n)
        return x + s.unsqueeze(-1) * y.unsqueeze(-2)       # (B,T,n,D)

    def forward(self, x, branch):
        y = branch(self.read(x))                           # (B,T,D)
        return self.write(x, y)                            # (B,T,n,D)


class ToyDeltaMemory(nn.Module):
    """Section 3.5/7.5: delta-rule memory stub chỉ để tạo write value v.

    One-feature-map causal delta rule, KHÔNG có normalization của outer
    product và KHÔNG chunkwise — teaching stub, không phải DeltaNet.
    """

    def __init__(self, d, d_value):
        super().__init__()
        self.k_proj = nn.Linear(d, d, bias=False)
        self.v_proj = nn.Linear(d, d_value, bias=False)

    def write_values(self, h):
        k = self.k_proj(h)                                 # (B,T,Dk)
        v = self.v_proj(h)                                 # (B,T,Dv)
        B, T, Dk = k.shape
        W = k.new_zeros(B, Dk, v.shape[-1])                # memory state
        outs = []
        for t in range(T):
            pred = torch.einsum("bk,bkv->bv", k[:, t], W)  # W φ(k_t)
            r = v[:, t] - pred                             # correction
            W = W + torch.einsum("bk,bv->bkv", k[:, t], r) # delta update
            outs.append(pred)
        return v, torch.stack(outs, dim=1)                 # write value, prediction


class CLVRSideRoute(nn.Module):
    """Sections 3.5 / 7.5: ε = P s cộng vào shared stream; P zero-init."""

    def __init__(self, d_value, d):
        super().__init__()
        self.proj = nn.Linear(d_value, d, bias=False)
        nn.init.zeros_(self.proj.weight)

    def forward(self, h, s):
        # h: (B,T,D); s: (B,T,Dv) -> (B,T,D)
        return h + self.proj(s)


class RecurrentBlockWithCLVR(nn.Module):
    """Một recurrent branch + side route theo công thức (3): h' = h + y + P v."""

    def __init__(self, d, d_value):
        super().__init__()
        self.norm = RMSNorm(d)
        self.memory = ToyDeltaMemory(d, d_value)
        self.out_proj = nn.Linear(d_value, d, bias=False)
        self.clvr = CLVRSideRoute(d_value, d)

    def forward(self, h):
        x = self.norm(h)
        v, pred = self.memory.write_values(x)   # write value + prediction
        y = self.out_proj(pred)                  # branch output (B,T,D)
        return self.clvr(h + y, v)               # (h + y) + P v
```

> [!note] Ranh giới toy/production
> Python loop của `ToyDeltaMemory` và `torch.stack` là để inspect, không phải serving. Production delta memory dùng chunkwise WY/UT-style training và recurrent decode; production `GR` cần fused read/write traversing widened state một lần mỗi chiều.[^qwen-gr-concept]

## 9. Verification trước benchmark

Chạy sau implementation block; mọi so sánh số dùng tolerance tường minh, `float32`.

```python
torch.manual_seed(11)
torch.set_default_dtype(torch.float32)
RTOL, ATOL = 1e-5, 1e-6
B, T, D, N_STREAMS = 2, 5, 8, 4

# Test 1 — GR zero-init read: gate ≡ 0.5 ⇒ x = 0.5 * mean(normed streams)
gr = GatedResidual(D, n_streams=N_STREAMS, rank=8)
x = torch.randn(B, T, N_STREAMS, D)
read = gr.read(x)
expected = 0.5 * gr.norm(x).mean(dim=-2)
torch.testing.assert_close(read, expected, rtol=RTOL, atol=ATOL)
assert read.shape == (B, T, D)

# Test 2 — GR zero-init write: s ≡ 1 ⇒ mọi stream nhận nguyên update
y = torch.randn(B, T, D)
written = gr.write(x, y)
torch.testing.assert_close(written, x + y.unsqueeze(-2), rtol=RTOL, atol=ATOL)
assert written.shape == x.shape

# Test 3 — write-gate bounds: s ∈ (0, 2) và update khớp phép tính manual
with torch.no_grad():
    gr.write_proj.weight.normal_(0, 0.05)
flat = gr.norm(x).flatten(start_dim=-2)
s_manual = 2.0 * torch.sigmoid(gr.write_proj(flat))         # (B,T,n)
assert (s_manual >= 0).all() and (s_manual <= 2).all()
torch.testing.assert_close(
    gr.write(x, y), x + s_manual.unsqueeze(-1) * y.unsqueeze(-2),
    rtol=RTOL, atol=ATOL,
)

# Test 4 — GR read phụ thuộc nội dung token, nhưng không trộn positions:
# đổi stream 1 của token cuối bằng phép CỘNG (phép nhân sẽ bị RMSNorm triệt tiêu)
with torch.no_grad():
    gr.gate_down.weight.normal_(0, 0.02)
    gr.gate_up.weight.normal_(0, 0.02)
r1 = gr.read(x)
x2 = x.clone(); x2[:, -1, 1, :] += 2.0
r2 = gr.read(x2)
assert not torch.allclose(r1[:, -1], r2[:, -1])       # token bị đổi phải đổi
torch.testing.assert_close(r1[:, :-1], r2[:, :-1], rtol=RTOL, atol=ATOL)

# Test 5 — retained-state ledger: n lane của GR so với 1 lane của standard
class IdentityBranch(nn.Module):
    def forward(self, x):
        return x
std = PreNormResidual(D, IdentityBranch())
h = torch.randn(B, T, D)
assert std(h).shape == (B, T, D)               # standard: 1 lane
assert gr(x, IdentityBranch()).shape == (B, T, N_STREAMS, D)  # GR: n lane

# Test 6 — CLVR zero-init: route ≡ 0 và block bằng đúng host baseline
block = RecurrentBlockWithCLVR(D, d_value=6)
v, pred = block.memory.write_values(block.norm(h))
no_route = h + block.out_proj(pred)           # forward không có route
torch.testing.assert_close(block(h), no_route, rtol=RTOL, atol=ATOL)
torch.testing.assert_close(
    block.clvr.proj(v), torch.zeros(B, T, D), rtol=RTOL, atol=ATOL,
)

# Test 7 — CLVR nonzero: h' = (h + y) + P v khớp phép tính manual
with torch.no_grad():
    block.clvr.proj.weight.normal_(0, 0.1)
manual = no_route + block.clvr.proj(v)
torch.testing.assert_close(block(h), manual, rtol=RTOL, atol=ATOL)

# Test 8 — delta-memory stub là causal: đổi token tương lai không đổi past
k = block.memory.k_proj(h)
k_shift = k.clone(); k_shift[:, -1] += 3.0
v_seq = block.memory.v_proj(h)
def causal_preds(kk, vv):
    W = kk.new_zeros(kk.shape[0], kk.shape[-1], vv.shape[-1])
    outs = []
    for t in range(kk.shape[1]):
        pred = torch.einsum("bk,bkv->bv", kk[:, t], W)
        r = vv[:, t] - pred
        W = W + torch.einsum("bk,bv->bkv", kk[:, t], r)
        outs.append(pred)
    return torch.stack(outs, dim=1)
p1, p2 = causal_preds(k, v_seq), causal_preds(k_shift, v_seq)
torch.testing.assert_close(p1[:, :-1], p2[:, :-1], rtol=RTOL, atol=ATOL)

print("All eight residual-extension tests passed.")
```

Ghi chú phạm vi: Tests 3–4 chứng minh gate là per-token content-dependent nhưng không trộn positions — trong toy này gate đọc state **của token đó**. Test 6 chứng minh zero-init của `CLVR` ở mức module, không phải thesis về quality. Test 8 chỉ trả về prediction của memory stub; nó không kiểm chứng chunkwise DeltaNet thật. Không test nào thay thế whole-model future-perturbation test khi ghép với token attention thật.

## 10. Benchmark và trade-offs đúng phạm vi

### 10.1 Cost ledger (từ state ledger ở 3.6, chuẩn hóa theo $D$)

| Hạng mục | Standard | `mHC` | `GR` | `Block AttnRes` | `CLVR` |
| --- | --- | --- | --- | --- | --- |
| Residual state per token | $D$ | $nD$ | $nD$ | $ND$ | $D$ (+nothing) |
| Mixing/branching compute | 0 | Sinkhorn + $n{\times}n$ map | rank-$r$ bottleneck | depth scoring mỗi sublayer | một matvec |
| Carried guarantee | identity | $\lVert B\rVert_2\le1$ (linear map) | identity carry, không bound | softmax weights $\ge0$, tổng 1 | zero-init ⇒ baseline |
| Reported systems overhead | — | +6.7% training time ($n{=}4$, fused)[^mhc-concept] | FP8 halves residual bytes (author claim)[^qwen-gr-concept] | <4% train PP, <2% inference; I/O $5.5d$ vs $3d$[^attnres-eval] | không có measurement[^clvr-concept] |

### 10.2 Mini-benchmark local: widened-state traffic

```python
import time

@torch.no_grad()
def bench_gr_vs_standard(device="cpu", n_streams=4, repeats=20):
    d, b, t = 512, 2, 128
    branch = nn.Linear(d, d)
    std_block = PreNormResidual(d, branch).to(device).eval()
    gr_block = GatedResidual(d, n_streams=n_streams, rank=64).to(device).eval()
    h = torch.randn(b, t, d, device=device)
    x = torch.randn(b, t, n_streams, d, device=device)

    def timeit(fn, arg):
        for _ in range(5):
            fn(arg)
        start = time.perf_counter()
        for _ in range(repeats):
            fn(arg)
        return (time.perf_counter() - start) * 1000 / repeats

    return {
        "standard_ms": timeit(std_block, h),
        "gr_ms": timeit(lambda xx: gr_block(xx, branch), x),
    }

print(bench_gr_vs_standard("cpu"))
```

Kết quả toy chỉ cho thấy cùng một branch, đường `GR` tốn thêm read-gate computation và làm việc trên state $n$ lần rộng hơn — nó **không** reproduce FP8 claim hay fused-kernel behavior của Qwen. Ghi device, dtype, PyTorch version, warm-up và dims khi chạy.

### 10.3 Đọc reported numbers đúng điều kiện

Bảng 4.2 và cột "Reported systems overhead" trên là các điểm single-study, author-run, cấu hình-specific. Protocol so sánh công bằng tối thiểu (từ synthesis residual-path): giữ token mixer, MoE, data order, optimizer, depth/width, budget cố định; baseline residual làm control; đo loss **và** task metrics; plot activation/gradient norms và gate entropy; đo peak activation, bytes, prefill, decode, concurrency; lặp seed.[^residual-comparison]

## 11. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
| --- | --- | --- |
| GR read ở init ra mean normed streams thay vì 0.5×mean | kỳ vọng sai về zero-init | xem Section 7.4 note; kiểm `gate_up.weight == 0` |
| Write scalar ngoài $(0,2)$ | thiếu hệ số 2 trước sigmoid | assert `s.min() >= 0 and s.max() <= 2` |
| Lane không phân hóa sau khi train | gate stuck quanh 0.5 hoặc rank quá nhỏ | plot histogram gate theo depth; tăng rank |
| GR memory gấp ~n lần baseline khi tưởng "gần free" | quên accounting widened state | đếm `n × D × T × bytes` của activation |
| Muốn mHC-style stability claim cho GR | nhầm guarantee | đọc lại 4.3: không có `B` ⇒ không có bound |
| CLVR không thay đổi loss | P vẫn ≈ 0 hoặc tín hiệu không hữu ích | kiểm norm của `P v` theo training; thử route `v` vs error như control |
| CLVR loss tệ hơn baseline | basis mismatch kiểu CLER | route vào shared stream chứ không đổi value target của layer nhận |
| Block summaries ăn memory khi long prefill | retained state × tokens | account `T × N × D × bytes`; xem sharding/chunked prefill của AttnRes report |
| Đổi residual xong quality nhảy | ablation đổi nhiều biến | rollback từng biến; giữ mixer/data/optimizer matched |
| AttnRes weights lúc init không đều | pseudo-query không zero-init | kiểm init; weights phải là $1/S$ |

## 12. Giới hạn và bước tiếp theo

Mini-lab chứng minh algebra của read/write gates, zero-init routes, shape invariants, per-token gate dependence, token-axis independence và causality của một delta-memory stub. Nó **không** chứng minh: trainability ở scale, benchmark quality, FP8 residual an toàn, production latency, hay rằng bốn hướng mở rộng kết hợp với nhau là tốt hơn (chưa có controlled evidence cho bất kỳ tổ hợp nào).[^residual-comparison]

Evidence mạnh nhất trong wiki cho từng phần: `GR` có mechanism + code + author-run ablations từ Qwen report (không có deployable kernel hay independent replication); `CLVR` chỉ có single-run matched comparisons trong một paper, chưa có deployment; `mHC` và `AttnRes` được cover sâu ở stage 8.1 và các concept nguồn.[^qwen-gr-concept][^clvr-concept][^mhc-concept][^attnres-eval]

Bước tiếp theo:

1. Chạy toy ở Section 8 với $n=2,4,8$ và plot gate entropy theo depth sau vài bước training trên một task nhỏ.
2. Ghép `CLVR` vào một host toy có nhiều recurrent layer và đo matched loss with/without route, route `v` vs route error (control CLER-style).
3. Đọc [So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path](residual-path-architecture-comparison.md) để có đầy đủ bằng chứng so sánh, kể cả GatedNorm và AltUp.
4. Xem [GLM-5.3-Flash and Qwen3.8-Flash-Next architecture comparison](glm-5-3-flash-and-qwen3-8-flash-next-architecture-comparison.md) để thấy residual topology ngồi cạnh mixer ratio và MoE trong hai checkpoint thật.
5. Tiếp stage 9.6–9.8 của [roadmap](llm-architecture-learning-roadmap.md): đặt residual design vào việc chọn archetype và workload-conditioned architecture.

## Relationships

- **Depends on:** [Depth and residual-path design — khóa học cho người mới](depth-and-residual-path-design-beginners-course.md) — stage 8.1; standard residual, AttnRes và mHC derivation nền tảng.
- **Uses:** [Qwen Gated Residual](qwen-gated-residual.md) — feature-gated multi-stream residual.
- **Uses:** [Cross-layer value routing for delta memories](cross-layer-value-routing-for-delta-memories.md) — zero-init side route từ delta memory.
- **Uses:** [Attention Residuals](attention-residuals.md) và [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) — recap depth retrieval và constrained mixing.
- **Synthesizes:** [So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path](residual-path-architecture-comparison.md) ở dạng dạy được cho người mới.
- **Applied by:** [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md).
- **Elaborates:** Stage 8.5 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Đây là pedagogical synthesis từ maintained wiki concepts, không phải evidence mới. Các con số ablation và systems overhead đều là author-run, single-study, configuration-bound; không có independent replication hay common benchmark giữa GR, mHC, AttnRes và CLVR trong knowledge base. `CLVR` chỉ có bằng chứng single-run trên DeltaNet/Gated DeltaNet hosts, chưa có inference measurement và chưa được test trên KDA/Gated DeltaNet-2. Toy PyTorch code được viết để inspect và verify mechanism với các simplification được ghi rõ (shared RMSNorm, zero-init weights, one-feature delta rule, Python loop); nó không phải source implementation hay serving benchmark.[^qwen-gr-concept][^clvr-concept][^residual-comparison][^attnres-eval][^mhc-concept]

[^residual-comparison]: [So sánh Gated Residual, mHC, AttnRes và họ kiến trúc residual-path](residual-path-architecture-comparison.md), maintained synthesis từ Transformer, Qwen3.8-Next, mHC, AttnRes và Linear Attention Architectures sources; bảng so sánh, GatedNorm/AltUp evidence và protocol so sánh.
[^qwen-gr-concept]: [Qwen Gated Residual](qwen-gated-residual.md), maintained synthesis từ Qwen3.8-Flash-Next card, config, modeling code và technical report; read/write path, rank 320, ablations, path analysis, FP8 và negative result hai-branch.
[^mhc-concept]: [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md), maintained synthesis từ mHC paper và DeepSeek-V4 report; doubly stochastic constraint, Sinkhorn 20 iterations, 27B comparison và 6.7% overhead; concept status `draft`.
[^attnres-concept]: [Attention Residuals](attention-residuals.md), maintained synthesis từ AttnRes/Kimi K3 reports và reference code; Full/Block form, nine sources của Kimi K3, I/O $5.5d$ và prefill state.
[^attnres-eval]: [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md), matched author-run scaling, ablation (436M và component variants), 48B comparison và systems overhead measurements.
[^clvr-concept]: [Cross-layer value routing for delta memories](cross-layer-value-routing-for-delta-memories.md), maintained synthesis từ Linear Attention Architectures paper; CLER→CLVR, zero-init, matched loss table, basis-mismatch interpretation và open tests.
[^qwen38-arch]: [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), checkpoint-level evidence cho GR quanh mỗi mixer và MoE branch, PLE, và training-recipe declaration.
[^depth-course]: [Depth and residual-path design — khóa học cho người mới](depth-and-residual-path-design-beginners-course.md), stage 8.1; derivation chuẩn của standard sum, AttnRes softmax, block summaries và doubly stochastic constraint.
[^kimi-k3-concept]: [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), phân vai KDA, MLA, Block AttnRes và MoE trong architecture thật.
[^deepseek-v4-concept]: [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), reported use of mHC cùng compressed attention, MoE và Muon; concept status `draft`.
