---
type: Synthesis
title: "Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới"
description: A top-down beginner course and PyTorch project explaining delta correction, channel-wise decay, fixed-state limits, and periodic MLA in hybrid long-context architectures.
tags: [delta-rule, kda, associative-memory, fixed-state, hybrid-attention, mla, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-24T12:23:09+07:00
sources:
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới

`Delta memory` (bộ nhớ hiệu chỉnh theo sai số) sửa association mà một key đang truy xuất thay vì tiếp tục cộng value mới vào association cũ. `Kimi Delta Attention` (KDA) bổ sung `channel-wise decay` (quên theo từng kênh) để kiểm soát retention chi tiết hơn, nhưng vẫn nén toàn bộ history vào một `fixed-state` (trạng thái kích thước cố định). Vì state này không còn slot riêng cho từng token, Kimi Linear xen kẽ ba KDA layers với một global MLA layer để đổi phần lớn cache tăng theo context lấy state cố định, đồng thời giữ một số đường truy xuất mức token.[^fast-weight-programmers-2021][^gated-deltanet-2025][^kimi-linear-2025]

> [!success] Sau bài này
> 1. Bạn có thể giải thích vấn đề, data flow, tác động, khác biệt và điều kiện sử dụng KDA mà chưa cần công thức.
> 2. Bạn có thể phân biệt `additive write`, `delta correction`, scalar decay, channel-wise decay và periodic MLA.
> 3. Bạn có thể tự suy ra recurrence, đọc shape flow, chạy PyTorch toy và kiểm chứng overwrite, interference, causality cùng state growth.
> 4. Bạn có thể tách hệ quả trực tiếp của thiết kế khỏi kết quả benchmark do tác giả báo cáo.

## 1. Bức tranh toàn cảnh

### 1.1 Vấn đề: context dài tạo ra hai yêu cầu xung đột

Một model xử lý stream dài thường muốn đồng thời:

- giữ chi tiết cũ để có thể copy hoặc truy xuất lại;
- cập nhật fact đã đổi mà không trộn value cũ với value mới;
- không để memory và decode cost tiếp tục tăng theo mỗi token;
- chạy hiệu quả trên GPU khi training và prefill.

`Token-addressable attention` (attention có thể chấm điểm từng token) giữ mỗi token trong một slot riêng. Cách này hỗ trợ truy xuất chi tiết, nhưng cache vẫn tăng theo context. `Fixed-state linear memory` làm điều ngược lại: gom history vào một state có kích thước không đổi, đổi lại các associations phải dùng chung capacity và có thể gây `interference` (nhiễu chéo).[^fast-weight-programmers-2021][^kimi-linear-2025]

### 1.2 Ý tưởng cốt lõi trong một câu

**KDA đọc value hiện tại tại key, chỉ ghi phần sai lệch sau khi quên có chọn lọc; hybrid KDA–MLA dùng state cố định cho phần lớn layers và giữ global token retrieval ở các layers định kỳ.**[^kimi-linear-2025]

### 1.3 Mental model: bảng trắng và tủ hồ sơ

```text
Token-level KV / MLA = tủ hồ sơ
  - mỗi token có một ngăn riêng
  - tìm lại chi tiết dễ hơn vì ngăn vẫn còn
  - càng nhiều token, tủ càng lớn

Additive fixed-state = một bảng trắng dùng chung
  - mỗi write chồng thêm nét mới
  - bảng không lớn lên
  - hai nét tại cùng vùng có thể trộn vào nhau

Delta memory = bảng trắng + thao tác sửa
  - nhìn nội dung hiện tại tại vùng cần sửa
  - chỉ thêm phần chênh lệch để vùng đó tiến về value mới

KDA = delta memory + núm "độ phai" cho từng vùng
  - vùng cần giữ lâu phai chậm
  - vùng cần giải phóng phai nhanh

Hybrid KDA–MLA = nhiều bảng trắng, thỉnh thoảng có một tủ hồ sơ
  - phần lớn layers dùng KDA
  - một số layers vẫn nhìn được từng token qua MLA
```

Mental model này chỉ mô tả storage và retrieval. Trong model thật, key, value, query và gates đều được học từ hidden state; model không nhận thao tác database rõ ràng.[^fast-weight-programmers-2021][^kimi-linear-2025]

### 1.4 Điều cần biết trước

- [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — vì sao history có thể được gom vào matrix state.
- [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — vì sao latent nhỏ hơn vẫn còn một entry trên mỗi token.
- [KV caching](kv-caching.md) — phân biệt cache reuse với fixed-state compression.

Bài này không cover CUDA kernel, distributed training, MoE routing hay quantization. `RoPE` không xuất hiện trong toy code; Kimi Linear dùng NoPE ở global MLA layers, còn KDA mang positional behavior theo thiết kế được báo cáo.[^kimi-linear-2025]

## 2. Cách hoạt động — nhìn từ đầu đến cuối

Ta dùng một ví dụ xuyên suốt: stream cần nhớ gói dịch vụ của `user_17`.

```text
Token/event 1: user_17 có plan_free
Token/event 2: có nhiều thông tin không liên quan
Token/event 3: user_17 đổi sang plan_pro
Token/event 4: model được hỏi plan hiện tại của user_17
```

### 2.1 Data flow của một KDA layer

```text
hidden state của token hiện tại
        │
        ├──► key: chọn vùng memory cần đọc/sửa
        ├──► value: nội dung mới muốn ghi
        ├──► query: đọc state để tạo output
        ├──► write gate: sửa mạnh hay nhẹ
        └──► decay gates: mỗi channel giữ hay quên bao nhiêu
                         │
state cũ ──► decay theo channel
                         │
                         ├──► đọc prediction hiện tại tại key
                         ├──► error = value mới - prediction cũ
                         ├──► ghi error có kiểm soát
                         └──► state mới, cùng kích thước state cũ
                                      │
query ────────────────────────────────► output
```

Vai trò của từng thành phần:

| Thành phần | Câu hỏi nó trả lời | Trong ví dụ |
|---|---|---|
| `key` | Sửa vùng nào? | vùng biểu diễn `user_17` |
| `value` | Muốn vùng đó trả gì? | `plan_pro` |
| `prediction` | State hiện đang trả gì? | `plan_free` |
| `error` | Cần sửa bao nhiêu? | bỏ dấu vết cũ, thêm value mới |
| `write gate` | Tin write này đến mức nào? | full update hoặc partial update |
| `decay gates` | Channel nào nên giữ/quên? | giữ identity, giảm dấu vết đã lỗi thời |
| `query` | Đọc gì để đưa sang layer tiếp theo? | truy xuất trạng thái liên quan user |

Delta correction tạo semantics gần với “sửa association” hơn additive write: nếu state đã trả đúng value, error gần bằng không; nếu value đổi, update tập trung vào phần chênh lệch.[^fast-weight-programmers-2021][^parallel-deltanet-2024]

### 2.2 Ví dụ chạy xuyên suốt

1. **Write đầu tiên:** state chưa biết `user_17`; prediction rỗng, nên correction ghi `plan_free`.
2. **Distractors:** các tokens khác cập nhật các vùng khác, nhưng có thể gây nhiễu nếu learned keys chồng lấn.
3. **Overwrite:** key cho `user_17` đọc lại association hiện tại. Value mới là `plan_pro`, nên correction không cộng cả hai plans mà đẩy association về plan mới.
4. **Read:** query đọc state đã cập nhật và truyền output sang residual stream.

Nếu hai entities khác nhau bị projection thành gần cùng key, sửa entity thứ hai có thể làm hỏng entity thứ nhất. Delta rule sửa đúng lỗi “cộng mãi tại cùng address”, nhưng không thể phục hồi identity đã mất khi nhiều items bị nén vào cùng address.[^fast-weight-programmers-2021]

### 2.3 Data flow của hybrid theo chiều sâu

Kimi Linear không chạy MLA sau mỗi ba tokens. Pattern là theo **layer depth**: mọi token đi qua mọi layer.[^kimi-linear-2025]

```text
input sequence
    │
    ▼
KDA layer 1  ── fixed recurrent state
    │
KDA layer 2  ── fixed recurrent state
    │
KDA layer 3  ── fixed recurrent state
    │
Global MLA   ── token-addressable latent cache
    │
    └──────── repeat pattern theo depth ───────► model output
```

KDA layers liên tục nén và cập nhật history. Global MLA layer vẫn tạo score riêng trên các retained token entries, nên nó cung cấp một data path khác cho exact copying và fine-grained retrieval. Hai mechanisms nối tiếp nhau, không phải một “backup database” được gọi conditionally.[^kimi-linear-2025]

### 2.4 Training/prefill và decode không chạy giống nhau

- **Training/prefill:** recurrence từng token tạo dependency tuần tự. DeltaNet và KDA dùng `chunkwise` WY/UT formulations để chuyển phần lớn work trong chunk thành matrix multiplication, còn state đi recurrently qua biên chunk.[^parallel-deltanet-2024][^kimi-linear-2025]
- **Decode:** token mới trực tiếp cập nhật recurrent state; MLA layers append latent cache entry cho token mới.[^kimi-linear-2025]

Chunkwise execution là cách tính hiệu quả hơn cho cùng recurrence, không phải một memory semantics khác.

## 3. Tác động

### 3.1 Hệ quả trực tiếp từ thiết kế

| Mặt tác động | Lợi ích trực tiếp | Chi phí / điều kiện |
|---|---|---|
| `behavior` | repeated key có thể được sửa thay vì cộng dồn | exact overwrite cần assumptions về key và gate; learned model không được bảo đảm |
| `memory` | KDA state không thêm một slot mới cho mỗi token | toàn hybrid vẫn có MLA cache tăng theo context |
| `decode` | KDA layer đọc và cập nhật tensor kích thước cố định | latency thực còn phụ thuộc kernel, convolution state, dtype và hardware |
| `capacity` | decay giải phóng dấu vết cũ; channel-wise decay kiểm soát retention chi tiết hơn | quên cũng làm mất thông tin; shared state vẫn có interference |
| `retrieval` | delta correction cải thiện association được address | không khôi phục token slots hoặc phân biệt hai logical items có cùng address |
| `training` | chunkwise algorithm mở ra GPU-friendly matrix operations | implementation phức tạp hơn toy recurrence và vẫn mang state qua chunks |
| `scaling` | giảm số layers có sequence-growing cache trong hybrid | global MLA layers vẫn đọc context và tỷ lệ layer là hyperparameter kiến trúc |

Các hệ quả “state KDA không tăng theo token”, “MLA cache vẫn tăng” và “delta update sửa association được chọn” theo trực tiếp từ state layout và recurrence. Quality, perplexity, speedup và tỷ lệ hybrid tối ưu **không** thể suy ra chỉ từ các tính chất đó.[^fast-weight-programmers-2021][^kimi-linear-2025]

### 3.2 Điều kiện để lợi ích xuất hiện

KDA có lợi nhất khi:

- task-relevant history có thể nén vào learned state;
- keys đủ phân tách để interference không chi phối;
- gates học được khi nào ghi và khi nào quên;
- runtime có chunkwise/fused recurrent kernels phù hợp;
- workload đủ dài để phần cache và history access bị tránh trở nên đáng kể.

Nếu context ngắn, kernel overhead có thể lấn át lợi ích. Nếu workload đòi exact copying từ rất nhiều vị trí xa, pure fixed-state là lựa chọn rủi ro hơn token-addressable attention.

### 3.3 Kết quả benchmark được báo cáo — không phải hệ quả tất yếu

Trong ablation Kimi Linear, tỷ lệ KDA:MLA là 3:1 đạt validation perplexity 5.65, gần với 1:1 ở 5.66 và tốt hơn các tỷ lệ 7:1, 15:1 cùng full MLA trong recipe được test. Điều này hỗ trợ lựa chọn 3:1 cho cấu hình đó, không chứng minh 3:1 tối ưu phổ quát.[^kimi-linear-2025]

Report cũng nêu tại batch size một và context một triệu token: prefill 22.753 giây so với 65.460 giây cho MLA; decode 7.99 ms/token so với 17.76 ms/token. Một setup maximum-throughput khác báo cáo mức tăng 6.3 lần; không được trộn con số throughput này với batch-one latency.[^kimi-linear-2025]

Các nghiên cứu DeltaNet và Gated DeltaNet riêng biệt cũng cho thấy hybrid local/global attention thường cải thiện recall hoặc long-context results trong recipe của họ. Đây là evidence về các model được test, không phải proof rằng mọi hybrid sẽ thắng pure recurrence.[^parallel-deltanet-2024][^gated-deltanet-2025]

## 4. Sự khác biệt

### 4.1 So với baseline và cơ chế gần nhất

| Cơ chế | Giống nhau | Thay đổi ở data flow | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| `Additive fixed-state` | cùng gom writes vào matrix state | ghi toàn value, không đọc lỗi trước khi ghi | đơn giản nhưng repeated writes bị cộng/trộn | toy đơn giản, history ít xung đột |
| `DeltaNet` | vẫn là fixed-state | đọc association hiện tại rồi ghi correction | overwrite tốt hơn; chưa có broad forgetting | cần sửa association có chọn lọc |
| `Gated DeltaNet` | giữ delta correction | thêm scalar decay cho toàn state/head | dọn memory rộng nhưng mọi channel cùng retention | cần forgetting toàn cục đơn giản |
| `KDA` | giữ fixed state và delta correction | thay scalar decay bằng channel-wise decay | retention linh hoạt hơn; gate/state transition phức tạp hơn | stream dài, learned compression quan trọng |
| `MLA` | vẫn là learned token mixer | giữ latent riêng cho từng token và chấm điểm từng vị trí | cache/read tăng theo context nhưng còn token-addressability | exact copy, retrieval chi tiết |
| `Hybrid KDA–MLA` | dùng cả learned fixed state và global retrieval | đổi loại token mixer theo layer depth | giảm cache slope, không tạo constant total cache | workload cần cân bằng memory và retrieval |

DeltaNet, Gated DeltaNet và KDA thay **state update**; phần còn lại của model vẫn có projections, normalization, residual path, output projection và MLP. Hybrid KDA–MLA thay **loại token mixer theo layer**; residual/MLP stack tiếp tục kết nối các layers.[^gated-deltanet-2025][^kimi-linear-2025]

### 4.2 Các khái niệm dễ nhầm

- `Overwrite` khác `forgetting`: overwrite sửa association được key hiện tại chọn; decay làm cũ đi một vùng rộng hơn.
- `Channel-wise` không có nghĩa “mỗi token một channel”: nhiều tokens vẫn chia sẻ hữu hạn channels.
- `Fixed-state` không có nghĩa “nhớ vô hạn”: kích thước không đổi là memory bound, không phải information guarantee.
- `Latent` không đồng nghĩa fixed-state: MLA latent nhỏ hơn K/V chuẩn nhưng vẫn có một latent trên mỗi token.
- `Periodic MLA` là periodic theo depth, không phải time.
- `KV cache` giữ candidate slots nhưng không bảo đảm model chọn đúng candidate.
- `Chunkwise` nói về execution schedule, không thay đổi mục tiêu của recurrence.[^parallel-deltanet-2024][^kimi-linear-2025]

## 5. Trong thực tế

### 5.1 Cơ chế nằm ở đâu trong model thật?

Trong một decoder block, KDA hoặc MLA thay vị trí của self-attention token mixer:

```text
hidden states
   │
normalization
   │
KDA hoặc MLA token mixer  ◄── recurrent state / latent KV cache
   │
residual addition
   │
normalization → MLP → residual addition
   │
next block
```

Một KDA layer thật còn có learned Q/K/V projections, short convolution, normalized Q/K, output normalization và output gate. Recurrence trong bài chỉ là lõi memory, không phải toàn bộ production layer.[^kimi-linear-2025]

### 5.2 Khi nào nên dùng, khi nào không?

**Nên cân nhắc KDA hoặc hybrid khi:**

- serving có long-lived streams hoặc context rất dài;
- KV-cache capacity hay decode bandwidth là bottleneck;
- workload cần summary/recency/state tracking nhiều hơn exact archival lookup;
- có thể train architecture end-to-end và triển khai kernel chuyên dụng;
- chấp nhận đo retrieval quality theo workload thay vì suy từ context-window headline.

**Không nên mặc định dùng pure KDA khi:**

- workload chủ yếu là exact copying, source citation hoặc needle retrieval ở vị trí bất kỳ;
- context ngắn và implementation overhead quan trọng hơn cache growth;
- cần đổi architecture của checkpoint softmax có sẵn mà không retrain;
- runtime không có chunkwise hoặc fused recurrent kernel đã được kiểm chứng;
- requirement đòi lossless history — fixed-state learned memory không cung cấp guarantee đó.

### 5.3 Walkthrough triển khai: trợ lý theo dõi ticket dài

Giả sử một support assistant đọc ticket có hàng chục nghìn events:

1. KDA layers giữ trạng thái tiến triển như owner hiện tại, severity và decision gần nhất.
2. Delta correction giúp một owner hoặc severity mới thay association cũ thay vì cộng hai trạng thái.
3. Channel-wise decay cho phép các features tạm thời phai nhanh hơn các features ổn định.
4. Periodic MLA layers giữ đường truy cập từng event để model còn cơ hội trích exact error code hoặc câu người dùng đã viết.
5. Khi decode, KDA states giữ kích thước cố định; MLA caches vẫn tăng ở các global layers.

Workload này chỉ hưởng lợi nếu learned keys/gates thật sự mã hóa đúng state transitions và periodic MLA đủ cho evidence lookup. Theory không chứng minh assistant sẽ cite đúng event.

### 5.4 Measurement phải kiểm tra

- **Quality:** exact copy, overwrite, distractor resistance, recent-versus-distant recall, task score.
- **Memory:** peak allocated bytes, recurrent state, convolution state, MLA cache và allocator overhead.
- **Latency:** prefill riêng; time per output token theo context riêng; batch-one và throughput riêng.
- **Numerics:** recurrent-versus-chunkwise parity ở FP32/BF16, drift theo sequence length, NaN/Inf.
- **Scale:** nhiều context lengths, batch sizes, head widths và hybrid ratios.
- **Evidence:** cùng model size, data, training tokens, tokenizer, kernel và hardware nếu muốn gán chênh lệch cho mechanism.

Không thể suy quality parity, production latency, ratio tối ưu hay long-context reliability chỉ từ state size và asymptotic argument.

> [!note] Gate kiểm tra trước toán
> Đến đây, người đọc đã có thể trả lời: cơ chế giải quyết repeated-write và cache-growth trade-off; nó chạy qua decay → predict → correct → read; nó giảm state growth nhưng đổi lấy interference; nó khác additive/MLA ở state update và token slots; nó phù hợp khi long-context memory cost quan trọng nhưng cần benchmark retrieval thực tế.

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
| $\hat v_t$ | $(d_v,)$ | value state hiện dự đoán tại key |
| $\beta_t$ | scalar trong $[0,1]$ | write strength |
| $\alpha_t$ | scalar hoặc $(d_k,)$ | decay gate |
| $I$ | $(d_k,d_k)$ | identity matrix |

### 6.2 Trường hợp nhỏ nhất: additive write thất bại khi overwrite

**Trực giác.** Nếu cùng một address nhận value cũ rồi value mới, additive memory giữ tổng hai writes.

**Công thức.**

$$
S_t=S_{t-1}+k_tv_t^\top,
\qquad
\operatorname{read}(q)=q^\top S_t.
$$

**Ý nghĩa ký hiệu.** $k_t$ chọn direction cần ghi; $v_t$ là nội dung; outer product tạo một matrix write; query nhân state để lấy value.

**Shape flow.**

$$
(d_k,1)(1,d_v)=(d_k,d_v),
\qquad
(1,d_k)(d_k,d_v)=(1,d_v).
$$

**Ví dụ số.** Chọn key đơn vị và hai values:

$$
k=\begin{bmatrix}1\\0\end{bmatrix},\quad
v_{old}=\begin{bmatrix}1\\0\end{bmatrix},\quad
v_{new}=\begin{bmatrix}0\\1\end{bmatrix}.
$$

Sau hai writes:

$$
S=kv_{old}^\top+kv_{new}^\top
=\begin{bmatrix}1&1\\0&0\end{bmatrix},
\qquad
k^\top S=\begin{bmatrix}1&1\end{bmatrix}.
$$

**Kết luận.** Output là tổng, không phải value mới. Additive update không tự biết write thứ hai mang nghĩa overwrite.

### 6.3 Delta correction: predict rồi sửa error

**Trực giác.** Đầu tiên hỏi memory đang trả gì tại key, sau đó chỉ ghi phần còn thiếu.

**Công thức.**

$$
\hat v_t=S_{t-1}^\top k_t,
\qquad
e_t=v_t-\hat v_t,
$$

$$
\boxed{S_t=S_{t-1}+\beta_t k_te_t^\top}
= S_{t-1}+\beta_t k_t(v_t-S_{t-1}^\top k_t)^\top.
$$

**Ý nghĩa ký hiệu.** $\hat v_t$ là prediction cũ; $e_t$ là retrieval error; $\beta_t$ quyết định correction mạnh đến đâu.

**Shape flow.**

| Mảnh | Shape |
|---|---:|
| $S_{t-1}^\top k_t$ | $(d_v,d_k)(d_k,)\to(d_v,)$ |
| $e_t$ | $(d_v,)$ |
| $k_te_t^\top$ | $(d_k,1)(1,d_v)\to(d_k,d_v)$ |
| $S_t$ | $(d_k,d_v)$, không xuất hiện trục $T$ |

**Ví dụ số.** Với key đơn vị ở trên, sau khi state đã lưu value cũ, prediction là value cũ. Error bằng value mới trừ value cũ. Khi write strength bằng một, cộng error vào đúng hàng đã chọn làm hàng đó trở thành value mới.

$$
\begin{bmatrix}1&0\\0&0\end{bmatrix}
+
\begin{bmatrix}1\\0\end{bmatrix}
\begin{bmatrix}-1&1\end{bmatrix}
=
\begin{bmatrix}0&1\\0&0\end{bmatrix}.
$$

**Kết luận.** Với normalized key và full write, addressed association được thay bằng target mới.[^fast-weight-programmers-2021][^parallel-deltanet-2024]

### 6.4 Dạng erase-then-write và proof overwrite

**Trực giác.** Delta update có thể tách thành xóa prediction cũ theo key rồi ghi target mới.

**Công thức.**

$$
\boxed{S_t=(I-\beta_tk_tk_t^\top)S_{t-1}+\beta_tk_tv_t^\top}.
$$

**Ý nghĩa ký hiệu.** Rank-one matrix $k_tk_t^\top$ chọn direction cần sửa; identity giữ các directions còn lại.

**Shape flow.**

$$
(d_k,d_k)(d_k,d_v)+(d_k,1)(1,d_v)=(d_k,d_v).
$$

**Ví dụ số.** Với $k=[1,0]^\top$, projection $kk^\top$ chỉ chọn hàng đầu tiên; erase term xóa prediction ở hàng đó và write term đặt value mới vào đúng hàng.

**Kết luận.** Hai cách viết là tương đương đại số. DeltaNet cũng được diễn giải như một online gradient step trên reconstruction loss.[^parallel-deltanet-2024]

**Proof ngắn.** Nếu $k_t^\top k_t=1$ và $\beta_t=1$:

$$
\begin{aligned}
S_t^\top k_t
&=S_{t-1}^\top k_t
 +(v_t-S_{t-1}^\top k_t)(k_t^\top k_t)\\
&=v_t.
\end{aligned}
$$

Nếu một key khác $u$ trực giao với $k_t$, correction không đổi read tại $u$ vì $u^\top k_t=0$.

### 6.5 Scalar decay và channel-wise KDA

**Trực giác.** Delta correction sửa direction hiện tại; decay làm dấu vết cũ nhỏ đi trước khi correction. Scalar decay làm cả state phai cùng tốc độ, còn KDA cho mỗi key channel một tốc độ riêng.

**Công thức scalar decay.**

$$
\widetilde S_{t-1}=\alpha_tS_{t-1},
\qquad
S_t=(I-\beta_tk_tk_t^\top)\widetilde S_{t-1}+\beta_tk_tv_t^\top.
$$

**Công thức KDA.**

$$
\boxed{
S_t=(I-\beta_tk_tk_t^\top)
\operatorname{Diag}(\alpha_t)S_{t-1}
+\beta_tk_tv_t^\top
}
$$

**Ý nghĩa ký hiệu.** Trong scalar variant, $\alpha_t$ là một số cho toàn head. Trong KDA, $\alpha_t$ là vector; diagonal matrix nhân mỗi hàng state với retention riêng.[^gated-deltanet-2025][^kimi-linear-2025]

**Shape flow.**

$$
(d_k,d_k)(d_k,d_v)\to(d_k,d_v),
$$

rồi prediction, error và outer-product correction giữ nguyên shape state.

**Ví dụ số.** Với hai hàng state và decay vector $[1,0.5]$, hàng đầu được giữ nguyên, hàng hai giảm một nửa trước correction. Nếu write address chỉ hàng đầu, hàng hai vẫn phai nhưng không nhận correction mới.

**Kết luận.** Channel-wise decay tăng granularity của retention, không tạo thêm token slots. Quên giúp quản lý capacity nhưng trực tiếp làm giảm old information.

### 6.6 Interference không biến mất

**Trực giác.** Update cho key mới ảnh hưởng key cũ theo mức hai keys overlap.

**Công thức.** Với correction cho key $k_B$, thay đổi trong read tại $k_A$ là:

$$
\Delta \hat v_A
=\beta(k_A^\top k_B)(v_B-\hat v_B).
$$

**Ý nghĩa ký hiệu.** Dot product giữa hai keys đo overlap; error của B bị truyền sang read của A theo overlap này.

**Shape flow.** scalar nhân vector value tạo vector value.

**Ví dụ số.** Nếu hai normalized keys trực giao, overlap bằng không và không có collateral update. Nếu chúng giống hệt nhau, overlap bằng một và hai logical items dùng cùng address; memory không có tín hiệu để phân biệt chúng.

**Kết luận.** Delta rule sửa overwrite cho một address nhưng không biến finite state thành database vô hạn.[^fast-weight-programmers-2021]

### 6.7 Memory accounting và hybrid

**Trực giác.** Token cache thêm state cho mỗi token; KDA giữ một matrix mỗi head; hybrid cộng fixed KDA states với sequence-growing MLA cache ở một phần layers.

**Công thức tổng quát.** Với bytes mỗi số là $p$:

$$
M_{MHA}=2B\,L_{MHA}\,T\,H_{KV}\,d_h\,p,
$$

$$
M_{KDA}=B\,L_{KDA}\,H\,d_kd_v\,p,
$$

$$
M_{MLA}=B\,L_{MLA}\,T\,(d_c+d_R)\,p,
$$

$$
M_{hybrid}=M_{KDA}+M_{MLA}+M_{aux}.
$$

**Ý nghĩa ký hiệu.** Hệ số hai trong MHA đếm cả key và value; $B$ là batch size; $L$ là số layers từng loại; $H_{KV}$ và $d_h$ là số KV heads và head width; $H$ là số KDA heads; $d_c$ là latent width; $d_R$ là positional-key width nếu được cache; $p$ là bytes mỗi số. Với NoPE MLA của Kimi Linear, positional-key cache term này bằng không. Auxiliary state gồm convolution và runtime metadata.

**Shape flow.** KDA term không có $T$; MLA term có $T$.

**Ví dụ số.** Với pattern ba KDA rồi một MLA, một phần tư token-mixing layers có sequence-growing MLA cache. Đây là cơ sở accounting cho claim giảm đến 75% KV cache so với full MLA trong cấu hình report, nhưng auxiliary state và implementation có thể làm tỷ lệ bytes thực khác đi.[^kimi-linear-2025]

**Kết luận.** Hybrid giảm slope của cache, không làm total cache hằng theo context.

### 6.8 Derivation nâng cao có thể bỏ qua: gradient step

Đặt reconstruction loss tại current pair là:

$$
\mathcal L(S)=\frac12\|S^\top k_t-v_t\|_2^2.
$$

Gradient theo state:

$$
\nabla_S\mathcal L
=k_t(S^\top k_t-v_t)^\top.
$$

Một gradient-descent step với learning rate $\beta_t$ cho:

$$
S_t=S_{t-1}-\beta_t\nabla_S\mathcal L
=S_{t-1}+\beta_tk_t(v_t-S_{t-1}^\top k_t)^\top,
$$

chính là delta update.[^parallel-deltanet-2024]

## 7. Implementation — PyTorch tối thiểu

Code dưới cụ thể hóa đúng flow đã học: decay → predict → error → correct. Nó dùng FP64 và Python loop để inspect algebra; đây không phải KDA layer đầy đủ hay serving kernel.

```python
from dataclasses import dataclass
import time
import torch

DTYPE = torch.float64
ATOL = 1e-10
RTOL = 0.0


def one_hot(i: int, n: int) -> torch.Tensor:
    return torch.nn.functional.one_hot(
        torch.tensor(i), num_classes=n
    ).to(DTYPE)


@dataclass
class FixedMemory:
    d_key: int
    d_value: int

    def __post_init__(self):
        # One-head teaching state: (d_k, d_v), no sequence axis.
        self.state = torch.zeros(self.d_key, self.d_value, dtype=DTYPE)

    def read(self, query: torch.Tensor) -> torch.Tensor:
        # (d_k,) @ (d_k, d_v) -> (d_v,)
        return query @ self.state

    def additive_write(self, key: torch.Tensor, value: torch.Tensor) -> None:
        self.state = self.state + torch.outer(key, value)

    def kda_write(
        self,
        key: torch.Tensor,
        value: torch.Tensor,
        beta: float = 1.0,
        alpha: torch.Tensor | None = None,
    ) -> None:
        if alpha is None:
            alpha = torch.ones(self.d_key, dtype=DTYPE)
        if key.shape != (self.d_key,):
            raise ValueError("key shape must be (d_key,)")
        if value.shape != (self.d_value,):
            raise ValueError("value shape must be (d_value,)")
        if alpha.shape != (self.d_key,):
            raise ValueError("alpha shape must be (d_key,)")

        # Mechanism step 1: channel-wise decay.
        decayed = alpha[:, None] * self.state
        # Mechanism step 2: predict at the addressed key.
        prediction = key @ decayed
        # Mechanism step 3: compute retrieval error.
        error = value - prediction
        # Mechanism step 4: write only the gated correction.
        self.state = decayed + beta * torch.outer(key, error)

    def run_causal(
        self,
        keys: torch.Tensor,       # (T, d_k)
        values: torch.Tensor,     # (T, d_v)
        betas: torch.Tensor,      # (T,)
        alphas: torch.Tensor,     # (T, d_k)
    ) -> torch.Tensor:
        outputs = []
        for t in range(keys.shape[0]):
            self.kda_write(keys[t], values[t], float(betas[t]), alphas[t])
            outputs.append(self.read(keys[t]))
        return torch.stack(outputs)  # (T, d_v)

    @property
    def state_elements(self) -> int:
        return self.state.numel()


class TokenSlots:
    """Oracle baseline: separate slots plus latest exact-key lookup."""

    def __init__(self):
        self.slots: list[tuple[int, torch.Tensor]] = []

    def write(self, logical_key: int, value: torch.Tensor) -> None:
        self.slots.append((logical_key, value.clone()))

    def read_latest(self, logical_key: int) -> torch.Tensor:
        for key, value in reversed(self.slots):
            if key == logical_key:
                return value.clone()
        raise KeyError(logical_key)

    @property
    def value_elements(self) -> int:
        return sum(value.numel() for _, value in self.slots)
```

`TokenSlots` là oracle storage baseline, không phải softmax attention: nó được cho exact logical key và policy “latest wins”. Baseline này chỉ tách câu hỏi “evidence còn nằm trong slot không?” khỏi câu hỏi “learned attention có chọn đúng slot không?”.

Production KDA có batch/head dimensions, learned projections, convolution state, gates, normalization và chunkwise/fused kernels. Không dùng `torch.cat` cache trong toy; nếu bổ sung MLA toy, `torch.cat` chỉ là teaching implementation, không đại diện paged serving.

## 8. Verification — chạy trước benchmark

```python
@torch.inference_mode()
def test_delta_overwrite_exact():
    mem = FixedMemory(2, 2)
    key = one_hot(0, 2)
    old = one_hot(0, 2)
    new = one_hot(1, 2)
    mem.kda_write(key, old)
    mem.kda_write(key, new)
    torch.testing.assert_close(mem.read(key), new, rtol=RTOL, atol=ATOL)


@torch.inference_mode()
def test_additive_is_not_overwrite():
    mem = FixedMemory(2, 2)
    key = one_hot(0, 2)
    old = one_hot(0, 2)
    new = one_hot(1, 2)
    mem.additive_write(key, old)
    mem.additive_write(key, new)
    torch.testing.assert_close(
        mem.read(key), old + new, rtol=RTOL, atol=ATOL
    )
    assert not torch.allclose(mem.read(key), new, rtol=RTOL, atol=ATOL)


@torch.inference_mode()
def test_channel_decay_has_a_cost():
    mem = FixedMemory(2, 2)
    key_a, key_b = one_hot(0, 2), one_hot(1, 2)
    value_a, value_b = one_hot(0, 2), one_hot(1, 2)
    mem.kda_write(key_a, value_a)
    mem.kda_write(
        key_b,
        value_b,
        alpha=torch.tensor([0.5, 1.0], dtype=DTYPE),
    )
    torch.testing.assert_close(
        mem.read(key_a), 0.5 * value_a, rtol=RTOL, atol=ATOL
    )


@torch.inference_mode()
def test_collision_loses_identity():
    mem = FixedMemory(2, 2)
    same_address = one_hot(0, 2)
    value_a, value_b = one_hot(0, 2), one_hot(1, 2)
    mem.kda_write(same_address, value_a)
    mem.kda_write(same_address, value_b)
    torch.testing.assert_close(
        mem.read(same_address), value_b, rtol=RTOL, atol=ATOL
    )
    assert not torch.allclose(
        mem.read(same_address), value_a, rtol=RTOL, atol=ATOL
    )


@torch.inference_mode()
def test_state_shape_is_fixed():
    torch.manual_seed(0)
    mem = FixedMemory(8, 4)
    expected_shape = torch.Size([8, 4])
    for _ in range(100):
        key = torch.randn(8, dtype=DTYPE)
        key = key / key.norm()
        value = torch.randn(4, dtype=DTYPE)
        mem.kda_write(key, value, beta=0.5)
        assert mem.state.shape == expected_shape
    torch.testing.assert_close(
        torch.tensor(mem.state_elements),
        torch.tensor(32),
        rtol=RTOL,
        atol=ATOL,
    )


@torch.inference_mode()
def test_causal_prefix_invariance():
    torch.manual_seed(1)
    T, d = 6, 4
    keys = torch.randn(T, d, dtype=DTYPE)
    keys = keys / keys.norm(dim=-1, keepdim=True)
    values = torch.randn(T, d, dtype=DTYPE)
    betas = torch.full((T,), 0.7, dtype=DTYPE)
    alphas = torch.full((T, d), 0.99, dtype=DTYPE)

    full = FixedMemory(d, d).run_causal(keys, values, betas, alphas)
    changed_values = values.clone()
    changed_values[4:] += 100.0  # sửa future tokens
    changed = FixedMemory(d, d).run_causal(
        keys, changed_values, betas, alphas
    )
    torch.testing.assert_close(
        full[:4], changed[:4], rtol=RTOL, atol=ATOL
    )


for test in (
    test_delta_overwrite_exact,
    test_additive_is_not_overwrite,
    test_channel_decay_has_a_cost,
    test_collision_loses_identity,
    test_state_shape_is_fixed,
    test_causal_prefix_invariance,
):
    test()
    print("passed:", test.__name__)
```

Các tests dùng FP64 để kiểm chứng algebra với tolerance chặt. Khi chuyển sang FP32, BF16 hoặc chunkwise kernel, phải đặt tolerance theo dtype và đo error accumulation thay vì copy nguyên ngưỡng này.

### Verification matrix

| Test | Claim được kiểm chứng | Không chứng minh |
|---|---|---|
| delta overwrite | normalized repeated key với full write ra value mới | learned model luôn tạo đúng key/gate |
| additive baseline | additive writes tạo tổng | mọi additive architecture đều thất bại mọi task |
| decay cost | decay làm old read nhỏ đi | learned decay luôn quên sai |
| collision | cùng address không giữ hai identities | threshold capacity của model thật |
| fixed shape | state elements không tăng theo writes | total runtime memory không tăng |
| causal prefix | future values không đổi prefix outputs trong loop | chunkwise production kernel causal và numerically equivalent |

## 9. Mini-project mở rộng: capacity stress

Thí nghiệm sau thay exact collision bằng nhiều random normalized addresses. Hãy chạy nhiều seeds và báo mean/std; không hard-code một accuracy “chuẩn”.

```python
def capacity_trial(n_items: int, d_key: int, seed: int) -> float:
    g = torch.Generator().manual_seed(seed)
    keys = torch.randn(n_items, d_key, generator=g, dtype=DTYPE)
    keys = keys / keys.norm(dim=-1, keepdim=True)
    values = torch.eye(n_items, dtype=DTYPE)
    mem = FixedMemory(d_key, n_items)

    for i in range(n_items):
        mem.kda_write(keys[i], values[i])

    predictions = torch.stack([mem.read(key) for key in keys])
    return (predictions.argmax(dim=-1) == torch.arange(n_items)).double().mean().item()


for width in (8, 16, 32, 64):
    scores = [capacity_trial(64, width, seed) for seed in range(10)]
    scores_t = torch.tensor(scores, dtype=DTYPE)
    print(
        f"width={width:2d} "
        f"mean={scores_t.mean():.3f} "
        f"std={scores_t.std(unbiased=True):.3f}"
    )
```

Báo cáo mini-project nên có:

1. accuracy và MSE theo số items;
2. nhiều key widths và nhiều seeds;
3. repeated-key overwrite tách khỏi distinct-key collision;
4. recent recall tách khỏi distant recall khi dùng decay;
5. state elements theo context cho token slots và fixed state;
6. phần riêng cho algebraic guarantee và empirical observation.

## 10. Benchmark và trade-offs

### 10.1 Protocol tối thiểu

Đo riêng:

- `prefill latency` cho toàn prompt;
- `decode latency` theo ms/token sau khi prefill;
- maximum throughput ở batch sizes được ghi rõ;
- peak memory và raw state bytes;
- retrieval quality tại cùng context lengths.

Warm up kernels, synchronize accelerator trước/sau timing, báo dtype, hardware, software versions, batch size, head dimensions, chunk size và hybrid ratio. Python loop ở trên chỉ dùng để correctness; benchmark nó không đại diện KDA production.[^parallel-deltanet-2024][^kimi-linear-2025]

Một timing smoke test cho toy CPU có thể viết:

```python
@torch.inference_mode()
def toy_decode_time(n_steps: int, d: int = 64) -> float:
    torch.manual_seed(0)
    mem = FixedMemory(d, d)
    keys = torch.randn(n_steps, d, dtype=DTYPE)
    keys = keys / keys.norm(dim=-1, keepdim=True)
    values = torch.randn(n_steps, d, dtype=DTYPE)

    start = time.perf_counter()
    for t in range(n_steps):
        mem.kda_write(keys[t], values[t], beta=0.5)
    elapsed = time.perf_counter() - start
    return 1e6 * elapsed / n_steps


for steps in (128, 512, 2048):
    print(steps, toy_decode_time(steps), "microseconds/step")
```

Chỉ dùng kết quả này để phát hiện regression trong cùng environment; không dùng để so với FlashAttention hoặc claim serving speed.

### 10.2 Reported ablation của Kimi Linear

| KDA:MLA | Global MLA share trong pattern | Validation PPL | Diễn giải đúng phạm vi |
|---:|---:|---:|---|
| 0:1 | toàn bộ | 5.77 | full-MLA reference trong recipe |
| 1:1 | một nửa | 5.66 | gần 3:1 trong phép đo này |
| **3:1** | **một phần tư** | **5.65** | tốt nhất trong các ratios được báo cáo |
| 7:1 | một phần tám | 5.70 | cache slope thấp hơn, quality giảm nhẹ |
| 15:1 | một phần mười sáu | 5.82 | quá ít global retrieval trong setup này |

Bảng là author-reported result cho cấu hình và training recipe cụ thể; không có uncertainty đủ để coi chênh lệch rất nhỏ là universal ranking.[^kimi-linear-2025]

### 10.3 Bảng quyết định

| Workload | Lựa chọn khởi đầu | Measurement quyết định |
|---|---|---|
| exact copy, source lookup | MLA/softmax hoặc hybrid nhiều global layers | exact-match recall theo distance |
| long streaming state tracking | KDA-heavy hybrid | state accuracy, drift, decode memory |
| context ngắn | baseline attention trước | end-to-end latency, không chỉ FLOPs |
| memory-constrained long context | hybrid | peak bytes và quality tại cùng budget |
| checkpoint softmax có sẵn | giữ baseline hoặc migration có retraining | recovery quality và training cost |
| unknown workload | ablate full MLA, pure KDA và vài hybrid ratios | Pareto quality-memory-latency |

## 11. Debug checklist

| Triệu chứng | Nguyên nhân khả dĩ | Check đầu tiên |
|---|---|---|
| overwrite không ra value mới | key chưa normalized, write gate không full hoặc prediction sai thứ tự | in key norm, beta và prediction |
| state có sequence axis | đang lưu mọi intermediate state hoặc token writes | state phải chỉ có batch/head/key/value axes |
| old fact biến mất quá nhanh | decay quá mạnh hoặc gate saturation | histogram decay theo channel và distance |
| entities nhiễm lẫn nhau | learned keys overlap | cosine similarity và collateral-update test |
| future token đổi prefix output | implementation không causal | prefix-invariance test trước benchmark |
| recurrent và chunkwise lệch | mask, cumulative decay hoặc numerical order sai | FP64 reference trên sequence ngắn |
| memory vẫn tăng nhanh | MLA/conv/allocator state chưa được tính | memory ledger theo từng layer type |
| latency không cải thiện | kernel overhead hoặc bottleneck khác | profile prefill/decode và memory bandwidth riêng |
| benchmark ratio quá đẹp | trộn batch-one latency với max throughput | ghi rõ concurrency và objective |
| gọi toy là KDA đầy đủ | thiếu projections, conv, gates hoặc output path | đối chiếu production block components |

## 12. Giới hạn và bước tiếp theo

Lab này chứng minh một số tính chất đại số của toy recurrence, không chứng minh:

- quality parity giữa KDA, MLA và softmax attention;
- context một triệu token đồng nghĩa reliable retrieval ở mọi vị trí;
- 3:1 tối ưu cho model, data hoặc hardware khác;
- Python loop phản ánh chunkwise/fused kernel speed;
- channel-wise decay luôn học semantic forgetting đúng;
- token cache tự động cho exact retrieval;
- fixed-state chứa vô hạn information.

Học tiếp:

1. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — recurrence và các biến thể mới hơn.
2. [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md) — cách recurrence được re-express cho GPU.
3. [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — architecture và reported evidence đầy đủ.
4. [Multi-head Latent Attention](multi-head-latent-attention.md) — token-addressable latent cache.
5. [DeltaNet evaluation and hybrid-attention trade-offs](deltanet-evaluation-and-hybrid-attention-trade-offs.md) và [Gated DeltaNet evaluation](gated-deltanet-evaluation-and-hybrid-trade-offs.md) — quality evidence và giới hạn.

## Relationships

- **Depends on:** [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) — nền tảng state layout và interference.
- **Depends on:** [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md) — baseline nén per-token nhưng vẫn giữ sequence axis.
- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — targeted correction và learned decay.
- **Uses:** [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md) — execution strategy cho training/prefill.
- **Explains:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) — pattern layerwise KDA–MLA và retrieval-memory trade-off.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — token-addressable state thay vì fixed recurrent state.
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng mini-project overwrite, decay, collision và causality.

## Evidence limits

Delta update, orthogonality argument và associative-memory framing đến từ primary fast-weight/DeltaNet papers. Scalar decay đến từ Gated DeltaNet; channel-wise KDA recurrence, layerwise 3:1 hybrid, ratio ablation và efficiency measurements đến từ Kimi Linear. Các benchmark đều là author-run evidence và chưa được độc lập tái lập trong repository. Mental models, support-ticket scenario, oracle token-slot baseline, code organization và tests là pedagogical synthesis: chúng làm rõ representation trade-off nhưng không dự đoán trực tiếp perplexity, long-context benchmark score hay production latency.[^fast-weight-programmers-2021][^parallel-deltanet-2024][^gated-deltanet-2025][^kimi-linear-2025]

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4 and Appendices A–B.
[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–5 and derivation appendices.
[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5 and Appendix A.
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 2–6 and chunkwise derivation appendices.
