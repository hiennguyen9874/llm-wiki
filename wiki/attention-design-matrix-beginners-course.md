---
type: Synthesis
title: "Attention design matrix — khóa học cho người mới"
description: A beginner-first course for separating positional mechanisms, KV representation, and token-access patterns, then evaluating their effects on logits, cache state, addressability, and long-context cost.
tags: [attention, positional-encoding, kv-cache, sparse-attention, long-context, pytorch, learning-roadmap]
status: stable
created: 2026-08-15
generated:
  by: llm-wiki-agent/1
  at: 2026-08-15T00:00:00+00:00
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: rope-summary
    resource: ../raw/RoPE.md
    title: "RoPE overview (Vietnamese summary)"
  - id: alibi-summary
    resource: ../raw/ALiBi.md
    title: "ALiBi overview (Vietnamese summary)"
  - id: mqa-summary
    resource: ../raw/MQA.md
    title: "MQA overview (Vietnamese summary)"
  - id: gqa-summary
    resource: ../raw/GQA.md
    title: "GQA overview (Vietnamese summary)"
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2-2025
    resource: ../raw/arXiv-2512.02556v1/main.tex
    title: "DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models"
  - id: deepseek-v4-2026
    resource: ../raw/arXiv-2606.19348v1/main.tex
    title: "DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence"
---

# Attention design matrix — khóa học cho người mới

Khi đọc một `attention` design, đừng hỏi ngay “cơ chế nào tốt nhất?”. Trước hết hãy đặt nó vào ba trục độc lập: **positional mechanism** đưa position vào score ở đâu; **KV representation** quyết định mỗi token được giữ lại dưới dạng bao nhiêu bytes; và **token-access pattern** quyết định query được đọc những token/block nào. `RoPE` và `ALiBi` thuộc trục thứ nhất; MHA/MQA/GQA/MLA thuộc trục thứ hai; full attention, DSA, CSA/HCA thuộc trục thứ ba. Một model có thể kết hợp một lựa chọn từ mỗi trục, nên không được gán lợi ích của một trục cho trục khác.[^rope-summary][^alibi-summary][^deepseek-v2-2024][^deepseek-v3-2-2025][^deepseek-v4-2026]

> [!success] Mục tiêu
> Sau bài này, bạn có thể: (1) lập `attention design matrix` cho một checkpoint hoặc paper; (2) chỉ ra chính xác cơ chế nào đổi logits, cache bytes, hay set token được đọc; (3) phân biệt `per-token compression` với `fixed-state`; (4) tính raw KV-cache memory; và (5) chọn đúng test trước khi nói một design cải thiện `long context`.

Đây là bài học tích hợp cho Stage 6.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Bạn nên biết `Q/K/V`, `softmax`, causal mask, và `KV cache`; nếu chưa, hãy học [Attention: beginner's guide](attention-beginner-guide.md) và [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) trước.

## 1. Baseline: causal MHA có những phần nào?

Với hidden states $X\in\mathbb{R}^{B\times T\times D}$, mỗi attention layer chiếu chúng thành `Query`, `Key`, `Value` rồi chia thành $H_Q$ heads, mỗi head có width $d_h$. Với một query token $t$ và key token $j$:

$$
q_t=X_tW_Q,\qquad k_j=X_jW_K,\qquad v_j=X_jW_V,
$$

$$
s_{t,j}=\frac{q_tk_j^\top}{\sqrt{d_h}}+M_{t,j},
\qquad
\alpha_{t,j}=\operatorname{softmax}_j(s_{t,j}),
\qquad
o_t=\sum_j\alpha_{t,j}v_j.
$$

`Causal mask` $M_{t,j}$ đặt future keys ($j>t$) thành $-\infty$. Nó là quy tắc **được phép đọc gì**, không phải positional encoding: ngay cả khi dùng RoPE hoặc ALiBi, causal language model vẫn cần causal mask.[^vaswani-transformer-2017]

Khi autoregressive `decode`, K/V của prefix đã tính được giữ theo từng layer trong `KV cache`. Với batch $B$, layers $L$, cached length $S$, KV-head count $H_{KV}$, dtype width $p$ bytes, raw cache của MHA là:

$$
M_{KV}\approx 2BLSH_{KV}d_hp.
$$

MHA có $H_{KV}=H_Q$. Công thức này là baseline để xem một design thực sự thay đổi gì: position rule không tự làm $H_{KV}$ nhỏ hơn, và cache compression không tự cấm query đọc future token.

```text
new hidden state
  ├─ Q projection ──► positional mechanism ──────────────┐
  ├─ K projection ──► positional mechanism ──► KV cache ─┼─ score/select/softmax ─► output
  └─ V projection ───────────────────────────► KV cache ─┘
                         ^                         ^                 ^
                    axis 1: position        axis 2: state      axis 3: access
```

## 2. Ba trục của `attention design matrix`

### Trục A — `positional mechanism`: position thay đổi score như thế nào?

Trục này trả lời: *position đi vào Q/K, hidden state, hay logits?* Nó thường thay đổi **attention logits**, không trực tiếp đổi số cache entries.

| Choice | Position đi vào đâu? | Score thay đổi thế nào? | Cần nhớ |
|---|---|---|---|
| Sinusoidal / learned absolute embedding | cộng vào input representation trước Q/K/V projection | Q/K học position gián tiếp từ input | learned table có thể có maximum trained table length; sinusoidal formula tính được ở position mới nhưng quality vẫn là vấn đề training |
| `RoPE` | xoay từng coordinate pair của projected Q và K | dot product chứa relative offset | cache giữ K đã rotate ở absolute position của token |
| `ALiBi` | cộng bias theo distance trực tiếp vào logit | distant past keys chịu head-specific linear penalty | là soft recency preference, không phải local mask |

### Trục B — `KV representation`: mỗi token được giữ lại như thế nào?

Trục này trả lời: *một token mới tăng cache bao nhiêu elements?* Nó thay đổi **retained state per token** và K/V bandwidth khi decode. Những design dưới đây vẫn có entry theo sequence position; không cái nào tự trở thành `fixed-state memory`.

| Choice | Cache entry của một token | Per-token width (minh họa) | Token-addressable? |
|---|---|---:|---|
| MHA | K và V riêng cho từng query head | $2H_Qd_h$ | Có |
| MQA | một K head và một V head share bởi mọi query head | $2d_h$ | Có |
| GQA | $H_{KV}$ K/V heads, mỗi head phục vụ một group query heads | $2H_{KV}d_h$ | Có |
| MLA | joint `KV latent` cộng decoupled rotary key | $d_c+d_h^R$ | Có |

### Trục C — `token-access pattern`: query đọc entries nào?

Trục này trả lời: *sau khi cache đã tồn tại, query đang score/retrieve toàn bộ history, một selected subset, hay compressed blocks?* Nó tác động trực tiếp đến **attention work**, retrieval granularity, và đôi khi cache layout.

| Choice | Query đọc gì? | Main attention work | Điều bị đánh đổi |
|---|---|---|---|
| Full global attention | mọi prior token entry | $O(L^2)$ trên full sequence | quadratic work; token-level retrieval được giữ nguyên |
| DSA | `top-k` token-level MLA entries do indexer chọn | core attention $O(Lk)$ | indexer vẫn có pass quadratic lower-cost; token bị bỏ không vào core attention |
| CSA | `top-k` compressed entries, cộng local uncompressed window | sparse over compressed entries | remote token-level identity trong block bị lossy aggregate |
| HCA | dense over heavily compressed entries, cộng local window | dense trên số entries đã nén | remote history không còn one-entry-per-token |

> [!important] Một sentence, một trục
> “ALiBi lowers KV cache” là sai category: ALiBi chỉ thêm logit bias. “GQA makes attention sub-quadratic” cũng sai: GQA giảm K/V heads, nhưng every query head vẫn score history. “DSA makes cache fixed-size” cũng sai: DSA chọn ít entries để core attention đọc, nhưng MLA entries retained vẫn grow with context.[^alibi-summary][^mqa-summary][^deepseek-v3-2-2025]

## 3. Trục A chi tiết: `positional mechanism`

### 3.1. Absolute position: position đi vào representation trước attention

Trong original Transformer, sinusoidal positional vectors được cộng vào token embeddings trước stack layers. Một learned absolute embedding làm cùng vị trí đó trong computation graph nhưng vector là parameter được học. Sau phép cộng $h_t=x_t+p_t$, Q/K/V projections nhận representation đã có position.[^vaswani-transformer-2017]

Điểm cần phân biệt:

- `causal mask` chỉ nói token $t$ không được nhìn token $>t$;
- absolute embedding nói “đây là position $t$” trước khi Q/K/V được tạo;
- quality ở context dài hơn training length không thể suy ra chỉ từ việc code có thể tạo position IDs.

### 3.2. `RoPE`: rotate Q/K, tạo relative-position term

Với mỗi 2D pair, RoPE quay Q và K ở position $m$ theo angle $m\theta$. Nếu $R_m$ là rotation matrix:

$$
\tilde q_m=R_mq_m,\qquad \tilde k_n=R_nk_n,
$$

$$
\tilde q_m^\top\tilde k_n=q_m^\top R_{n-m}k_n.
$$

Hai absolute rotations rút gọn thành relative offset $n-m$. Vì vậy position nằm trong dot product, thay vì được cộng thành position vector ở input. Standard RoPE thường rotate Q/K sau projection và không rotate V.[^rope-summary]

Trong `KV cache`, old K đã rotate theo absolute position cũ. Decode token mới phải dùng position tiếp nối prefix, không reset về zero. Nếu prompt cache dài 100 tokens, token kế tiếp dùng position 100. Quy tắc này đặc biệt quan trọng khi compare cached vs uncached logits.[^rope-summary]

`RoPE` có thể evaluate sin/cos ở position vượt training context, nhưng đây là **mechanical extrapolation**, không phải guarantee về retrieval quality. Scaling variant, base/frequency, training data và long-context fine-tuning là các biến khác.[^rope-summary]

### 3.3. `ALiBi`: thêm recency bias vào logits

ALiBi giữ Q/K projections bình thường, nhưng đổi logit của causal attention head $h$ thành:

$$
s_{i,j}^{(h)}=\frac{q_i^{(h)\top}k_j^{(h)}}{\sqrt{d_h}}-m_h(i-j),\qquad j\le i.
$$

$m_h>0$ là slope cố định của head. Key càng xa trong past có penalty âm càng lớn; content match đủ mạnh vẫn có thể thắng penalty. Do đó ALiBi không phải hard `sliding-window attention`.[^alibi-summary]

ALiBi không có learned positional table và rule chỉ phụ thuộc relative distance, nên same rule áp dụng được ở distance dài hơn training. Nhưng full dense score matrix vẫn quadratic, và monotonic recency preference có thể gây bất lợi cho evidence ở rất xa.[^alibi-summary]

### 3.4. So sánh đúng câu hỏi

| Câu hỏi | Absolute embedding | RoPE | ALiBi |
|---|---|---|---|
| Position được inject ở đâu? | input representation | Q/K vectors | attention logits |
| Tạo relative signal trực tiếp? | không theo formula mặc định | có, qua rotation algebra | có, qua distance bias |
| Có đổi K/V cache width? | không | không theo standard RoPE | không |
| Có thay causal mask? | không | không | không |
| Có tự đảm bảo long-context quality? | không | không | không |

Đừng compare RoPE và ALiBi bằng câu “cái nào encode position tốt hơn” mà thiếu checkpoint, training length, task, context distribution, and evaluation protocol. Đây là architecture/training choices; không phải drop-in switch cho pretrained weights.

## 4. Trục B chi tiết: `KV-head sharing` và `latent KV`

### 4.1. MHA → MQA → GQA: thay số K/V subspaces

MHA dùng một K/V head cho mỗi query head: $H_{KV}=H_Q$. MQA giữ $H_Q$ query heads nhưng tất cả share một K head và một V head: $H_{KV}=1$. GQA là điểm giữa, với $1<H_{KV}<H_Q$.

Nếu group size $R=H_Q/H_{KV}$, query head $i$ của GQA dùng KV head:

$$
g(i)=\left\lfloor\frac{i}{R}\right\rfloor.
$$

Query heads vẫn khác nhau và có thể tạo attention weights khác nhau. Phần được share là key representation để match và value representation để retrieve.[^mqa-summary][^gqa-summary]

```text
MHA, H_Q=8:    Q0→KV0, Q1→KV1, ..., Q7→KV7
GQA, H_KV=2:   Q0..Q3→KV0; Q4..Q7→KV1
MQA, H_KV=1:   Q0..Q7→KV0
```

Vì raw cache scales linearly with $H_{KV}$, GQA-8 với $H_Q=32$ giữ khoảng $8/32=25\%$ raw K/V tensor bytes của MHA, nếu all other dimensions giống nhau. Đây là memory accounting, không phải promise latency giảm bốn lần: attention-score work vẫn có $H_Q$ query heads, và kernel/hardware/batch/context quyết định decode time.[^mqa-summary][^gqa-summary]

### 4.2. `MLA`: nén representation của từng token, không share whole K/V heads

`Multi-head Latent Attention` (MLA) down-project hidden state của mỗi token thành joint latent $c_t^{KV}$ rồi dùng learned up-projections để biểu diễn content K/V. Decode cache giữ latent nhỏ đó thay vì expanded K/V của từng head. Để RoPE không cản matrix absorption, MLA tách một shared rotary key path; cache giữ latent cộng rotary key.[^deepseek-v2-2024]

$$
\text{MLA cache/token/layer}=d_c+d_h^R.
$$

MLA khác MQA/GQA ở chỗ nó không đơn giản giảm số whole K/V heads; nó thay representation per token bằng low-rank joint latent. Tuy nhiên, cả hai family cùng trả lời trục B: cache vẫn có sequence axis $S$, và query vẫn có thể score một entry riêng cho token $j$.

> [!warning] `latent` không có nghĩa là một vector tóm tắt cả context
> MLA có **một latent entry cho mỗi token** ở mỗi MLA layer. Sau $S$ tokens, cache vẫn có $S$ entries; cache bytes và history reads vẫn grow linearly with $S$. Xem [MLA và token-addressable memory — bài học cho người mới](mla-token-addressable-memory-beginners-guide.md).

### 4.3. Memory example

Giả sử $B=1$, $L=32$, $S=4096$, $H_Q=32$, $d_h=128$, BF16 ($p=2$ bytes):

| Layout | $H_{KV}$ hoặc width | Raw cache formula | Raw cache |
|---|---:|---:|---:|
| MHA | $H_{KV}=32$ | $2BLS(32)(128)p$ | 2 GiB |
| GQA-8 | $H_{KV}=8$ | $2BLS(8)(128)p$ | 512 MiB |
| MQA | $H_{KV}=1$ | $2BLS(1)(128)p$ | 64 MiB |
| MLA example | $d_c+d_h^R=576$ | $BLS(576)p$ | 144 MiB |

MLA row là một **chosen dimensional example**, không phải ratio chung. Raw tensor bytes không gồm model weights, allocator fragmentation, page/block metadata, temporary tensors, padding, hay prefix sharing.

## 5. Trục C chi tiết: full, sparse-selected, và compressed access

### 5.1. Full global attention giữ direct token retrieval

Full attention tạo one score per query–key pair. Với sequence length $L$, score matrix có quadratic size/work. Đổi positional mechanism hoặc GQA does not change the fact that a query can directly compare itself với từng token entry in history.[^vaswani-transformer-2017]

### 5.2. `DSA`: index, select, rồi core attention trên `top-k` token entries

DeepSeek Sparse Attention (DSA) dùng lightweight learned indexer để score prior token-level MLA entries, select top-$k$, rồi thực hiện core MQA chỉ trên set đó. Report mô tả core attention từ $O(L^2)$ thành $O(Lk)$, nhưng indexer itself remains a lower-cost quadratic pass. Vì vậy “DSA is linear attention” là kết luận sai.[^deepseek-v3-2-2025]

DSA vẫn dùng token-level MLA entries: token được select vẫn addressable individually. Khác biệt là một query không đưa every old token vào core softmax. Nếu indexer bỏ relevant token, core attention không thể retrieve nó ở step đó. Quality and serving claims cần được đọc cùng $k$, continued training, kernel, context, and workload của report.[^deepseek-v3-2-2025]

### 5.3. `CSA`/`HCA`: nén groups token thành entries, giữ local window

DeepSeek-V4 mô tả `Compressed Sparse Attention` (CSA) và `Heavily Compressed Attention` (HCA): thay vì một cache representation riêng cho every remote token, model tạo learned compressed entry cho groups tokens và vẫn giữ local uncompressed window.

- CSA: compression modest (reported $m=4$), indexer selects top-$k$ compressed entries.
- HCA: much heavier compression (reported $m'=128$), attention densely reads compressed entries.
- Both: reported local sliding-window branch giữ detail gần query.[^deepseek-v4-2026]

Khác với DSA, remote history của CSA/HCA không nhất thiết còn one cache entry per token. Nén aggregation có thể giảm state/work, nhưng remote individual-token identity bị lossy. Local window không phải chỉ optimization: nó là part of design để preserve short-range detail mà aggressive compression có thể làm mất.[^deepseek-v4-2026]

### 5.4. Addressability ladder

```text
full MHA/GQA/MLA:  query → every token slot
DSA:               query → selected token slots
CSA:               query → selected compressed block slots + local token slots
HCA:               query → compressed block slots + local token slots
fixed-state:        query → one aggregated recurrent state (no independent token slots)
```

`fixed-state` được thêm vào ladder để tránh confusion, nhưng không phải một option của Stage 6.1 matrix. Nó thuộc long-context mixing: sequence axis bị loại khỏi retained state, đổi lại history associations superpose và no longer have independent token slots.[^deepseek-v2-2024]

## 6. Matrix hoàn chỉnh: đọc một design theo đúng dimension

| Design | Positional mechanism | KV representation | Access pattern | Cache growth theo context | Remote retrieval granularity |
|---|---|---|---|---|---|
| Standard MHA + RoPE | RoPE on Q/K | full per-head K/V | full global | linear, high slope | token |
| GQA + ALiBi | distance bias in logits | fewer shared K/V heads | full global | linear, lower slope | token |
| MLA + decoupled RoPE | RoPE in separate rotary path | per-token joint latent + rotary key | full global | linear, lower slope | token |
| DSA | architecture-specific position paths | MLA in MQA mode | top-$k$ token entries | linear retained cache | selected token |
| CSA/HCA | reported partial RoPE | compressed KV entries + local state | sparse/dense compressed entries + local window | compressed prefix plus local/tail state | block remotely, token locally |

Bảng này không nói quality ranking. Nó chỉ là **mechanism ledger**. Một modern model có thể mix rows: ví dụ shared-KV MQA có thể đồng thời dùng partial RoPE, learned compression, sparse indexer, and local window.[^deepseek-v4-2026]

## 7. PyTorch lab: lập matrix từ configuration và kiểm tra causal semantics

Code dưới đây không implement MLA/DSA production. Mục tiêu là biến design claims thành quantities có thể inspect: raw cache bytes, shape của retained state, and causal non-leakage. Dùng nó trước khi benchmark latency.

```python
from dataclasses import dataclass
import math
import torch
import torch.nn.functional as F


@dataclass(frozen=True)
class AttentionDesign:
    name: str
    position: str            # e.g. "rope", "alibi"
    kv_layout: str           # "mha", "gqa", "mqa", "mla"
    access: str              # "full", "top-k-token", "compressed-block"
    hq: int
    hkv: int | None = None
    head_dim: int | None = None
    latent_dim: int | None = None
    rotary_dim: int = 0


def cache_elements_per_token(design: AttentionDesign) -> int:
    """One layer, one sequence. This is retained-state accounting only."""
    if design.kv_layout in {"mha", "gqa", "mqa"}:
        assert design.hkv is not None and design.head_dim is not None
        return 2 * design.hkv * design.head_dim  # K plus V
    if design.kv_layout == "mla":
        assert design.latent_dim is not None
        return design.latent_dim + design.rotary_dim
    raise ValueError(f"unknown KV layout: {design.kv_layout}")


def raw_cache_bytes(design, batch, layers, context, bytes_per_element=2):
    return (batch * layers * context * cache_elements_per_token(design)
            * bytes_per_element)


mha = AttentionDesign("MHA + RoPE", "rope", "mha", "full", 32, 32, 128)
gqa = AttentionDesign("GQA-8 + ALiBi", "alibi", "gqa", "full", 32, 8, 128)
mqa = AttentionDesign("MQA + RoPE", "rope", "mqa", "full", 32, 1, 128)
mla = AttentionDesign("MLA + decoupled RoPE", "rope", "mla", "full", 32,
                      latent_dim=512, rotary_dim=64)

for d in (mha, gqa, mqa, mla):
    gib = raw_cache_bytes(d, batch=1, layers=32, context=4096) / 2**30
    print(f"{d.name:28s} {cache_elements_per_token(d):5d} elem/token/layer "
          f"{gib:.3f} GiB raw cache")
```

Expected interpretation:

- changing `position` from `rope` to `alibi` changes no value in this accounting;
- GQA/MQA reduce cache elements by reducing `hkv`;
- MLA has its own latent-plus-rotary cache width;
- changing `access` to `top-k-token` is not represented by cache bytes alone—measure or derive core attention work separately.

### A causal non-leakage test

Every causal variant—regardless of position, KV layout, or sparse access—must satisfy this invariant: changing future input must not change outputs at earlier positions. The following minimal full-attention function is intentionally simple; a real model additionally requires its exact RoPE/ALiBi/cache implementation tests.

```python
def causal_attention(q, k, v):
    """q, k, v: (B, H, T, d). Returns causal attention output."""
    _, _, T, d = q.shape
    logits = q @ k.transpose(-2, -1) / math.sqrt(d)
    causal = torch.ones(T, T, dtype=torch.bool, device=q.device).tril()
    logits = logits.masked_fill(~causal, float("-inf"))
    return F.softmax(logits, dim=-1) @ v


@torch.no_grad()
def test_future_perturbation_cannot_leak():
    torch.manual_seed(0)
    q = torch.randn(1, 2, 6, 4)
    k = torch.randn(1, 2, 6, 4)
    v = torch.randn(1, 2, 6, 4)
    before = causal_attention(q, k, v)

    # Replace only future K/V relative to output position t=2.
    k_changed, v_changed = k.clone(), v.clone()
    k_changed[:, :, 3:] = torch.randn_like(k_changed[:, :, 3:])
    v_changed[:, :, 3:] = torch.randn_like(v_changed[:, :, 3:])
    after = causal_attention(q, k_changed, v_changed)

    torch.testing.assert_close(before[:, :, :3], after[:, :, :3])


test_future_perturbation_cannot_leak()
```

Nếu test fail trong design thật, debug mask shape/orientation trước. RoPE and ALiBi are not substitutes for the mask. Với cached decode, thêm test thứ hai: full prefill output phải khớp prefix prefill + continuation decode của **cùng weights, same position IDs, same cache layout**. [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md) và [MQA/GQA: giảm KV cache khi decode — bài học cho người mới](mqa-gqa-kv-cache-decode-beginners-guide.md) có tests cụ thể hơn.

> [!warning] Không dùng output equality cho sai câu hỏi
> - MHA checkpoint và GQA checkpoint có parameter shapes/weights khác nhau; differing logits không chứng minh GQA bug.
> - Full attention và DSA intentionally read different key sets; equality không phải expected behavior.
> - Correctness cho một architecture là cached vs uncached execution của **cùng architecture**; quality comparison cần train/evaluate matched models.

## 8. Quy trình đánh giá trước khi kết luận một design “tốt hơn”

### Bước 1 — Ghi rõ baseline

Viết đủ: MHA hay GQA? full attention hay top-$k$? BF16 hay FP8? cache length, batch, hardware, and kernel là gì? “Memory reduced 90%” không có nghĩa nếu baseline không rõ.

### Bước 2 — Điền matrix theo mechanism, không theo tên marketing

| Câu hỏi | Evidence cần tìm |
|---|---|
| Position vào đâu? | formula Q/K rotation, input embedding, hoặc additive logit bias |
| Cache giữ tensor nào? | cache shape/formula, `H_KV`, latent/block width, dtype |
| Cache có sequence axis $S$ không? | retained-state shape sau $S$ tokens |
| Query score entries nào? | full range, top-$k$ indices, compressed blocks, local window |
| Có extra indexer/compression cost không? | complexity statement, kernel description, training recipe |
| Long-context claim được đo thế nào? | training length, eval context, task, throughput/cost protocol |

### Bước 3 — Test semantics trước, đo performance sau

1. Test causal non-leakage.
2. Test cached vs uncached outputs for exact same model.
3. Inspect retained cache shape/bytes and verify formula.
4. Measure `prefill` and one-token `decode` separately.
5. Only then compare task quality at target context lengths.

`Raw KV bytes`, peak GPU memory, `TTFT`, `TPOT`, throughput, and accuracy are different metrics. Không dùng một metric để claim metric khác.

### Bước 4 — Nêu trade-off đúng scope

- MQA/GQA can reduce decode cache bandwidth, but sharing may reduce representational capacity.
- MLA can reduce bytes per token while retaining token-addressable softmax attention, but cache still grows with context.
- DSA can reduce core attention work, but selected retrieval depends on its indexer and training recipe; it still has an indexer pass.
- CSA/HCA can reduce remote-entry count aggressively, but compression makes remote information lossy and relies on a local window for token-level detail.[^mqa-summary][^deepseek-v2-2024][^deepseek-v3-2-2025][^deepseek-v4-2026]

## 9. Các lỗi suy luận thường gặp

1. **“Position mechanism quyết định cache size.”** Thường sai. RoPE/ALiBi change scores, while MQA/GQA/MLA change retained representation.
2. **“GQA makes attention linear.”** Sai. It lowers KV-head count, not the number of query-to-history comparisons in full attention.
3. **“MLA is fixed-state.”** Sai. It stores a compressed latent per token; retained state still has length $S$.
4. **“Sparse attention has no quadratic component.”** Không tự suy ra được. DSA report explicitly retains a lower-cost quadratic indexer pass.[^deepseek-v3-2-2025]
5. **“Compressed block equals original tokens.”** Sai by default. Learned aggregation is lossy outside any retained local window.
6. **“A smaller raw cache guarantees lower end-to-end latency.”** Sai. Kernel, memory bandwidth, batch/concurrency, allocator, scheduler, and other layers can dominate.
7. **“A reported whole-model benchmark proves one component caused the gain.”** Không đủ evidence unless controlled ablation isolates that component.

## 10. Bài tập: tự lập matrix cho một model

1. Chọn [DeepSeek-V2 architecture, training, and efficiency](deepseek-v2-architecture-training-and-efficiency.md). Điền three axes cho MLA và ghi formula cache/token.
2. Chọn [DeepSeek Sparse Attention](deepseek-sparse-attention.md). Viết separately: `retained cache`, `indexer work`, `core attention work`, và retrieval unit.
3. Chọn [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md). Giải thích local window giải quyết loss nào của remote compression.
4. Sửa code lab để plot raw cache GiB against `context` cho MHA, GQA, MQA, and MLA. Chỉ ra design nào thay slope và design nào không.
5. Chạy causal test, rồi deliberately remove the mask. Giải thích vì sao positional mechanism không cứu được future leakage.
6. Với một target backend, benchmark separately: prompt `prefill`, fixed-cache one-token `decode`, retained KV bytes, and task quality. Record dtype, batch, context, GPU, and kernel.

## Kết luận

`Attention design matrix` giúp tách một architecture name thành các decisions kiểm chứng được:

```text
position:     How does position change the score?
KV state:     What does each token add to retained memory?
access:       Which entries can this query read?
```

Khi ba câu trả lời được tách riêng, bạn sẽ không nhầm `RoPE` với cache compression, GQA với sparse attention, hay MLA với fixed-state memory. Đây cũng là cách đọc long-context claims có kỷ luật: tìm formula, cache shape, selected set, and measurement protocol trước khi suy ra quality hoặc serving benefit.

## Relationships

- **Elaborates:** Stage 6.1 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) with a three-axis comparison and verification workflow.
- **Builds on:** [Rotary position embedding (RoPE)](rotary-position-embedding.md), [ALiBi attention with linear biases](alibi-attention-with-linear-biases.md), [Multi-query and grouped-query attention](multi-query-and-grouped-query-attention.md), and [Multi-head Latent Attention](multi-head-latent-attention.md).
- **Synthesizes:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md) and [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) as token-access alternatives rather than positional or KV-head-sharing alternatives.
- **Prepares for:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) and Stage 8 fixed-state long-context mixing.

## Evidence limits

Mechanism claims and formulas are supported by the cited concept sources. RoPE, ALiBi, MQA, and GQA primary papers have not all been independently ingested in this wiki; their relevant claims here come from the repository’s marked secondary summaries. DeepSeek MLA, DSA, CSA, and HCA details come from author technical reports. Their quality, throughput, and cost results are configuration-specific and author-reported; this course does not treat them as universal rankings. The matrix, code, memory examples, test procedure, and evaluation workflow are pedagogical synthesis.[^rope-summary][^alibi-summary][^mqa-summary][^gqa-summary][^deepseek-v2-2024][^deepseek-v3-2-2025][^deepseek-v4-2026]

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex), scaled dot-product attention, positional encoding, and decoder masking.
[^rope-summary]: “RoPE overview” (Vietnamese summary), [source](../raw/RoPE.md), Sections 1–17. Secondary evidence; the original RoFormer paper has not been independently ingested here.
[^alibi-summary]: “ALiBi overview” (Vietnamese summary), [source](../raw/ALiBi.md), Sections 1–18. Secondary evidence; the original ALiBi paper has not been independently ingested here.
[^mqa-summary]: “MQA overview” (Vietnamese summary), [source](../raw/MQA.md), Sections 1–14. Secondary evidence summarizing MQA and its decode trade-offs.
[^gqa-summary]: “GQA overview” (Vietnamese summary), [source](../raw/GQA.md), Sections 3–24. Secondary evidence summarizing GQA and checkpoint conversion evidence.
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex), Section 2.1 and appendices.
[^deepseek-v3-2-2025]: DeepSeek-AI, “DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models,” [source](../raw/arXiv-2512.02556v1/main.tex), Sections 2.1–2.3.
[^deepseek-v4-2026]: DeepSeek-AI, “DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence,” [source](../raw/arXiv-2606.19348v1/main.tex), Section 2.3 and Sections 4.5–4.6.
