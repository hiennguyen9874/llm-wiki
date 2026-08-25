---
type: Synthesis
title: "SSD → Mamba-2: fixed-state sequence mixing từ trực giác đến implementation — bài học cho người mới"
description: A top-down beginner course on how SSD combines fixed-state recurrence with chunked matrix computation, how Mamba-2 turns it into a scalable block, and how to derive, implement, and verify the mechanism.
tags: [ssd, mamba-2, ssm, recurrence, structured-attention, chunked-training, parallelism, pytorch, learning-roadmap]
status: stable
created: 2026-08-12
generated: { by: llm-wiki-agent/1, at: 2026-08-25T03:56:00Z }
sources:
  - id: dao-gu-2024
    resource: ../raw/arXiv-2405.21060v1/structure.tex
    title: "Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality"
---

# SSD → Mamba-2: fixed-state sequence mixing từ trực giác đến implementation — bài học cho người mới

`Structured State Space Duality` (`SSD`) giải quyết một tension trong sequence modeling: recurrent state có thể xử lý stream với memory không tăng theo context, nhưng token-by-token recurrence khó tận dụng GPU khi training; attention-like matrix computation chạy song song tốt, nhưng materializing mọi token pair rất đắt. SSD mô tả cùng một causal transformation bằng cả hai góc nhìn, rồi chia sequence thành chunks để dùng matrix multiplication bên trong chunk và chỉ truyền state qua các chunk boundaries. `Mamba-2` đặt SSD vào một block có parallel projections, local convolution, gate, normalization và layout phù hợp hơn với distributed training.[^dao-gu-2024]

> [!success] Sau bài này
> 1. Bạn có thể giải thích **vấn đề → cơ chế → tác động → khác biệt → cách dùng thực tế** mà chưa cần công thức.
> 2. Bạn có thể theo dõi data flow của recurrent SSD, chunked SSD và Mamba-2 block.
> 3. Bạn có thể derive recurrent form, structured attention-like form và chunk decomposition với shapes rõ ràng.
> 4. Bạn có thể chạy PyTorch reference và kiểm tra equivalence, causality, chunk-boundary continuity cùng fixed state bằng `torch.testing.assert_close`.
> 5. Bạn có thể tách hệ quả trực tiếp của thiết kế khỏi author-reported quality và speed benchmark.

## 1. Điều cần biết trước

Bạn chỉ cần:

- hiểu trực giác `Q/K/V` và causal token mixing từ [Attention: beginner's guide](attention-beginner-guide.md);
- phân biệt `training`, `prefill`, `decode` từ [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md);
- biết vector, matrix, `dot product`, `outer product` và matrix multiplication cơ bản.

Nên đọc [Mamba selective state spaces and architecture](mamba-selective-state-spaces-and-architecture.md) nếu muốn hiểu lineage từ Mamba-1. Bài này không implement production kernel, backward fusion, continuous-time SSM discretization, full language model hay distributed runtime. Code là executable reference để nhìn cơ chế, không phải benchmark implementation.

## 2. Bức tranh toàn cảnh — vấn đề và mental model

### 2.1 Vấn đề: chọn tuần tự hay song song?

Một sequence mixer phải vừa tích lũy history, vừa phục vụ hai chế độ rất khác:

- Khi `training` hoặc `prefill`, toàn sequence đã có sẵn; GPU hiệu quả nhất khi được cấp các matrix multiplications lớn và song song.
- Khi `decode`, mỗi lần chỉ có một token mới; giữ một compact state và update nó thường hợp lý hơn tính lại toàn history.

Hai baseline cực đoan đều có điểm yếu:

| Baseline | Điểm mạnh | Bottleneck |
|---|---|---|
| Token-by-token recurrence | State cố định; update tự nhiên khi decode | Dependency tuần tự làm naive training khó tận dụng GPU |
| Full attention-like matrix | Pairwise work phơi ra dưới dạng matrix operations | Full sequence matrix tăng theo bình phương length |

SSD hỏi: **nếu cùng transformation có cả recurrent view và matrix view, ta có thể chọn contraction order phù hợp với từng vùng của computation không?** Paper trả lời bằng semiseparable structure và block decomposition.[^dao-gu-2024]

**Ý tưởng cốt lõi trong một câu:** nén history cũ vào fixed-size state, nhưng xử lý các token gần nhau trong từng chunk bằng parallel matrix multiplication.

### 2.2 Mental model: đoàn tàu và trạm trung chuyển

```text
sequence dài

[token token token token] [token token token token] [token token token token]
       chunk 0                    chunk 1                    chunk 2
          │                          │                          │
   local matrix work         local matrix work         local matrix work
          │                          │                          │
       summary ─────────► boundary state ─────────► boundary state

Trong mỗi toa/chunk: xử lý nhiều token song song.
Giữa các toa/chunks: chỉ bàn giao một kiện state có kích thước cố định.
```

- `Local matrix work` giữ GPU bận bằng các operations đều đặn.
- `Boundary state` là interface nén giữa past chunk và future chunk.
- Chunk sau không nhận danh sách toàn bộ token cũ; nó nhận state đã tổng hợp.

Analogy này không có nghĩa state là summary bằng natural language. Nó là learned numerical state, và compression có thể mất hoặc trộn thông tin.

### 2.3 Ví dụ xuyên suốt: stream trạng thái đơn hàng

Ta dùng stream:

```text
1. order_17 created
2. order_42 created
3. order_17 shipped
4. order_42 delayed
5. query order_17
6. answer shipped
```

Giả sử tokens 1–3 là chunk đầu, tokens 4–6 là chunk sau. Chunk đầu cập nhật associations và tạo boundary state. Chunk sau nhận state đó, thêm event `order_42 delayed`, rồi token query đọc information liên quan đến `order_17`. Nếu learned write/read directions tách biệt tốt, output có thể ưu tiên `shipped`; nếu state capacity hoặc learned addressing không đủ, memories có thể interfere.

## 3. Cách hoạt động — nhìn từ input đến output

### 3.1 End-to-end flow của một SSD mixer

```text
input hidden states
      │
      ├─► value-like stream X ───────────────────────┐
      ├─► transition/decay A ────────────────────────┤
      ├─► write directions B ────────────────────────┤
      └─► read directions C ─────────────────────────┤
                                                     ▼
                             split sequence into chunks
                                                     │
              ┌──────────────────────────────────────┼──────────────────────┐
              ▼                                      ▼                      ▼
       local interactions                    chunk summaries       transition summaries
              │                                      │                      │
              └──────────────► short boundary-state scan ◄─────────────────┘
                                             │
                              add past-chunk contribution
                                             │
                                             ▼
                                       SSD outputs
```

Luồng gồm sáu bước:

1. **Project inputs:** model tạo value-like stream, transition factors, write directions và read directions cho từng token.
2. **Partition:** sequence được chia thành chunks có length cố định theo implementation.
3. **Compute local interactions:** các token trong cùng chunk dùng structured attention-like matrix operations.
4. **Compress each chunk:** mỗi chunk tạo contribution vào state ở cuối chunk.
5. **Scan boundaries:** summaries đi qua recurrence ngắn ở cấp chunk, không phải loop Python qua từng token.
6. **Expand past contribution:** state đi vào mỗi chunk được đọc bởi các tokens trong chunk; contribution này cộng với local output.

Bốn phần cốt lõi của block algorithm thường được gọi là `diagonal`, `right`, `center`, `left`: local diagonal blocks, input-to-state factors, state-to-state scan và state-to-output factors.[^dao-gu-2024]

### 3.1.1 Biểu đồ tương tác về khối SSD

Diagram dưới gộp cả **data flow của block** (input → projections → SSD mixer → gate → output) và **bốn phần của block algorithm** (`diagonal` / `right` / `center` / `left`), kèm shape cho một head. Node màu nhạt là cơ chế bên trong; node viền xanh là concept mở được khi bấm (ở chế độ đọc Obsidian) hoặc qua link tương đối bên dưới.

```mermaid
flowchart TD
    classDef flow fill:#f7f7f7,stroke:#888,stroke-width:1px;
    classDef concept fill:#e8f0fe,stroke:#4a7dd6,stroke-width:2px,rx:6px,ry:6px;

    IN["block input u<br/>(B, T, D)"] --> PROJ["parallel projections"]
    PROJ --> X["X value-like<br/>(B,T,H,P) = V"]
    PROJ --> A["A transition<br/>(B,T,H) scalar"]
    PROJ --> B["B write/expand<br/>(B,T,H,N) = K"]
    PROJ --> C["C read/contract<br/>(B,T,H,N) = Q"]
    PROJ --> Z["gate branch z"]

    X --> CONV["short depthwise conv"]
    CONV --> SSD["SSD mixer"]

    A --> SSD
    B --> SSD
    C --> SSD

    SSD --> DIAG["DIAGONAL<br/>intra-chunk (Q,Q)×(Q,P)"]
    SSD --> RIGHT["RIGHT<br/>per-chunk final state<br/>(B,C,H,P,N)"]
    RIGHT --> CENTER["CENTER<br/>chunk 1-SS scan<br/>(B,K,H,P,N)"]
    CENTER --> LEFT["LEFT<br/>state→output<br/>(B,C,L,H,P)"]
    DIAG --> ADD["Y = Y_local + Y_past<br/>(B,C,L,H,P)"]
    LEFT --> ADD

    ADD --> GATE["gate × (elementwise)"]
    GATE --> NORM["extra normalization"]
    NORM --> OUT["output projection"]
    OUT --> RES["residual stream<br/>(B,T,D)"]

    SSD -.-> C1["structured-state-space-duality"]
    SSD -.-> C2["mamba-2-architecture-and-parallelism"]
    SSD -.-> C3["linear-attention-as-fixed-state-memory"]
    SSD -.-> C4["self-attention-computational-profile"]
    class C1,C2,C3,C4 concept internal-link;
```

> [!info] Bấm để mở concept
> Trong Obsidian, các node viền xanh ở trên là link nội bộ (diagram tương tác) — bấm vào node sẽ điều hướng tới note tương ứng. Nếu trình render không hỗ trợ click, dùng link tương đối sau:
> - [Structured State Space Duality](structured-state-space-duality.md)
> - [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md)
> - [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md)
> - [Self-attention computational profile](self-attention-computational-profile.md)

### 3.2 Chạy ví dụ đơn hàng qua flow

| Bước | Chunk 0: events 1–3 | Chunk 1: events 4–6 |
|---|---|---|
| Local work | xử lý `created`, `created`, `shipped` | xử lý `delayed`, query, answer candidate |
| Chunk summary | nén các writes của chunk 0 | nén updates của chunk 1 |
| Boundary scan | tạo state sau event 3 | kết hợp incoming state với chunk 1 |
| Read | outputs cục bộ của chunk 0 | query đọc cả local update và compressed past |

Điểm quan trọng: event 3 ảnh hưởng query ở event 5 qua boundary state, không qua một token slot riêng được query trực tiếp.

### 3.3 Từ SSD layer đến Mamba-2 block

SSD chỉ là core sequence transformation. Mamba-2 block thêm các pathways cần cho một neural network thực tế:[^dao-gu-2024]

```text
block input u
   │
   ├─► parallel projections ─► X, A, B, C
   ├─► gate branch z ─────────────────────────────────────┐
   │                                                      │
   └─► X ─► short depthwise convolution ─► SSD mixer ─► gate
                                                          │
                                                   normalization
                                                          │
                                                   output projection
                                                          │
                                                   residual stream
```

| Thành phần | Vai trò |
|---|---|
| Parallel projections | Sinh các SSD inputs trực tiếp từ block input; giảm dependency giữa projection stages |
| Short convolution | Trộn local neighborhood trước recurrent/global sequence mixing |
| SSD mixer | Tích lũy và đọc fixed-size sequence state |
| Gate | Modulate mixer output theo token và channel |
| Added normalization | Ổn định path trước output projection trong design được báo cáo |
| Output projection | Đưa head features về model width |

Mamba-2 tạo transition/write/read branches song song từ block input, thay vì derive chúng sau projected stream như Mamba-1. Sự thay đổi này cho phép mỗi tensor-parallel shard tự giữ local heads và chỉ cần output all-reduce theo block analysis của paper.[^dao-gu-2024]

## 4. Tác động — behavior, quality, memory, compute và latency

### 4.1 Hệ quả trực tiếp từ thiết kế

| Trục | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
|---|---|---|---|
| Decode state | Pure SSD layer giữ state không tăng theo context length | History bị compress vào finite state | Runtime dùng recurrent update, không lưu teaching matrices |
| Token retrieval | Learned read có thể lấy information từ compressed history | Không có một slot tách biệt cho từng token | Task cho phép useful compression và state đủ capacity |
| Training/prefill work | Full-sequence work tăng tuyến tính theo length trong SSD algorithm | Có local quadratic work theo chunk và state-width cost | Optimized chunked kernel, chunk size và layout phù hợp |
| GPU utilization | Local matrix multiplications dùng tensor cores tốt hơn naive scan | Algorithm và kernel phức tạp hơn recurrence đơn giản | Workload đủ lớn để amortize overhead |
| Long sequence distribution | Chunks có thể trao đổi boundary states thay vì all token pairs | Causal state dependency vẫn còn | Context partition đúng thứ tự, communication không chi phối |
| Tensor parallelism | Parallel branches tránh một intermediate all-reduce của Mamba-1 design | Vẫn cần output collective | Head/group layout và local normalization tương thích |

Đây là consequences của state layout và data flow. Chúng không tự chứng minh quality, usable context, wall-clock speedup hay scaling efficiency end-to-end.[^dao-gu-2024]

### 4.2 Behavior và capacity

Fixed state tạo một information bottleneck: model phải quyết định history nào cần giữ và cách superpose nhiều signals. `Selective` transitions giúp input điều khiển retention, nhưng không biến state thành lossless storage. Tăng state dimension có thể tăng capacity, song cũng tăng recurrent state, per-token operations và parameter/activation costs.

Hệ quả trực tiếp là **không có structural guarantee về exact token recall**. Quality chỉ xuất hiện khi learned dynamics, model width, data và task khiến compression hữu ích.

### 4.3 Kết quả chỉ được báo cáo qua benchmark

Primary report nêu các kết quả sau trong setup của tác giả:[^dao-gu-2024]

- SSD kernel nhanh hơn Mamba fused scan khoảng `2–8×` ở benchmark large-state được test.
- Trên A100 80GB PCIe, state dimension 64, SSD timing vượt FlashAttention-2 từ sequence length 2K trong figure được báo cáo.
- Mamba-2 đạt Pile language-model results cạnh tranh với hoặc tốt hơn các baselines được so trong report.
- Synthetic multi-query associative recall cải thiện khi state size/model width tăng trong các cấu hình được test.
- Một số hybrid Mamba-2 + attention configurations tốt hơn pure Mamba-2 trong experiments của paper.

Các số trên không phải định lý. Chúng phụ thuộc hardware, dtype, kernel, state size, sequence length, batch, architecture matching, tokenizer, data và evaluation harness. Paper cũng lưu ý full Mamba-2 model có thể không hiệu quả bằng Transformer ở short sequence dù SSD kernel riêng lẻ nhanh.[^dao-gu-2024]

## 5. Sự khác biệt — baseline đổi ở đâu?

### 5.1 Bảng so sánh

| Cơ chế | Giống nhau | Khác nhau trong data flow | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| Mamba-1 selective scan | Đều dùng input-dependent recurrent dynamics và fixed state | Mamba-1 projections có dependency tuần tự hơn; scan kernel không dùng SSD block matmul pattern | Design đơn giản đã kiểm chứng nhưng large-state scan/TP kém thuận lợi hơn | Checkpoint/runtime Mamba-1 sẵn có |
| Recurrent SSD | Cùng exact SSD transformation | Loop/update theo từng token; không dựng token-pair matrix | Tốt cho decode, kém song song nếu dùng naive loop | One-token generation, reference semantics |
| Quadratic SSD view | Cùng exact SSD transformation | Dựng structured pair matrix cho toàn sequence | Song song dễ nhưng memory/work quadratic theo sequence | Toy verification hoặc local chunk nhỏ |
| Chunked SSD | Cùng outputs với recurrent SSD về algebra | Matrix work trong chunk, recurrent scan ở chunk boundaries | Linear full-sequence scaling nhưng implementation phức tạp | Training/prefill dài với optimized kernels |
| Softmax attention | Đều là causal content mixing | Query chấm từng token slot rồi softmax; history token-addressable | Direct retrieval nhưng KV state tăng và global pair work đắt | Exact token lookup và context trong budget |
| Hybrid SSD + attention | Kết hợp fixed-state và token-addressable paths | Một số layers giữ recurrent state, một số giữ KV cache | Chất lượng/retrieval tốt hơn có thể đổi lấy growing cache | Workload cần cả streaming lẫn direct retrieval |

### 5.2 Phần nào thay đổi, phần nào giữ nguyên?

```text
Giữ tương đối nguyên:
tokens → embeddings → residual stream → [sequence mixer] → residual/MLP → logits

Thay tại sequence mixer:
softmax baseline: query + per-token K/V history → token scores → weighted values
SSD:             new write + old state → updated state → learned read → output
chunked SSD:     local token matrices + boundary states → same SSD output
```

SSD không tự thay tokenizer, next-token objective, sampling, FFN/MoE hay scheduler. Mamba-2 thay block internals và systems layout quanh mixer, nhưng vẫn nằm trong decoder stack.

### 5.3 Các khái niệm dễ nhầm

- `Duality` không nói SSD bằng standard `softmax attention`; SSD structured matrix không có row-wise softmax.
- `Quadratic form` là một cách biểu diễn/tính cùng SSD transformation, không phải inference strategy cần dùng ở long context.
- `Chunked` không có nghĩa truncated backpropagation; đúng implementation vẫn truyền state và gradient qua boundaries.
- `Fixed-size state` không có nghĩa infinite, lossless hay token-addressable memory.
- `Linear in sequence length` không có nghĩa constant time per full sequence hoặc nhanh hơn trên mọi hardware.
- `SSD` là sequence-layer framework/algorithm; `Mamba-2` là block/architecture dùng SSD.

## 6. Trong thực tế — dùng ở đâu và đo thế nào?

### 6.1 Vị trí trong model và system

Trong pure Mamba-2 language model, SSD mixer thay attention mixer ở decoder blocks. Mỗi layer giữ SSM state và short convolution state khi decode. Trong hybrid model, attention layers vẫn có per-token KV cache; vì vậy chỉ state của SSD layers là context-independent.

Ở distributed training:

- `Tensor parallelism` chia heads/features; Mamba-2 paper phân tích một output all-reduce mỗi block nhờ parallel projections và local GroupNorm.
- `Sequence parallelism` chia residual/normalization activations theo sequence axis.
- `Context parallelism` chia token-mixing sequence thành contiguous chunks và truyền recurrent boundary state. Paper phân biệt pattern này với attention, nơi query/key blocks cần cross-worker interactions rộng hơn.[^dao-gu-2024]

### 6.2 Walkthrough: agent theo dõi log dài

Giả sử một operations agent đọc liên tục status và incident logs:

1. **Prefill:** prompt ban đầu được chia chunks; mỗi SSD layer dùng local matrix work và boundary scan để tạo final state.
2. **Streaming:** mỗi log token mới update recurrent và convolution states; SSD state shape không tăng chỉ vì stream dài hơn.
3. **Query:** khi người dùng hỏi “service nào vừa recovery?”, learned read lấy information từ state đã tổng hợp.
4. **Hybrid fallback:** nếu model có attention layers, chúng có thể truy cập token positions cụ thể trong retained context nhưng vẫn trả KV-cache cost.
5. **Serving:** scheduler batch các streams; memory accounting phải gồm weights, SSD states, conv states, temporary buffers và KV cache của bất kỳ attention layer nào.

Workload hưởng lợi nếu history chủ yếu là evolving state, xu hướng hoặc summaries. Nếu requirement là trích nguyên văn một UUID duy nhất từ rất xa hoặc audit exact source position, pure fixed-state mixer là lựa chọn rủi ro; hybrid attention hoặc external retrieval phù hợp hơn.

### 6.3 Khi nên và không nên dùng

| Nên cân nhắc | Không nên mặc định chọn |
|---|---|
| Long streaming, online state tracking | Exact long-range copy/retrieval là requirement cứng |
| KV-cache growth giới hạn concurrency | Context ngắn và optimized attention đã đủ nhanh |
| Training/prefill có optimized SSD kernel | Chỉ có naive Python/token loop implementation |
| Model được train hoặc checkpointed với Mamba-2 | Muốn thay attention checkpoint mà không retrain/validate |
| Distributed layout hưởng lợi từ local heads/state passing | Communication, unsupported dtype hoặc kernel dominates |

### 6.4 Measurement cần kiểm tra

- Tách `training step time`, `prefill latency`, `TTFT`, `decode latency/TPOT` và throughput.
- Sweep sequence length, batch/concurrency, state dimension, chunk size và dtype.
- Báo peak memory và tách weights, activations, SSD state, conv state, temporary buffers, hybrid KV cache.
- Đo next-token quality cùng exact recall, repeated updates, distractors và context-length generalization.
- Với distributed run, đo collective time, state-passing bytes, scaling efficiency và load imbalance.
- So matched model size, active FLOPs, data, tokens, tokenizer, hardware, kernel và harness.

Từ theory không thể suy ra maximum reliable context, quality parity, speedup end-to-end, optimal chunk size hay optimal tỷ lệ attention layers.

> [!note] Checkpoint trước phần toán
> Đến đây bạn nên trả lời được: SSD giải quyết tension giữa recurrent efficiency và parallel training; nó dùng local chunk computation cộng boundary-state scan; tác động trực tiếp là bounded decode state nhưng finite retrieval capacity; nó khác softmax ở việc không giữ token slots; và nó phù hợp với streaming/long-sequence workloads khi có optimized kernel và measurement đúng phạm vi.

## 7. Toán học — zoom in sau trực giác

### 7.1 Bảng ký hiệu

| Ký hiệu | Shape cho một head | Ý nghĩa |
|---|---:|---|
| $t,i$ | scalar indices | vị trí output và input |
| $T$ | scalar | sequence length |
| $Q$ | scalar | chunk length |
| $K$ | scalar | number of chunks |
| $P$ | scalar | value/head width |
| $N$ | scalar | recurrent state dimension |
| $x_t$ | $(P,)$ | value-like input tại token $t$ |
| $b_t,c_t$ | $(N,)$ | write direction và read direction |
| $a_t$ | scalar | transition/retention factor |
| $S_t$ | $(P,N)$ | recurrent matrix state |
| $y_t$ | $(P,)$ | output tại token $t$ |
| $L$ | $(T,T)$ | causal transition-product matrix |
| $X,Y$ | $(T,P)$ | stacked inputs và outputs |
| $B,C$ | $(T,N)$ | stacked write/read directions |

Với batch và heads, input có shape `(B, T, H, P)` và state có shape `(B, H, P, N)`. Trục sequence không nằm trong persistent state.

### 7.2 Trường hợp nhỏ nhất: scalar recurrence tính tay

**Trực giác.** State mới giữ một phần state cũ rồi cộng input hiện tại.

**Công thức.**

$$
h_t=a_t h_{t-1}+x_t,\qquad y_t=h_t.
$$

**Ý nghĩa ký hiệu.** $h_t$ là scalar state; $a_t$ là retention; $x_t$ là input; output đọc trực tiếp state.

**Shape flow.** `scalar × scalar + scalar → scalar`.

**Ví dụ số.** Với initial state bằng zero, inputs `[2, 4, 10]` và retention `[1, 0.5, 0.2]`:

$$
h_0=2,\qquad h_1=0.5\cdot2+4=5,\qquad h_2=0.2\cdot5+10=11.
$$

**Kết luận.** Token đầu ảnh hưởng token cuối qua product của các transition factors nằm giữa chúng; một factor nhỏ gần như reset distant history.

### 7.3 SSD matrix state: write rồi read

**Trực giác.** Scalar state quá nhỏ. SSD dùng outer product để ghi value-like input theo một learned direction, rồi read state theo direction khác.

**Công thức.**

$$
\boxed{S_t=a_tS_{t-1}+x_tb_t^{\top}},\qquad
\boxed{y_t=S_tc_t}.
$$

**Ý nghĩa ký hiệu.** $a_t$ decay toàn state cũ; $b_t$ chọn state direction để write; $c_t$ chọn direction để read.

**Shape flow.**

```text
old state       write outer product             new state
 (P,N)     +    (P,1) × (1,N)       →           (P,N)

new state       read vector                     output
 (P,N)     ×       (N,)             →             (P,)
```

**Ví dụ số.** Chọn `P=2`, `N=2`, old state bằng zero, input `[3, 5]`, write direction `[1, 0]`. Write tạo matrix có cột đầu `[3, 5]` và cột hai bằng zero. Read direction `[1, 0]` trả lại `[3, 5]`; read `[0, 1]` trả zeros.

**Kết luận.** State có `P × N` elements bất kể đã đọc bao nhiêu tokens; đổi lại mọi history phải đi qua finite interface này.[^dao-gu-2024]

### 7.4 Unroll: từ recurrence đến structured attention-like form

**Trực giác.** Thay state cũ lặp lại cho thấy output hiện tại là tổng mọi past write, mỗi write bị decay theo quãng đường và được read theo content.

**Công thức.**

$$
S_t=\sum_{i=0}^{t}\left(\prod_{r=i+1}^{t}a_r\right)x_ib_i^{\top},
$$

$$
y_t=\sum_{i=0}^{t}\underbrace{\left(\prod_{r=i+1}^{t}a_r\right)}_{L_{t,i}}
\underbrace{\left(c_t^{\top}b_i\right)}_{\text{content interaction}}x_i.
$$

Stack toàn sequence:

$$
\boxed{Y=\left(L\circ CB^{\top}\right)X},\qquad
L_{t,i}=\begin{cases}
\prod_{r=i+1}^{t}a_r,&i\le t,\\
0,&i>t.
\end{cases}
$$

**Ý nghĩa ký hiệu.** $L$ chứa causal transition products; `circ` là elementwise product; matrix `C B transpose` chứa read-write content scores.

**Shape flow.**

```text
C (T,N) × Bᵀ (N,T) → content scores (T,T)
L (T,T) elementwise-multiplied by scores → M (T,T)
M (T,T) × X (T,P) → Y (T,P)
```

**Ví dụ số.** Với scalar case ở trên, transition matrix là:

$$
L=\begin{bmatrix}
1&0&0\\
0.5&1&0\\
0.1&0.2&1
\end{bmatrix}.
$$

Hệ số `0.1` từ token đầu đến token ba là product `0.5 × 0.2`. Matrix nhân inputs `[2,4,10]` trả `[2,5,11]`.

**Kết luận.** Recurrent và quadratic forms là hai contraction orders của cùng SSD transformation. Đây là `structured attention-like` form, không phải softmax attention.[^dao-gu-2024]

### 7.5 Vì sao semiseparable structure cho phép chunking?

**Trực giác.** Mọi influence từ chunk cũ sang chunk mới phải đi qua boundary state có width hữu hạn. Vì vậy off-diagonal chunk blocks factor qua interface nhỏ thay vì cần một arbitrary dense matrix.

**Công thức tổng quát.** Một time-varying SSM:

$$
h_t=A_th_{t-1}+B_tx_t,\qquad y_t=C_t^{\top}h_t
$$

sinh causal matrix entries:

$$
M_{t,i}=C_t^{\top}A_tA_{t-1}\cdots A_{i+1}B_i,\qquad i\le t.
$$

SSD specialization dùng scalar-identity transition:

$$
A_t=a_tI.
$$

**Ý nghĩa ký hiệu.** General transition có thể trộn state dimensions; SSD restriction scale toàn state bằng một scalar ở mỗi head/token. Restriction này làm transition products tách khỏi content factors.

**Shape flow.** General state vector đi qua an `N × N` boundary transformation. Trong matrix-state convention của bài, boundary interface có `P × N` elements. Một block influence từ old inputs sang future outputs factor thành `input → boundary state → output`, nên rank bị chặn bởi state dimension.[^dao-gu-2024]

**Ví dụ số.** Chia six tokens thành two chunks length three. Thay vì giữ a dense `3 × 3` arbitrary cross-chunk map, chunk đầu tạo one state; chunk hai dùng its three read directions để expand state thành three output contributions.

**Kết luận.** Semiseparable factorization là lý do algebraic cho bốn bước `diagonal/right/center/left`.

### 7.6 Chunked SSD: four-part decomposition

**Trực giác.** Tách output của mỗi chunk thành contribution từ local tokens và contribution từ all previous chunks.

**Công thức.** Với chunk index $j$:

$$
Y^{(j)}=Y_{\mathrm{local}}^{(j)}+Y_{\mathrm{past}}^{(j)}.
$$

Block algorithm thực hiện:

1. `diagonal`: tính $Y_{\mathrm{local}}^{(j)}$ bằng local structured matrix có shape `Q × Q`;
2. `right`: compress inputs chunk $j$ thành final-state contribution shape `P × N`;
3. `center`: scan $K$ chunk summaries để tìm incoming state cho từng chunk;
4. `left`: expand incoming state thành $Y_{\mathrm{past}}^{(j)}$ shape `Q × P`.

**Ý nghĩa ký hiệu.** $Q$ là chunk length; $K$ là number of chunks; chỉ center scan mang dependency dọc sequence ở cấp chunk.

**Shape flow.**

```text
local:    (Q,Q) × (Q,P) → (Q,P)
compress: Q token writes → (P,N)
scan:     K states, mỗi state (P,N)
expand:   incoming (P,N) + Q reads → (Q,P)
```

**Ví dụ số.** Sequence length 12, chunk length 3 tạo 4 chunks. Naive recurrence có 12 token steps; block view phơi local work của 4 chunks song song và chỉ scan 4 summaries. Đây là structural explanation, không phải claim Python implementation sẽ nhanh hơn bốn lần.

**Kết luận.** Khi head width, state dimension và chunk length cùng scale theo một width, paper cho full-sequence training work tuyến tính theo sequence length, activation memory tuyến tính theo sequence length, và recurrent inference state độc lập với sequence length; constants vẫn phụ thuộc mạnh vào state/head widths.[^dao-gu-2024]

### 7.7 Proof sketch có thể bỏ qua

Chọn any boundary giữa old chunks và future chunks. Mọi causal influence đi từ old inputs vào recurrent state tại boundary, rồi từ state đó ra future outputs. Do intermediate interface chỉ có finite state dimension, cross-boundary submatrix có bounded rank. Ngược lại, semiseparable generators cung cấp factors tương ứng với transition, write và read operators. SSD dùng scalar transition để đưa factorization về mask nhân content matrix, tạo dual recurrent/matrix views. Đây là proof intuition; theorem đầy đủ và index conventions nằm trong primary paper.[^dao-gu-2024]

## 8. Implementation — PyTorch tối thiểu

Code dưới cụ thể hóa Sections 7.3–7.4. `ssd_recurrent` là decode/reference path; `ssd_quadratic` materialize matrix để verify duality. Nó không implement optimized four-part kernel.

```python
import torch


def ssd_recurrent(x, a, b, c, initial_state=None):
    """
    Exact recurrent SSD reference, write-then-read convention.

    x: [B, T, H, P]       value-like inputs
    a: [B, T, H]          scalar transitions
    b: [B, T, H, N]       write directions
    c: [B, T, H, N]       read directions
    state: [B, H, P, N]   no sequence axis
    """
    batch, length, heads, width = x.shape
    state_dim = b.shape[-1]
    if initial_state is None:
        state = x.new_zeros(batch, heads, width, state_dim)
    else:
        state = initial_state.clone()

    outputs = []
    for t in range(length):
        write = torch.einsum("bhp,bhn->bhpn", x[:, t], b[:, t])
        state = a[:, t, :, None, None] * state + write
        y_t = torch.einsum("bhpn,bhn->bhp", state, c[:, t])
        outputs.append(y_t)

    return torch.stack(outputs, dim=1), state


def transition_mask(a):
    """Teaching reference: materialize L with shape [B, H, T, T]."""
    batch, length, heads = a.shape
    mask = a.new_zeros(batch, heads, length, length)
    for t in range(length):
        mask[:, :, t, t] = 1.0
        running = torch.ones_like(a[:, 0])
        for i in range(t - 1, -1, -1):
            running = running * a[:, i + 1]
            mask[:, :, t, i] = running
    return mask


def ssd_quadratic(x, a, b, c):
    """Exact matrix-form reference; never use this for long contexts."""
    decay = transition_mask(a)                         # [B,H,T,T]
    content = torch.einsum("bthn,bshn->bhts", c, b) # [B,H,T,T]
    mixing = decay * content                           # elementwise
    return torch.einsum("bhts,bshp->bthp", mixing, x)
```

### 8.1 Cách code nối với cơ chế

- `write` là outer product từ Section 7.3.
- `state` không chứa sequence axis; đây là fixed-state decode path.
- `transition_mask` materialize products từ Section 7.4 chỉ để kiểm chứng.
- `mixing` là structured mask nhân content interaction.
- Production chunked SSD thay full `T × T` teaching matrix bằng local `Q × Q` blocks, chunk summaries và fused kernels.[^dao-gu-2024]

> [!warning] Teaching code
> `for` loops, `float64` và full transition matrix ưu tiên auditability. Không dùng timing của code này để suy ra Mamba-2 latency. Production còn cần convolution state, grouped heads, fused forward/backward, stable cumulative transitions, variable lengths, padding/reset semantics và mixed-precision validation.

## 9. Verification — chạy trước benchmark

```python
@torch.inference_mode()
def make_case(length=8):
    torch.manual_seed(7)
    dtype = torch.float64
    B, H, P, N = 2, 3, 4, 5
    x = torch.randn(B, length, H, P, dtype=dtype)
    a = torch.sigmoid(torch.randn(B, length, H, dtype=dtype))
    b = torch.randn(B, length, H, N, dtype=dtype)
    c = torch.randn(B, length, H, N, dtype=dtype)
    return x, a, b, c


@torch.inference_mode()
def test_recurrent_equals_quadratic():
    x, a, b, c = make_case()
    y_rec, _ = ssd_recurrent(x, a, b, c)
    y_mat = ssd_quadratic(x, a, b, c)
    torch.testing.assert_close(y_rec, y_mat, rtol=1e-10, atol=1e-10)


@torch.inference_mode()
def test_causality():
    x, a, b, c = make_case()
    split = 5
    y_ref, _ = ssd_recurrent(x, a, b, c)

    x2, a2, b2, c2 = x.clone(), a.clone(), b.clone(), c.clone()
    x2[:, split:] += 100.0
    a2[:, split:] = 0.1
    b2[:, split:] -= 50.0
    c2[:, split:] += 25.0
    y_changed, _ = ssd_recurrent(x2, a2, b2, c2)

    torch.testing.assert_close(
        y_ref[:, :split], y_changed[:, :split], rtol=1e-10, atol=1e-10
    )


@torch.inference_mode()
def test_chunk_boundary_continuity():
    x, a, b, c = make_case(length=10)
    split = 4
    y_full, final_full = ssd_recurrent(x, a, b, c)

    y_left, boundary = ssd_recurrent(
        x[:, :split], a[:, :split], b[:, :split], c[:, :split]
    )
    y_right, final_split = ssd_recurrent(
        x[:, split:], a[:, split:], b[:, split:], c[:, split:], boundary
    )
    y_split = torch.cat([y_left, y_right], dim=1)

    torch.testing.assert_close(y_full, y_split, rtol=1e-10, atol=1e-10)
    torch.testing.assert_close(final_full, final_split, rtol=1e-10, atol=1e-10)


@torch.inference_mode()
def test_fixed_state_shape():
    expected = torch.zeros(2, 3, 4, 5, dtype=torch.float64)
    for length in (1, 8, 64):
        x, a, b, c = make_case(length)
        _, state = ssd_recurrent(x, a, b, c)
        torch.testing.assert_close(
            torch.zeros_like(state), expected, rtol=0.0, atol=0.0
        )


test_recurrent_equals_quadratic()
test_causality()
test_chunk_boundary_continuity()
test_fixed_state_shape()
print("all SSD reference tests passed")
```

### 9.1 Test nào chứng minh điều gì?

1. **Recurrent equals quadratic:** hai views cho cùng output trong toy `float64` setup.
2. **Causality:** thay toàn bộ future branches không đổi prior outputs.
3. **Chunk-boundary continuity:** chia sequence và truyền exact state cho kết quả giống full recurrent run; đây là semantic basis của state passing.
4. **Fixed state shape:** state shape không đổi khi sequence length đổi.

Các tests không chứng minh optimized chunk kernel đúng, gradients match, BF16 ổn định, full Mamba-2 checkpoint parity, quality hoặc speed.

## 10. Benchmark và trade-offs đúng phạm vi

### 10.1 Complexity/state ledger

| Path | Materialized sequence interaction | Persistent decode state mỗi head | Dùng cho |
|---|---:|---:|---|
| Recurrent SSD reference | không có full pair matrix | `P × N` | one-token decode, semantic reference |
| Quadratic SSD reference | `T × T` | không phải serving cache | equivalence test nhỏ |
| Chunked SSD kernel | local `Q × Q` blocks + chunk states | `P × N` khi decode | training/prefill |
| Softmax attention | global/local score pattern tùy variant | per-token KV entries | token-addressable retrieval |

Với SSD regime trong paper nơi state width, head width và chunk length cùng bậc, reported asymptotic accounting là full-sequence training FLOPs tuyến tính theo sequence length, activation memory tuyến tính theo sequence length, còn recurrent state không chứa sequence length.[^dao-gu-2024] Đây là algorithmic accounting, không phải latency benchmark.

### 10.2 Benchmark protocol tối thiểu

| Measurement | Sweep | Giữ/báo cáo |
|---|---|---|
| Training step time | sequence, batch, state, chunk | model config, dtype, backward, optimizer, hardware |
| Prefill | prompt length, batch | kernel, compilation, warmup, peak memory |
| Decode TPOT | current context, concurrency | state layout, scheduler, output length |
| Kernel time | state width, chunk, sequence | exact kernel versions và synchronization |
| Quality | context/task difficulty | data, tokens, parameters, tokenizer, harness |
| Distributed scaling | devices, TP/CP degree | interconnect, collectives, communication overlap |

Không so Python recurrent loop với FlashAttention rồi kết luận architecture speed. Không dùng kernel-only gain để dự đoán end-to-end model gain. Không dùng synthetic recall để khẳng định arbitrary real-world memory.

### 10.3 Decision table

| Ưu tiên | Lựa chọn cần thử | Rủi ro cần đo |
|---|---|---|
| Bounded layer state khi stream dài | Pure/recurrent SSD | exact recall và state saturation |
| Fast long-sequence training | Chunked SSD kernel | crossover length, chunk tuning, dtype stability |
| Direct lookup của distant token | Attention hoặc hybrid | KV-cache memory và bandwidth |
| Multi-GPU long context | SSD context parallelism | boundary dependency và communication overlap |
| Short prompts trên mature runtime | Optimized attention baseline trước | Mamba-2 full-block overhead có thể thắng/lỗ tùy setup |

## 11. Debug checklist

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên |
|---|---|---|
| Recurrent khác matrix form | Sai transition product hoặc write/read order | Check diagonal bằng one và product bắt đầu từ token kế tiếp |
| Future làm đổi past | Mask/indexing leak | Perturb đồng thời `x/a/b/c` sau split |
| Split run khác full run | Không truyền exact boundary state | So final state của chunk đầu với state tại split |
| State tăng theo length | Vô tình giữ all intermediate states | Persistent cache phải chỉ có final state và conv buffer |
| Output explode/vanish | Transition parameterization không ổn định | Inspect transition ranges và cumulative products |
| BF16 fail nhưng FP64 pass | Precision/accumulation issue | So FP32 reference trước, đặt tolerance có lý do |
| Packed examples leak | Không reset state ở document boundary | Test đổi document trước không ảnh hưởng document sau |
| Chunk sizes cho outputs khác nhau | Boundary/local decomposition bug | Test edge cases chunk length one và full length |
| TP có extra communication | Branches/norm không shard local | Vẽ projection dependency và collective timeline |
| Kernel nhanh, model chậm | Projections/conv/FFN/communication dominate | Profile end-to-end theo operator |

## 12. Giới hạn và bước tiếp theo

Bài này không:

- derive continuous-time SSM discretization;
- implement optimized four-part SSD kernel hoặc backward pass;
- reproduce Mamba-2 normalization, convolution, residual và grouped-head details trong one full block;
- establish quality, stability hay speed trên target hardware;
- chứng minh fixed state có thể nhớ lossless context bất kỳ.

Bước tiếp theo:

1. Đọc [Structured State Space Duality](structured-state-space-duality.md) để xem concise theorem/algorithm statement.
2. Đọc [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) để zoom vào block và distributed layout.
3. Đọc [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) để xem reported benchmark cùng evidence limits.
4. Thêm gradient equivalence test giữa recurrent và optimized chunk implementation của bạn.
5. So sánh với [Linear attention as fixed-state memory](linear-attention-as-fixed-state-memory.md) và [Multi-head Latent Attention](multi-head-latent-attention.md) theo retrieval/state-growth axes.

## Relationships

- **Depends on:** [Mamba selective state spaces and architecture](mamba-selective-state-spaces-and-architecture.md) — cung cấp selective recurrent lineage trước Mamba-2.
- **Depends on:** [Self-attention computational profile](self-attention-computational-profile.md) — baseline cho pairwise interaction và sequence-scaling trade-off.
- **Synthesizes:** [Structured State Space Duality](structured-state-space-duality.md) — dual recurrent/matrix views và chunk decomposition.
- **Synthesizes:** [Mamba-2 architecture and parallelism](mamba-2-architecture-and-parallelism.md) — block projections, heads và distributed execution.
- **Evaluated by:** [Mamba-2 evaluation and efficiency](mamba-2-evaluation-and-efficiency.md) — author-reported quality, recall và speed results.
- **Contrasts with:** [Multi-head Latent Attention](multi-head-latent-attention.md) — MLA nén representation theo token nhưng vẫn giữ token axis.
- **Elaborates:** Stage 8 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) — fixed-state và long-context mixing.

## Evidence limits

Duality, semiseparable structure, block SSD algorithm, complexity accounting, Mamba-2 block changes, distributed communication analysis và benchmark statements đều dựa trên primary report của Dao và Gu.[^dao-gu-2024] Code, examples, mental models, decision tables và teaching order là **pedagogical synthesis**. Source bundle không cung cấp independent replication; kernel and model claims phải được kiểm tra lại trên checkpoint, implementation, dtype, hardware và workload đích. Fixed-size state chỉ bảo đảm bounded tensor dimensions, không bảo đảm lossless memory, constant end-to-end latency, quality parity với softmax attention hay reliable context vô hạn.

[^dao-gu-2024]: Tri Dao và Albert Gu, “Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality,” arXiv:2405.21060v1, [source](../raw/arXiv-2405.21060v1/structure.tex), Sections 2–10 và bundled algorithm/system appendices.
