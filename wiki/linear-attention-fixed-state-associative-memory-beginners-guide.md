---
type: Synthesis
title: "Linear attention như fixed-state associative memory — bài học cho người mới"
description: A top-down beginner course on why linear attention compresses token history into fixed-state associative memory, how that changes retrieval and serving trade-offs, and how to derive, implement, and verify it.
tags: [attention, associative-memory, linear-attention, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-24T05:13:49Z }
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: gpt2-kimi3-2026
    resource: ../raw/2026-07-27-from-gpt2-to-kimi-k3.md
    title: "22580: From GPT2 to Kimi3, Explained"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
  - id: kimi-k3-2026
    resource: ../raw/arXiv-2607.24653v1/main.tex
    title: "Kimi K3: Open Frontier Intelligence"
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# Linear attention như fixed-state associative memory — bài học cho người mới

`Linear attention` đổi mô hình memory của attention: thay vì giữ một `K/V slot` cho từng token cũ, nó liên tục nén các liên hệ `key → value` vào một `fixed-state associative memory` (bộ nhớ liên kết có kích thước cố định). Nhờ vậy, recurrent state và lượng việc đọc history ở mỗi bước `decode` không tăng theo context length; đổi lại, nhiều memories dùng chung state nên có thể chồng lấn, không còn khả năng truy cập lossless từng token như `softmax attention`.[^fast-weight-programmers-2021][^kimi-linear-2025]

> [!success] Sau bài này
> 1. Bạn có thể giải thích **vấn đề → cơ chế → tác động → khác biệt → cách dùng thực tế** mà chưa cần công thức.
> 2. Bạn có thể derive phép `write`, `read`, và `normalization` từ kernel tách được, kèm `shape flow` và ví dụ số.
> 3. Bạn có thể chạy một PyTorch reference, kiểm tra `recurrent == parallel prefix`, causality, state shape và interference bằng `torch.testing.assert_close`.
> 4. Bạn có thể phân biệt claim do thiết kế suy ra với kết quả chỉ được báo cáo qua benchmark.

## 1. Điều cần biết trước

Bạn chỉ cần hiểu ở mức trực giác:

- `Q/K/V` và `causal attention`: [Attention: beginner's guide](attention-beginner-guide.md).
- `KV cache`, `prefill`, `decode`: [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md).
- Vector, matrix, `dot product`, `outer product`, và phép nhân matrix cơ bản.

Bài này không cover production kernel, distributed training, quantization hay full KDA. Code cố ý dùng `for` loop và materialized prefix làm reference; đó là code để học và kiểm chứng, không phải serving implementation.

## 2. Bức tranh toàn cảnh — vấn đề và mental model

### 2.1 Vấn đề: history càng dài, kho token càng lớn

Trong `softmax attention` có `KV cache`, mỗi token cũ giữ một record riêng. Query mới có thể so với từng record, nên retrieval vẫn `token-addressable`: model có một đường truy cập riêng đến từng vị trí. Nhưng số record, bytes phải giữ và lượng history cần đọc khi `decode` đều tăng theo context length.[^gpt2-kimi3-2026]

`Linear attention` hỏi một câu khác:

> Có thể cập nhật một bản tóm tắt cố định của history, rồi đọc bản tóm tắt đó thay vì giữ và quét mọi token không?

**Ý tưởng cốt lõi trong một câu:** mỗi token ghi một association `key → value` vào cùng một matrix state; query sau đọc matrix đó bằng content của mình.[^fast-weight-programmers-2021]

### 2.2 Mental model: tủ hồ sơ và bảng trắng

```text
Softmax + KV cache
┌────────┬────────┬────────┬────────┐
│ token 1│ token 2│ token 3│  ...   │  thêm token → thêm ngăn
└────────┴────────┴────────┴────────┘
query mới ───────────────────────────► chấm điểm từng ngăn

Linear fixed-state
┌───────────────────────────────────┐
│ một bảng trắng chung              │  thêm token → cập nhật cùng bảng
│ các association chồng lên nhau    │
└───────────────────────────────────┘
query mới ───────────────────────────► đọc một state cố định
```

- **Tủ hồ sơ** tốn chỗ tăng dần nhưng giữ các record tách biệt.
- **Bảng trắng** luôn cùng kích thước nhưng chữ mới có thể đè, trộn hoặc làm nhiễu chữ cũ.

Đây là analogy sư phạm, không phải mô tả rằng model lưu text nguyên văn. `Key`, `value` và state đều là learned numerical representations.

### 2.3 Ví dụ xuyên suốt: stream hỗ trợ khách hàng

Giả sử một sequence chứa các sự kiện:

```text
1. customer_A → order_17
2. order_17   → shipped
3. customer_B → order_42
4. order_42   → delayed
5. hỏi: trạng thái đơn của customer_A?
```

Một hệ token-addressable có thể quay lại từng event. Một fixed-state memory cố gắng gộp các liên hệ vào state:

```text
customer_A ↔ order_17 ↔ shipped
customer_B ↔ order_42 ↔ delayed
```

Query ở bước 5 không hỏi “token số 2 là gì?” mà tạo content key gần với association cần đọc. Nếu learned addresses đủ khác nhau, state trả về thông tin liên quan đến `shipped`; nếu addresses overlap hoặc history chứa nhiều cập nhật xung đột, output có thể thành mixture.

## 3. Cách hoạt động — nhìn từ input đến output

### 3.1 Data flow cho một token

```text
hidden state của token
        │
        ├──► Q projection ─► query ─► feature map ──────────────┐
        ├──► K projection ─► key   ─► feature map ─► WRITE ─┐   │
        └──► V projection ─► value ──────────────────────────┤   │
                                                            ▼   ▼
                                                    fixed matrix state
                                                            │
                                                            └──► READ ─► output
```

Luồng từ đầu đến cuối:

1. **Project:** hidden state được biến thành `query`, `key`, `value`, giống attention thông thường.
2. **Map:** `query` và `key` đi qua `feature map`. Đây là điều kiện để đổi thứ tự tính.
3. **Write:** mapped key và value tạo một update rồi cộng vào matrix state.
4. **Normalize:** một state nhỏ khác theo dõi tổng key features để output không chỉ lớn dần theo số lần write.
5. **Read:** mapped query kết hợp với matrix state; kết quả được chia bởi normalization term.
6. **Emit:** vector đọc được đi tiếp qua output projection, residual path và các phần còn lại của block.

### 3.2 Chạy ví dụ hỗ trợ khách hàng qua flow

| Event | `key` đại diện cho | `value` đại diện cho | State thay đổi trực giác |
|---|---|---|---|
| `customer_A → order_17` | customer A | order 17 | thêm association A–17 |
| `order_17 → shipped` | order 17 | trạng thái shipped | thêm association 17–shipped |
| `customer_B → order_42` | customer B | order 42 | thêm association B–42 |
| `order_42 → delayed` | order 42 | trạng thái delayed | thêm association 42–delayed |
| query về A | pattern gần A/17 | — | đọc mixture ưu tiên pathway A–17–shipped |

Một layer đơn không nhất thiết thực hiện reasoning hai hop như bảng minh họa; nhiều layers, projections và nonlinear blocks phối hợp để tạo behavior đó. Điểm cần giữ là **history không còn là danh sách slot riêng trong fixed-state layer; nó đã được tổng hợp trước khi query cuối xuất hiện**.

### 3.3 Các thành phần phối hợp như thế nào?

| Thành phần | Vai trò | Nếu làm kém |
|---|---|---|
| `Q/K/V projections` | học cách biểu diễn câu hỏi, địa chỉ và nội dung | địa chỉ không phản ánh task |
| `feature map` | làm similarity có thể tách và reassociate | kernel thiếu selectivity hoặc khó ổn định |
| matrix state | giữ các associations đã aggregate | state hẹp gây interference |
| normalization state | kiểm soát scale của normalized variant | output phụ thuộc mạnh vào số writes |
| update rule | quyết định add, correct, decay hay overwrite | stale hoặc conflicting memory tích tụ |
| hybrid global attention | giữ một pathway token-addressable định kỳ | pure fixed-state khó exact copy/retrieval |

## 4. Tác động — behavior, quality, memory, compute và latency

### 4.1 Hệ quả trực tiếp từ thiết kế

| Tác động | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
|---|---|---|---|
| Persistent state | state của fixed-state layer không tăng theo context length | finite capacity, memories superpose | implementation thật sự chỉ giữ final recurrent state |
| Decode work | một token mới đọc state cố định thay vì quét toàn history | work vẫn phụ thuộc state width | recurrent/fused kernel hiệu quả |
| Token retrieval | model học content-based summary | không có slot riêng để exact-address từng token | task có thể nén history thành useful state |
| Prefill/training | recurrence có thể được viết dạng parallel/chunkwise | naive token loop tuần tự và chậm | dùng chunkwise algorithm thay vì Python loop |
| Long streams | có thể tiếp tục update mà state shape không phình | usable memory không phải vô hạn | learned forgetting và workload phù hợp |

Các hàng trên là hệ quả của state layout và data flow. Chúng **không tự chứng minh** quality parity, speedup end-to-end hay usable context vô hạn.[^fast-weight-programmers-2021][^kimi-linear-2025]

### 4.2 Vì sao quality có thể giảm?

Có hai nguồn cần tách:

1. **Kernel limitation:** feature-space similarity không nhất thiết select sắc như exact softmax kernel.
2. **State interference:** nhiều associations dùng chung finite matrix; addresses overlap thì values rò vào nhau.

Normalization kiểm soát scale nhưng không xóa interference. Tăng feature width có thể tăng capacity hoặc cải thiện approximation, nhưng làm state, FLOPs và bandwidth lớn hơn.

### 4.3 Claim benchmark phải đứng riêng

Kimi Linear báo cáo architecture hybrid dùng ba KDA layers rồi một global MLA layer. Trong ablation của chính report, tỷ lệ ba-một có validation perplexity tốt nhất trong các tỷ lệ được liệt kê; report cũng nêu lợi ích latency và throughput ở các workload cụ thể.[^kimi-linear-2025]

Đó là **author-run evidence cho một model, kernel, hardware setup và training recipe**, không phải hệ quả logic rằng mọi linear attention sẽ nhanh hơn hoặc tốt hơn softmax. Bounded state chỉ cho ta biết slope của retained state; wall-clock còn phụ thuộc projections, FFN/MoE, kernel launch, memory movement, batching và global-attention layers.

## 5. Sự khác biệt — baseline nào đổi, phần nào giữ nguyên?

### 5.1 So sánh ba memory models

| Cơ chế | Giống nhau | Khác nhau trong data flow | Trade-off chính | Khi phù hợp |
|---|---|---|---|---|
| `Softmax attention + KV cache` | đều tạo Q/K/V và output mixing | giữ K/V từng token; query chấm từng slot | memory và decode reads tăng theo context, nhưng token-addressable | exact copy, retrieval một item cụ thể, context vừa sức |
| `MLA` | vẫn là global softmax attention | nén K/V **mỗi token** thành latent nhỏ hơn | giảm slope cache nhưng cache vẫn tăng theo context | cần token-addressability với cache/token nhỏ hơn |
| `Linear fixed-state` | vẫn dùng learned query/key/value-like pathways | aggregate history trước; query đọc matrix chung | bounded state đổi lấy interference và finite effective capacity | streaming, long context có thể nén, memory pressure cao |
| `Hybrid KDA–MLA` | phối hợp hai pathways trên | đa số layers recurrent, một số layers global | còn cache tăng ở global layers nhưng giảm tổng slope | cần cân bằng bounded state và periodic exact retrieval |

MLA làm **ngăn tủ mỏng hơn**; fixed-state **bỏ dãy ngăn và dùng bảng chung**. Đây là khác biệt dễ nhầm nhất.[^kimi-linear-2025]

### 5.2 Thay đổi nằm ở đâu?

```text
Giữ nguyên tương đối:
embedding → hidden stream → projections → token mixer output → residual → FFN/MoE

Softmax baseline thay đổi tại token mixer:
new query + [cached K/V từng token] → scores → softmax → weighted values

Fixed-state thay đổi tại token mixer:
new key/value + old state → updated state
new query + updated state → output
```

`Linear attention` không tự thay tokenizer, embedding, residual path, FFN, training objective hay sampler. Architecture thật có thể thay thêm positional treatment, gating và kernels, nhưng đó là quyết định riêng, không nằm trong định nghĩa tối thiểu của fixed-state memory.

### 5.3 Các khái niệm dễ nhầm

- `Linear attention` **không phải** `FlashAttention`: FlashAttention tính exact softmax theo tiles; linear attention đổi kernel/data flow.
- `Fixed-state` **không phải** lossless compression: state shape cố định không bảo đảm giữ mọi chi tiết.
- `Long context` **không đồng nghĩa** exact long-context retrieval.
- `Constant state per layer` **không đồng nghĩa** constant memory toàn model: weights, activations, convolution state và hybrid MLA cache vẫn tồn tại.
- `Decode work independent of context length` trong fixed-state mixer **không đồng nghĩa** constant end-to-end latency.

## 6. Trong thực tế — đặt ở đâu, dùng khi nào?

### 6.1 Nó nằm ở đâu trong model thật?

Fixed-state linear attention thường thay **token-mixing sublayer** của một số hoặc toàn bộ decoder blocks. Kimi Linear không dùng pure linear stack: report interleave ba KDA layers với một global NoPE MLA layer. KDA dùng chunkwise execution cho multi-token processing và recurrent update cho generation; global MLA định kỳ giữ direct token retrieval.[^kimi-linear-2025]

Kimi K3 tiếp tục dùng hybrid fixed-state KDA và periodic global MLA, nên không thể suy rằng toàn model có context-independent decode memory.[^kimi-k3-2026]

### 6.2 Walkthrough: trợ lý đọc log dài liên tục

Scenario: một agent đọc stream log hàng giờ và cần theo dõi service health.

1. **Prefill/chunk processing:** các log tokens đi qua KDA layers; state học giữ patterns như service, error type, xu hướng và status gần đây.
2. **State update:** mỗi chunk cập nhật fixed states; state shape của KDA layers không tăng chỉ vì stream dài hơn.
3. **Periodic retrieval:** global MLA layers vẫn có thể nhìn các token positions cụ thể trong retained context khi task cần trích đoạn chính xác.
4. **Decode:** khi agent trả lời, KDA layer đọc recurrent state; MLA layer đọc cache token-level của riêng nó.
5. **Measure:** theo dõi peak memory, TTFT/prefill latency, time per output token, retrieval accuracy theo context length và quality trên update-conflict cases.

Workload này hưởng lợi nếu phần lớn history có thể nén thành trạng thái hữu ích. Nếu yêu cầu là trích nguyên văn một UUID xuất hiện đúng một lần rất xa trong history, pure fixed-state là lựa chọn rủi ro; global attention hoặc external retrieval phù hợp hơn.

### 6.3 Khi nên và không nên dùng

| Nên cân nhắc | Không nên mặc định chọn |
|---|---|
| streaming dài, online state tracking | exact copy/needle retrieval là yêu cầu cứng |
| concurrency bị giới hạn bởi KV memory | context ngắn và baseline đã đủ nhanh |
| workload chấp nhận learned compression | chưa có optimized recurrent/chunkwise kernel |
| hybrid model có global retrieval pathway | cần suy quality/speed từ complexity table בלבד |

### 6.4 Measurement bắt buộc trước deployment

- Tách `prefill latency`, `decode latency`, throughput và peak allocated memory.
- Sweep context length thay vì chỉ đo một length; quan sát **slope**.
- Đo exact recall, repeated-key updates, stale-memory behavior và normal task quality.
- Giữ model size, active parameters, data, dtype, batch, hardware và kernels càng matched càng tốt.
- Với hybrid, account riêng fixed state và sequence-growing cache.

Từ lý thuyết **không thể suy ra** benchmark quality, tỷ lệ hybrid tối ưu, usable context, speedup wall-clock hay stability ở BF16/FP8. Các điểm đó cần measurement trên target implementation.

> [!note] Checkpoint trước phần toán
> Đến đây, bạn nên trả lời được: cơ chế giải quyết cache/history growth; nó aggregate `key → value` vào state; lợi ích là bounded state còn chi phí là interference; nó khác baseline ở token-mixing memory path; và nó phù hợp với streaming hoặc hybrid long-context hơn exact token retrieval.

## 7. Toán học — zoom in sau trực giác

### 7.1 Bảng ký hiệu

| Ký hiệu | Shape cho một head | Ý nghĩa |
|---|---:|---|
| $t$ | scalar | vị trí hiện tại |
| $d_k$ | scalar | chiều query/key gốc |
| $d_v$ | scalar | chiều value |
| $m$ | scalar | feature width sau feature map |
| $q_t,k_t$ | $(d_k,)$ | query và key tại vị trí $t$ |
| $v_t$ | $(d_v,)$ | value tại vị trí $t$ |
| $\phi(q_t),\phi(k_t)$ | $(m,)$ | mapped query/key |
| $S_t$ | $(m,d_v)$ | associative matrix state |
| $z_t$ | $(m,)$ | normalization state |
| $o_t$ | $(d_v,)$ | output |
| $B,H,T$ | scalars | batch, heads, sequence length |

Với batch và heads, state có shape `(B, H, m, d_v)` và normalizer có shape `(B, H, m)`. Không shape nào chứa trục sequence length.

### 7.2 Trường hợp nhỏ nhất tính tay: hai addresses trực giao

**Trực giác.** Hai key vuông góc chiếm hai “ngăn theo feature” khác nhau trong cùng matrix, nên query trùng key đầu chỉ lấy value đầu.

**Công thức.**

$$
u_A=\begin{bmatrix}1\\0\end{bmatrix},\quad
u_B=\begin{bmatrix}0\\1\end{bmatrix},\quad
S=u_Av_A^\top+u_Bv_B^\top.
$$

$$
u_A^\top S=(u_A^\top u_A)v_A^\top+(u_A^\top u_B)v_B^\top=v_A^\top.
$$

**Ý nghĩa ký hiệu.** $u_A,u_B$ là mapped keys; $v_A,v_B$ là values; $S$ là state sau hai writes.

**Shape flow.** `(2,1) × (1,d_v) → (2,d_v)` cho mỗi write; `(1,2) × (2,d_v) → (1,d_v)` cho read.

**Ví dụ số.** Chọn $v_A=[10,0]$ và $v_B=[0,20]$ thì state là matrix có hai hàng tương ứng; đọc bằng $u_A$ trả `[10,0]`.

**Kết luận.** Exact retrieval xuất hiện trong ví dụ lý tưởng vì addresses trực giao, không phải vì fixed-state tạo slot token-level.

### 7.3 Kernel form: điều kiện để đổi thứ tự tính

**Trực giác.** Nếu similarity giữa query và key có thể viết thành dot product của hai feature vectors được tính riêng, ta có thể cộng các key-value writes trước khi query xuất hiện.

**Công thức.**

$$
\kappa(q,k)=\phi(q)^\top\phi(k),
$$

$$
o_t=\frac{\sum_{j=1}^{t}\kappa(q_t,k_j)v_j}
{\sum_{j=1}^{t}\kappa(q_t,k_j)}.
$$

**Ý nghĩa ký hiệu.** $\kappa$ là similarity kernel; $\phi$ là feature map; chỉ số $j$ chạy qua causal history.

**Shape flow.** Mapped query và key đều `(m,)`; dot product cho scalar; scalar nhân value `(d_v,)`; tổng cho output `(d_v,)`.

**Ví dụ số.** Nếu similarities với hai memories là `2` và `1`, values là `[10,0]` và `[0,20]`, output normalized là `[20,20] / 3 = [6.67,6.67]`.

**Kết luận.** Normalized linear attention vẫn là weighted mixture, nhưng kernel được chọn để reassociate; nó không phải exact softmax nói chung.[^fast-weight-programmers-2021]

### 7.4 Derivation: từ tổng history đến recurrent write/read

**Trực giác.** Gom tất cả outer products `mapped key × value` thành một matrix trước, rồi query chỉ cần nhân matrix đó.

**Công thức.**

$$
\sum_{j=1}^{t}\bigl(\phi(q_t)^\top\phi(k_j)\bigr)v_j^\top
=\phi(q_t)^\top\left(\sum_{j=1}^{t}\phi(k_j)v_j^\top\right).
$$

Đặt state và update:

$$
S_t\triangleq\sum_{j=1}^{t}\phi(k_j)v_j^\top,
\qquad
\boxed{S_t=S_{t-1}+\phi(k_t)v_t^\top}.
$$

Read chưa normalize:

$$
\boxed{\tilde{o}_t=\phi(q_t)^\top S_t}.
$$

**Ý nghĩa ký hiệu.** Mỗi outer product là một write; tổng outer products là memory; mapped query là read address.

**Shape flow.**

```text
φ(k_t)          v_t^T              write             state
 (m,1)     ×    (1,d_v)      →     (m,d_v)     +     (m,d_v)

φ(q_t)^T         S_t               output
 (1,m)      ×    (m,d_v)     →     (1,d_v)
```

**Ví dụ số.** Với mapped key `[1,0]`, value `[10,3]`, outer product là `[[10,3],[0,0]]`. Query `[1,0]` đọc `[10,3]`; query `[0,1]` đọc `[0,0]`.

**Kết luận.** Reassociation xóa trục history khỏi persistent state; chi phí chuyển thành matrix width `m × d_v`.[^fast-weight-programmers-2021]

### 7.5 Normalization state

**Trực giác.** Nếu chỉ cộng writes, output scale có thể tăng cùng tổng similarity. Ta tích lũy tổng key features để biết cần chia bao nhiêu.

**Công thức.**

$$
z_t\triangleq\sum_{j=1}^{t}\phi(k_j),
\qquad
z_t=z_{t-1}+\phi(k_t),
$$

$$
\boxed{o_t=\frac{\phi(q_t)^\top S_t}
{\phi(q_t)^\top z_t+\varepsilon}}.
$$

**Ý nghĩa ký hiệu.** $z_t$ không chứa values; mẫu số là tổng query-key similarity; $\varepsilon$ tránh chia cho zero.

**Shape flow.** Tử số `(1,m) × (m,d_v) → (1,d_v)`; mẫu số `(1,m) × (m,1) → scalar`; scalar chia từng chiều output.

**Ví dụ số.** Nếu tử số `[20,20]`, mẫu số `3`, và epsilon rất nhỏ, output gần `[6.67,6.67]`.

**Kết luận.** Normalization sửa scale, không tách lại memories đã bị overlap.

> [!warning] Causal convention
> Bài và code dùng `write-then-read`, nên output tại vị trí hiện tại thấy cả token hiện tại. `Read-then-write` tạo strict-past convention. Chọn cách nào cũng được, nhưng implementation và tests phải nhất quán.

### 7.6 Interference: crosstalk và collision

**Trực giác.** Query không chỉ kích hoạt key mong muốn; nó còn kích hoạt mọi key có hướng overlap.

**Công thức.**

$$
S=k_Av_A^\top+k_Bv_B^\top,
$$

$$
k_A^\top S=\lVert k_A\rVert^2v_A^\top+(k_A^\top k_B)v_B^\top.
$$

**Ý nghĩa ký hiệu.** Hạng đầu là signal; hạng thứ hai là `crosstalk`.

**Shape flow.** Mỗi dot product key-key là scalar; scalar nhân value cho `(d_v,)`; hai vectors cộng lại.

**Ví dụ số.** Chọn `k_A=[1,0]`, `k_B=[0.8,0.6]`, `v_A=[10,0]`, `v_B=[0,30]`. Đọc bằng `k_A` cho `[10,24]`; số `24` là nhiễu do overlap `0.8 × 30`.

**Kết luận.** Trong không gian feature hữu hạn, interference-free associations cần mapped keys trực giao; tối đa có thể có `m` hướng trực giao. Đây là bound lý tưởng, không phải mốc “quên đúng ở token m+1”.[^fast-weight-programmers-2021]

Nếu cùng address được ghi hai values:

$$
S=uv_1^\top+uv_2^\top=u(v_1+v_2)^\top.
$$

Pure additive memory tạo mixture, không tự hiểu “write sau thắng”. Delta rule đọc value hiện tại rồi ghi correction; learned decay giúp giải phóng capacity rộng hơn.[^fast-weight-programmers-2021][^kimi-linear-2025]

### 7.7 Memory và compute ledger

Gọi $L$ là số layers, $H_{KV}$ là số KV heads, $d_h$ là head width và $p$ là bytes mỗi phần tử. MHA cache lý tưởng hóa có:

$$
M_{KV}=2LBT H_{KV}d_hp,
$$

trong đó $T$ là context length. Với normalized fixed-state:

$$
M_{state}=LBH\bigl(md_v+m\bigr)p.
$$

| Cơ chế | Persistent state theo context | Work attention ở một decode step | Retrieval |
|---|---:|---:|---|
| MHA/GQA + KV cache | tăng tuyến tính theo $T$ | tăng theo $T$ | từng token |
| MLA | tăng tuyến tính theo $T$, slope nhỏ hơn | vẫn phụ thuộc $T$ | từng latent token |
| Fixed-state | không chứa $T$ | phụ thuộc $m d_v$ | aggregated state |

Đây là accounting của retained tensors và dominant mixer work, không phải benchmark latency.

### 7.8 Biến thể nâng cao có thể đọc sau

Delta update sửa association được address:

$$
\bar v_t=S_{t-1}^\top k_t,
\qquad
S_t=S_{t-1}+\beta_tk_t(v_t-\bar v_t)^\top.
$$

KDA thêm channel-wise decay và chunkwise parallel training; chi tiết xem [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md). SSD mở rộng góc nhìn này bằng structured semiseparable masks; xem [Structured State Space Duality](structured-state-space-duality.md).[^kimi-linear-2025][^dao-gu-2024]

## 8. Implementation (PyTorch tối thiểu)

Code nhận Q/K/V đã projected cho **một head**. Nó cụ thể hóa đúng flow ở trên: feature map → outer-product write → normalizer update → read. Toy không dùng RoPE; nếu tích hợp RoPE, phải khai báo pairing convention, chẳng hạn `interleaved`, và dùng absolute `position_ids`. Recurrent cache mỗi layer ở đây là `(B, m, d_v)` cộng `(B, m)`, không phải `(B, H_KV, S, d_h)` như token-level KV cache.

```python
import torch
import torch.nn.functional as F


def positive_feature(x: torch.Tensor) -> torch.Tensor:
    """φ(x) = ELU(x) + 1; shape (..., d_k) -> (..., m), m=d_k."""
    return F.elu(x) + 1.0


def linear_attention_recurrent(q, k, v, eps=1e-6, return_state=False):
    """Normalized causal linear attention, write-then-read.

    q, k: (B, T, d_k)
    v:    (B, T, d_v)
    state: (B, m, d_v); normalizer: (B, m)
    """
    qf, kf = positive_feature(q), positive_feature(k)
    batch, steps, width = qf.shape
    value_width = v.size(-1)
    state = q.new_zeros(batch, width, value_width)
    normalizer = q.new_zeros(batch, width)
    outputs = []

    for t in range(steps):
        # WRITE: mapped key × value -> association update.
        state = state + torch.einsum("bm,bv->bmv", kf[:, t], v[:, t])
        normalizer = normalizer + kf[:, t]

        # READ: mapped query selects a mixture from the shared state.
        numerator = torch.einsum("bm,bmv->bv", qf[:, t], state)
        denominator = torch.einsum(
            "bm,bm->b", qf[:, t], normalizer
        ).unsqueeze(-1)
        outputs.append(numerator / denominator.clamp_min(eps))

    output = torch.stack(outputs, dim=1)
    if return_state:
        return output, (state, normalizer)
    return output


def linear_attention_parallel_reference(q, k, v, eps=1e-6):
    """Materialize every prefix state for verification, not serving."""
    qf, kf = positive_feature(q), positive_feature(k)
    writes = torch.einsum("btm,btv->btmv", kf, v)
    prefix_states = writes.cumsum(dim=1)
    prefix_normalizers = kf.cumsum(dim=1)
    numerator = torch.einsum("btm,btmv->btv", qf, prefix_states)
    denominator = torch.einsum(
        "btm,btm->bt", qf, prefix_normalizers
    ).unsqueeze(-1)
    return numerator / denominator.clamp_min(eps)
```

Production KDA còn short-convolution state, learned decay, delta correction, multiple heads và optimized recurrent/chunkwise kernels. `cumsum` reference materialize `(B,T,m,d_v)`, nên chính nó **không** có fixed-memory behavior; nó chỉ là oracle dễ inspect.

## 9. Verification trước benchmark

Dùng `float64` để test algebra với tolerance chặt. Với BF16/FP16, cần tolerance rộng hơn và kiểm tra numerical range riêng.

```python
@torch.inference_mode()
def test_recurrent_equals_parallel_prefix():
    torch.manual_seed(0)
    q = torch.randn(2, 7, 4, dtype=torch.float64)
    k = torch.randn(2, 7, 4, dtype=torch.float64)
    v = torch.randn(2, 7, 3, dtype=torch.float64)
    actual = linear_attention_recurrent(q, k, v)
    expected = linear_attention_parallel_reference(q, k, v)
    torch.testing.assert_close(actual, expected, rtol=1e-10, atol=1e-10)


@torch.inference_mode()
def test_future_does_not_change_past():
    torch.manual_seed(1)
    q = torch.randn(2, 8, 4, dtype=torch.float64)
    k = torch.randn(2, 8, 4, dtype=torch.float64)
    v = torch.randn(2, 8, 3, dtype=torch.float64)
    baseline = linear_attention_recurrent(q, k, v)
    changed_k, changed_v = k.clone(), v.clone()
    changed_k[:, 5:] = torch.randn_like(changed_k[:, 5:]) * 100
    changed_v[:, 5:] = torch.randn_like(changed_v[:, 5:]) * 100
    changed = linear_attention_recurrent(q, changed_k, changed_v)
    torch.testing.assert_close(
        baseline[:, :5], changed[:, :5], rtol=1e-10, atol=1e-10
    )


@torch.inference_mode()
def test_state_shape_is_independent_of_sequence_length():
    shapes = []
    for steps in (3, 100):
        q = torch.randn(2, steps, 4, dtype=torch.float64)
        k = torch.randn(2, steps, 4, dtype=torch.float64)
        v = torch.randn(2, steps, 3, dtype=torch.float64)
        output, (state, normalizer) = linear_attention_recurrent(
            q, k, v, return_state=True
        )
        assert output.shape == (2, steps, 3)
        shapes.append((state.shape, normalizer.shape))
    assert shapes == [
        (torch.Size([2, 4, 3]), torch.Size([2, 4])),
        (torch.Size([2, 4, 3]), torch.Size([2, 4])),
    ]


@torch.inference_mode()
def test_orthogonal_retrieval_and_crosstalk():
    e1 = torch.tensor([1.0, 0.0], dtype=torch.float64)
    e2 = torch.tensor([0.0, 1.0], dtype=torch.float64)
    v1 = torch.tensor([10.0, 0.0], dtype=torch.float64)
    v2 = torch.tensor([0.0, 20.0], dtype=torch.float64)
    state = torch.outer(e1, v1) + torch.outer(e2, v2)
    torch.testing.assert_close(e1 @ state, v1, rtol=0.0, atol=0.0)

    overlap = torch.tensor([0.8, 0.6], dtype=torch.float64)
    v3 = torch.tensor([0.0, 30.0], dtype=torch.float64)
    state = state + torch.outer(overlap, v3)
    expected = torch.tensor([10.0, 24.0], dtype=torch.float64)
    torch.testing.assert_close(e1 @ state, expected, rtol=1e-12, atol=1e-12)


test_recurrent_equals_parallel_prefix()
test_future_does_not_change_past()
test_state_shape_is_independent_of_sequence_length()
test_orthogonal_retrieval_and_crosstalk()
print("all tests passed")
```

Bốn tests trả lời bốn câu khác nhau:

1. **Algebra:** recurrent và prefix evaluation có cùng semantics.
2. **Causality:** future writes không đổi past outputs.
3. **State scaling:** output length đổi, recurrent state shape không đổi.
4. **Capacity behavior:** orthogonal addresses tách được; overlap tạo crosstalk dự đoán được.

## 10. Benchmark và trade-offs

### 10.1 Đo raw state trước latency

```python
def mha_cache_bytes(B, L, S, H_kv, d_h, bytes_per_element=2):
    return 2 * B * L * S * H_kv * d_h * bytes_per_element


def fixed_state_bytes(B, L, H, m, d_v, bytes_per_element=2):
    return B * L * H * (m * d_v + m) * bytes_per_element


for length in (128, 1024, 8192, 32768):
    mha = mha_cache_bytes(1, 32, length, 32, 128)
    fixed = fixed_state_bytes(1, 32, 4, 128, 128)
    print(length, mha / 2**20, fixed / 2**20)
```

Đây chỉ đo theoretical retained elements cho hai layouts minh họa. Nó không account allocator fragmentation, convolution state, MLA layers, activations, quantization metadata hay kernel workspace.

### 10.2 Protocol tối thiểu

| Measurement | Sweep/control | Điều có thể kết luận | Không thể kết luận |
|---|---|---|---|
| state bytes | context length, batch, dtype | slope của retained state | latency |
| prefill latency | prompt length, batch | multi-token execution cost | decode speed |
| decode ms/token | warm cache, generated length | recurrent serving behavior | quality |
| exact recall | distance, number of writes | retrieval degradation | general language quality |
| task metrics | matched model/data/training | end-task result cho setup | causal effect của một component nếu thiếu ablation |

Kimi Linear report nêu khoảng `2.9×` prefill và `2.2×` batch-one decode speedup so với MLA ở configuration một-million-token của họ; maximum-throughput setup báo con số lớn hơn do tận dụng memory cho batch. Các số này là author-run, workload-specific và không được tái lập bởi lab toy này.[^kimi-linear-2025]

### 10.3 Decision table

| Ưu tiên | Chọn để thử trước | Rủi ro cần test |
|---|---|---|
| exact token retrieval | softmax/GQA/MLA | KV memory và long-context latency |
| bounded streaming state | recurrent linear/KDA-like | interference, stale memory, kernel maturity |
| cân bằng | hybrid recurrent + periodic global attention | global cache vẫn tăng; ratio không universal |
| chỉ cần kernel-efficient exact attention | FlashAttention | không giảm token-level cache bằng việc đổi semantics |

## 11. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| recurrent khác prefix | write/read order hoặc epsilon khác | so state ở từng timestep |
| future leakage | prefix không causal hoặc dùng future K/V | perturb future rồi so past |
| state có trục sequence | đang giữ mọi prefix writes | in `state.shape`, phân biệt oracle và cache |
| NaN/Inf | denominator nhỏ, feature map hoặc dtype bất ổn | log min denominator và feature range |
| output thành mixture | key collision/overlap | đo pairwise key similarity |
| repeated key không overwrite | additive rule không có correction | thử delta update |
| memory nhỏ nhưng không nhanh | bottleneck ở FFN, projections, launch hoặc bandwidth | profile từng kernel, tách prefill/decode |
| hybrid vẫn tăng memory | MLA/global layers còn token cache | account từng layer type |
| long-context quality giảm | finite capacity, decay hoặc distribution shift | sweep distance và write count |

## 12. Giới hạn và bước tiếp theo

Lab này chứng minh algebra và state semantics của normalized additive linear attention. Nó không implement full KDA, không attest speedup, không chứng minh quality parity và không cho phép suy ra usable context length.

Học tiếp theo:

1. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — targeted correction và learned forgetting.
2. [Delta memory, KDA, và hybrid KDA–MLA — mini-project](delta-memory-kda-hybrid-architecture-beginners-project.md) — build overwrite behavior và hybrid path.
3. [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — hiểu rõ “nén mỗi token” khác “nén toàn history”.
4. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — architecture và author-run evidence.
5. [Structured State Space Duality](structured-state-space-duality.md) — góc nhìn recurrence/structured attention tổng quát hơn.

Bài tập:

- Đổi code sang `read-then-write` và test output đầu tiên theo strict-past convention.
- Sweep số writes và feature width; plot retrieval error.
- Implement delta update cho repeated-key case.
- So raw bytes và latency theo context length; không dùng bytes làm proxy trực tiếp cho latency.

## Relationships

- **Depends on:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md) — baseline token-addressable để thấy phần data flow bị thay.
- **Depends on:** [KV caching](kv-caching.md) — cache growth là vấn đề serving mà fixed-state thay đổi.
- **Elaborates:** [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) — course mở rộng concept thành top-down explanation, derivation và lab.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — MLA nén state trên mỗi token nhưng vẫn giữ trục context.
- **Improved by:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — correction và decay quản lý finite state.
- **Used by:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) và [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — fixed-state KDA phối hợp periodic global MLA.[^kimi-linear-2025][^kimi-k3-2026]
- **Generalized by:** [Structured State Space Duality](structured-state-space-duality.md) — mở rộng từ all-ones causal accumulation sang structured semiseparable masks.[^dao-gu-2024]
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Fast-weight interpretation, recurrent write/read và associative-capacity analysis dựa trên primary paper 2021; KDA recurrence, chunkwise/recurrent split, hybrid ratio và performance claims dựa trên Kimi Linear report; Kimi K3 và SSD chỉ hỗ trợ architecture/generalization context. Benchmark results là author-run và chưa được independently replicated ở đây. Các diagrams, support-stream example, decision tables, PyTorch implementation và tests là **pedagogical synthesis**. Chúng xác minh toy semantics, không xác minh production kernels, training stability, quality, usable context hay wall-clock gains.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4 and Appendices A–B.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md). Secondary explanatory evidence; primary-paper claims take precedence.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 1–3, 5–6 and appendices.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.1 and 5.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 4–6.
