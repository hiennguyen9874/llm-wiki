---
type: Synthesis
title: "Sparse-attention architecture: từ chọn vùng đọc đến compressed entries — khóa học cho người mới"
description: A top-down beginner course on fixed and learned sparse attention, pooled retrieval, locality-aware index reuse, compressed entries, and the separation of sparse reads from retained KV state.
tags: [sparse-attention, attention, long-context, kv-cache, pytorch, learning-roadmap]
status: stable
created: 2026-08-30
generated:
  by: llm-wiki-agent/1
  at: 2026-08-30T11:28:34+07:00
sources:
  - id: sparse-evolution
    resource: sparse-attention-evolution-and-architecture-comparison.md
    title: Sparse Attention evolution and architecture comparison
  - id: dsa-concept
    resource: deepseek-sparse-attention.md
    title: DeepSeek Sparse Attention
  - id: qsa-concept
    resource: qwen-sparse-attention.md
    title: Qwen Sparse Attention
  - id: lsa-concept
    resource: longcat-sparse-attention.md
    title: LongCat Sparse Attention
  - id: csa-hca-concept
    resource: compressed-sparse-and-heavily-compressed-attention.md
    title: Compressed sparse and heavily compressed attention
  - id: lsa-evidence
    resource: longcat-sparse-attention-systems-trade-offs-and-evidence.md
    title: LongCat Sparse Attention systems trade-offs and evidence
  - id: kv-cache-tradeoffs
    resource: kv-cache-compression-and-trade-offs.md
    title: KV-cache compression and trade-offs
---

# Sparse-attention architecture: từ chọn vùng đọc đến compressed entries — khóa học cho người mới

`Sparse attention` giảm số history entries mà một query đưa vào core attention, nhưng các architecture khác nhau quyết định **chọn gì**, **chọn ở độ hạt nào**, **đọc có liên tục trong memory không**, và **history được lưu dưới dạng gì**. Tiến trình từ fixed local mask đến DSA, QSA, LSA rồi CSA/HCA vì vậy không chỉ là “giảm top-k”: nó đi từ topology cố định, qua learned token/block retrieval và index reuse, tới thay đổi cả KV representation. Bài học này giữ riêng ba sổ cái: `read set`, `indexer work`, và `retained cache`, vì giảm sparse reads không tự động làm cache nhỏ hơn.[^sparse-evolution][^kv-cache-tradeoffs]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Giải thích được sparse attention giải quyết bottleneck nào và vì sao “đọc ít” khác “lưu ít”.
> 2. Trace được luồng `query → index/mask → selected entries → gather → core attention → output` cho local, DSA, QSA, LSA và CSA/HCA.
> 3. So sánh token selection, block selection, locality-aware reuse và compressed-entry retrieval theo quality, compute, memory, latency và addressability.
> 4. Chạy một PyTorch lab có local attention và toy block top-k selector; đo `indexer work`, `selected-token recall`, `gather locality`, `retained cache` và remote-token addressability.
> 5. Kiểm chứng causal behavior và output của sparse path bằng `torch.testing.assert_close`, rồi đọc benchmark trong đúng phạm vi evidence.

## 1. Bức tranh toàn cảnh

### 1.1 Vấn đề: history dài làm query phải tìm trong một kho quá lớn

Trong dense causal attention, mỗi query có thể so sánh trực tiếp với mọi token trước nó. Đây là baseline mạnh về `token addressability`: một chi tiết ở rất xa vẫn có slot riêng để được đọc. Nhưng khi prompt dài, full-sequence attention phải xử lý rất nhiều query–key pairs; lúc decode, mỗi token mới vẫn phải đọc một prefix ngày càng dài. KV cache cũng tăng theo context nếu mỗi token được giữ lại.[^sparse-evolution]

`Sparse attention` hỏi một câu hẹp hơn: **query hiện tại thực sự cần đưa những history entries nào vào core attention?** Nếu chỉ đọc một subset nhỏ, phần core attention có thể làm ít việc hơn. Nhưng trước đó hệ thống có thể phải chạy một `indexer`, và entries không được đọc vẫn có thể còn nguyên trong cache.[^dsa-concept][^qsa-concept]

### 1.2 Ý tưởng cốt lõi trong một câu

**Dùng một fixed rule hoặc learned indexer để tạo một read set nhỏ trước core attention; sau đó tối ưu đơn vị selection, memory locality, index reuse và cuối cùng cả representation của entries được lưu.**[^sparse-evolution]

### 1.3 Mental model: thư viện, mục lục và kho sách

```text
Dense attention
  độc giả → xem từng cuốn trong toàn kho → chọn nội dung

Local attention
  độc giả → chỉ xem kệ ngay bên cạnh

DSA
  độc giả → mục lục học được chọn từng cuốn → lấy các cuốn rời rạc

QSA / pooled retrieval
  độc giả → mục lục chọn từng cụm kệ → lấy mọi cuốn trong cụm

LSA
  độc giả → luôn giữ quầy đầu + kệ gần
          → một tầng lập danh sách, tầng kế tiếp tái dùng
          → tìm khu vực trước, rồi mới tìm cuốn trong khu vực

CSA / HCA
  kho đã thay nhiều cuốn cũ bằng bản tóm tắt theo cụm
  độc giả → đọc selected summaries hoặc toàn bộ số summaries ít hơn
          + vẫn đọc nguyên văn ở kệ gần
```

Điểm quan trọng: **danh sách sách được lấy** là `sparse reads`; **cách sách được cất trong kho** là `KV representation`; **có vứt sách cũ hay không** là `cache retention`. Ba quyết định này có thể thay đổi độc lập.

### 1.4 Điều cần biết trước

- [Attention: beginner's guide](attention-beginner-guide.md): Q/K/V, softmax và causal mask.
- [Attention design matrix](attention-design-matrix-beginners-course.md): tách positional mechanism, KV representation và access pattern.
- [KV caching](kv-caching-beginners-guide.md): vì sao decode giữ K/V theo layer và token.
- [MLA và token-addressable memory](mla-token-addressable-memory-beginners-guide.md): một compressed latent **mỗi token** vẫn khác fixed-state.

Bài này không dạy kernel CUDA/Triton, distributed context parallelism hay cách continued pre-training một frontier checkpoint. PyTorch lab là semantic reference: vòng lặp Python, list indices và `torch.cat`/gather minh họa không đại diện serving kernel.

## 2. Cách hoạt động — nhìn từ đầu đến cuối

Ta dùng một ví dụ xuyên suốt: prompt dài chứa bốn vùng — system instruction ở đầu, nhiều đoạn log cũ, lỗi thật ở xa ghi `database timeout`, và các log mới gần query. Query cuối hỏi: “root cause là gì?”.

### 2.1 Luồng chung

```text
hidden state của query
        │
        ├──► fixed mask hoặc learned indexer
        │         │
        │         ├──► candidate scores
        │         └──► selected token/block/entry indices
        │
retained history ─┴──► gather selected K/V representations
                              │
                              ▼
                    causal core attention
                              │
                              ▼
                       output representation
```

| Thành phần | Vai trò | Câu hỏi kiểm tra |
|---|---|---|
| `mask/indexer` | tạo candidate và xếp hạng | Có scan toàn history không? |
| `selection unit` | token, block, page hay compressed entry | Relevant token có thể bị ẩn trong group không? |
| `gather` | lấy K/V từ memory | Reads liên tục hay rải rác? |
| `core attention` | tính softmax trên selected set | Budget thực tế là bao nhiêu entries? |
| `retained state` | history còn được lưu sau query | Cache có nhỏ đi hay chỉ đọc ít đi? |

### 2.2 Fixed local/block mask: chọn bằng vị trí

Với `local attention`, query cuối chỉ đọc vài log gần nhất. Không có indexer nên data flow ngắn và gather thường contiguous. Nếu `database timeout` nằm ngoài window, layer này không thể đọc trực tiếp nó. `Block-sparse mask` mở hoặc đóng nguyên score blocks theo topology định trước; đều đặn hơn token-level random access nhưng vẫn có structural blind spot.[^sparse-evolution]

Trong ví dụ, local window đọc các triệu chứng mới nhưng bỏ lỡ root cause ở xa. Nó phù hợp nếu thông tin hữu ích chủ yếu gần query hoặc được truyền qua nhiều layer, không phù hợp nếu cần direct arbitrary retrieval.

### 2.3 DSA: learned token selection

DSA thêm lightweight indexer để score các token-level MLA entries, lấy token top-k rồi chạy MQA trên subset đó. Relevant token `database timeout` có thể được chọn dù ở xa; nếu chọn đúng, nó vẫn là một token slot riêng. Đổi lại, indexer vẫn phải nhìn history và selected positions có thể rải rác, gây indirect gather kém locality.[^dsa-concept]

```text
query → token indexer → [token 4, token 917, token 6201, ...]
      → gather các MLA entries rời rạc → sparse MQA → output
```

DSA giảm việc của **core attention**, không tự loại mọi quadratic work và không tự biến retained cache thành fixed-size.[^dsa-concept]

### 2.4 QSA / pooled block retrieval: chọn cụm rồi mở lại thành token

QSA mean-pool index keys theo block bốn token, score các blocks, chọn tối đa 512 complete blocks rồi mở chúng thành tối đa 2.048 raw tokens trước causal GQA; incomplete visible tail được giữ riêng trong reference implementation.[^qsa-concept]

```text
raw index keys
  → pool mỗi 4 token
  → rank block summaries
  → top blocks
  → expand thành raw token indices
  → gather token-level main K/V
  → causal GQA
```

Nếu block chứa `database timeout`, cả các token láng giềng cũng được đọc. Điều này tăng contiguous access và giảm candidate count, nhưng tiêu budget cho false positives trong block. Quan trọng: pooling ở đây phục vụ **selection**; main K/V vẫn là per-token state.[^qsa-concept]

### 2.5 LSA: fixed regions + cross-layer reuse + coarse-to-fine retrieval

LSA giữ token-level MLA entries nhưng tổ chức lại đường retrieval:

1. Luôn đọc một `sink` region ở đầu và local sliding window.
2. Dùng dynamic selection cho phần distant budget còn lại.
3. Một owner layer chạy indexer; layer kế tiếp trong group tái dùng indices đã được distill cho cả group.
4. Ở context rất dài, rank pages trước rồi token-score chỉ trong recalled pages.[^lsa-concept]

Trong cấu hình được báo cáo với budget 2.048, ví dụ phân bổ là 16 sink, 1.024 local và 1.008 dynamic distant positions. Cross-layer group mặc định bằng hai giảm số lần lập index; hierarchical indexing giảm candidate search nhưng có thể bỏ relevant page ngay từ coarse stage.[^lsa-concept]

Trong ví dụ, sink bảo vệ system instruction, local window giữ triệu chứng mới, dynamic branch lấy `database timeout`. Reuse giúp layer sau không lập lại mục lục, nhưng selection của owner có thể không tối ưu cho mọi layer.

### 2.6 CSA/HCA: thay cả entries được lưu và đọc

CSA/HCA không chỉ coarsen selection. Chúng tạo learned compressed entries từ groups token ở remote history và giữ local uncompressed window.[^csa-hca-concept]

- `CSA`: mức nén vừa phải; indexer chọn top-k compressed entries.
- `HCA`: nén rất mạnh; vì số entries đã ít hơn nên đọc dense trên chúng.
- Cả hai: local window giữ token detail gần query; incomplete tail cần state riêng cho tới khi đủ block.[^csa-hca-concept]

Trong ví dụ, root-cause region ở xa có thể chỉ còn một learned summary. Query có thể tìm đúng summary nhưng không còn guaranteed direct access tới từng token gốc bên trong. Đây là thay đổi về **representation và addressability**, không chỉ read set.

> [!note] Kiểm tra data flow
> Hỏi theo thứ tự: `index cái gì → select đơn vị gì → gather representation gì → cache giữ gì`. Nếu chỉ biết top-k mà chưa biết bốn câu này, ta chưa hiểu architecture.

## 3. Tác động

### 3.1 Hệ quả trực tiếp của thiết kế

| Thiết kế | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
|---|---|---|---|
| Fixed local/block | không learned indexer; regular reads | distant blind spot | dependency chủ yếu local hoặc được relay qua depth |
| DSA token top-k | fine-grained distant retrieval; core đọc ít token | history-scanning indexer; scattered gather | indexer recall cao và sparse kernel trả được overhead |
| Pooled block top-k | ít candidates hơn; reads contiguous hơn | block false positives/negatives | relevant evidence có locality theo block |
| Cross-layer reuse | ít index passes theo depth | owner indices có thể lệch nhu cầu reuse layer | layers trong group có retrieval tương thích và distillation tốt |
| Hierarchical index | giảm fine scoring trên full history | coarse miss không phục hồi được | context đủ dài để two-stage search trả overhead |
| CSA/HCA | ít remote entries được lưu/đọc | lossy remote identity; compression work | workload chấp nhận aggregate remote memory và cần local exact detail |

### 3.2 Behavior và quality

Learned selection có thể tìm distant evidence mà fixed local mask không thấy, nhưng thêm failure mode `selection miss`. Block/page retrieval thêm `coarse miss`; compression thêm `representation loss`. Vì vậy context window lớn không đảm bảo selected-token recall hoặc answer quality lớn.

### 3.3 Memory, compute và latency

- **Compute:** sparse core attention làm ít query–entry interactions; indexer, pooling, top-k và gather vẫn tốn việc.
- **Memory:** DSA, QSA và LSA có thể vẫn giữ entry cho mọi token. CSA/HCA mới thay remote entry count bằng compressed groups.[^sparse-evolution][^csa-hca-concept]
- **Latency:** regular local/block reads dễ coalesce hơn random token gathers. Nhưng latency cuối phụ thuộc kernel, dtype, batch, context, cache layout và hardware.
- **Scaling:** top-k cố định làm core budget tăng chậm hơn full prefix, nhưng flat token indexer vẫn có thể trở thành bottleneck; reuse/hierarchy nhắm trực tiếp vào phần đó.[^lsa-concept]

### 3.4 Direct consequence khác benchmark result

LSA report đo speedup và quality gần các baseline trong các setup cụ thể; đó không phải hệ quả đại số của locality hay reuse. QSA report cũng công bố kernel speedups ở long context, nhưng reference Python path không chứng minh production latency. CSA/HCA chưa có public controlled ablation cô lập từng compression/index/local-window choice trong concept nguồn.[^qsa-concept][^lsa-evidence][^csa-hca-concept]

## 4. Sự khác biệt

### 4.1 So với baseline và cơ chế gần nhất

| Cơ chế | Giống nhau | Khác nhau trong data flow | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| Dense full | đều dùng Q/K/V và causal softmax | không selection; đọc mọi prior token | retrieval đầy đủ, work/read lớn | context vừa hoặc exact arbitrary retrieval quan trọng |
| Local/block mask | vẫn giữ token K/V và causal attention | mask cố định trước content scoring | regular, rẻ; blind spot | streaming/local workloads |
| DSA | vẫn token-addressable MLA entries | learned token indexer trước core MQA | fine retrieval; scattered reads/index cost | distant evidence rời rạc, có sparse kernel |
| QSA | vẫn core attention trên raw token K/V | pool → rank blocks → expand tokens → GQA | locality tốt hơn; coarse selection | evidence có cluster locality |
| LSA | vẫn token-level DSA/MLA family | fixed sink/window + dynamic branch + reuse + hierarchy | ít repeated work; reuse/coarse miss | very-long-context serving có kernel co-design |
| CSA | vẫn index rồi sparse core attention | remote raw tokens → moderately compressed entries | cache/read nhỏ hơn; remote identity lossy | cần cân bằng compression và selective retrieval |
| HCA | vẫn local raw window | remote raw tokens → heavily compressed entries → dense read | ít index complexity hơn; coarse remote memory | remote summary đủ, local detail quan trọng |

### 4.2 Phần nào giữ nguyên?

Causal ordering, query projection, softmax semantics trên **read set**, output projection, residual path và FFN có thể giữ nguyên. Thay đổi chính nằm giữa query creation và core attention: mask/index, selected indices, gather và đôi khi retained KV representation. Sparse attention không đồng nghĩa với MQA/GQA/MLA; các KV layouts đó có thể là core bên dưới access pattern.[^sparse-evolution]

### 4.3 Khái niệm dễ nhầm

- `Sparse read` không bằng `cache eviction`: entry không được đọc ở query này vẫn có thể còn cho query sau.
- `Block selection` không bằng `block compression`: QSA mở block về raw tokens; CSA/HCA đọc learned aggregate entries.
- `Pooling` không luôn có cùng vai trò: có thể tạo index summary hoặc tạo representation thật được cache.
- `Top-k core` không có nghĩa toàn layer là linear-time: phải tính cả indexer.
- `Locality` có hai nghĩa: model ưu tiên nearby positions và hardware đọc contiguous addresses; hai ý liên quan nhưng không đồng nhất.
- `Individually addressable` nghĩa một remote token còn slot riêng để score/gather; không có nghĩa selector chắc chắn chọn nó.

## 5. Trong thực tế

### 5.1 Cơ chế nằm ở đâu trong model/system?

```text
Decoder layer
  normalization
      │
  Q/K/V + index projections
      │
  index/mask planner ──► selected logical positions
      │                         │
  KV cache manager ─────► logical-to-physical gather
      │                         │
  sparse attention kernel ◄────┘
      │
  output projection → residual → MLP
```

Model định nghĩa score, grouping và training objective; runtime phải hiện thực top-k, index reuse, paged/cache addressing và kernel. Một semantic reference tạo dense mask có thể đúng output nhưng không cho sparse speedup.

### 5.2 Khi nào nên dùng?

**Nên cân nhắc khi:** context rất dài; mỗi query chỉ cần ít distant evidence; target runtime có sparse gather/top-k kernel; hoặc cache compression đáng đổi lấy remote granularity.

**Không nên mặc định khi:** context ngắn; workload cần exact copy/citation từ vị trí bất kỳ; relevant tokens phân tán khiến block budget lãng phí; indexer recall chưa được đo; runtime chỉ materialize dense mask; hoặc model/checkpoint chưa được train cho sparse path.

### 5.3 Walkthrough: agent đọc log một triệu token

1. **Prefill:** system giữ token/index K/V hoặc tạo compressed entries tùy architecture.
2. **Query cuối:** local branch lấy log mới; sink lấy instruction; learned branch tìm root-cause region.
3. **Selection:** DSA lấy individual tokens; QSA lấy block chứa chúng; LSA có thể page-recall trước và tái dùng index ở layer kế.
4. **Core attention:** chỉ selected set đi vào expensive attention.
5. **Answer:** model sinh “database timeout”, nhưng đúng cơ chế không chứng minh factual correctness; cần evaluation có distractors, late relevance và exact citation.

### 5.4 Measurement phải ghi lại

| Sổ cái | Metric tối thiểu | Không được suy ra |
|---|---|---|
| Selection | candidate scores, top-k, selected-token recall, block/page recall | recall cao trên toy không đảm bảo downstream quality |
| Locality | contiguous runs, adjacency ratio, bytes/transactions nếu profiler có | indices gần nhau không đảm bảo kernel nhanh |
| State | retained entries, bytes theo layer/dtype, tail/window, host/offload state | read budget nhỏ không chứng minh cache nhỏ |
| Compute | indexer, pooling/top-k, gather, core attention tách riêng | core FLOPs nhỏ không chứng minh end-to-end latency |
| Serving | prefill, decode, TTFT, TPOT, throughput theo batch/concurrency | operator speedup không bằng serving speedup |
| Quality | exact retrieval, multi-hop, distractors, long code, target task | theory không dự đoán benchmark score |

> [!note] Gate trước phần toán
> Đến đây, người mới phải trả lời được: sparse attention giải quyết read/compute trên history dài; nó chạy qua mask/index → selection → gather → core attention; lợi ích phụ thuộc selector và kernel; DSA/QSA/LSA khác nhau ở granularity/locality/reuse; CSA/HCA còn đổi retained representation; nên dùng khi workload dài và sparse retrieval đo được là phù hợp.

## 6. Toán học — zoom in sau cùng

### 6.1 Bảng ký hiệu

| Ký hiệu | Shape | Ý nghĩa |
|---|---:|---|
| `B` | scalar | batch size |
| `T` | scalar | sequence length |
| `H` | scalar | số attention heads trong toy |
| `d` | scalar | head width |
| `Q, K, V` | `(B, H, T, d)` | query, key, value theo token |
| `W` | scalar | local window width |
| `r` | scalar | block width |
| `K_b` | `(B, H, ceil(T/r), d)` | pooled block keys |
| `J_t` | tối đa `k` blocks | block indices được chọn cho query `t` |
| `A_t` | variable-length set | raw token indices core attention được đọc |
| `m` | scalar | compression group size |

### 6.2 Dense causal attention — baseline nhỏ nhất

**Trực giác.** Query ở vị trí hiện tại so sánh với mọi key không nằm trong tương lai, rồi lấy weighted sum của values.

$$
s_{t,j}=\frac{q_t k_j^{\top}}{\sqrt d}+M_{t,j},\qquad
a_{t,:}=\operatorname{softmax}(s_{t,:}),\qquad
o_t=\sum_{j=0}^{T-1}a_{t,j}v_j.
$$

**Ký hiệu.** `M` bằng zero cho prior/current positions và negative infinity cho future positions. **Shape flow:** một `q_t` có shape `(d)` nhân `K` shape `(T,d)` thành scores `(T)`, softmax vẫn `(T)`, rồi nhân `V` thành output `(d)`.

**Ví dụ số.** Với một chiều, query bằng một, ba prior keys là `[2, 0, 1]`, logits trước scaling là `[2, 0, 1]`; softmax ưu tiên token đầu nhưng cả ba vẫn có weight dương.

**Kết luận.** Dense baseline giữ mọi prior token trong candidate set; sparse designs thay set này hoặc representation nằm trong set.

### 6.3 Local mask

**Trực giác.** Chỉ cho query đọc `W` vị trí gần nhất, bao gồm chính nó.

$$
M^{\text{local}}_{t,j}=
\begin{cases}
0, & \max(0,t-W+1)\le j\le t,\\
-\infty, & \text{ngược lại}.
\end{cases}
$$

**Shape flow.** Mask vẫn là `(T,T)` trong reference dense implementation, nhưng optimized kernel chỉ cần xử lý khoảng `W` keys mỗi query. **Ví dụ số:** `t=7`, `W=3` cho read set `[5,6,7]`. **Kết luận:** work của core phụ thuộc window, nhưng distant token số zero không thể được đọc trực tiếp.

### 6.4 Pooled block top-k

**Trực giác.** Tạo một “đại diện mục lục” cho mỗi block, xếp hạng blocks bằng query, rồi mở selected blocks về raw tokens.

$$
\bar{k}_b=\frac{1}{r}\sum_{j=br}^{(b+1)r-1}k_j,
\qquad
u_{t,b}=\frac{q_t\bar{k}_b^{\top}}{\sqrt d},
\qquad
J_t=\operatorname{TopK}_b(u_{t,b},k).
$$

$$
A_t=\{j:\lfloor j/r\rfloor\in J_t,\ j\le t\}\ \cup\ \{j:\max(0,t-W+1)\le j\le t\}.
$$

**Ký hiệu.** `r` là block width, `k` là selected-block budget, `J_t` là blocks đã chọn, `A_t` là raw read set sau expand cộng local window. **Shape flow:** `K` `(B,H,T,d)` → pooled keys `(B,H,ceil(T/r),d)` → block scores `(B,H,blocks)` → token indices → gathered `K,V` `(B,H,|A_t|,d)` → output `(B,H,d)`.

**Ví dụ số.** Với tám tokens, block width hai, query cuối, selected blocks zero và hai, local window hai: expanded read set là `[0,1,4,5,6,7]`. Root-cause token zero còn addressable, nhưng token một đi kèm dù có thể không relevant.

**Kết luận.** Candidate count và gather locality tốt hơn token top-k, đổi lại selection granularity thô hơn.[^qsa-concept]

### 6.5 Work và retained-state ledger

**Trực giác.** Tách chi phí tìm kiếm khỏi chi phí đọc, rồi tách cả hai khỏi số entries được giữ.

$$
C_{\text{dense-core}}\propto T^2d,
\qquad
C_{\text{sparse-core}}\propto T\,|A_t|\,d,
\qquad
C_{\text{pooled-index}}\propto T\left\lceil\frac{T}{r}\right\rceil d_I.
$$

Với cache K/V thường:

$$
M_{KV}=2LBTH_{KV}d_hp.
$$

**Ký hiệu.** `d_I` là index width; `L` là layers; `p` là bytes mỗi element. **Shape flow:** sparse read không xóa sequence axis khỏi cached `(B,H_KV,T,d_h)` tensors. **Ví dụ số:** giảm read set từ toàn prefix xuống 2.048 tokens nhưng vẫn giữ mọi token làm `T` trong cache thì retained bytes không đổi. **Kết luận:** DSA/QSA/LSA có thể giảm core reads mà cache vẫn tăng tuyến tính theo context.[^dsa-concept][^qsa-concept][^lsa-concept]

### 6.6 Recall và locality metrics

**Trực giác.** Selector phải tìm đúng evidence, còn hardware muốn indices tạo thành contiguous runs.

$$
\operatorname{Recall}(A,R)=\frac{|A\cap R|}{|R|},
\qquad
\operatorname{Adjacency}(A)=
\frac{\sum_{i=1}^{|A|-1}\mathbf{1}[a_i=a_{i-1}+1]}{\max(1,|A|-1)},
$$

trong đó `A` đã sort và `R` là oracle relevant-token set.

**Shape/example.** Với selected `[0,1,4,5,6,7]` và relevant `[0,4]`, recall bằng một; bốn trong năm transitions là adjacent nên locality ratio bằng 0,8. **Kết luận:** hai metrics đo hai failure modes khác nhau; không metric nào thay cho end-to-end latency/quality.

### 6.7 Compressed entries và mất individual addressability

**Trực giác.** QSA chỉ dùng block summary để chọn rồi quay lại raw tokens; CSA/HCA dùng learned aggregate làm remote entry thật.

$$
c_b=\sum_{j\in G_b}\pi_{b,j}x_j,
\qquad
\sum_{j\in G_b}\pi_{b,j}=1.
$$

**Ký hiệu.** `G_b` là compression group; `c_b` là compressed entry. **Shape flow:** group raw entries `(m,d)` → một entry `(d_c)`; remote sequence có khoảng `T/m` entries thay vì `T`. **Ví dụ số:** 128 remote tokens thành một HCA entry thì query có thể score entry đó, không score riêng token thứ 37 bên trong. **Kết luận:** compression giảm retained/read entries nhưng làm remote identity lossy; local raw window giữ nearby token detail.[^csa-hca-concept]

## 7. Implementation — PyTorch tối thiểu

Code nối trực tiếp với luồng đã học: `local_causal_attention` là fixed mask; `block_topk_indices` pool/rank/expand và union local window; `sparse_block_attention` gather raw token K/V rồi softmax. Nó không implement learned projection, distillation, cross-layer reuse, hierarchical page search hay compressed entries.

Toy không dùng RoPE. Nếu thêm RoPE, dùng `interleaved` pairing `(0,1), (2,3), ...`; cached decode phải dùng absolute `position_ids` tiếp nối prefix, không reset về zero. Cache minh họa giữ shape `(B, H_KV, S, d_h)` cho K và V ở mỗi layer.

```python
import math
import torch
import torch.nn.functional as F


def dense_attention_with_mask(q, k, v, allowed):
    """q,k,v: (B,H,T,d); allowed: (T,T) bool."""
    logits = q @ k.transpose(-2, -1) / math.sqrt(q.size(-1))
    logits = logits.masked_fill(~allowed[None, None], float("-inf"))
    return F.softmax(logits, dim=-1) @ v


def local_causal_attention(q, k, v, window):
    T = q.size(-2)
    row = torch.arange(T, device=q.device)[:, None]
    col = torch.arange(T, device=q.device)[None, :]
    allowed = (col <= row) & (col >= row - window + 1)
    return dense_attention_with_mask(q, k, v, allowed)


def block_topk_indices(q, k, block_size=2, top_blocks=2, local_window=2):
    """Semantic reference for B=H=1. Only fully visible remote blocks compete."""
    assert q.shape[:2] == (1, 1) and k.shape[:2] == (1, 1)
    T, d = q.size(-2), q.size(-1)
    selected, candidate_counts = [], []

    for t in range(T):
        local_start = max(0, t - local_window + 1)
        local = set(range(local_start, t + 1))

        candidates, scores = [], []
        for start in range(0, T, block_size):
            end = min(start + block_size, T)
            # Fully visible and strictly before the local region.
            if end - 1 < local_start:
                pooled = k[0, 0, start:end].mean(dim=0)
                score = torch.dot(q[0, 0, t], pooled) / math.sqrt(d)
                candidates.append((start, end))
                scores.append(score)

        candidate_counts.append(len(scores))
        chosen = []
        if scores:
            score_tensor = torch.stack(scores)
            take = min(top_blocks, score_tensor.numel())
            for i in torch.topk(score_tensor, take).indices.tolist():
                chosen.extend(range(*candidates[i]))

        selected.append(sorted(local.union(chosen)))
    return selected, candidate_counts


def sparse_block_attention(q, k, v, **selector_kwargs):
    """Gather raw token slots; unlike compressed-entry attention."""
    selected, candidate_counts = block_topk_indices(q, k, **selector_kwargs)
    outputs = []
    for t, idx in enumerate(selected):
        index = torch.tensor(idx, device=q.device)
        k_sel = k[:, :, index, :]                 # (1,1,R,d)
        v_sel = v[:, :, index, :]                 # (1,1,R,d)
        logits = (q[:, :, t:t+1, :] @ k_sel.transpose(-2, -1))
        logits = logits / math.sqrt(q.size(-1))
        outputs.append(F.softmax(logits, dim=-1) @ v_sel)
    return torch.cat(outputs, dim=-2), selected, candidate_counts


def selected_token_recall(selected, relevant):
    relevant = set(relevant)
    return len(set(selected) & relevant) / max(1, len(relevant))


def gather_adjacency(selected):
    idx = sorted(selected)
    adjacent = sum(b == a + 1 for a, b in zip(idx, idx[1:]))
    return adjacent / max(1, len(idx) - 1)


# Example xuyên suốt: query cuối thích key-axis thứ nhất.
torch.manual_seed(0)
q = torch.zeros(1, 1, 8, 2)
q[..., 0] = 1.0
k = torch.tensor([[[[3., 0.], [3., 0.],
                    [0., 3.], [0., 3.],
                    [2., 0.], [2., 0.],
                    [0., 1.], [0., 1.]]]])
v = torch.randn(1, 1, 8, 2)

out, selected, candidate_counts = sparse_block_attention(
    q, k, v, block_size=2, top_blocks=2, local_window=2
)
last = selected[-1]  # [0,1,4,5,6,7]
metrics = {
    "indexer_candidate_scores_last_query": candidate_counts[-1],
    "selected_token_recall": selected_token_recall(last, relevant=[0, 4]),
    "gather_adjacency": gather_adjacency(last),
    "retained_cache_elements": k.numel() + v.numel(),
    "selected_read_elements": len(last) * (k.size(-1) + v.size(-1)),
    "remote_tokens_individually_addressable": all(i in last for i in [0, 4]),
}
print(last)
print(metrics)
```

Expected cuối query: ba candidate blocks được score, relevant recall bằng một, gather adjacency bằng 0,8, retained cache vẫn gồm toàn bộ K/V tensors, và remote tokens zero/bốn còn có slots riêng. `selected_read_elements` nhỏ hơn retained elements không có nghĩa cache đã bị evict.

## 8. Verification — xác minh trước benchmark

Các test dùng FP32 và tolerance tường minh. Chạy cùng definitions ở trên.

```python
@torch.no_grad()
def test_local_matches_explicit_mask():
    torch.manual_seed(1)
    q0 = torch.randn(1, 2, 6, 4)
    k0 = torch.randn(1, 2, 6, 4)
    v0 = torch.randn(1, 2, 6, 4)
    T, W = 6, 3
    row = torch.arange(T)[:, None]
    col = torch.arange(T)[None, :]
    allowed = (col <= row) & (col >= row - W + 1)
    expected = dense_attention_with_mask(q0, k0, v0, allowed)
    actual = local_causal_attention(q0, k0, v0, W)
    torch.testing.assert_close(actual, expected, rtol=1e-5, atol=1e-6)


@torch.no_grad()
def test_block_selector_and_metrics():
    _, selected, counts = sparse_block_attention(
        q, k, v, block_size=2, top_blocks=2, local_window=2
    )
    assert selected[-1] == [0, 1, 4, 5, 6, 7]
    assert counts[-1] == 3
    torch.testing.assert_close(
        torch.tensor(selected_token_recall(selected[-1], [0, 4])),
        torch.tensor(1.0), rtol=0.0, atol=0.0
    )
    torch.testing.assert_close(
        torch.tensor(gather_adjacency(selected[-1])),
        torch.tensor(0.8), rtol=0.0, atol=1e-7
    )


@torch.no_grad()
def test_sparse_output_matches_manual_gather():
    actual, selected, _ = sparse_block_attention(
        q, k, v, block_size=2, top_blocks=2, local_window=2
    )
    idx = torch.tensor(selected[-1])
    logits = q[:, :, -1:, :] @ k[:, :, idx, :].transpose(-2, -1)
    logits = logits / math.sqrt(q.size(-1))
    expected_last = F.softmax(logits, dim=-1) @ v[:, :, idx, :]
    torch.testing.assert_close(
        actual[:, :, -1:, :], expected_last, rtol=1e-5, atol=1e-6
    )


@torch.no_grad()
def test_future_perturbation_cannot_leak():
    torch.manual_seed(2)
    q0 = torch.randn(1, 1, 8, 4)
    k0 = torch.randn(1, 1, 8, 4)
    v0 = torch.randn(1, 1, 8, 4)
    before, _, _ = sparse_block_attention(
        q0, k0, v0, block_size=2, top_blocks=2, local_window=2
    )
    k1, v1 = k0.clone(), v0.clone()
    k1[:, :, 5:] = torch.randn_like(k1[:, :, 5:])
    v1[:, :, 5:] = torch.randn_like(v1[:, :, 5:])
    after, _, _ = sparse_block_attention(
        q0, k1, v1, block_size=2, top_blocks=2, local_window=2
    )
    torch.testing.assert_close(
        before[:, :, :5], after[:, :, :5], rtol=1e-5, atol=1e-6
    )


@torch.no_grad()
def test_sparse_reads_do_not_imply_smaller_cache():
    _, selected, _ = sparse_block_attention(
        q, k, v, block_size=2, top_blocks=2, local_window=2
    )
    retained = k.numel() + v.numel()
    read_last = len(selected[-1]) * (k.size(-1) + v.size(-1))
    assert retained == 32
    assert read_last == 24
    assert read_last < retained
    torch.testing.assert_close(
        k[:, :, 0, :], torch.tensor([[[3.0, 0.0]]]), rtol=0.0, atol=0.0
    )


test_local_matches_explicit_mask()
test_block_selector_and_metrics()
test_sparse_output_matches_manual_gather()
test_future_perturbation_cannot_leak()
test_sparse_reads_do_not_imply_smaller_cache()
print("all sparse-attention toy tests passed")
```

Test suite chứng minh semantic properties của toy, không chứng minh selector được train tốt, compressed entries bảo toàn thông tin, hoặc kernel nhanh.

## 9. Benchmark / Trade-offs

### 9.1 Evidence ledger

| Claim | Loại evidence | Phạm vi đúng | Không được kết luận |
|---|---|---|---|
| DSA core attention chuyển từ full pairwise sang top-k-scaled work | mechanism/report | core attention; indexer vẫn còn | toàn layer hết quadratic work hoặc cache fixed-size |
| QSA report tới 7,6 lần prefill và 4,9 lần decode ở một triệu tokens | author-run attention-module benchmark | disclosed long-context kernel workloads | end-to-end speedup phổ quát |
| LSA report 1,42–3,60 lần prefill và 1,25–1,40 lần decode so với DSA | author-run end-to-end comparison | reported 4K–1.024K setups | portable gain trên hardware/kernel khác |
| LSA giữ KV entry cho mọi token | architecture/state fact | aggregate retained cache | cache compression |
| CSA/HCA giảm remote entry count | mechanism/report | learned compressed representation + local/tail state | lossless remote token retrieval |

Các số QSA/LSA là author-reported và không tạo một bảng xếp hạng chéo vì baseline, model, workload, kernel và hardware không matched.[^qsa-concept][^lsa-evidence]

### 9.2 Benchmark protocol nên dùng

1. Ghi model/checkpoint, sparse training stage và selector budget.
2. Đo riêng indexer, top-k, gather và core attention.
3. Tách prompt `prefill` khỏi one-token/batched `decode`.
4. Report batch, concurrency, context, dtype, device, backend, page/block size.
5. Ghi retained cache bytes, device-resident bytes và offloaded bytes riêng.
6. Đo selected-token/block/page recall trên oracle task trước downstream score.
7. So sánh với dense/local baseline có cùng model dimensions và training data nếu muốn gán causal effect.

## 10. Debug checklist

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên |
|---|---|---|
| Future token đổi output cũ | candidate pooling hoặc mask nhìn future | test perturb future; inspect block end condition |
| Recall thấp dù top-k lớn | index score sai, coarse block miss, relevant labels sai | print ranked blocks và oracle positions |
| Reads sparse nhưng memory không giảm | cache vẫn giữ per-token K/V | inspect cache shape và retained entries |
| Sparse path chậm hơn dense | Python/dense mask, top-k/gather overhead, context ngắn | profiler theo index/gather/core; xác nhận sparse kernel |
| QSA block count vượt dự kiến | incomplete visible tail được append | log complete blocks và tail riêng |
| Reuse layer quality giảm | owner selection không hợp reuse layer | đo recall theo từng layer/group size |
| HI nhanh nhưng quality giảm | relevant page bị coarse stage loại | page recall trước token recall |
| CSA/HCA không copy chính xác remote span | token identity đã aggregate | so với local window và group-level retrieval |
| Cached decode lệch full pass | sai absolute position hoặc cache offsets | log absolute `position_ids`; kiểm tra interleaved RoPE pairing |
| NaN ở softmax | query không có allowed key | luôn include self/local token; inspect all-negative-infinity rows |

## 11. Giới hạn & bước tiếp theo

Toy selector dùng mean-pooling cố định, một batch/head, Python loops và raw-token gather. Nó không học indexer, không distill attention distribution, không reuse indices qua layer, không có page hierarchy, không tạo compressed entries, không benchmark GPU và không implement production cache retention. `retained_cache_elements` chỉ là raw tensor accounting.

Bước tiếp theo:

1. Thay mean score bằng learned multi-head indexer và train trên synthetic retrieval.
2. Thêm page → token hierarchy; đo page recall rồi token recall.
3. Tái dùng owner indices cho hai layers có query projections khác nhau; đo mismatch.
4. Tạo lossy compressed entries và so exact-copy quality với block selection.
5. Học [Programmable attention execution](flexattention-programming-model-and-compilation.md) để tách semantic mask khỏi block skipping/kernel generation.
6. Dùng [Sparse Attention evolution](sparse-attention-evolution-and-architecture-comparison.md) và [Workload-conditioned selection](workload-conditioned-frontier-llm-architecture-selection.md) để đặt design vào model/system lớn hơn.

## Relationships

- **Depends on:** [Attention design matrix — khóa học cho người mới](attention-design-matrix-beginners-course.md) — tách access pattern khỏi KV representation và positional mechanism.
- **Uses:** [DeepSeek Sparse Attention](deepseek-sparse-attention.md), [Qwen Sparse Attention](qwen-sparse-attention.md), [LongCat Sparse Attention](longcat-sparse-attention.md), và [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) — các mốc cơ chế chính.
- **Distinguishes:** [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md) — sparse reads, cache retention và lossy aggregation là các quyết định khác nhau.
- **Elaborates:** Stage 6.2 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) — từ fixed masks đến learned/locality-aware/compressed retrieval.
- **Prepares for:** [Sparse Attention evolution and architecture comparison](sparse-attention-evolution-and-architecture-comparison.md) và Stage 9.6 long-context archetypes.

## Evidence limits

Đây là pedagogical synthesis từ các concept wiki đã duy trì. DSA và QSA mechanism/training/evaluation dựa trên author reports và reference implementations; LSA mechanism và speed/quality evidence đến từ một author technical report không có released kernels/config đủ để independent reproduction; CSA/HCA dựa trên DeepSeek-V4 report và concept vẫn ở trạng thái `draft`. Không có matched, independent benchmark chung cho toàn bộ family. Công thức complexity bỏ qua projection, top-k, metadata, padding, communication và kernel effects; PyTorch lab chỉ attests toy semantics. Mọi claim về target latency, memory peak, quality và scalability phải được đo lại trên checkpoint, dtype, hardware, backend và workload đích.[^dsa-concept][^qsa-concept][^lsa-evidence][^csa-hca-concept]

[^sparse-evolution]: [Sparse Attention evolution and architecture comparison](sparse-attention-evolution-and-architecture-comparison.md), synthesis of fixed patterns, DSA, pooled retrieval, LSA, CSA/HCA and hybrid branches; status `draft`.
[^dsa-concept]: [DeepSeek Sparse Attention](deepseek-sparse-attention.md), mechanism and evidence boundaries grounded primarily in DeepSeek-V3.2 Sections 2.1–2.3.
[^qsa-concept]: [Qwen Sparse Attention](qwen-sparse-attention.md), mechanism, training and author-run results grounded in the Qwen3.8-Flash-Next report and reference artifacts.
[^lsa-concept]: [LongCat Sparse Attention](longcat-sparse-attention.md), streaming-aware selection, cross-layer indexing and hierarchical indexing from the LongCat report.
[^csa-hca-concept]: [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md), DeepSeek-V4 CSA/HCA mechanism and deployment boundary; status `draft`.
[^lsa-evidence]: [LongCat Sparse Attention systems trade-offs and evidence](longcat-sparse-attention-systems-trade-offs-and-evidence.md), author-run latency and quality measurements with reproducibility limits.
[^kv-cache-tradeoffs]: [KV-cache compression and trade-offs](kv-cache-compression-and-trade-offs.md), taxonomy separating retention, lower precision and lossy aggregation; status `draft`.
