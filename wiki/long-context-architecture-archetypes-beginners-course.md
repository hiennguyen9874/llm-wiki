---
type: Synthesis
title: "Long-context architecture archetypes: token retrieval, compressed entries, và recurrent hybrids — khóa học cho người mới"
description: A top-down beginner course comparing attention-centric token retrieval (GLM-style MLA/DSA), compressed-entry retrieval (DeepSeek-V4-style CSA/HCA), and recurrent-majority hybrids (Kimi-K3-style KDA plus periodic MLA) under matched addressability, state-growth, locality, and indexer dimensions.
tags: [long-context, attention, sparse-attention, hybrid-attention, kv-cache, learning-roadmap, pytorch]
status: stable
created: 2026-09-02
generated:
  by: llm-wiki-agent/1
  at: 2026-09-02T12:04:05+07:00
sources:
  - id: sparse-evolution
    resource: sparse-attention-evolution-and-architecture-comparison.md
    title: Sparse Attention evolution and architecture comparison
  - id: v4-k3-comparison
    resource: deepseek-v4-and-kimi-k3-architecture-comparison.md
    title: DeepSeek-V4 and Kimi K3 architecture comparison
  - id: glm5-k3-comparison
    resource: glm-5-and-kimi-k3-architecture-comparison.md
    title: GLM-5 and Kimi K3 architecture comparison
  - id: csa-hca
    resource: compressed-sparse-and-heavily-compressed-attention.md
    title: Compressed sparse and heavily compressed attention
  - id: dsa-concept
    resource: deepseek-sparse-attention.md
    title: DeepSeek Sparse Attention
  - id: mla-concept
    resource: multi-head-latent-attention.md
    title: Multi-head Latent Attention
  - id: kda-concept
    resource: delta-rule-and-gated-associative-memory.md
    title: Delta-rule and gated associative memory
  - id: k3-arch
    resource: kimi-k3-hybrid-retrieval-architecture.md
    title: Kimi K3 hybrid retrieval architecture
  - id: v4-arch
    resource: deepseek-v4-hybrid-architecture-and-pretraining.md
    title: DeepSeek-V4 hybrid architecture and pretraining
  - id: workload-selection
    resource: workload-conditioned-frontier-llm-architecture-selection.md
    title: Workload-conditioned frontier LLM architecture selection
---

# Long-context architecture archetypes: token retrieval, compressed entries, và recurrent hybrids — khóa học cho người mới

Các model dài ngữ cảnh triệu token không phân chia theo "tên hãng" mà theo **mô hình bộ nhớ**: history được lưu dưới dạng gì và query đọc nó bằng cách nào. Bài này tách ba `archetype` đang thống trị frontier — **attention-centric token retrieval** (GLM-style MLA/DSA), **compressed-entry retrieval** (DeepSeek-V4-style CSA/HCA), và **recurrent-majority hybrid** (Kimi-style KDA cộng periodic MLA) — rồi so chúng trên cùng bốn chiều: `addressability`, `state growth`, `read locality`, và `indexer`. Mỗi archetype được trace bằng **cùng một remote fact** từ lúc ghi vào lúc đọc ra, sau đó mới zoom vào công thức, PyTorch toy, và verification.[^glm5-k3-comparison][^v4-k3-comparison][^sparse-evolution]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Giải thích được ba archetype giải quyết vấn đề gì: giữ chi phí đọc/lưu history thấp khi context dài, nhưng bằng ba câu trả lời khác nhau cho câu hỏi "lưu gì và đọc gì".
> 2. Trace được một remote fact qua từng archetype: nó được lưu ở đâu, query đọc gì, khi nào copy chính xác được, và failure mode khi không.
> 3. So sánh ba archetype với dense baseline bằng `archetype matrix` trên `addressability` — `state growth` — `locality` — `indexer`, phân biệt hệ quả trực tiếp của thiết kế với benchmark number.
> 4. Chạy được PyTorch toy của cả ba đường: top-k token retrieval, compressed entries cộng local window, và delta-rule fixed state cộng periodic global read.
> 5. Kiểm chứng bằng `torch.testing.assert_close`: slot-level addressability, mất token identity trong group, state cố định của KDA, và state-growth ledger.

## 1. Điều cần biết trước

- [Attention: beginner's guide](attention-beginner-guide.md): Q/K/V, softmax, causal mask.
- [MLA và token-addressable memory — bài học cho người mới](mla-token-addressable-memory-beginners-guide.md): nén KV **mỗi token** vẫn khác group compression và fixed state.
- [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md) và [Delta memory, KDA, hybrid KDA–MLA](delta-memory-kda-hybrid-architecture-beginners-project.md): bộ nhớ associative cố định và delta correction.
- [Sparse-attention architecture — khóa học cho người mới](sparse-attention-architecture-beginners-course.md): chuỗi từ local mask đến compressed entries; bài này đứng "một tầng cao hơn" và so các nhánh với nhau.
- [Kimi K3 theo information path](kimi-k3-integrated-architecture-information-path-beginners-course.md) và [Comparative reading và evidence discipline](comparative-reading-evidence-discipline-beginners-course.md): cách đọc một model tích hợp và kỷ luật evidence.

Không phủ trong bài: kernel CUDA/Triton, distributed context parallelism, training recipe của từng checkpoint, residual-path và MoE chi tiết (được nhắc như trục phụ để tránh hiểu nhầm).

## 2. Bức tranh toàn cảnh

### 2.1 Vấn đề: history dài, và ba câu trả lời khác nhau cho cùng một câu hỏi

Dense causal attention cho mỗi query đọc trực tiếp mọi token trước nó. Đó là baseline mạnh nhất về retrieval — một chi tiết ở vị trí bất kỳ vẫn có slot riêng — nhưng khi context lên hàng triệu token thì có hai áp lực: **chi phí đọc** (mỗi query phải chạm toàn bộ prefix) và **chi phí lưu** (mỗi token được giữ lại một entry K/V trên mỗi layer, nên state tăng theo context và theo chiều sâu model).[^sparse-evolution]

Mọi kiến trúc long-context hiện đại đều trả lời chung một câu hỏi: **"history nên được lưu dưới dạng gì, và query nên đọc nó bằng cách nào?"** — và frontier đang tụ họp thành ba câu trả lời khác nhau. Người mới hay nhầm vì đọc theo tên model: "Kimi dùng MLA", "DeepSeek dùng sparse" — nhưng hai model cùng nhắc MLA có thể nằm ở hai archetype khác nhau, vì vai trò của MLA (core mọi layer, hay checkpoint định kỳ) mới là thứ quyết định hành vi.[^glm5-k3-comparison][^v4-k3-comparison]

### 2.2 Ý tưởng cốt lõi trong một câu

**Ba archetype khác nhau ở một quyết định duy nhất — unit của bộ nhớ dài ngữ cảnh: per-token latent được chọn lọc, compressed group entry, hay fixed-state recurrent memory cộng periodic token retrieval.**[^sparse-evolution][^v4-k3-comparison]

### 2.3 Mental model: ba thư viện cho cùng một kho sách

```text
Archetype A — token-addressable + indexer (GLM-style MLA/DSA)
  kho: MỌI trang được photocopy nén (latent) và giữ nguyên
  đọc: thủ thư học được (indexer) chọn tối đa 2.048 trang cho bạn
       → trang được chọn là CHÍNH trang gốc, đọc nguyên văn

Archetype B — compressed entries (DeepSeek-V4-style CSA/HCA)
  kho: chương cũ bị THAY BẰNG bản tóm tắt theo cụm
       CSA: tóm tắt mỗi ~4 trang    HCA: tóm tắt mỗi ~128 trang
       128 trang cuối vẫn còn nguyên văn
  đọc: CSA chọn vài bản tóm tắt; HCA đọc DẦY mọi bản tóm tắt (đã ít)
       → không còn "trang thứ 37" để đọc chính xác nữa

Archetype C — recurrent majority + periodic MLA (Kimi-style)
  kho: 3/4 phòng đọc KHÔNG có kệ sách — chỉ một bảng trắng cố định kích thước
       mỗi token vào là GHI ĐÈ lên bảng (delta rule: sửa phần bảng mà key nó chỉ tới)
  đọc: query đọc bảng trắng hiện tại — fact cũ có thể đã bị trộn/đè
  ngoại lệ: cứ mỗi 4 phòng lại có MỘT phòng kệ đầy (global MLA)
       → fact cũ vẫn nguyên văn trên kệ của phòng đó
```

Điểm mấu chốt: ba thư viện trả **câu trả lời khác nhau cho cùng câu hỏi "đọc lại trang cũ"** — A giữ nguyên trang nhưng phải tìm đúng; B bỏ luôn trang gốc chỉ giữ tóm tắt; C đa số phòng không còn khái niệm trang, thi thoảng mới có phòng còn kệ.

### 2.4 Text diagram: ba archetype trong một glance

```text
                 prefill: ghi history          decode: query cuối đọc gì
A  MLA/DSA       latent mỗi token ──────────── indexer chấm điểm MỌI entry
   (GLM-5)       (cache tăng theo token)       → top-k token slots → softmax
                                               → đọc đúng slot gốc

B  CSA/HCA       remote → entry theo group ─── CSA: indexer chọn top-k entry
   (DeepSeek-V4) local 128 token giữ nguyên    HCA: dense trên ít entry
                                               + local window nguyên văn

C  KDA + MLA     69/93 layer: state cố định ── KDA: đọc state hiện tại
   (Kimi K3)     24/93 layer: latent MLA       MLA: dense đọc mọi token slot
                                               (checkpoint định kỳ)
```

### 2.5 Ba câu hỏi phân loại mọi kiến trúc dài ngữ cảnh

Trước khi thuộc tên bất kỳ model nào, hãy thuộc ba câu hỏi — chúng đủ để phân loại mọi biến thể (synthesis từ các concept nguồn):

1. **Một remote token còn "slot riêng" để bị score/gather không?** (`addressability`)
2. **State của layer tăng theo context thế nào?** (`state growth`)
3. **Query phải scan bao nhiêu thứ để tìm ra thứ cần đọc, và reads có liền mạch không?** (`indexer` + `locality`)[^sparse-evolution]

Sau bài này, người đọc trả lời được: nó giải quyết gì (2.1), hoạt động ra sao (mục 3), tác động gì (mục 4), khác baseline thế nào (mục 5), và dùng thực tế khi nào (mục 6).

## 3. Cách hoạt động — nhìn từ đầu đến cuối

### 3.1 Ví dụ xuyên suốt: một remote fact

Một prompt dài (toy dùng 16 token, model thật có thể 1 triệu token). **Fact** nằm ở token đầu: `endpoint db-primary-77` — trong toy, fact là một cặp key/value riêng (`k` trùng hướng query, `v` là giá trị cần copy). Các token ở giữa là distractor. **Query** ở token cuối hỏi lại fact. Câu hỏi duy nhất: *mỗi archetype trả về gì khi đọc?*

Kết quả chạy toy ở mục 8 (verify ở mục 9, giá trị làm tròn) làm thước đo xuyên suốt:

| Archetype | Query đọc ra | Diễn giải |
|---|---|---|
| A — MLA/DSA | `≈ [1.0, 0.0]` | copy **chính xác** fact — slot gốc được gather nguyên văn |
| B — CSA (group 4, top-2) | `[0.22, 0.24]` | fact bị **pha loãng** vào entry của cả nhóm distractor |
| B — HCA (group 8, dense) | `[0.05, 0.70]` | nén mạnh hơn — gần như chỉ còn "hướng" của fact |
| C — KDA | `[0.5, 0.71]` | fact bị **trộn** với write của distractor lên cùng vùng state |
| C — periodic MLA | `≈ [1.0, 0.0]` | checkpoint MLA đọc lại slot gốc — copy chính xác |

Cùng một fact, ba mô hình bộ nhớ, ba định mệnh khác nhau. Ba mục dưới giải thích vì sao.

### 3.2 Luồng chung: prefill → decode

```text
PREFILL (xử lý toàn bộ prompt)
  token-1, token-2, … đi qua từng layer
  mỗi layer "lưu" history theo mô hình bộ nhớ của nó:
      A: append latent entry mỗi token   (cache dài thêm theo token)
      B: nhóm remote token thành entry    (entry tăng theo số group)
      C: KDA cập nhật state cố định       (state KHÔNG dài thêm)
         MLA-layer append latent entry     (chỉ 1/4 số layer)

DECODE (sinh token mới)
  query của token mới → TÌM (indexer hoặc không cần) → ĐỌC state → softmax → output
```

| Thành phần | Archetype A | Archetype B | Archetype C |
|---|---|---|---|
| Cái được lưu ở prefill | latent **per token** | **entry theo group** + local window thô | **state cố định** (KDA) + latent per token (MLA layers) |
| Bước "tìm" khi decode | indexer chấm điểm mọi entry, chọn top-k token | CSA: chọn top-k entry; HCA: không tìm, đọc hết | KDA: không tìm; MLA: không tìm, dense |
| Bước "đọc" | gather đúng token slot | đọc value của entry (đã trộn nhóm) + window | đọc state hiện tại / dense mọi token |
| Ai phải quét toàn prefix | indexer (rẻ nhưng vẫn quét) | indexer CSA (trên ít entry hơn) | không ai — KDA không quét; MLA chỉ quét ở 1/4 layer |

### 3.3 Archetype A — token retrieval: indexer chọn, slot gốc được đọc nguyên văn

Vai trò từng thành phần (GLM-style):

- **MLA latent** (mỗi token): nén K/V của token thành một vector latent nhỏ — cache nhỏ hơn nhiều so với MHA nhưng **vẫn là một entry mỗi token**, nên cache vẫn tăng theo context.[^mla-concept]
- **Lightning indexer**: trước khi attention chính chạy, một mạng nhỏ chấm điểm mọi entry prefix theo query (trên GLM-5: chọn tối đa 2.048 vị trí).[^dsa-concept]
- **Core attention (MQA)**: softmax chỉ trên các entry được chọn; giá trị đọc về là **chính latent của token gốc** — không trộn, không aggregate.[^dsa-concept]

Với remote fact: indexer phải xếp token chứa `db-primary-77` vào top-k. Nếu xếp trúng, layer này copy được fact nguyên văn — đó là lý do toy của A trả về đúng `[1.0, 0.0]`. Nếu indexer trượt, fact **không bao giờ** được layer đó đọc: failure mode là *selection miss*, không phải *representation loss*.[^glm5-k3-comparison]

### 3.4 Archetype B — compressed entries: fact trở thành phần của tóm tắt

Vai trò từng thành phần (DeepSeek-V4-style):

- **Compression**: nhóm remote token (CSA: ~4 token/entry với hai cửa sổ chồng lấn có trọng số học được; HCA: nhóm không chồng lấn ~128 token/entry) thành **một entry key và một entry value học được**. Token trong nhóm không còn slot riêng.[^csa-hca]
- **Local window**: 128 token gần nhất giữ nguyên dạng thô; tail chưa đủ nhóm cũng phải giữ state riêng.[^csa-hca]
- **Retrieval**: CSA chạy indexer chọn top-k entry; HCA đọc dense toàn bộ entry (vì đã ít sau nén mạnh); cả hai cộng local window vào read set.[^csa-hca]

Với remote fact: entry chứa nó là một *trung bình học được* của cả nhóm — toy cho thấy group của fact trả về `[0.22, 0.24]`, fact vẫn "hướng" đúng nhưng bị pha loãng, và hoán đổi hai token trong nhóm không làm output đổi (mục 9 chứng minh). Failure mode: *representation loss* — query có thể tìm đúng entry mà vẫn không copy đúng token gốc; chỉ có local window là còn đọc nguyên văn.[^v4-arch]

### 3.5 Archetype C — recurrent majority: fact bị ghi đè lên bảng trắng, periodic MLA cứu lại

Vai trò từng thành phần (Kimi-style, theo tỉ lệ 69 KDA : 24 MLA của K3):[^k3-arch]

- **KDA (đa số layer)**: một state ma trận cố định. Mỗi token vào làm hai việc: **đọc** phần state mà key của nó chỉ tới, rồi **sửa** phần đó về phía value của nó (delta rule), kèm decay theo kênh để quên dần. State không dài thêm theo context.[^kda-concept]
- **Periodic global MLA (khoảng 1/4 layer)**: cứ sau ba layer KDA lại có một layer MLA toàn cục, cache latent per token và đọc dense — token-addressable trở lại ở đó.[^k3-arch]
- Trục phụ không phải sequence memory: Block AttnRes truy xuất theo **độ sâu**, LatentMoE trộn kênh thưa — xem [Kimi K3 theo information path](kimi-k3-integrated-architecture-information-path-beginners-course.md).

Với remote fact: ở layer KDA, fact từng được ghi lên state; các token sau write đè/trộn lên cùng vùng (toy: một distractor có key giao với key của fact khiến phép đọc trả về `[0.5, 0.71]` — nửa fact, nửa junk). Ở layer MLA, slot gốc vẫn còn nguyên nên periodic read copy chính xác. Failure mode: *interference* — và mức độ cứu lại phụ thuộc vào mật độ layer MLA.[^kda-concept][^k3-arch]

> [!note] Kiểm tra data flow
> Với bất kỳ kiến trúc dài ngữ cảnh nào, hỏi theo thứ tự: **lưu gì ở prefill → quét gì khi tìm → đọc gì khi retrieve → cache còn giữ gì sau đó**. Nếu chỉ biết tên cơ chế (MLA, sparse, linear) mà chưa trả lời được bốn câu này, ta chưa phân loại được archetype của nó.

## 4. Tác động

### 4.1 Behavior và quality

| Archetype | Copy chính xác remote fact khi nào | Failure mode |
|---|---|---|
| A — token retrieval | indexer xếp fact vào top-k (mọi layer đều có indexer) | selection miss: fact tồn tại nhưng không được chọn |
| B — compressed entries | fact nằm trong 128-token local window | representation loss: token gốc đã bị aggregate |
| C — recurrent hybrid | đọc ở đúng layer MLA (khoảng 1/4 số layer) | interference: state bị write sau này trộn/đè |

Đây là **hệ quả trực tiếp của thiết kế**, không phải benchmark: không có indexer hoàn hảo (A), không có nén không mất thông tin của token trong group (B), không có state hữu hạn không giao thoa (C). Lợi ích chỉ xuất hiện khi điều kiện đi kèm được thỏa: A cần indexer recall cao và kernel gather tốt; B cần workload chấp nhận remote detail dạng aggregate; C cần mật độ MLA đủ dày cho workload retrieval.[^glm5-k3-comparison][^csa-hca][^kda-concept]

### 4.2 Memory: state-growth ledger (hệ quả trực tiếp)

| Chiều | A | B | C |
|---|---|---|---|
| State mỗi layer theo context | tăng **tuyến tính theo token** (latent nhỏ nhưng vẫn mỗi token một entry)[^mla-concept] | tăng theo **số group** remote + window/tail thô[^csa-hca] | KDA **cố định**; MLA-layer tăng tuyến tính → toàn model **không** cố định[^k3-arch] |
| Context dài gấp đôi | cache gấp đôi | cache tăng chậm hơn gấp đôi (phần remote theo group) | chỉ phần MLA gấp đôi |

Bảng trên là suy luận trực tiếp từ cơ chế, tính bằng toy ở mục 7.7 và verify ở mục 9; nó **không** nói lên tổng bytes thật vì còn dtype, số layer, số head và overhead cache layout của từng model.

### 4.3 Compute và latency

- **Prefill/scan**: A vẫn phải quét toàn prefix bằng indexer trước khi core attention chạy trên top-k; B-CSA quét trên ít entry hơn; B-HCA bỏ indexer; C không quét gì ở layer KDA (decode chỉ cập nhật state) nhưng MLA-layer vẫn dense.[^dsa-concept][^csa-hca][^kda-concept]
- **Đọc khi decode**: A gather token slot rời rạc (kém locality — các đo đạc của LongCat về fetch rải rác chính là động cơ cho LSA); B đọc entry thô hơn và liền mạch hơn; C đọc state nhỏ trong DRAM.[^sparse-evolution]
- **Điều kiện để lợi ích xuất hiện**: A cần sparse kernel và indexer rẻ (DSA được report chiếm phần lớn decode latency của layer ở context rất dài khi kernel không tối ưu); B cần compression trả đủ chất lượng; C cần chunkwise training khả thi cho KDA (đã có kernel WY/UT) và chấp nhận MLA-layer làm trần trên của state.[^dsa-concept][^csa-hca][^kda-concept]

### 4.4 Hệ quả trực tiếp khác kết quả benchmark

Ba ví dụ tách bạch:

- "Token trong group không còn slot riêng" (B) là hệ quả **đại số của nén** — đúng với mọi cài đặt. "Pro đạt 27% FLOPs và 10% KV cache so với V3.2 ở 1M context" là **author-run estimate** trong cấu hình cụ thể của DeepSeek-V4.[^v4-arch]
- "State KDA cố định" (C) là hệ quả trực tiếp. "K3 cải thiện scaling-efficiency khoảng 2.5 lần so với K2" là kết quả **fit validation-loss**, đánh giá jointly toàn bộ thay đổi, không isolate cơ chế nào.[^k3-arch]
- "Core attention của DSA chỉ tính trên top-k entries" (A) là hệ quả trực tiếp. "DSA không suy giảm chất lượng" là claim của report GLM-5 mà chính các evaluation 128K của nó cho kết quả **mixed** — không thể suy ra từ thiết kế.[^dsa-concept]

Nguyên tắc đọc: mọi con số "x% nhanh hơn/nhỏ hơn" trong các nguồn đều là author-run, cấu hình cụ thể; mọi thuộc tính addressability/state là suy luận cơ chế.

## 5. Sự khác biệt

### 5.1 Archetype matrix — deliverable của stage này

| Chiều matched | Dense MLA (baseline) | A — GLM-style MLA/DSA | B — DeepSeek-V4-style CSA/HCA | C — Kimi-style KDA + periodic MLA |
|---|---|---|---|---|
| Remote token addressability | mọi token có slot riêng, query đọc hết | mọi token **vẫn có slot riêng**, chỉ top-k được đọc | **không** — slot bị thay bằng entry theo group; local window giữ slot | KDA-layer: **không** (state associative); MLA-layer: có slot, dense |
| State growth theo context | tuyến tính mỗi layer | tuyến tính mỗi layer (latent nhỏ hơn) | theo số group + window/tail | KDA cố định; tổng model vẫn tuyến tính qua MLA-layers |
| Read locality | dense, đều | gather rời rạc theo token (kém locality) | entry liền mạch hơn, window contiguous | state nhỏ; MLA-layer dense như thường |
| Indexer | không | có, quét prefix mỗi layer (GLM code có chế độ reuse qua layer) | có ở CSA (trên entry), không ở HCA | không cần tìm ở KDA; MLA dense không cần |
| Failure mode copy fact | chỉ fail khi context vượt khả năng xử lý | selection miss | representation loss | interference tại KDA, được MLA cứu định kỳ |
| Đại diện | DeepSeek-V2/V3 | GLM-5 (MLA + DSA toàn backbone) | DeepSeek-V4 (CSA + HCA xen kẽ) | Kimi K3, Kimi Linear, Qwen3.8-Flash-Next |

Nguồn từng cột: baseline và A từ [^mla-concept][^dsa-concept][^glm5-k3-comparison]; B từ [^csa-hca][^v4-arch]; C từ [^k3-arch][^kda-concept]; dòng "đại diện" và góc nhìn tiến hóa từ [^sparse-evolution][^v4-k3-comparison].

### 5.2 So với baseline và cơ chế gần nhất

| So sánh | Giống nhau | Khác nhau | Trade-off | Khi nào phù hợp |
|---|---|---|---|---|
| A vs dense MLA | vẫn MLA cache, softmax trên token slots, causal | thêm indexer + top-k giữa query và core | đọc ít hơn; rủi ro selection miss + indexer cost | context dài, cần exact retrieval ở **mọi** layer, có sparse kernel |
| B vs A | cùng giảm chi phí đọc bằng selection (CSA) | đổi cả representation: group entry thay token entry | cache nhỏ hơn rõ rệt; mất token identity | context rất dài, chấp nhận remote dạng tóm tắt, cần cache/IO nhỏ |
| C vs B | cùng muốn state không tăng (B ở remote, C ở đa số layer) | C không nén history — C **thay** history bằng state; C giữ periodic MLA exact | decode rẻ, state cố định; interference + vẫn có MLA-layer tăng tuyến tính | general-purpose dài ngữ cảnh, streaming, memory-bound |
| C vs A | đều có MLA ở đâu đó trong stack | vai trò khác nhau: A dùng MLA ở core mọi layer; C dùng MLA làm checkpoint 1/4 layer | C giảm state phần lớn layer; A giữ token-addressability xuyên suốt | C cho workload trộn local/recency nhiều; A khi exact retrieval là yêu cầu cứng |

### 5.3 Thay đổi nằm ở đâu trong data flow, phần nào giữ nguyên

```text
token → embedding → [LAYERS] → output head
                    │
   ┌────────────────┴─────────────────────────┐
   │ GIỮ NGUYÊN: causal order, query/value     │
   │ projection, softmax semantics trên read   │
   │ set, residual stream, FFN/MoE, output     │
   │ projection                                 │
   ├───────────────────────────────────────────┤
   │ ĐỔI: representation của history được lưu  │
   │ (latent/token vs entry/state), bước tìm   │
   │ (indexer vs dense), lịch layer (phần lớn   │
   │ layer dùng cơ chế gì)                     │
   └───────────────────────────────────────────┘
```

Cả ba archetype đều là quyết định **giữa query creation và core attention, cộng với cache retention** — phần còn lại của hệ thống (residual, FFN/MoE, training objective, serving scheduler) nguyên tắc không đổi. MoE của V4, GLM-5, K3 khác nhau vì các lựa chọn độc lập với archetype attention.[^v4-k3-comparison]

### 5.4 Khái niệm dễ nhầm (đọc trước khi đi vào kỹ thuật)

- **MLA không phải một archetype.** MLA là *nén representation per token*; nó đứng ở baseline (dense), ở core của A, và ở checkpoint của C. Câu hỏi phân loại là vai trò của nó, không phải sự hiện diện.[^mla-concept]
- **Sparse read không bằng cache nhỏ.** DSA giảm entries được *đọc*; cache vẫn giữ entry mỗi token. CSA/HCA mới giảm entries được *lưu*.[^sparse-evolution]
- **Compressed per-token khác compressed group.** MLA nén K/V của **một** token; CSA/HCA nén **một nhóm** token thành một entry. Cái trước giữ token identity, cái sau không.[^mla-concept][^csa-hca]
- **Fixed-state không nghĩa model hết state tăng.** K3 có 24/93 layer MLA vẫn cache theo token; "constant state end-to-end" là claim chưa từng đúng cho cả ba model trong nguồn.[^k3-arch][^v4-k3-comparison]
- **Context window không bằng recall.** "1M context" là claim về khả năng xử lý độ dài; độ tin cậy truy xuất ở mỗi vị trí là phép đo riêng.[^glm5-k3-comparison]
- **Interference của KDA có hướng sửa:** delta correction viết đè lên đúng association mà key chỉ tới, và decay theo kênh kiểm soát tốc độ quên — nhưng không hoàn nguyên token đã bị trộn.[^kda-concept]

## 6. Trong thực tế

### 6.1 Cơ chế nằm ở đâu trong các model thật

| Model | Archetype | Cấu hình long-context chính | Ghi chú hệ thống |
|---|---|---|---|
| GLM-5 | A | MLA toàn 78 layer backbone + DSA indexer chọn tối đa 2.048 token; code mở có chế độ layer tái dùng indices | indexer warm-up 1.000 bước, sparse training 20B token từ checkpoint mid-training[^glm5-k3-comparison][^dsa-concept] |
| DeepSeek-V4 Pro/Flash | B | xen kẽ CSA (group 4, top-512/1.024 entry) và HCA (group 128, dense) + sliding window 128 token | KV RoPE-dim BF16, phần còn lại FP8, indexer QK FP4; compressed-prefix có thể lưu disk[^csa-hca][^v4-arch] |
| Kimi K3 | C | 69 KDA + 24 NoPE gated MLA (tỉ lệ 3:1) + MLA cuối stack; AttnRes và LatentMoE là trục khác | KDA chạy chunk kernel lúc prefill, fused recurrent kernel lúc decode; cache API chứa hai loại state[^k3-arch][^v4-k3-comparison] |

Ranh giới cần nhớ: DeepSeek-V3.2 (DSA thuần, token-level) là prototype của A; LongCat-Flash-Lite-Sparse là biến thể A với index reuse và hierarchy; Qwen3.8-Flash-Next là C nhưng periodic layer dùng sparse attention thay vì dense MLA — cho thấy "periodic retrieval" là trừu tượng hóa, layer cụ thể có thể dense hoặc sparse.[^sparse-evolution]

### 6.2 Khi nào nên dùng archetype nào

Từ [Workload-conditioned selection](workload-conditioned-frontier-llm-architecture-selection.md) — đề xuất kỹ thuật có điều kiện, không phải benchmark verdict:[^workload-selection]

- **Chọn A** khi exact long-context retrieval ở mọi layer là yêu cầu cứng (audit, citation, exact copy từ vị trí bất kỳ) và runtime có sparse gather/top-k kernel; chấp nhận cache vẫn tăng tuyến tính và indexer là chi phí mới.
- **Chọn B** khi memory/IO của KV cache là ràng buộc chính, context cực dài, và workload dùng remote history ở mức "tóm tắt đúng vùng" hơn là từng token (code navigation tổng quan, RAG-style evidence thô) — không dùng khi user cần quote nguyên văn đoạn cũ.
- **Chọn C** cho general-purpose chat/agent/coding dài ngữ cảnh: decode streaming rẻ, state per-request nhỏ ở đa số layer; nhưng phải đo retrieval vì interference là nguy cơ thật.
- **Không chọn gì cả khi context ngắn**: mọi cơ chế trên đều trả overhead (indexer, compression, MLA periodic) mà dense attention vốn đã rẻ.

### 6.3 Walkthrough: agent đọc log 1 triệu token

Yêu cầu: agent truy hồi `endpoint db-primary-77` xuất hiện một lần ở vị trí ~120.000 và quote nó ở câu trả lời.

1. **Prefill.** A: mỗi token ghi một latent entry, indexer weights đã train. B: vùng log cũ trở thành entries theo group, chỉ 128 token cuối giữ nguyên văn; entry chứa fact giờ là trung bình học được của cả vùng log quanh nó. C: 69 layer KDA lần lượt cập nhật state (fact được ghi rồi dần bị trộn bởi ~120K token sau nó); 24 layer MLA cache latent per token.
2. **Query cuối.** A: indexer chấm điểm ~120K entry prefix; nếu token fact vào top-2.048 → đọc slot gốc. B: CSA chấm điểm entry (ít hơn nhiều); HCA đọc dense entries; fact có thể vào read set nhưng chỉ ở dạng aggregate. C: layer KDA đọc state — fact có thể chỉ còn "mờ"; layer MLA đọc dense và thấy slot gốc.
3. **Trả lời.** Chỉ A và C-ở-layer-MLA có đường copy nguyên văn. B trả lời được "endpoint ở vùng log giữa" nhưng quote chính xác không được đảm bảo bởi kiến trúc.
4. **Đo sau khi chạy:** recall theo vị trí fact, exact-copy score, bytes cache mỗi loại layer, chi phí indexer tách riêng, TTFT và TPOT.

### 6.4 Measurement phải ghi và claim không thể suy ra

| Phải đo | Vì sao |
|---|---|
| Recall/exact-copy theo **vị trí** fact (gần/xa), có distractor | failure mode khác nhau per archetype (4.1) |
| Bytes cache **tách theo loại layer** và dtype | C trộn fixed state và token-linear; B trộn entry và window |
| Chi phí indexer/compression tách khỏi core attention | đây là chi phí "tìm" mà baseline dense không có |
| TTFT (prefill) tách TPOT (decode) | ba archetype đổi hai pha này không đồng đều |

Claim **không thể suy ra chỉ từ lý thuyết**: model nào "tốt hơn" overall (cần matched benchmark); "lossless" của selection (A) hoặc compression (B); interference thực tế của C trên workload cụ thể; mọi con số latency/memory — tất cả phải đo trên checkpoint, dtype, kernel, hardware đích.[^glm5-k3-comparison][^v4-arch][^k3-arch]

> [!note] Gate trước phần toán
> Đến đây bạn phải trả lời được: (1) ba archetype giải quyết chi phí đọc/lưu history dài; (2) chúng chạy qua lưu-ở-prefill → tìm-và-đọc-khi-decode với ba mô hình bộ nhớ khác nhau; (3) tác động là addressability/state/quality đổi theo từng failure mode riêng; (4) khác dense baseline ở representation, bước tìm, và lịch layer — không phải ở softmax hay residual; (5) dùng khi workload khớp điều kiện của từng failure mode. Phần dưới chỉ làm các trực giác đó chính xác bằng công thức và code.

## 7. Toán học — zoom in sau cùng

### 7.1 Bảng ký hiệu

| Ký hiệu | Shape | Ý nghĩa |
|---|---:|---|
| $L$ | scalar | chiều dài prefix (context length) |
| $k$ | scalar | budget top-k của indexer (token hoặc entry) |
| $d$ | scalar | head dimension của attention toy |
| $q_t, k_j, v_j$ | $(d)$ | query tại vị trí $t$, key/value của token $j$ |
| $c^{KV}_t$ | $(d_c)$ | latent KV của token $t$ trong MLA |
| $d_c, d^R_h$ | scalar | bề rộng latent content và rotary key của MLA |
| $I_{t,s}$ | scalar | điểm indexer của DSA cho query $t$, entry $s$ |
| $m, m'$ | scalar | compression group size (CSA $m=4$, HCA $m'=128$) |
| $\tilde{k}_b, \tilde{v}_b$ | $(d)$ | key/value entry của group $b$ sau nén |
| $S_t$ | $(d_k, d_v)$ | recurrent state của KDA tại bước $t$ |
| $k_t, v_t$ | $(d_k)$, $(d_v)$ | key/value token $t$ trong memory KDA |
| $\beta_t, \alpha_t$ | scalar / $(d_v)$ | write strength và decay (KDA: $\alpha$ theo kênh) |
| $\pi_{b,j}$ | scalar | trọng số nén của token $j$ trong group $b$ |

### 7.2 Baseline: dense causal attention

**Trực giác.** Query chấm điểm mọi key quá khứ rồi lấy softmax có trọng số.

$$
s_{t,j}=\frac{q_t^{\top}k_j}{\sqrt{d}},\qquad
o_t=\sum_{j\le t}\operatorname{softmax}_j(s_{t,:})\,v_j .
$$

**Ký hiệu.** $t$ là vị trí query, $j$ duyệt mọi vị trí quá khứ. **Shape flow:** $q_t$ nhân $K^{\top}$ cho scores $(L)$, softmax giữ shape, nhân $V$ ra output $(d)$. **Ví dụ số** (toy của bài): $d=2$, query $(1,0)$, key của fact $(20,0)$ và 15 key $(0,1)$ → logit fact $\approx 14{,}1$, các logit khác $0$ → trọng số fact $\approx 0{,}99999$. **Kết luận.** Dense softmax giữ đúng mọi slot; ba archetype dưới chỉ đổi *tập được chấm*, *đại diện được đọc*, hoặc *cách lưu*.

### 7.3 MLA: nén per-token nhưng vẫn per-token

**Trực giác.** Không lưu K/V đầy đủ mỗi head; lưu một latent chung rồi "mở" ra bằng up-projection có thể hấp thụ vào query/output path.

$$
c^{KV}_t=W^{DKV}h_t,\qquad k_j = W^{UK}c^{KV}_j,\qquad v_j = W^{UV}c^{KV}_j .
$$

**Ký hiệu.** $W^{DKV}$ nén hidden state $h_t$ (chiều $d_{\text{model}}$) xuống latent $d_c$; up-projections chỉ cần lúc training, decode cache chỉ giữ $c^{KV}_t$ cộng decoupled rotary key (thêm $d^R_h$ phần tử).[^mla-concept] **Shape flow:** cache mỗi token là $(d_c + d^R_h)$ thay vì $2 n_h d_h$ của MHA. **Ví dụ số.** Với cấu hình DeepSeek-V2 $d_c=4d_h$, $d^R_h=d_h/2$: khoảng $4{,}5 d_h$ phần tử mỗi token so với $2 n_h d_h$ — nhưng **vẫn là một entry mỗi token**, nên cache vẫn tuyến tính theo $L$ (bằng chứng trực tiếp cho 4.2).[^mla-concept] **Kết luận.** MLA đổi *kích thước entry*, không đổi *đơn vị entry* — lý do nó đứng được ở cả ba archetype với vai trò khác nhau.

### 7.4 DSA: indexer và top-k trên token entries

**Trực giác.** Một mạng chấm điểm cực rẻ quét prefix, chọn top-k, core attention chỉ chạy trên đó.

$$
I_{t,s}=\sum_{j=1}^{H^I}w^I_{t,j}\operatorname{ReLU}\!\left(q^I_{t,j}\cdot k^I_s\right),
\qquad
J_t=\operatorname{TopK}_s(I_{t,:},k),
$$

$$
o_t=\sum_{j\in J_t}\operatorname{softmax}_j\!\left(\frac{q_t^{\top}k_j}{\sqrt d}\right)v_j .
$$

**Ký hiệu.** $H^I$ indexer heads rất ít; $J_t$ là tập token được chọn; công thức thứ hai chính là baseline 7.2 với tập $j$ bị giới hạn. **Shape flow:** indexer cho $(L)$ scores mỗi query; core từ $(L,d)\times(d,L)$ co còn $(k,d)\times(d,k)$. **Ví dụ số.** $L=131{,}072$, $k=2{,}048$: core đọc $\approx 1{,}6\%$ prefix — nhưng indexer vẫn phải chấm đủ $131{,}072$ điểm cho mỗi query. **Kết luận.** Core attention của DSA scale theo top-k; tổng layer không tự do khỏi quét prefix (động cơ cho pooling/reuse/hierarchy của các thiết kế sau).[^dsa-concept][^sparse-evolution]

### 7.5 CSA/HCA: entry theo group thay token

**Trực giác.** Nén một nhóm token thành một entry key và một entry value bằng trọng số học được; local window giữ thô.

$$
\tilde{k}_b=\sum_{j\in G_b}\pi_{b,j}\,k_j,\qquad
\tilde{v}_b=\sum_{j\in G_b}\pi_{b,j}\,v_j,\qquad
\sum_{j\in G_b}\pi_{b,j}=1 ,
$$

$$
o_t=\operatorname{softmax}\!\left(\frac{q_t^{\top}[\tilde K_{\text{sel}};\,K_{\text{local}}]}{\sqrt d}\right)
[\tilde V_{\text{sel}};\,V_{\text{local}}] .
$$

**Ký hiệu.** $G_b$ là group $b$ kích thước $m$ (CSA) hoặc $m'$ (HCA); $\pi$ trọng số học được (toy ở mục 8 dùng mean, $\pi=1/m$); tập đọc gồm entries được chọn (CSA) hoặc tất cả (HCA) cộng local window. **Shape flow:** remote prefix từ $L$ token thành khoảng $L/m$ entries; giá trị đọc về là $\tilde{v}_b$ — trung bình có trọng số, không phải $v_j$ của token nào. **Ví dụ số.** $L=1{,}048{,}576$: CSA $m=4$ → khoảng 262K entries (Pro chọn top-1.024); HCA $m'=128$ → khoảng 8.192 entries — ít đủ để dense attention khả thi. **Kết luận.** Số entry giảm theo group size nhưng *token identity trong group mất*; chỉ window $W=128$ còn đọc $v_j$ nguyên văn.[^csa-hca][^v4-arch]

### 7.6 KDA: delta rule trên state cố định

**Trực giác.** State là một ma trận nhớ association key→value; token mới **đọc** association hiện tại của key mình rồi **sửa** nó về phía value mình.

$$
S_t=\left(I-\beta_t\,k_tk_t^{\top}\right)\operatorname{Diag}(\alpha_t)\,S_{t-1}
+\beta_t\,k_tv_t^{\top},
\qquad
o_t=S_t^{\top}q_t .
$$

**Ký hiệu.** $S_t\in(d_k,d_v)$; $\beta_t\in[0,1]$ là write strength; $\alpha_t$ là decay — KDA dùng vector theo kênh, toy dùng scalar; rank-one $k_tk_t^{\top}$ chính là "phần bảng mà key chỉ tới".[^kda-concept] **Shape flow:** mọi đại lượng state đều không phụ thuộc $L$; update và read chỉ là ma trận nhỏ $(d_k, d_v)$.

**Ví dụ số — trường hợp nhỏ nhất tính tay** (chính là test ở mục 9): $d_k=d_v=2$, $\beta=1$, $\alpha=1$, $k_0=(1,0)$, $v_0=(1,0)$:

1. Sau token 0: $S_0=k_0v_0^{\top}$ — đọc lại bằng $q=k_0$ trả về $(1,0)$, fact nguyên vẹn.
2. Token 1 là distractor $k_1=(1,1)/\sqrt{2}$, $v_1=(0,1)$; vì $k_1$ giao với $k_0$, phép update đụng cùng vùng state:

$$
S_1=S_0-k_1\left(k_1^{\top}S_0\right)+k_1v_1^{\top},\qquad
S_1^{\top}k_0=\tfrac{1}{2}v_0+\tfrac{1}{\sqrt{2}}\,v_1=(0{,}5;\ 0{,}707).
$$

3. Token 2 có key $(0,1)$ (ghi lên trục khác, không đụng fact) nhưng query $(1,0)$ — đọc ra đúng $(0{,}5;\ 0{,}707)$: **fact bị trộn**, không mất hẳn.

**Kết luận.** Interference là hệ quả hình học của state hữu hạn: write với key giao nhau buộc chia sẻ vùng state; delta rule khiến sự chia sẻ đó có tính "sửa đúng chỗ" (7.8) nhưng không tách lại hai value đã trộn. Periodic MLA (công thức 7.2 trên latent cache) là con đường copy chính xác duy nhất của C.[^kda-concept][^k3-arch]

### 7.7 State-growth ledger — hợp nhất

**Trực giác.** Cộng state của từng loại layer để so tăng trưởng khi $L$ đổi.

$$
M_A(L)=2L\,(d_c+d_h^R)\ \ \text{(mỗi layer)},\qquad
M_B(L)\approx 2\frac{L-W}{m}\,d_c+2W\,d ,
$$

$$
M_C^{\text{block}}(L)=3\,(d_k d_v)+2L\,(d_c+d_h^R)\qquad\text{(một block 3 KDA + 1 MLA)} .
$$

**Ký hiệu.** $W$ là local window; các hệ số 2 là factor K và V. **Shape flow / ví dụ số** (toy, $d=2$): $L=1024$ → dense 4.096, A 4.096, B-CSA 1.036, B-HCA 316, C-block 4.108 (12 từ KDA + 4.096 từ MLA); $L=2048$ → A gấp đôi (8.192), B-HCA chỉ 572, C-block 8.204 (chỉ phần MLA gấp đôi). **Kết luận.** C chỉ "cố định" ở phần KDA; phần MLA của C tăng y hệt A. Đúng như matrix 5.1: không model nào constant-size end-to-end.[^k3-arch][^v4-k3-comparison]

### 7.8 Nâng cao (có thể bỏ qua)

**Delta rule là một bước gradient descent.** Viết loss tái tạo association tại token $t$: $\mathcal{L}_t=\tfrac12\lVert S^{\top}k_t-v_t\rVert^2$. Một bước descent trên $S$ với learning rate $\beta_t$:

$$
S\leftarrow S-\beta_t\,k_t\left(k_t^{\top}S-v_t^{\top}\right)
=\left(I-\beta_tk_tk_t^{\top}\right)S+\beta_tk_tv_t^{\top},
$$

đúng dạng update của 7.6 khi $\alpha=1$. Đây là lý do "delta" được gọi là *correction*: nó cực tiểu hóa sai số giữa association hiện tại và value mới. Chứng minh đầy đủ và các biến thể (channel decay, chunkwise equivalence WY/UT) nằm ở [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md).[^kda-concept]

**Ghi chú capacity:** với state $(d_k, d_v)$, số key gần trực giao (do đó không giao thoa) bị chặn bởi $d_k$; vượt quá đó, các association buộc chồng lấn — cận trên lý thuyết cho interference, còn mức độ thực tế phải đo.

## 8. Implementation — PyTorch tối thiểu

Code cụ thể hóa đúng ba luồng đã học: `mla_dsa_read` là archetype A (select → gather token slots → softmax); `csa_hca_read` là archetype B (compress theo group → chọn hoặc dense → cộng local window); `kda_run` cộng `dense_global_read` là archetype C (delta update trên state cố định cộng periodic dense read). Toy không có learned indexer, learned compression weights, channel decay, RoPE/NoPE, FP8/FP4, chunkwise kernel hay paged cache — mỗi sai lệch được ghi ở mục 11.

Toy chạy FP32, một batch một head, không dùng RoPE. Model thật dùng decoupled RoPE (GLM MLA), partial RoPE (V4) hoặc NoPE với position do KDA gánh (K3); nếu thêm RoPE vào toy, dùng pairing `interleaved` và `position_ids` tuyệt đối tiếp nối prefix. Cache hình `(B, H, S, d)` mỗi phần K/V; đây là semantic reference, không phải serving kernel.

```python
import math
import torch
import torch.nn.functional as F


# ---------- Archetype A: token-addressable latent entries + learned top-k ----------

def select_topk(query, keys, top_k):
    """query: (B,H,1,d); keys: (B,H,S,d) -> causal top-k indices over the prefix."""
    scores = (query @ keys.transpose(-2, -1)) / math.sqrt(query.size(-1))  # (B,H,1,S)
    take = min(top_k, keys.size(-2))
    return torch.topk(scores.squeeze(-2), take, dim=-1).indices.sort(dim=-1).values


def mla_dsa_read(query, keys, values, top_k):
    """One decode query over cached per-token latent entries (MLA stand-in)."""
    d = query.size(-1)
    idx = select_topk(query, keys, top_k)                     # (B,H,take)
    gather_idx = idx.unsqueeze(-1).expand(-1, -1, -1, d)      # (B,H,take,d)
    k_sel = torch.gather(keys, -2, gather_idx)                # per-token slots, verbatim
    v_sel = torch.gather(values, -2, gather_idx)
    logits = (query @ k_sel.transpose(-2, -1)) / math.sqrt(d)
    out = F.softmax(logits, dim=-1) @ v_sel                   # (B,H,1,d)
    return out, idx, v_sel


# ---------- Archetype B: compressed group entries + local window ----------

def csa_hca_read(query, keys, values, group=4, top_k=None, window=4):
    """Remote history becomes mean-compressed group entries; window/tail stay raw.
    top_k=None -> dense over all entries (HCA-style); else sparse (CSA-style)."""
    B, H, S, d = keys.shape
    local = min(window, S)
    remote_end = S - local
    n_entries = remote_end // group
    k_g = keys[:, :, : n_entries * group, :].reshape(B, H, n_entries, group, d).mean(dim=-2)
    v_g = values[:, :, : n_entries * group, :].reshape(B, H, n_entries, group, d).mean(dim=-2)
    selected = n_entries
    if top_k is not None and n_entries > 0:
        take = min(top_k, n_entries)
        scores = (query @ k_g.transpose(-2, -1)) / math.sqrt(d)
        idx = torch.topk(scores.squeeze(-2), take, dim=-1).indices.sort(dim=-1).values
        k_g = torch.gather(k_g, -2, idx.unsqueeze(-1).expand(-1, -1, -1, d))
        v_g = torch.gather(v_g, -2, idx.unsqueeze(-1).expand(-1, -1, -1, d))
        selected = take
    k_raw = keys[:, :, n_entries * group:, :]                 # tail + local window, raw
    v_raw = values[:, :, n_entries * group:, :]
    k_all = torch.cat([k_g, k_raw], dim=-2)
    v_all = torch.cat([v_g, v_raw], dim=-2)
    logits = (query @ k_all.transpose(-2, -1)) / math.sqrt(d)
    out = F.softmax(logits, dim=-1) @ v_all
    info = {"remote_entries": n_entries, "selected_entries": selected,
            "raw_read": k_raw.size(-2), "tail": remote_end - n_entries * group}
    return out, info


# ---------- Archetype C: fixed-state delta rule (KDA stand-in) + periodic MLA ----------

def kda_run(keys, values, queries, beta=1.0, alpha=1.0):
    """keys/queries: (B,H,T,d_k); values: (B,H,T,d_v); fixed state S: (B,H,d_k,d_v).
    Toy uses fixed beta/alpha; real KDA learns both, channel-wise for alpha."""
    B, H, T, d_k = keys.shape
    d_v = values.size(-1)
    S = torch.zeros(B, H, d_k, d_v, dtype=keys.dtype)
    outputs = torch.zeros(B, H, T, d_v, dtype=keys.dtype)
    for t in range(T):
        k = keys[:, :, t, :]
        v = values[:, :, t, :]
        v_bar = torch.einsum("bhk,bhkv->bhv", k, S)           # read current association
        S = alpha * (S - beta * torch.einsum("bhk,bhv->bhkv", k, v_bar)) \
            + beta * torch.einsum("bhk,bhv->bhkv", k, v)      # delta correction
        outputs[:, :, t, :] = torch.einsum("bhk,bhkv->bhv", queries[:, :, t, :], S)
    return outputs, S


def dense_global_read(query, keys, values):
    """Periodic global-MLA stand-in: dense causal read of per-token entries."""
    d = query.size(-1)
    logits = (query @ keys.transpose(-2, -1)) / math.sqrt(d)
    probs = F.softmax(logits, dim=-1)
    return probs @ values, probs


# ---------- Ví dụ xuyên suốt: một remote fact ----------

def build_remote_fact_example(T=16, d=2, fact_scale=20.0):
    """Token 0 là remote fact (key dọc trục 0, value riêng); token 1..T-2 là junk
    dọc trục 1; token cuối mang query trục 0 nhưng key như junk."""
    keys = torch.zeros(1, 1, T, d)
    values = torch.zeros(1, 1, T, d)
    queries = torch.zeros(1, 1, T, d)
    keys[0, 0, 0, 0] = fact_scale
    values[0, 0, 0, 0] = 1.0
    for t in range(1, T - 1):
        keys[0, 0, t, 1] = 1.0
        values[0, 0, t, 1] = 0.1 * t
    keys[0, 0, -1, 1] = 1.0                                  # query token writes like junk
    queries[0, 0, -1, 0] = 1.0                               # but queries the fact axis
    return keys, values, queries


def state_ledger(T, d=2, group_csa=4, group_hca=16, window=4, kda_dk=2, kda_dv=2):
    """Toy per-layer retained-element accounting for the archetypes at length T."""
    dense = 2 * T * d
    arch_a = 2 * T * d                                       # latent entries still per token
    remote = max(0, T - window)
    n_csa = remote // group_csa
    n_hca = remote // group_hca
    arch_b_csa = 2 * n_csa * d + 2 * (T - n_csa * group_csa) * d
    arch_b_hca = 2 * n_hca * d + 2 * (T - n_hca * group_hca) * d
    arch_c_block = 3 * (kda_dk * kda_dv) + 2 * T * d         # 3 KDA + 1 MLA per block
    return {"dense": dense, "a": arch_a, "b_csa": arch_b_csa,
            "b_hca": arch_b_hca, "c_block": arch_c_block}


if __name__ == "__main__":
    k, v, q = build_remote_fact_example(T=16)
    query = q[:, :, -1:, :]
    out_a, idx, _ = mla_dsa_read(query, k, v, top_k=4)
    print("A selected:", idx[0, 0].tolist(), "out:", out_a[0, 0, 0].tolist())
    out_b, info_b = csa_hca_read(query, k, v, group=4, top_k=2, window=4)
    print("B CSA:", info_b, "out:", out_b[0, 0, 0].tolist())
    out_bh, info_h = csa_hca_read(query, k, v, group=8, top_k=None, window=4)
    print("B HCA:", info_h, "out:", out_bh[0, 0, 0].tolist())
    k3 = torch.zeros(1, 1, 3, 2)
    v3 = torch.zeros(1, 1, 3, 2)
    q3 = torch.zeros(1, 1, 3, 2)
    k3[0, 0, 0] = torch.tensor([1.0, 0.0])
    v3[0, 0, 0] = torch.tensor([1.0, 0.0])
    k3[0, 0, 1] = torch.tensor([1.0, 1.0]) / math.sqrt(2)    # junk overlaps fact axis
    v3[0, 0, 1] = torch.tensor([0.0, 1.0])
    k3[0, 0, 2] = torch.tensor([0.0, 1.0])
    q3[0, 0, 2] = torch.tensor([1.0, 0.0])
    outputs, S = kda_run(k3, v3, q3)
    print("C KDA state shape:", tuple(S.shape),
          "read:", outputs[0, 0, 2].tolist())
    out_m, probs = dense_global_read(query, k, v)
    print("C periodic MLA out:", out_m[0, 0, 0].tolist(),
          "fact prob:", float(probs[0, 0, 0, 0]))
```

Output khi chạy (PyTorch 2.14, CPU, FP32) — chính là các con số ở bảng 3.1:

```text
A selected: [0, 10, 11, 12] out: [0.9999978542327881, 2.3804636839486193e-06]
B CSA: {'remote_entries': 3, 'selected_entries': 2, 'raw_read': 4, 'tail': 0} out: [0.21820415556430817, 0.2441156506538391]
B HCA: {'remote_entries': 1, 'selected_entries': 1, 'raw_read': 8, 'tail': 4} out: [0.05283825471997261, 0.7035926580429077]
C KDA state shape: (1, 1, 2, 2) read: [0.5, 0.7071067690849304]
C periodic MLA out: [0.9999892711639404, 7.574137725896435e-06] fact prob: 0.9999892711639404
```

## 9. Xác minh trước khi benchmark

Suite dưới đã được thực thi và pass toàn bộ trên PyTorch 2.14 CPU (FP32) trong môi trường biên soạn; nội dung là bản y nguyên của test đã chạy. Các test chứng minh **semantic properties của toy**, không chứng minh selector được train, compression giữ chất lượng, hay kernel nhanh.

```python
@torch.no_grad()
def test_mla_dsa_matches_manual_gather():
    k, v, q = build_remote_fact_example()
    query = q[:, :, -1:, :]
    out, idx, v_sel = mla_dsa_read(query, k, v, top_k=4)
    gather_idx = idx.unsqueeze(-1).expand(-1, -1, -1, k.size(-1))
    logits = (query @ torch.gather(k, -2, gather_idx).transpose(-2, -1)) / math.sqrt(k.size(-1))
    expected = F.softmax(logits, dim=-1) @ torch.gather(v, -2, gather_idx)
    torch.testing.assert_close(out, expected, rtol=1e-5, atol=1e-6)


@torch.no_grad()
def test_dsa_selection_causal_and_fact_slot_addressable():
    k, v, q = build_remote_fact_example()
    for t in (2, 5, 15):
        idx = select_topk(q[:, :, t:t+1, :], k[:, :, :t+1, :], top_k=3)
        assert int(idx.max()) <= t                            # causal by construction
    query = q[:, :, -1:, :]
    out, idx, v_sel = mla_dsa_read(query, k, v, top_k=4)
    assert 0 in idx[0, 0].tolist()                            # fact selected
    pos = idx[0, 0].tolist().index(0)
    torch.testing.assert_close(                               # slot read verbatim
        v_sel[0, 0, pos, :], v[0, 0, 0, :], rtol=0.0, atol=0.0)


@torch.no_grad()
def test_compressed_group_is_lossy_local_window_exact():
    T, d = 16, 2
    k = torch.zeros(1, 1, T, d)
    v = torch.zeros(1, 1, T, d)
    for t in range(T):
        k[0, 0, t, 1 if t >= T - 4 else 0] = 1.0
    v[0, 0, 1, 0] = 1.0
    v[0, 0, 2, 0] = 3.0                                       # same remote group as token 1
    query = torch.tensor([[[[1.0, 0.0]]]])
    out_a, info_a = csa_hca_read(query, k, v, group=4, top_k=None, window=4)
    v_swap = v.clone()
    v_swap[0, 0, 1, 0], v_swap[0, 0, 2, 0] = 3.0, 1.0         # swap inside one group
    out_b, info_b = csa_hca_read(query, k, v_swap, group=4, top_k=None, window=4)
    assert info_a == {"remote_entries": 3, "selected_entries": 3, "raw_read": 4, "tail": 0}
    torch.testing.assert_close(out_a, out_b, rtol=0.0, atol=0.0)   # swap invisible
    v_local = v.clone()
    v_local[0, 0, -1, 1] += 10.0                              # perturb a local-window value
    out_c, _ = csa_hca_read(query, k, v_local, group=4, top_k=None, window=4)
    assert (out_c - out_a).abs().max() > 1e-3                 # local token read raw


@torch.no_grad()
def test_kda_state_fixed_size_and_mla_grows():
    for T in (8, 16):
        k, v, q = build_remote_fact_example(T=T)
        _, S = kda_run(k, v, q)
        assert tuple(S.shape) == (1, 1, 2, 2)                 # independent of T
    k1, v1, q1 = build_remote_fact_example(T=16)
    k2, v2, q2 = build_remote_fact_example(T=32)
    assert (k2.numel() + v2.numel()) == 2 * (k1.numel() + v1.numel())


@torch.no_grad()
def test_kda_delta_overwrites_same_key():
    keys = torch.zeros(1, 1, 2, 2)
    values = torch.zeros(1, 1, 2, 2)
    queries = torch.zeros(1, 1, 2, 2)
    keys[:, :, 0, 0] = 1.0
    keys[:, :, 1, 0] = 1.0                                    # same one-hot key
    values[:, :, 0, :] = torch.tensor([1.0, 0.0])
    values[:, :, 1, :] = torch.tensor([0.0, 3.0])
    queries[:, :, 1, 0] = 1.0
    outputs, _ = kda_run(keys, values, queries)
    torch.testing.assert_close(                               # second write wins
        outputs[0, 0, 1, :], torch.tensor([0.0, 3.0]), rtol=0.0, atol=1e-6)


@torch.no_grad()
def test_kda_interference_blends_remote_fact():
    d = 2
    keys = torch.zeros(1, 1, 3, d)
    values = torch.zeros(1, 1, 3, d)
    queries = torch.zeros(1, 1, 3, d)
    keys[0, 0, 0] = torch.tensor([1.0, 0.0])                  # fact: one-hot key
    values[0, 0, 0] = torch.tensor([1.0, 0.0])
    keys[0, 0, 1] = torch.tensor([1.0, 1.0]) / math.sqrt(2)   # junk overlaps fact axis
    values[0, 0, 1] = torch.tensor([0.0, 1.0])
    keys[0, 0, 2] = torch.tensor([0.0, 1.0])                  # query token writes junk axis
    queries[0, 0, 2] = torch.tensor([1.0, 0.0])               # but reads the fact axis
    outputs, _ = kda_run(keys, values, queries)
    expected = torch.tensor([0.5, 1.0 / math.sqrt(2)])        # hand-computed blend (7.6)
    torch.testing.assert_close(outputs[0, 0, 2, :], expected, rtol=1e-5, atol=1e-6)


@torch.no_grad()
def test_periodic_mla_recovers_remote_fact():
    k, v, q = build_remote_fact_example()
    query = q[:, :, -1:, :]
    out, probs = dense_global_read(query, k, v)
    d = k.size(-1)
    logits = (query @ k.transpose(-2, -1)) / math.sqrt(d)
    expected = F.softmax(logits, dim=-1) @ v
    torch.testing.assert_close(out, expected, rtol=1e-5, atol=1e-6)
    assert float(probs[0, 0, 0, 0]) > 0.99                    # fact dominates


@torch.no_grad()
def test_kda_causality():
    torch.manual_seed(3)
    keys = torch.randn(1, 1, 8, 2)
    values = torch.randn(1, 1, 8, 2)
    queries = torch.randn(1, 1, 8, 2)
    out1, _ = kda_run(keys, values, queries)
    values2 = values.clone()
    values2[0, 0, 5, :] += torch.tensor([5.0, -5.0])
    out2, _ = kda_run(keys, values2, queries)
    torch.testing.assert_close(                               # prefix reads unchanged
        out2[:, :, :5, :], out1[:, :, :5, :], rtol=0.0, atol=0.0)
    assert (out2[:, :, 5:, :] - out1[:, :, 5:, :]).abs().max() > 1e-3


@torch.no_grad()
def test_state_growth_ledger():
    s1 = state_ledger(1024)
    s2 = state_ledger(2048)
    assert s2["dense"] == 2 * s1["dense"]
    assert s2["a"] == 2 * s1["a"]                             # A linear in context
    assert s2["b_hca"] < 2 * s1["b_hca"]                      # B sublinear
    assert s2["c_block"] - s1["c_block"] == 2 * (2048 - 1024) * 2  # only MLA grows
    assert s1["c_block"] == 3 * 4 + 2 * 1024 * 2


test_mla_dsa_matches_manual_gather()
test_dsa_selection_causal_and_fact_slot_addressable()
test_compressed_group_is_lossy_local_window_exact()
test_kda_state_fixed_size_and_mla_grows()
test_kda_delta_overwrites_same_key()
test_kda_interference_blends_remote_fact()
test_periodic_mla_recovers_remote_fact()
test_kda_causality()
test_state_growth_ledger()
print("all archetype toy tests passed")
```

Chín test phủ đúng ba claim trung kiến: (1) **A giữ slot-level addressability** — gather đọc nguyên văn entry token và selection nhân quan; (2) **B mất token identity trong group nhưng giữ local window thô** — swap trong group vô hình, perturb trong window thấy được; (3) **C có state cố định, delta overwrite, interference tính tay được, và periodic MLA cứu lại fact** — kèm state-growth ledger ở ba mức tăng trưởng khác nhau.

## 10. Benchmark / Trade-offs

### 10.1 Toy ledger (tính từ cấu hình, không đo timing)

| `T` (token) | Dense/A mỗi layer | B-CSA (group 4, window 4) | B-HCA (group 16, window 4) | C mỗi block 3 KDA + 1 MLA |
|---:|---:|---:|---:|---:|
| 1.024 | 4.096 | 1.036 | 316 | 4.108 (12 + 4.096) |
| 2.048 | 8.192 | 2.060 | 572 | 8.204 (12 + 8.192) |
| Tăng trưởng khi `T` ×2 | ×2 | <×2 | <×2 | ×2 − 0 (chỉ phần MLA) |

Bảng là element counting của toy (đã verify bằng `test_state_growth_ledger`); **không** phải bytes thật và không nói gì về latency — serving thật phụ thuộc dtype, layout, kernel và số layer thực.

### 10.2 Evidence ledger cho các model thật

| Claim | Loại evidence | Phạm vi đúng | Không được kết luận |
|---|---|---|---|
| V4 Pro: 27% FLOPs, 10% KV cache so với V3.2 ở 1M context (Flash: 10%/7%) | author-run estimate | cấu hình V4 cụ thể | end-to-end serving speedup phổ quát; chất lượng compression đã được isolate |
| K3: ~2.5× scaling-efficiency so với K2 | author-run fit trên validation-loss OOD | toàn bộ thay đổi đánh giá jointly | đóng góp riêng của KDA/MLA-hybrid/AttnRes/LatentMoE |
| GLM-5 DSA: 128K evaluations mixed (MV-NIAH, SQuAD cải thiện; HotpotQA kém MLA) | author-run ablation | cấu hình GLM-5 cụ thể | "lossless by construction" như claim của report |
| DSA indexer 90% decode latency ở 1.024K (LongCat profile) | author-run measurement | BF16, batch 4, K=2048 trên HBM | thuộc tính phổ quát của mọi DSA implementation |
| KDA state cố định; K3 cache API hai loại state | cấu trúc kiến trúc từ report và reference code | kiến trúc disclosed | constant-size end-to-end cho toàn model |

Không có matched, independent benchmark chung cho ba archetype; mọi xếp hạng chéo cần experiment đối chứng riêng.[^v4-arch][^k3-arch][^dsa-concept][^glm5-k3-comparison]

## 11. Debug checklist

| Triệu chứng | Nguyên nhân thường gặp | Check đầu tiên |
|---|---|---|
| A chọn sai tập, recall thấp | indexer chưa align (thiếu warm-up), top-k quá nhỏ, distractor tương đồng | in ranked scores quanh oracle positions; đo recall trước quality |
| A chậm hơn dense ở context ngắn | overhead top-k/gather không bù được việc core tiết kiệm | profile indexer, top-k, gather, core tách riêng |
| B trả "đúng vùng, sai chi tiết" | token identity đã aggregate trong entry | test swap-trong-group như mục 9; kiểm tra fact có nằm trong window không |
| B thiếu tail/window state | chỉ build entry ở block boundary, vứt phần dư | log `tail` và `raw_read`; đảm bảo cache giữ uncompressed tail |
| C mất fact ở layer KDA | interference: write sau giao vùng state của fact | reproduce bằng interference test; tăng mật độ layer MLA rồi đo lại |
| C decode khác prefill output | recurrent update và chunkwise path không tương đương | so output prefill từng chunk với decode từng token trên cùng input |
| Ledger nói "nhỏ" nhưng memory không giảm | đếm entries thay vì bytes + dtype + layout | nhân dtype bytes; kiểm tra phần state phụ (conv state, index keys, sink) |
| Cache shape kỳ lạ khi hybrid | hai loại state (recurrent + token-linear) trộn trong một cache API | tách ledger theo loại layer như 10.1 |
| Softmax NaN | query không có entry nào được chọn | luôn bảo đảm local window/self trong read set |
| Copy fact đúng nhưng câu trả lời sai | retrieval đúng là điều kiện cần, không đủ | evaluation cần distractor, multi-hop và vị trí fact đa dạng |

## 12. Giới hạn & bước tiếp theo

Toy không: học indexer (dùng chính keys làm score thay vì ReLU-head network), học trọng số nén (mean thay vì `π` học được), decay theo kênh (scalar), chunkwise training (chỉ recurrence tuần tự), RoPE/NoPE, FP8/FP4, paged cache, nhiều head/batch, và không đo timing. Kết luận quantitative về model thật không rút ra được từ toy.

Bước tiếp theo:

1. Học indexer thật trên synthetic retrieval rồi đo recall theo vị trí fact.
2. Thay mean bằng trọng số học được và đo mất mát exact-copy theo group size.
3. Thêm channel decay vào KDA toy và đo interference theo decay rate.
4. Ghép toy thành block 3:1 KDA/MLA mini và đo exact-copy theo tỉ lệ layer.
5. Đọc tiếp [Recurrent-majority frontier models (Stage 9.7)](recurrent-majority-frontier-models-beginners-course.md) và [Workload-conditioned selection (Stage 9.8)](workload-conditioned-frontier-llm-architecture-selection.md).

## Relationships

- **Depends on:** [MLA và token-addressable memory — bài học cho người mới](mla-token-addressable-memory-beginners-guide.md), [Linear attention như fixed-state associative memory](linear-attention-fixed-state-associative-memory-beginners-guide.md), và [Sparse-attention architecture — khóa học cho người mới](sparse-attention-architecture-beginners-course.md) — ba mảnh cơ chế mà các archetype ghép lại.
- **Uses:** [Multi-head Latent Attention](multi-head-latent-attention.md), [DeepSeek Sparse Attention](deepseek-sparse-attention.md), [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md), [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — core mechanism của từng archetype.
- **Synthesizes:** [DeepSeek-V4 and Kimi K3 architecture comparison](deepseek-v4-and-kimi-k3-architecture-comparison.md), [GLM-5 and Kimi K3 architecture comparison](glm-5-and-kimi-k3-architecture-comparison.md), và [Sparse Attention evolution and architecture comparison](sparse-attention-evolution-and-architecture-comparison.md) thành một khung archetype thống nhất.
- **Elaborates:** Stage 9.6 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md) — archetype matrix và remote-fact trace.
- **Prepares for:** [Recurrent-majority frontier models](recurrent-majority-frontier-models-beginners-course.md) ở Stage 9.7 và [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md).

## Evidence limits

Đây là pedagogical synthesis từ các wiki concept đã duy trì; không mở raw source mới. Cơ chế GLM-5/V4/K3 đến từ các author report và reference code với mọi giới hạn đã ghi ở từng concept (V4 và các comparison của nó đang `draft`; các kết quả đều author-run, không có matched benchmark giữa ba model). Toy code là semantic reference: indexer/decay/compression được cố định thay vì học, không có kernel tối ưu, và các con số output in ra là kết quả chạy một lần trên PyTorch 2.14 CPU — reproducible về mặt thuật toán nhưng không đại diện serving. Test suite đã được thực thi và pass trong môi trường biên soạn; hãy chạy lại trên môi trường của bạn trước khi tin các hằng số cụ thể. Mọi claim về latency, memory thật, và quality của các model thật phải đo lại trên checkpoint, dtype, kernel, hardware và workload đích.[^sparse-evolution][^v4-k3-comparison][^glm5-k3-comparison][^csa-hca][^k3-arch]

[^sparse-evolution]: [Sparse Attention evolution and architecture comparison](sparse-attention-evolution-and-architecture-comparison.md) — synthesis map về access pattern, KV representation, layer allocation; trạng thái `draft`, tổng hợp từ user-supplied map và các report nguồn.
[^v4-k3-comparison]: [DeepSeek-V4 and Kimi K3 architecture comparison](deepseek-v4-and-kimi-k3-architecture-comparison.md) — so sánh thiết kế V4 (compressed token-derived entries) với K3 (fixed-state KDA cộng periodic MLA); `draft`, design comparison không phải performance verdict.
[^glm5-k3-comparison]: [GLM-5 and Kimi K3 architecture comparison](glm-5-and-kimi-k3-architecture-comparison.md) — so sánh GLM-5 (MLA/DSA toàn backbone) với K3; nguồn là các author report và reference implementations.
[^csa-hca]: [Compressed sparse and heavily compressed attention](compressed-sparse-and-heavily-compressed-attention.md) — cơ chế CSA/HCA của DeepSeek-V4 (group 4/128, window 128, FP8/BF16/FP4); `draft`, không có controlled ablation công khai.
[^dsa-concept]: [DeepSeek Sparse Attention](deepseek-sparse-attention.md) — cơ chế indexer + top-k token-level của DSA, training recipe, và các kết quả author-run của DeepSeek-V3.2, GLM-5, LongCat.
[^mla-concept]: [Multi-head Latent Attention](multi-head-latent-attention.md) — latent KV per token, decoupled RoPE, cache tuyến tính; bằng chứng primary từ DeepSeek-V2.
[^kda-concept]: [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — delta update, gated decay, channel-wise decay của KDA và chunkwise training; nguồn là các paper gốc và K3 reference code.
[^k3-arch]: [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — tỉ lệ 69 KDA/24 MLA, NoPE gated MLA, cache API hai loại state, và giới hạn của claim scaling-efficiency.
[^v4-arch]: [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) — cấu hình CSA/HCA xen kẽ và các estimate FLOPs/KV-cache ở 1M context; `draft`.
[^workload-selection]: [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md) — đề xuất chọn archetype theo workload, tự khai là synthesis có điều kiện chứ không phải benchmark verdict.
