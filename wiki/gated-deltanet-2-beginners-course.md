---
type: Synthesis
title: "Gated DeltaNet-2: tách erase và write trong delta rule — khóa học cho người mới"
description: A top-down beginner course on Gated DeltaNet-2's decoupled channel-wise erase and write gates for fixed-state delta-rule memory, from problem, mechanism, impact, and practical use to derivation, PyTorch, and verification.
tags: [deltanet, gating, associative-memory, linear-attention, hybrid-attention, long-context, learning-roadmap]
status: stable
created: 2026-08-25
generated:
  by: llm-wiki-agent/1
  at: 2026-08-25T00:00:00Z
sources:
  - id: gdn2-2026
    resource: ../raw/2605.22791_GatedDeltaNet-2/main.tex
    title: "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
  - id: kda-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: gdn-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
---

# Gated DeltaNet-2: tách erase và write trong delta rule — khóa học cho người mới

Gated DeltaNet-2 là một recurrent attention layer thuộc nhánh delta-rule: nó giữ `channel-wise decay` của Kimi Delta Attention (KDA) nhưng thay `scalar delta gate` bằng hai gate chuyên biệt — một `erase gate` trên key-axis quyết định đọc và xoá nội dung cũ, một `write gate` trên value-axis quyết định ghi nội dung mới. Nhờ đó model có thể xoá một phần association cũ theo chiều key trong khi chỉ ghi một phần value theo chiều value, thay vì buộc cả hai thao tác dùng chung một số. Khi hai gate bị gắn vào cùng scalar, Gated DeltaNet-2 rút gọn chính xác về KDA; nếu decay cũng bị scalar hoá thì về Gated DeltaNet.[^gdn2-2026]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Giải thích được vấn đề `scalar tie` giữa erase và write trong KDA/Gated DeltaNet và vì sao tách chúng có ý nghĩa.
> 2. Đọc được data flow end-to-end: `decay → đọc theo erase direction → sửa sai số → ghi theo write gate`.
> 3. Phân biệt `erase gate` (key-axis) với `write gate` (value-axis), và phân biệt với `channel-wise decay` (KDA) và `scalar delta gate` (Gated DeltaNet).
> 4. Suy ra recurrence, đọc shape flow, chạy PyTorch toy và kiểm chứng recovery về KDA/Gated DeltaNet kèm tính causal và số chiều state cố định.
> 5. Tách hệ quả trực tiếp của thiết kế khỏi kết quả benchmark do tác giả báo cáo.

## 1. Bức tranh toàn cảnh

### 1.1 Vấn đề: cùng một state, mong muốn "xoá" và "ghi" theo hai chiều khác nhau

Một `fixed-state` delta-rule memory là một ma trận $S_t\in\mathbb{R}^{d_k\times d_v}$ và một vòng lặp cập nhật nó. Điểm mạnh của delta rule là nó **sửa** association mà key đang chọn thay vì cộng thêm mãi: nó đọc nội dung hiện tại rồi chỉ ghi phần sai số.[^parallel-deltanet-2024] Điểm yếu nằm ở chỗ delta rule sửa theo kiểu "một nút gạt" — `Gated DeltaNet` và `KDA` đều dùng **một scalar** $\beta_t$ để đồng thời quyết định:

- **xoá bao nhiêu nội dung cũ** (phía key-side: cô lập nội dung đang được đọc);
- **ghi bao nhiêu nội dung mới** (phía value-side: cô lập số chiều value sẽ được commit).

Hai quyết định này nằm trên **hai trục khác nhau** của state (key-axis và value-axis), nhưng bị ép phải dùng chung một số. Vậy nên nếu model muốn bỏ một phần nội dung cũ nhưng giữ lại phần khác, hoặc ghi một phần value mới nhưng không đụng các phần còn lại, một scalar không đủ khả năng biểu diễn.[^gdn2-2026][^kda-2025]

### 1.2 Ý tưởng cốt lõi trong một câu

**Gated DeltaNet-2 tách hành động "đọc/xoá cái gì" (erase gate trên key-axis) khỏi hành động "ghi cái gì" (write gate trên value-axis), để mỗi lần edit có thể chỉ xoá theo một tập chiều key trong khi chỉ ghi theo một tập chiều value khác.**[^gdn2-2026]

### 1.3 Mental model: hai "cánh tay" độc lập trên cùng một bảng trắng

```text
State = bảng trắng (d_k x d_v), không lớn lên theo số token

KDA / Gated DeltaNet  = MỘT cánh tay cầm đồng thời "cục tẩy" lẫn "bút"
   - xoá bao nhiêu thì ghi đúng bấy nhiêu (cùng một scalar β_t)
   - không thể: tẩy mạnh chỗ này, viết nhẹ chỗ kia

Gated DeltaNet-2 = HAI cánh tay
   - TAY TRÁI (erase gate b_t trên key-axis): xoá nội dung đang đọc
     theo chiều nào, mạnh hay nhẹ
   - TAY PHẢI (write gate w_t trên value-axis): ghi nội dung mới vào
     những chiều value nào, mạnh hay nhẹ
   → hai tay hoạt động độc lập trên hai trục khác nhau của state
```

`Key` chọn vùng cần đụng tới; `value` là nội dung mới; `decay` làm cũ cả state theo từng kênh; còn hai gate nói trên chỉ ra **từng kênh** của phép xoá và phép ghi. Mental model này mô tả cơ chế lưu trữ; trong model thật, key, value, query và các gate đều được học từ hidden state chứ không phải lệnh database tường minh.[^gdn2-2026]

### 1.4 Điều cần biết trước

- [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — vì sao history được nén vào matrix state và bị `interference`.
- [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — delta correction, scalar decay và `channel-wise decay` (KDA).
- [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) — scalar decay và decay-aware chunkwise.
- [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — KDA và pattern lai periodic global attention.
- [Delta memory, KDA, và hybrid KDA–MLA](delta-memory-kda-hybrid-architecture-beginners-project.md) — nền tảng toy course; bài này là **bước tiếp theo** trên cùng nhánh delta-rule.

Bài này không cover kernel CUDA/Triton chi tiết (WY/UT, gate-aware backward), cách broadcast theo `grouped value heads`, hay scaling training recipe. Toy code không có `attention` nên không dùng `RoPE`/`position_ids`; vị trí được mang bởi `channel-wise decay` học được và, trong bản hybrid, bởi khối `SWA` (positional convention không được nêu trong các phần nguồn đã đọc).[^gdn2-2026]

## 2. Cách hoạt động — nhìn từ đầu đến cuối

Ta dùng ví dụ xuyên suốt: một `state` lưu "hồ sơ" của `user_17` dưới dạng vector value `v = [id, plan, ts]`, với key `k = [user_coord, category_coord]`. Sự kiện: `user_17` đổi plan từ `free` sang `pro`.

```text
Token/event 1: user_17 = {plan: free,  id: 17, ts: t0}
Token/event 2: nhiều thông tin không liên quan
Token/event 3: user_17 đổi plan = pro  (id, ts giữ nguyên)
Token/event 4: hỏi plan hiện tại của user_17
```

### 2.1 Data flow của Gated Delta Rule-2 (một token, một head)

```text
hidden state của token hiện tại
        │
        ├──► key k_t        : chọn vùng memory cần đụng tới
        ├──► value v_t      : nội dung mới muốn ghi
        ├──► query q_t      : đọc state để tạo output
        ├──► decay α_t      : mỗi key-channel giữ/quên bao nhiêu
        ├──► erase gate b_t : đọc ở chiều key nào để xoá nội dung cũ
        └──► write gate w_t : ghi vào chiều value nào nội dung mới
                                 │
state cũ S_{t-1} ──► decay theo channel (D_t S_{t-1})
                                 │
                                 ├──► e_t = b_t ⊙ k_t      (erase direction)
                                 ├──► z_t = w_t ⊙ v_t      (write target)
                                 ├──► r_t = (D_t S_{t-1})^T e_t  (đọc cái sẽ xoá)
                                 ├──► S_t = D_t S_{t-1} + k_t (z_t - r_t)^T
                                 │
query ────────────────────────────────► output o_t = S_t^T q_t
```

Vai trò từng thành phần:

| Thành phần | Câu hỏi nó trả lời | Trong ví dụ |
|---|---|---|
| `key` | Đụng vùng nào? | vùng `user_17 / plan` |
| `value` | Nội dung mới là gì? | `plan: pro` |
| `decay α_t` (channel-wise) | Kênh nào nên cũ đi? | kênh `ts` phai nhanh, kênh `id` giữ lâu |
| `erase gate b_t` (key-axis) | Đọc nội dung cũ ở **chiều key** nào để xoá? | chỉ xoá chiều `plan`, giữ chiều `id` |
| `write gate w_t` (value-axis) | Ghi nội dung mới vào **chiều value** nào? | chỉ ghi chiều `plan`, không đụng `id`/`ts` |
| `query` | Đọc gì để đưa sang lớp tiếp theo? | truy xuất `plan` hiện tại |

Điểm mấu chốt: `b_t` nhân vào **key** (trục đọc), `w_t` nhân vào **value** (trục ghi). Vì nằm ở hai trục khác nhau, model có thể tẩy mạnh một phía key trong khi ghi nhẹ một phía value, điều mà một scalar không làm được.[^gdn2-2026]

### 2.2 Ví dụ chạy xuyên suốt

1. **Write đầu tiên:** state chưa biết `user_17`; đọc ra rỗng, nên correction ghi `plan: free`, `id`, `ts`.
2. **Distractors:** các token khác đụng các vùng khác, có thể gây nhiễu nếu learned keys chồng lấn.
3. **Overwrite có chọn lọc:** với `decay` nhẹ và `write gate` chỉ vào chiều `plan`, model ghi `plan: pro`; `erase gate` chỉ xoá phần đọc ở chiều `plan`, nên `id` và `ts` không bị xoá.
4. **Read:** query đọc state đã cập nhật và truyền output sang `residual stream`.

Nếu dùng **một scalar** (KDA), bước 3 sẽ xoá cả `id`/`ts` lẫn `plan` theo cùng mức rồi ghi toàn bộ value mới — chính xác là giới hạn mà Gated DeltaNet-2 muốn gỡ bỏ.[^gdn2-2026][^kda-2025]

### 2.3 Training/prefill và decode

- **Training/prefill:** vòng lặp token tuần tự bị chuyển thành `chunkwise` `WY`/`UT` form để phần lớn công việc trong chunk là matrix multiplication; state chỉ chạy `recurrent` qua biên chunk.[^gdn2-2026]
- **Decode:** token mới trực tiếp cập nhật recurrent state bằng công thức ở trên. Trong bản hybrid, khối `SWA` thêm một window cache có giới hạn.

Chunkwise là cách **tính hiệu quả hơn** cho cùng recurrence, không thay đổi ngữ nghĩa bộ nhớ.[^gdn2-2026]

## 3. Tác động

### 3.1 Hệ quả trực tiếp từ thiết kế

| Mặt | Lợi ích trực tiếp | Chi phí / điều kiện |
|---|---|---|
| `behavior` | hai trục điều khiển độc lập: xoá (key-axis) tách khỏi ghi (value-axis) | thêm hai branch tạo gate và tham số; model phải học được ý nghĩa từng gate |
| `memory` | state vẫn `(d_k, d_v)` cố định, không thêm slot mỗi token | vẫn là fixed-state nên còn `interference`; không phải database vô hạn |
| `compute` (train) | giữ cấu trúc chunkwise `WY`/`UT` như KDA | backward phải "gate-aware" vì không thể tách scalar ra ngoài dot product; throughput H100 giảm nhẹ so với KDA |
| `retrieval` | chỉnh sửa kênh nhỏ hơn nên giảm xung đột giữa các association bị nén | không phục hồi token slots; vẫn cần `SWA`/attention cho local exact retrieval |
| `decode` | state kích thước cố định, không `KV cache` tăng | latency thực còn phụ thuộc kernel, dtype, hardware; hybrid thêm window cache |
| `scaling` | profile throughput gần phẳng theo sequence length | chi phí là hằng số nhỏ so với KDA; phải có fused kernel phù hợp |

### 3.2 Điều kiện để lợi ích xuất hiện

- Task-relevant history nén được, và keys đủ tách để `interference` không chi phối;
- Nhiều chiều cần được xoá/ghi theo **nhịp khác nhau** (nếu chỉ cần "xoá hết rồi ghi hết" thì KDA đã đủ);
- Có `chunkwise`/`fused recurrent` kernel phù hợp;
- Context đủ dài để lợi ích về memory/bandwidth trở nên đáng kể.

Nếu context ngắn, overhead kernel và chi phí gate có thể lấn át lợi ích.

### 3.3 Kết quả benchmark — không phải hệ quả tất yếu

Bản thân việc tách erase/write **không** suy ra số điểm cao hơn; đó là kết quả đo được trong một recipe cụ thể. Paper báo cáo ở 1.3B/100B token (FineWeb-Edu, AdamW, 4K train length, hybrid dùng 2K `SWA`) rằng Gated DeltaNet-2 dẫn đầu nhóm recurrent và hybrid của bảng về common-sense average, retrieval recall và multi-key retrieval — nhưng đây là `author-run point estimates`, không `variance`, không `independent replication`.[^gdn2-2026] Xem chi tiết ở Mục 6–10 bên dưới.

## 4. Sự khác biệt

### 4.1 So với baseline và cơ chế gần nhất

| Cơ chế | Giống nhau | Thay đổi ở data flow | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| `Fixed-state additive` | cùng nén history vào matrix state | ghi toàn value, không đọc lỗi trước khi ghi | đơn giản nhưng repeated writes bị cộng/trộn | history ít xung đột |
| `DeltaNet` | vẫn là fixed-state | đọc association hiện tại rồi ghi correction | sửa association tốt hơn, chưa có quên rộng | cần sửa có chọn lọc, không cần quên |
| `Gated DeltaNet` | giữ delta correction | thêm **scalar decay** cho toàn state | dọn memory rộng nhưng mọi kênh chung một retention | cần quên toàn cục đơn giản |
| `KDA` | giữ fixed-state + delta correction | thay scalar decay bằng **channel-wise decay** | retention linh hoạt hơn; nhưng phép edit vẫn dùng **một scalar** $\beta_t$ | stream dài cần quên chi tiết |
| `Gated DeltaNet-2` | giữ channel-wise decay + delta correction | tách phép edit thành **erase gate (key-axis)** và **write gate (value-axis)** | kiểm soát mịn hơn; thêm gate/tham số, throughput H100 giảm nhẹ so với KDA | cần xoá và ghi theo nhịp khác nhau |

### 4.2 Vị trí thay đổi trong data flow — phần nào giữ nguyên

Chỉ **state update** thay đổi: toàn bộ projection Q/K/V, short convolution + SiLU, L2-normalization trên Q/K, `RMSNorm` output, `SiLU output gate`, output projection và residual/MLP stack vẫn như `Gated DeltaNet`/`KDA`. Bản hybrid chỉ thay **loại token mixer theo depth** (cell `GDN-2 → MLP → SWA → MLP`).[^gdn2-2026]

### 4.3 Các khái niệm dễ nhầm

- **Erase ≠ decay.** `decay` làm cũ cả state theo từng kênh; `erase gate` chỉ đọc nội dung theo một hướng key để xoá phần đó ra khỏi correction.
- **"Recover KDA" không có nghĩa "mạnh hơn KDA".** Đó là **reduction đại số**: khi $b_t=\beta_t\mathbf{1}_{d_k}$ và $w_t=\beta_t\mathbf{1}_{d_v}$ thì recurrence trùng với KDA; đây không phải khẳng định tương đương chất lượng sau khi huấn luyện độc lập.[^gdn2-2026]
- **Hai gate không phải "hai scalar".** Mỗi gate là một vector theo kênh: $b_t\in[0,1]^{d_k}$, $w_t\in[0,1]^{d_v}$.
- **Channel-wise không nghĩa là mỗi token một channel.** Nhiều token vẫn chia sẻ hữu hạn channel.
- **Fixed-state không nghĩa là nhớ vô hạn.** Kích thước không đổi là memory bound, không phải information guarantee.
- **`corrective residual` khác `additive write`.** Delta rule ghi sai số (target − đã đọc), không cộng target nguyên khối.

## 5. Trong thực tế

### 5.1 Cơ chế nằm ở đâu trong model thật?

Gated DeltaNet-2 là `token mixer` trong một decoder block:

```text
hidden states
   │
normalization
   │
GDN-2 hoặc SWA token mixer  ◄── recurrent state / SWA window
   │
residual addition
   │
normalization → MLP → residual addition
   │
next block
```

- **Recurrent-only:** xếp `GDN-2` + MLP lặp lại.
- **Hybrid:** cell lặp là `GDN-2 → MLP → SWA → MLP`. `GDN-2` nén lịch sử dài vào state cố định; `SWA` (window 2K) xử lý local interaction chính xác.[^gdn2-2026]

### 5.2 Khi nào nên dùng, khi nào không?

**Nên cân nhắc khi:**

- context rất dài và `interference` giữa các association bị nén là vấn đề chính;
- cần xoá/ghi theo nhịp khác nhau giữa các kênh;
- có thể train end-to-end và triển khai fused recurrent kernel;
- chấp nhận đo retrieval theo workload thay vì suy từ context-window headline.

**Không nên mặc định khi:**

- workload chủ yếu là exact copy / citation / needle ở vị trí bất kỳ — cần `token-addressable` attention hoặc hybrid nhiều global layer;
- context ngắn và overhead gate/kernel quan trọng hơn cache growth;
- cần chỉnh checkpoint softmax có sẵn mà không retrain;
- runtime không có chunkwise/fused kernel đã kiểm chứng;
- requirement đòi lossless history.

### 5.3 Walkthrough: support assistant đọc ticket dài

1. `GDN-2` state giữ tiến triển: owner, severity, decision gần nhất.
2. `erase gate` `b_t` bảo vệ các kênh ổn định (`id`, `created_at`) khỏi bị xoá khi cập nhật `severity`.
3. `write gate` `w_t` chỉ ghi các chiều value liên quan tới `severity`, không đụng các chiều khác.
4. `channel-wise decay` để `ts` phai nhanh hơn `owner`.
5. Ở decode, state cố định; `SWA` window cache cung cấp local exact interaction.

Workload này chỉ hưởng lợi nếu learned keys/gates mã hoá đúng state transition và `SWA` đủ cho evidence lookup; lý thuyết không chứng minh assistant sẽ cite đúng event.

### 5.4 Measurement cần kiểm tra

- **Quality:** exact copy, overwrite, distractor resistance, multi-key recall, recent-versus-distant recall.
- **Memory:** `state bytes = B·L·H·d_k·d_v·p`; `SWA` window cache; allocator overhead.
- **Latency/throughput:** prefill riêng, decode riêng, batch-one riêng với max throughput.
- **Numerics:** log-decay/state trong `fp32`, recurrent-vs-chunkwise parity, drift theo sequence length.
- **Evidence:** matched model size, data, tokenizer, kernel, hardware nếu muốn gán chênh lệch cho mechanism.

> [!note] Gate kiểm tra trước toán
> Đến đây người đọc có thể trả lời: cơ chế giải quyết `scalar tie` giữa erase và write; nó chạy qua decay → đọc theo erase direction → sửa sai số → ghi theo write gate; giảm interference nhưng thêm gate và throughput cost; khác KDA/Gated DeltaNet ở chỗ tách phép edit thành hai trục; phù hợp khi cần chỉnh sửa bộ nhớ nén theo kênh khác nhau.

## 6. Toán học — zoom in sau cùng

### 6.1 Bảng ký hiệu

| Ký hiệu | Shape ở một head | Ý nghĩa |
|---|---:|---|
| $T$ | scalar | sequence length |
| $d_k$ | scalar | key/query width |
| $d_v$ | scalar | value width |
| $S_t$ | $(d_k,d_v)$ | associative state sau token $t$ |
| $k_t,q_t$ | $(d_k,)$ | key để update và query để read |
| $v_t$ | $(d_v,)$ | target value của write |
| $\alpha_t$ | $(d_k,)$ | channel-wise decay, $\alpha_t\in(0,1]^{d_k}$ |
| $D_t$ | $(d_k,d_k)$ | $\operatorname{Diag}(\alpha_t)$ |
| $b_t$ | $(d_k,)$ | erase gate, $b_t\in[0,1]^{d_k}$ |
| $w_t$ | $(d_v,)$ | write gate, $w_t\in[0,1]^{d_v}$ |
| $e_t$ | $(d_k,)$ | erase direction, $e_t=b_t\odot k_t$ |
| $z_t$ | $(d_v,)$ | gated write target, $z_t=w_t\odot v_t$ |
| $C$ | scalar | chunk size |

### 6.2 Trường hợp nhỏ nhất: additive write thất bại khi overwrite

**Trực giác.** Cùng một key nhận value cũ rồi value mới: additive memory giữ tổng hai giá trị, không biết write thứ hai nghĩa là overwrite.

**Công thức.**

$$
S_t=S_{t-1}+k_tv_t^\top,\qquad o_t=S_t^\top q_t.
$$

**Ý nghĩa ký hiệu.** $k_t$ chọn direction ghi; $v_t$ là nội dung; outer product tạo matrix write; query đọc state.

**Shape flow.**

$$
(d_k,1)(1,d_v)=(d_k,d_v),\qquad (1,d_k)(d_k,d_v)=(1,d_v).
$$

**Ví dụ số.** Với $k=[1,0]^\top$, $v_{old}=[1,0]^\top$ rồi $v_{new}=[0,1]^\top$:

$$
S=kv_{old}^\top+kv_{new}^\top=\begin{bmatrix}1&1\\0&0\end{bmatrix},\qquad k^\top S=[1,1].
$$

**Kết luận.** Output là tổng, không phải value mới. Delta rule sửa lỗi này bằng cách đọc trước rồi ghi sai số.[^parallel-deltanet-2024][^kda-2025]

### 6.3 Delta rule và scalar tie

**Trực giác.** DeltaNet đọc nội dung đang lưu tại key rồi ghi phần sai số; Gated DeltaNet thêm một scalar decay;[^gdn-2025] KDA cho decay theo từng key-channel. Điểm chung: phép edit vẫn do **một scalar** $\beta_t$ điều khiển.

**Công thức KDA (baseline).**

$$
S_t=(I-\beta_tk_tk_t^\top)D_tS_{t-1}+\beta_tk_tv_t^\top,\qquad \beta_t\in[0,1].
$$

**Ý nghĩa ký hiệu.** $D_t=\operatorname{Diag}(\alpha_t)$ làm cũ state theo kênh; rank-one matrix $k_tk_t^\top$ chọn direction sửa; $\beta_t$ quyết định vừa xoá (hệ số của $I-\beta kk^\top$) vừa ghi (hệ số của value) theo **cùng một mức**.[^kda-2025]

**Ví dụ số.** Xem Mục 6.4 dưới, so với phiên bản tách gate.

### 6.4 Gated Delta Rule-2: tách erase và write

**Trực giác.** Giữ channel-wise decay như KDA, nhưng phép edit không còn do một số: `erase gate` chỉ ra **chiều key** dùng để đọc/xoá nội dung cũ, `write gate` chỉ ra **chiều value** dùng để ghi nội dung mới.

**Công thức.**

$$
e_t=b_t\odot k_t,\qquad z_t=w_t\odot v_t,
$$

$$
\bar S_t=D_tS_{t-1},\qquad r_t=\bar S_t^\top e_t,
$$

$$
\boxed{
S_t=(I-k_te_t^\top)D_tS_{t-1}+k_tz_t^\top
}
=
\bar S_t+k_t(z_t-r_t)^\top.
$$

**Ý nghĩa từng ký hiệu.** $e_t=b_t\odot k_t$ là **erase direction**: mỗi kênh key được nhân với $b_t$, nên chỉ những kênh key có $b_t$ lớn mới được đọc/xoá. $z_t=w_t\odot v_t$ là **gated write target**: chỉ những chiều value có $w_t$ lớn mới được commit. $D_t$ làm cũ state trước. Vế trái của rank-one factor giữ nguyên $k_t$ (giữ hướng ghi của delta rule); vế phải trở thành $b_t\odot k_t$ (hướng đọc có chọn lọc theo kênh).[^gdn2-2026]

**Shape flow.**

| Mảnh | Shape |
|---|---:|
| $e_t=b_t\odot k_t$ | $(d_k,)$ |
| $z_t=w_t\odot v_t$ | $(d_v,)$ |
| $D_tS_{t-1}$ | $(d_k,d_v)$ |
| $r_t=(D_tS_{t-1})^\top e_t$ | $(1,d_k)(d_k,d_v)\to(d_v,)$ |
| $k_tz_t^\top$ | $(d_k,1)(1,d_v)\to(d_k,d_v)$ |
| $S_t$ | $(d_k,d_v)$, không có trục $T$ |

**Ví dụ số — vì sao tách gate quan trọng.** Cho $d_k=d_v=2$, key $k=[1,0]^\top$, state đã lưu $v_{old}=[1,0]^\top$ với full write (không decay), nên:

$$
D_t=I,\qquad S=\begin{bmatrix}1&0\\0&0\end{bmatrix}.
$$

Token mới $v_{new}=[0,1]^\top$ tại cùng key.

- **KDA, $\beta_t=1$:** $e=k=[1,0]$, $z=v_{new}=[0,1]$; $r=S^\top e=[1,0]$; $S\leftarrow S+k(z-r)^\top=[[0,1],[0,0]]$; đọc tại $k$ ra $[0,1]=v_{new}$. → **overwrite đầy đủ.**
- **Gated DeltaNet-2, tách gate:** chọn $b=[0,1]$ (chặn đọc chiều key 0) và $w=[1,1]$ (ghi cả hai chiều value). Khi đó $e=b\odot k=[0,0]$ nên $r=[0,0]$; $S\leftarrow S+k(z-0)^\top=[[1,1],[0,0]]$; đọc tại $k$ ra $[1,1]=v_{old}+v_{new}$. → **nội dung cũ KHÔNG bị xoá, nội dung mới được CỘNG.**

Như vậy chính `erase gate` (key-axis) quyết định nội dung cũ có bị xoá hay không, tách khỏi `write gate` (value-axis) quyết định nội dung mới có được ghi hay không — điều một scalar không biểu diễn nổi.[^gdn2-2026]

**Kết luận.** Tách hai trục giúp model chọn lọc hơn: vẫn là fixed-state, vẫn có `interference`, nhưng thao tác edit trở nên "có địa chỉ" hơn theo từng kênh.

### 6.5 Recovery về KDA và Gated DeltaNet (reduction đại số)

**Trực giác.** Gated DeltaNet-2 chứa các biến thể cũ trong "không gian con bị gắn scalar".

**Công thức.**

$$
b_t=\beta_t\mathbf{1}_{d_k},\;w_t=\beta_t\mathbf{1}_{d_v}\ \Longrightarrow\ S_t=(I-\beta_tk_tk_t^\top)D_tS_{t-1}+\beta_tk_tv_t^\top=\text{KDA}.
$$

Thêm $\alpha_t=\alpha_t^{scalar}\mathbf{1}_{d_k}$:

$$
S_t=\alpha_t^{scalar}(I-\beta_tk_tk_t^\top)S_{t-1}+\beta_tk_tv_t^\top=\text{Gated DeltaNet}.
$$

**Ý nghĩa ký hiệu.** $\mathbf{1}_{d}$ là vector toàn một. Khi mọi kênh của $b_t,w_t$ bằng cùng $\beta_t$, hai gate "sụp" về một scalar.

**Kết luận.** Đây là reduction đại số của recurrence, **không phải** claim rằng một model Gated DeltaNet-2 đã train tương đương với KDA sau khi gắn gate.[^gdn2-2026]

### 6.6 Fast-weight view (trực giác, có thể bỏ qua proof)

**Trực giác.** Mỗi bước, state di chuyển về tối ưu của một bài toán online: giữ `state` gần bản đã decay, đồng thời sửa theo residual giữa target đã ghi và nội dung đã đọc.

**Công thức.**

$$
S_t=\arg\min_S\Bigl[\|S-\bar S_t\|_F^2-2\langle S^\top k_t,\,z_t-\bar S_t^\top e_t\rangle\Bigr].
$$

**Kết luận.** Đây là cách hiểu "fast-weight" của update; nó khớp chính xác với công thức ở Mục 6.4.[^gdn2-2026]

### 6.7 Chunkwise training (có thể bỏ qua để hiểu ý chính)

Trong một chunk, `channel-wise decay` được hút vào hai factor của mỗi rank-one erase. Gọi $\gamma_r=\exp(\sum_{i\le r}g_i)$ là tích luỹ decay, và

$$
\bar k_r=\gamma_r^{-1}\odot k_r,\qquad \bar e_r=\gamma_r\odot e_r .
$$

Toàn bộ tương tác trong chunk là matrix product và triangular solve:

$$
T=\operatorname{tril}(\bar E\bar K^\top,-1),\qquad A=(I+T)^{-1},\qquad Y=A\bar E,\qquad U=A Z,
$$

với $Z=W\odot V$. Output và state cuối chunk dùng lại `A`, `Y`, `U`:

$$
S_{[n+1]}=\operatorname{Diag}(\gamma_C)S_{[n]}+K_{\mathrm{tail}}^\top(U-YS_{[n]}),
$$

$$
O_{[n]}=Q_\gamma S_{[n]}+A_{qk}(U-YS_{[n]}).
$$

Cùng hình dạng với KDA; khác biệt duy nhất là việc `erase gate` đi vào `\bar E` còn `write gate` đi vào `Z`.[^gdn2-2026]

### 6.8 Loại trừ scalar shortcut ở backward (nâng cao)

Với delta rule dùng scalar, một factor $\beta_r$ có thể đưa ra ngoài dot product khi tích luỹ gradient của `A`. Với Gated Delta Rule-2 điều đó không còn đúng: vế ghi có một diagonal gate khác trên value, vế xoá có một diagonal gate khác trên key, nên gate phải nằm ngay tại chỗ tích luỹ:

$$
\mathrm{d}A \mathrel{+}= \mathrm{d}U\,Z^\top,\quad Z=W\odot V;\qquad \mathrm{d}A \mathrel{+}= \mathrm{d}Y\,\bar E^\top,\quad \bar E=\gamma\odot(B\odot K).
$$

Đây là thay đổi toán học chính khi huấn luyện Gated Delta Rule-2; các kernel backward còn lại tái dùng cấu trúc KDA.[^gdn2-2026]

## 7. Implementation (PyTorch tối thiểu)

Code dưới cụ thể hoá đúng flow Mục 2 và recurrence Mục 6.4: `decay → đọc theo erase direction → sửa sai số → ghi theo write gate`. Dùng FP64 và Python loop để inspect algebra; **không** phải block Gated DeltaNet-2 production hay serving kernel. Trong toy không có `attention`, nên không có `RoPE`/`position_ids`; `position` trong Gated DeltaNet-2 được mang bằng `channel-wise decay` học được (bản hybrid thêm `SWA`).

```python
from dataclasses import dataclass
import torch

DTYPE = torch.float64
ATOL = 1e-10
RTOL = 0.0


def one_hot(i: int, n: int) -> torch.Tensor:
    return torch.nn.functional.one_hot(torch.tensor(i), num_classes=n).to(DTYPE)


@dataclass
class GatedDeltaRule2:
    # Single-head teaching state; no batch/head/sequence axis.
    d_key: int
    d_value: int

    def __post_init__(self):
        self.state = torch.zeros(self.d_key, self.d_value, dtype=DTYPE)

    def _check(self, v, n, name):
        if v.shape != (n,):
            raise ValueError(f"{name} must have shape ({n},)")
        if v.dtype != DTYPE:
            raise ValueError(f"{name} must be {DTYPE}")

    def step(self, key, value, alpha, b, w):
        """One token: channel-wise decay, gated erase-read, gated write."""
        self._check(key, self.d_key, "key")
        self._check(alpha, self.d_key, "alpha")
        self._check(b, self.d_key, "erase gate b")
        self._check(value, self.d_value, "value")
        self._check(w, self.d_value, "write gate w")

        # Mechanism step 1: channel-wise decay of the state.
        decayed = alpha[:, None] * self.state                     # (d_k, d_v)
        # Mechanism step 2: erase direction = b ⊙ k  (key-axis).
        e = b * key                                               # (d_k,)
        # Mechanism step 3: read the content that will be erased.
        r = decayed.T @ e                                         # (d_v,)
        # Mechanism step 4: gated write target = w ⊙ v  (value-axis).
        z = w * value                                             # (d_v,)
        # Mechanism step 5: correct toward the residual.
        self.state = decayed + torch.outer(key, z - r)            # (d_k, d_v)

    def read(self, query):
        self._check(query, self.d_key, "query")
        return query @ self.state                                 # (d_v,)

    @property
    def state_elements(self) -> int:
        return self.state.numel()


# Reference reductions for the algebra checks below.
def kda_step(mem, key, value, alpha, beta):
    b = torch.full((mem.d_key,), beta, dtype=DTYPE)
    w = torch.full((mem.d_value,), beta, dtype=DTYPE)
    mem.step(key, value, alpha, b, w)


def gdn_step(mem, key, value, alpha_scalar, beta):
    alpha = torch.full((mem.d_key,), alpha_scalar, dtype=DTYPE)
    kda_step(mem, key, value, alpha, beta)
```

Ghi chú khác biệt với production:

- Layer thật có `Q/K/V` projection, short convolution + SiLU và L2-normalization trên Q/K; `RMSNorm`, `SiLU output gate` và output projection.[^gdn2-2026]
- Gate được tạo bằng projection riêng: $b_t=\sigma(W_bx_t)$, $w_t=\sigma(W_wx_t)$; log-decay $\boldsymbol g_t=-\exp(a)\odot\operatorname{softplus}(W_fx_t+\delta)$, $\alpha_t=\exp(g_t)$, tính ở `fp32`.[^gdn2-2026]
- Với `grouped value heads`: $\{q,k,\boldsymbol g,b\}$ lặp theo group, còn $\{v,w\}$ nằm trên trục `value-head`.
- `torch.cat` không dùng trong toy này; nếu thêm vùng nhớ `SWA` toy, `torch.cat` chỉ là teaching, không đại diện paged serving.

## 8. Xác minh trước khi benchmark

```python
@torch.inference_mode()
def test_reduces_to_kda():
    # Because b = beta*1_dk and w = beta*1_dv, Gated Delta Rule-2 == KDA.
    mem = GatedDeltaRule2(2, 2)
    key = one_hot(0, 2)
    value = torch.tensor([0.3, 0.8], dtype=DTYPE)
    alpha = torch.tensor([0.9, 0.5], dtype=DTYPE)
    mem.step(key, value, alpha, b=0.6 * torch.ones(2, dtype=DTYPE),
             w=0.6 * torch.ones(2, dtype=DTYPE))

    ref = GatedDeltaRule2(2, 2)
    kda_step(ref, key, value, alpha, beta=0.6)

    torch.testing.assert_close(mem.state, ref.state, rtol=RTOL, atol=ATOL)


@torch.inference_mode()
def test_reduces_to_gated_deltanet():
    # Tying decay to a scalar as well recovers Gated DeltaNet exactly.
    mem = GatedDeltaRule2(2, 2)
    key = one_hot(0, 2)
    value = torch.tensor([0.3, 0.8], dtype=DTYPE)
    mem.step(key, value, alpha=0.9 * torch.ones(2, dtype=DTYPE),
             b=0.6 * torch.ones(2, dtype=DTYPE),
             w=0.6 * torch.ones(2, dtype=DTYPE))

    ref = GatedDeltaRule2(2, 2)
    gdn_step(ref, key, value, alpha_scalar=0.9, beta=0.6)

    torch.testing.assert_close(mem.state, ref.state, rtol=RTOL, atol=ATOL)


@torch.inference_mode()
def test_erase_gate_controls_removal_independently():
    # b = [0,1] blocks reading along key coordinate 0, so the old value is
    # NOT removed while the new value IS added -> read = old + new.
    mem = GatedDeltaRule2(2, 2)
    key = one_hot(0, 2)
    old = one_hot(0, 2)
    new = one_hot(1, 2)
    mem.step(key, old, alpha=torch.ones(2, dtype=DTYPE),
             b=torch.ones(2, dtype=DTYPE), w=torch.ones(2, dtype=DTYPE))
    mem.step(key, new, alpha=torch.ones(2, dtype=DTYPE),
             b=torch.tensor([0.0, 1.0], dtype=DTYPE),   # block erase on coord 0
             w=torch.ones(2, dtype=DTYPE))               # write both value coords
    torch.testing.assert_close(mem.read(key), old + new, rtol=RTOL, atol=ATOL)

    # KDA with b=w=1*beta and beta=1 overwrites fully instead.
    ref = GatedDeltaRule2(2, 2)
    kda_step(ref, key, old, torch.ones(2, dtype=DTYPE), beta=1.0)
    kda_step(ref, key, new, torch.ones(2, dtype=DTYPE), beta=1.0)
    torch.testing.assert_close(ref.read(key), new, rtol=RTOL, atol=ATOL)


@torch.inference_mode()
def test_write_gate_limits_committed_value_channels():
    # w = [1,0] commits only value coordinate 0.
    mem = GatedDeltaRule2(2, 2)
    key = one_hot(0, 2)
    value = torch.tensor([1.0, 5.0], dtype=DTYPE)
    mem.step(key, value, alpha=torch.ones(2, dtype=DTYPE),
             b=torch.ones(2, dtype=DTYPE),
             w=torch.tensor([1.0, 0.0], dtype=DTYPE))
    torch.testing.assert_close(
        mem.read(key), torch.tensor([1.0, 0.0], dtype=DTYPE), rtol=RTOL, atol=ATOL
    )


@torch.inference_mode()
def test_state_shape_is_fixed():
    torch.manual_seed(0)
    mem = GatedDeltaRule2(8, 4)
    for _ in range(100):
        key = torch.randn(8, dtype=DTYPE)
        key = key / key.norm()
        value = torch.randn(4, dtype=DTYPE)
        alpha = torch.rand(8, dtype=DTYPE) + 0.01
        b = torch.rand(8, dtype=DTYPE)
        w = torch.rand(4, dtype=DTYPE)
        mem.step(key, value, alpha, b, w)
        assert mem.state.shape == torch.Size([8, 4])
    torch.testing.assert_close(
        torch.tensor(mem.state_elements),
        torch.tensor(32), rtol=RTOL, atol=ATOL
    )


@torch.inference_mode()
def test_causal_prefix_invariance():
    torch.manual_seed(1)
    T, d = 6, 4
    keys = torch.randn(T, d, dtype=DTYPE)
    keys = keys / keys.norm(dim=-1, keepdim=True)
    values = torch.randn(T, d, dtype=DTYPE)
    alphas = torch.full((T, d), 0.99, dtype=DTYPE)
    bs = torch.rand(T, d, dtype=DTYPE)
    ws = torch.rand(T, d, dtype=DTYPE)

    def run(extra_values):
        mem = GatedDeltaRule2(d, d)
        outs = []
        for t in range(T):
            mem.step(keys[t], extra_values[t] if extra_values is not None else values[t],
                     alphas[t], bs[t], ws[t])
            outs.append(mem.read(keys[t]))
        return torch.stack(outs)

    full = run(None)
    changed = values.clone()
    changed[4:] += 100.0
    perturbed = run(changed)
    torch.testing.assert_close(full[:4], perturbed[:4], rtol=RTOL, atol=ATOL)


for test in (
    test_reduces_to_kda,
    test_reduces_to_gated_deltanet,
    test_erase_gate_controls_removal_independently,
    test_write_gate_limits_committed_value_channels,
    test_state_shape_is_fixed,
    test_causal_prefix_invariance,
):
    test()
    print("passed:", test.__name__)
```

Các test dùng FP64 để kiểm chứng algebra với tolerance chặt. Khi chuyển sang FP32/BF16 hoặc chunkwise kernel, phải đặt `rtol/atol` theo dtype và đo error accumulation thay vì copy nguyên ngưỡng này.

### Verification matrix

| Test | Claim được kiểm chứng | Không chứng minh |
|---|---|---|
| reduces to KDA | $b=w=\beta\mathbf{1}$ khớp KDA | model đã train độc lập tương đương KDA |
| reduces to Gated DeltaNet | thêm $\alpha$ scalar khớp Gated DeltaNet | mọi mô hình GDN-2 đều rút gọn sau training |
| erase controls removal | $b$ chặn đọc → nội dung cũ không bị xoá | learned erase gate luôn hành xử đúng |
| write limits commit | $w$ giới hạn chiều value được ghi | learned write gate luôn chọn đúng kênh |
| fixed shape | số phần tử state không đổi theo writes | total runtime memory không tăng |
| causal prefix | future values không đổi prefix outputs trong loop | chunkwise production kernel causal & numerically equivalent |

## 9. Benchmark / Trade-offs

Đây là kết quả do tác giả báo cáo trong **một** recipe (1.3B, 100B FineWeb-Edu, AdamW `lr=4e-4`, 4K train length, hybrid dùng 2K `SWA`). Chúng là `point estimates`, không có `variance` và chưa được lặp độc lập trong repository.[^gdn2-2026]

### 9.1 Language modeling & common-sense (recurrent / hybrid)

| Model | Wiki. ppl | LAMBADA ppl | Common-sense avg |
|---|---:|---:|---:|
| Mamba-2 | 16.79 / 17.46 | 12.38 / 11.29 | 51.82 / 51.99 |
| Gated DeltaNet | 16.40 / 16.00 | 11.89 / 10.82 | 52.07 / 52.25 |
| KDA | 16.81 / 16.01 | 11.68 / 10.66 | 52.28 / 52.68 |
| Mamba-3 (MIMO) | 16.45 / 15.81 | 11.66 / 10.92 | 52.39 / 52.72 |
| **Gated DeltaNet-2** | **15.90** / 15.62 | **11.41** / **10.43** | **53.11** / **53.97** |

Bảng thể hiện thứ hạng nội tại trong recipe này, **không** so được chéo với study Mamba-3 (corpus/tokenizer/scale/context khác nhau).

### 9.2 Retrieval (recurrent / hybrid)

- **Real-world recall avg** (2K trunc): Gated DeltaNet-2 **29.88** / **42.28** (KDA 28.67 / 40.14; Mamba-3 MIMO 28.35 / 40.11).
- **Multi-key RULER NIAH** (MK-NIAH-1, 1K/2K/4K): recurrent **72.6 / 51.4 / 37.8**; hybrid **93.0 / 84.6 / 48.0** — cao nhất trong bảng.

### 9.3 Ablation: gate channel structure (recurrent)

| Biến thể | Common avg | MK-NIAH-1@4K | Recall avg |
|---|---:|---:|---:|
| full Gated DeltaNet-2 | **53.11** | **37.8** | **29.88** |
| b-only channel (scalar write) | 52.79 | 35.2 | 29.51 |
| w-only channel (scalar erase) | 52.45 | 30.6 | 28.92 |
| expanded erase $b\in[0,2]$ | 53.04 | 37.6 | 29.81 |

Erase gate (`b`) chiếm phần lớn lợi ích; mở rộng range erase lên `[0,2]` không cho gain nhất quán ở scale này.[^gdn2-2026]

### 9.4 Throughput (H100, hybrid training)

| Model | 2K×8 → 16K×1 (Kt/s) | Profile |
|---|---|---:|
| Transformer | 45.83 → 29.36 | giảm mạnh theo độ dài |
| KDA | 39.81 → 38.50 | gần phẳng |
| **Gated DeltaNet-2** | **38.00 → 36.11** | gần phẳng, **thấp hơn KDA một hằng số nhỏ** |
| Mamba-3 MIMO | 34.44 → 26.86 | giảm theo độ dài |

Đây là `training throughput` trên một kernel fused; **không** kết luận `decode latency`, `serving throughput` hay khả năng chuyển sang accelerator khác.[^gdn2-2026]

### 9.5 Phạm vi không suy ra

- **Không** có baseline thắng tuyệt đối: thứ hạng phụ thuộc model scale, tokenizer, context, kernel, optimizer, hybrid stack.
- **Hybrid gain không chỉ do recurrence**: `SWA` phục hồi local token-addressable interaction (khoảng cách NQ/DROP còn lại nói lên điều này).[^gdn2-2026]

## 10. Debug checklist

| Triệu chứng | Nguyên nhân khả dĩ | Check đầu tiên |
|---|---|---|
| không khớp KDA khi gắn gate | `b`/`w` chưa bằng `β·1`, hoặc thứ tự decay/đọc sai | in `b`, `w`, `alpha` và so state |
| overwrite ra tổng (không phải value mới) | erase direction bị chặn (`b=0`) hoặc key chưa normalize | in `e_t` và norm(key) |
| nội dung cũ không bị xoá | `b_t` quá nhỏ ở các kênh cần xoá | histogram `b` theo channel |
| value mới không vào state | `w_t` quá nhỏ ở chiều value cần ghi | histogram `w` theo channel |
| state có axis sequence | đang lưu mọi intermediate state hoặc token writes | state chỉ có `(d_k, d_v)` |
| future token đổi prefix output | implementation không causal | prefix-invariance test trước benchmark |
| recurrent và chunkwise lệch | mask, cumulative decay hoặc numerical order sai | FP64 reference trên sequence ngắn |
| throughput không cải thiện | kernel overhead hoặc gate branches | profile training prefill/decode riêng |
| benchmark ratio quá đẹp | trộn batch-one latency với max throughput | ghi rõ concurrency và objective |
| gọi toy là block đầy đủ | thiếu projection, conv, gate branches, output gate | đối chiếu production block components |

## 11. Giới hạn & bước tiếp theo

Course này chứng minh một số tính chất đại số của toy recurrence và trình bày lại kết quả do tác giả báo cáo; nó **không** chứng minh:

- quality parity giữa Gated DeltaNet-2, KDA và softmax attention;
- context một triệu token ≡ reliable retrieval ở mọi vị trí;
- 1.3B/100B là scale tối ưu hay phổ quát;
- Python loop phản ánh chunkwise/fused kernel speed;
- learned erase/write gate luôn học semantic editing đúng;
- fixed-state chứa vô hạn information.

Học tiếp:

1. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — recurrence và lineage tổng thể.
2. [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) — scalar-decay precursor.
3. [Gated DeltaNet-2 decoupled delta rule and training](gated-deltanet-2-decoupled-delta-rule-and-training.md) — mechanism và chunkwise chi tiết.
4. [Gated DeltaNet-2 evaluation and hybrid trade-offs](gated-deltanet-2-evaluation-and-hybrid-trade-offs.md) — evaluation và giới hạn evidence.
5. [Mamba-2/3, KDA, Gated DeltaNet, và Gated DeltaNet-2 comparison](mamba-kda-gated-deltanet-comparison.md) — cơ chế-và-bằng-chứng so sánh.

## Relationships

- **Depends on:** [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — nền tảng state layout và interference.
- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — targeted correction và channel-wise decay (KDA).
- **Extends:** [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md) — thêm gating mịn hơn scalar decay.
- **Extends:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — tách scalar active edit thành hai gate.
- **Evaluated by:** [Gated DeltaNet-2 evaluation and hybrid trade-offs](gated-deltanet-2-evaluation-and-hybrid-trade-offs.md).
- **Contrasts with:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) và [Mamba-3 architecture and state-space methods](mamba-3-architecture-and-state-space-methods.md) — nhánh SSM, không có rank-one correction.
- **Contrasts with:** [Mamba-2/3, KDA, Gated DeltaNet, và Gated DeltaNet-2 comparison](mamba-kda-gated-deltanet-comparison.md) — comparison tổng hợp cho branch split.
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng course tách erase/write (bước sau `Delta memory, KDA, và hybrid KDA–MLA`).

## Evidence limits

Recurrence, recovery reductions, chunkwise `WY`/`UT`, gate-aware backward, block design và mọi con số (language modeling, common-sense, retrieval, recall, ablation, throughput) đều là `author-run` claim từ primary source; đây là tóm tắt có chủ đích về cơ chế chứ không phải kết quả được độc lập tái lập trong repository. Kết quả bị giới hạn bởi recipe cụ thể (1.3B/100B FineWeb-Edu, 4K train length, 2K `SWA`, H100, fused kernel) và không có `variance`/`independent replication`. Mental model, ví dụ `user_17`, walkthrough support-ticket và code organization là `pedagogical synthesis`: chúng làm rõ representation trade-off nhưng không dự đoán trực tiếp perplexity, long-context benchmark score hay production latency. Không có credentials, tokens hay PII trong nội dung, code và footnote.

[^gdn2-2026]: Ali Hatamizadeh, Yejin Choi, and Jan Kautz, “Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention,” supplied LaTeX source, [source](../raw/2605.22791_GatedDeltaNet-2/main.tex), Sections 2–4, Tables 1–4, Figure 2, and appendices.
[^kda-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 2–3 and 6.
[^gdn-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5 and Appendix A.
[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–5 and derivation appendices.
