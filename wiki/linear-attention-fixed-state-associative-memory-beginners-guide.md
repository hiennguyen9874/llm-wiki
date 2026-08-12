---
type: Synthesis
title: "Linear attention như fixed-state associative memory — bài học cho người mới"
description: A beginner-first course on linear attention as fixed-state associative memory, including write/read equations, normalization, interference, retrieval trade-offs, and a testable PyTorch implementation.
tags: [attention, associative-memory, linear-attention, fixed-state, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-07-31
generated: { by: llm-wiki-agent/1, at: 2026-08-12T05:19:29Z }
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

`Linear attention` có thể được nhìn như một `fixed-state associative memory`: mỗi token **ghi** một key–value association vào cùng một matrix state, còn query **đọc** state đó bằng key tương tự. State không có sequence axis nên shape của nó không tăng theo `context length`. Đổi lại, history không còn các K/V slot độc lập cho từng token: nhiều associations bị `superposition` trong cùng state, có thể gây `interference`, và không bảo đảm `exact retrieval` như việc giữ từng token để chấm điểm riêng. Đây là trade-off cốt lõi: **bounded recurrent state và decode cost** đổi lấy **retrieval precision và finite effective capacity**.[^fast-weight-programmers-2021][^kimi-linear-2025]

> [!success] Mục tiêu
> Sau bài này, bạn có thể:
> 1. phân biệt `token-addressable memory` với `fixed-state memory`;
> 2. suy ra phép biến đổi từ kernel attention sang recurrent write/read;
> 3. giải thích vai trò của matrix state $S_t$ và normalization state $z_t$;
> 4. tự tạo ví dụ `interference` khi keys trùng hoặc không orthogonal;
> 5. implement normalized causal linear attention bằng PyTorch;
> 6. kiểm tra recurrent form và parallel reference cho cùng kết quả;
> 7. giải thích vì sao fixed state không đồng nghĩa với lossless, infinite, hay constant-latency model.

## 1. Prerequisites và mental model

Bạn nên biết Q/K/V, causal mask và `KV cache`. Nếu chưa, hãy học [Attention: beginner's guide](attention-beginner-guide.md) và [KV caching](kv-caching-beginners-guide.md) trước. Để so sánh với một cơ chế vẫn giữ entry theo token nhưng nén nhỏ hơn, xem [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md).

Ta sẽ dùng các ký hiệu:

| Ký hiệu | Shape ở một head | Ý nghĩa |
|---|---:|---|
| $q_t,k_t$ | $d_k$ | query và key của token $t$ |
| $v_t$ | $d_v$ | value cần lưu |
| $\phi(q_t),\phi(k_t)$ | $m$ | query/key sau `feature map` |
| $S_t$ | $m\times d_v$ | associative matrix state |
| $z_t$ | $m$ | normalization state |
| $o_t$ | $d_v$ | output đọc từ memory |

Trong bài này, `fixed-state` nghĩa là shape của $S_t,z_t$ do $m,d_v$ quyết định và **không chứa $t$**. Nội dung state vẫn thay đổi sau mỗi token.

Một mental model hữu ích:

```text
Token t
  ├─ key k_t   ──feature map──> memory address pattern φ(k_t)
  ├─ value v_t ───────────────> content to write
  └─ query q_t ─feature map──> pattern used to read

Write: S_t = S_{t-1} + φ(k_t) ⊗ v_t
Read:  o_t ∝ φ(q_t)^T S_t
```

`Address` ở đây là một vector phân tán, không phải integer index như địa chỉ RAM.

## 2. Baseline: softmax attention giữ token-addressable memory

Ở một causal attention head:

$$
o_t=\sum_{i=1}^{t}\alpha_{t,i}v_i,
\qquad
\alpha_{t,i}=\frac{\exp(q_t^Tk_i/\sqrt{d_k})}
{\sum_{j=1}^{t}\exp(q_t^Tk_j/\sqrt{d_k})}.
$$

Mỗi token cũ có một $k_i,v_i$ riêng. Query mới tính score riêng cho từng $k_i$, vì vậy memory là `token-addressable`: index $i$ vẫn tồn tại trong computation.

Khi autoregressive decode có `KV cache`:

- không cần tính lại K/V cũ;
- cache vẫn thêm một K/V entry sau mỗi token;
- một query mới vẫn phải tương tác với prefix đang được giữ;
- cache memory tăng theo $O(Td_k+Td_v)$ trên mỗi head, với $T$ là context length.

`FlashAttention` thay đổi evaluation order và data movement nhưng vẫn tính exact softmax attention; nó không biến token-addressable cache thành fixed state. `MLA` nén số elements trên mỗi token nhưng cache vẫn có sequence axis. [^kimi-linear-2025]

## 3. Từ kernel attention đến recurrent state

### 3.1 Thay softmax kernel bằng feature map

Viết attention dưới dạng một similarity kernel:

$$
o_t=
\frac{\sum_{i=1}^{t}\kappa(q_t,k_i)v_i}
{\sum_{i=1}^{t}\kappa(q_t,k_i)}.
$$

Softmax attention dùng kernel liên quan đến $\exp(q_t^Tk_i)$, nhưng thông thường không thể tách chính xác thành một feature map hữu hạn nhỏ. `Linear attention` chọn hoặc xấp xỉ một kernel có dạng:

$$
\kappa(q,k)=\phi(q)^T\phi(k).
$$

Thay vào tử số:

$$
\sum_{i=1}^{t}
\left(\phi(q_t)^T\phi(k_i)\right)v_i.
$$

Vì matrix multiplication có tính associative, ta đổi thứ tự ngoặc:

$$
\phi(q_t)^T
\left(\sum_{i=1}^{t}\phi(k_i)v_i^T\right).
$$

Đặt:

$$
S_t=\sum_{i=1}^{t}\phi(k_i)v_i^T
\in\mathbb{R}^{m\times d_v}.
$$

Ta có recurrent write:

$$
\boxed{S_t=S_{t-1}+\phi(k_t)v_t^T}
$$

và unnormalized read:

$$
\boxed{\tilde o_t=\phi(q_t)^TS_t.}
$$

Outer product $\phi(k_t)v_t^T$ ghi value lên các rows của state theo address pattern của key. Cách nhìn `fast-weight programmer` xem $S_t$ như một weight matrix được lập trình nhanh bởi chuỗi outer-product updates.[^fast-weight-programmers-2021]

### 3.2 Normalization state

Để giữ denominator của normalized kernel attention, tích lũy thêm:

$$
z_t=\sum_{i=1}^{t}\phi(k_i)
=z_{t-1}+\phi(k_t).
$$

Read đầy đủ là:

$$
\boxed{
o_t=
\frac{\phi(q_t)^TS_t}
{\phi(q_t)^Tz_t+\varepsilon}.}
$$

$S_t$ giữ weighted value sums; $z_t$ giữ tổng key features dùng để normalize. Khi $\phi$ không âm, denominator thường dễ diễn giải như tổng similarity. $\varepsilon$ chỉ bảo vệ numerical stability, không sửa được một feature map hoặc state đã học kém.

> [!important] Causal convention
> Công thức trên **write trước rồi read**, nên output ở position $t$ được dùng token hiện tại và các token trước: $i\le t$. Nếu task cần strict past $i<t$, hãy read trước write. Hai conventions khác nhau một vị trí và không nên bị trộn trong test.

## 4. Vì sao đây là associative memory?

Giả sử mapped keys $u_A,u_B$ là unit vectors orthogonal và ta ghi:

$$
S=u_Av_A^T+u_Bv_B^T.
$$

Query bằng $u_A$ cho:

$$
u_A^TS
=(u_A^Tu_A)v_A^T+(u_A^Tu_B)v_B^T
=v_A^T.
$$

Memory trả về value liên kết với key giống query. Không cần biết association được ghi ở token index nào.

Tổng quát hơn, sau $n$ writes:

$$
q^TS=\sum_{i=1}^{n}(q^Tk_i)v_i^T.
$$

Mỗi value được lấy theo similarity giữa query và key. Đây chính là `content-based retrieval`.

### Token-addressable và association-addressable khác nhau thế nào?

| Thuộc tính | Softmax + KV cache | Linear fixed-state memory |
|---|---|---|
| History representation | một K/V entry mỗi token | mọi writes cùng gộp vào state |
| Có sequence axis trong decode state | có | không |
| Query chấm từng token cũ | có | không; query state đã tổng hợp |
| State tăng theo context | có | không |
| Exact access tới một retained token slot | structurally available | không được bảo đảm |
| Rủi ro chính | cache/read bandwidth tăng | superposition và interference |

`Token-addressable` cũng không bảo đảm model luôn retrieve đúng; nó chỉ giữ các candidate slots riêng. Ngược lại, fixed-state có thể retrieve rất tốt trên distribution đã học, nhưng không có một slot lossless riêng cho mỗi token.

## 5. Interference: khi nhiều memories dùng chung state

### 5.1 Crosstalk giữa non-orthogonal keys

Ghi hai associations:

$$
S=k_Av_A^T+k_Bv_B^T.
$$

Read bằng $q=k_A$:

$$
k_A^TS=
\|k_A\|^2v_A^T+(k_A^Tk_B)v_B^T.
$$

Hạng thứ hai là `crosstalk`. Nếu $k_A^Tk_B\ne0$, value $v_B$ rò vào retrieval của $A$. Feature map và learned projections có thể cố tách addresses, nhưng state width hữu hạn không tạo ra vô hạn orthogonal directions.

### 5.2 Collision: cùng key, values khác nhau

Nếu ghi cùng mapped key $u$ hai lần với $v_1,v_2$:

$$
S=u(v_1+v_2)^T.
$$

Pure additive memory không biết write thứ hai là:

- evidence bổ sung cần cộng;
- một record khác tình cờ có cùng address;
- hay update mới cần thay thế record cũ.

Với normalized read và hai writes có cùng key, kết quả có xu hướng là một mixture/average thay vì tự động trả về latest value. Đây là lý do `delta rule` đọc association hiện tại rồi ghi correction, còn learned `decay` giúp quên rộng hơn.[^fast-weight-programmers-2021][^kimi-linear-2025]

### 5.3 Capacity không phải một context-length hằng số

Trong phân tích interference-free đơn giản của paper, mapped keys phải mutually orthogonal. Không gian feature có dimension $m$ chỉ chứa tối đa $m$ vectors mutually orthogonal, nên số associations hoàn toàn không interference trong giả định đó không vượt quá $m$.[^fast-weight-programmers-2021]

Không nên diễn giải thành “model quên chính xác ở token $m+1$” vì thực tế:

- keys không nhất thiết cần orthogonal hoàn toàn để task thành công;
- values, sparsity, normalization, gates và data distribution đều ảnh hưởng;
- nhiều tokens có thể củng cố cùng association;
- model có thể học chỉ giữ task-relevant information;
- effective capacity phụ thuộc workload, không chỉ dimension.

Vì vậy đây là `representational capacity bound` trong một điều kiện lý tưởng, không phải universal benchmark threshold.

## 6. Fixed-state trade-off qua memory và compute

Gọi $m$ là feature width, $d_v$ là value width và bỏ qua batch/layer/head factors:

| Cơ chế | Persistent decode state | Work của một decode step | Retrieval structure |
|---|---:|---:|---|
| Softmax + KV cache | $O(T(d_k+d_v))$ | tăng theo $T$ | score từng cached token |
| MLA-like compressed cache | $O(Tr)$ | vẫn tăng theo $T$ | score từng compressed token entry |
| Linear attention | $O(md_v+m)$ | $O(md_v)$ | read một aggregated state |

Trong linear attention, cả state size và recurrent work của một step không chứa $T$. Tuy nhiên:

- model vẫn phải xử lý từng token autoregressively;
- end-to-end latency còn projections, FFN/MoE, kernels, memory movement và batching;
- training/prefill cần tạo output cho mọi position, không phải $O(1)$ tổng cộng;
- recurrent formulation có sequential dependency; efficient systems thường dùng parallel/chunkwise formulations khi training hoặc prefill;
- feature width $m$ lớn hơn tăng cả state capacity lẫn cost.

Kimi Linear chẳng hạn dùng chunkwise KDA cho multi-token processing và recurrent update cho generation; KDA state có shape theo $d_k\times d_v$, nhưng hybrid model vẫn giữ sequence-growing MLA cache ở các global-attention layers.[^kimi-linear-2025][^kimi-k3-2026]

> [!warning] “Linear” đang nói về gì?
> `Linear attention` thường nói sequence computation/state scaling theo context dưới formulation phù hợp. Nó không có nghĩa mọi operation đều scalar-linear, model có constant total runtime, hay output là linear function của input sau khi tính Q/K/V và feature maps.

## 7. Feature map cũng là một retrieval trade-off

Reassociation chỉ hoạt động khi similarity factorize thành $\phi(q)^T\phi(k)$. Vì thế architecture phải chọn một feature map hoặc kernel approximation.

Một toy choice phổ biến để học là:

$$
\phi(x)=ELU(x)+1,
$$

cho positive features. Production variants có thể dùng maps khác, normalized keys, learned gates, random features hoặc deterministic expanded features. [Deterministic parameter-free projection](deterministic-parameter-free-projection-for-linear-attention.md) tăng feature dimension để tăng capacity bound, nhưng state và compute cũng lớn hơn.[^fast-weight-programmers-2021]

Có hai nguồn mất retrieval precision cần tách riêng:

1. **Kernel/feature limitation:** $\phi(q)^T\phi(k)$ không có toàn bộ selectivity của exact softmax kernel.
2. **State interference:** nhiều associations superpose trong state hữu hạn.

Tăng $m$ có thể giúp cả kernel approximation và address separation, nhưng làm fixed state rộng hơn. Không có “free infinite context”: state shape bounded còn information phải được compress, overwritten, decayed hoặc mixed.

## 8. PyTorch lab: normalized causal linear attention

Code sau ưu tiên semantics và testability. Nó nhận Q/K/V đã projected cho **một head**; production code còn multi-head layout, learned projections, output projection, normalization, gating và optimized kernels.

```python
import torch
import torch.nn.functional as F


def positive_feature(x: torch.Tensor) -> torch.Tensor:
    """Toy non-negative feature map φ(x) = ELU(x) + 1."""
    return F.elu(x) + 1.0


def linear_attention_recurrent(q, k, v, eps=1e-6):
    """
    Normalized causal linear attention, inclusive of current token.

    q, k: (batch, time, d_key)
    v:    (batch, time, d_value)
    return: (batch, time, d_value)
    """
    qf = positive_feature(q)  # (B, T, M); here M == d_key
    kf = positive_feature(k)  # (B, T, M)

    B, T, M = qf.shape
    Dv = v.size(-1)
    state = q.new_zeros(B, M, Dv)  # S_t
    normalizer = q.new_zeros(B, M)  # z_t
    outputs = []

    for t in range(T):
        # Write current association: S <- S + φ(k_t) v_t^T
        state = state + torch.einsum("bm,bv->bmv", kf[:, t], v[:, t])
        normalizer = normalizer + kf[:, t]

        # Read: φ(q_t)^T S / (φ(q_t)^T z + eps)
        numerator = torch.einsum("bm,bmv->bv", qf[:, t], state)
        denominator = torch.einsum(
            "bm,bm->b", qf[:, t], normalizer
        ).unsqueeze(-1)
        outputs.append(numerator / denominator.clamp_min(eps))

    return torch.stack(outputs, dim=1)


def linear_attention_parallel_reference(q, k, v, eps=1e-6):
    """
    Materializes every prefix state for verification only.
    Not a memory-efficient production implementation.
    """
    qf = positive_feature(q)
    kf = positive_feature(k)

    writes = torch.einsum("btm,btv->btmv", kf, v)
    prefix_states = writes.cumsum(dim=1)       # (B, T, M, Dv)
    prefix_normalizers = kf.cumsum(dim=1)      # (B, T, M)

    numerator = torch.einsum("btm,btmv->btv", qf, prefix_states)
    denominator = torch.einsum(
        "btm,btm->bt", qf, prefix_normalizers
    ).unsqueeze(-1)
    return numerator / denominator.clamp_min(eps)


# 1) Recurrent and explicit-prefix forms must agree.
torch.manual_seed(0)
q = torch.randn(2, 7, 4, dtype=torch.float64)
k = torch.randn(2, 7, 4, dtype=torch.float64)
v = torch.randn(2, 7, 3, dtype=torch.float64)

y_rec = linear_attention_recurrent(q, k, v)
y_ref = linear_attention_parallel_reference(q, k, v)
torch.testing.assert_close(y_rec, y_ref, rtol=1e-10, atol=1e-10)
print("recurrent == prefix reference")

# 2) Causality: changing future K/V cannot change earlier outputs.
k_changed = k.clone()
v_changed = v.clone()
k_changed[:, 5:] = torch.randn_like(k_changed[:, 5:]) * 100
v_changed[:, 5:] = torch.randn_like(v_changed[:, 5:]) * 100

y_changed = linear_attention_recurrent(q, k_changed, v_changed)
torch.testing.assert_close(y_rec[:, :5], y_changed[:, :5])
print("future perturbation does not affect the past")

# 3) Persistent recurrent state size does not depend on T.
B, M, Dv = 2, q.size(-1), v.size(-1)
state_elements = B * M * Dv + B * M
print("persistent state elements:", state_elements)
```

### Điều gì được test và chưa được test?

Đã test:

- đúng shape;
- recurrent reassociation bằng explicit prefix-state computation;
- causal behavior;
- persistent state shape không chứa sequence length.

Chưa test:

- equality với softmax attention — hai mechanisms dùng kernel khác nên không nên mặc định bằng nhau;
- production speed — Python loop thường chậm;
- mixed-precision stability;
- quality sau training;
- multi-head projections, masking cho padding và cache lifecycle.

## 9. Lab nhỏ: nhìn thấy interference trực tiếp

Đoạn code sau bỏ feature projection để thao tác trực tiếp trong address space:

```python
import torch


def write(state, key, value):
    return state + torch.outer(key, value)


def read(state, query):
    return query @ state


# Hai orthogonal addresses: retrieval tách biệt.
e1 = torch.tensor([1.0, 0.0])
e2 = torch.tensor([0.0, 1.0])
v_a = torch.tensor([10.0, 0.0])
v_b = torch.tensor([0.0, 20.0])

S = torch.zeros(2, 2)
S = write(S, e1, v_a)
S = write(S, e2, v_b)
print(read(S, e1))  # tensor([10.,  0.])

# Non-orthogonal address gây crosstalk.
k_c = torch.tensor([0.8, 0.6])  # unit vector, overlaps e1
v_c = torch.tensor([0.0, 30.0])
S2 = write(S, k_c, v_c)
print(read(S2, e1))  # tensor([10., 24.]): v_c leaks into read(e1)

# Cùng address không tự hiểu "latest write wins".
S3 = torch.zeros(2, 2)
S3 = write(S3, e1, torch.tensor([1.0, 0.0]))
S3 = write(S3, e1, torch.tensor([0.0, 1.0]))
print(read(S3, e1))  # tensor([1., 1.]): additive mixture
```

Hãy thử:

1. thay $k_c$ bằng vector gần orthogonal hơn và đo crosstalk;
2. tăng số random keys trong address dimension 2, 8, 32;
3. normalize keys rồi vẽ pairwise cosine similarity;
4. so sánh additive write với một toy `delta update`;
5. đo retrieval error theo số associations và feature width.

## 10. Từ additive memory đến delta rule và gating

Pure additive update:

$$
S_t=S_{t-1}+k_tv_t^T
$$

không có thao tác overwrite rõ ràng. `Delta rule` trước tiên đọc prediction hiện tại cho key $k_t$, sau đó chỉ ghi residual error:

$$
\bar v_t=S_{t-1}^Tk_t,
$$

$$
S_t=S_{t-1}+\beta_tk_t(v_t-\bar v_t)^T.
$$

Nếu keys orthogonal và $\beta_t=1$, update có thể sửa association được address mà ít ảnh hưởng associations orthogonal. Learned decay bổ sung cơ chế quên rộng hơn. [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) trình bày chi tiết con đường từ additive linear attention tới DeltaNet, Gated DeltaNet và KDA.[^fast-weight-programmers-2021][^kimi-linear-2025]

Các cải tiến này quản lý finite state tốt hơn; chúng không biến state thành token-addressable lossless storage.

## 11. Vì sao hybrid architecture hợp lý?

Pure fixed-state memory phù hợp khi model có thể nén history thành task-relevant sufficient state. Nó khó hơn với các bài cần exact copy hoặc truy xuất một item cụ thể trong history dài. Kimi Linear report gọi long-context retrieval là bottleneck chính của pure linear attention và kết hợp ba KDA layers với một global MLA layer trong pattern được thử nghiệm của họ.[^kimi-linear-2025]

Hai pathways bổ sung nhau:

- **KDA/linear recurrent layers:** bounded state, efficient recurrent decode, learned compression và memory update;
- **global MLA layers:** giữ token-derived entries để query có thể thực hiện token-level retrieval định kỳ.

Đây không phải bằng chứng tỷ lệ 3:1 tối ưu cho mọi model. Nó là architecture-specific empirical choice. Kimi K3 cũng giữ hybrid fixed-state KDA và periodic global MLA; vì thế không nên mô tả toàn model như có memory hoàn toàn constant theo context.[^kimi-k3-2026]

## 12. Những hiểu lầm thường gặp

1. **“Linear attention là FlashAttention.”** Sai. FlashAttention là exact softmax attention với IO-aware evaluation; linear attention đổi formulation/kernel để reassociate computation.
2. **“Fixed-state nghĩa là nhớ vô hạn.”** Sai. Shape không tăng nhưng information từ context phải chia sẻ finite state.
3. **“Context window vô hạn nghĩa là exact retrieval vô hạn.”** Sai. Model có thể tiếp tục recurrent updates rất lâu mà retrieval quality vẫn suy giảm do interference, decay hoặc distribution shift.
4. **“Decode của softmax luôn $O(T^2)$ mỗi token.”** Sai. Với KV cache, một decode query tương tác với $T$ cached entries; full prefill/training attention trên $T$ positions mới có score matrix quadratic theo sequence.
5. **“Normalization xóa interference.”** Sai. Nó kiểm soát scale của weighted sum; overlapping addresses vẫn mix values.
6. **“State constant nên toàn model có constant memory.”** Sai. Weights, activations, batching, convolution state và bất kỳ global-attention cache nào vẫn tồn tại.
7. **“Linear attention phải bằng softmax attention.”** Sai. Exact equality chỉ có nếu kernel factorization tương ứng là exact; finite feature maps thường định nghĩa hoặc xấp xỉ similarity khác.
8. **“Tăng feature width luôn tốt.”** Không chắc. Capacity có thể tăng nhưng state, FLOPs, bandwidth và optimization difficulty cũng tăng.

## 13. Checklist khi đọc một linear-attention paper

Hãy trả lời các câu sau trước khi tin headline về long context:

1. Persistent state chính xác có shape nào? Có sequence axis không?
2. Write rule là additive, delta, decay, gate hay combination?
3. Read rule có normalization state không?
4. Feature map/kernel là gì? Exact cho kernel nào, approximation cho kernel nào?
5. Training/prefill dùng recurrent, parallel hay chunkwise algorithm?
6. Decode state có thêm short-convolution state hoặc cache khác không?
7. Model pure linear hay hybrid với local/global attention?
8. Benchmark đo perplexity, recall, exact copy, long-context retrieval hay end-task quality?
9. Efficiency number là batch-one latency, throughput hay theoretical FLOPs?
10. Evidence là author-run hay independently replicated?

## 14. Bài tập cuối bài

1. **Derivation:** từ $\kappa(q,k)=\phi(q)^T\phi(k)$, tự suy ra $S_t,z_t$ mà không nhìn công thức.
2. **Strict-past variant:** sửa code thành read-before-write và viết test position 0 trả output zero.
3. **Interference curve:** với random unit keys/values, plot mean retrieval error theo số writes cho $m\in\{8,32,128\}$.
4. **Overwrite:** implement delta update với $\beta=1$ và test repeated-key case.
5. **Memory accounting:** so sánh element count của MHA KV cache và state $m\times d_v+m$ tại nhiều context lengths.
6. **Integration:** thay một attention head trong toy causal model bằng implementation trên; so sánh loss, speed và memory mà không tuyên bố quality từ một run duy nhất.

## 15. Tóm tắt

- Linear attention factorize similarity qua $\phi(q)^T\phi(k)$ để gom prefix thành $S_t$ và, khi cần, $z_t$.
- Write là outer product; read là query nhân matrix state.
- State shape không tăng theo context, nên recurrent decode memory và work mỗi layer có thể không phụ thuộc số token cũ.
- Nhiều associations cùng superpose trong finite state; non-orthogonal keys tạo crosstalk, repeated keys tạo additive mixture.
- Feature map, state width, normalization và update rule quyết định retrieval behavior.
- Delta rule và decay quản lý overwrite/forgetting tốt hơn nhưng không phục hồi lossless token slots.
- Hybrid architecture kết hợp fixed-state efficiency với periodic token-addressable retrieval vì hai cơ chế có strengths khác nhau.

## Relationships

- **Contrasts with:** [Scaled dot-product and multi-head attention](scaled-dot-product-and-multi-head-attention.md), nơi query chấm điểm từng retained token entry.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md), cơ chế nén state trên mỗi token nhưng vẫn tăng cache theo context.
- **Improved by:** [Deterministic parameter-free projection](deterministic-parameter-free-projection-for-linear-attention.md), which expands feature-space capacity at greater fixed-state cost.
- **Improved by:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), which adds targeted correction and learned forgetting.
- **Used by:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md) and [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) through KDA alongside periodic global MLA.[^kimi-linear-2025][^kimi-k3-2026]
- **Generalized by:** [Structured State Space Duality](structured-state-space-duality.md), which relates linear attention and a broader structured state-space family through semiseparable sequence transformations.[^dao-gu-2024]

## Evidence limits

Write/read equivalence, fast-weight interpretation và simple capacity analysis are documented by the 2021 primary paper. KDA’s fixed matrix state, recurrent/chunkwise split and hybrid retrieval motivation are documented by the Kimi Linear and Kimi K3 reports. The PyTorch implementations, worked examples, complexity table and teaching sequence above are synthesis for explanation; they are not production benchmarks. Fixed state guarantees bounded state dimensions, not lossless memory, constant end-to-end latency, infinite usable context or quality parity with exact softmax attention.

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), especially Sections 3–4 and Appendices A–B.

[^gpt2-kimi3-2026]: ali (@waterloo_intern), “22580: From GPT2 to Kimi3, Explained,” 2026-07-27, [raw source](../raw/2026-07-27-from-gpt2-to-kimi-k3.md). This is secondary explanatory evidence; primary-paper claims take precedence.

[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 1–3, 5–6 and appendices.

[^kimi-k3-2026]: Kimi Team, “Kimi K3: Open Frontier Intelligence,” arXiv:2607.24653v1, [source](../raw/arXiv-2607.24653v1/main.tex), Sections 2.1 and 5.

[^dao-gu-2024]: Tri Dao and Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 4–6.
