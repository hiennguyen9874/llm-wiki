---
type: Synthesis
title: "MLA và token-addressable memory — bài học cho người mới"
description: A top-down beginner course on how MLA compresses each token's KV representation while preserving token-addressable softmax retrieval, context-linear cache growth, and practical deployment trade-offs.
tags: [mla, attention, kv-cache, token-addressable-memory, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-24T05:13:22Z
sources:
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# MLA và token-addressable memory — bài học cho người mới

`Multi-head Latent Attention` (MLA) giải quyết áp lực `KV cache` bằng cách nén representation lưu cho **từng token**, thay vì bỏ khả năng truy cập từng token. Ý tưởng cốt lõi trong một câu: **giữ một `joint KV latent` nhỏ cho mỗi token, rồi dùng nó để thực hiện `softmax attention` trên toàn bộ history**. Vì vậy MLA làm “mỗi ngăn nhớ mỏng hơn”, nhưng số ngăn vẫn tăng theo `context length`; đây là khác biệt nền tảng với `fixed-state memory`, nơi nhiều token cùng được gộp vào một state có kích thước cố định.[^deepseek-v2-2024][^fast-weight-programmers-2021]

> [!success] Sau bài này
> 1. Bạn có thể giải thích vấn đề MLA giải quyết, data flow từ input đến output, và vì sao MLA vẫn `token-addressable` mà không cần công thức.
> 2. Bạn có thể phân biệt `MHA`, `GQA/MQA`, `MLA`, và `fixed-state memory` theo cache representation, state growth, retrieval và workload.
> 3. Bạn có thể tính cache bytes, theo dõi tensor shapes, implement một MLA-like content path tối thiểu và kiểm chứng `cached decode == full forward`.

## 1. Bức tranh toàn cảnh

### 1.1 Vấn đề: history hữu ích nhưng đắt để giữ

Trong autoregressive generation, mỗi `decode step` cần dùng token mới để tra cứu các token trước. Standard `Multi-head Attention` (MHA) giữ `key` và `value` của từng token, tại từng layer, cho nhiều heads. Cách này cho phép query chọn trực tiếp token liên quan, nhưng cache lớn dần khi prompt, output hoặc concurrency tăng.[^deepseek-v2-2024]

MLA không thay câu hỏi “token cũ nào liên quan?”. Nó thay **cách biểu diễn mỗi token trong cache**:

```text
MHA: token 1 [K heads | V heads]   token 2 [K heads | V heads]   ...
MLA: token 1 [latent | position]   token 2 [latent | position]   ...
                  nhỏ hơn                         nhỏ hơn
```

### 1.2 Mental model: tủ hồ sơ

Hãy tưởng tượng context là một tủ hồ sơ:

- `MHA`: mỗi token có một ngăn riêng, trong ngăn có bộ K/V đầy đủ cho nhiều heads.
- `GQA/MQA`: vẫn một ngăn mỗi token, nhưng nhiều query heads dùng chung một số bộ K/V.
- `MLA`: vẫn một ngăn mỗi token, nhưng ngăn chỉ giữ một `joint latent` nhỏ và phần position nhỏ.
- `Fixed-state memory`: bỏ các ngăn riêng; mọi hồ sơ được ghi chồng lên một bảng trắng cố định.

Mental model này cho hai câu hỏi tách biệt:

1. **Mỗi token tốn bao nhiêu state?** MLA giảm đại lượng này.
2. **Tổng state có tiếp tục tăng khi có thêm token không?** Với MLA, có.

> [!warning] Điều dễ hiểu sai nhất
> “Compressed KV cache” không đồng nghĩa với “fixed-size memory”. MLA nén **theo token**; nó không nén toàn bộ context thành một latent duy nhất.[^deepseek-v2-2024]

### 1.3 Điều cần biết trước

Bạn chỉ cần biết trực giác `Q/K/V`, `causal attention`, `prefill` và `decode`. Nếu chưa quen, đọc [Attention: beginner's guide](attention-beginner-guide.md), [KV caching](kv-caching.md), và [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md).

Bài này không cover `MoE routing`, training objective, `PagedAttention`, hay production kernels. Toy code dùng `torch.cat` để nhìn rõ cache growth; serving thật thường pre-allocate hoặc quản lý cache theo blocks.

## 2. Cách hoạt động — nhìn từ đầu đến cuối

Ta dùng một ví dụ xuyên suốt: prompt **“Hà Nội là thủ đô của”**, và model chuẩn bị sinh token tiếp theo. Giả sử tokenizer tạo năm token cũ; token mới cần tìm thông tin liên quan trong năm token đó.

### 2.1 Data flow trực giác

```text
hidden state của từng token cũ
        │
        ├─► down-projection ─► joint KV latent nhỏ ─────────┐
        └─► position path  ─► rotary key nhỏ ───────────────┤
                                                             ▼
                                              cache một entry / token

hidden state của token đang query
        │
        ├─► content query ──────────────────────────────────┐
        └─► rotary query ───────────────────────────────────┤
                                                             ▼
                      score riêng cho token 1, 2, 3, 4, 5
                                                             │
                                                       softmax weights
                                                             │
                                           weighted retrieval ─► output
```

Cơ chế đi qua sáu bước:

1. **Compress:** mỗi hidden state cũ đi qua `down-projection` để tạo một `joint KV latent`.
2. **Attach position:** một đường riêng tạo `rotary key` nhỏ để giữ positional information.
3. **Cache:** lưu cặp `latent + rotary key`; không lưu K/V content đã expand.
4. **Prepare query:** token mới tạo content query và rotary query.
5. **Address tokens:** query tạo một score riêng cho từng entry cũ; `softmax` biến chúng thành weights.
6. **Retrieve:** các weights trộn value information thành output cho token mới.[^deepseek-v2-2024]

### 2.2 Vai trò của từng thành phần

| Thành phần | Vai trò trực giác | Điều nó không làm |
|---|---|---|
| `KV down-projection` | Ép information của một token qua bottleneck nhỏ | Không gộp nhiều tokens thành một state |
| `Joint KV latent` | Representation nhỏ dùng chung để suy ra content K và V | Không phải summary của cả sequence |
| `K/V up-projections` | Ánh xạ latent sang spaces cần cho attention | Không nhất thiết phải materialize rồi cache khi inference |
| `Decoupled RoPE path` | Mang position mà không chặn projection absorption | Không làm cache independent với context length |
| `Softmax over token entries` | Chọn mức liên quan của từng token cũ | Không có fixed per-step work khi history dài dần |
| `Output projection` | Trộn retrieved head outputs về model stream | Không quyết định cache growth |

### 2.3 Ví dụ xuyên suốt

Với năm token cũ, cache MLA có năm rows. Khi query mới cần hoàn tất câu, nó vẫn tạo năm scores — một score cho mỗi row. Nếu `softmax weights` trực giác là:

```text
Hà      Nội      là      thủ đô      của
0.05    0.10     0.05    0.70        0.10
```

thì token “thủ đô” đóng góp mạnh nhất vào output. MLA có thể làm việc này vì row của token ấy vẫn tồn tại riêng. Nếu thêm 1.000 token, cache có thêm 1.000 rows; mỗi row nhỏ hơn MHA, nhưng query global vẫn phải xét các rows đó trừ khi hệ thống bổ sung sparse selection hoặc local window.

> [!note] `Projection absorption`
> MLA có thể chuyển một số learned projections sang query/output paths bằng tính kết hợp của matrix multiplication. Đây là cách tránh lưu hoặc reconstruct expanded content K/V; nó không merge token positions với nhau.[^deepseek-v2-2024]

## 3. Tác động

### 3.1 Hệ quả trực tiếp của thiết kế

| Trục | Tác động trực tiếp | Điều kiện / chi phí |
|---|---|---|
| `Memory capacity` | Ít elements hơn trên mỗi cached token so với MHA | Compression phụ thuộc latent width và position width |
| `State growth` | Vẫn tăng tuyến tính theo số cached tokens | Mỗi token vẫn có một latent entry riêng |
| `Retrieval behavior` | Giữ global, token-level softmax retrieval | Query vẫn tạo weights trên history axis |
| `Decode bandwidth` | Có thể giảm bytes cần đọc cho cached representation | Lợi ích thực tế cần kernel hỗ trợ projection absorption và layout phù hợp |
| `Decode compute` | Không tự biến global attention thành constant work | Số positions được score vẫn tăng với history |
| `Prefill` | Giảm retained cache representation | Full global score interactions vẫn tồn tại nếu không có sparse/local mechanism |
| `Representation capacity` | Low-rank bottleneck giảm degrees of freedom của cached K/V | Latent quá hẹp có thể làm giảm quality; phải train và đánh giá |

### 3.2 Lợi ích xuất hiện khi nào?

MLA hấp dẫn nhất khi workload có context dài hoặc concurrency cao, `KV cache` là phần memory đáng kể, và model vẫn cần token-level retrieval. Giảm bytes trên mỗi token có thể cho phép context dài hơn hoặc nhiều requests đồng thời hơn, nhưng chỉ khi model weights, temporary buffers hay scheduler không phải bottleneck chi phối.

### 3.3 Điều chỉ benchmark mới trả lời được

Theory cho phép kết luận cache representation nhỏ hơn và vẫn tăng theo context. Theory **không** đủ để kết luận:

- quality bằng hoặc hơn MHA/GQA;
- latency giảm theo đúng compression ratio;
- throughput tăng trên mọi batch size;
- retrieval dài hạn luôn chính xác;
- một latent width cụ thể là tối ưu.

DeepSeek-V2 báo cáo cache-size và quality comparisons có lợi cho MLA trong cấu hình của họ, nhưng đó là author-run, architecture-specific evidence; không phải universal guarantee.[^deepseek-v2-2024]

## 4. Sự khác biệt

### 4.1 So với các baseline gần nhất

| Cơ chế | Giống nhau | Thay đổi nằm ở đâu | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| `MHA` | Token-addressable softmax; một entry mỗi token | Baseline giữ K và V riêng cho mỗi head | Representation capacity cao, cache lớn | Context vừa, quality/capacity ưu tiên hơn cache |
| `GQA/MQA` | Vẫn softmax và cache theo token | Share whole K/V heads giữa query heads | Cache nhỏ hơn MHA, ít independent KV subspaces hơn | Decode bandwidth quan trọng, runtime hỗ trợ tốt |
| `MLA` | Vẫn softmax và cache theo token | Nén K/V qua one joint latent; position path tách riêng | Cache/token nhỏ, thêm bottleneck và implementation complexity | Cần global retrieval nhưng per-token cache phải nhỏ |
| `Fixed-state` | Đều dùng state quá khứ để tạo output | Bỏ token slots; update một recurrent state chung | Bounded state/work nhưng associations có thể interfere | Streaming rất dài, bounded memory quan trọng hơn direct token lookup |
| `Hybrid KDA–MLA` | Kết hợp global retrieval và compressed/fixed memory | Một số layers fixed-state, một số layers MLA | Giảm cache slope nhưng hệ thống phức tạp; vẫn còn growing cache | Workload cần cả long streaming và periodic exact retrieval |

MLA khác GQA/MQA ở **representation axis**: GQA/MQA share nguyên K/V heads; MLA học một low-rank latent chung rồi ánh xạ sang head spaces. MLA khác fixed-state ở **sequence axis**: latent width có thể nhỏ, nhưng vẫn có một row cho mỗi token.[^deepseek-v2-2024][^fast-weight-programmers-2021]

### 4.2 Phần nào giữ nguyên?

Từ góc nhìn block, input hidden states, query-driven scoring, causal masking, `softmax`, weighted retrieval, output projection và residual path vẫn tồn tại. Thay đổi chính nằm giữa hidden state và cached K/V representation, cộng với cách positional information được tách ra để không phá projection absorption.

### 4.3 Các khái niệm dễ nhầm

- `Low-rank compression` giảm **số elements** qua bottleneck; `quantization` giảm **bits per element**.
- `KV-cache compression` không nhất thiết xóa token axis; `fixed-state` mới bỏ growing token slots.
- `Query compression` có thể giảm training activations, nhưng query hiện tại không phải history state nên không trực tiếp giảm decode cache.[^deepseek-v2-2024]
- `Latent` trong MLA là **per-token latent**, không phải một context summary duy nhất.
- `NoPE MLA` trong Kimi Linear là một architecture-specific variant; không được suy rằng mọi MLA đều bỏ positional treatment.[^kimi-linear-2025]

## 5. Trong thực tế

### 5.1 MLA nằm ở đâu trong model và serving system?

MLA thay attention sublayer trong một decoder block. Mỗi MLA layer có projection weights riêng và duy trì cache riêng cho từng active sequence. Inference server quản lý các per-layer entries qua `prefill`, rồi append entry mới ở mỗi `decode step`.

```text
request
  └─► tokenizer
       └─► decoder layer 1: MLA projections + layer-1 latent cache
            └─► decoder layer 2: MLA projections + layer-2 latent cache
                 └─► ...
                      └─► logits ─► sampling

server: scheduler + batching + cache allocator + kernels
```

### 5.2 Walkthrough: assistant đọc repository dài

Giả sử một coding assistant nhận 100.000 tokens source code và sinh 500 tokens trả lời:

1. `Prefill` tạo one latent entry cho mỗi input token ở từng MLA layer.
2. Server phải reserve và ghi cache cho prompt; cache nhỏ hơn MHA nếu MLA dimensions nhỏ hơn expanded K/V.
3. Mỗi `decode step` append một latent entry mới.
4. Query mới vẫn có thể score token ở đầu repository, nên direct token retrieval còn tồn tại.
5. Tuy nhiên global decode vẫn đọc/score history ngày càng dài; cache nhỏ không bảo đảm low latency.
6. Nếu workload chủ yếu streaming vô hạn và hiếm khi cần exact token lookup, fixed-state hoặc hybrid có thể phù hợp hơn.

Kimi Linear minh họa lựa chọn hybrid: ba KDA layers fixed-state xen một global MLA layer. Report mô tả cách này giảm số layers có sequence-growing cache, nhưng toàn model vẫn có cache tăng theo context tại các MLA layers.[^kimi-linear-2025]

### 5.3 Khi nên và không nên dùng

**Nên cân nhắc MLA khi:**

- model được train với MLA hoặc có migration recipe được kiểm chứng;
- global token retrieval là requirement;
- KV-cache capacity/bandwidth giới hạn context hoặc concurrency;
- runtime có optimized MLA kernels và projection absorption.

**Không nên chọn chỉ vì theory khi:**

- phải convert checkpoint MHA/GQA mà không có uptraining/validation;
- workload ngắn nên KV cache không phải bottleneck;
- runtime chỉ hỗ trợ MLA bằng reconstruct K/V chậm;
- requirement là bounded memory bất kể context length;
- exact latency/quality target chưa được benchmark.

### 5.4 Measurement phải kiểm tra

| Measurement | Cần giữ cố định / báo cáo |
|---|---|
| Raw cache bytes | layers, batch, context, dtype, latent/position widths |
| `TTFT` / prefill latency | prompt distribution, batch/concurrency, warmup, cache hits |
| `TPOT` / decode latency | current context length, output length, scheduler, percentile |
| Throughput | request mix, memory budget, batching policy, hardware |
| Quality | same data, tokens, parameters/active compute, eval harness |
| Long-context retrieval | task type, needle depth, distractors, context lengths |

> [!warning] Claim boundary
> Từ theory có thể suy ra retained tensor scaling. Không thể suy trực tiếp end-to-end latency, quality parity, maximum reliable context hay concurrency gain nếu chưa đo trên checkpoint, kernel, dtype, hardware và workload đích.

## 6. Checkpoint trước toán

Đến đây, người mới cần trả lời được:

1. **Giải quyết gì?** Giảm representation được cache cho mỗi token.
2. **Hoạt động ra sao?** Cache one joint latent + position entry mỗi token, rồi softmax-address từng entry.
3. **Tác động gì?** Cache slope nhỏ hơn nhưng vẫn tăng theo context; retrieval trực tiếp còn giữ; latency/quality cần đo.
4. **Khác baseline thế nào?** MHA giữ full per-head K/V, GQA share heads, MLA compress per token, fixed-state bỏ token slots.
5. **Dùng khi nào?** Khi cần global token retrieval và KV cache là bottleneck, với model/runtime đã hỗ trợ và benchmark.

Nếu chưa trả lời được, hãy quay lại Sections 1–5. Toán dưới đây chỉ làm trực giác chính xác hơn.

## 7. Toán học — zoom in

### 7.1 Bảng ký hiệu

| Ký hiệu | Ý nghĩa | Shape / đơn vị |
|---|---|---|
| $B$ | batch size | sequences |
| $L$ | số attention layers | layers |
| $S$ | số cached tokens | tokens |
| $H$ | số query heads | heads |
| $d$ | model width | features |
| $d_h$ | content width mỗi head | features/head |
| $d_c$ | joint KV latent width | features/token/layer |
| $d_h^R$ | shared rotary-key width | features/token/layer |
| $p$ | bytes mỗi element | bytes |
| $h_t$ | hidden state token $t$ | $(d,)$ |
| $c_t^{KV}$ | joint KV latent token $t$ | $(d_c,)$ |

### 7.2 Trường hợp nhỏ nhất tính tay: address ba tokens

**Trực giác.** Một query so sánh riêng với ba keys, tạo ba weights, rồi trộn ba values. Token-addressability nằm ở việc ba slots vẫn tách biệt.

**Công thức.**

$$
\alpha_j=\operatorname{softmax}_j(q^\top k_j),\qquad
o=\sum_{j=1}^{3}\alpha_j v_j
$$

**Ký hiệu.** $q$ là query hiện tại; $k_j,v_j$ là key/value của token thứ $j$; $\alpha_j$ là weight dành riêng cho token đó.

**Shape flow.** Ba dot products tạo scores shape `(3,)`; `softmax` giữ shape `(3,)`; weights nhân ba values shape `(3, d_h)` tạo output `(d_h,)`.

**Ví dụ số.** Nếu scores là `[0, 1, 0]`, weights xấp xỉ `[0.212, 0.576, 0.212]`. Token 2 được đọc mạnh nhất nhưng token 1 và 3 vẫn có địa chỉ riêng.

**Kết luận.** MLA thay representation tạo ra $k_j,v_j$; nó không xóa index $j$.

### 7.3 Baseline attention và shape flow

**Trực giác.** Với cả sequence, mỗi query row chấm với mọi key column.

**Công thức.**

$$
Q=XW^Q,\qquad K=XW^K,\qquad V=XW^V
$$

$$
O=\operatorname{softmax}\!\left(\frac{QK^\top+M}{\sqrt{d_h}}\right)V
$$

**Ký hiệu.** $X$ là hidden states; $W^Q,W^K,W^V$ là learned projections; $M$ là causal mask.

**Shape flow.** Batched multi-head form dùng `Q,K,V: (B,H,S,d_h)`, scores và weights `(B,H,S,S)`, output `(B,H,S,d_h)`.

**Ví dụ số.** Với một batch, hai heads, bốn tokens và head width tám, scores có shape `(1,2,4,4)`: mỗi head chứa 16 token-to-token score slots trước causal masking.

**Kết luận.** Standard global attention có explicit sequence axis; MLA giữ axis này.

### 7.4 Joint low-rank KV compression

**Trực giác.** Thay vì cache expanded K/V, đưa hidden state qua một bottleneck nhỏ rồi cache bottleneck output.

**Công thức.**

$$
c_t^{KV}=W^{DKV}h_t,\qquad
k_t^C=W^{UK}c_t^{KV},\qquad
v_t^C=W^{UV}c_t^{KV}
$$

**Ký hiệu.** $W^{DKV}$ là down-projection; $W^{UK}$ và $W^{UV}$ là content up-projections; superscript $C$ nghĩa là content path.[^deepseek-v2-2024]

**Shape flow.** `(d_c,d) @ (d,) -> (d_c,)`; sau đó `(H*d_h,d_c) @ (d_c,) -> (H*d_h,)`, reshape thành `(H,d_h)`.

**Ví dụ số.** Nếu model width là 16, bốn heads có head width bốn, và latent width là sáu, hidden state đi từ 16 elements xuống sáu cached elements trước khi được ánh xạ lại sang head spaces.

**Kết luận.** Low-rank bottleneck giảm per-token representation; sequence có $S$ tokens vẫn tạo $S$ latent vectors.

### 7.5 Vì sao projection absorption đúng?

**Trực giác.** Thay vì expand cached latent thành key rồi dot với query, có thể transform query trước rồi dot trực tiếp với latent.

**Công thức.**

$$
q^\top (W^{UK}c)=\big((W^{UK})^\top q\big)^\top c
$$

**Ký hiệu.** $q$ là content query, $c$ là cached latent, $W^{UK}$ là key up-projection.

**Shape flow.** Cách trái: `(H*d_h,) dot [(H*d_h,d_c) @ (d_c,)]`; cách phải: `[(d_c,H*d_h) @ (H*d_h,)] dot (d_c,)`; cả hai ra scalar.

**Ví dụ số.** Cho $q=[1,2]$, $W^{UK}=[[3,4],[5,6]]$, $c=[7,8]$. Cách trái tạo key `[53,83]`, score là `219`; cách phải tạo transformed query `[13,16]`, score cũng là `219`.

**Kết luận.** Associativity cho phép score trên latent cache. Tương tự, value up-projection có thể được kết hợp với output path; production kernels không nhất thiết reconstruct full K/V.[^deepseek-v2-2024]

### 7.6 Vì sao cần `decoupled RoPE`?

**Trực giác.** Nếu rotation phụ thuộc position nằm giữa up-projection và latent, một projection cố định không còn hấp thụ được nó cho mọi position. MLA tách content và position thành hai paths.[^deepseek-v2-2024]

**Công thức.**

$$
q_{t,i}=[q_{t,i}^{C};q_{t,i}^{R}],\qquad
k_{t,i}=[k_{t,i}^{C};k_t^{R}]
$$

$$
s_{t,j,i}=\frac{(q_{t,i}^{C})^\top k_{j,i}^{C}+(q_{t,i}^{R})^\top k_j^{R}}
{\sqrt{d_h+d_h^R}}
$$

**Ký hiệu.** $i$ là head; superscript $R$ là rotary path; $[a;b]$ là concatenation; shared $k_j^R$ được cache một lần cho token $j$.

**Shape flow.** Content vectors `(d_h,)` nối rotary vectors `(d_h^R,)` thành `(d_h+d_h^R,)`; decode scores có shape `(B,H,1,S)`.

**Ví dụ số.** Nếu content width là bốn và rotary width là hai, mỗi concatenated query/key head có sáu features. Với năm cached tokens và ba heads, one-token scores có shape `(B,3,1,5)`.

**Kết luận.** Position path thêm cache width nhỏ nhưng giữ content projection absorbable; chiều cuối của scores vẫn là token axis.

### 7.7 Memory accounting

**Trực giác.** So sánh số elements mỗi token trước, rồi nhân với batch, layers, tokens và bytes mỗi element.

**Công thức.**

$$
M_{MHA}=BLS(2Hd_h)p
$$

$$
M_{MLA}=BLS(d_c+d_h^R)p
$$

$$
\frac{M_{MHA}}{M_{MLA}}=\frac{2Hd_h}{d_c+d_h^R}
$$

**Ký hiệu.** Factor `2` là K và V; MLA giữ latent width cộng rotary-key width.[^deepseek-v2-2024]

**Shape flow.** MHA retained state tương ứng `(B,L,S,2,H,d_h)`; MLA retained state tương ứng `(B,L,S,d_c+d_h^R)`. Cả hai đều có trục $S$.

**Ví dụ số.** Với một sequence, 32 layers, 32 heads, head width 128, BF16, latent width 512 và rotary width 64:

| Context | MHA raw cache | MLA raw cache | Tăng khi context tăng 8 lần |
|---:|---:|---:|---:|
| 1,024 | 512 MiB | 36 MiB | — |
| 8,192 | 4,096 MiB | 288 MiB | cả hai 8 lần |
| 32,768 | 16,384 MiB | 1,152 MiB | cả hai 32 lần so với 1,024 |

Các số là pedagogical tensor accounting, không gồm allocator metadata, padding, temporary buffers hay prefix sharing.

**Kết luận.** Trong ví dụ, MLA giảm slope khoảng 14,2 lần; nó không làm slope bằng zero.

### 7.8 Contrast toán học với fixed-state

**Trực giác.** Fixed-state ghi nhiều associations vào cùng một matrix thay vì giữ one row per token.

**Công thức.**

$$
S_t=S_{t-1}+\phi(k_t)^\top v_t,\qquad
o_t=\phi(q_t)S_t
$$

**Ký hiệu.** $\phi$ là feature map; $S_t$ là associative state; $v_t$ là value.[^fast-weight-programmers-2021]

**Shape flow.** `(d_k,1) @ (1,d_v) -> (d_k,d_v)` để update; state luôn `(d_k,d_v)`; read dùng `(1,d_k) @ (d_k,d_v) -> (1,d_v)`.

**Ví dụ số.** State shape `(64,64)` vẫn như nhau sau 10 hay 10.000 tokens. Nhưng associations được superpose, nên keys không đủ tách biệt có thể gây interference.

**Kết luận.** Fixed-state xóa sequence axis khỏi recurrent state bằng cách chấp nhận một retrieval/capacity trade-off khác; MLA giữ direct token slots.

## 8. Implementation — PyTorch tối thiểu

Code cụ thể hóa Sections 2 và 7: tạo one latent per token, cache latent theo sequence axis, reconstruct content K/V để dễ inspect, rồi softmax trên token axis. Production MLA thường absorb projections và dùng optimized cache layout.

Toy cố ý bỏ `decoupled RoPE` để cô lập cache semantics. Nếu thêm RoPE, dùng `interleaved` convention trên pairs `(0,1), (2,3), ...`, và dùng absolute `position_ids`: cached positions bắt đầu từ zero, token mới bắt đầu từ `past_len`.

```python
import math
from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F


class ToyLatentAttention(nn.Module):
    """MLA-like content path để học semantics; không phải production MLA."""

    def __init__(self, d_model: int, n_heads: int, d_latent: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.d_latent = d_latent
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.kv_down = nn.Linear(d_model, d_latent, bias=False)
        self.k_up = nn.Linear(d_latent, d_model, bias=False)
        self.v_up = nn.Linear(d_latent, d_model, bias=False)
        self.out_proj = nn.Linear(d_model, d_model, bias=False)

    def _heads(self, x: torch.Tensor) -> torch.Tensor:
        # (B,T,D) -> (B,H,T,d_h)
        B, T, D = x.shape
        return x.view(B, T, self.n_heads, self.head_dim).transpose(1, 2)

    def forward(
        self,
        x: torch.Tensor,
        past_latent: Optional[torch.Tensor] = None,
        use_cache: bool = False,
    ):
        B, T_new, D = x.shape
        q = self._heads(self.q_proj(x))          # query cho token mới
        c_new = self.kv_down(x)                  # one latent per new token

        if past_latent is None:
            c_all, past_len = c_new, 0
        else:
            if past_latent.shape[0] != B:
                raise ValueError("cache batch size does not match")
            # Teaching only: serving thật tránh copy toàn cache bằng block/pre-allocation.
            c_all = torch.cat((past_latent, c_new), dim=1)
            past_len = past_latent.size(1)

        # Inspectable reconstruction; optimized MLA absorbs these projections.
        k = self._heads(self.k_up(c_all))        # (B,H,S,d_h)
        v = self._heads(self.v_up(c_all))        # (B,H,S,d_h)
        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)

        S = c_all.size(1)
        # Absolute positions: new queries start at past_len.
        q_pos = past_len + torch.arange(T_new, device=x.device)[:, None]
        k_pos = torch.arange(S, device=x.device)[None, :]
        allowed = k_pos <= q_pos
        scores = scores.masked_fill(~allowed, float("-inf"))

        weights = F.softmax(scores, dim=-1)      # (B,H,T_new,S): S token addresses
        y = weights @ v
        y = y.transpose(1, 2).contiguous().view(B, T_new, D)
        present = c_all if use_cache else None   # (B,S,d_latent): still grows with S
        return self.out_proj(y), present, weights
```

## 9. Verification trước benchmark

Dùng float32 trên CPU/GPU. Mỗi test có explicit `rtol` và `atol`; với BF16/FP16 cần tolerance lớn hơn và phải ghi dtype/hardware.

```python
import torch

RTOL, ATOL = 1e-5, 1e-6


@torch.inference_mode()
def test_1_cached_decode_matches_full():
    torch.manual_seed(0)
    layer = ToyLatentAttention(32, 4, 8).eval()
    x = torch.randn(2, 7, 32, dtype=torch.float32)

    full_y, _, _ = layer(x)
    _, cache, _ = layer(x[:, :6], use_cache=True)
    step_y, cache, step_w = layer(x[:, 6:7], cache, use_cache=True)

    torch.testing.assert_close(
        step_y, full_y[:, 6:7], rtol=RTOL, atol=ATOL
    )
    torch.testing.assert_close(
        torch.tensor(cache.shape), torch.tensor([2, 7, 8]), rtol=0, atol=0
    )
    torch.testing.assert_close(
        torch.tensor(step_w.shape), torch.tensor([2, 4, 1, 7]), rtol=0, atol=0
    )


@torch.inference_mode()
def test_2_weights_are_token_addressable_and_normalized():
    torch.manual_seed(1)
    layer = ToyLatentAttention(32, 4, 8).eval()
    _, _, w = layer(torch.randn(1, 5, 32))

    torch.testing.assert_close(
        torch.tensor(w.shape), torch.tensor([1, 4, 5, 5]), rtol=0, atol=0
    )
    torch.testing.assert_close(
        w.sum(dim=-1), torch.ones_like(w.sum(dim=-1)), rtol=RTOL, atol=ATOL
    )
    torch.testing.assert_close(
        w[0, 0, 0, 1:], torch.zeros_like(w[0, 0, 0, 1:]), rtol=0, atol=ATOL
    )


@torch.inference_mode()
def test_3_cache_growth_is_linear_in_tokens():
    torch.manual_seed(2)
    layer = ToyLatentAttention(32, 4, 8).eval()
    _, short, _ = layer(torch.randn(1, 10, 32), use_cache=True)
    _, long, _ = layer(torch.randn(1, 100, 32), use_cache=True)

    ratio = torch.tensor(long.numel() / short.numel())
    torch.testing.assert_close(ratio, torch.tensor(10.0), rtol=0, atol=0)
    torch.testing.assert_close(
        torch.tensor([short.shape[-1], long.shape[-1]]),
        torch.tensor([8, 8]), rtol=0, atol=0
    )


@torch.inference_mode()
def test_4_no_future_leakage():
    torch.manual_seed(3)
    layer = ToyLatentAttention(32, 4, 8).eval()
    x = torch.randn(1, 6, 32)
    y, _, _ = layer(x)

    changed = x.clone()
    changed[:, 3:] = torch.randn(1, 3, 32)
    y_changed, _, _ = layer(changed)
    torch.testing.assert_close(
        y[:, :3], y_changed[:, :3], rtol=RTOL, atol=ATOL
    )


test_1_cached_decode_matches_full()
test_2_weights_are_token_addressable_and_normalized()
test_3_cache_growth_is_linear_in_tokens()
test_4_no_future_leakage()
print("all tests passed")
```

Các test chỉ xác minh toy semantics:

1. Cache reuse không đổi causal output.
2. Weights có one address per token và chuẩn hóa đúng.
3. Latent width cố định nhưng token axis tăng tuyến tính.
4. Future tokens không ảnh hưởng past outputs.

Chúng không chứng minh parity với full DeepSeek-V2 MLA vì toy không implement query compression, decoupled RoPE hay absorbed inference kernels.

## 10. Benchmark và trade-offs

### 10.1 Raw memory benchmark

```python
def mha_cache_bytes(B, L, S, H, d_h, p=2):
    return B * L * S * (2 * H * d_h) * p


def mla_cache_bytes(B, L, S, d_c, d_rope, p=2):
    return B * L * S * (d_c + d_rope) * p


for S in (128, 1024, 8192, 32768):
    mha = mha_cache_bytes(1, 32, S, 32, 128)
    mla = mla_cache_bytes(1, 32, S, 512, 64)
    print(S, f"MHA={mha / 2**20:.1f} MiB", f"MLA={mla / 2**20:.1f} MiB")
```

Đây là deterministic accounting, không phải latency benchmark. Khi đo runtime, tách:

- `prefill latency` theo prompt length;
- `TPOT` theo current context length;
- peak allocated/reserved memory;
- throughput theo concurrency;
- quality/retrieval trên cùng checkpoint recipe và harness.

### 10.2 Trade-off ledger

| Lựa chọn | Memory theo context | Direct token retrieval | Decode work theo history | Rủi ro chính |
|---|---|---|---|---|
| MHA | tăng, slope lớn | có | tăng | KV cache lớn |
| GQA/MQA | tăng, slope nhỏ hơn | có | tăng | KV sharing capacity |
| MLA | tăng, slope nhỏ hơn | có | tăng | low-rank bottleneck + kernel complexity |
| Fixed-state | bounded recurrent state | không có slot trực tiếp | bounded theo state shape | interference/capacity |
| Hybrid | chỉ MLA layers tăng | periodic | workload-dependent | integration complexity |

Không báo một speedup chung: DeepSeek-V2 và Kimi Linear numbers là author-run và phụ thuộc model, layer ratio, kernel, hardware, context và batching.[^deepseek-v2-2024][^kimi-linear-2025]

## 11. Debug checklist

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên |
|---|---|---|
| Cache là `(B,H,S,d_h)` thay vì `(B,S,d_c)` | Đang cache expanded K/V | In `present.shape` ngay sau layer |
| `cached decode != full forward` | Absolute position offset hoặc causal mask sai | In `past_len`, `q_pos`, `k_pos`, `allowed` |
| Future leakage | Mask direction đảo hoặc mask sau softmax | Xác nhận future scores là negative infinity trước softmax |
| Cache nhỏ nhưng latency không giảm | Kernel reconstruct K/V hoặc bottleneck nằm nơi khác | Profile projection, cache reads, attention, scheduler riêng |
| OOM ở context dài | Quên MLA vẫn nhân với batch, layers và tokens | Tính raw bytes với config thật |
| Quality giảm | Latent bottleneck/config hoặc migration không phù hợp | Matched ablation theo latent width và training recipe |
| RoPE cache mismatch | Sai pairing convention hoặc position IDs reset khi decode | Kiểm tra `interleaved` pairs và absolute positions |
| Gọi MLA là fixed-state | Nhìn latent width nhưng bỏ qua token axis | In cache shape ở hai context lengths |

## 12. Giới hạn và bước tiếp theo

Bài này thiết lập mechanism, scaling và verification của một content-path toy; nó không tái lập full MLA, không chứng minh quality parity và không đo production speed. Memory formulas chỉ tính retained tensors. Deployment còn phụ thuộc allocator, cache blocks, precision, fused kernels, batching và prefix sharing.

Học tiếp theo:

1. [Multi-head Latent Attention](multi-head-latent-attention.md) — concept canonical và evidence chi tiết.
2. [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — hiểu update/read và interference.
3. [Delta memory, KDA, và hybrid KDA–MLA](delta-memory-kda-hybrid-architecture-beginners-project.md) — xây fixed-state và hybrid.
4. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — layer ratio và reported trade-offs.
5. [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) — phân biệt compression, quantization, retention và systems effects.

## Relationships

- **Depends on:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) và [KV caching](kv-caching.md) — baseline token retrieval và decode state.
- **Uses:** [Rotary position embedding (RoPE)](rotary-position-embedding.md) qua decoupled position path trong DeepSeek-V2 MLA.
- **Elaborates:** [Multi-head Latent Attention](multi-head-latent-attention.md) bằng top-down explanation, shape derivation, code và tests.
- **Contrasts with:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — bỏ token slots để có bounded recurrent state.
- **Prepares for:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — kết hợp periodic MLA với fixed-state KDA.
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Cơ chế MLA, low-rank joint KV compression, decoupled RoPE, projection absorption và configuration examples dựa trên primary DeepSeek-V2 report. Fixed-state contrast dựa trên primary associative-memory analysis; hybrid scenario dựa trên Kimi Linear report. Reported quality, latency, throughput và cache gains là author-run, configuration-specific evidence và chưa được tái lập ở đây. Data-flow explanation, hand examples, tensor accounting, toy code, tests, benchmark protocol và decision guidance là **pedagogical synthesis**; cần verify trên checkpoint, dtype, kernels, hardware và workload đích.[^deepseek-v2-2024][^fast-weight-programmers-2021][^kimi-linear-2025]

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” arXiv:2405.04434v5, [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.1, 3.1–3.2, and Appendices C–D.
[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4.
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 1–3 and 6.
