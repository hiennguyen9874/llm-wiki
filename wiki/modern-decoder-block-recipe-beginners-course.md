---
type: Synthesis
title: "Modern decoder-block recipe: cấu hình, lý thuyết, và PyTorch cho người mới"
description: A beginner-first course on the interchangeable input/position, normalization, residual, FFN/gating, and embedding/output choices inside a modern decoder-only Transformer block.
tags: [decoder-only-transformer, decoder-block, rmsnorm, swiglu, rope, pytorch, learning-roadmap]
status: stable
created: 2026-08-15
generated:
  by: llm-wiki-agent/1
  at: 2026-08-15T11:06:51+07:00
sources:
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
  - id: llama-summary
    resource: ../raw/LLaMA.md
    title: "LLaMA overview (Vietnamese summary)"
  - id: huggingface-openai-gpt-pytorch
    resource: ../raw/gpt-source.py
    title: PyTorch OpenAI GPT model
---

# Modern decoder-block recipe: cấu hình, lý thuyết, và PyTorch cho người mới

Một `decoder block` hiện đại không chỉ là “`attention + FFN`”. Nó là một **recipe** gồm các lựa chọn phải khớp với nhau: token representation nhận position ở đâu; `normalization` đặt trước hay sau residual branch; dùng `LayerNorm` hay `RMSNorm`; `FFN` dùng activation thường hay gated `SwiGLU`; và có `weight tying` giữa input embedding với `lm_head` hay không. Các lựa chọn này giữ nguyên interface chính `(B, T, D) → (B, T, D)`, nhưng chúng thay đổi activation flow, số parameters, checkpoint keys và nghĩa của trained weights. Original Transformer minh họa `post-LayerNorm` + ReLU; GPT-2 báo cáo `pre-LayerNorm`; LLaMA summary mô tả `pre-RMSNorm` + `SwiGLU` + `RoPE`.[^vaswani-transformer-2017][^radford-gpt-2-2019][^llama-summary]

> [!success] Mục tiêu
> Sau bài này, bạn có thể đọc configuration của một GPT-style checkpoint, vẽ đúng data flow của block, tính parameter change khi đổi `FFN`, viết một `DecoderBlock` configurable bằng PyTorch, và biết vì sao đổi một option không phải là cách an toàn để dùng lại checkpoint cũ.

Bài này là **synthesis sư phạm**, không phải khẳng định một recipe là tốt nhất cho mọi scale, dataset, optimizer, hoặc hardware. Evidence về LLaMA trong wiki hiện là một secondary summary; các details model-specific ngoài những điểm ghi rõ bên dưới cần được đối chiếu primary source trước khi dùng để reproduce.[^llama-summary]

## 1. Bắt đầu từ interface bất biến

Dù recipe thay đổi, một dense causal decoder block thường có contract sau:

```text
hidden states x: (B, T, D)
    │
    ├── causal self-attention: communication across token positions
    │
    ├── residual path + normalization: preserve and stabilize depth flow
    │
    └── FFN / MLP: nonlinear computation at each position

output hidden states: (B, T, D)
```

- `B` = `batch_size`.
- `T` = `sequence_length`.
- `D` = `d_model` / `hidden_size`.
- `H` = number of attention heads, with `D % H == 0`.

`Self-attention` is where a token may retrieve information from allowed token positions. `FFN` receives a contextualized vector but applies the same function independently to each position. `Residual connection` adds the old representation to the branch update, so a stack can refine rather than replace the signal at every depth.[^vaswani-transformer-2017]

A causal mask remains mandatory for a causal language model. None of `RMSNorm`, `SwiGLU`, `RoPE`, or weight tying prevents future-token leakage; they answer different design questions. See [Attention: beginner's guide for causal language models](attention-beginner-guide.md) for the mask and Q/K/V mechanics.

## 2. Bản đồ các lựa chọn trong recipe

| Decision | Common options | What stays invariant | What changes materially |
|---|---|---|---|
| Input + position | token + learned/sinusoidal absolute position; token only at input plus `RoPE` in attention | first hidden state has shape `(B, T, D)` | where position enters; parameter tensors; attention-score computation |
| Normalization | `LayerNorm`, `RMSNorm` | normalized tensor stays `(B, T, D)` | centering, learned parameters, checkpoint keys, numerical behavior |
| Norm placement | `post-norm`, `pre-norm` | two residual branches per basic block | activation and gradient path through depth; usually final norm convention |
| FFN | ReLU, GELU, gated `SwiGLU` | input/output width is `D` | number of projections, intermediate width, parameter count, nonlinear path |
| Vocabulary interface | untied or tied `token_embedding` / `lm_head` | logits shape `(B, T, V)` | parameter count and shared parameter semantics |

A useful reading habit: do **not** infer an option only from a model family name. Open the configuration and model code, then answer five concrete questions: where is position applied, which norm class exists, whether norm comes before a branch, how many FFN projections exist, and whether embedding/head weights are the same tensor.

## 3. Input representation và position: cùng mục tiêu, khác vị trí đặt mechanism

Token IDs are integers. An embedding table turns them into vectors:

$$
E_{token}[\text{ids}] \in \mathbb{R}^{B\times T\times D}.
$$

Attention by itself has no built-in coordinate meaning “position 17”. A positional mechanism supplies order information, but its placement differs.

### 3.1 Learned or sinusoidal absolute `position embedding`

The original Transformer adds sinusoidal position vectors to embeddings; it also reports learned positional embeddings as a close experimental alternative. The summed input is:

$$
x^{(0)}_t = e_{token}(id_t) + p_t.
$$

The original Transformer uses fixed sinusoidal vectors, whereas a GPT-style implementation can use a learned table `position_emb[t]`. In either case position reaches all later projections because it is part of the residual stream from the start.[^vaswani-transformer-2017][^huggingface-openai-gpt-pytorch]

```text
token IDs → token embedding ─┐
                              ├→ x0 → all decoder blocks
position IDs → position embedding ─┘
```

### 3.2 `RoPE`: rotate Q and K after projection

`Rotary Position Embedding` (`RoPE`) does not add a position vector to the input residual stream. Each attention layer first projects hidden states, then rotates coordinate pairs in `Q` and `K` according to their positions:

$$
Q=XW_Q,\quad K=XW_K,
$$
$$
\tilde Q_t=R_tQ_t,\quad \tilde K_t=R_tK_t,
$$
$$
A=\operatorname{softmax}\left(\frac{\tilde Q\tilde K^\top}{\sqrt{d_h}}+M_{causal}\right).
$$

The resulting dot product carries relative-offset information. `V` is normally not rotated. The LLaMA summary reports RoPE rather than learned absolute position embeddings; this makes it a useful contrasting recipe, not evidence that both mechanisms should be added together.[^llama-summary]

```text
hidden X
  ├─ Wq → Q ── RoPE ─┐
  ├─ Wk → K ── RoPE ─┼→ scores → causal mask → softmax
  └─ Wv → V ────────┘
```

> [!warning] Checkpoint boundary
> Switching an absolute-position checkpoint to `RoPE` is not a harmless refactor. The former has a position-embedding parameter and learned downstream distribution; the latter changes every attention score calculation and has no such table. `strict=True` loading should fail because state-dict keys differ; forcing `strict=False` only hides the mismatch, not solves it.

For the rotation derivation, pairing conventions, and tests, use [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md).

## 4. `LayerNorm` và `RMSNorm`: normalize cái gì?

Let one token hidden vector be $x\in\mathbb{R}^{D}$. Normalization is applied over its feature dimension, separately for every token and sample.

### 4.1 `LayerNorm`

`LayerNorm` centers and rescales the vector:

$$
\mu=\frac{1}{D}\sum_i x_i,\qquad
\sigma^2=\frac{1}{D}\sum_i(x_i-\mu)^2,
$$
$$
\operatorname{LayerNorm}(x)=\gamma\odot\frac{x-\mu}{\sqrt{\sigma^2+\epsilon}}+\beta.
$$

It normally has learned scale `γ` and shift `β`, each of shape `(D,)`. `nn.LayerNorm(D)` implements this standard form. The original Transformer uses layer normalization around each sublayer.[^vaswani-transformer-2017]

### 4.2 `RMSNorm`

`RMSNorm` does **not** subtract the mean. It divides by root mean square and usually learns only a scale:

$$
\operatorname{RMSNorm}(x)=\gamma\odot
\frac{x}{\sqrt{\frac{1}{D}\sum_i x_i^2+\epsilon}}.
$$

Therefore both norms preserve shape, but their computation and parameterization differ. The supplied LLaMA overview reports `RMSNorm` in a pre-normalized decoder-only Transformer.[^llama-summary]

| Question | `LayerNorm` | `RMSNorm` |
|---|---|---|
| Subtract feature mean? | yes | no |
| Learned affine parameters in usual form | scale and bias | scale; the implementation below has no bias |
| Output shape | `(B, T, D)` | `(B, T, D)` |
| Can a trained norm be swapped by class name alone? | no | no |

The table does **not** prove that one norm is universally more stable or higher quality. Training behavior also depends on depth, initialization, optimizer, precision, data, and learning rate.

## 5. `pre-norm` versus `post-norm`: vị trí làm đổi đường activation

This is the most important formula distinction when reading a block.

### 5.1 `Post-norm`: original Transformer pattern

For a sublayer `F`, original Transformer uses:

$$
y=\operatorname{Norm}(x+F(x)).
$$

For a decoder-like block with attention then FFN:

$$
u=\operatorname{Norm}_1(x+\operatorname{Attention}(x)),
$$
$$
y=\operatorname{Norm}_2(u+\operatorname{FFN}(u)).
$$

The original source explicitly describes `LayerNorm(x + Sublayer(x))`, and its FFN is two linear layers with ReLU.[^vaswani-transformer-2017]

### 5.2 `Pre-norm`: GPT-2-style pattern

In `pre-norm`, normalize the input to the branch and keep residual addition outside it:

$$
u=x+\operatorname{Attention}(\operatorname{Norm}_1(x)),
$$
$$
y=\nu+\operatorname{FFN}(\operatorname{Norm}_2(\nu)).
$$

GPT-2 reports moving layer normalization to the input of every sub-block and adding an additional final layer normalization after the last self-attention block. It also reports scaling residual-layer weights at initialization by $1/\sqrt{N}$ for $N$ residual layers.[^radford-gpt-2-2019]

```text
post-norm                            pre-norm
---------                            --------
x → attention → + x → norm           x → norm → attention → + x
  → FFN → + previous → norm            → norm → FFN → + previous
```

The arrows may look similar but the tensors sent into attention and FFN differ. A `pre-norm` stack generally includes a final normalization before `lm_head`; do not accidentally omit it when translating the equations into code.

> [!warning] Never mix recipes mid-block
> `x + attention(norm(x))` is pre-norm. `norm(x + attention(x))` is post-norm. Combining one branch from each pattern without an intentional design produces a third architecture, not a faithful implementation of either reference.

## 6. FFN: cùng output width, khác nonlinear computation

Attention lets positions communicate. The `FFN` or `MLP` then computes at each position independently. Suppose $x\in\mathbb{R}^{D}$ and `d_ff` is intermediate width.

### 6.1 Standard FFN with ReLU or GELU

A standard two-projection FFN is:

$$
\operatorname{FFN}(x)=W_{down}\,\phi(W_{up}x+b_{up})+b_{down}.
$$

Original Transformer uses ReLU and `d_ff = 2048` at `D = 512`, i.e. $4D$.[^vaswani-transformer-2017] GPT-style models frequently use GELU, but the essential interface remains:

```text
(B, T, D) → linear D→d_ff → activation → linear d_ff→D → (B, T, D)
```

Ignoring bias, its parameter count is approximately:

$$
P_{standard}\approx 2D\,d_{ff}.
$$

### 6.2 Gated FFN and `SwiGLU`

A gated FFN computes two projections, uses one as a content/up branch and one as a gate, multiplies them elementwise, then projects down:

$$
\operatorname{SwiGLU}(x)=W_{down}\bigl(\operatorname{SiLU}(xW_{gate})\odot(xW_{up})\bigr).
$$

`SiLU(z)=z\,\sigma(z)`. The multiplication is elementwise, so `gate` and `up` must have the same shape `(B, T, d_ff)`. The supplied LLaMA summary reports SwiGLU and says the intermediate width is adjusted to roughly $\frac{2}{3}(4D)=\frac{8D}{3}$ before hardware-friendly rounding.[^llama-summary]

Ignoring bias:

$$
P_{SwiGLU}\approx 3D\,d_{ff,glu}.
$$

If a standard `4D` FFN has about $8D^2$ parameters, choose $d_{ff,glu}\approx 8D/3$ so a SwiGLU FFN is comparable:

$$
3D\left(\frac{8D}{3}\right)=8D^2.
$$

This is why blindly keeping `d_ff=4D` while changing GELU to SwiGLU increases the FFN's approximate matrix parameters from $8D^2$ to $12D^2$ - a 50% increase. That is a configuration change, not an activation-only experiment.

| Variant | Linear projections | Intermediate width for roughly matched standard `4D` parameter count | Common mistake |
|---|---:|---:|---|
| ReLU/GELU FFN | 2 | `4D` | calling it gated when it has one expansion branch |
| SwiGLU FFN | 3 | about `8D/3`, then round deliberately | retaining `4D` without accounting for extra matrices |

## 7. `Weight tying`: one matrix, two roles

Let vocabulary size be `V`. Input embedding has a matrix $E\in\mathbb{R}^{V\times D}$ and maps token ID to its row. The output head normally has $W_{out}\in\mathbb{R}^{V\times D}$ and produces logits:

$$
\text{logits}_t=h_tW_{out}^{\top}.
$$

With `weight tying`, set $W_{out}=E$. The input and output use **the same parameter object**, not merely two tensors initialized to equal values. It removes roughly $V\times D$ separate parameters (assuming an untied head would exist), and an update from either role changes the shared matrix. The original Transformer shares embedding and pre-softmax weights; the supplied OpenAI GPT wrapper also declares its language-model projection tied to input embeddings.[^vaswani-transformer-2017][^huggingface-openai-gpt-pytorch]

```python
# Correct tying: both module attributes refer to the same Parameter.
model.lm_head.weight = model.token_embedding.weight
assert model.lm_head.weight is model.token_embedding.weight
```

Weight tying requires compatible `V` and `D`. It is a model-definition decision: an untied checkpoint expects two independently trained matrices. Loading it into a tied model means one of its learned matrices is discarded or overwrites the other, so it is not a semantics-preserving conversion.

## 8. PyTorch lab: một `DecoderBlock` configurable

The code below intentionally favors visible semantics over performance. It uses full score matrices, has no padding mask, `KV cache`, mixed precision, or fused attention kernel. It supports exactly one positional recipe at a time: learned absolute position **or** RoPE.

```python
import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class RMSNorm(nn.Module):
    def __init__(self, d_model, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d_model))
        self.eps = eps

    def forward(self, x):
        # Normalize last dimension, separately for every (batch, position).
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).rsqrt()
        return x * rms * self.weight


def make_norm(kind, d_model):
    if kind == "layernorm":
        return nn.LayerNorm(d_model)
    if kind == "rmsnorm":
        return RMSNorm(d_model)
    raise ValueError("norm must be 'layernorm' or 'rmsnorm'")


def apply_rope_interleaved(x):
    """x: (B, H, T, Dh); rotate pairs (0,1), (2,3), ... ."""
    _, _, T, Dh = x.shape
    if Dh % 2:
        raise ValueError("RoPE requires an even head_dim")
    positions = torch.arange(T, device=x.device, dtype=x.dtype)
    frequencies = 1.0 / (10000 ** (torch.arange(0, Dh, 2, device=x.device,
                                                  dtype=x.dtype) / Dh))
    angles = positions[:, None] * frequencies[None, :]  # (T, Dh/2)
    cos, sin = angles.cos()[None, None], angles.sin()[None, None]
    even, odd = x[..., 0::2], x[..., 1::2]
    rotated = torch.stack((even * cos - odd * sin, even * sin + odd * cos), dim=-1)
    return rotated.flatten(-2)


class CausalSelfAttention(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.0, use_rope=False):
        super().__init__()
        if d_model % n_heads:
            raise ValueError("d_model must be divisible by n_heads")
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.use_rope = use_rope
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out = nn.Linear(d_model, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        B, T, D = x.shape
        # q, k, v each becomes (B, H, T, Dh).
        qkv = self.qkv(x).view(B, T, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.permute(2, 0, 3, 1, 4)
        if self.use_rope:
            q, k = apply_rope_interleaved(q), apply_rope_interleaved(k)

        scores = (q @ k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        causal_allow = torch.ones(T, T, device=x.device, dtype=torch.bool).tril()
        scores = scores.masked_fill(~causal_allow, float("-inf"))
        weights = F.softmax(scores, dim=-1)
        y = weights @ v                                  # (B, H, T, Dh)
        y = y.transpose(1, 2).contiguous().view(B, T, D)
        return self.dropout(self.out(y))


class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff, kind="gelu", dropout=0.0):
        super().__init__()
        self.kind = kind
        if kind in {"relu", "gelu"}:
            self.up = nn.Linear(d_model, d_ff)
            self.down = nn.Linear(d_ff, d_model)
        elif kind == "swiglu":
            self.gate = nn.Linear(d_model, d_ff, bias=False)
            self.up = nn.Linear(d_model, d_ff, bias=False)
            self.down = nn.Linear(d_ff, d_model, bias=False)
        else:
            raise ValueError("ffn must be 'relu', 'gelu', or 'swiglu'")
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        if self.kind == "relu":
            y = F.relu(self.up(x))
        elif self.kind == "gelu":
            y = F.gelu(self.up(x))
        else:
            y = F.silu(self.gate(x)) * self.up(x)
        return self.dropout(self.down(y))


class DecoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, d_ff, *, norm="layernorm",
                 norm_placement="pre", ffn="gelu", dropout=0.0, use_rope=False):
        super().__init__()
        if norm_placement not in {"pre", "post"}:
            raise ValueError("norm_placement must be 'pre' or 'post'")
        self.norm_placement = norm_placement
        self.norm_1 = make_norm(norm, d_model)
        self.norm_2 = make_norm(norm, d_model)
        self.attn = CausalSelfAttention(d_model, n_heads, dropout, use_rope)
        self.ffn = FeedForward(d_model, d_ff, ffn, dropout)

    def forward(self, x):
        if self.norm_placement == "pre":
            x = x + self.attn(self.norm_1(x))
            x = x + self.ffn(self.norm_2(x))
        else:  # original-Transformer-style post-norm
            x = self.norm_1(x + self.attn(x))
            x = self.norm_2(x + self.ffn(x))
        return x


class ConfigurableTinyGPT(nn.Module):
    def __init__(self, vocab_size, max_seq_len, d_model=128, n_heads=4, n_layers=2,
                 d_ff=None, position="absolute", norm="layernorm",
                 norm_placement="pre", ffn="gelu", tie_weights=True, dropout=0.0):
        super().__init__()
        if position not in {"absolute", "rope"}:
            raise ValueError("position must be 'absolute' or 'rope'")
        if d_ff is None:
            # Parameter-aware defaults, not a claim of universal optimality.
            d_ff = 4 * d_model if ffn != "swiglu" else (8 * d_model) // 3
        self.vocab_size = vocab_size
        self.max_seq_len = max_seq_len
        self.position = position
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_embedding = (
            nn.Embedding(max_seq_len, d_model) if position == "absolute" else None
        )
        self.blocks = nn.ModuleList([
            DecoderBlock(d_model, n_heads, d_ff, norm=norm,
                         norm_placement=norm_placement, ffn=ffn,
                         dropout=dropout, use_rope=(position == "rope"))
            for _ in range(n_layers)
        ])
        # Conventional for pre-norm; included here for a uniform toy-model interface.
        self.final_norm = make_norm(norm, d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        if tie_weights:
            self.lm_head.weight = self.token_embedding.weight

    def forward(self, input_ids):
        B, T = input_ids.shape
        if not 1 <= T <= self.max_seq_len:
            raise ValueError("sequence length must be in [1, max_seq_len]")
        x = self.token_embedding(input_ids)
        if self.position == "absolute":
            pos = torch.arange(T, device=input_ids.device)
            x = x + self.position_embedding(pos)[None, :, :]
        for block in self.blocks:
            x = block(x)
        return self.lm_head(self.final_norm(x))  # (B, T, vocab_size)
```

### 8.1 What this code deliberately makes visible

- Change `norm="layernorm"` to `"rmsnorm"`: shape stays unchanged, but the class and state dict change.
- Change `norm_placement="pre"` to `"post"`: the same modules exist but receive different tensors.
- Change `ffn="gelu"` to `"swiglu"`: set `d_ff` deliberately, otherwise parameter count changes.
- Change `position="absolute"` to `"rope"`: the position table disappears and `Q/K` are rotated in every attention layer.
- Change `tie_weights`: `lm_head.weight` either aliases input embedding or becomes an independent parameter.

This is not a production implementation. In particular, calculating RoPE angles and allocating a causal mask in every forward are clear but inefficient; a production model caches them or uses a fused kernel. Optimization must preserve the same mask, rotation pairing convention, projection shapes, and state layout.

## 9. Verification lab: test invariants before comparing loss

A model that trains is not automatically architecturally correct. Run structural tests first.

```python
@torch.no_grad()
def assert_causal(model, ids, cut):
    """Changing suffix after cut must not change logits at positions <= cut."""
    model.eval()
    changed = ids.clone()
    changed[:, cut + 1:] = torch.randint(
        model.vocab_size, changed[:, cut + 1:].shape, device=ids.device
    )
    torch.testing.assert_close(
        model(ids)[:, :cut + 1], model(changed)[:, :cut + 1],
        rtol=1e-5, atol=1e-6,
    )


def trainable_parameters(model):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


ids = torch.randint(0, 1000, (2, 8))

# Same external input/output contract, different internal recipe.
classic = ConfigurableTinyGPT(
    1000, 32, d_model=128, n_heads=4,
    position="absolute", norm="layernorm", norm_placement="post", ffn="relu",
    tie_weights=False, dropout=0.0,
)
modern = ConfigurableTinyGPT(
    1000, 32, d_model=128, n_heads=4,
    position="rope", norm="rmsnorm", norm_placement="pre", ffn="swiglu",
    tie_weights=True, dropout=0.0,
)

assert classic(ids).shape == modern(ids).shape == (2, 8, 1000)
assert_causal(classic, ids, cut=3)
assert_causal(modern, ids, cut=3)
assert modern.lm_head.weight is modern.token_embedding.weight

print("classic parameters:", trainable_parameters(classic))
print("modern parameters:", trainable_parameters(modern))
```

Expected facts:

1. Both models return logits `(B, T, V)`; output shape alone does **not** show they implement the same architecture.
2. Both pass the causal test because both use the same lower-triangular mask.
3. Parameter counts differ for multiple reasons: position table, norm bias, FFN projection count/width, and tied output weights.
4. The code has not established that either configuration reaches better validation loss. That requires a controlled training comparison with matched data, optimizer, initialization policy, compute budget, and repeated runs.

## 10. Checkpoint compatibility: shapes are necessary, not sufficient

A checkpoint contains trained parameters for a particular computation graph. Before loading it, compare this ledger.

| Choice changed | What can fail immediately | Why equal output shape is insufficient |
|---|---|---|
| absolute position ↔ `RoPE` | missing/unexpected position keys | position enters different locations and Q/K score semantics change |
| `LayerNorm` ↔ `RMSNorm` | norm bias may be missing or unexpected | centering and parameterization differ |
| pre-norm ↔ post-norm | keys can have same shapes | the stored weights expect different branch inputs |
| GELU/ReLU ↔ SwiGLU | FFN tensor shapes / keys differ | SwiGLU needs a second expansion projection and changes nonlinear function |
| untied ↔ tied head | both weight tensors may exist or one alias is expected | two independently trained matrices cannot be losslessly collapsed into one |
| head count / `D` / `d_ff` / vocabulary | tensor-size mismatch | linear maps no longer represent the same dimensions |

`model.load_state_dict(checkpoint, strict=True)` is a useful first guard. If it fails, inspect every missing, unexpected, and size-mismatched key. If it succeeds, still verify architecture metadata: some semantically different choices have identically shaped tensors. Use a documented conversion procedure and continued training only when a source supports that conversion; do not call `strict=False` a compatibility solution.

## 11. Workflow để tự học recipe thay vì nhớ tên model

1. **Freeze a baseline.** Start with one small causal GPT that passes shape, target-shift, tiny-overfit, and causality tests. [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) provides that baseline.
2. **Change one axis.** For example, `LayerNorm → RMSNorm` while keeping position, norm placement, FFN width, seed, data, and optimizer fixed.
3. **Record the ledger.** Write down code path, parameter count, state-dict key changes, initial loss, training loss, validation loss, tokens/sec, and memory. Do not call a result “from SwiGLU” if position and normalization also changed.
4. **Test semantics before quality.** Check causality and logits shape; then run a tiny overfit. A lower loss with a broken mask is not an improvement.
5. **Only then study systems choices.** `RoPE`, GQA, FlashAttention, and `KV cache` have additional inference and context-state consequences that are separate from the local decoder-block interface.

> [!tip] A compact recipe description
> Write a model block as: **position / norm placement + norm type / attention / FFN / residual / output tying**. For example: “RoPE / pre-RMSNorm / causal MHA / SwiGLU with parameter-matched width / ordinary residual additions / tied vocabulary head.” This sentence is much more informative than only saying “a Transformer”.

## 12. Exercises

1. **Derive parameter count.** With `D=768`, calculate approximate matrix parameters for a standard `d_ff=3072` FFN and for a parameter-matched SwiGLU. Ignore bias first, then add it.
2. **Trace one position.** In pre-norm code, label exactly which tensor feeds `norm_1`, attention, first residual addition, `norm_2`, FFN, and the second residual addition.
3. **Break causality.** Replace `.tril()` with `.triu()` in the lab, run `assert_causal`, then restore it. Explain why a good training loss would be untrustworthy with the broken mask.
4. **Inspect `state_dict()`.** Instantiate absolute-position and RoPE variants. Compare keys and identify which keys make a strict load fail.
5. **Measure tying.** Instantiate tied and untied models with the same `V` and `D`; verify the parameter difference is `V × D`, accounting for any head bias choice.
6. **Controlled mini-experiment.** Train only GELU and SwiGLU variants with matched approximate FFN parameter count. Report what is observed; do not generalize one small run into a universal architectural claim.

## 13. Đường học tiếp

- [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md) explains Q/K rotation, cache offsets, and convention tests.
- [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md) moves from a full-sequence block to incremental decode state.
- [MQA/GQA: giảm KV cache khi decode — bài học cho người mới](mqa-gqa-kv-cache-decode-beginners-guide.md) changes the K/V-head layout while preserving causal attention intent.
- [Tích hợp RoPE, GQA, và FlashAttention vào GPT nhỏ](rope-gqa-flashattention-integration-beginners-guide.md) combines several compatible changes and tests semantics before benchmarking.

This course elaborates Stage 4.1 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md). Complete it after the dense decoder baseline, before treating long-context or sparse-capacity mechanisms as drop-in features.

## Relationships

- **Elaborates:** Stage 4.1 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) with theory, a configurable implementation, parameter accounting, and compatibility checks.
- **Builds on:** [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) for the dense causal baseline and [Attention: beginner's guide for causal language models](attention-beginner-guide.md) for Q/K/V and causal masking.
- **Synthesizes:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), [LLaMA efficient pre-trained language models](llama-efficient-pre-trained-language-models.md), and [OpenAI GPT PyTorch reference implementation](openai-gpt-pytorch-reference-implementation.md).
- **Prepares for:** [RoPE: positional encoding, implementation, và kiểm chứng cho người mới](rope-positional-encoding-beginners-guide.md), [KV caching: cơ chế, implementation, và kiểm chứng](kv-caching-beginners-guide.md), and [MQA/GQA: giảm KV cache khi decode — bài học cho người mới](mqa-gqa-kv-cache-decode-beginners-guide.md).

[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [LaTeX source](../raw/arXiv-1706.03762v7/ms.tex), especially encoder/decoder stacks, position-wise FFN, embeddings/softmax, and positional encoding.
[^radford-gpt-2-2019]: Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [PDF](../raw/gpt2.pdf), Section 2.3 and Table 2. The report states that LayerNorm moves to each sub-block input, a final LayerNorm is added, and residual-layer initialization is depth-scaled.
[^llama-summary]: “LLaMA overview” (Vietnamese summary), [raw source](../raw/LLaMA.md), Section 3. Secondary-source evidence for its reported pre-RMSNorm, SwiGLU, and RoPE recipe; the LLaMA primary paper is not independently ingested in this wiki.
[^huggingface-openai-gpt-pytorch]: Hugging Face, “PyTorch OpenAI GPT model,” [source](../raw/gpt-source.py), especially `Block`, `MLP`, positional embedding, and language-model wrapper. The supplied implementation uses post-residual LayerNorm and tied output embedding, and is code evidence rather than a GPT-2 reproduction.
