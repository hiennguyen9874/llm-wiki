---
type: Synthesis
title: "Workload-conditioned architecture selection: từ requirement ledger đến matched ablation — khóa học cho người mới"
description: A top-down beginner course for selecting recurrent-plus-periodic attention, token-addressable sparse attention, or compressed-entry attention from workload constraints and validating the choice with matched ablations.
tags: [architecture-selection, long-context, hybrid-attention, sparse-attention, mixture-of-experts, ablation, serving, learning-roadmap, pytorch]
status: stable
created: 2026-09-02
generated:
  by: llm-wiki-agent/1
  at: 2026-09-02T15:06:21+07:00
sources:
  - id: selection
    resource: workload-conditioned-frontier-llm-architecture-selection.md
    title: Workload-conditioned frontier LLM architecture selection
  - id: archetypes
    resource: long-context-architecture-archetypes-beginners-course.md
    title: Long-context architecture archetypes
  - id: evidence
    resource: comparative-reading-evidence-discipline-beginners-course.md
    title: Comparative reading and evidence discipline
  - id: recurrent
    resource: recurrent-majority-frontier-models-beginners-course.md
    title: Recurrent-majority frontier models
  - id: v4-k3
    resource: deepseek-v4-and-kimi-k3-architecture-comparison.md
    title: DeepSeek-V4 and Kimi K3 architecture comparison
  - id: glm-k3
    resource: glm-5-and-kimi-k3-architecture-comparison.md
    title: GLM-5 and Kimi K3 architecture comparison
  - id: compressed
    resource: compressed-sparse-and-heavily-compressed-attention.md
    title: Compressed sparse and heavily compressed attention
  - id: k3
    resource: kimi-k3-hybrid-retrieval-architecture.md
    title: Kimi K3 hybrid retrieval architecture
  - id: qwen-next
    resource: qwen3-8-flash-next-architecture-and-implementation.md
    title: Qwen3.8-Flash-Next architecture and implementation
  - id: delta-ssm
    resource: delta-rule-vs-ssm-frontier-adoption.md
    title: Delta-rule versus SSM frontier adoption
  - id: moe
    resource: mixture-of-experts-training-and-systems-trade-offs.md
    title: Mixture-of-Experts training and systems trade-offs
  - id: lifecycle
    resource: llm-inference-lifecycle-training-prefill-decode-and-latency.md
    title: LLM inference lifecycle
---

# Workload-conditioned architecture selection: từ requirement ledger đến matched ablation — khóa học cho người mới

Chọn kiến trúc long-context không phải là chọn model có benchmark cao nhất, mà là biến workload thành các requirement có thể đo, chọn **memory semantics** phù hợp, rồi kiểm tra lựa chọn bằng `matched ablation`. Bài này so ba nhánh: **recurrent-plus-periodic attention** giữ state cố định ở phần lớn layer và khôi phục token retrieval theo chu kỳ; **token-addressable sparse attention** giữ slot của từng token nhưng chỉ đọc một subset; **compressed-entry attention** thay nhóm token cũ bằng entry nén. Khuyến nghị mặc định cho general-purpose workload là recurrent-plus-periodic attention, nhưng đó là synthesis có điều kiện, không phải universal winner.[^selection][^archetypes][^evidence]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Chuyển một workload thật thành `requirement ledger` gồm quality, state, compute, latency, scale và evidence constraints.
> 2. Giải thích data flow và failure mode của ba kiến trúc bằng cùng một remote-fact scenario.
> 3. Chọn một nhánh có điều kiện, nêu rõ khi nào quyết định phải đảo chiều.
> 4. Thiết kế `matched ablation` cho `mixer ratio`, retrieval, MoE routing, residual design và context curriculum.
> 5. Chạy PyTorch toy và kiểm tra addressability, compression loss, fixed-state growth, periodic recovery và tính matched của ablation bằng `torch.testing.assert_close`.
> 6. Đo riêng `TTFT`, decode latency/`TPOT`, memory và long-context recall thay vì suy chúng từ architecture name.

## 1. Điều cần biết trước

- [Long-context architecture archetypes](long-context-architecture-archetypes-beginners-course.md): phân biệt token slots, compressed entries và recurrent state.
- [Recurrent-majority frontier models](recurrent-majority-frontier-models-beginners-course.md): đọc `mixer schedule`, periodic attention và state/cache ledger.
- [Comparative reading và evidence discipline](comparative-reading-evidence-discipline-beginners-course.md): phân biệt mechanism, empirical và causal claim.
- [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md): `prefill`, `decode`, `TTFT`, `TPOT` và end-to-end latency.
- [Mixture-of-Experts trade-offs](mixture-of-experts-training-and-systems-trade-offs.md): active FLOPs không đồng nghĩa total-weight memory hay latency.

Bài không chọn checkpoint production cụ thể, không thiết kế kernel CUDA/Triton và không tuyên bố model nào thắng quality. PyTorch code là semantic toy; `torch.cat` và Python loops dùng để nhìn rõ state, không phải serving implementation.

## 2. Bức tranh toàn cảnh

### 2.1 Vấn đề: một architecture không tối ưu đồng thời mọi workload

Một long-context model phải đánh đổi ít nhất bốn thứ:

1. **Có giữ địa chỉ riêng cho mỗi token cũ không?**
2. **State per request tăng nhanh thế nào khi context dài?**
3. **Query phải scan/gather bao nhiêu history?**
4. **Thông tin mất vì selector trượt, vì nén, hay vì recurrent interference?**

Ba nhánh kiến trúc trả lời khác nhau. Token-addressable sparse attention ưu tiên exact retrieval nhưng vẫn giữ cache theo token. Compressed-entry attention ưu tiên giảm số entry nhưng hy sinh token identity ngoài local window. Recurrent-plus-periodic attention ưu tiên bounded state ở đa số layer, đổi lại recurrent interference và vẫn cần periodic attention layers có cache tăng theo token.[^archetypes][^v4-k3][^glm-k3]

### 2.2 Ý tưởng cốt lõi trong một câu

**Chọn representation của history theo failure mode mà workload chịu được; sau đó dùng matched ablation để kiểm tra quality–latency–memory frontier trên chính workload đó.**

### 2.3 Mental model: ba cách tổ chức hồ sơ bệnh án

```text
A. Token-addressable sparse attention
   Giữ từng trang hồ sơ → indexer chọn vài trang để bác sĩ đọc.
   Sai khi: indexer bỏ sót đúng trang.

B. Compressed-entry attention
   Hồ sơ cũ được tóm tắt theo tập → đọc summary + vài trang gần nhất.
   Sai khi: chi tiết cần tìm đã biến mất trong summary.

C. Recurrent + periodic attention
   Đa số phòng chỉ mang một bảng trạng thái cố định;
   cứ vài phòng có một kho hồ sơ đầy đủ theo token.
   Sai khi: bảng bị interference trước khi tới kho truy hồi kế tiếp.
```

Không có cách nào miễn phí. A trả memory/indexer cost; B trả representation loss; C trả interference và periodic-cache cost.

### 2.4 Requirement ledger đứng trước architecture diagram

Đừng bắt đầu bằng “dùng KDA hay DSA?”. Hãy bắt đầu bằng ledger:

| Requirement | Câu hỏi vận hành | Metric / gate ví dụ | Nếu requirement này cứng |
|---|---|---|---|
| Exact remote copy | Có phải quote identifier, số, citation nguyên văn? | exact match, recall theo vị trí | nghiêng về token-addressable sparse |
| Semantic accumulation | Cần duy trì gist hơn là copy từng token? | task score với distractor | recurrent có thể phù hợp |
| Context cực dài | Prompt p50/p95 dài bao nhiêu? | token distribution, max useful length | cân nhắc recurrent hoặc compression |
| Per-request memory | Bao nhiêu concurrent requests phải resident? | bytes/request tại p95 context | recurrent/compressed được ưu tiên |
| Cold `TTFT` | User chờ prompt mới bao lâu? | p50/p95 cold TTFT | đo indexer/compression/chunk kernel |
| Decode cadence | Stream có SLA nào? | p50/p95 `TPOT` | recurrent thường đáng thử, không tự thắng |
| Prefix reuse | Bao nhiêu request chia sẻ prefix? | hit rate, warm TTFT | cache policy có thể đổi ranking |
| Hardware/runtime | Có sparse gather và recurrent kernels tốt không? | profiler + utilization | thiếu kernel thì dùng baseline đơn giản |
| MoE topology | Network chịu all-to-all tới đâu? | all-to-all time/bytes, rank load | top-k/expert count phải theo topology |
| Evidence bar | Quyết định research hay production? | seeds, CI, independent run | claim strength phải tương ứng |

Các threshold trong ledger là do project đặt; architecture report không đặt SLA thay cho bạn.

### 2.5 Sau bài này người đọc phải quyết định được gì?

Bạn sẽ không nhận một ranking cố định. Bạn sẽ có một procedure:

```text
workload trace
  → requirement ledger
  → shortlist memory semantics
  → smallest viable baseline
  → matched ablation matrix
  → quality + lifecycle + memory measurements
  → Pareto frontier
  → decision có điều kiện + rollback gate
```

## 3. Cách hoạt động — nhìn từ đầu đến cuối

### 3.1 Ví dụ xuyên suốt: coding agent với repository 500K token

Repository có dòng `retry_limit = 7` ở token 80K. Agent phải đọc toàn repo, sửa function gần cuối và copy đúng số `7`. Mỗi request tạo patch 1K token; nhiều request có thể chia sẻ cùng repository prefix.

Ta trace cùng fact qua ba pha:

```text
INPUT
  repository tokens + instruction cuối

PREFILL
  ghi history theo memory representation của từng layer

DECODE
  query mới tìm/đọc history, tạo patch token từng bước

OUTPUT
  patch phải giữ đúng retry_limit = 7
```

### 3.2 Nhánh A — token-addressable sparse attention

```text
mỗi token → latent/KV slot riêng → cache
query cuối → indexer scan prefix/block index
           → top-k token/block IDs
           → gather K/V gốc
           → causal attention → output
```

- **Representation:** token chứa `7` vẫn có slot riêng.
- **Selection:** indexer phải đưa slot/block đó vào budget.
- **Read:** main attention đọc K/V gốc của selected token; pooling của một số selector chỉ dùng để chọn, không nhất thiết nén main values.
- **Output:** exact copy khả thi nếu selection hit.
- **Failure mode:** `selection miss`.

GLM-5 là ví dụ attention-centric MLA/DSA: token-addressable state được giữ xuyên backbone, DSA giảm tập được đọc chứ không biến cache thành fixed state.[^glm-k3] Qwen Sparse Attention cũng tách pooled index keys khỏi main token K/V.[^qwen-next]

### 3.3 Nhánh B — compressed-entry attention

```text
remote token groups → learned compressed entries → cache ít entry hơn
local window        → raw token entries
query cuối → CSA: select top-k compressed entries
           → HCA: dense read trên các entry đã nén mạnh
           → đọc thêm local raw window → output
```

- **Representation:** token `7` ở xa không còn slot riêng; nó là một phần của group entry.
- **Selection:** CSA còn indexer; HCA có thể dense-read vì số entry đã giảm mạnh.
- **Read:** query đọc summary vector, không đọc lại value nguyên bản của token.
- **Output:** semantic clue có thể còn, exact quote không được bảo đảm bởi cơ chế.
- **Failure mode:** `representation loss`, kể cả selector chọn đúng group.

DeepSeek-V4 report mô tả CSA group khoảng 4 token, HCA group 128 token và local window 128 token; các cấu hình và lợi ích được báo cáo là author-run, còn concept liên quan hiện ở trạng thái `draft` và thiếu public controlled ablation cô lập từng thành phần.[^compressed][^v4-k3]

### 3.4 Nhánh C — recurrent-plus-periodic attention

```text
R layer: token → key/value/write gates → fixed recurrent state → output
R layer: token → update cùng state shape
R layer: token → update cùng state shape
A layer: token → append per-token latent/KV → global/sparse retrieval
lặp lại theo depth
```

- **Representation:** recurrent layers gộp history vào state ma trận cố định; periodic attention giữ token slots ở một phần depth.
- **Selection/read:** recurrent query đọc state trực tiếp; periodic attention đọc global hoặc sparse-selected token cache.
- **Output:** gist/association đi qua recurrent path; exact token có đường phục hồi ở periodic layer.
- **Failure mode:** `interference` trong recurrent state, cộng selection miss nếu periodic layer là sparse.

Kimi K3 dùng 69 KDA và 24 MLA layers; Qwen3.8-Flash-Next dùng 36 Gated DeltaNet và 12 QSA layers. Cả hai gần pattern `R R R A`, nhưng khác recurrent rule, periodic core, residual, MoE và cache representation; cùng ratio không đồng nghĩa cùng latency hay quality.[^k3][^qwen-next][^recurrent]

### 3.5 Vai trò của các trục ngoài retrieval

Một architecture decision đầy đủ không dừng ở mixer:

```text
embedding
  → sequence mixer (A/B/C)
  → residual read/write topology
  → dense FFN hoặc MoE router → dispatch → experts → combine
  → lặp theo depth
  → LM head
```

- **MoE routing** đổi channel capacity và distributed traffic, không đổi remote-token addressability.
- **Residual design** đổi information flow theo depth, không thay KV/recurrent memory semantics.
- **Context curriculum** quyết định model đã được train để dùng length nào, không phải một inference component.
- **Serving runtime** quyết định paging, prefix reuse, batching và kernel; architecture equation không quyết định toàn bộ TTFT/TPOT.[^moe][^lifecycle]

## 4. Tác động

### 4.1 Hệ quả trực tiếp từ thiết kế

| Chiều | Token-addressable sparse | Compressed-entry | Recurrent + periodic |
|---|---|---|---|
| Remote token còn slot riêng? | có | không ngoài raw window | không ở R; có ở A |
| State theo context | tăng theo token ở attention layers | tăng theo số group + window | R fixed; A tăng theo token |
| Main read | top-k token/block | top-k entry hoặc dense trên ít entry | fixed state ở R; global/sparse ở A |
| Chi phí tìm | indexer scan | CSA có indexer; HCA có thể không | R không index; A tùy core |
| Failure mode trực tiếp | selection miss | representation loss | interference; thêm selection miss nếu A sparse |

Đây là mechanism implications, không phải benchmark ranking.[^archetypes]

### 4.2 Lợi ích, chi phí và điều kiện để lợi ích xuất hiện

#### Token-addressable sparse

- **Lợi ích:** exact token value còn tồn tại; main attention đọc ít token hơn dense baseline.
- **Chi phí:** cache vẫn tăng, indexer phải scan, gather có thể rời rạc.
- **Điều kiện:** selector recall cao tại budget mục tiêu; kernel sparse/gather đủ tốt; workload thật sự cần exact remote detail.

#### Compressed-entry

- **Lợi ích:** ít retained entries và ít remote read hơn; phù hợp khi memory/IO là bottleneck.
- **Chi phí:** token identity bị mất trong group; compression/tail/window làm implementation phức tạp.
- **Điều kiện:** workload chấp nhận remote summary; local window bao phủ chi tiết cần exact; quality giữ được dưới compression ratio mục tiêu.[^compressed]

#### Recurrent + periodic

- **Lợi ích:** đa số layer không append state theo token; one-token decode ở recurrent layer chỉ update state nhỏ.
- **Chi phí:** interference; periodic cache vẫn tăng; chunkwise/recurrent kernel và mixed cache API phức tạp.
- **Điều kiện:** workload trộn semantic accumulation với periodic exact retrieval; periodic density đủ; runtime tối ưu cả recurrent và attention paths.[^k3][^recurrent]

### 4.3 Tác động lên behavior và quality

Cùng lỗi `retry_limit`:

- A có thể trả `9` vì selector không chọn block chứa `7` dù slot vẫn tồn tại.
- B có thể nhớ “retry limit nhỏ” nhưng không giữ chính xác `7` vì group compression.
- C có thể trộn association `retry_limit→7` với một key tương tự, rồi được periodic attention sửa lại nếu layer đó đọc đúng slot.

Do đó long-context quality cần tách ít nhất:

1. `selection recall`: fact có vào read set không?
2. `representation fidelity`: read set có còn value nguyên bản không?
3. `answer accuracy`: model có dùng evidence đúng không?
4. `position robustness`: kết quả đổi thế nào khi fact di chuyển?

### 4.4 Memory, compute và latency

- Sparse main attention giảm selected read nhưng không tự xóa retained cache hay index scan.
- Compression giảm số entry, nhưng compression kernel, local state và tail entries vẫn tốn work.
- Recurrent state giảm context-growing state ở R layers, nhưng toàn model vẫn có periodic cache và MoE/residual overhead.
- `TTFT` chịu prefill, queueing, tokenizer, prefix hit và network; `TPOT` chịu decode kernel, cache length, batching và memory bandwidth. Không được đổi FLOPs estimate thành end-to-end latency claim.[^lifecycle]

### 4.5 Direct implication khác benchmark result

| Claim | Loại | Cách viết đúng |
|---|---|---|
| KDA state shape không tăng theo token | mechanism | suy trực tiếp từ recurrence/state shape |
| DSA giữ token slots nhưng đọc top-k | mechanism | specification/code path |
| CSA/HCA mất token identity trong group | mechanism | suy từ group aggregation |
| Qwen hybrid average cao hơn full attention trong matched smaller-scale report | empirical ablation | “trong setup author-run đó”[^qwen-next] |
| Kimi K3 overall scaling efficiency đến từ KDA | unsupported causal leap | report thay đổi architecture, data và recipe cùng lúc[^k3] |
| V4 nhanh hơn K3 cho mọi workload | unsupported | không có matched head-to-head[^v4-k3] |

## 5. Sự khác biệt

### 5.1 Bảng so baseline và ba lựa chọn

| Thiết kế | Giống dense baseline | Thay đổi ở data flow | Trade-off | Khi phù hợp |
|---|---|---|---|---|
| Dense attention | causal token slots, softmax, residual/FFN | không selector/compression/recurrent state | đơn giản, exact; cache/read lớn | context vừa, kernel dense tốt |
| Token-addressable sparse | vẫn giữ token K/V/latent và softmax trên selected slots | thêm indexer giữa query và main read | exact nếu hit; indexer + cache + gather | audit, code identifiers, citation/copy |
| Compressed-entry | vẫn dùng attention trên retained entries | thay remote token groups bằng entries nén | ít state/read; mất identity | semantic summary, extreme context, memory-bound |
| Recurrent + periodic | periodic layers vẫn token-attend; causal LM/FFN giữ nguyên | phần lớn layers thay append/read bằng fixed-state update | bounded R state; interference + mixed runtime | general-purpose chat/agent/coding dài |

### 5.2 Phần nào giữ nguyên?

```text
GIỮ NGUYÊN
  tokenizer → embeddings → causal next-token objective
  normalization → residual framework → FFN/MoE → LM head

THAY ĐỔI
  history representation
  selection/read path
  mixer schedule theo depth
  request-state layout và kernels

CÓ THỂ THAY ĐỔI ĐỘC LẬP
  MoE routing, residual topology, position method,
  context curriculum, dtype, serving scheduler
```

Nếu hai model đổi cả mixer, MoE, residual, data và curriculum, whole-model score không isolate mixer causality.[^evidence]

### 5.3 Khái niệm dễ nhầm

1. **Sparse read ≠ sparse storage.** Có thể đọc 2K token nhưng vẫn lưu toàn prefix.
2. **Per-token compression ≠ group compression.** MLA có thể nén mỗi token mà vẫn giữ addressability; CSA/HCA gộp nhiều token.
3. **Fixed-state layer ≠ fixed-state model.** Periodic attention layers vẫn có context-growing state.
4. **`3:1` ≠ universal optimum.** Đó là starting point có precedent, phải ablate theo workload.[^selection]
5. **Active parameters ≠ latency.** Resident weights, all-to-all, batch và utilization vẫn chi phối.[^moe]
6. **1M context support ≠ 1M reliable recall.** Cần đo recall theo vị trí và distractor.
7. **Residual retrieval ≠ sequence retrieval.** AttnRes/multi-stream residual xử lý depth information, không thay remote token memory.

## 6. Trong thực tế

### 6.1 Cơ chế nằm ở đâu trong model và serving system?

```text
request
  → tokenizer / optional modality encoder
  → prefill through mixed layer schedule
       R: recurrent/conv state
       A: KV/latent + optional index state
       B: compressed entries + local/tail state
       MoE: dispatch/expert/combine state
  → request-state handoff
  → decode loop
  → scheduler batches requests, manages prefix/cache pages
  → streamed output
```

Architecture chọn loại state; serving system quyết định placement, paging, reuse, quantization và scheduling.

### 6.2 Decision tree thực dụng

```text
Exact remote token copy là hard requirement?
├─ Có
│  ├─ Cache tuyến tính chấp nhận được + sparse kernel tốt?
│  │  └─ Chọn token-addressable sparse làm baseline chính.
│  └─ Memory quá chặt?
│     └─ Recurrent + periodic sparse/global, nhưng tăng A density
│        và đặt recall gate nghiêm ngặt; không mặc định group compression.
└─ Không
   ├─ Per-request memory/very-long decode là hard constraint?
   │  └─ Recurrent + periodic làm baseline chính.
   └─ Remote history chủ yếu cần summary và extreme compression?
      └─ Thử compressed-entry, luôn giữ local raw window.
```

Nếu context ngắn hoặc runtime thiếu optimized kernels, dense/GQA/MLA baseline có thể đơn giản và nhanh hơn cả ba nhánh phức tạp.

### 6.3 Walkthrough: chọn backbone cho coding agent 500K token

**Requirement ledger:**

| Field | Giá trị minh họa |
|---|---|
| Prompt | p50 120K, p95 500K tokens |
| Output | p50 800, p95 2K tokens |
| Exact retrieval | identifiers/numbers: hard gate ≥99% trên test nội bộ |
| Concurrency | 16–64 requests/GPU group |
| Prefix reuse | cao với cùng repository, nhưng cold path vẫn quan trọng |
| SLA | cold TTFT và p95 TPOT đo riêng |
| Hardware | runtime có recurrent kernel và block-sparse gather |

**Shortlist:**

1. Dense MLA/GQA baseline để biết complexity overhead thực.
2. Recurrent `3R:1A` với periodic sparse token retrieval.
3. Token-addressable sparse ở mọi attention layer như exact-retrieval control.
4. Compressed-entry là stress variant, không phải default vì exact identifiers là hard gate.

**Quyết định ban đầu:** chọn recurrent + periodic sparse cho development vì decode dài và concurrency tạo memory pressure, nhưng đặt token-addressable sparse làm fallback nếu exact recall không đạt gate. Đây là synthesis; chưa phải conclusion trước experiment.[^selection]

**Measurement:**

- exact-copy và selected-block recall theo vị trí 1%, 25%, 50%, 75%, 99%;
- cold/warm `TTFT`, prefill tokens/s, indexer/compression time;
- p50/p95 `TPOT` theo context và concurrency;
- bytes/request tách recurrent, conv, K/V, index và allocator peak;
- MoE all-to-all, rank load, dropped/overflow assignments;
- short-context regression và training stability qua curriculum stages.

### 6.4 Khi nên và không nên dùng

| Lựa chọn | Nên dùng khi | Không nên dùng khi |
|---|---|---|
| Token-addressable sparse | exact remote copy quan trọng; selector/kernel tốt | memory per request là hard bottleneck; index recall thấp |
| Compressed-entry | summary semantics đủ; context cực dài; cache IO chi phối | audit/quote/code identifier phải exact ngoài local window |
| Recurrent + periodic | mixed workload; long decode; cần giảm cache depth | workload cần dense exact interaction ở hầu hết layers; runtime recurrent kém |

### 6.5 Claim không thể suy ra chỉ từ lý thuyết

Không thể suy ra trước measurement:

- nhánh nào có lower `TTFT` hoặc `TPOT` trên target hardware;
- long-context benchmark quality và exact-copy reliability;
- MoE configuration nào cho best quality/cost;
- `3:1` có tối ưu ở scale/data mới hay không;
- residual design nào ổn định hơn sau post-training;
- curriculum tới 1M có giữ short-context quality;
- whole-model speedup, energy, dollar cost hoặc tail latency.

> [!note] Gate trước phần toán
> Đến đây người mới phải trả lời được: kiến trúc giải quyết việc lưu/đọc history dài; ba nhánh khác nhau ở token slots, group entries và recurrent state; tác động trực tiếp nằm ở addressability/state/failure mode; dense baseline vẫn giữ causal LM, residual và FFN; lựa chọn thực tế phải dựa trên exact-retrieval, memory, TTFT/TPOT, kernels và workload. Nếu chưa trả lời được, hãy quay lại requirement ledger thay vì đọc công thức.

## 7. Toán học — zoom in sau cùng

### 7.1 Bảng ký hiệu

| Ký hiệu | Shape / đơn vị | Ý nghĩa |
|---|---:|---|
| `S` | tokens | context length |
| `L_R`, `L_A`, `L_C` | layers | số recurrent, token-attention và compressed-entry layers |
| `B` | requests | batch/concurrency được accounting |
| `p` | bytes/element | dtype storage size |
| `c_A` | elements/token/layer | retained token-addressable state |
| `c_C` | elements/entry/layer | retained compressed-entry state |
| `m` | tokens/entry | compression group size |
| `f_R` | elements/layer | fixed recurrent/conv state |
| `k` | entries | top-k read budget |
| `q, k_i, v_i` | vectors | query, key và value |
| `H_t` | `(d_k,d_v)` | recurrent associative state |
| `r` | scalar | recurrent-to-attention mixer ratio |
| `Y` | metric | quality, latency, memory hoặc recall outcome |

### 7.2 Trường hợp nhỏ tính tay: một block `R R R A`

**Trực giác.** Ba recurrent layers giữ state không đổi theo context; một attention layer append state cho mỗi token.

**Công thức.** Raw request-state accounting giản lược:

$$
M_{3R:1A}(S)=pB\left(3f_R+Sc_A\right).
$$

**Ý nghĩa ký hiệu.** `3f_R` là fixed intercept; `S c_A` là context-linear slope của periodic attention.

**Shape flow.** Recurrent state có thể là `(B,H,d_k,d_v)`; attention cache có token axis `(B,H_KV,S,d_h)` cho K và V hoặc latent tương ứng.

**Ví dụ số.** Cho `p=2`, `B=1`, `f_R=8`, `c_A=4`:

- `S=2`: `M=2×(24+8)=64 bytes`.
- `S=5`: `M=2×(24+20)=88 bytes`.

Thêm ba token chỉ tăng phần A: `24 bytes`; recurrent state không đổi.

**Kết luận.** `75% recurrent layers` không làm whole model constant-state; nó giảm slope theo số attention layers.

### 7.3 Ba state-growth model tổng quát

**Trực giác.** So sánh cùng context bằng representation được giữ lại.

**Công thức.** Bỏ metadata/fragmentation:

$$
M_A(S)=pB L_A S c_A,
$$

$$
M_C(S)\approx pB L_C\left(\left\lceil\frac{S-W}{m}\right\rceil c_C+Wc_A\right),
$$

$$
M_R(S)=pB\left(L_Rf_R+L_ASc_A\right).
$$

**Ý nghĩa.** A là token-addressable; C dùng group size `m` và raw local window `W`; R là recurrent-plus-periodic.

**Shape flow.** A giữ token axis length `S`; C thay remote token axis bằng khoảng `(S-W)/m` entries; R bỏ token axis ở recurrent layers nhưng giữ nó ở A layers.

**Ví dụ số.** `S=1024`, `W=128`, `m=128`, một layer, `c_A=c_C=4`: A giữ 4096 elements; C giữ `(7+128)×4=540` elements. Số này chỉ là logical toy; model thật có tail, K/V factors, precision và layer-specific widths.

**Kết luận.** Compression làm slope nhỏ theo `m`; recurrence xóa slope ở R layers; sparse selection một mình không đổi slope nếu vẫn giữ mọi token.

### 7.4 Token-addressable sparse read

**Trực giác.** Indexer chọn candidate; main softmax chỉ đọc candidate nhưng value vẫn là token value gốc.

**Công thức.** Với selector score `g`:

$$
\mathcal I_t=\operatorname{TopK}_i g(q_t,k_i;k),
\qquad
o_t=\sum_{i\in\mathcal I_t}\operatorname{softmax}_i\left(\frac{q_t^\top k_i}{\sqrt d}\right)v_i.
$$

**Ý nghĩa.** `I_t` là selected token/block set; `k` là budget.

**Shape flow.** Prefix keys `(S,d)` → selector scores `(S)` → indices `(k)` → gathered K/V `(k,d)` → output `(d)`.

**Ví dụ số.** Với bốn values `[7,3,2,1]`, selector chọn index 0 và 2: main read vẫn thấy `7` nguyên bản. Nếu index 0 không được chọn, tăng softmax quality không thể phục hồi `7`.

**Kết luận.** Quality decomposes thành selector recall và attention/use quality.

### 7.5 Compressed-entry read

**Trực giác.** Group value là weighted summary; chọn đúng group không hoàn nguyên token thành viên.

**Công thức.** Với group `G_b`:

$$
\tilde k_b=\sum_{i\in G_b}\pi_{b,i}k_i,
\qquad
\tilde v_b=\sum_{i\in G_b}\pi_{b,i}v_i,
\qquad
\sum_{i\in G_b}\pi_{b,i}=1.
$$

**Ý nghĩa.** `π` là learned hoặc fixed compression weights; toy dùng mean.

**Shape flow.** `(m,d)` token vectors → một `(d)` entry; token axis co `m:1`.

**Ví dụ số.** Group values `[7,1,0,0]`, mean compression cho entry `2`; query chọn đúng entry vẫn đọc `2`, không phải `7`.

**Kết luận.** Đây là representation loss, khác selection miss.

### 7.6 Recurrent delta state và periodic recovery

**Trực giác.** State sửa association tại key thay vì append token; periodic attention giữ đường đọc slot gốc.

**Công thức.** Delta update giản lược:

$$
H_t=H_{t-1}+\beta_t k_t\left(v_t-H_{t-1}^{\top}k_t\right)^{\top},
\qquad o_t=H_t^{\top}q_t.
$$

**Ý nghĩa.** Error term sửa current association về value mới; KDA/Gated DeltaNet thêm decay/gating khác nhau.[^delta-ssm]

**Shape flow.** `k_t:(d_k)`, error `(d_v)`, outer product `(d_k,d_v)`, nên `H_t` giữ shape qua mọi token.

**Ví dụ số.** `H_0=0`, `k=(1,0)`, `v=(7,0)`, `β=1`: write đầu làm query cùng key đọc `(7,0)`; write sau cùng key với `(9,0)` sửa thành `(9,0)` mà không append row. Với non-orthogonal keys, updates có thể giao thoa.

**Kết luận.** State size fixed không đồng nghĩa memory lossless; periodic token attention là recovery path.

### 7.7 Mixer ratio và slope

**Trực giác.** Ratio giảm số layers có context-growing cache, nhưng periodic-layer width vẫn quan trọng.

**Công thức.** Với `r=L_R/L_A`:

$$
\rho_A=\frac{L_A}{L_R+L_A}=\frac{1}{r+1},
\qquad
\frac{\Delta M_R}{\Delta S}=pB L_A c_A.
$$

**Ví dụ số.** `3:1` cho `ρ_A=25%`; `7:1` cho `12.5%`. Nếu variant `7:1` phải tăng `c_A` gấp đôi hoặc mất recall, memory/quality frontier có thể không tốt hơn.

**Kết luận.** Ablate ratio cùng cache width và recall; không ablate ratio bằng layer count riêng.

### 7.8 Matched causal effect

**Trực giác.** Muốn nói component X gây thay đổi, control và treatment chỉ được đổi X trong phạm vi khả thi.

**Công thức.** Với seed `s`:

$$
\Delta_X=\frac{1}{n}\sum_{s=1}^{n}\left[Y_s(X=1)-Y_s(X=0)\right].
$$

Báo uncertainty qua distribution của paired differences, không chỉ một point estimate.

**Ví dụ số.** Giữ data, tokens, active FLOPs, optimizer, schedule, evaluation và runtime fixed; đổi `3R:1A` thành `2R:1A`. Nếu đồng thời tăng model width và đổi tokenizer, `Δ` không còn isolate mixer ratio.

**Kết luận.** Whole-model comparison chỉ cho bundle effect; matched ablation mới hỗ trợ scoped component causality.[^evidence]

## 8. Implementation — PyTorch tối thiểu

Code cụ thể hóa đúng ba memory semantics và một `ablation ledger`. Nó dùng FP64 để verification ổn định; không có learned selector/compressor, RoPE, multi-head, chunk kernel, MoE hay serving cache.

```python
from dataclasses import dataclass, replace
import math
import torch

DTYPE = torch.float64
RTOL, ATOL = 1e-7, 1e-9


def sparse_token_read(query, keys, values, top_k):
    """Token slots retained; selector and main read share dot-product in this toy."""
    scores = query @ keys.T / math.sqrt(keys.shape[-1])       # (S,)
    idx = torch.topk(scores, min(top_k, keys.shape[0])).indices
    logits = query @ keys[idx].T / math.sqrt(keys.shape[-1]) # (k,)
    out = torch.softmax(logits, dim=-1) @ values[idx]         # (d_v,)
    return out, idx, values[idx]


def compressed_entry_read(query, keys, values, group_size):
    """Mean-compress complete groups; dense-read compressed entries."""
    n = keys.shape[0] // group_size
    k_entry = keys[:n * group_size].reshape(n, group_size, -1).mean(dim=1)
    v_entry = values[:n * group_size].reshape(n, group_size, -1).mean(dim=1)
    logits = query @ k_entry.T / math.sqrt(keys.shape[-1])
    return torch.softmax(logits, dim=-1) @ v_entry, k_entry, v_entry


class DeltaMemory:
    """Fixed-state delta memory; production KDA/GDN adds projections/decay/kernels."""
    def __init__(self, d_key, d_value):
        self.state = torch.zeros(d_key, d_value, dtype=DTYPE)

    def write(self, key, value, beta=1.0):
        current = self.state.T @ key
        self.state = self.state + beta * torch.outer(key, value - current)

    def read(self, query):
        return self.state.T @ query


@dataclass(frozen=True)
class AblationConfig:
    mixer_ratio: str = "3R:1A"
    retrieval: str = "periodic-sparse"
    moe_experts: int = 256
    moe_top_k: int = 8
    residual: str = "standard"
    context_curriculum: tuple = (8_192, 32_768, 131_072)
    train_tokens: int = 10_000_000_000
    active_flops: float = 1.0
    optimizer: str = "same"
    tokenizer: str = "same"


def diff_fields(a, b):
    return [name for name in a.__dataclass_fields__
            if getattr(a, name) != getattr(b, name)]


def logical_state_elements(kind, seq_len, d=2, group=4,
                           recurrent_layers=3, attention_layers=1):
    if kind == "token-sparse":
        return attention_layers * 2 * seq_len * d
    if kind == "compressed":
        return attention_layers * 2 * math.ceil(seq_len / group) * d
    if kind == "recurrent-periodic":
        fixed = recurrent_layers * d * d
        growing = attention_layers * 2 * seq_len * d
        return fixed + growing
    raise ValueError(kind)


def remote_fact_fixture():
    # Token 0 carries the fact; high key scale makes retrieval inspectable.
    keys = torch.tensor([[20., 0.], [0., 1.], [0., 1.], [0., 1.]], dtype=DTYPE)
    values = torch.tensor([[7., 0.], [0., 1.], [0., 2.], [0., 3.]], dtype=DTYPE)
    query = torch.tensor([1., 0.], dtype=DTYPE)
    return query, keys, values


def run_tests():
    query, keys, values = remote_fact_fixture()

    # 1) Token-addressable sparse read selects and exposes the original fact slot.
    out, idx, selected_values = sparse_token_read(query, keys, values, top_k=1)
    assert idx.tolist() == [0]
    torch.testing.assert_close(selected_values[0], values[0], rtol=0.0, atol=0.0)
    torch.testing.assert_close(out, values[0], rtol=RTOL, atol=ATOL)

    # 2) Mean compression loses identity: the first group stores mean([7,0],[0,1]).
    out_c, _, v_entry = compressed_entry_read(query, keys, values, group_size=2)
    torch.testing.assert_close(
        v_entry[0], torch.tensor([3.5, 0.5], dtype=DTYPE), rtol=RTOL, atol=ATOL
    )
    assert not torch.allclose(v_entry[0], values[0])

    # 3) Permuting members inside a mean-compressed group cannot be observed.
    perm = torch.tensor([1, 0, 2, 3])
    out_perm, _, entries_perm = compressed_entry_read(
        query, keys[perm], values[perm], group_size=2
    )
    torch.testing.assert_close(v_entry, entries_perm, rtol=RTOL, atol=ATOL)
    torch.testing.assert_close(out_c, out_perm, rtol=RTOL, atol=ATOL)

    # 4) Recurrent state shape remains fixed across writes.
    memory = DeltaMemory(d_key=2, d_value=2)
    shape = memory.state.shape
    memory.write(torch.tensor([1., 0.], dtype=DTYPE),
                 torch.tensor([7., 0.], dtype=DTYPE))
    memory.write(torch.tensor([0., 1.], dtype=DTYPE),
                 torch.tensor([0., 3.], dtype=DTYPE))
    assert memory.state.shape == shape
    torch.testing.assert_close(memory.read(query), values[0], rtol=RTOL, atol=ATOL)

    # 5) A non-orthogonal write causes interference in fixed state.
    memory.write(torch.tensor([1., 1.], dtype=DTYPE) / math.sqrt(2),
                 torch.tensor([0., 9.], dtype=DTYPE))
    assert not torch.allclose(memory.read(query), values[0])

    # 6) Periodic token attention recovers the original slot.
    periodic, _, _ = sparse_token_read(query, keys, values, top_k=1)
    torch.testing.assert_close(periodic, values[0], rtol=RTOL, atol=ATOL)

    # 7) State ledger has the expected context slope.
    for kind, expected_delta in [
        ("token-sparse", 2 * 2),
        ("recurrent-periodic", 2 * 2),
    ]:
        delta = logical_state_elements(kind, 9) - logical_state_elements(kind, 8)
        torch.testing.assert_close(
            torch.tensor(float(delta)), torch.tensor(float(expected_delta)),
            rtol=0.0, atol=0.0,
        )
    # Compression adds one entry only when crossing a group boundary.
    torch.testing.assert_close(
        torch.tensor(float(logical_state_elements("compressed", 9)
                           - logical_state_elements("compressed", 8))),
        torch.tensor(4.0), rtol=0.0, atol=0.0,
    )

    # 8) A matched ablation changes exactly one declared factor.
    control = AblationConfig()
    treatment = replace(control, mixer_ratio="2R:1A")
    assert diff_fields(control, treatment) == ["mixer_ratio"]
    bad = replace(control, mixer_ratio="2R:1A", moe_top_k=10)
    assert diff_fields(control, bad) == ["mixer_ratio", "moe_top_k"]

    print("8 verification groups passed")


if __name__ == "__main__":
    run_tests()
```

### Mapping code về cơ chế

| Code | Cơ chế đã giải thích | Cố ý bỏ qua |
|---|---|---|
| `sparse_token_read` | select → gather slot gốc → softmax | learned block indexer, causal offsets, sparse kernel |
| `compressed_entry_read` | group → entry → dense read | learned overlapping compression, local window, tail |
| `DeltaMemory` | fixed state + key-addressed correction | decay, multi-head, chunkwise/recurrent kernels |
| `logical_state_elements` | fixed intercept và context slope | dtype/layout/allocator/metadata thật |
| `AblationConfig` | chỉ một treatment field được đổi | training launcher và artifact tracking |

Nếu attention implementation thật dùng RoPE, phải ghi rõ pairing convention (`interleaved` trong course convention) và dùng absolute `position_ids` tiếp nối prefix. Cache token-level thông thường có shape `(B, H_KV, S, d_h)` mỗi K/V per layer; toy bỏ batch/head để dễ inspect.

## 9. Verification trước benchmark

Lưu code vào file và chạy:

```bash
python3 workload_selection_toy.py
```

Expected output:

```text
8 verification groups passed
```

Suite đã được thực thi thành công bằng PyTorch 2.13 trên CPU trong môi trường biên soạn offline; môi trường thiếu NumPy phát một warning khởi tạo không ảnh hưởng các tensor tests này.

Ý nghĩa từng nhóm:

1. **Addressability:** selected value bằng đúng fact slot.
2. **Compression loss:** group entry là mean, không còn fact riêng.
3. **Permutation invariance:** mean compression không phân biệt thứ tự trong group.
4. **Fixed shape:** recurrent state không có token axis tăng dần.
5. **Interference:** non-orthogonal key làm association cũ đổi.
6. **Periodic recovery:** token-addressable checkpoint đọc lại fact gốc.
7. **State slope:** sparse read không giảm retained-token slope; compression tăng theo boundary; recurrent chỉ thêm slope ở periodic layer.
8. **Matched ablation:** treatment hợp lệ chỉ đổi một factor; variant đổi thêm MoE top-k là confounded.

FP64 và tolerance `rtol=1e-7`, `atol=1e-9` phù hợp semantic toy CPU. Với BF16/FP16/FP8 hoặc fused kernels, phải đo numerical error rồi chọn tolerance; không sao chép tolerance này vào production tests.

## 10. Requirement ledger hoàn chỉnh

Dùng ledger này trước khi allocate training run:

| Nhóm | Field bắt buộc | Baseline | Gate / decision rule |
|---|---|---|---|
| Workload | prompt/output p50,p95,p99; concurrency; prefix hit | production trace | trace đủ representative |
| Retrieval | exact-copy, semantic QA, recall theo vị trí/distractor | dense token attention | hard requirements không regression |
| Mixer | schedule và ratio; R/A state shapes | full attention hoặc current model | quality–memory Pareto |
| Retrieval type | dense, token sparse, block sparse, compressed entry | cùng periodic density | selector recall + answer quality |
| MoE | expert count, top-k, shared path, capacity, placement | dense FFN hoặc current MoE | quality cùng active compute; no overload |
| Residual | standard, multi-stream/gated/constrained/depth retrieval | standard residual | stability/quality bù activation/comm cost |
| Curriculum | stage lengths, tokens/stage, transition gate | short-context recipe | long gain không phá short quality |
| Prefill | cold/warm TTFT, tokens/s, index/compress/chunk time | same server/runtime | p50/p95 SLA |
| Decode | TPOT, throughput, recurrent/KV/MoE time | same concurrency | p50/p95 SLA |
| Memory | weights, KV/latent, recurrent, index, allocator peak | same dtype/cache policy | fit target concurrency |
| Training | loss, instability, tokens, FLOPs, wall time | matched budget | same token/compute boundary |
| Evidence | seeds, confidence interval, code/config artifacts | predeclared protocol | claim strength không vượt design |

Mọi row phải có owner, measurement command, artifact path và stop/go threshold trong experiment system thật. Course không đặt threshold thay cho deployment.

## 11. Matched ablation plan

### 11.1 Nguyên tắc chung

- Dùng cùng tokenizer, data mixture, token budget, optimizer family, learning-rate search budget, active FLOPs target và evaluation harness.
- Pair seeds khi có thể; báo mean và paired differences.
- Tách architecture semantic run khỏi kernel/runtime run.
- Không đổi nhiều trục trong một row rồi gọi đó là component ablation.
- Nếu shape buộc thay parameter count, match cả `iso-active-compute` và `iso-total-parameter` views hoặc ghi rõ không match được.[^evidence]

### 11.2 Phase 0 — baseline và instrumentation

| Run | Mixer | Retrieval | MoE | Residual | Mục đích |
|---|---|---|---|---|---|
| B0 | full dense/MLA | dense token | dense hoặc current | standard | quality/latency reference |
| B1 | current production | current | current | current | operational reference |

Instrumentation phải xuất per-layer state bytes, indexer/compression/recurrent time, MoE all-to-all và cold/warm lifecycle timestamps.

### 11.3 Phase 1 — mixer ratio

| Treatment | Giữ fixed | Đo |
|---|---|---|
| full A, `1R:1A`, `2R:1A`, `3R:1A`, `7R:1A` | retrieval core, cache width, MoE, residual, data/compute | loss, exact/semantic recall, memory slope, TTFT, TPOT |

`3:1` là starting point có precedent ở Kimi/Qwen, không phải prior rằng nó sẽ thắng.[^selection][^k3][^qwen-next]

**Decision:** loại ratio vi phạm hard recall gate; trên phần còn lại chọn Pareto set thay vì một weighted score bí mật.

### 11.4 Phase 2 — retrieval type

Chạy tại 1–2 ratio sống sót:

| Variant | Representation | Read | Metric riêng |
|---|---|---|---|
| global token | per-token | dense | exact upper-control, cache slope |
| token sparse | per-token | top-k token | index recall@k, gather locality |
| block sparse | per-token main KV | top-k blocks | block recall, extra tokens/read |
| compressed sparse | group entries | top-k entries + local | representation fidelity + selector recall |
| heavily compressed | large group entries | dense entries + local | exact-copy loss, memory reduction |

Match read budget nơi có ý nghĩa, nhưng không giả vờ `k token` tương đương `k compressed entries`; báo actual tokens/bytes touched.

### 11.5 Phase 3 — MoE routing

| Axis | Variants | Match / report |
|---|---|---|
| Expert count | dense, 128, 256, 512 | total/resident params |
| top-k | 1, 4, 8, 10 | active FLOPs, all-to-all |
| shared path | none / one shared | active compute |
| balance | auxiliary / bias control | load, overflow, quality |
| placement | expert-parallel group sizes | topology, rank load |

Đo `router entropy`, offered/accepted tokens per expert, capacity overflow/drop, all-to-all bytes/time, p95 expert time và total resident memory. Active parameter count không thay cho measurement.[^moe]

### 11.6 Phase 4 — residual design

So `standard residual` với từng treatment riêng: gated multi-stream, constrained multi-stream hoặc depth retrieval. Giữ mixer/MoE đã chọn fixed.

- training loss và gradient/update norms;
- activation/retained-depth bytes;
- extra communication/read-write time;
- downstream và long-context quality;
- post-training stability nếu source cho thấy pretrain-neutral change có thể diverge sau post-training.[^qwen-next]

Không ghép residual treatment mới và mixer mới trong cùng run đầu tiên.

### 11.7 Phase 5 — context curriculum

Ví dụ staged plan:

```text
8K → 32K → 128K → 512K → 1M
```

Mỗi transition chỉ xảy ra khi:

- validation loss không bất ổn;
- short-context regression dưới threshold;
- recall theo vị trí đạt gate;
- numerical state/kernel checks pass;
- memory và training throughput vẫn nằm trong budget.

Ablate ít nhất `short-only`, `direct-to-long` và `staged`; match tổng tokens/compute hoặc ghi rõ khác biệt. Context metadata không chứng minh model đã học dùng mọi vị trí.

### 11.8 Phase 6 — serving trên target hardware

| Sweep | Giữ fixed | Báo cáo |
|---|---|---|
| context 8K→1M | output, batch, dtype | cold/warm TTFT, prefill tokens/s, peak bytes |
| output 128→2K | prompt, concurrency | TPOT distribution, E2E |
| concurrency 1→N | prompt/output distribution | throughput, p50/p95 latency, OOM point |
| prefix hit 0→100% | same prefix corpus | cache hit, warm TTFT, eviction |
| dtype/quantization | checkpoint/runtime | quality drift, bytes, kernel time |

Báo `TTFT` boundary rõ ràng và tách server queueing khỏi model prefill khi có thể.[^lifecycle]

### 11.9 Run matrix tối thiểu reviewable

Một kế hoạch thực tế không cần Cartesian product toàn bộ. Dùng staged elimination:

1. 5 mixer-ratio runs ở scale nhỏ, 3 seeds.
2. 5 retrieval runs trên 2 ratios tốt nhất.
3. 4–6 MoE runs trên 1–2 architecture candidates.
4. 3 residual treatments, mỗi treatment riêng.
5. 3 curriculum variants.
6. 2 finalists chạy full serving sweep và long-context suite.

Pre-register gates để tránh chọn metric thuận lợi sau khi xem kết quả.

## 12. Benchmark / Trade-offs

### 12.1 Quality suite

- exact-copy identifiers, numbers, citations;
- semantic QA với distractors;
- multi-hop retrieval;
- code patch correctness;
- short-context language/reasoning controls;
- recall theo normalized position và context length;
- selector recall trước answer score.

### 12.2 Systems suite

| Pha | Metric chính | Breakdown |
|---|---|---|
| Training | tokens/s, loss/FLOP, stability | mixer, MoE, communication |
| Prefill | cold/warm TTFT, tokens/s | indexer, compression, recurrent chunk, attention |
| Decode | TPOT, throughput | state update, KV read, gather, MoE |
| Memory | bytes/request, peak allocator | recurrent, conv, K/V, index, entries, workspace |
| Scale | p50/p95/p99 under load | queue, batch, network, cache eviction |

### 12.3 Pareto decision

Không cộng tùy tiện quality, latency và memory thành một score nếu business chưa định nghĩa utility. Trước hết loại mọi candidate vi phạm hard gates; sau đó giữ các candidate không bị candidate khác thắng đồng thời trên mọi metric quan trọng. Human owner chọn điểm trên Pareto frontier theo cost/risk.

### 12.4 Điều benchmark không kết luận

- Toy pass không chứng minh learned selector/compressor tốt.
- Microbenchmark kernel không chứng minh end-to-end serving.
- Smaller-scale ablation không đảm bảo frontier-scale effect.
- Whole-model benchmark không isolate mixer, MoE hay residual.
- Author-reported point estimate không phải independent reproduction.
- Context window và synthetic needle score không đủ chứng minh production-agent reliability.

## 13. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| Exact recall thấp nhưng answer đôi lúc đúng | selector miss bị model đoán | đo selected-set recall trước generation |
| Chọn đúng group nhưng quote sai | compressed representation mất identity | inspect group entry và local-window membership |
| “Fixed-state” memory vẫn tăng | periodic K/V/index/cache bị bỏ sót | log tensor shape/bytes theo layer và token |
| Sparse attention chậm hơn dense | indexer/gather overhead, kernel locality kém | profile index, gather, main attention riêng |
| `3:1` quality kém | periodic density thấp hoặc recurrent interference | sweep ratio với cùng retrieval/MoE |
| TPOT tốt nhưng TTFT xấu | chunk/index/compression prefill overhead | tách prefill stage timing |
| Active params thấp nhưng latency cao | all-to-all, small GEMM, total weights | profile MoE dispatch/combine và rank load |
| Residual variant pretrain ổn, post-train kém | branch usage/gating thay đổi | giữ checkpoint và ablate post-training riêng |
| Long curriculum phá short tasks | positional/curriculum distribution shift | chạy short suite tại mỗi stage |
| Ablation “thắng” nhưng đổi hai fields | confounded treatment | diff config artifacts tự động |
| Warm TTFT rất tốt, cold path xấu | prefix cache che raw prefill | báo hit rate và cold/warm riêng |
| BF16 test fail nhưng FP64 pass | numerical range/accumulation | inspect dtype, normalization, decay và tolerance |

## 14. Giới hạn & bước tiếp theo

Course này là synthesis sư phạm và decision procedure. Nó không chứng minh blueprint `Hybrid-96`, ratio `3:1`, KDA, DSA hay CSA/HCA là optimum. DeepSeek-V4 concepts được dùng cho mechanism nhưng hiện ở trạng thái `draft`; V4/K3/GLM/Qwen evidence chủ yếu là author reports và reference implementations, không có một head-to-head matched experiment trên cùng data, scale, hardware và runtime.[^selection][^v4-k3][^glm-k3]

Bước tiếp theo:

1. Điền requirement ledger bằng production trace thật.
2. Chạy toy để khóa semantic expectations.
3. Pre-register smallest matched matrix và stop/go gates.
4. Bắt đầu từ dense baseline, không từ frontier bundle đầy đủ.
5. Đọc [Delta-rule vs SSM adoption](delta-rule-vs-ssm-frontier-adoption.md) nếu recurrent branch còn chưa chốt.
6. Dùng [Comparative reading và evidence discipline](comparative-reading-evidence-discipline-beginners-course.md) để review mọi causal sentence trước quyết định.

## Relationships

- **Depends on:** [Long-context architecture archetypes](long-context-architecture-archetypes-beginners-course.md) — định nghĩa ba memory semantics và failure modes.
- **Depends on:** [Comparative reading và evidence discipline](comparative-reading-evidence-discipline-beginners-course.md) — quy tắc matched comparison và causal scope.
- **Uses:** [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md) — recommendation và Hybrid-96 proposal có điều kiện.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — routing, capacity, residency và communication ledger.
- **Uses:** [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md) — tách TTFT, prefill, TPOT và end-to-end latency.
- **Elaborates:** Stage 9.8 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Các mechanism claim được tổng hợp từ wiki concepts về Kimi K3, GLM-5, Qwen3.8-Flash-Next và DeepSeek-V4; các report không cung cấp một experiment ba nhánh matched end-to-end. Những con số cấu hình là model-specific, còn ledger thresholds, decision tree, toy equations và ablation ordering là pedagogical synthesis. PyTorch tests chỉ kiểm tra invariants của mean compression, dot-product selection và delta memory giản lược; chúng không xác minh checkpoint weights, selector recall, learned compression, optimized kernels, MoE communication, residual variants, 1M-context quality hay production SLA. Mọi quyết định deployment phải được đo lại trên target data, dtype, runtime, hardware, concurrency và cache policy.

[^selection]: [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md), recommendation, Hybrid-96 proposal, mandatory ablation order, and explicit non-universality.
[^archetypes]: [Long-context architecture archetypes](long-context-architecture-archetypes-beginners-course.md), matched comparison of token addressability, compressed entries, recurrent state, locality, indexers, and direct versus benchmark implications.
[^evidence]: [Comparative reading và evidence discipline](comparative-reading-evidence-discipline-beginners-course.md), claim types, matched dimensions, controls, confounders, serving workload cards, and causal wording.
[^recurrent]: [Recurrent-majority frontier models](recurrent-majority-frontier-models-beginners-course.md), schedule, state/cache ledger, periodic retrieval, practical measurements, and reference-code boundaries.
[^v4-k3]: [DeepSeek-V4 and Kimi K3 architecture comparison](deepseek-v4-and-kimi-k3-architecture-comparison.md), compressed-entry versus recurrent-plus-periodic design and unmatched-evidence limits; page status is `draft`.
[^glm-k3]: [GLM-5 and Kimi K3 architecture comparison](glm-5-and-kimi-k3-architecture-comparison.md), token-addressable MLA/DSA versus fixed-state KDA plus periodic MLA and non-comparability limits.
[^compressed]: [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md), CSA/HCA grouping, local window, state layout, and missing controlled component ablations; page status is `draft`.
[^k3]: [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), 69 KDA/24 MLA schedule, mixed cache forms, MoE/depth paths, and component-isolation limits.
[^qwen-next]: [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), 36 Gated DeltaNet/12 QSA schedule, QSA token retrieval, Gated Residual, MoE, context boundary, and author-run smaller-scale ablations.
[^delta-ssm]: [Delta-rule versus SSM frontier adoption](delta-rule-vs-ssm-frontier-adoption.md), key-addressed delta correction, forgetting granularity, hybridization, contradictory rankings, and author-run evidence limits.
[^moe]: [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), capacity, routing balance, all-to-all, total-weight residency, and configuration-dependent efficiency.
[^lifecycle]: [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md), operational definitions and measurement boundaries for prefill, decode, TTFT, TPOT, throughput, prefix caching, and end-to-end latency.
