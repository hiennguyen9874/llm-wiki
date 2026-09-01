---
type: Synthesis
title: "Sparse capacity beyond MoE: compute, block routing và lookup memory — khóa học cho người mới"
description: A top-down beginner course that distinguishes routed FFN compute, routed complete blocks, and sparse lookup memory through separate total, active, resident, accessed, FLOP, byte, and dispatch ledgers.
tags: [sparse-capacity, mixture-of-experts, mixture-of-layers, conditional-memory, n-grams, pytorch, learning-roadmap]
status: stable
created: 2026-09-01
generated:
  by: llm-wiki-agent/1
  at: 2026-09-01T17:15:06+07:00
sources:
  - id: ngram-memory
    resource: n-gram-embeddings-and-conditional-memory.md
    title: N-gram embeddings and conditional memory
  - id: engram
    resource: engram-conditional-memory-architecture.md
    title: Engram conditional-memory architecture
  - id: scone
    resource: scone-scalable-contextualized-offloaded-n-gram-embeddings.md
    title: SCONE scalable contextualized offloaded n-gram embeddings
  - id: over-encoding
    resource: over-encoding-hierarchical-n-gram-input-embeddings.md
    title: Over-Encoding hierarchical n-gram input embeddings
  - id: mol
    resource: mixture-of-layers-block-routing.md
    title: Mixture of Layers block routing
  - id: mol-evaluation
    resource: mixture-of-layers-evaluation-and-serving-trade-offs.md
    title: Mixture of Layers evaluation and serving trade-offs
  - id: moe-course
    resource: mixture-of-experts-sparse-routing-beginners-guide.md
    title: Mixture-of-Experts và sparse routing — bài học cho người mới
  - id: moe-systems
    resource: mixture-of-experts-training-and-systems-trade-offs.md
    title: Mixture-of-Experts training and systems trade-offs
---

# Sparse capacity beyond MoE: compute, block routing và lookup memory — khóa học cho người mới

`Sparse capacity` không phải một cơ chế duy nhất. `MoE` chọn một số `FFN experts` để **tính**, `Mixture of Layers` chọn một số complete thin blocks để **tính cả token mixing lẫn FFN**, còn `conditional memory` chọn vài rows từ bảng lớn để **đọc**. Cả ba đều cho phép `total parameters` lớn hơn phần được dùng cho một token, nhưng chúng tạo FLOPs, dispatch, memory traffic và placement constraints khác nhau. Bài này dùng bốn sổ cái độc lập — `total`, `active`, `resident`, `accessed` — để tránh suy luận sai rằng “sparse” đồng nghĩa với “nhẹ”, “nằm vừa trên GPU”, hoặc “latency thấp”.[^moe-course][^mol][^ngram-memory]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Giải thích được routed FFN compute, routed complete blocks và sparse lookup memory giải quyết ba kiểu bottleneck khác nhau.
> 2. Trace được một token qua router hoặc hash lookup từ input đến output mà chưa cần công thức.
> 3. Tách được hệ quả trực tiếp của cơ chế khỏi quality/latency chỉ được báo cáo qua benchmark.
> 4. Lập được ledger cho `total`, `active`, `resident`, `accessed`, active FLOPs, bytes read và dispatch.
> 5. Chạy một PyTorch lab gồm hashed n-gram lookup có collision accounting, toy MoE và toy whole-block router; kiểm chứng bằng `torch.testing.assert_close`.

## 1. Bức tranh toàn cảnh

### 1.1 Vấn đề: tăng capacity mà không làm mọi token chạy qua mọi weight

Trong dense Transformer, mỗi token thường đi qua cùng attention block và cùng FFN. Nếu tăng width hoặc depth, model có thêm parameters nhưng mỗi token cũng phải chạy thêm arithmetic. `Sparse capacity` tìm cách mở rộng “kho năng lực” mà chỉ dùng một phần kho cho mỗi token.[^moe-course]

Có ba câu hỏi khác nhau thường bị gom thành một:

1. **Token cần transformation nào?** — routed FFN chọn expert computation.
2. **Token cần processing path nào?** — block routing chọn complete block gồm nhiều sublayers.
3. **Local pattern này cần vector nào?** — sparse lookup dùng key xác định để đọc table row.

Cùng là “chỉ dùng một phần parameters”, nhưng một expert FFN phải thực hiện matrix multiplications, một routed block còn chạy token mixer và residual logic, còn một embedding row chủ yếu được fetch rồi fuse. Vì thế không thể so chúng chỉ bằng `active parameters`.[^mol][^engram]

### 1.2 Ý tưởng cốt lõi trong một câu

**Hãy hỏi sparse mechanism đang chọn computation hay chọn stored value, rồi ghi riêng weights tồn tại, weights được kích hoạt, weights phải cư trú ở từng memory tier và bytes thực sự được đọc.**

Câu này là synthesis sư phạm từ các cơ chế được dẫn nguồn; nó không phải một metric chuẩn duy nhất của các paper.[^moe-systems][^mol][^ngram-memory]

### 1.3 Mental model: bệnh viện, phòng điều trị và kho hồ sơ

```text
Routed FFN / MoE
  bệnh nhân → quầy phân loại học được → 1–2 bác sĩ chuyên khoa
  phần được chọn: một transformation chuyên biệt

Routed complete blocks / Mixture of Layers
  bệnh nhân → quầy phân loại học được → 1–2 phòng điều trị hoàn chỉnh
  mỗi phòng: khám chuỗi thông tin + xử lý nội bộ + trả kết quả

Sparse lookup memory / n-gram memory
  mã hồ sơ từ vài token gần nhau → địa chỉ ngăn tủ → lấy vector đã lưu
  phần được chọn: một record, không phải cả đội xử lý
```

Một bệnh viện có thể có hàng trăm bác sĩ nhưng ca hiện tại chỉ gọi hai người. Kho hồ sơ có thể rất lớn nhưng mỗi ca chỉ lấy vài records. Tuy vậy, bệnh viện vẫn phải bố trí bác sĩ ở đâu đó; kho hồ sơ vẫn phải nằm trong GPU, host RAM hoặc NVMe; và đi lấy hồ sơ chậm có thể làm cả pipeline chờ.

### 1.4 Bốn sổ cái không được trộn

| Sổ cái | Câu hỏi | Ví dụ hiểu đúng | Suy luận không hợp lệ |
|---|---|---|---|
| `total parameters` | Model có bao nhiêu learned scalars? | Tất cả experts hoặc mọi table rows đều được tính | “Tất cả đều chạy cho mỗi token” |
| `active parameters` | Parameters của selected computation nào tham gia transformation? | Hai FFN experts được gọi | “Chỉ cần chứa hai experts trong memory” |
| `resident parameters` | Parameters nào đang nằm ở GPU, host RAM hoặc storage tier? | Toàn expert bank có thể GPU-resident; table có thể host-resident | “Resident nghĩa là được đọc ở token này” |
| `accessed parameters` | Token/request thực sự đọc weights hoặc rows nào? | Hai experts được stream/read; ba n-gram rows được fetch | “Đếm scalars được đọc đủ để suy ra latency” |

`Resident` là thuộc tính của placement và runtime, không chỉ của architecture. `Accessed` cũng cần định nghĩa phạm vi: logical selected parameters, unique bytes sau cache, hay physical traffic đo tại memory controller. Bài này dùng **logical accessed bytes** trong toy ledger và luôn ghi rõ giới hạn đó.

### 1.5 Điều cần biết trước

- [Mixture-of-Experts và sparse routing](mixture-of-experts-sparse-routing-beginners-guide.md): router, top-k và expert FFN.
- [Decoder-only Transformer](decoder-only-transformer-beginners-guide.md): attention/token mixer, FFN và residual trong một block.
- Kiến thức PyTorch cơ bản: `nn.Linear`, `nn.Embedding`, indexing và tensor shape.

Không cần biết distributed kernels. Bài này không thiết kế production `all-to-all`, asynchronous prefetch hay NVMe cache.

## 2. Cách hoạt động — nhìn từ đầu đến cuối

Ta dùng một ví dụ xuyên suốt: model xử lý câu **“New York pizza is great”**. Ở token `pizza`, bigram `York pizza` là local pattern hữu ích; hidden state cũng có thể được router gửi đến một processing path phù hợp.

### 2.1 Dense baseline

```text
token IDs
   ↓
base embedding
   ↓
attention / token mixer
   ↓
shared FFN
   ↓
next hidden state
```

Mọi token chạy cùng block weights. Không có selection, hash collision hay token dispatch. Đây là baseline dễ triển khai nhưng tăng parameters trong block thường kéo theo tăng per-token computation.

### 2.2 Luồng A — routed FFN compute

```text
hidden state của "pizza"
   ├── router chấm điểm expert bank
   ├── top-k chọn expert IDs
   ├── dispatch token đến selected FFNs
   ├── selected experts chạy matrix multiplications
   ├── combine outputs bằng gate weights
   └── cộng residual → output
```

Điểm thay đổi nằm ở **FFN branch**; attention, token order, causal mask và phần còn lại của block vẫn giữ nguyên. Practical MoE phải group tokens, giới hạn capacity, cân bằng load và có thể gửi tokens qua devices bằng `all-to-all`.[^moe-course][^moe-systems]

Trong ví dụ, router có thể gửi `pizza` đến Expert 1 và Expert 4. Điều này không chứng minh Expert 1 là “food expert”: semantic specialization cần evidence riêng. Router chỉ đưa ra learned conditional path.

### 2.3 Luồng B — routed complete blocks

```text
hidden state của "pizza"
   ├── block router chấm điểm nhiều thin blocks
   ├── top-k chọn complete processing paths
   ├── gather các token cùng routed block thành subsequence
   ├── mỗi selected block chạy token mixer + FFN
   ├── scatter và combine block deltas
   └── cộng outer residual → output
```

Khác biệt quan trọng là selection bao quanh **cả block**, không chỉ FFN. Trong Mixture of Layers được document, mỗi thin block có down/up projections, attention và FFN; shared full-sequence softmax block luôn hoạt động, còn routed blocks dùng Gated DeltaNet trên sparse token subsequences.[^mol]

Ví dụ `pizza` và `great` có thể vào Block 2, còn `New` và `York` vào Block 0. Khi block có sequence mixer, grouping không còn chỉ là “chạy MLP độc lập”: routed subsequence và thứ tự token ảnh hưởng phần mixer. Reported MoL giữ một shared global block để bù việc routed blocks chỉ thấy subset.[^mol]

> [!note] Toy lab và paper khác nhau
> Toy whole-block router bên dưới dùng causal cumulative mean làm token mixer để data flow dễ inspect. Nó minh họa “routing bao quanh mixer + FFN”, không tái tạo thin projection, Gated DeltaNet hay shared softmax block của Mixture of Layers.

### 2.4 Luồng C — sparse lookup memory

```text
token IDs: ... "York", "pizza"
   ├── chuẩn hóa IDs nếu architecture yêu cầu
   ├── tạo suffix n-gram key: "York pizza"
   ├── deterministic hash → table row
   ├── fetch một vector từ table
   ├── optional projection / convolution / contextual gate
   └── fuse với hidden state → output
```

Selection ở đây không hỏi “expert nào nên tính?”. Key token IDs xác định địa chỉ trước khi deep hidden state tồn tại. Hash table giữ kích thước hữu hạn nhưng hai n-grams khác nhau có thể trỏ cùng row; đó là `collision`.[^ngram-memory][^engram]

Các variants đặt lookup ở vị trí khác nhau:

- **Over-Encoding:** thêm hierarchical hashed n-gram features ở input, giữ base output vocabulary.[^over-encoding]
- **SCONE:** chọn longest frequent n-gram; training dùng một f-gram Transformer, inference precompute vector vào off-accelerator table.[^scone]
- **Engram:** lookup deterministic hashed suffix n-grams ở selected intermediate layers, rồi dùng current hidden state để gate vector trước residual fusion.[^engram]

Với `York pizza`, table có thể trả một vector local-pattern. Downstream Transformer vẫn làm contextual processing và next-token prediction; đây không phải classical n-gram probability model.[^ngram-memory]

### 2.5 Một lượt trace chung

| Bước | MoE | Whole-block routing | Lookup memory |
|---|---|---|---|
| Input cho selector | hidden state | hidden state | token-ID n-gram key |
| Selector | learned router | learned block router | deterministic/frequency lookup |
| Selected unit | FFN expert | mixer + FFN block | embedding row |
| Main work | matrix compute | mixer + matrix compute | memory fetch + light fusion tùy design |
| Dispatch | token ↔ expert | token ↔ block subsequence | key ↔ row/tier |
| Output | weighted expert delta | weighted block delta | retrieved vector fused vào representation |
| Failure mode dễ thấy | collapse/overflow | fragmented subsequences/global-context loss | collision/miss/bandwidth stall |

## 3. Tác động

### 3.1 Hệ quả trực tiếp của thiết kế

| Cơ chế | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
|---|---|---|---|
| Routed FFN | Không chạy mọi expert FFN cho mỗi token | router, packing, dispatch/combine, imbalance; total expert weights vẫn phải lưu | selected expert GEMMs đủ lớn và balanced; communication không lấn át compute |
| Routed complete blocks | Sparsify nhiều work hơn FFN-only vì selection bao cả mixer và FFN | dispatch phức tạp hơn; routed block chỉ thấy subset; projection wrapper có floor | sparse block kernel hiệu quả và có path giữ global context khi workload cần |
| Sparse lookup | Rất nhiều table parameters nhưng chỉ đọc vài rows/token | table storage, hash collisions, lookup bandwidth, placement/prefetch | keys có ích; rows tới kịp; collision và transfer không phá quality/latency |

MoE giảm **routed FFN arithmetic**, không tự giảm attention hay KV cache. Block routing có thể thay đổi cả sequence-mixing work. Lookup memory chủ yếu thêm **capacity qua stored values**, nên FLOPs nhỏ không có nghĩa bytes hoặc latency nhỏ.[^moe-systems][^mol][^ngram-memory]

### 3.2 Quality và behavior

- MoE và block routers là learned selectors, nên behavior phụ thuộc training signal, balance và data distribution.
- Hashed n-gram lookup inject local-pattern features; collision làm nhiều keys chia một row, còn contextual gate chỉ có thể học cách suppress noise chứ không bảo đảm khôi phục đúng record.[^engram]
- Complete-block routing thay information path sâu hơn FFN routing: token mixer trong routed path nhìn routed subsequence, nên selection có thể ảnh hưởng token interaction chứ không chỉ channel transformation.[^mol]

Đây là mechanism-level consequences. Không cơ chế nào tự chứng minh downstream quality cao hơn dense baseline.

### 3.3 Memory, compute và latency

- **Memory capacity:** cả expert bank và lookup table làm `total parameters` tăng.
- **Active compute:** MoE chọn vài FFNs; whole-block routing chọn vài blocks; lookup chỉ cần fusion compute ngoài row read.
- **Parameter residency:** MoE weights thường cần placement phù hợp với low-latency expert execution; static lookup có thể phù hợp hơn với host/offload vì address có thể biết sớm, nhưng overlap là implementation claim phải đo.[^engram][^scone]
- **Traffic:** expert routing gửi activations đến weights; lookup routing đưa keys đến rows rồi trả vectors. Hai loại traffic có byte shape và locality khác nhau.
- **Latency:** FLOPs giảm có thể bị dispatch, small GEMMs, random reads hoặc synchronization che lấp.

### 3.4 Direct consequence và reported benchmark không phải một

Mixture of Layers trực tiếp giảm số routed blocks active, nhưng preprint được compile báo cáo kết quả phụ thuộc scale và workload: có iso-active perplexity gain trong một số regime, vẫn thua iso-total dense model, prefill crossover phụ thuộc GPU/context, và measured decode chậm hơn trong implementation có Python dispatch floor.[^mol-evaluation]

Engram, SCONE và Over-Encoding có author-run evidence riêng, nhưng course này không dùng các scores đó để kết luận lookup memory “tốt hơn MoE”. Concept tổng hợp ghi rõ LongCat chỉ thấy lợi thế allocation trong một high-sparsity regime cụ thể; threshold không phổ quát.[^ngram-memory]

## 4. Sự khác biệt

### 4.1 Bảng so sánh với dense baseline

| Cơ chế | Giống dense ở đâu | Khác ở data flow | Trade-off chính | Khi phù hợp |
|---|---|---|---|---|
| Dense block | Cùng hidden width, residual, objective | Không selector; mọi token dùng cùng weights | Compute tăng cùng block capacity | Baseline đơn giản, batch nhỏ, latency predictability quan trọng |
| MoE | Attention và block shell thường giữ nguyên | Router thay shared FFN bằng selected FFNs | Nhiều total capacity, ít expert compute; trả dispatch và residency | Large batches/training hoặc runtime có expert kernels/interconnect tốt |
| Whole-block routing | Vẫn nhận/trả residual-width hidden states | Router bao quanh mixer + FFN blocks | Sparsify rộng hơn nhưng information path và dispatch phức tạp hơn | Muốn conditional processing path và có cách giữ global context |
| Lookup memory | Main Transformer và output head vẫn tồn tại | Token-derived key đọc row rồi fuse | Ít arithmetic, nhiều static capacity; trả storage/bandwidth/collision | Local repeated patterns, predictable keys, memory tier có thể prefetch |

### 4.2 Những khái niệm dễ nhầm

**`Active` không phải `resident`.** Hai experts active không có nghĩa sáu experts còn lại biến mất khỏi GPU hoặc host. Placement quyết định resident set.

**`Accessed parameters` không phải FLOPs.** Đọc một embedding row gồm nhiều scalars nhưng gần như không nhân toàn bộ row như một matrix. Ngược lại, expert weight có thể được reuse cho nhiều routed tokens trong một GEMM.

**`Hash routing` không phải learned routing.** N-gram hash quyết định address từ IDs. Router MoE học scores từ hidden state. Collision trong hash table khác routing collapse: collision là nhiều keys chung row; collapse là learned traffic dồn vào ít experts.

**`Complete block` không phải expert FFN lớn hơn.** Block còn chứa token mixer, normalization và residual/projection logic. Routing nó thay đổi vị trí selection trong data flow.[^mol]

**`Offloaded` không phải miễn phí.** Host/NVMe table giảm accelerator residency nhưng thêm transfer và lookup path. SCONE explicitly chuyển added inference table ra off-accelerator; Engram đề xuất host prefetch và cache hierarchy, không chứng minh zero latency.[^scone][^engram]

### 4.3 Phần nào giữ nguyên, phần nào đổi

```text
Dense:   embedding → [mixer → FFN] → logits
MoE:     embedding → [mixer → ROUTED FFN] → logits
MoL:     embedding → [ROUTED (mixer → FFN) paths + shared path] → logits
Lookup:  embedding ─┬→ main blocks → logits
                    └→ key → table row → fuse tại input/intermediate layer
```

Output vocabulary và next-token objective có thể giữ nguyên trong cả ba. Sparse capacity là một module choice, không tự biến decoder-only model thành backbone khác.[^over-encoding][^scone][^engram]

## 5. Trong thực tế

### 5.1 Cơ chế nằm ở đâu trong model/system thật?

- **MoE:** thường thay FFN ở một số hoặc nhiều Transformer layers; experts có thể shard qua accelerator ranks.[^moe-systems]
- **Mixture of Layers:** một split stage có shared full-sequence block và nhiều routed thin blocks song song; report dùng routed Gated DeltaNet blocks.[^mol]
- **Over-Encoding/SCONE:** sửa input representation trước main Transformer.[^over-encoding][^scone]
- **Engram:** chèn lookup ở selected intermediate layers để hidden state đã contextualized có thể gate retrieved vector; table có thể shard khi training và được đề xuất prefetch từ host khi inference.[^engram]

### 5.2 Walkthrough deployment: trợ lý support có catalog phrases lớn

Giả sử workload có nhiều cụm lặp như product codes, error phrases và tên tính năng:

1. **Baseline:** đo dense model theo quality, prefill, decode, GPU memory và batch distribution.
2. **Nếu bottleneck là FFN compute/capacity:** thử MoE, nhưng đo expert load, capacity overflow, all-to-all time, GEMM utilization và total weight residency.
3. **Nếu cần conditional processing path sâu hơn:** thử whole-block routing only khi có kernel xử lý routed subsequences và global path; đo riêng mixer/FFN/dispatch.
4. **Nếu local phrases lặp lại và key biết từ token IDs:** hashed/frequent n-gram memory có thể phù hợp. Log unique n-grams, collision rate, hit rate, bytes per lookup, cache-tier hit, transfer overlap và quality theo phrase frequency.
5. **Nếu GPU không chứa table:** đặt table ở host chỉ khi prefetch lead time và bandwidth đáp ứng latency target. Placement là experiment, không phải hệ quả tự động của “static memory”.
6. **Ablation:** giữ backbone, training tokens và tổng budget càng matched càng tốt; đổi một sparse mechanism hoặc allocation axis mỗi lần.

### 5.3 Khi nào nên và không nên dùng

| Tình huống | Nên cân nhắc | Không nên vội dùng |
|---|---|---|
| Batch lớn, interconnect tốt, FFN chiếm phần lớn compute | MoE | Batch rất nhỏ, expert weights thường xuyên phải page-in |
| Muốn conditional mixer + FFN paths | Whole-block routing | Không có sparse block kernels hoặc task cần mọi block thấy toàn sequence |
| Nhiều local token patterns lặp lại, lookup address biết sớm | N-gram lookup memory | Tokenizer đổi thường xuyên, patterns hiếm, collision/host latency cao |
| GPU memory thiếu nhưng host RAM lớn | Offloaded static table có prefetch | Strict tail latency mà transfer không overlap ổn định |
| Cần arbitrary long-range fact retrieval | Không cơ chế nào ở đây tự bảo đảm | N-gram lookup chỉ encode local suffix; MoE/block routing không phải external retrieval |

### 5.4 Measurement bắt buộc

Đừng chỉ report một headline parameter count. Tối thiểu cần:

- `total`, `active`, `resident by tier`, `logical accessed`; nêu inclusion scope.
- Active FLOPs/MACs tách router, mixer, FFN, projection và fusion.
- Logical bytes và measured physical traffic; cache hit/miss, coalescing và prefetch overlap.
- Dispatch/combine latency, token counts per expert/block, padding/drop rate và slowest rank.
- Prefill và decode riêng; batch/concurrency, context, dtype, hardware và kernel version.
- Collision rate theo unique keys, key frequency và multi-head collision pattern.
- Quality trên matched budgets; component ablation thay vì suy causal từ whole-model benchmark.

### 5.5 Claim không thể suy ra chỉ từ lý thuyết

Không thể suy ra rằng nhiều total parameters sẽ tăng quality; lookup sẽ nhanh hơn GEMM; offload không tăng latency; whole-block routing tốt hơn MoE; hay active count thấp sẽ giảm GPU requirement. Những kết luận đó phụ thuộc model, data, placement, cache, kernels, batch và hardware.[^mol-evaluation][^moe-systems][^ngram-memory]

> [!success] Checkpoint trước toán
> Đến đây, người mới phải trả lời được: (1) bài toán là tăng conditional capacity; (2) MoE chọn FFN compute, block routing chọn complete path, lookup chọn stored rows; (3) mỗi loại đổi compute/memory/dispatch khác nhau; (4) khác dense ở vị trí selector và khác nhau ở selected unit; (5) chỉ dùng khi workload và measurement xác nhận bottleneck tương ứng. Phần toán dưới đây chỉ làm chính xác các ledger đó.

## 6. Toán học — zoom in sau cùng

### 6.1 Bảng ký hiệu

| Ký hiệu | Ý nghĩa | Shape hoặc đơn vị |
|---|---|---|
| $B,T,D$ | batch, sequence length, hidden width | số nguyên |
| $N_E,k_E$ | số FFN experts và số experts chọn mỗi token | số nguyên |
| $P_E$ | parameters trong một expert FFN | scalars |
| $N_L,k_L$ | số routed blocks và số blocks chọn mỗi token | số nguyên |
| $P_L$ | parameters trong một complete thin block | scalars |
| $R_n$ | số rows của table cho n-gram order $n$ | rows |
| $D_m$ | width của một memory row | scalars/row |
| $q$ | bytes mỗi scalar theo dtype | bytes |
| $U_n,C_n$ | unique n-gram keys và collision count quan sát được | counts |
| $P_{total}$ | mọi learned scalars thuộc scope | scalars |
| $P_{active}$ | selected computation parameters trong scope/token | scalars/token |
| $P_{resident}^{tier}$ | parameters nằm ở một memory tier | scalars |
| $P_{accessed}$ | logical selected weights/rows được đọc | scalars/token |

### 6.2 Trường hợp nhỏ nhất tính tay: tám experts, top-2

**Trực giác.** Có tám FFNs bằng nhau nhưng token chỉ gọi hai. Capacity tăng theo tám, selected compute tăng theo hai.

**Công thức.**

$$
P_{expert,total}=N_E P_E,
\qquad
P_{expert,active/token}=k_E P_E.
$$

**Ý nghĩa ký hiệu.** $N_E$ là toàn expert bank; $k_E$ là số selected experts; $P_E$ là parameters của một expert.

**Shape flow.** Hidden token có shape $(D)$; router tạo scores $(N_E)$; top-k tạo IDs $(k_E)$; mỗi selected FFN nhận $(D)$ và trả $(D)$.

**Ví dụ số.** Nếu mỗi expert có 100 triệu parameters, tám experts cho 800 triệu total; top-2 cho 200 triệu expert-active parameters/token. Router, attention và dense components chưa nằm trong hai số này.

**Kết luận.** Active expert count không phải model-active count và không cho biết residency.

### 6.3 FFN parameters và active arithmetic

**Trực giác.** Một two-linear-layer FFN đọc hai matrices và thực hiện matrix-vector products; parameters và multiply-add work có cùng bậc nhưng không phải cùng đơn vị.

**Công thức.** Bỏ qua biases, với intermediate width $D_f$:

$$
P_E \approx 2DD_f,
\qquad
\operatorname{FLOPs}_{MoE/token}\approx k_E\,4DD_f.
$$

Quy ước ở đây đếm một multiply-add là hai FLOPs.

**Ý nghĩa ký hiệu.** Hai matrices lần lượt map hidden width sang intermediate width và quay lại; hệ số bốn đến từ hai matrices nhân với hai FLOPs mỗi multiply-add.

**Shape flow.** $(D)\rightarrow(D_f)\rightarrow(D)$ cho mỗi selected expert.

**Ví dụ số.** Với hidden width 16, intermediate width 64, một expert có xấp xỉ 2,048 matrix parameters và khoảng 4,096 FLOPs/token. Top-2 dùng khoảng 8,192 expert FLOPs, chưa tính activation, router và combine.

**Kết luận.** `Active parameters` có thể là proxy thô cho linear compute trong FFN, nhưng không thay thế profiler.

### 6.4 Complete-block routing

**Trực giác.** Selected unit lớn hơn expert: nó chứa projection, mixer và FFN, nên ledger phải cộng từng phần.

**Công thức.** Với một thin block gồm down/up projections, mixer và FFN:

$$
P_L=P_{down/up}+P_{mixer}+P_{ffn},
\qquad
P_{block,active/token}=k_LP_L+P_{shared}.
$$

Nếu shared block luôn active thì nó phải được cộng riêng, không được giấu trong top-k.

**Ý nghĩa ký hiệu.** $P_{shared}$ là full-sequence path luôn chạy; $P_L$ là một routed complete block.

**Shape flow.** Residual $(D)$ đi xuống thin width, qua mixer và FFN, rồi lên lại $(D)$. Router chọn $k_L$ block deltas để combine.

**Ví dụ số.** Nếu mỗi routed block có 30 triệu parameters, top-2 dùng 60 triệu routed-block parameters/token. Một shared block 50 triệu làm active scope thành 110 triệu; gọi cấu hình này “60 triệu active” sẽ bỏ sót shared path.

**Kết luận.** So sánh MoE và block routing phải match selected unit, không chỉ match top-k.

### 6.5 Hashed n-gram lookup và collision

**Trực giác.** Direct n-gram address space tăng rất nhanh, nên hash ép nhiều possible keys vào bảng hữu hạn. Collision quan sát được là số unique keys vượt số unique rows chúng chiếm.

**Công thức.** Với một deterministic hash $H_n$:

$$
r_{t,n}=H_n(x_{t-n+1},\ldots,x_t)\bmod R_n,
\qquad
C_n=U_n-\left|\{r_{t,n}:\text{unique observed keys}\}\right|.
$$

Một collision rate đơn giản trong observed batch là

$$
\rho_n=\frac{C_n}{\max(U_n,1)}.
$$

**Ý nghĩa ký hiệu.** $R_n$ là table rows; $U_n$ chỉ đếm unique keys quan sát được; $C_n$ không phải expected global collision trên toàn language.

**Shape flow.** Token IDs $(B,T)$ tạo row IDs $(B,T)$ cho mỗi order; embedding lookup trả $(B,T,D_m)$; nhiều orders được sum hoặc concatenate/project.

**Ví dụ số.** Ba unique bigrams hash vào rows `[2, 2, 5]`. Chỉ hai unique rows được dùng, nên collision count là một và observed rate là một phần ba.

**Kết luận.** Report collision phải gắn với key set, hash heads, table sizes và counting convention.

### 6.6 Total, resident và accessed cho lookup table

**Trực giác.** Table có thể rất lớn nhưng mỗi token chỉ lấy một row cho mỗi n-gram order. Total storage và logical bytes/token vì vậy scale theo hai trục khác nhau.

**Công thức.** Với set orders $\mathcal N$:

$$
P_{lookup,total}=\sum_{n\in\mathcal N}R_nD_m,
\qquad
P_{lookup,accessed/token}=|\mathcal N|D_m,
$$

$$
M_{logical/token}=q|\mathcal N|D_m.
$$

Placement phải thỏa

$$
P_{lookup,total}=P_{resident}^{GPU}+P_{resident}^{host}+P_{resident}^{storage},
$$

nếu mỗi parameter chỉ được đếm ở một tier; replication phải được ghi thành physical copies riêng.

**Ý nghĩa ký hiệu.** Logical bytes giả sử một row/order/token và bỏ qua cache reuse, index metadata, transfer granularity, projection weights và writes.

**Shape flow.** Mỗi order trả một row $(D_m)$; ba orders trả ba rows trước fusion.

**Ví dụ số.** Hai tables, mỗi table một triệu rows, row width 128, BF16 hai bytes: total table storage khoảng 512 MB; mỗi token đọc logical 512 bytes cho hai rows. Physical traffic có thể thấp hơn do cache hit hoặc cao hơn do transaction granularity.

**Kết luận.** Ít accessed rows không làm total table biến mất; residency và bandwidth là ledgers riêng.

### 6.7 General accounting ledger

**Trực giác.** Một architecture thực thường compose dense backbone, sparse module, router/indexer và shared paths.

**Công thức tổng quát.** Với component set $\mathcal C$:

$$
P_{total}=\sum_{c\in\mathcal C}P_c,
\qquad
P_{active/token}=\sum_{c\in\mathcal C}a_cP_c,
$$

trong đó $a_c$ là một nếu component luôn active, gate indicator nếu selected, hoặc expected activation fraction khi report trung bình. Memory traffic và FLOPs phải tính bằng hai hàm riêng:

$$
M_{access}=\sum_c \operatorname{BytesRead}(c),
\qquad
F_{active}=\sum_c \operatorname{FLOPs}(c).
$$

**Shape flow.** Mỗi component phải ghi input/output, selector output và dispatch unit; nếu shape không rõ thì active count khó audit.

**Ví dụ số.** Một token có dense backbone 40 triệu active parameters, top-2 experts mỗi expert 10 triệu và hai lookup rows tổng 256 scalars. Active-parameter headline gần 60 triệu, nhưng lookup traffic phải tính theo 256 scalars và expert FLOPs theo matrices; không cộng hai con số rồi gọi đó là cost.

**Kết luận.** Parameter count là inventory; FLOPs là arithmetic; bytes là traffic; latency là measured outcome.

## 7. Implementation — PyTorch tối thiểu

Code dưới cụ thể hóa đúng ba data flows đã giải thích. Nó dùng Python loops để dễ inspect, không có capacity, distributed dispatch, fused kernels, asynchronous prefetch hay production cache.

```python
from dataclasses import dataclass
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class CollisionStats:
    unique_keys: int
    unique_rows: int
    collisions: int
    rate: float


def stable_ngram_hash(ids: Tuple[int, ...], seed: int = 17) -> int:
    """Deterministic toy hash; không dùng Python hash ngẫu nhiên theo process."""
    h = seed
    for token_id in ids:
        h = (h * 1_000_003) ^ (token_id + 0x9E3779B9)
        h &= (1 << 63) - 1
    return h


class HashedNGramLookup(nn.Module):
    """Một table cho mỗi order; left-pad bằng pad_id ở đầu sequence."""
    def __init__(
        self,
        vocab_size: int,
        d_model: int,
        orders: Tuple[int, ...] = (2, 3),
        rows_per_order: Tuple[int, ...] = (101, 103),
        pad_id: int = 0,
    ):
        super().__init__()
        if len(orders) != len(rows_per_order):
            raise ValueError("orders and rows_per_order must have equal length")
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.orders = orders
        self.rows_per_order = rows_per_order
        self.pad_id = pad_id
        self.tables = nn.ModuleList(
            [nn.Embedding(rows, d_model) for rows in rows_per_order]
        )

    def row_ids_and_keys(self, token_ids: torch.Tensor, order: int, rows: int):
        if token_ids.ndim != 2:
            raise ValueError("token_ids must have shape (B, T)")
        B, T = token_ids.shape
        row_ids = torch.empty(B, T, dtype=torch.long, device=token_ids.device)
        keys: List[Tuple[int, ...]] = []
        # .item() và Python loop là teaching path, không phải serving kernel.
        for b in range(B):
            for t in range(T):
                key = tuple(
                    self.pad_id if j < 0 else int(token_ids[b, j].item())
                    for j in range(t - order + 1, t + 1)
                )
                keys.append(key)
                row_ids[b, t] = stable_ngram_hash(key) % rows
        return row_ids, keys

    def forward(self, token_ids: torch.Tensor):
        per_order = []
        metadata = []
        for order, rows, table in zip(
            self.orders, self.rows_per_order, self.tables
        ):
            row_ids, keys = self.row_ids_and_keys(token_ids, order, rows)
            per_order.append(table(row_ids))  # (B, T, D)

            key_to_row = {
                key: stable_ngram_hash(key) % rows for key in set(keys)
            }
            unique_keys = len(key_to_row)
            unique_rows = len(set(key_to_row.values()))
            collisions = unique_keys - unique_rows
            metadata.append(
                CollisionStats(
                    unique_keys=unique_keys,
                    unique_rows=unique_rows,
                    collisions=collisions,
                    rate=collisions / max(unique_keys, 1),
                )
            )

        # Toy fusion: sum. Engram dùng projection/gate phức tạp hơn.
        return torch.stack(per_order, dim=0).sum(dim=0), metadata

    def logical_bytes_per_token(self) -> int:
        element_bytes = next(self.parameters()).element_size()
        return len(self.orders) * self.d_model * element_bytes


class ExpertFFN(nn.Module):
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.fc1 = nn.Linear(d_model, d_ff)
        self.fc2 = nn.Linear(d_ff, d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.fc2(F.gelu(self.fc1(x)))


class ToyMoE(nn.Module):
    """Chỉ route FFN; mixer/attention nằm ngoài module này."""
    def __init__(self, d_model: int, d_ff: int, n_experts: int, k: int = 1):
        super().__init__()
        self.k = k
        self.router = nn.Linear(d_model, n_experts)
        self.experts = nn.ModuleList(
            [ExpertFFN(d_model, d_ff) for _ in range(n_experts)]
        )

    def forward(self, x: torch.Tensor):
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(x.dtype)
        gates, expert_ids = probs.topk(self.k, dim=-1)
        out = torch.zeros_like(tokens)
        for expert_id, expert in enumerate(self.experts):
            token_rows, slots = torch.where(expert_ids == expert_id)
            if token_rows.numel() == 0:
                continue
            delta = expert(tokens[token_rows])
            out.index_add_(
                0, token_rows, gates[token_rows, slots, None] * delta
            )
        loads = torch.bincount(
            expert_ids.reshape(-1), minlength=len(self.experts)
        )
        return out.reshape(B, T, D), probs, expert_ids, loads


class ToyCompleteBlock(nn.Module):
    """Complete toy path = causal token mixer + FFN, cùng residual width."""
    def __init__(self, d_model: int, d_ff: int):
        super().__init__()
        self.mix_norm = nn.LayerNorm(d_model)
        self.mix_proj = nn.Linear(d_model, d_model)
        self.ffn_norm = nn.LayerNorm(d_model)
        self.ffn = ExpertFFN(d_model, d_ff)

    def forward(self, routed_sequence: torch.Tensor) -> torch.Tensor:
        # routed_sequence: (N_routed, D), đã giữ original token order.
        z = self.mix_norm(routed_sequence)
        denom = torch.arange(
            1, z.shape[0] + 1, device=z.device, dtype=z.dtype
        )[:, None]
        causal_mean = z.cumsum(dim=0) / denom
        h = routed_sequence + self.mix_proj(causal_mean)
        return h + self.ffn(self.ffn_norm(h))


class ToyWholeBlockRouter(nn.Module):
    """Top-1 route complete blocks; output là selected block delta + residual."""
    def __init__(self, d_model: int, d_ff: int, n_blocks: int):
        super().__init__()
        self.router = nn.Linear(d_model, n_blocks)
        self.blocks = nn.ModuleList(
            [ToyCompleteBlock(d_model, d_ff) for _ in range(n_blocks)]
        )

    def forward(self, x: torch.Tensor):
        B, T, D = x.shape
        tokens = x.reshape(B * T, D)
        probs = F.softmax(self.router(tokens.float()), dim=-1).to(x.dtype)
        gates, block_ids = probs.max(dim=-1)
        delta = torch.zeros_like(tokens)

        for block_id, block in enumerate(self.blocks):
            rows = torch.where(block_ids == block_id)[0]
            if rows.numel() == 0:
                continue
            # rows tăng dần nên giữ original flattened token order.
            block_out = block(tokens[rows])
            block_delta = block_out - tokens[rows]
            delta.index_add_(0, rows, gates[rows, None] * block_delta)

        loads = torch.bincount(block_ids, minlength=len(self.blocks))
        return (tokens + delta).reshape(B, T, D), probs, block_ids, loads


def nparams(module: nn.Module) -> int:
    return sum(p.numel() for p in module.parameters())


def sparse_ledger(
    lookup: HashedNGramLookup,
    moe: ToyMoE,
    block_router: ToyWholeBlockRouter,
) -> Dict[str, Dict[str, int]]:
    expert_params = nparams(moe.experts[0])
    block_params = nparams(block_router.blocks[0])
    lookup_total = sum(table.weight.numel() for table in lookup.tables)
    return {
        "lookup": {
            "total_params": lookup_total,
            "accessed_params_per_token": len(lookup.orders) * lookup.d_model,
            "logical_bytes_per_token": lookup.logical_bytes_per_token(),
        },
        "moe": {
            "total_expert_params": nparams(moe.experts),
            "active_expert_params_per_token": moe.k * expert_params,
            "router_params": nparams(moe.router),
        },
        "whole_block": {
            "total_routed_block_params": nparams(block_router.blocks),
            "active_block_params_per_token": block_params,  # top-1 toy
            "router_params": nparams(block_router.router),
        },
    }
```

### 7.1 Chạy toy example xuyên suốt

```python
torch.manual_seed(7)

# IDs tượng trưng: [New, York, pizza, is, great]
token_ids = torch.tensor([[1, 2, 3, 4, 5]])
x = torch.randn(1, 5, 8)

lookup = HashedNGramLookup(
    vocab_size=32,
    d_model=8,
    orders=(2, 3),
    rows_per_order=(11, 13),
)
moe = ToyMoE(d_model=8, d_ff=16, n_experts=4, k=2)
block_router = ToyWholeBlockRouter(d_model=8, d_ff=16, n_blocks=3)

memory_delta, collision_stats = lookup(token_ids)
moe_delta, moe_probs, expert_ids, expert_loads = moe(x)
block_out, block_probs, block_ids, block_loads = block_router(x)

print("collision stats:", collision_stats)
print("MoE expert IDs:", expert_ids.reshape(1, 5, 2))
print("block IDs:", block_ids.reshape(1, 5))
print("ledger:", sparse_ledger(lookup, moe, block_router))

# Một fusion tối giản để minh họa placement trong model, không phải Engram.
x_with_memory = x + memory_delta
assert x_with_memory.shape == x.shape
assert moe_delta.shape == x.shape
assert block_out.shape == x.shape
```

Lookup code là toy-explicit: production sẽ vectorize hashing, batch/coalesce reads và có cache hierarchy. Whole-block code flatten cả batch nên không được dùng để mix nhiều independent sequences trong production; lab dùng batch một để semantics rõ ràng.

## 8. Verification — xác minh trước benchmark

### 8.1 Test 1 — deterministic lookup và shape

```python
torch.manual_seed(11)
lookup = HashedNGramLookup(
    vocab_size=16, d_model=4, orders=(2,), rows_per_order=(7,)
)
ids = torch.tensor([[1, 2, 3, 2]])
y1, stats1 = lookup(ids)
y2, stats2 = lookup(ids.clone())

assert y1.shape == torch.Size([1, 4, 4])
torch.testing.assert_close(y1, y2, rtol=0, atol=0)
assert stats1 == stats2
```

Cùng IDs phải tạo cùng rows và vectors. Test dùng exact equality vì không có nondeterministic arithmetic trong lookup path.

### 8.2 Test 2 — collision accounting với table một row

```python
lookup_one_row = HashedNGramLookup(
    vocab_size=16, d_model=4, orders=(2,), rows_per_order=(1,)
)
_, stats = lookup_one_row(torch.tensor([[1, 2, 3, 4]]))

# Bốn observed padded bigram keys, tất cả vào cùng một row.
assert stats[0].unique_keys == 4
assert stats[0].unique_rows == 1
assert stats[0].collisions == 3
torch.testing.assert_close(
    torch.tensor(stats[0].rate), torch.tensor(0.75), rtol=0, atol=0
)
```

Test cố ý dùng pathological table để collision có kết quả tính tay. Nó không dự đoán collision của table lớn.

### 8.3 Test 3 — logical bytes và parameter inventory

```python
lookup = HashedNGramLookup(
    vocab_size=16,
    d_model=8,
    orders=(2, 3),
    rows_per_order=(11, 13),
)
expected_total = (11 + 13) * 8
assert sum(t.weight.numel() for t in lookup.tables) == expected_total
assert lookup.logical_bytes_per_token() == 2 * 8 * 4  # float32
```

Nếu đổi module sang BF16, expected bytes/token đổi từ 64 thành 32. Đây là logical row payload, không phải measured HBM/PCIe traffic.

### 8.4 Test 4 — MoE load và manual selected-expert match

```python
torch.manual_seed(13)
moe = ToyMoE(d_model=4, d_ff=8, n_experts=3, k=1)
x = torch.randn(1, 3, 4)
y, probs, ids, loads = moe(x)

assert loads.sum().item() == 3
assert ids.shape == torch.Size([3, 1])
torch.testing.assert_close(
    probs.sum(dim=-1), torch.ones(3), rtol=0, atol=1e-6
)

# Manual reference cho từng token, đúng selected expert và raw gate.
manual = []
flat = x.reshape(3, 4)
for row in range(3):
    expert_id = int(ids[row, 0].item())
    gate = probs[row, expert_id]
    selected_expert = moe.experts[expert_id]
    manual.append(gate * selected_expert(flat[row : row + 1]))
manual = torch.cat(manual, dim=0).reshape_as(y)
torch.testing.assert_close(y, manual, rtol=1e-5, atol=1e-6)
```

### 8.5 Test 5 — whole-block router thực sự route mixer + FFN

```python
torch.manual_seed(17)
router = ToyWholeBlockRouter(d_model=4, d_ff=8, n_blocks=2)
x = torch.randn(1, 4, 4)

# Force mọi token sang block 0; gate tiến gần 1 nhưng vẫn lấy đúng probs.
with torch.no_grad():
    router.router.weight.zero_()
    router.router.bias.copy_(torch.tensor([20.0, -20.0]))

y, probs, block_ids, loads = router(x)
assert torch.equal(block_ids, torch.zeros(4, dtype=torch.long))
assert loads.tolist() == [4, 0]

flat = x.reshape(4, 4)
selected_block = router.blocks[0]
full_block = selected_block(flat)
gate = probs[:, 0:1]
manual = flat + gate * (full_block - flat)
torch.testing.assert_close(y.reshape(4, 4), manual, rtol=1e-5, atol=1e-6)
```

Nếu implementation chỉ route FFN mà bỏ causal mixer, test reference này sẽ không còn match.

### 8.6 Test 6 — causal mixer không leak future trong cùng routed subsequence

```python
torch.manual_seed(19)
block = ToyCompleteBlock(d_model=4, d_ff=8)
x = torch.randn(5, 4)
y = block(x)

x_changed = x.clone()
x_changed[4] += 100.0
y_changed = block(x_changed)

torch.testing.assert_close(
    y[:4], y_changed[:4], rtol=1e-5, atol=1e-6
)
```

Dtype mặc định của tests là float32. Với BF16/FP16, tăng tolerance có lý do và report dtype; không copy tolerance mù quáng.

## 9. Benchmark và trade-offs

### 9.1 Microbenchmark scaffold

Đo từng path riêng, warm-up trước và synchronize khi dùng CUDA:

```python
import time


def bench_ms(fn, warmup=10, iters=50):
    for _ in range(warmup):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    start = time.perf_counter()
    for _ in range(iters):
        fn()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    return 1_000 * (time.perf_counter() - start) / iters


# Ví dụ; toy Python loops chủ yếu benchmark overhead, không phải architecture.
print("lookup ms:", bench_ms(lambda: lookup(token_ids)))
print("moe ms:", bench_ms(lambda: moe(x)))
print("block ms:", bench_ms(lambda: block_router(x)))
```

Không so ba số này như production throughput: module làm lượng semantic work khác nhau và toy paths chưa optimized.

### 9.2 Bảng metric cần report

| Metric | MoE | Whole-block routing | Lookup memory |
|---|---|---|---|
| `total` | toàn expert bank + router | toàn routed/shared blocks + router | mọi table rows + projection/gate |
| `active` | selected experts + always-on paths | selected blocks + shared block | fusion components; rows nên ghi `accessed` riêng |
| `resident` | weights theo device/rank | block weights theo device/rank | table rows theo GPU/host/storage tier |
| `accessed` | selected expert weights, có reuse theo routed batch | selected block weights | unique/logical rows và cache-tier hits |
| FLOPs | router + selected FFNs | router + selected mixers/FFNs/projections | hash/index + projection/gate/fusion |
| Bytes | activation dispatch + weight reads | subsequence dispatch + block reads/state | row payload + metadata + transfer granularity |
| Health | loads, overflow, drop, rank skew | block loads, subsequence lengths, global-path use | collision, hit/miss, key frequency, prefetch miss |

### 9.3 Evidence-bounded trade-offs

| Claim | Evidence hiện có | Không được kết luận |
|---|---|---|
| MoE giảm selected expert FFN compute | Mechanism và systems synthesis; dispatch/residency caveats được document[^moe-systems] | End-to-end latency luôn giảm |
| MoL route complete thin blocks | Author preprint document down/up, mixer, FFN, shared softmax path[^mol] | Mọi whole-block router đều có cùng design hoặc quality |
| MoL có long-context prefill gains trong một số measurements | Single-preprint, hardware/context-specific measurements; measured decode chậm hơn trong tested implementation[^mol-evaluation] | Universal crossover hoặc production decode gain |
| Hashed lookup thêm sparse local-pattern capacity | Primary-source-backed Over-Encoding/Engram concepts[^over-encoding][^engram] | Collision vô hại hoặc local pattern đủ cho global retrieval |
| Static table có thể offload | SCONE materializes inference table off-accelerator; Engram đề xuất prefetch/cache hierarchy[^scone][^engram] | Transfer luôn được ẩn hoàn toàn |

### 9.4 Benchmark protocol tối thiểu

1. Match backbone, tokens, optimizer và quality target khi có thể.
2. Report cả iso-active và iso-total; hai baseline trả lời câu hỏi khác nhau.
3. Tách training, prefill và decode; tách batch một khỏi high concurrency.
4. Profile router/hash, packing, dispatch, compute, combine/fusion và memory transfer.
5. Với lookup, sweep table rows và log collision theo key frequency; với router, sweep top-k và log load/capacity.
6. Report physical residency, replication và peak memory, không chỉ checkpoint parameter count.
7. Lặp nhiều seeds cho quality; report tail latency cho serving.

## 10. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| “Active nhỏ” nhưng OOM khi load | Total weights vẫn resident/replicated | In parameter inventory theo device và memory tier |
| FLOPs giảm nhưng latency tăng | Dispatch, small GEMM, random lookup hoặc sync | Profile timeline; tách selector/dispatch/compute/combine |
| Một expert/block nhận gần hết tokens | Routing collapse hoặc biased data | Histogram loads theo batch/layer/rank |
| Nhiều dropped tokens | Capacity thấp hoặc imbalance | Offered load, accepted load, capacity và drop rate |
| Lookup quality giảm khi table nhỏ | Collision hoặc insufficient capacity | Unique keys, unique rows, collisions theo order/head |
| Collision count thay đổi giữa runs | Dùng Python `hash()` hoặc nondeterministic preprocessing | Dùng deterministic hash và snapshot normalized IDs |
| Host table làm tail latency xấu | Prefetch miss hoặc transfer không overlap | Cache-tier hit, bytes/request, PCIe/NVLink timeline |
| Whole-block output sai theo batch | Toy flatten trộn independent sequences | Route/mix từng sequence; giữ batch boundaries |
| Earlier token đổi khi sửa future token | Mixer/mask không causal hoặc order scatter sai | Future-perturbation test trước benchmark |
| Ledger cộng lookup rows vào FLOPs như FFN weights | Trộn inventory, traffic và arithmetic | Viết ba cột parameters/FLOPs/bytes riêng |

## 11. Giới hạn và bước tiếp theo

### 11.1 Lab không chứng minh gì?

- Toy hash không tái tạo multiplicative-XOR multi-head hashing, tokenizer normalization, causal convolution hay contextual gate của Engram.[^engram]
- Toy whole block không tái tạo Mixture of Layers: không có thin down/up projections, Gated DeltaNet, shared softmax block, CV-squared balance loss hay distributed placement.[^mol]
- Python loops làm benchmark phản ánh interpreter overhead nhiều hơn sparse kernel quality.
- Logical bytes bỏ qua cache lines, indices, allocator, metadata, coalescing, replication và writes.
- Parameter/FLOP formulas là accounting approximations; target hardware cần profiler và end-to-end measurements.
- Course không chứng minh quality ranking giữa MoE, block routing và lookup memory.

### 11.2 Bước tiếp theo

1. Thêm `capacity factor`, dropped assignments và balance metrics từ [MoE capacity lab](moe-capacity-load-balancing-stability-lab.md).
2. Mô phỏng device placement/all-to-all theo [Expert parallelism và serving trade-offs](expert-parallelism-serving-trade-offs-beginners-guide.md).
3. Thay one-head table bằng nhiều hash heads với prime-sized subtables; report per-head và joint collisions.
4. Thêm LRU cache mô phỏng GPU/host tiers; đo hit rate và bytes transferred thay vì chỉ logical payload.
5. Đọc source-specific evaluation pages trước khi chọn architecture cho workload thật.

## Relationships

- **Depends on:** [Mixture-of-Experts và sparse routing](mixture-of-experts-sparse-routing-beginners-guide.md) — baseline cho routed FFN compute và top-k.
- **Uses:** [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md) — taxonomy và systems boundary của sparse local-pattern lookup.
- **Uses:** [Engram conditional-memory architecture](engram-conditional-memory-architecture.md), [SCONE](scone-scalable-contextualized-offloaded-n-gram-embeddings.md) và [Over-Encoding](over-encoding-hierarchical-n-gram-input-embeddings.md) — ba placement/fusion variants.
- **Uses:** [Mixture of Layers block routing](mixture-of-layers-block-routing.md) — complete-block routing khác FFN-only routing.
- **Prepares for:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — capacity, balance, all-to-all và residency.
- **Elaborates:** Stage 7.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Đây là synthesis sư phạm từ maintained wiki concepts. Mixture of Layers evidence đến từ một author preprint chưa được independent replication trong kho; MoE systems page còn phụ thuộc một secondary overview cho Switch-specific details; concept N-gram tổng hợp có cả primary-source-backed variants và phần research line chưa được kiểm độc lập. Công thức ledger và toy implementation là synthesis có thể inspect, không phải benchmark claim. Mọi kết luận về quality, physical bytes, throughput, tail latency, optimal placement hoặc scalability phải được xác minh trên target model, tokenizer, dtype, workload, runtime và hardware.[^mol-evaluation][^moe-systems][^ngram-memory]

[^ngram-memory]: [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md), mechanism, design line, capacity/systems trade-offs và evidence limits; synthesis này phân biệt lookup feature với classical n-gram LM và routed MoE.
[^engram]: [Engram conditional-memory architecture](engram-conditional-memory-architecture.md), lookup keys, contextual fusion, storage/execution boundary và evidence limits; primary author-paper evidence được concept biên dịch.
[^scone]: [SCONE scalable contextualized offloaded n-gram embeddings](scone-scalable-contextualized-offloaded-n-gram-embeddings.md), input representation, training parameterization và inference offload boundary; primary author-paper evidence được concept biên dịch.
[^over-encoding]: [Over-Encoding hierarchical n-gram input embeddings](over-encoding-hierarchical-n-gram-input-embeddings.md), hashed input construction, retained output vocabulary và collision/system limits; primary author-paper evidence được concept biên dịch.
[^mol]: [Mixture of Layers block routing](mixture-of-layers-block-routing.md), thin-block split stage, hybrid attention, sparse dispatch và evidence limits; single author preprint.
[^mol-evaluation]: [Mixture of Layers evaluation and serving trade-offs](mixture-of-layers-evaluation-and-serving-trade-offs.md), iso-active/iso-total quality, training, prefill, decode và hardware limits; author-reported, unreplicated evidence.
[^moe-course]: [Mixture-of-Experts và sparse routing — bài học cho người mới](mixture-of-experts-sparse-routing-beginners-guide.md), beginner synthesis of routed FFN, total/active accounting and toy top-k routing.
[^moe-systems]: [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), capacity, balancing, all-to-all, residency and operational limits; mixed primary and secondary evidence as documented there.
