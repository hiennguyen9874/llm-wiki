---
type: Synthesis
title: "Delta memory, KDA, và hybrid KDA–MLA — mini-project cho người mới"
description: A beginner-first course and PyTorch mini-project on delta correction, scalar and channel-wise decay, KDA, fixed-state retrieval limits, and why hybrid architectures periodically insert global MLA layers.
tags: [delta-rule, kda, associative-memory, fixed-state, hybrid-attention, mla, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated:
  by: llm-wiki-agent/1
  at: 2026-08-12T12:30:08+07:00
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

`Delta memory` giải quyết một lỗi cơ bản của additive associative memory: khi cùng một key xuất hiện với value mới, memory cần **sửa association cũ** thay vì cộng hai values lại. `Decay` bổ sung khả năng quên rộng hơn; `Kimi Delta Attention` (KDA) kết hợp delta correction với `channel-wise decay` để điều khiển retention chi tiết hơn. Tuy nhiên, mọi associations vẫn phải chia sẻ một fixed-size matrix state, nên interference và giới hạn precise retrieval không biến mất. Kimi Linear vì thế dùng pattern theo chiều sâu `3 KDA layers → 1 global MLA layer`: phần lớn layers có bounded recurrent state, còn periodic MLA khôi phục token-level retrieval tại một số layers.[^fast-weight-programmers-2021][^gated-deltanet-2025][^kimi-linear-2025]

> [!success] Mục tiêu
> Sau bài này, bạn có thể:
> 1. giải thích vì sao additive write không có semantics `overwrite`;
> 2. tự suy ra `delta correction` từ retrieval error;
> 3. phân biệt vai trò của $\beta_t$ và decay gate $\alpha_t$;
> 4. đọc recurrence của DeltaNet, Gated DeltaNet và KDA;
> 5. giải thích vì sao fixed state vẫn gặp `interference` và retrieval bottleneck;
> 6. phân biệt periodic **theo layer depth** với periodic theo token/time;
> 7. chạy mini-project so sánh token-level KV storage với fixed associative state trên `exact recall`, `overwrite` và capacity stress.

## 1. Prerequisites và bài toán cần giải

Nên học trước:

1. [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md);
2. [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md);
3. [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md).

Ta xét stream các key–value pairs:

```text
WRITE(user_17, plan_free)
QUERY(user_17)                 -> plan_free
WRITE(user_17, plan_pro)       # overwrite
QUERY(user_17)                 -> plan_pro
```

Một memory hữu ích phải trả lời hai loại yêu cầu:

- **Exact recall:** key đã lưu phải trả đúng value.
- **Overwrite:** khi key cũ được gán value mới, query sau đó phải trả value mới chứ không phải tổng hay trung bình của hai values.

Đây là toy abstraction. Trong LLM thật, keys, values, gates và queries được học từ hidden states; model không nhận sẵn integer key hay thao tác database rõ ràng.

## 2. Hai cách lưu history

### 2.1 Token-level KV cache: giữ từng slot

Token-addressable attention giữ một K/V entry cho mỗi token:

$$
K_{1:T}=[k_1,\ldots,k_T],
\qquad
V_{1:T}=[v_1,\ldots,v_T].
$$

Query $q$ tạo score riêng cho từng retained key:

$$
a_i=\operatorname{softmax}_i(q^Tk_i),
\qquad
o=\sum_i a_iv_i.
$$

Ưu điểm về representation là association ở token $i$ không bị bắt buộc cộng vào cùng matrix slot với token $j$. Hệ thống còn giữ sequence axis để model chọn từng candidate token. Cái giá là persistent cache tăng theo context:

$$
M_{KV}=O(T(d_k+d_v)).
$$

`Token-addressable` không đồng nghĩa model luôn recall đúng. Softmax có thể chọn sai, duplicate keys có thể tạo mixture, và positional/recency behavior phải được học hoặc mã hóa. Nó chỉ nói rằng các token slots vẫn còn riêng biệt để retrieval mechanism chấm điểm.

### 2.2 Fixed-state associative memory: gộp history

Một additive memory tối giản có matrix state:

$$
S_t=S_{t-1}+k_tv_t^T,
\qquad S_t\in\mathbb{R}^{d_k\times d_v}.
$$

Query đọc:

$$
\hat v_t=S_t^Tq_t.
$$

State size là:

$$
M_{fixed}=O(d_kd_v),
$$

không chứa context length $T$. Nhưng tất cả writes cùng nằm trong $S_t$. Nếu keys không orthogonal, retrieval chứa `crosstalk`; nếu nhiều logical keys dùng cùng hoặc gần cùng address, chúng không còn slot độc lập.[^fast-weight-programmers-2021]

## 3. Vì sao additive memory thất bại khi overwrite?

Giả sử một unit key $k$ được ghi lần lượt với $v_{old}$ và $v_{new}$:

$$
S=kv_{old}^T+kv_{new}^T.
$$

Read bằng cùng key:

$$
S^Tk=(k^Tk)(v_{old}+v_{new})=v_{old}+v_{new}.
$$

Memory không biết write thứ hai mang nghĩa:

- thay thế record cũ;
- thêm evidence;
- hay tạo một record khác bị collision.

Normalization có thể biến tổng thành mixture/average, nhưng vẫn không tự tạo `latest value wins`.

> [!example] Intuition
> Additive write giống viết tiếp mực lên cùng tờ giấy trong suốt. Delta write trước tiên nhìn xem trên giấy đang có gì, rồi chỉ thêm phần sai lệch để hình hiện tại tiến về mục tiêu mới.

## 4. Delta correction: read trước, sửa error sau

Gọi prediction hiện tại của memory tại key $k_t$ là:

$$
\bar v_t=S_{t-1}^Tk_t.
$$

Retrieval error là:

$$
e_t=v_t-\bar v_t.
$$

Thay vì ghi toàn bộ $v_t$, delta rule chỉ ghi error:

$$
\boxed{S_t=S_{t-1}+\beta_tk_te_t^T}
$$

hay:

$$
\boxed{S_t=S_{t-1}+\beta_tk_t(v_t-S_{t-1}^Tk_t)^T.}
$$

Với $\|k_t\|_2=1$ và $\beta_t=1$:

$$
S_t^Tk_t
=S_{t-1}^Tk_t+(v_t-S_{t-1}^Tk_t)
=v_t.
$$

Association được address bởi $k_t$ trở thành value mới chỉ sau một update. Nếu một key $u$ orthogonal với $k_t$, vì $u^Tk_t=0$, update không thay đổi read tại $u$.

Dạng matrix thường thấy trong DeltaNet là:

$$
\boxed{
S_t=(I-\beta_tk_tk_t^T)S_{t-1}
+\beta_tk_tv_t^T.
}
$$

Hai terms có ý nghĩa:

1. $(I-\beta_tk_tk_t^T)S_{t-1}$ loại bỏ một phần association cũ theo direction $k_t$;
2. $\beta_tk_tv_t^T$ ghi association mới vào direction đó.

Đây cũng có thể được diễn giải là một online gradient step trên reconstruction loss $\tfrac12\|S^Tk_t-v_t\|^2$.[^parallel-deltanet-2024][^kimi-linear-2025]

### Vai trò của $\beta_t$

- $\beta_t=0$: không sửa memory.
- $0<\beta_t<1$: cập nhật một phần; hữu ích khi write có thể nhiễu hoặc cần smooth.
- $\beta_t=1$: full correction theo addressed direction nếu key normalized.

Trong model thật, $\beta_t$ thường được sinh từ input qua learned projection và `sigmoid`; nó không phải một hyperparameter luôn bằng 1.

## 5. Delta rule sửa được gì, chưa sửa được gì?

### Sửa tốt trong trường hợp lý tưởng

Nếu mapped keys là orthonormal:

$$
k_i^Tk_j=\begin{cases}1&i=j\\0&i\ne j,\end{cases}
$$

thì delta update có thể overwrite association $i$ mà không chạm association $j$.

### Không loại bỏ finite-capacity interference

Nếu $k_A^Tk_B\ne0$, update cho $B$ làm read tại $A$ đổi theo:

$$
\Delta \hat v_A
=\beta(k_A^Tk_B)(v_B-\hat v_B).
$$

Overlap càng lớn, collateral update càng lớn. Trường hợp cực đoan $k_A=k_B$ có nghĩa hai logical keys dùng đúng một address; bất kỳ rule chỉ nhìn address đó đều không thể phân biệt chúng.

Vì vậy delta rule cho memory semantics tốt hơn additive write, nhưng không biến fixed-size state thành một database có vô hạn exact slots.

## 6. Tại sao cần decay?

Delta correction chỉ sửa direction được current key address. Nó không trực tiếp giải quyết mọi state content đã lỗi thời, nhiễu hoặc không còn hữu ích ở các directions khác.

Một scalar decay đơn giản tạo intermediate state:

$$
\widetilde S_{t-1}=\alpha_tS_{t-1},
\qquad \alpha_t\in[0,1].
$$

Sau đó delta correction chạy trên state đã decay:

$$
S_t=(I-\beta_tk_tk_t^T)\widetilde S_{t-1}
+\beta_tk_tv_t^T.
$$

Tác dụng của hai controls khác nhau:

| Control | Phạm vi | Vai trò chính |
|---|---|---|
| `Delta correction` | key-addressed direction | sửa association được chọn |
| Scalar `decay` | toàn state/head | quên rộng, giải phóng capacity |
| Channel-wise `decay` | từng key channel | retention horizon chi tiết hơn |

`Decay` tạo trade-off không tránh được:

- decay yếu: giữ lâu hơn nhưng nhiễu cũ tồn tại;
- decay mạnh: dọn state nhanh hơn nhưng exact retention dài hạn suy giảm.

Gated DeltaNet kết hợp scalar learned decay với delta rule; paper của nó cho thấy hai cơ chế bổ sung nhau trong recipe được đánh giá, nhưng kết quả vẫn phụ thuộc model, data và benchmark.[^gated-deltanet-2025]

## 7. KDA: channel-wise decay + delta correction

KDA thay scalar decay bằng vector:

$$
\alpha_t\in[0,1]^{d_k}.
$$

State được decay theo từng row/key channel:

$$
\widetilde S_{t-1}=\operatorname{Diag}(\alpha_t)S_{t-1}.
$$

Recurrence là:

$$
\boxed{
S_t=(I-\beta_tk_tk_t^T)
\operatorname{Diag}(\alpha_t)S_{t-1}
+\beta_tk_tv_t^T.
}
$$

Một cách implement tương đương, dễ đọc:

```python
decayed = alpha[:, None] * state
prediction = key @ decayed
state = decayed + beta * outer(key, value - prediction)
```

KDA có thể học để một số channels giữ information lâu, trong khi channels khác quên nhanh theo input. Kimi Linear còn dùng normalized Q/K, short convolution, output normalization và output gate; recurrence trên chỉ là lõi memory, không phải toàn bộ KDA layer.[^kimi-linear-2025]

### Tại sao gọi là `fixed-state`?

Với một head, $S_t$ luôn có shape $d_k\times d_v$. Token thứ một triệu cập nhật cùng tensor shape như token thứ mười. During autoregressive decode, update recurrent không cần append một K/V slot mới cho KDA state.

Điều này không có nghĩa:

- state chứa vô hạn information;
- retrieval luôn exact;
- toàn model có memory constant;
- training/prefill nhất thiết chạy token-by-token.

KDA dùng chunkwise formulation để parallelize training/prefill và recurrent update khi decode; hybrid model vẫn có sequence-growing cache tại MLA layers.[^kimi-linear-2025]

## 8. Vì sao periodic MLA vẫn cần thiết?

Kimi Linear report xác định long-context retrieval là bottleneck chính của pure linear attention và chọn layerwise hybrid:

```text
Block 1: KDA
Block 2: KDA
Block 3: KDA
Block 4: global NoPE MLA
          ↓ repeat across depth
```

> [!important] “Periodic” là theo layer depth
> Pattern `3:1` không có nghĩa model dùng MLA sau mỗi ba tokens. **Mọi token** đi qua tất cả layers. MLA xuất hiện định kỳ khi đi lên network depth: ba KDA token-mixing layers rồi một global MLA layer.[^kimi-linear-2025]

### Hai pathways bổ sung nhau

**KDA layers** cung cấp:

- fixed-size recurrent matrix state;
- per-step state update không tăng theo prefix length;
- delta overwrite và learned channel-wise forgetting;
- learned compression của history thành task-relevant state.

**Global MLA layers** cung cấp:

- một compressed latent entry cho mỗi retained token;
- score/weight riêng theo token position;
- direct token-level retrieval và fine-grained selection;
- đường truy cập phù hợp hơn với exact copying và recall từ history dài.

MLA giảm bytes trên mỗi token so với standard MHA, nhưng cache vẫn tăng theo $T$. Hybrid architecture chấp nhận một phần sequence-growing state để tránh buộc mọi retrieval đi qua fixed-capacity compression.

### Tại sao không dùng toàn MLA?

Full MLA giữ token-addressability ở mọi attention layer nhưng phải trả cache/read cost tăng theo context ở mọi layer. Dùng KDA ở phần lớn layers giảm số layers cần giữ cache theo token. Với pattern 3:1, chỉ một phần tư token-mixing layers là MLA, dẫn tới claim “up to 75% KV-cache reduction” so với full MLA trong cấu hình report; đây là layer-ratio accounting và author-reported system result, không phải universal guarantee.[^kimi-linear-2025]

### Tại sao không dùng toàn KDA?

Fixed state phải compress ngày càng nhiều history vào cùng số dimensions. Delta correction và decay quản lý state tốt hơn, nhưng không khôi phục isolated token slots sau khi associations interfere hoặc collide. Primary report nhấn mạnh exact copying và fine-grained long-context retrieval là điểm yếu còn lại của pure linear attention.[^kimi-linear-2025]

### Tỷ lệ 3:1 không phải định luật

Trong ablation của Kimi Linear, 3:1 có validation PPL 5.65; 1:1 là 5.66; 7:1 là 5.70; 15:1 là 5.82; full MLA là 5.77. Kết quả 3:1 tốt nhất trong configurations và training recipe được test, nhưng không chứng minh đây là optimum cho mọi scale, workload hoặc hardware.[^kimi-linear-2025]

## 9. Mini-project: KV slots vs fixed associative state

### 9.1 Câu hỏi nghiên cứu

Ta sẽ kiểm tra bốn hypotheses:

1. Token-level storage có thể giữ mỗi write trong slot riêng, nhưng memory tăng theo số writes.
2. Delta memory có thể exact recall khi addresses orthogonal và capacity đủ.
3. Delta correction xử lý repeated-key overwrite tốt hơn additive write.
4. Khi logical keys collide trong fixed address space, delta correction không thể giữ cả hai exact; token slots vẫn giữ được evidence riêng.

### 9.2 Fairness và scope

Mini-project cố ý so sánh **storage semantics**, không so chất lượng hai neural architectures đã train:

- `TokenLevelKV` dùng exact logical-key match và chọn write mới nhất. Đây là oracle retrieval policy trên retained token slots, **không phải** implementation của softmax attention.
- `FixedAssociativeMemory` nhận address vectors đã định sẵn. Trong model thật, các vectors và gates phải được học.
- Exact lookup baseline cho thấy token slots còn giữ information nào; nó không chứng minh Transformer tự học được lookup policy đó.
- Code chạy FP64 để test algebra, không benchmark production kernel, BF16 stability hay throughput.

### 9.3 Runnable PyTorch code

```python
from dataclasses import dataclass

import torch


torch.set_default_dtype(torch.float64)


def one_hot(index: int, size: int) -> torch.Tensor:
    return torch.nn.functional.one_hot(
        torch.tensor(index), num_classes=size
    ).to(torch.get_default_dtype())


class TokenLevelKV:
    """
    Oracle latest-match retrieval over separate token slots.

    This isolates storage capacity. Standard attention would learn a scoring
    policy over retained slots rather than receive exact integer-key matching.
    """

    def __init__(self):
        self.slots = []  # list[(logical_key: int, value: Tensor)]

    def write(self, logical_key: int, value: torch.Tensor) -> None:
        self.slots.append((logical_key, value.clone()))

    def read(self, logical_key: int) -> torch.Tensor:
        for stored_key, stored_value in reversed(self.slots):
            if stored_key == logical_key:
                return stored_value.clone()
        raise KeyError(logical_key)

    @property
    def state_elements(self) -> int:
        # Count values only; real KV cache also stores key vectors/metadata.
        return sum(value.numel() for _, value in self.slots)


@dataclass
class FixedAssociativeMemory:
    d_address: int
    d_value: int

    def __post_init__(self):
        self.state = torch.zeros(self.d_address, self.d_value)

    def read(self, address: torch.Tensor) -> torch.Tensor:
        return address @ self.state

    def write_additive(
        self, address: torch.Tensor, value: torch.Tensor
    ) -> None:
        self.state = self.state + torch.outer(address, value)

    def write_delta(
        self,
        address: torch.Tensor,
        value: torch.Tensor,
        beta: float = 1.0,
        alpha: torch.Tensor | None = None,
    ) -> None:
        if alpha is None:
            alpha = torch.ones(self.d_address)
        if alpha.shape != (self.d_address,):
            raise ValueError("alpha must have shape (d_address,)")

        # KDA-like ordering: channel-wise decay, then delta correction.
        decayed = alpha[:, None] * self.state
        prediction = address @ decayed
        error = value - prediction
        self.state = decayed + beta * torch.outer(address, error)

    @property
    def state_elements(self) -> int:
        return self.state.numel()


def is_exact(actual: torch.Tensor, expected: torch.Tensor) -> bool:
    return torch.allclose(actual, expected, rtol=0.0, atol=1e-10)


def decoded_id(value: torch.Tensor) -> int:
    return int(value.argmax())


# ------------------------------------------------------------------
# Experiment 1: exact recall with orthogonal addresses and enough state.
# ------------------------------------------------------------------
d_address = 4
d_value = 4
kv = TokenLevelKV()
delta = FixedAssociativeMemory(d_address, d_value)

for key_id in range(4):
    address = one_hot(key_id, d_address)
    value = one_hot(key_id, d_value)
    kv.write(key_id, value)
    delta.write_delta(address, value, beta=1.0)

for key_id in range(4):
    expected = one_hot(key_id, d_value)
    assert is_exact(kv.read(key_id), expected)
    assert is_exact(delta.read(one_hot(key_id, d_address)), expected)

print("E1: both memories recall 4/4 with orthogonal addresses")


# ------------------------------------------------------------------
# Experiment 2: repeated-key overwrite.
# ------------------------------------------------------------------
old_value = one_hot(0, d_value)
new_value = one_hot(1, d_value)
address = one_hot(0, d_address)

kv_overwrite = TokenLevelKV()
kv_overwrite.write(0, old_value)
kv_overwrite.write(0, new_value)

additive = FixedAssociativeMemory(d_address, d_value)
additive.write_additive(address, old_value)
additive.write_additive(address, new_value)

corrective = FixedAssociativeMemory(d_address, d_value)
corrective.write_delta(address, old_value, beta=1.0)
corrective.write_delta(address, new_value, beta=1.0)

print("E2 token latest:", kv_overwrite.read(0).tolist())
print("E2 additive:    ", additive.read(address).tolist())
print("E2 delta:       ", corrective.read(address).tolist())

assert is_exact(kv_overwrite.read(0), new_value)
assert not is_exact(additive.read(address), new_value)
assert is_exact(corrective.read(address), new_value)


# ------------------------------------------------------------------
# Experiment 3: two logical keys collide at exactly the same address.
# ------------------------------------------------------------------
collision_address = one_hot(0, d_address)
value_a = one_hot(2, d_value)
value_b = one_hot(3, d_value)

kv_collision = TokenLevelKV()
kv_collision.write(100, value_a)
kv_collision.write(200, value_b)

fixed_collision = FixedAssociativeMemory(d_address, d_value)
fixed_collision.write_delta(collision_address, value_a)
fixed_collision.write_delta(collision_address, value_b)

assert is_exact(kv_collision.read(100), value_a)
assert is_exact(kv_collision.read(200), value_b)
assert not is_exact(fixed_collision.read(collision_address), value_a)
assert is_exact(fixed_collision.read(collision_address), value_b)

print("E3 token slots retain A and B; fixed state retains latest collision")


# ------------------------------------------------------------------
# Experiment 4: decay trades retention for forgetting.
# ------------------------------------------------------------------
decaying = FixedAssociativeMemory(d_address, d_value)
key_a = one_hot(0, d_address)
key_b = one_hot(1, d_address)
decaying.write_delta(key_a, value_a)

alpha = torch.full((d_address,), 0.5)
decaying.write_delta(key_b, value_b, alpha=alpha)

read_a = decaying.read(key_a)
assert not is_exact(read_a, value_a)  # old association was scaled by 0.5
print("E4 old value after decay:", read_a.tolist())


# Persistent-state trend. Fixed count is independent of writes.
print("KV value elements after 4 writes:", kv.state_elements)
print("fixed-state elements:             ", delta.state_elements)
kv.write(99, one_hot(0, d_value))
assert kv.state_elements == 5 * d_value
assert delta.state_elements == d_address * d_value
```

### 9.4 Expected output

```text
E1: both memories recall 4/4 with orthogonal addresses
E2 token latest: [0.0, 1.0, 0.0, 0.0]
E2 additive:     [1.0, 1.0, 0.0, 0.0]
E2 delta:        [0.0, 1.0, 0.0, 0.0]
E3 token slots retain A and B; fixed state retains latest collision
E4 old value after decay: [0.0, 0.0, 0.5, 0.0]
KV value elements after 4 writes: 16
fixed-state elements:              16
```

Sau write thứ năm, `TokenLevelKV.state_elements` tăng lên 20, còn fixed state vẫn là 16. Đừng so hai con số tuyệt đối như production memory: baseline đã cố ý không đếm key vectors, layer/head/batch dimensions, dtype và allocator. Điều cần quan sát là **slope theo số writes**.

## 10. Đọc kết quả mini-project đúng cách

### Experiment 1: fixed state không mặc định kém

Khi có đủ orthogonal addresses, delta memory exact recall hoàn hảo trong toy algebra. Fixed state có thể rất hiệu quả nếu task-relevant state fit vào dimensions và learned representation tách được associations.

### Experiment 2: delta tạo overwrite semantics

Additive memory trả $v_{old}+v_{new}$. Delta correction đọc prediction cũ và ghi residual, nên với normalized key và $\beta=1$, output trở thành chính xác $v_{new}$.

Token-level baseline cũng trả value mới vì retrieval policy quét từ slot mới nhất. Lưu ý standard softmax attention không tự có policy này chỉ vì cache tồn tại; model vẫn phải dùng content/position để chọn slot đúng.

### Experiment 3: collision là information loss

Hai logical keys dùng cùng address nhưng values khác nhau. Fixed state không thể biết query muốn key 100 hay 200 vì hai queries nhìn giống hệt nhau trong address space. Delta rule chọn latest association cho direction đó, đồng thời phá recall của association trước.

Token cache giữ cả hai writes ở slots riêng. Đây là động cơ representation-level cho periodic token-addressable attention.

### Experiment 4: decay không miễn phí

Global decay 0.5 giúp old state nhỏ đi, nhưng exact old value cũng giảm một nửa. Trong KDA thật, channel-wise gate được học và phụ thuộc input, nên model có thể chọn quên/giữ tinh vi hơn toy scalar-like vector. Dù vậy, learned gate không tạo guarantee rằng mọi old fact quan trọng sẽ được giữ.

## 11. Capacity stress mở rộng

Thay exact collision bằng nhiều random normalized addresses để quan sát gradual interference:

```python
def random_unit_addresses(n_keys: int, d_address: int, seed: int = 0):
    generator = torch.Generator().manual_seed(seed)
    addresses = torch.randn(n_keys, d_address, generator=generator)
    return addresses / addresses.norm(dim=-1, keepdim=True)


def delta_recall_accuracy(n_keys: int, d_address: int) -> float:
    # One-hot values let argmax act as a discrete recall decision.
    memory = FixedAssociativeMemory(d_address, n_keys)
    addresses = random_unit_addresses(n_keys, d_address)

    for key_id in range(n_keys):
        memory.write_delta(addresses[key_id], one_hot(key_id, n_keys))

    correct = 0
    for key_id in range(n_keys):
        prediction = memory.read(addresses[key_id])
        correct += decoded_id(prediction) == key_id
    return correct / n_keys


for width in (8, 16, 32, 64):
    accuracy = delta_recall_accuracy(n_keys=64, d_address=width)
    print(f"d_address={width:2d} | recall={accuracy:.3f}")
```

Không hard-code expected accuracy: kết quả phụ thuộc seed, write order, value coding và metric. Hãy chạy nhiều seeds, báo mean/std và plot:

- x-axis: số keys hoặc số writes;
- y-axis: exact-match accuracy và MSE;
- các curves: address width 8, 16, 32, 64;
- baseline: token-level latest-match lookup;
- variants: additive, delta, scalar decay, channel-wise decay.

### Questions cần trả lời trong report

1. Khi nào delta memory đạt exact recall?
2. Accuracy giảm ra sao khi số keys lớn hơn address width?
3. Repeated-key overwrite khác collision giữa hai logical keys như thế nào?
4. Decay nào cải thiện recent recall nhưng làm hỏng old recall?
5. State elements tăng theo context ở từng baseline ra sao?
6. Kết quả nào là algebraic guarantee, kết quả nào chỉ là empirical observation?

## 12. Nếu muốn gần KDA thật hơn

Mini-project chưa học gates. Có thể mở rộng bằng một small controller:

```python
beta_t = torch.sigmoid(beta_proj(x_t))       # scalar per head
alpha_t = torch.sigmoid(alpha_proj(x_t))     # vector per key channel
```

Sau đó train end-to-end trên sequence gồm `WRITE`, `QUERY`, repeated overwrite và distractors. Cần tách datasets:

- train length và longer test length;
- seen và unseen key/value combinations;
- recall without overwrite;
- overwrite cùng key;
- collision/capacity stress;
- recent versus distant query.

Đừng gọi toy này là KDA đầy đủ nếu thiếu learned Q/K/V projections, normalization, short convolution, output gate, multi-head composition và chunkwise training algorithm.

## 13. Vì sao mini-project giải thích hybrid architecture?

Toy experiments tạo ba vùng behavior:

1. **State đủ và addresses tách tốt:** fixed delta memory recall chính xác với state bounded.
2. **Overwrite cùng address đúng semantics:** delta correction thắng additive update.
3. **Nhiều distinct items vượt separability:** associations interfere/collide; không update rule nào phục hồi identity đã bị nén mất.

Hybrid KDA–MLA khai thác vùng 1–2 ở phần lớn layers, nhưng không đặt cược toàn bộ model vào việc mọi long-context detail luôn fit vào vùng đó. Periodic global MLA layers giữ per-token candidates để network có cơ hội truy xuất fine-grained evidence sau khi KDA layers đã thực hiện recurrent mixing.

MLA không phải một “backup database” được gọi conditionally trong Kimi Linear. Hai loại layers nối tiếp trong network; hidden states được biến đổi qua cả hai pathways. Mini-project chỉ minh họa trade-off storage/retrieval, không mô phỏng đầy đủ information flow giữa layers.

## 14. Complexity và serving implications

Bỏ qua batch/layer/head factors:

| Mechanism | Persistent decode state | New-token history access | Retrieval risk chính |
|---|---:|---:|---|
| MHA KV cache | $O(T(d_k+d_v))$ | $O(T)$ slots | bandwidth/cache growth |
| MLA cache | $O(Tr)$ | $O(T)$ compressed slots | low-rank per-token compression + cache growth |
| Delta/KDA state | $O(d_kd_v)$ | fixed-shape state | interference, decay, capacity |
| Hybrid KDA–MLA | fixed KDA states + MLA cache ở một số layers | mixed | cả hai trade-offs, nhưng ít global-cache layers hơn |

Kimi Linear report đo speedups và cache reduction cho full model/configuration của họ. Không suy throughput chỉ từ Big-O: kernels, batch size, context, dtype, hardware, MoE, short convolution và memory allocator đều ảnh hưởng.[^kimi-linear-2025]

## 15. Những hiểu lầm thường gặp

1. **“Delta rule làm fixed state lossless.”** Sai. Nó sửa addressed association; overlapping addresses vẫn gây collateral update.
2. **“Decay tăng capacity mà không mất gì.”** Sai. Forgetting dọn state bằng cách giảm old information.
3. **“Channel-wise decay tạo một slot cho mỗi token.”** Sai. State vẫn không có sequence axis.
4. **“MLA là fixed-state vì dùng latent.”** Sai. MLA giữ một latent trên mỗi token.
5. **“Periodic MLA nghĩa là thỉnh thoảng mới xử lý token.”** Sai. Periodic mô tả pattern theo layer depth.
6. **“3:1 luôn tối ưu.”** Sai. Đây là empirical choice trong Kimi Linear recipe.
7. **“KV cache bảo đảm exact recall.”** Sai. Nó giữ candidate slots; scoring/retrieval vẫn có thể sai.
8. **“Hybrid có constant total cache.”** Sai. Periodic MLA layers vẫn có cache tăng theo context.
9. **“Toy latest-match KV là softmax attention.”** Sai. Nó là oracle storage baseline để tách storage khỏi learned retrieval.
10. **“Chunkwise training đổi recurrence.”** Không nên mặc định. Mục tiêu của derivation/kernel là tính cùng recurrence hiệu quả hơn; equivalence phải được kiểm chứng theo implementation và precision.[^parallel-deltanet-2024][^kimi-linear-2025]

## 16. Checklist khi đọc delta/hybrid paper

1. State có shape gì và có sequence axis không?
2. Update là additive, delta, decay hay cả hai?
3. Delta prediction đọc trước hay sau decay?
4. $\beta$ là scalar, vector hay matrix; có nằm trong $[0,1]$ không?
5. $\alpha$ là scalar per head hay channel-wise vector?
6. Keys có được normalize không?
7. Training/prefill dùng recurrent hay chunkwise algorithm?
8. Decode cache còn short-convolution state hoặc auxiliary state nào?
9. Hybrid là headwise hay layerwise?
10. Global attention là MHA, GQA, MLA, local hay sparse attention?
11. “Periodic” được định nghĩa theo depth hay time?
12. Benchmark có `exact copy`, MQAR, overwrite và distractors không?
13. Ratio ablation có matched compute/model/data không?
14. Efficiency number là theoretical FLOPs, batch-one latency hay max throughput?
15. Claim là derivation, author-run experiment hay independent replication?

## 17. Bài tập cuối bài

1. **Partial overwrite:** chạy $\beta\in\{0,0.25,0.5,1\}$ và plot MSE sau mỗi repeated write.
2. **Selective decay:** đặt $\alpha=[1,1,0.1,0.1]$; kiểm tra channels nào giữ association lâu hơn.
3. **Non-orthogonal keys:** thay one-hot addresses bằng vectors có cosine similarity được kiểm soát và đo collateral update.
4. **Latest versus first occurrence:** sửa token baseline để chọn first match, latest match và softmax mixture; giải thích retrieval policy khác storage layout.
5. **Memory crossover:** thêm key element count và tìm context $T$ nơi token cache lớn hơn matrix state.
6. **Long-range overwrite:** chèn hàng nghìn distractor writes giữa old và new value; đo recent/old recall.
7. **Hybrid thought experiment:** giữ một small exact token buffer cạnh fixed state và thay buffer size. Ghi rõ đây là local-cache toy, không phải Kimi Linear layerwise MLA.
8. **Train gates:** học $\alpha_t,\beta_t$ trên synthetic WRITE/QUERY task và test length extrapolation.
9. **Recurrent equivalence:** tạo explicit prefix reference cho recurrence và so với online update bằng `torch.testing.assert_close`.
10. **Evidence review:** đối chiếu synthetic KDA tasks với end-to-end long-context benchmarks; không dùng một bên để chứng minh bên kia.

## 18. Tóm tắt

- Additive associative memory cộng mọi writes và không tự hiểu overwrite.
- Delta rule đọc value hiện tại, tính error và ghi correction theo key direction.
- $\beta_t$ điều khiển strength của correction; decay $\alpha_t$ điều khiển retention.
- Gated DeltaNet dùng scalar decay; KDA dùng channel-wise decay để quản lý state chi tiết hơn.
- Fixed matrix state giữ bounded decode state nhưng nhiều associations vẫn superpose, nên interference và capacity limits còn tồn tại.
- MLA giữ compressed per-token entries và global token-level scoring; cache nhỏ hơn MHA trên mỗi token nhưng vẫn tăng theo context.
- Kimi Linear xen `3 KDA layers → 1 MLA layer` theo network depth để đổi phần lớn sequence-growing cache lấy fixed state mà vẫn giữ periodic global retrieval.
- Mini-project cho thấy delta correction giải quyết overwrite trong điều kiện lý tưởng, nhưng exact-address collision vẫn làm fixed state mất khả năng phân biệt.
- Token slots giữ evidence riêng; retrieval correctness vẫn phải được model học và không được KV cache tự bảo đảm.

## Relationships

- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng lý thuyết delta/KDA và mini-project exact recall/overwrite.
- **Builds on:** [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) và [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md).
- **Contrasts with:** [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md), nơi mỗi token vẫn có compressed cache entry riêng.
- **Explains:** [Kimi Linear hybrid attention architecture](kimi-linear-hybrid-attention-architecture.md), đặc biệt pattern layerwise 3:1 và retrieval-versus-memory trade-off.
- **Supported by:** [Gated DeltaNet evaluation and hybrid trade-offs](gated-deltanet-evaluation-and-hybrid-trade-offs.md), where adding token-addressable attention improves reported retrieval and long-context results under that paper's setup.

## Evidence limits

Delta update, associative-memory interpretation và orthogonality argument đến từ primary fast-weight/DeltaNet papers. Scalar decay evidence đến từ Gated DeltaNet; channel-wise KDA recurrence, 3:1 hybrid, synthetic tasks, ratio ablation và efficiency claims đến từ Kimi Linear primary report. Các papers cung cấp author-run results, không phải independent replication. Derivations in this course follow the documented recurrences; the oracle KV baseline, collision experiments, code organization, expected outputs and teaching sequence are **pedagogical synthesis**. Chúng minh họa representation trade-offs, không dự đoán trực tiếp perplexity, long-context benchmark score hoặc production speed.[^fast-weight-programmers-2021][^parallel-deltanet-2024][^gated-deltanet-2025][^kimi-linear-2025]

[^fast-weight-programmers-2021]: Imanol Schlag, Kazuki Irie, and Jürgen Schmidhuber, “Linear Transformers Are Secretly Fast Weight Programmers,” ICML 2021, [source](../raw/arXiv-2102.11174v3/main.tex), Sections 3–4 and Appendices A–B.
[^parallel-deltanet-2024]: Songlin Yang, Bailin Wang, Yu Zhang, Yikang Shen, and Yoon Kim, “Parallelizing Linear Transformers with the Delta Rule over Sequence Length,” NeurIPS 2024, [source](../raw/arXiv-2406.06484v6/neurips_2024.tex), Sections 2–3 and appendices.
[^gated-deltanet-2025]: Songlin Yang, Jan Kautz, and Ali Hatamizadeh, “Gated Delta Networks: Improving Mamba2 with Delta Rule,” ICLR 2025, [source](../raw/arXiv-2412.06464v3/main.tex), Sections 3–5 and Appendix A.
[^kimi-linear-2025]: Kimi Team, “Kimi Linear: An Expressive, Efficient Attention Architecture,” arXiv:2510.26692v2, [source](../raw/arXiv-2510.26692v2/main.tex), especially Sections 2–6 and the chunkwise derivation appendices.
