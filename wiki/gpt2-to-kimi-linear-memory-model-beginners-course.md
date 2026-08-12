---
type: Synthesis
title: "GPT-2 → Kimi Linear: changing the memory model — khóa học cho người mới"
description: A beginner-first course tracing token-addressable softmax attention and growing KV cache through fixed-state linear memory, delta correction, scalar and channel-wise decay, chunkwise training, and periodic MLA in Kimi Linear.
tags: [gpt-2, kimi-linear, kv-cache, linear-attention, deltanet, gated-deltanet, kda, mla, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T13:55:19+07:00
sources:
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
  - id: kv-caching-explained
    resource: ../raw/KVCachinginLLMsClearlyExplained.md
    title: "KV Caching in LLMs, Clearly Explained"
  - id: fast-weight-programmers-2021
    resource: ../raw/arXiv-2102.11174v3/main.tex
    title: "Linear Transformers Are Secretly Fast Weight Programmers"
  - id: parallel-deltanet-2024
    resource: ../raw/arXiv-2406.06484v6/neurips_2024.tex
    title: "Parallelizing Linear Transformers with the Delta Rule over Sequence Length"
  - id: gated-deltanet-2025
    resource: ../raw/arXiv-2412.06464v3/main.tex
    title: "Gated Delta Networks: Improving Mamba2 with Delta Rule"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: kimi-linear-2025
    resource: ../raw/arXiv-2510.26692v2/main.tex
    title: "Kimi Linear: An Expressive, Efficient Attention Architecture"
---

# GPT-2 → Kimi Linear: changing the memory model — khóa học cho người mới

Con đường từ GPT-2 đến Kimi Linear không đơn thuần là thay một `attention layer` bằng một equation nhanh hơn. Thay đổi cốt lõi nằm ở **memory model**: GPT-2-style softmax attention giữ một K/V entry riêng cho từng token, trong khi linear attention nén history vào một fixed-size matrix state. DeltaNet bổ sung `correction`, Gated DeltaNet bổ sung `scalar decay`, Kimi Delta Attention (KDA) nâng decay thành `channel-wise decay`, rồi Kimi Linear định kỳ chèn global MLA để lấy lại `token-addressable retrieval`. Mỗi bước giải quyết một bottleneck nhưng đồng thời tạo trade-off mới.[^radford-gpt-2-2019][^fast-weight-programmers-2021][^gated-deltanet-2025][^kimi-linear-2025]

> [!success] Learning outcomes
> Sau bài này, bạn có thể:
> - phân biệt `token-addressable memory` với `fixed-state associative memory`;
> - giải thích vì sao KV cache giảm recomputation nhưng vẫn tăng theo context length;
> - suy ra linear-attention recurrence từ một separable kernel;
> - đọc và chú thích recurrence của additive memory, DeltaNet, Gated DeltaNet và KDA;
> - giải thích riêng vai trò của `delta correction`, `scalar decay` và `channel-wise decay`;
> - phân biệt recurrent `decode` với chunkwise-parallel `training/prefill`;
> - giải thích vì sao Kimi Linear vẫn giữ periodic global MLA;
> - chạy một PyTorch lab để kiểm tra overwrite, interference và state growth.

## 1. Prerequisites và câu hỏi trung tâm

Nên học trước:

1. [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md);
2. [Attention: beginner's guide](attention-beginner-guide.md);
3. [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md);
4. [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md).

Câu hỏi xuyên suốt bài học là:

> Sau khi model đọc token, information của token đó được giữ ở đâu, state tăng thế nào, và query tương lai có thể truy cập information đó bằng cách nào?

Đừng chỉ hỏi complexity là $O(T^2)$ hay $O(T)$. Cần tách bốn dimensions:

| Dimension | Câu hỏi |
|---|---|
| `State size` | Persistent state có tăng theo context length $T$ không? |
| `Addressability` | Query còn chấm điểm từng token slot hay chỉ đọc state đã gộp? |
| `Update semantics` | Write mới chỉ cộng thêm, sửa association cũ, hay chủ động quên? |
| `Execution regime` | Cơ chế chạy ra sao trong training, prefill và one-token decode? |

## 2. Điểm xuất phát: GPT-2-style causal softmax attention

GPT-2 dùng decoder-only causal Transformer. Mỗi block có masked multi-head self-attention, FFN, residual connections và pre-layer normalization; report gốc dùng learned positional embeddings và context 1,024 tokens.[^radford-gpt-2-2019]

Ở một attention head, output tại position $t$ là:

$$
o_t=\sum_{i=1}^{t}a_{t,i}v_i,
\qquad
a_{t,i}=\frac{\exp(q_t^Tk_i/\sqrt{d_k})}
{\sum_{j=1}^{t}\exp(q_t^Tk_j/\sqrt{d_k})}.
$$

Causal mask chỉ cho phép $i\le t$. Điểm quan trọng về memory không phải chỉ là softmax, mà là sequence axis vẫn còn nguyên:

```text
position:   1       2       3                T
cache:    (k1,v1) (k2,v2) (k3,v3) ...     (kT,vT)
query qT:   ↓score   ↓score   ↓score          ↓score
```

Mỗi retained token có K/V slot riêng. Vì thế softmax attention là `token-addressable`: query mới có thể tạo score riêng cho từng token cũ. Điều này **không bảo đảm** model luôn retrieve đúng; nó chỉ bảo toàn các candidate slots riêng để retrieval mechanism lựa chọn.

### 2.1 Không có KV cache: recomputation

Trong naive autoregressive generation, khi prefix tăng từ $T$ lên $T+1$, model có thể tính lại Q/K/V cho toàn prefix. Các K/V cũ không đổi nên đây là redundant work.

### 2.2 Có KV cache: compute tốt hơn, memory lớn dần

KV caching giữ K/V cũ và mỗi decode step chỉ append K/V của token mới:[^kv-caching-explained]

```text
prefill: [prompt tokens] → compute all prompt K/V → initialize cache
decode:  [new token]     → append one K/V       → query full cache
```

Bỏ qua batch, layer và head factors, cache của một head có số elements:

$$
M_{KV}(T)=T(d_k+d_v)=O(T).
$$

Một query decode mới vẫn tương tác với $T$ cached keys và values. KV cache vì vậy đổi **recomputation lấy persistent memory**; nó không làm history thành fixed-size.

> [!warning] Hai câu dễ nhầm
> - “Full attention có quadratic full-sequence interaction” nói về training/prefill với nhiều queries.
> - “Cached decode không tính lại toàn prefix” nói về one-token generation.
>
> Cached decode vẫn đọc growing history, còn cache vẫn tăng tuyến tính theo $T$.

## 3. Bước ngoặt: đổi từ token slots sang fixed-state memory

### 3.1 Từ attention kernel đến separable feature map

Viết một normalized attention kernel tổng quát:

$$
o_t=
\frac{\sum_{i\le t}\kappa(q_t,k_i)v_i}
{\sum_{i\le t}\kappa(q_t,k_i)}.
$$

Linear attention chọn hoặc xấp xỉ kernel có thể factorize:

$$
\kappa(q,k)=\phi(q)^T\phi(k).
$$

Khi đó tử số có thể đổi thứ tự nhân:

$$
\sum_{i\le t}\left(\phi(q_t)^T\phi(k_i)\right)v_i
=
\phi(q_t)^T\left(\sum_{i\le t}\phi(k_i)v_i^T\right).
$$

Đặt:

$$
S_t=\sum_{i\le t}\phi(k_i)v_i^T,
\qquad
z_t=\sum_{i\le t}\phi(k_i).
$$

Ta có recurrence:

$$
S_t=S_{t-1}+\phi(k_t)v_t^T,
\qquad
z_t=z_{t-1}+\phi(k_t),
$$

và read:

$$
o_t=
\frac{\phi(q_t)^TS_t}
{\phi(q_t)^Tz_t+\varepsilon}.
$$

Nếu feature width là $m$, state có shape $S_t\in\mathbb{R}^{m\times d_v}$ và $z_t\in\mathbb{R}^{m}$. Shape không chứa $T$.

### 3.2 Memory model đã thay đổi như thế nào?

| Thuộc tính | Softmax + KV cache | Fixed-state linear memory |
|---|---|---|
| Persistent history | K/V slot cho mỗi token | một matrix state dùng chung |
| Sequence axis trong state | Có | Không |
| State growth theo $T$ | $O(T(d_k+d_v))$ | $O(md_v+m)$ |
| Query operation | chấm từng retained key | nhân với state đã tổng hợp |
| Direct token-level selection | structurally available | không còn được bảo đảm |
| Rủi ro chính | cache capacity và bandwidth | superposition và interference |

Cách nhìn `fast-weight programmer` coi $S_t$ như một weight matrix được sequence “lập trình” nhanh bằng outer-product writes.[^fast-weight-programmers-2021]

> [!important] Fixed-state không có nghĩa infinite memory
> Shape không tăng theo $T$ chỉ bảo đảm bounded state storage. Nó không bảo đảm state giữ lossless mọi token, exact recall vô hạn, hay end-to-end latency không phụ thuộc workload.

## 4. Vấn đề của additive write: superposition không có overwrite

Xét unnormalized associative state:

$$
S_t=S_{t-1}+k_tv_t^T,
\qquad
o_t=S_t^Tq_t.
$$

Nếu cùng unit key $k$ lần lượt được ghi với $v_{old}$ rồi $v_{new}$:

$$
S=kv_{old}^T+kv_{new}^T.
$$

Read bằng $k$ cho:

$$
S^Tk=v_{old}+v_{new}.
$$

Memory không biết write thứ hai có nghĩa “replace old value”. Normalization có thể tạo mixture, nhưng vẫn không tự tạo `latest value wins`.

### 4.1 Interference giữa keys

Với hai associations:

$$
S=k_Av_A^T+k_Bv_B^T,
$$

read tại $k_A$ là:

$$
S^Tk_A
=\|k_A\|^2v_A+(k_B^Tk_A)v_B.
$$

Nếu keys không orthogonal, $v_B$ rò vào result. Mapped keys có thể được học để giảm collision, nhưng finite-dimensional state không tạo ra vô hạn orthogonal addresses. Trong phân tích interference-free của fast-weight paper, số associations có mapped keys mutually orthogonal không thể vượt feature dimension; đây là capacity bound trong giả định lý tưởng, không phải mốc token mà model chắc chắn quên.[^fast-weight-programmers-2021]

## 5. DeltaNet: sửa association thay vì cộng vô hạn

### 5.1 Suy ra delta correction từ retrieval error

Prediction hiện tại tại key $k_t$ là:

$$
\hat v_t=S_{t-1}^Tk_t.
$$

Error cần sửa:

$$
e_t=v_t-\hat v_t.
$$

Thay vì write toàn bộ $v_t$, delta rule chỉ write error:

$$
S_t=S_{t-1}+\beta_tk_te_t^T.
$$

Khai triển:

$$
\boxed{
S_t=(I-\beta_tk_tk_t^T)S_{t-1}
+\beta_tk_tv_t^T.
}
$$

Đây cũng là một online gradient step trên reconstruction loss $\tfrac12\|S^Tk_t-v_t\|^2$.[^parallel-deltanet-2024]

### 5.2 Chú thích từng transition

```text
current state S_{t-1}
  ↓ read with k_t
current prediction v_hat
  ↓ compare with target v_t
error = v_t - v_hat
  ↓ scale by beta_t and address with k_t
correction = beta_t * outer(k_t, error)
  ↓
new state S_t
```

Vai trò của $\beta_t\in[0,1]$:

- $\beta_t=0$: bỏ qua write;
- $0<\beta_t<1$: partial correction;
- $\beta_t=1$: full correction theo addressed direction nếu key normalized.

Với $\|k_t\|=1$ và $\beta_t=1$:

$$
S_t^Tk_t=v_t.
$$

Nếu một key khác $u$ orthogonal với $k_t$, correction không đổi read tại $u$. Nếu $u^Tk_t\ne0$, collateral interference vẫn tồn tại. Delta rule cải thiện update semantics nhưng không biến shared matrix thành database vô hạn.

## 6. Parallel DeltaNet: recurrence đúng nhưng training không nên chạy Python loop

DeltaNet có dependency qua state:

$$
S_1\rightarrow S_2\rightarrow\cdots\rightarrow S_T.
$$

Direct recurrent execution rất tự nhiên cho decode vì mỗi step chỉ có một token. Nhưng chạy toàn sequence token-by-token khi training sẽ không tận dụng tốt GPU.

Parallel DeltaNet nhóm sequence thành chunks. Bên trong mỗi chunk, products của các rank-one transitions được biểu diễn compact bằng `WY representation`; một lower-triangular `UT transform` đưa phần lớn work về batched matrix multiplication. State cuối chunk vẫn truyền recurrent sang chunk sau.[^parallel-deltanet-2024]

```text
chunk 0              chunk 1              chunk 2
[token ... token] → S_C → [token ... token] → S_2C → ...
  intra-chunk matmul          intra-chunk matmul

cross-chunk: recurrent
within chunk: mostly parallel
```

Điều cần ghi nhớ:

- chunkwise form là exact re-expression của recurrence được nêu, không phải approximate model khác;
- sequential depth giảm từ token count xuống chunk count nếu chưa dùng thêm scan;
- đây không phải fully sequence-parallel algorithm;
- kernel speed phụ thuộc head width, chunk size, precision và hardware.

## 7. Gated DeltaNet: thêm scalar decay để quên rộng

Delta correction chỉ sửa direction được current key address. State vẫn có thể chứa stale information ở các directions khác. Gated DeltaNet thêm learned scalar $\alpha_t\in(0,1)$:[^gated-deltanet-2025]

$$
\boxed{
S_t=
\alpha_t(I-\beta_tk_tk_t^T)S_{t-1}
+\beta_tk_tv_t^T.
}
$$

Có thể đọc thành hai bước:

$$
\widetilde S_{t-1}=\alpha_tS_{t-1},
$$

$$
S_t=(I-\beta_tk_tk_t^T)\widetilde S_{t-1}
+\beta_tk_tv_t^T.
$$

Hai controls không thay thế nhau:

| Control | Scope | Chức năng |
|---|---|---|
| $\beta_t$ + delta correction | direction được $k_t$ address | quyết định mức sửa association hiện tại |
| scalar $\alpha_t$ | toàn state của head | broad forgetting / capacity clearing |

Decay tạo trade-off:

- $\alpha_t$ gần 1: retention dài hơn nhưng stale interference tồn tại lâu;
- $\alpha_t$ nhỏ: dọn state nhanh hơn nhưng long-range information mất nhanh hơn.

Gated DeltaNet mở rộng chunkwise WY/UT algorithm bằng decay-aware scaling. Equation tương đương không tự bảo đảm numerical stability hay end-to-end speed trên mọi hardware.[^gated-deltanet-2025]

## 8. KDA: từ scalar decay đến channel-wise decay

Kimi Delta Attention thay một scalar bằng vector:

$$
\alpha_t\in[0,1]^{d_k}.
$$

KDA recurrence là:[^kimi-linear-2025]

$$
\boxed{
S_t=
(I-\beta_tk_tk_t^T)
\operatorname{Diag}(\alpha_t)S_{t-1}
+\beta_tk_tv_t^T,
\qquad
o_t=S_t^Tq_t.
}
$$

### 8.1 Đọc equation theo đúng thứ tự

1. **Channel-wise decay**:

   $$D_t=\operatorname{Diag}(\alpha_t),
   \qquad
   \widetilde S_{t-1}=D_tS_{t-1}.$$

2. **Read old association after decay**:

   $$\hat v_t=\widetilde S_{t-1}^Tk_t.$$

3. **Compute correction**:

   $$e_t=v_t-\hat v_t.$$

4. **Write correction**:

   $$S_t=\widetilde S_{t-1}+\beta_tk_te_t^T.$$

Dạng cuối tương đương recurrence đóng hộp ở trên. Một implementation dễ đọc là:

```python
decayed = alpha[:, None] * state
prediction = key @ decayed
error = value - prediction
state = decayed + beta * torch.outer(key, error)
output = query @ state
```

### 8.2 Channel-wise control thêm gì?

Scalar Gated DeltaNet buộc mọi key channels trong một head dùng cùng retention rate ở step $t$. KDA có thể giữ một số channels lâu hơn và decay các channels khác nhanh hơn, tùy input.

Đây là **expressive control**, không phải guarantee rằng mỗi channel tự động học một semantic timescale hữu ích. Behavior cuối cùng còn phụ thuộc data, optimization và toàn block.

### 8.3 KDA layer thật nhiều hơn recurrence

Trong Kimi Linear report, mỗi head dùng $d_k=d_v=128$. Q/K đi qua projection, `ShortConv`, `Swish` và L2 normalization; V không dùng L2 normalization. $\alpha_t$ dùng low-rank projection và decay function, $\beta_t$ dùng sigmoid. KDA output còn đi qua head-wise RMSNorm, data-dependent output gate và output projection.[^kimi-linear-2025]

Vì vậy toy recurrence mô tả memory core, không phải drop-in reproduction của production KDA block.

### 8.4 Constrained DPLR và hardware co-design

Transition của KDA có thể viết:

$$
A_t=
(I-\beta_tk_tk_t^T)\operatorname{Diag}(\alpha_t),
\qquad
S_t=A_tS_{t-1}+\beta_tk_tv_t^T.
$$

Đây là một constrained `Diagonal-Plus-Low-Rank` transition: diagonal decay cộng một key-tied rank-one correction. Việc ràng buộc low-rank factors theo key cho phép KDA factor decay rồi dùng Householder/WY-style update. Report cho rằng thiết kế này bỏ bớt secondary chunking và matrix multiplications so với general DPLR path của họ; đó là implementation-specific author evidence, không phải chứng minh mọi KDA kernel nhanh hơn mọi DPLR implementation.[^kimi-linear-2025]

## 9. Ba execution regimes: training, prefill và decode

Cùng một mathematical recurrence có thể có nhiều execution forms:

| Regime | Input shape điển hình | KDA execution | State behavior | Bottleneck chính |
|---|---|---|---|---|
| `training` | nhiều tokens, forward + backward | chunkwise WY/UT | carried state qua chunks; lưu/recompute activations | matmul throughput, activation memory, backward |
| `prefill` | toàn prompt | chunkwise-parallel | tạo final recurrent state cho KDA layers | prompt work và chunk kernels |
| `decode` | một token mới mỗi step | direct recurrent update | update fixed $d_k\times d_v$ state | weight/state reads và small-kernel efficiency |

Với global attention:

| Regime | Softmax/MLA behavior |
|---|---|
| `training` | causal token-pair interactions trên sequence |
| `prefill` | xử lý prompt và tạo per-token cache |
| `decode` | query cache rồi append entry mới |

> [!note] Algorithm và kernel là hai lớp khác nhau
> KDA đổi memory representation và recurrence. Chunkwise KDA đổi cách execute recurrence trên GPU. Không nên dùng kernel benchmark để suy ra quality, hoặc dùng quality benchmark để chứng minh kernel speed.

Kimi Linear report cho KDA-head attention FLOPs theo sequence length $T$, chunk size $C$ và head width $d_h$ là:

$$
6Td_h^2+3TCd_h+TC^2,
$$

trong khi global attention có dominant term $2T^2d_h$. Công thức cho thấy vì sao KDA hấp dẫn khi $T$ lớn và $C,d_h$ cố định, nhưng wall-clock còn phụ thuộc implementation và hardware.[^kimi-linear-2025]

## 10. Tại sao KDA vẫn chưa đủ cho mọi retrieval?

KDA quản lý fixed state tốt hơn additive linear attention:

- delta correction hỗ trợ overwrite theo addressed key;
- channel-wise decay tạo learned forgetting chi tiết;
- recurrent state không tăng theo context.

Nhưng KDA vẫn bắt mọi history đi qua fixed number of state elements. Khi nhiều associations dùng overlapping addresses, information có thể interfere. Một query không thể quay lại chấm điểm riêng tất cả token slots vì sequence axis đã bị nén mất.

Long-context workload thường cần cả hai dạng operation:

1. **Summarize/update state**: ví dụ giữ running topic, syntax state hoặc accumulated evidence.
2. **Retrieve a specific item**: ví dụ copy chính xác identifier xuất hiện rất xa, chọn một line trong repository, hoặc tìm một occurrence cụ thể.

Fixed-state recurrence hợp với operation thứ nhất. Token-addressable global attention cung cấp structural path tốt hơn cho operation thứ hai.

## 11. Periodic MLA: lấy lại global token retrieval

MLA vẫn là token-addressable softmax attention, nhưng mỗi token cache một compressed joint KV latent thay vì full per-head K/V. Cache của MLA nhỏ hơn theo mỗi token nhưng vẫn tăng tuyến tính theo $T$.[^deepseek-v2-2024]

Kimi Linear dùng layerwise pattern:[^kimi-linear-2025]

```text
Layer 1: KDA         fixed-state sequence memory
Layer 2: KDA         fixed-state sequence memory
Layer 3: KDA         fixed-state sequence memory
Layer 4: global MLA  compressed token-addressable retrieval
                    ↓ repeat through depth
```

> [!important] “Periodic” theo depth, không theo token
> Pattern `3:1` không có nghĩa cứ ba tokens mới chạy MLA. Mọi token đi qua mọi layers; toàn MLA layer xuất hiện sau ba KDA layers khi representation đi lên network depth.

### 11.1 Hai pathways bổ sung nhau

| KDA pathway | MLA pathway |
|---|---|
| fixed-size recurrent state | compressed entry cho mỗi token |
| history được learned compression | retained tokens vẫn được score riêng |
| cheap state growth khi decode | direct global retrieval |
| correction + channel-wise forgetting | giữ token-level candidate slots |
| có interference/capacity pressure | cache và reads tăng theo context |

Kimi Linear chọn whole-layer hybrid thay vì trộn KDA/MLA heads trong cùng layer vì report cho rằng layerwise design đơn giản hơn về infrastructure và ổn định training hơn trong recipe của họ.[^kimi-linear-2025]

### 11.2 Vì sao ratio là 3:1?

Trong ablation được report:

| KDA:MLA | Validation perplexity |
|---:|---:|
| 3:1 | 5.65 |
| 1:1 | 5.66 |
| 7:1 | 5.70 |
| 15:1 | 5.82 |
| 0:1, full MLA | 5.77 |

3:1 tốt nhất trong configurations và training recipe đã test. Chênh lệch 3:1 với 1:1 rất nhỏ, nên không được biến 3:1 thành universal law.

Vì chỉ một phần tư token-mixing layers giữ sequence-growing MLA cache, report nêu claim “up to 75% KV-cache reduction” so với full MLA. Đây là architecture/configuration claim; total runtime memory vẫn gồm periodic MLA cache, KDA states, short-convolution states, weights, allocator metadata và workspaces.[^kimi-linear-2025]

### 11.3 NoPE trong MLA layers

Kimi Linear dùng NoPE cho global MLA layers và giao positional/recency role cho KDA transitions. Report nêu hai practical motivations: NoPE MLA có thể chuyển thành pure MQA ở inference và context extension không cần retune RoPE parameters.[^kimi-linear-2025]

Không nên suy ra rằng:

- NoPE luôn tốt hơn RoPE;
- KDA đã chứng minh universal position extrapolation;
- bỏ position encoding khỏi một arbitrary Transformer sẽ cho cùng behavior.

Đây là assignment of responsibility của toàn hybrid architecture.

## 12. Bảng tiến hóa của memory model

| Bước | State update / storage | Vấn đề giải quyết | Vấn đề còn lại |
|---|---|---|---|
| GPT-2 softmax | giữ $(k_i,v_i)$ theo token | direct token-addressable retrieval | full-sequence attention cost; serving cache tăng theo $T$ |
| KV caching | append K/V, không recompute K/V cũ | redundant decode projections | cache và per-step history read vẫn tăng |
| Additive linear memory | $S_t=S_{t-1}+k_tv_t^T$ | fixed-size recurrent state | no overwrite; interference |
| DeltaNet | read old value rồi write error | key-addressed correction | stale state ngoài addressed direction |
| Gated DeltaNet | scalar decay + correction | broad learned forgetting | mọi channels cùng decay rate |
| KDA | channel-wise decay + correction | fine-grained retention control | fixed-state retrieval/capacity limit |
| Kimi Linear | 3 KDA + 1 global MLA | kết hợp bounded state với periodic token retrieval | một phần cache vẫn tăng; hybrid complexity |

## 13. Runnable PyTorch lab

Lab này kiểm tra **memory semantics**, không reproduce Kimi Linear và không benchmark production kernels.

### 13.1 Code

```python
from __future__ import annotations

import math
from dataclasses import dataclass

import torch


torch.set_default_dtype(torch.float64)


def causal_softmax_attention(q, k, v):
    """Parallel reference. q/k: [T, Dk], v: [T, Dv]."""
    scores = q @ k.T / math.sqrt(k.shape[-1])
    causal = torch.triu(
        torch.ones_like(scores, dtype=torch.bool), diagonal=1
    )
    weights = torch.softmax(scores.masked_fill(causal, -torch.inf), dim=-1)
    return weights @ v


class SoftmaxKVCache:
    """One-head decode cache; keeps every token slot."""

    def __init__(self):
        self.keys = []
        self.values = []

    def step(self, q_t, k_t, v_t):
        self.keys.append(k_t.clone())
        self.values.append(v_t.clone())
        keys = torch.stack(self.keys)
        values = torch.stack(self.values)
        weights = torch.softmax(
            (keys @ q_t) / math.sqrt(q_t.numel()), dim=0
        )
        return weights @ values

    @property
    def state_elements(self):
        return sum(x.numel() for x in self.keys + self.values)


@dataclass
class MatrixMemory:
    d_key: int
    d_value: int

    def __post_init__(self):
        self.state = torch.zeros(self.d_key, self.d_value)

    def read(self, query):
        return query @ self.state

    def additive_step(self, query, key, value):
        self.state = self.state + torch.outer(key, value)
        return self.read(query)

    def delta_step(self, query, key, value, beta=1.0):
        prediction = key @ self.state
        error = value - prediction
        self.state = self.state + beta * torch.outer(key, error)
        return self.read(query)

    def gated_delta_step(self, query, key, value, alpha, beta=1.0):
        # alpha may be a scalar (Gated DeltaNet) or [Dk] (KDA).
        if torch.as_tensor(alpha).ndim == 0:
            decayed = alpha * self.state
        else:
            if alpha.shape != (self.d_key,):
                raise ValueError("channel-wise alpha must have shape [d_key]")
            decayed = alpha[:, None] * self.state

        prediction = key @ decayed
        error = value - prediction
        self.state = decayed + beta * torch.outer(key, error)
        return query @ self.state

    @property
    def state_elements(self):
        return self.state.numel()


def one_hot(index, size):
    return torch.nn.functional.one_hot(
        torch.tensor(index), num_classes=size
    ).to(torch.get_default_dtype())


# ------------------------------------------------------------
# Test 1: cached one-token softmax equals parallel causal output.
# ------------------------------------------------------------
torch.manual_seed(7)
T, Dk, Dv = 8, 4, 3
q = torch.randn(T, Dk)
k = torch.randn(T, Dk)
v = torch.randn(T, Dv)

parallel = causal_softmax_attention(q, k, v)
cache = SoftmaxKVCache()
cached = torch.stack([cache.step(q[t], k[t], v[t]) for t in range(T)])
assert torch.allclose(parallel, cached, atol=1e-12, rtol=0.0)
print("T1 softmax: parallel == cached decode")
print("   cached elements:", cache.state_elements)  # T * (Dk + Dv)


# ------------------------------------------------------------
# Test 2: additive write fails latest-value overwrite.
# ------------------------------------------------------------
key = one_hot(0, 4)
old_value = one_hot(0, 3)
new_value = one_hot(1, 3)

additive = MatrixMemory(4, 3)
additive.additive_step(key, key, old_value)
additive_result = additive.additive_step(key, key, new_value)

corrective = MatrixMemory(4, 3)
corrective.delta_step(key, key, old_value, beta=1.0)
delta_result = corrective.delta_step(key, key, new_value, beta=1.0)

print("T2 additive read:", additive_result.tolist())  # [1, 1, 0]
print("   delta read:   ", delta_result.tolist())     # [0, 1, 0]
assert not torch.allclose(additive_result, new_value)
assert torch.allclose(delta_result, new_value)


# ------------------------------------------------------------
# Test 3: non-orthogonal addresses cause collateral interference.
# ------------------------------------------------------------
a = torch.tensor([1.0, 0.0])
b = torch.tensor([0.8, 0.6])  # unit norm but overlaps with a
value_a = torch.tensor([1.0, 0.0])
value_b = torch.tensor([0.0, 1.0])

memory = MatrixMemory(2, 2)
memory.delta_step(a, a, value_a)
before = memory.read(a).clone()
memory.delta_step(b, b, value_b)
after = memory.read(a)
print("T3 read(a) before writing b:", before.tolist())
print("   read(a) after writing b: ", after.tolist())
assert not torch.allclose(before, after)


# ------------------------------------------------------------
# Test 4: scalar versus channel-wise decay.
# ------------------------------------------------------------
base = torch.tensor([[10.0, 0.0], [0.0, 10.0]])
zero_key = torch.zeros(2)      # isolate decay; no addressed correction
zero_value = torch.zeros(2)

scalar = MatrixMemory(2, 2)
scalar.state = base.clone()
scalar.gated_delta_step(
    zero_key, zero_key, zero_value, alpha=torch.tensor(0.5)
)

channel = MatrixMemory(2, 2)
channel.state = base.clone()
channel.gated_delta_step(
    zero_key,
    zero_key,
    zero_value,
    alpha=torch.tensor([0.9, 0.1]),
)

print("T4 scalar-decayed state:\n", scalar.state)
print("   channel-decayed state:\n", channel.state)
assert torch.allclose(scalar.state, torch.tensor([[5.0, 0.0], [0.0, 5.0]]))
assert torch.allclose(channel.state, torch.tensor([[9.0, 0.0], [0.0, 1.0]]))


# ------------------------------------------------------------
# Test 5: growing cache versus fixed matrix state.
# ------------------------------------------------------------
for length in [1, 16, 256, 4096]:
    kv_elements = length * (Dk + Dv)
    fixed_elements = Dk * Dv
    print(
        f"T={length:4d} | KV={kv_elements:6d} elements "
        f"| fixed={fixed_elements:3d} elements"
    )
```

Expected key observations:

```text
T1 softmax: parallel == cached decode
T2 additive read: [1.0, 1.0, 0.0]
   delta read:    [0.0, 1.0, 0.0]
T3 read(a) changes after writing overlapping key b
T4 scalar decay treats both rows equally; channel decay does not
T5 KV elements grow with T; fixed matrix element count does not
```

### 13.2 Lab này chứng minh và không chứng minh điều gì?

**Chứng minh trong toy setup:**

- causal softmax parallel form và cached one-token decode có cùng semantics;
- additive memory không implement overwrite cho repeated key;
- delta correction overwrite được normalized key trong ideal case;
- overlapping keys gây collateral interference;
- channel-wise gate có control chi tiết hơn scalar gate;
- matrix state shape không tăng theo number of writes.

**Không chứng minh:**

- KDA production model luôn recall tốt hơn softmax attention;
- fixed-state model có infinite capacity;
- Python loop phản ánh GPU throughput;
- toy `alpha`, `beta`, keys và values giống learned distributions;
- Kimi Linear benchmark gains do riêng KDA recurrence gây ra.

## 14. Bài tập mở rộng

### Exercise 1 — capacity stress

Tạo $N>d_k$ random normalized keys, ghi random one-hot values bằng delta rule, rồi đo mean squared retrieval error khi $N$ tăng. Lặp lại với orthogonal keys khi $N\le d_k$.

**Câu hỏi:** error tăng do number of writes hay do key overlap? Hai yếu tố liên quan thế nào?

### Exercise 2 — retention horizon

Ghi một association, sau đó chạy 100 steps với scalar $\alpha=0.99$, $0.95$, $0.8$. Vẽ norm của retrieved value theo step.

**Câu hỏi:** half-life của information thay đổi ra sao? Learned decay phải cân bằng retention và capacity như thế nào?

### Exercise 3 — mixed channel timescales

Dùng $\alpha=[0.999,0.99,0.9,0.5]$ và khởi tạo state khác 0 ở mọi rows. Vẽ norm từng row. Đây chỉ là controlled illustration; đừng gọi rows là “semantic channels” nếu chưa có evidence từ trained model.

### Exercise 4 — annotate a macrocycle

Vẽ pattern `KDA → KDA → KDA → MLA`, rồi với mỗi layer ghi:

- persistent state shape;
- state có sequence axis hay không;
- one-token decode append hay update;
- query có thể score từng past token hay không.

### Exercise 5 — evidence ledger

Tạo bảng bốn cột:

| Mechanism | Replaced baseline | Expected trade-off | Evidence needed |
|---|---|---|---|
| KDA recurrence | full attention ở phần lớn layers | bounded state ↔ interference | recurrence + controlled ablation |
| chunkwise KDA | token-loop execution | matmul utilization ↔ algorithm complexity | kernel/end-to-end benchmark |
| periodic MLA | pure KDA | token retrieval ↔ growing cache | ratio ablation + retrieval tests |
| NoPE MLA | RoPE MLA | simpler extension ↔ position burden on KDA | isolated or carefully controlled comparison |

## 15. Cách đọc evidence của Kimi Linear

Primary report cung cấp matched-scale comparisons và architecture ablations, nhưng cần giữ scope:[^kimi-linear-2025]

- 3:1 là lựa chọn tốt nhất trong tested ratios, không phải mathematical optimum;
- “up to 75% KV-cache reduction” gắn với layer ratio và configuration;
- batch-one 1M-context report nêu prefill 22.753 s so với 65.460 s cho MLA, và decode 7.99 ms/token so với 17.76 ms/token;
- reported $6.3\times$ decode figure đến từ maximum-throughput setup dùng freed memory cho larger batches, không phải batch-one latency;
- quality comparisons thay đồng thời attention mechanism, positional treatment và kernels, nên whole-model result không isolate từng component;
- hardware details trong report text chưa đủ để universalize latency.

Một claim an toàn có dạng:

> Trong configuration và evaluation do tác giả report, Kimi Linear 3:1 giảm số layers có sequence-growing MLA cache và đạt latency/quality được báo cáo tốt hơn matched full-MLA baseline trên nhiều, nhưng không phải mọi, evaluations.

Một claim quá mức là:

> KDA luôn nhanh hơn attention, có memory $O(1)$ cho toàn model và recall tốt hơn ở mọi context.

## 16. Checklist hoàn thành Stage 9.3

Bạn đã sẵn sàng sang Stage 9.4 khi có thể trả lời không nhìn tài liệu:

- [ ] KV cache bỏ recomputation nào và không bỏ cost/state nào?
- [ ] Vì sao factorized kernel cho phép đổi token list thành matrix state?
- [ ] Additive write thất bại thế nào với repeated key?
- [ ] Delta correction được suy ra từ retrieval error ra sao?
- [ ] $\beta_t$ khác $\alpha_t$ ở scope và chức năng nào?
- [ ] Scalar decay khác channel-wise decay thế nào?
- [ ] Vì sao recurrent decode và chunkwise training có thể cùng implement một recurrence?
- [ ] `Periodic MLA` periodic theo token hay depth?
- [ ] MLA khác KDA ở `addressability` và state growth nào?
- [ ] Claim nào là mechanism, kernel result, component ablation hay whole-model result?

## 17. Kết luận

Từ GPT-2 đến Kimi Linear, thay đổi lớn nhất là cách model biểu diễn history:

```text
GPT-2-style softmax
  token slots + growing KV cache
        ↓ replace token list with shared state
additive linear memory
  bounded state, but no overwrite and interference
        ↓ add key-addressed correction
DeltaNet
        ↓ add broad learned forgetting
Gated DeltaNet
        ↓ replace scalar with channel-wise retention control
KDA
        ↓ restore periodic direct token retrieval
Kimi Linear = 3 KDA layers + 1 global NoPE MLA layer
```

Không có bước nào “xóa” mọi trade-off. KV cache giữ addressability nhưng tăng theo context; fixed state chặn state growth nhưng phải compress history; correction và decay quản lý memory tốt hơn nhưng không tạo vô hạn capacity; periodic MLA khôi phục global retrieval nhưng đưa một phần sequence-growing cache trở lại. Hiểu được sự trao đổi này quan trọng hơn việc thuộc tên từng architecture.

## Relationships

- **Depends on:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), [KV caching](kv-caching.md), và [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md).
- **Uses:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), [Parallel DeltaNet chunkwise training](parallel-deltanet-chunkwise-training.md), [Gated DeltaNet architecture and chunkwise training](gated-deltanet-architecture-and-training.md), và [Multi-head Latent Attention](multi-head-latent-attention.md) để giải thích progression.
- **Explains:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) như một hybrid memory design thay vì một mechanism đơn lẻ.
- **Extends:** [Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới](delta-memory-kda-hybrid-architecture-beginners-project.md) từ prerequisite mechanism sang Stage 9 frontier-architecture reading.
- **Part of:** [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md), Stage 9.3.

## Evidence limits

Bài này là pedagogical synthesis từ các concept đã compile và primary reports được liệt kê. GPT-2 report mô tả architecture nhưng không trình bày modern serving KV-cache analysis; phần cache dùng secondary explainer và được giới hạn như mechanism-level orientation. DeltaNet, Gated DeltaNet và KDA equations/chunkwise algorithms có primary evidence. Kimi Linear quality và efficiency numbers là author-reported, chưa được independently replicated trong wiki. Code là algebraic toy reference, không phải released KDA kernel hay faithful model reproduction.

[^radford-gpt-2-2019]: Alec Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [source](../raw/gpt2.pdf), Sections 2.1–2.3.

[^kv-caching-explained]: “KV Caching in LLMs, Clearly Explained,” [source](../raw/KVCachinginLLMsClearlyExplained.md), Parts 1–6. Đây là secondary orientation source không ghi author/date/URL trong raw file.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4 and appendices.

[^parallel-deltanet-2024]: Songlin Yang et al., “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–3 and appendices.

[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–4 and Appendix A.

[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and cache ablations.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), Sections 1–6 and chunkwise derivation/pseudocode appendices.
