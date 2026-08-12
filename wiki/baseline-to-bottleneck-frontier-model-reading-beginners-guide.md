---
type: Synthesis
title: "Baseline-to-bottleneck: cách đọc frontier model cho người mới"
description: A beginner-first course for reading frontier-model reports by mapping each novelty back to a dense GPT-2 baseline, the bottleneck it targets, its trade-offs, and the evidence that supports it.
tags: [frontier-model, architecture-reading, gpt-2, bottleneck, kv-cache, attention, mixture-of-experts, residual-stream, profiling, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-12T13:42:02+07:00 }
sources:
  - id: radford-gpt-2-2019
    resource: ../raw/gpt2.pdf
    title: Language Models are Unsupervised Multitask Learners
  - id: vaswani-transformer-2017
    resource: ../raw/arXiv-1706.03762v7/ms.tex
    title: Attention Is All You Need
  - id: deepseek-v2-2024
    resource: ../raw/arXiv-2405.04434v5/main.tex
    title: "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model"
  - id: deepseek-v3-2024
    resource: ../raw/arXiv-2412.19437v2/main.tex
    title: DeepSeek-V3 Technical Report
  - id: attnres-2026
    resource: ../raw/arXiv-2603.15031v1/main.tex
    title: Attention Residuals
  - id: flashattention-summary
    resource: ../raw/FlashAttention.md
    title: FlashAttention overview (Vietnamese summary)
---

# Baseline-to-bottleneck: cách đọc frontier model cho người mới

Một architecture report trở nên dễ đọc hơn khi bạn không bắt đầu từ tên mechanism mới. Hãy bắt đầu từ một **dense GPT-2-style baseline**, chỉ ra component nào đang bị thay thế, bottleneck nào được nhắm tới, trade-off nào xuất hiện, rồi mới kiểm tra evidence. Phương pháp này ngăn ta đánh đồng một equation mới với end-to-end speedup, hoặc dùng whole-model benchmark để chứng minh một component riêng lẻ. Đây là pedagogical synthesis cho Stage 9.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md), dựa trên Transformer/GPT-2 và các case study MLA, MoE systems, Attention Residuals, và FlashAttention.[^radford-gpt-2-2019][^vaswani-transformer-2017][^deepseek-v2-2024][^deepseek-v3-2024][^attnres-2026][^flashattention-summary]

> [!success] Sau bài này
> Bạn có thể:
> - vẽ data flow của một dense decoder block;
> - phân biệt sáu bottleneck: `KV state`, `attention cost`, `FFN compute`, `routing balance`, `residual dilution`, và `hardware utilization`;
> - đặt một novelty vào đúng layer: `architecture`, `training objective`, `numerical format`, `distributed system`, hoặc `serving policy`;
> - tạo evidence ledger gồm `mechanism → replaced baseline → expected trade-off → evidence`;
> - dùng một tiny PyTorch model để đo parameter mix, activation shapes, latency, và KV-cache estimate trước khi đọc model lớn.

## 1. Vì sao phải bắt đầu bằng `baseline`?

Một câu như “model dùng MLA, MoE và FP8” liệt kê tên nhưng chưa giải thích design. Muốn hiểu design, ta cần một control tưởng tượng:

> Nếu bỏ novelty này đi, model quay về component nào và vấn đề nào quay lại?

Đó là vai trò của `baseline`. Trong bài này, baseline là decoder-only Transformer gần với GPT-2:

```text
token IDs
  ↓
token embedding + learned position embedding
  ↓
┌──────────────── decoder block × L ────────────────┐
│ x ── LayerNorm ── causal MHA ── (+ residual)      │
│   ── LayerNorm ── dense FFN/MLP ── (+ residual)   │
└────────────────────────────────────────────────────┘
  ↓
final LayerNorm → lm_head → next-token logits
```

GPT-2 sử dụng causal Transformer, pre-layer normalization, final normalization, learned position range 1,024 tokens, và dense blocks; các model hiện đại có thể thay đổi position method, normalization, activation, hoặc bias mà vẫn giữ skeleton này.[^radford-gpt-2-2019] Hãy xem [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md) nếu bạn chưa tự triển khai được block trên.

### 1.1 Data flow trong một block

Với hidden state $X_l\in\mathbb{R}^{B\times T\times D}$, một pre-norm block đơn giản là:

$$
U_l = X_l + \operatorname{Attention}(\operatorname{Norm}_1(X_l)),
$$

$$
X_{l+1} = U_l + \operatorname{FFN}(\operatorname{Norm}_2(U_l)).
$$

Hai sublayer có vai trò khác nhau:

- `attention`: giao tiếp giữa token positions;
- `FFN`: biến đổi channel tại từng position;
- `residual stream`: mang và cộng dồn representation qua depth;
- `normalization`: ổn định scale của input vào sublayer.

Nếu không biết novelty tác động vào term nào trong hai equation này, bạn chưa có component map.

### 1.2 Hai execution regime khác nhau

Cùng một model nhưng bottleneck thay đổi theo lifecycle:

| Regime | Input mỗi forward | Work nổi bật | State nổi bật |
|---|---:|---|---|
| `training` | nhiều sequences và positions | forward + backward + optimizer | activations, gradients, optimizer state |
| `prefill` | nhiều prompt tokens | full causal attention và GEMM | tạo KV cache |
| `decode` | thường một token mới/request/step | đọc weights và growing cache | đọc rồi append KV cache |

Vì vậy câu “attention là bottleneck” chưa đủ. Phải hỏi: **training, prefill hay decode; sequence length bao nhiêu; batch/concurrency bao nhiêu; hardware nào?** [Inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md) phân biệt chi tiết `TTFT` và `TPOT`.

## 2. Component map của dense baseline

Trước khi đọc paper, điền bảng baseline này bằng symbol của model:

| Component | Baseline mechanism | State/compute tăng theo | Câu hỏi profiling đầu tiên |
|---|---|---|---|
| Position | learned absolute embedding | $T\times D$ table lookup | context có vượt trained range không? |
| Sequence mixing | full causal MHA | prefill interaction $T^2$ | score/probability có materialize không? |
| Decode memory | per-layer, per-token K/V | $L\times T\times H_{kv}\times d_h$ | cache bytes/request là bao nhiêu? |
| Channel mixing | dense FFN | $B\times T\times D\times D_{ff}$ | FFN chiếm bao nhiêu parameters/FLOPs? |
| Depth path | additive residual | số layer $L$ | layer có truy xuất chọn lọc state cũ không? |
| Execution | dense GEMM kernels | shape, dtype, device topology | GPU có thật sự bận hay đang chờ memory/network? |

Bảng này tách **mathematical mechanism** khỏi **physical execution**. Cùng equation attention có thể chạy bằng implementation naive hoặc FlashAttention; semantics gần như giữ nguyên nhưng memory traffic khác.[^flashattention-summary]

## 3. Sáu bottleneck cần nhận diện

### 3.1 `KV state`: memory tăng theo context và concurrency

Trong standard multi-head attention, mỗi layer cache key và value của mọi token đã xử lý. Bỏ qua metadata, cache bytes xấp xỉ:

$$
M_{KV}=2\,B\,T\,L\,H_{kv}\,d_h\,s,
$$

với $s$ là bytes/element. Factor 2 đến từ K và V. Với MHA, $H_{kv}=H_q$; MQA/GQA giảm $H_{kv}$; MLA cache một compressed latent cộng position key thay cho full per-head K/V.[^deepseek-v2-2024]

> [!example] Memory estimate
> Với $B=1$, $T=8192$, $L=32$, $H_{kv}=32$, $d_h=128$, BF16 ($s=2$):
>
> $$M_{KV}=2\times1\times8192\times32\times32\times128\times2=4\ \text{GiB}. $$
>
> Đây chỉ là raw tensor estimate, chưa gồm allocator fragmentation, block metadata hoặc workspace.

**Dấu hiệu:** out-of-memory khi context/concurrency tăng; `TPOT` xấu dần theo history; cache chiếm phần lớn free memory.

**Các hướng xử lý:**

- MQA/GQA chia sẻ K/V heads;
- MLA giảm representation **mỗi token** nhưng vẫn token-addressable và vẫn tăng tuyến tính theo $T$;
- quantization, eviction hoặc PagedAttention thay representation/layout/policy;
- fixed-state recurrent memory không giữ từng token, nhưng đổi retrieval semantics.

**Trade-off cần tìm:** giảm cache có thể giảm representational capacity, thêm compression/decompression, đổi kernels, hoặc mất exact token-addressability. Không được viết “MLA làm cache $O(1)$”; MLA vẫn cache state cho từng token.[^deepseek-v2-2024]

### 3.2 `attention cost`: token interaction và intermediate memory

Full attention cho sequence dài có score matrix shape $(B,H,T,T)$ và arithmetic $O(T^2d)$.[^vaswani-transformer-2017] Nhưng có hai bài toán khác nhau:

1. **Algorithmic cost:** có bao nhiêu token pairs được tương tác?
2. **IO/implementation cost:** tensors nào phải đi giữa HBM và on-chip memory?

FlashAttention giải bài toán thứ hai: tile Q/K/V, duy trì online-softmax statistics, không ghi full score/probability matrix ra HBM. Nó giữ exact softmax-attention semantics trong giới hạn finite precision, nhưng không loại bỏ quadratic arithmetic.[^flashattention-summary]

```text
naive attention:   QKᵀ → write scores → softmax → write probs → probs·V
FlashAttention:    stream tiles → online softmax → final output

same target formula; different data movement
```

**Dấu hiệu:** prefill latency tăng mạnh theo prompt length; activation memory tăng nhanh; profiler cho thấy attention kernel/IO chiếm lớn.

**Trade-off cần tìm:** sparse/local/linear attention có thể đổi algorithm và retrieval; FlashAttention chủ yếu đổi kernel. Hai loại claim không thể thay thế nhau.

### 3.3 `FFN compute`: dense compute ở mọi token

Một dense FFN gần GPT-2 có:

$$
\operatorname{FFN}(x)=W_2\phi(W_1x),\qquad D_{ff}\approx4D.
$$

Bỏ bias, parameter count mỗi block gần $2DD_{ff}$; mỗi token luôn đi qua toàn bộ matrices. Khi $D_{ff}=4D$, FFN thường có khoảng $8D^2$ weights, trong khi Q/K/V/output projections của MHA gần $4D^2$. Đây là parameter accounting của simplified baseline, không phải universal runtime ratio.

MoE thay một dense FFN bằng nhiều experts nhưng chỉ activate top-$k$ experts mỗi token. Điều này tách:

- `total parameters`: capacity và weight memory;
- `active parameters`: phần FFN compute dùng cho token;
- `communication`: dispatch/combine tokens tới expert devices.

**Dấu hiệu:** FFN GEMMs chiếm phần lớn compute; tăng model capacity bằng dense width quá tốn training/inference FLOPs.

**Trade-off cần tìm:** sparse FFN giảm active expert compute nhưng vẫn phải lưu/load total expert weights và có router, capacity padding, dispatch, all-to-all. “Ít active parameters” không tự động suy ra latency thấp.[^deepseek-v3-2024]

### 3.4 `routing balance`: bottleneck mới do MoE tạo ra

Dense baseline **không có router**. Routing balance là ví dụ quan trọng: optimization giải `FFN compute` có thể sinh ra bottleneck mới.

Nếu nhiều tokens chọn cùng expert:

- expert đó overflow hoặc trở thành straggler;
- experts khác idle và học kém;
- device load lệch dù aggregate FLOPs có vẻ thấp;
- communication và padding tăng.

DeepSeek-V3 dùng adaptive routing bias để thay đổi top-$k$ assignment theo observed load, trong khi selected-expert mixture weights vẫn dựa trên affinity chưa cộng bias; hệ thống còn dùng node-limited routing và redundant experts trong deployment.[^deepseek-v3-2024]

Phân biệt ba level:

| Level | Câu hỏi |
|---|---|
| `expert balance` | mỗi expert nhận bao nhiêu tokens? |
| `device/rank balance` | tổng work trên mỗi accelerator có đều không? |
| `communication balance` | bytes gửi/nhận và fan-out có đều/bị giới hạn không? |

**Trade-off cần tìm:** balance pressure có thể làm router chọn expert kém phù hợp hơn; bias/auxiliary loss thêm control dynamics; capacity cao giảm drops nhưng tăng padding và memory.

### 3.5 `residual dilution`: mọi layer cũ bị cộng vào một stream

Standard residual có thể unfold thành:

$$
X_L=X_0+F_0(X_0)+F_1(X_1)+\cdots+F_{L-1}(X_{L-1}).
$$

Nó tạo gradient path tốt, nhưng layer sau nhận một accumulated stream thay vì có interface để chọn trực tiếp một representation theo depth. Từ “residual dilution” trong roadmap nên được hiểu là **hypothesis/design motivation** về retrieval qua depth, không phải định luật rằng model sâu chắc chắn mất information.

Attention Residuals thay uniform additive accumulation bằng learned softmax mixture trên earlier representations. Full form cho phép retrieval theo layer nhưng có $O(L^2d)$ depth-attention arithmetic và giữ $O(Ld)$ outputs; block form chỉ giữ summaries theo block để giảm cache và pipeline communication.[^attnres-2026]

**Dấu hiệu:** paper nhấn mạnh depth-wise retrieval, representation mixing, hoặc residual path; ablation thay residual mechanism nhưng giữ sequence mixer/FFN gần như cố định.

**Trade-off cần tìm:** extra state per token, depth-attention compute, pipeline transfer và prefill memory. Đây không phải optimization cho sequence-attention $T^2$.

### 3.6 `hardware utilization`: ít FLOPs chưa chắc nhanh hơn

Wall-clock time không chỉ do FLOPs:

$$
\text{time}\approx\max(\text{compute time},\text{memory time},\text{communication time})+\text{overhead}.
$$

Đây là mental model, không phải equation đo chính xác. Một GPU có thể chờ vì:

- decode GEMM quá nhỏ để saturate compute units;
- KV cache/weights bị giới hạn bởi memory bandwidth;
- MoE all-to-all chờ network hoặc straggler expert;
- dynamic shapes gây padding, launch overhead hoặc khó fuse;
- pipeline bubble khiến stages idle;
- low precision cần conversion/scaling không được kernel hỗ trợ tốt.

DeepSeek-V3 là ví dụ co-design: DualPipe, communication overlap, custom all-to-all và fine-grained FP8 nhằm cải thiện execution của architecture lớn. Những claim này phụ thuộc H800 topology, model shape, routing và custom kernels; không phải thuộc tính tự động của MoE/FP8.[^deepseek-v3-2024]

> [!warning] `FLOPs reduction ≠ speedup`
> Chỉ kết luận end-to-end speedup khi có measurement trên workload, hardware, batch/concurrency, precision và software stack được mô tả. Kernel benchmark không phải model-serving benchmark.

## 4. Classification trước khi đánh giá novelty

Mỗi novelty nên có **một primary label** và có thể có secondary labels:

| Label | Nó thay đổi gì? | Ví dụ |
|---|---|---|
| `architecture` | computation graph hoặc learned state | MLA, MoE, Attention Residuals |
| `training objective/control` | loss hoặc update signal | auxiliary loss, routing-bias update |
| `numerical format` | representation/accumulation precision | FP8 GEMM, BF16/FP32 exceptions |
| `distributed system` | placement, schedule, communication | expert parallelism, DualPipe |
| `kernel implementation` | cách chạy cùng operator | FlashAttention, fused MoE kernel |
| `serving policy` | scheduling/allocation theo requests | redundant experts, prefix caching |

Nếu paper viết “our model uses FP8”, FP8 không tự nó là sequence architecture. Nếu report viết “FlashAttention”, attention formula không vì thế trở thành linear attention. Classification sai dẫn tới comparison sai.

## 5. Evidence ladder: claim mạnh đến đâu?

Dùng ladder sau trước khi điền cột `evidence`:

1. **Definition/equation:** chứng minh mechanism tồn tại, chưa chứng minh hữu ích.
2. **Complexity/accounting:** cho expected scaling, chưa phải wall-clock measurement.
3. **Kernel microbenchmark:** đo operator, chưa bao gồm toàn model.
4. **Component ablation:** gần nhất để gán effect cho novelty nếu control tốt.
5. **Matched model comparison:** mạnh hơn whole-model comparison nhưng vẫn phụ thuộc recipe.
6. **End-to-end workload benchmark:** chứng minh behavior trong setup đã công bố.
7. **Independent replication:** tăng độ tin cậy ngoài author setup.

Whole-model benchmark của model mới chứa architecture + data + scale + optimizer + post-training + harness. Vì vậy nó thường **không** chứng minh một component cụ thể gây ra gain.

### Cách viết scoped claim

| Tránh viết | Nên viết |
|---|---|
| “MLA giải quyết long context.” | “MLA giảm per-token KV representation trong reported configuration, nhưng cache và exact global attention vẫn tăng theo context.” |
| “MoE nhanh hơn dense model.” | “MoE giảm active expert-FFN compute; realized speed phụ thuộc routing, weight memory, batch và all-to-all.” |
| “FlashAttention có linear attention cost.” | “FlashAttention giảm intermediate-memory traffic nhưng giữ quadratic full-attention arithmetic.” |
| “AttnRes sửa information loss.” | “AttnRes cung cấp learned retrieval qua depth; benefit và overhead cần component ablation và systems measurement.” |

## 6. Evidence ledger bốn cột

Template bắt buộc của Stage 9.1:

| Mechanism | Replaced baseline | Expected trade-off | Evidence |
|---|---|---|---|
| Tên + equation/data flow ngắn | component/path cũ cụ thể | gain dự kiến **và** cost mới | evidence type, setup, author/independent, gaps |

### Worked example

| Mechanism | Replaced baseline | Expected trade-off | Evidence |
|---|---|---|---|
| MLA caches joint KV latent + decoupled rotary key | per-head K/V cache của MHA | cache nhỏ hơn/token; vẫn $O(T)$ state và global-attention work | DeepSeek-V2 equations, cache accounting và author-run ablations; configuration-specific[^deepseek-v2-2024] |
| Sparse top-$k$ experts | dense FFN chạy cho mọi token | giảm active FFN compute, tăng total weights/router/dispatch | architecture + author-run model/system evidence; no universal latency guarantee[^deepseek-v3-2024] |
| Adaptive routing bias | unconstrained top-$k$ MoE routing | load đều hơn nhưng thêm control dynamics và có thể đổi assignment | V3 mechanism + ablations; workload/hardware dependent[^deepseek-v3-2024] |
| Block Attention Residuals | uniform additive residual accumulation | depth retrieval chọn lọc; extra state/IO/compute | primary mechanism, author-run ablations và systems measurements; not independently replicated[^attnres-2026] |
| FlashAttention | naive materialized score/probability tensors | giảm HBM traffic/activation memory; giữ $O(T^2d)$ arithmetic | secondary summary of algorithm; primary paper chưa được ingest độc lập ở wiki[^flashattention-summary] |

> [!tip] Mỗi row phải có cả upside và downside
> Nếu cột trade-off chỉ có lợi ích, row đó là marketing summary chứ chưa phải architecture analysis.

## 7. Quy trình đọc một report trong hai lượt

### Lượt 1 — lập bản đồ, chưa đọc benchmark headline

1. Ghi model dimensions: $L,D,H,H_{kv},D_{ff}$, expert count, top-$k$, context.
2. Vẽ một block và macrocycle; đánh dấu component dense nào được giữ nguyên.
3. Highlight mọi state tồn tại qua token (`KV cache`, recurrent state), qua depth (block summaries), hoặc qua requests (serving cache).
4. Gán mỗi novelty vào bottleneck và classification label.
5. Tự dự đoán trade-off trước khi đọc phần evaluation.

### Lượt 2 — audit evidence

1. Tìm ablation giữ data, scale và training budget gần nhau.
2. Tách quality metric, memory accounting, kernel speed, training throughput và serving latency.
3. Ghi hardware, precision, sequence length, batch/concurrency và baseline implementation.
4. Đánh dấu `author-reported`, `independently replicated`, hoặc `missing`.
5. Hạ scope claim nếu evidence không isolate component.

### Bộ câu hỏi cho từng novelty

- **What changes?** Equation, tensor shape hay schedule nào khác?
- **What stays the same?** Objective, attention semantics, FFN, data hay model scale?
- **Where is the state?** Per token, fixed-size, per layer, per expert hay per request?
- **Which phase benefits?** Training, prefill, decode hay serving concurrency?
- **What moves?** FLOPs, bytes trong HBM, bytes qua network, hoặc synchronization?
- **What new failure mode appears?** Quality loss, imbalance, overflow, instability, fragmentation?
- **What evidence isolates it?** Ablation nào và control có matched không?

## 8. PyTorch lab: baseline trước, bottleneck sau

Code dưới đây không mô phỏng frontier system. Nó tạo một dense block đủ nhỏ để:

- đếm parameter split giữa attention và FFN;
- quan sát score tensor $T\times T$;
- estimate KV-cache bytes;
- benchmark latency theo sequence length.

```python
import math
import time
import torch
import torch.nn as nn
import torch.nn.functional as F


class BaselineAttention(nn.Module):
    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out = nn.Linear(d_model, d_model, bias=False)
        self.last_score_shape = None

    def forward(self, x):
        B, T, D = x.shape
        qkv = self.qkv(x).view(B, T, 3, self.n_heads, self.head_dim)
        q, k, v = qkv.unbind(dim=2)
        q, k, v = [z.transpose(1, 2) for z in (q, k, v)]

        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        self.last_score_shape = tuple(scores.shape)  # (B, H, T, T)
        mask = torch.ones(T, T, dtype=torch.bool, device=x.device).tril()
        probs = F.softmax(scores.masked_fill(~mask, float("-inf")), dim=-1)
        y = probs @ v
        y = y.transpose(1, 2).contiguous().view(B, T, D)
        return self.out(y)


class DenseFFN(nn.Module):
    def __init__(self, d_model: int, expansion: int = 4):
        super().__init__()
        d_ff = expansion * d_model
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff, bias=False),
            nn.GELU(),
            nn.Linear(d_ff, d_model, bias=False),
        )

    def forward(self, x):
        return self.net(x)


class BaselineBlock(nn.Module):
    def __init__(self, d_model=256, n_heads=8):
        super().__init__()
        self.ln1 = nn.LayerNorm(d_model)
        self.attn = BaselineAttention(d_model, n_heads)
        self.ln2 = nn.LayerNorm(d_model)
        self.ffn = DenseFFN(d_model)

    def forward(self, x):
        x = x + self.attn(self.ln1(x))
        return x + self.ffn(self.ln2(x))


def n_params(module):
    return sum(p.numel() for p in module.parameters())


def kv_cache_bytes(batch, seq_len, layers, kv_heads, head_dim,
                   bytes_per_element=2):
    return (2 * batch * seq_len * layers * kv_heads
            * head_dim * bytes_per_element)


@torch.inference_mode()
def benchmark(block, seq_lengths=(64, 128, 256, 512), repeats=20):
    device = next(block.parameters()).device
    rows = []
    for T in seq_lengths:
        x = torch.randn(1, T, 256, device=device)
        for _ in range(5):
            block(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(repeats):
            block(x)
        if device.type == "cuda":
            torch.cuda.synchronize()
        ms = (time.perf_counter() - start) * 1000 / repeats
        rows.append((T, block.attn.last_score_shape, ms))
    return rows


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
block = BaselineBlock().eval().to(device)
print("attention params:", n_params(block.attn))
print("FFN params:", n_params(block.ffn))
print("KV GiB:", kv_cache_bytes(
    batch=1, seq_len=8192, layers=32,
    kv_heads=8, head_dim=128
) / 2**30)
for row in benchmark(block):
    print(row)
```

### Cách đọc kết quả

1. `FFN params` gần gấp đôi attention projections trong cấu hình $D_{ff}=4D$.
2. Khi $T$ gấp đôi, hai chiều cuối của score tensor cùng gấp đôi, nên số phần tử tăng gần bốn lần.
3. Benchmark latency sẽ không khớp hoàn hảo $T^2$: kernel, CPU/GPU, warm-up và small shapes tạo overhead.
4. Đổi `kv_heads=8 → 1` trong estimate mô phỏng memory accounting của MQA, **không** biến implementation trên thành MQA.
5. Code materialize full scores; không dùng nó để benchmark FlashAttention.

> [!warning] Đo đúng phase
> Forward trên cả sequence gần với training/prefill shape, không phải one-token KV-cached decode. Muốn đo decode, cần implementation cache K/V và chỉ đưa token mới vào mỗi step; xem [KV caching: implementation và kiểm chứng](kv-caching-beginners-guide.md).

### Bài tập

1. Thêm forward hooks để log output bytes của attention và FFN.
2. Thay dense FFN bằng toy top-1 MoE; log tokens/expert và coefficient of variation.
3. Dùng `torch.nn.functional.scaled_dot_product_attention`; kiểm tra output với baseline trước khi benchmark.
4. Viết hai ledger rows cho các thay đổi trên, kể cả downside.
5. Benchmark CPU và CUDA (nếu có), rồi giải thích vì sao cùng FLOPs nhưng latency ratio khác.

## 9. Những lỗi đọc paper phổ biến

1. **So model với tên gọi thay vì baseline component.** “MLA vs KDA” không đủ; phải so addressability, state growth, training parallelism và decode behavior.
2. **Gộp prefill với decode.** Optimization tốt cho long-prompt GEMM chưa chắc tốt cho one-token memory-bound decode.
3. **Nhầm cache compression với fixed state.** Cache nhỏ hơn/token vẫn có thể tăng theo $T$.
4. **Nhầm exact kernel với approximate architecture.** FlashAttention đổi execution, không đổi full-attention graph.
5. **Chỉ đếm active parameters.** MoE vẫn trả total-weight memory và communication.
6. **Coi router balance là quality objective duy nhất.** Nó còn là systems requirement để tránh straggler và idle devices.
7. **Biến design motivation thành fact.** “Residual dilution” cần ablation; không thể suy ra chỉ từ residual-sum equation.
8. **Dùng whole-model score để gán causality.** Data, scale, post-training và harness đều confound kết quả.
9. **Bỏ qua baseline quality.** Speedup so với implementation yếu không chứng minh superiority so với optimized baseline.
10. **Không ghi evidence gap.** `Missing ablation` là kết quả audit hợp lệ, không phải lý do để tự suy diễn.

## 10. Deliverable hoàn chỉnh cho Stage 9.1

Trước khi sang 9.2, hãy nộp hai phần.

### A. Dense baseline diagram

Diagram phải có:

- embedding/position path;
- pre-norm attention branch;
- pre-norm dense FFN branch;
- residual stream qua depth;
- `lm_head`;
- KV cache chỉ tồn tại trong inference;
- annotation khác nhau cho training, prefill và decode.

### B. Evidence ledger

Mỗi novelty cần:

- đúng một baseline component bị thay hoặc giữ nguyên;
- một bottleneck cụ thể, không dùng từ chung chung “efficiency”;
- ít nhất một downside/new bottleneck;
- evidence type và setup;
- marker `author-reported`, `independent`, `secondary`, hoặc `missing`.

Checklist cuối:

```text
[ ] Tôi biết tensor/state nào thay đổi.
[ ] Tôi biết complexity là theo T, L, experts hay devices.
[ ] Tôi tách architecture khỏi kernel/system/policy.
[ ] Tôi tách training, prefill và decode.
[ ] Tôi ghi cả expected benefit và cost mới.
[ ] Tôi không biến correlation của whole model thành component causality.
[ ] Tôi có thể nói claim nào là documented và claim nào là synthesis.
```

## 11. Hướng đọc tiếp

Sau method này, áp dụng nó theo thứ tự của roadmap:

1. DeepSeek-V2 → V3: theo dõi MLA, DeepSeekMoE, routing balance, FP8 và distributed schedule.
2. GPT-2 → Kimi Linear: so growing token-addressable KV cache với fixed-state memory và periodic global retrieval.
3. Kimi K3: trace information path theo sequence, depth và sparse experts.
4. Cuối cùng audit comparative evidence và missing ablations.

Mục tiêu không phải nhớ danh sách acronym. Mục tiêu là nhìn một model mới và luôn trả lời được: **nó thay gì, giải bottleneck nào, đổi cost sang đâu, và evidence mạnh đến mức nào?**

## Relationships

- **Elaborates:** Stage 9.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) bằng một reading workflow, evidence ledger và profiling lab.
- **Builds on:** [GPT-2 WebText pre-training and architecture](gpt-2-webtext-pre-training-and-architecture.md), [Decoder-only Transformer: beginner's guide](decoder-only-transformer-beginners-guide.md), [Inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md), và [KV caching](kv-caching.md).
- **Uses:** [Self-attention computational profile](self-attention-computational-profile.md), [Multi-head Latent Attention](multi-head-latent-attention.md), [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), [Auxiliary-loss-free MoE load balancing](auxiliary-loss-free-moe-load-balancing.md), [Attention Residuals](attention-residuals.md), và [DeepSeek-V3 training systems and FP8](deepseek-v3-training-systems-and-fp8.md) làm case studies cho sáu bottleneck.
- **Prepares for:** Stage 9.2–9.5 của roadmap, nơi method được áp dụng cho DeepSeek và Kimi lineages.

## Evidence limits

Bài này là curriculum synthesis, không phải controlled study chứng minh đây là thứ tự học tối ưu. GPT-2 và Transformer cung cấp primary evidence cho baseline; DeepSeek-V2/V3 và Attention Residuals cung cấp author-reported primary evidence cho các case study. FlashAttention evidence trong wiki hiện dựa trên secondary summary, nên bài chỉ dùng nó để giải thích distinction giữa exact attention semantics và IO-aware implementation, không dùng để khẳng định speedup cụ thể. Code lab là educational implementation; timing của nó không đại diện frontier model hoặc production serving.

[^radford-gpt-2-2019]: Radford et al., “Language Models are Unsupervised Multitask Learners” (2019), [PDF](../raw/gpt2.pdf), Sections 2.1–2.3 and Table 2.
[^vaswani-transformer-2017]: Vaswani et al., “Attention Is All You Need,” [source](../raw/arXiv-1706.03762v7/ms.tex), especially the architecture and self-attention complexity sections.
[^deepseek-v2-2024]: DeepSeek-AI, “DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model,” [source](../raw/arXiv-2405.04434v5/main.tex), Sections 2.1 and 3, including MLA equations and reported ablations.
[^deepseek-v3-2024]: DeepSeek-AI, “DeepSeek-V3 Technical Report,” [source](../raw/arXiv-2412.19437v2/main.tex), Sections 2–5 and Appendix A, including routing, systems, FP8, and ablations.
[^attnres-2026]: Kimi Team, “Attention Residuals,” [source](../raw/arXiv-2603.15031v1/main.tex), including mechanism, block form, systems analysis, and author-run evaluation.
[^flashattention-summary]: “FlashAttention overview” (Vietnamese summary), [source](../raw/FlashAttention.md), Sections 1–13. It summarizes Dao et al. (NeurIPS 2022); the primary paper has not been independently ingested into this wiki.
