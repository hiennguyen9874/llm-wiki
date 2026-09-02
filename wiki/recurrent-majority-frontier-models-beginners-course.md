---
type: Synthesis
title: "Recurrent-majority frontier models: đọc schedule, state và evidence — khóa học cho người mới"
description: A top-down beginner course for decomposing recurrent-majority frontier checkpoints by mixer schedule, periodic attention, residual topology, MoE, conditional memory, modality path, context-growing state, and evidence strength.
tags: [hybrid-attention, recurrent-models, long-context, mixture-of-experts, kv-cache, learning-roadmap, pytorch]
status: stable
created: 2026-09-02
generated:
  by: llm-wiki-agent/1
  at: 2026-09-02T12:04:05+07:00
sources:
  - id: glm-qwen-comparison
    resource: glm-5-3-flash-and-qwen3-8-flash-next-architecture-comparison.md
    title: GLM-5.3-Flash and Qwen3.8-Flash-Next architecture comparison
  - id: glm53-arch
    resource: glm-5-3-flash-hybrid-multimodal-architecture.md
    title: GLM-5.3-Flash hybrid multimodal architecture
  - id: qwen-next-arch
    resource: qwen3-8-flash-next-architecture-and-implementation.md
    title: Qwen3.8-Flash-Next architecture and implementation
  - id: qwen-a95b
    resource: qwen3-8-2-4t-a95b-checkpoint-architecture.md
    title: Qwen3.8-2.4T-A95B checkpoint architecture
  - id: nemotron
    resource: nemotron-3-5-lightning-architecture-and-training.md
    title: Nemotron 3.5 Lightning architecture and training
  - id: ling
    resource: ling-3-0-flash-hybrid-architecture.md
    title: Ling-3.0-flash hybrid architecture
  - id: longcat
    resource: longcat-2-0-sparse-attention-and-embedding-architecture.md
    title: LongCat-2.0 sparse-attention and embedding architecture
  - id: delta-memory
    resource: delta-rule-and-gated-associative-memory.md
    title: Delta-rule and gated associative memory
  - id: qsa
    resource: qwen-sparse-attention.md
    title: Qwen Sparse Attention
  - id: residuals
    resource: residual-path-architecture-comparison.md
    title: Residual-path architecture comparison
  - id: ngram
    resource: n-gram-embeddings-and-conditional-memory.md
    title: N-gram embeddings and conditional memory
  - id: moe
    resource: mixture-of-experts-training-and-systems-trade-offs.md
    title: Mixture-of-Experts training and systems trade-offs
  - id: glm53-eval
    resource: glm-5-3-flash-evaluation-serving-and-evidence-limits.md
    title: GLM-5.3-Flash evaluation, serving, and evidence limits
  - id: qwen-next-eval
    resource: qwen3-8-flash-next-evaluation-and-deployment-limits.md
    title: Qwen3.8-Flash-Next evaluation and deployment limits
  - id: lifecycle
    resource: llm-inference-lifecycle-training-prefill-decode-and-latency.md
    title: LLM inference lifecycle — training, prefill, decode, and latency
---

# Recurrent-majority frontier models: đọc schedule, state và evidence — khóa học cho người mới

Một `recurrent-majority frontier model` không phải là “một recurrent model có thêm attention”, mà là một hệ nhiều trục: phần lớn depth dùng mixer có state cố định; một số layer định kỳ khôi phục token-addressable retrieval; residual path, MoE, conditional memory và modality encoder bổ sung các đường thông tin khác. Bài này dùng GLM-5.3-Flash và Qwen3.8-Flash-Next làm hai checkpoint xuyên suốt để biến tên model thành `per-layer schedule`, `state/cache ledger` và `evidence ledger`; sau đó mới dùng toán và PyTorch để làm chính xác trực giác.[^glm-qwen-comparison][^glm53-arch][^qwen-next-arch]

> [!success] Kết quả cần đạt / Sau bài này
> 1. Giải thích được vấn đề mà recurrent-majority hybrid giải quyết và vì sao periodic attention vẫn cần thiết.
> 2. Phân rã một checkpoint theo bảy trục: `mixer ratio`, `periodic-attention core`, `residual topology`, `MoE`, `conditional memory`, `modality path`, và `context-growing state`.
> 3. Dựng đúng schedule 45 layer của GLM-5.3-Flash và 48 layer của Qwen3.8-Flash-Next từ config/code facts.
> 4. Tách hệ quả trực tiếp của thiết kế khỏi speed/quality claim do vendor báo cáo.
> 5. Chạy PyTorch toy để kiểm tra schedule, fixed-state versus growing cache, delta rewrite và causal behavior.

## 1. Điều cần biết trước

- [Linear attention như fixed-state memory](linear-attention-fixed-state-associative-memory-beginners-guide.md): vì sao state có kích thước cố định có thể bị interference.
- [Delta memory, KDA và hybrid KDA–MLA](delta-memory-kda-hybrid-architecture-beginners-project.md): delta correction, decay và periodic token retrieval.
- [Sparse-attention architecture](sparse-attention-architecture-beginners-course.md): indexer, selected read và retained cache là ba chuyện khác nhau.
- [Mixture-of-Experts và sparse routing](mixture-of-experts-sparse-routing-beginners-guide.md): `total parameters` khác `active parameters`.
- [Depth and residual-path design](depth-and-residual-path-design-beginners-course.md): residual topology là một trục độc lập với sequence mixer.
- [Inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md): tách `prefill`, `decode`, `TTFT` và `TPOT`.

Bài không dạy lại toàn bộ KDA, Gated DeltaNet, DSA/QSA, mHC hoặc MoE kernel. Mục tiêu là **đọc một model tích hợp**. Code là semantic toy, không phải implementation tương thích checkpoint hay serving kernel.

## 2. Bức tranh toàn cảnh

### 2.1 Vấn đề: full attention ở mọi layer làm history trở thành chi phí lặp lại

Trong dense Transformer, mỗi attention layer giữ state theo token và mỗi query đọc một tập history lớn. Khi context dài, cùng một prefix gây áp lực lặp lại qua nhiều layer: cache tăng theo `sequence length × attention depth`, còn việc đọc cache ảnh hưởng memory bandwidth và latency. Recurrent mixer đổi nhiều layer sang một state ma trận có kích thước không tăng theo số token; periodic attention giữ lại vài “trạm truy hồi” nơi token cũ vẫn có địa chỉ riêng.[^delta-memory][^glm-qwen-comparison]

### 2.2 Ý tưởng cốt lõi trong một câu

**Nén phần lớn depth thành recurrent state cố định, nhưng đặt periodic token-addressable attention như các checkpoint để khôi phục khả năng tìm chi tiết theo vị trí.**[^glm-qwen-comparison]

### 2.3 Mental model: tuyến metro và ga trung chuyển

```text
Dense Transformer
  A ─ A ─ A ─ A ─ A ─ A ─ A ─ A
  mỗi ga giữ một kho hồ sơ tăng theo số hành khách/token

Recurrent-majority hybrid
  R ─ R ─ R ─ A ─ R ─ R ─ R ─ A
  R: bảng trạng thái cố định, rẻ để mang sang decode step kế tiếp
  A: ga trung chuyển còn truy cập hồ sơ theo token

Nhưng quanh mỗi R/A còn có các đường khác:
  residual streams ── giữ/chuyển feature qua depth
  MoE              ── chọn FFN capacity theo token
  N-gram memory    ── tra local pattern bằng hash
  vision encoder   ── biến image/video thành feature đi vào text backbone
```

`R` và `A` chỉ mô tả **sequence-mixing path**. Không được dùng mixer ratio để suy ra toàn bộ compute, memory hay quality của model.

### 2.4 Bảy câu hỏi thay cho tên model

| Trục đọc | Câu hỏi phải trả lời | Sai lầm thường gặp |
|---|---|---|
| `mixer ratio` | Bao nhiêu recurrent layer cho mỗi attention layer? Layer nào ở đâu? | Chỉ nói “hybrid” |
| `periodic-attention core` | Global, sparse hay latent? Token nào còn addressable? | Nghĩ mọi periodic attention giống nhau |
| `residual topology` | Một stream hay nhiều stream? Read/write/mixing bị gate hay constraint? | Gán lợi ích residual cho mixer |
| `MoE` | Expert count, top-k, shared expert, active/total/resident là gì? | Dùng active parameters như latency |
| `conditional memory` | Có lookup table không? Key, placement, collision và bandwidth? | Gọi N-gram table là một expert |
| `modality path` | Text-only hay vision features thay placeholder embeddings? | Gọi mọi family là multimodal |
| `context-growing state` | Thành phần nào tăng theo token dù main read là sparse? | “Sparse” hoặc “linear” = cache cố định toàn model |

Sau phần 2–6, người đọc đã có thể trả lời năm câu bắt buộc trước khi gặp công thức đầu tiên: **giải quyết gì, chạy ra sao, tác động gì, khác baseline thế nào, dùng khi nào**.

## 3. Cách hoạt động — nhìn từ đầu đến cuối

### 3.1 Ví dụ xuyên suốt: đọc một repository dài

Giả sử một coding agent nhận repository 500K token. Đầu file có contract: `retry_limit = 7`; gần cuối có function đang cần sửa. Model phải vừa duy trì “gist” của code đã đi qua, vừa truy hồi đúng con số `7` khi tạo patch.

```text
input tokens
  └─► embedding / optional vision replacement
       └─► layer 1..L
            ├─ recurrent layer: state ← update(state, token)
            ├─ periodic attention layer:
            │    index history → select token blocks → attention read
            ├─ residual read/write around branch
            └─ MoE router → selected experts + optional shared expert
       └─► final residual reduction + LM head
            └─► next-token logits / output token
```

- Recurrent layers cố giữ bản tóm lược có thể cập nhật về repository mà không append K/V cho mọi token.
- Periodic attention layers cho query cơ hội tìm lại token chứa `retry_limit = 7`.
- Residual streams quyết định feature nào được mang qua depth và branch output được ghi trở lại đâu.
- MoE chọn transformation capacity; nó không thay sequence memory.
- N-gram memory, nếu có, hỗ trợ local token patterns; nó không thay remote retrieval.
- Vision encoder, nếu có screenshot hoặc diagram, tạo feature rồi đưa chúng vào language backbone.

### 3.2 Checkpoint 1 — GLM-5.3-Flash từ config đến output

Config phát hành mô tả 45 text layers: 11 chu kỳ `KDA, KDA, KDA, DSA`, sau đó một KDA cuối. Vì vậy có 34 KDA và 11 DSA layers. Ba FFN đầu là dense; 42 FFN sau dùng 288 routed experts, top-8 và một shared expert. Cả attention và FFN branch được bao bởi bốn residual streams kiểu mHC. Vision encoder 24 blocks tạo image/video features để thay placeholder embeddings.[^glm53-arch]

```text
layers  1–4 : K K K D
layers  5–8 : K K K D
...
layers 41–44: K K K D
layer     45: K

K = fixed-state KDA
D = pooled DSA: learned pool 4 token → chọn ≤512 pools → đọc ≤2,048 token
```

Luồng ví dụ:

1. `retry_limit = 7` đi qua KDA và cập nhật state tại phần lớn depth.
2. Tại mỗi DSA layer, indexer nhóm bốn token, score các pool rồi main attention đọc token thuộc pool được chọn.
3. Reference code mở rộng latent KV thành K/V 64 heads trước khi cập nhật cache; vì vậy đường code đã phát hành vẫn giữ state tăng theo token tại 11 DSA layers.
4. mHC collapse bốn streams thành branch input, chạy KDA/DSA hoặc MoE, rồi đặt output trở lại bốn streams; carried mixing được xấp xỉ doubly stochastic qua Sinkhorn.
5. Với multimodal input, vision features đi vào cùng text stream trước chuỗi layer; output cuối vẫn là language logits.[^glm53-arch][^glm-qwen-comparison]

### 3.3 Checkpoint 2 — Qwen3.8-Flash-Next từ config đến output

Config phát hành mô tả đúng 12 chu kỳ `GDN, GDN, GDN, QSA`: 36 Gated DeltaNet và 12 QSA layers. Sau mọi mixer là MoE với 512 routed experts, top-10 và một gated shared expert. Bốn Gated Residual streams bao quanh từng mixer/MoE branch. Layer 2 còn có hashed bigram/trigram PLE; vision encoder có 27 blocks.[^qwen-next-arch]

```text
layers  1–4 : G G G Q
layers  5–8 : G G G Q
...
layers 45–48: G G G Q

G = fixed-state Gated DeltaNet, scalar decay
Q = QSA: mean index-key theo block 4 token
         → chọn ≤512 blocks → causal GQA đọc ≤2,048 token
```

Luồng cùng ví dụ:

1. Ba GDN layers liên tiếp cập nhật fixed state bằng delta correction và scalar decay.
2. QSA indexer nén **index key** của mỗi block bốn token bằng mean; main K/V của từng token vẫn được cache riêng.
3. Nếu block chứa `retry_limit = 7` lọt top-k, main GQA đọc các token gốc trong block — pooling phục vụ selection, không thay token K/V bằng một summary entry.
4. Gated Residual dùng feature-wise read gate để tạo branch input và bốn scalar write gates để tiêm output; carried state là identity path, không có Sinkhorn matrix.
5. PLE ở layer 2 hash suffix bigram/trigram để lấy local-pattern vectors. Đây là conditional lookup capacity, không phải long-range KV cache.
6. Vision features thay placeholder embeddings; text attention dùng partial RoPE.[^qsa][^qwen-next-arch][^ngram]

### 3.4 Hai schedule giống hình, nhưng data flow khác ở lõi

| Bước | GLM-5.3-Flash | Qwen3.8-Flash-Next |
|---|---|---|
| Recurrent write | KDA với channel-wise decay | Gated DeltaNet với scalar decay |
| Periodic selection | learned weighted pooling theo nhóm 4 | mean index-key theo block 4 |
| Main attention | NoPE MLA/DSA trong reference path | partial-RoPE GQA + output gate |
| Residual read/write | mHC collapse/place + constrained 4×4 mixing | feature-wise read + scalar writes + identity carry |
| Conditional lookup | không thấy N-gram table trong bundle | PLE bigram/trigram ở layer 2 |
| Modality | 24-block vision encoder | 27-block vision encoder |

Các layer embedding, normalization, MoE transformation và LM head vẫn tồn tại. “Đổi attention” không đồng nghĩa phần còn lại của model biến mất.[^glm-qwen-comparison]

## 4. Tác động

### 4.1 Hệ quả trực tiếp của thiết kế

| Chiều | Lợi ích có thể suy trực tiếp | Chi phí / điều kiện |
|---|---|---|
| Decode state | Recurrent layer không append K/V theo token | Whole model vẫn tăng state tại periodic attention layers |
| Remote retrieval | Periodic attention giữ token-addressable checkpoints | Indexer phải chọn đúng block; selection miss làm token không được đọc |
| Main attention work | Sparse core đọc tối đa khoảng 2,048 selected tokens theo config | Indexer vẫn score prefix/block index; gather locality và kernel quyết định speed |
| Depth flow | Bốn residual streams tăng đường mang feature | Tăng activation/state traffic; mHC và GR có semantics khác nhau |
| Capacity | MoE chỉ kích hoạt một subset experts mỗi token | Tất cả weights vẫn phải resident/offload; routing và all-to-all có thể chi phối[^moe] |
| Local patterns | PLE/N-gram lookup thêm capacity với ít dense FLOPs | Table memory, collision, tokenizer coupling, lookup bandwidth/prefetch |
| Multimodal | Vision path cho image/video đi vào text backbone | Encode cost, token expansion, state handoff và modality quality phải đo riêng |

Fixed-state là thuộc tính **theo layer**, không phải nhãn bảo đảm cho toàn model. Sparse read cũng không đồng nghĩa sparse storage: QSA/DSA vẫn có cache/index tăng theo context ở các periodic layers.[^glm-qwen-comparison][^qsa]

### 4.2 Behavior và quality

- Recurrent state hữu hạn có thể trộn hoặc ghi đè association; periodic attention cung cấp một đường truy hồi token cụ thể để bù lại, nhưng không bảo đảm indexer recall.
- KDA channel-wise decay có control chi tiết hơn GDN scalar decay theo định nghĩa cơ chế; từ đó **không thể** suy ra GLM có quality tốt hơn Qwen vì dimensions, data, optimizer và toàn bộ model đều khác.
- Gated Residual linh hoạt theo feature ở read path; mHC ràng buộc carried mixing. Bảo đảm spectral của mHC không chuyển sang GR, còn benchmark của GR không chứng minh mHC kém hơn trong checkpoint khác.[^delta-memory][^residuals]

### 4.3 Memory, compute và latency

**Điều chắc chắn từ data flow:** số periodic attention layers càng ít thì số layer có state tăng theo context càng ít. **Điều chưa chắc:** TTFT hoặc TPOT giảm bao nhiêu, vì indexer, expanded versus latent cache, dtype, batch, kernel, quantization và hardware đều tham gia.[^lifecycle][^glm-qwen-comparison]

Reference-path accounting cho mỗi token tại một sparse layer là khoảng 33,025 elements ở GLM DSA (expanded main K/V + indexer state) và 1,152 ở Qwen QSA (hai KV heads + index key). Tỉ lệ khoảng 28.7× này chỉ so hai đường code tham chiếu trên cùng cách đếm; nó không phải tỉ lệ total VRAM, latency hay production cache của hai model.[^glm-qwen-comparison]

### 4.4 Claim benchmark phải để ở cột khác

| Claim | Loại evidence | Có thể kết luận | Không thể kết luận |
|---|---|---|---|
| QSA kernel tới 7.6× prefill, 4.9× decode ở 1M | vendor module benchmark | cấu hình tác giả đo nhanh hơn baseline đã chọn | Qwen nhanh hơn GLM end-to-end |
| GLM serving cải thiện 3× so baseline nội bộ | vendor production claim | vendor báo có co-design hệ thống hữu ích | architecture riêng lẻ gây ra 3× |
| Qwen hybrid ablation average 53.81 vs full attention 49.87 ở matched 25B-A3B | author-run smaller-scale ablation | recipe hybrid hữu ích trong setup đó | checkpoint 125B thắng nhờ mixer ratio riêng |
| GLM/Qwen coding, agentic, vision scores | heterogeneous vendor evaluations | capability được báo cáo dưới harness tương ứng | cơ chế recurrent/sparse gây ra score |

Các baseline, hardware, cache policy và harness khác nhau; không ghép hai bảng vendor thành head-to-head ranking.[^glm53-eval][^qwen-next-eval][^qwen-next-arch]

## 5. Sự khác biệt

### 5.1 So với dense baseline và các neighbor gần nhất

| Thiết kế | Giống nhau | Khác nằm ở data flow | Trade-off chính | Khi phù hợp |
|---|---|---|---|---|
| Dense attention mọi layer | Cùng causal LM, residual, FFN, LM head | mọi layer append/read token KV | retrieval mạnh; cache/read cost qua mọi depth | context vừa, exact retrieval quan trọng, kernel dense tốt |
| Recurrent-majority + periodic full attention | vẫn có token checkpoints | đa số layer dùng state cố định; attention layer đọc toàn prefix | giảm attention depth nhưng periodic layer còn full read | long context với periodic global retrieval |
| Recurrent-majority + periodic sparse attention | như trên | periodic layer thêm indexer rồi chỉ gather selected blocks | giảm main read; chịu selection/indexer/kernel cost | context rất dài, top-k recall và locality tốt |
| Attention-centric sparse model | cùng sparse selector | sparse token cache/read ở phần lớn hoặc mọi attention depth | còn context-growing state nhiều layer | cần token addressability dày hơn recurrent hybrid |
| Compressed-entry attention | cùng mục tiêu giảm long-context cost | token cũ bị thay bằng group entries | giảm state mạnh hơn nhưng mất token identity | workload chấp nhận remote summary |

### 5.2 Những khái niệm dễ nhầm

1. **`linear/recurrent` không có nghĩa toàn model fixed-state.** Chỉ recurrent layers fixed-state; periodic attention cache vẫn dài ra.
2. **`sparse attention` không có nghĩa không lưu token.** QSA chọn block để đọc nhưng reference path vẫn cache K/V từng token.
3. **`pooled index` không nhất thiết là pooled value.** Qwen mean index keys để chọn; main attention vẫn đọc token K/V gốc.
4. **MoE sparsity khác attention sparsity.** MoE chọn transformation channel; attention chọn history positions.
5. **N-gram memory khác recurrent memory.** N-gram lookup được address bằng local token IDs; recurrent state được update tuần tự từ hidden features.
6. **Residual depth path khác sequence memory.** Bốn streams giữ feature qua layer, không thay KV/history state.

### 5.3 Family matrix: dùng neighbor để tránh overfit vào hai tên model

| Model | Mixer schedule | Periodic core | Residual / MoE | Conditional memory / modality | Evidence boundary |
|---|---|---|---|---|---|
| GLM-5.3-Flash | 34 KDA + 11 DSA, gần 3:1 | pooled sparse NoPE MLA/DSA | 4-stream mHC; 288 top-8 + shared | không N-gram; native vision | config + reference code + vendor blog[^glm53-arch] |
| Qwen3.8-Flash-Next | 36 GDN + 12 QSA, đúng 3:1 | block-sparse partial-RoPE GQA | 4-stream GR; 512 top-10 + gated shared | 51.2B PLE; native vision | config + reference code + report[^qwen-next-arch] |
| Qwen3.8-A95B | 69 GDN + 23 global GQA, 3:1 | global GQA | ordinary path; 512 top-10 + gated shared | không disclosed PLE; text-only | config + generic reference code[^qwen-a95b] |
| Nemotron 3.5 Lightning | 23 Mamba-2 + 6 GQA; 23 MoE blocks xen kẽ | global GQA | ordinary pre-norm residual; 128 top-6 + shared | text-only | config + code; 1M path chưa giải thích từ 256K metadata[^nemotron] |
| Ling-3.0-flash | 35 KDA + 7 Gated MLA, 5:1 | Gated MLA | 512 top-8 + shared | không đủ disclosure | model card + diagram, không config/code[^ling] |
| LongCat-2.0 | **không phải recurrent-majority** | LSA sparse attention | 1.6T/48B-active MoE claim | 135B N-gram | model card; dùng như negative control[^longcat] |

Bảng cho thấy `recurrent-majority` là một họ quyết định chứ không phải một block duy nhất: recurrent core có thể là delta rule hoặc SSM; attention có thể global hoặc sparse; conditional memory và multimodality là tùy chọn độc lập.

## 6. Trong thực tế

### 6.1 Cơ chế nằm ở đâu trong model/system thật?

```text
request
  ├─ text tokenizer ─────────────────────────────┐
  └─ image/video processor → vision encoder ────┤ (nếu có)
                                                 ▼
      embeddings / feature replacement
                 ▼
      recurrent-majority text backbone
        R R R A ... + residual topology + MoE
                 ▼
      request state handed from prefill to decode
        recurrent conv/state + periodic-attention KV/index cache
                 ▼
      LM head → sampler → streamed tokens
```

Server phải hiểu nhiều loại state, không chỉ `KV cache`: recurrent state, convolution state, periodic K/V, indexer cache và có thể vision encode output. Prefix caching, paging, quantization và worker disaggregation là runtime policy; chúng không nằm trong mixer equation.[^glm53-eval][^lifecycle]

### 6.2 Walkthrough: chọn model cho coding agent đọc repository 500K token

**Yêu cầu:** prompt rất dài, output 2K token, nhiều request chia sẻ cùng repository prefix, cần copy chính xác identifiers.

1. **Đọc config, không đọc marketing name.** Xác nhận native versus extrapolated context. GLM config khai báo 1,048,576; Qwen native 262,144 và card mô tả static YaRN factor 4 cho 1M, kèm cảnh báo chất lượng short input.[^glm53-arch][^qwen-next-arch]
2. **Dựng schedule.** GLM có 11 sparse checkpoints; Qwen có 12. Cả hai còn context-growing state.
3. **Dựng ledger.** Liệt kê recurrent state, conv state, main K/V, index keys/pooling metadata, dtype và batch/concurrency. Không lấy `active parameters` thay cache bytes.
4. **Kiểm tra retrieval.** Dùng needle tasks với identifiers, numbers và code spans ở nhiều depth; đo `selected-block recall` riêng với exact-answer accuracy.
5. **Đo lifecycle.** Tách `TTFT` ở cold prefix, warm-prefix TTFT, `TPOT`, tokens/s và peak memory. 90% prefix-cache hit không đại diện cold repository.
6. **Kiểm tra quality boundary.** Với Qwen 1M, chạy cả short và long prompt vì static YaRN có warning. Với GLM, max-position metadata không tự chứng minh retrieval ổn định ở 1M.
7. **Kiểm tra multimodal nếu cần screenshot.** Đo encode time và số visual tokens riêng; text-only workload không được hưởng lợi tự động từ vision encoder.

### 6.3 Khi nên dùng

- Prompt dài và decode nhiều, nên giảm số depth phải mang token-growing K/V.
- Workload có cả semantic accumulation lẫn remote exact lookup, phù hợp recipe recurrent state + periodic retrieval.
- Runtime có optimized recurrent, sparse-index/gather và MoE kernels; đủ memory/network cho total weights và expert dispatch.
- Có benchmark đúng prompt length, concurrency, dtype, hardware và cache-hit distribution của deployment.

### 6.4 Khi không nên dùng

- Context ngắn, batch nhỏ hoặc runtime chỉ tối ưu dense attention: indexer, multi-stream residual và MoE dispatch có thể thành overhead.
- Workload cần dense exact cross-token interaction ở hầu hết depth mà top-k selector không giữ recall.
- Hardware không chứa/stream được total MoE/N-gram weights dù active FLOPs thấp.
- Chỉ có vendor score nhưng không có config/code/kernel tương thích target stack.

### 6.5 Measurement checklist trước quyết định

| Nhóm | Measurement tối thiểu |
|---|---|
| Quality | task score, exact-copy, long-context recall theo vị trí/độ dài, short-context regression |
| Selection | indexer recall@budget, selected blocks, false negatives, gather locality |
| State | bytes/request theo loại state, peak allocator memory, prefix reuse, quantization error |
| Prefill | cold/warm TTFT, chunk size, tokens/s, indexer versus main-attention time |
| Decode | TPOT distribution, batch/concurrency sweep, memory bandwidth, recurrent update time |
| MoE | per-expert/rank load, all-to-all bytes/time, shared-expert cost, total resident bytes |
| Multimodal | encode latency, visual-token count, state-transfer volume, modality quality |

Không thể suy từ lý thuyết: end-to-end speedup, benchmark quality, one-million-token reliability, energy/cost, production stability hoặc model nào tốt hơn. Những claim đó cần measurement có baseline và workload khớp.

## 7. Toán học — zoom in sau cùng

### 7.1 Bảng ký hiệu

| Ký hiệu | Nghĩa | Shape / đơn vị |
|---|---|---|
| `L` | tổng số sequence-mixing layers | scalar |
| `L_R`, `L_A` | số recurrent và periodic-attention layers | scalar |
| `S` | context length | tokens |
| `B` | batch hoặc concurrent sequences được tính trong ledger | sequences |
| `p` | bytes mỗi cached element | bytes |
| `c_l` | cached elements **mỗi token** tại attention layer `l` | elements/token |
| `f_l` | fixed recurrent/conv elements tại recurrent layer `l` | elements |
| `S_t` | associative recurrent state | `(d_k, d_v)` trong convention dưới |
| `k_t`, `v_t`, `q_t` | key, value, query tại token `t` | `(d_k)`, `(d_v)`, `(d_k)` |
| `α_t`, `β_t` | decay và write/correction strength | scalar trong toy |

### 7.2 Mixer ratio: đo depth nào mang token cache

**Trực giác.** Tỉ lệ recurrent cao làm ít layer append token cache hơn; nó không cho biết bytes mỗi attention layer hoặc cost của MoE.

**Công thức đầu tiên:**

$$
\rho_R=\frac{L_R}{L},\qquad \rho_A=\frac{L_A}{L}=1-\rho_R.
$$

**Ý nghĩa ký hiệu.** `L_R` đếm recurrent mixers, `L_A` đếm periodic attention mixers; FFN-only/MoE blocks phải được phân loại riêng nếu architecture như Nemotron xen chúng thành block độc lập.

**Shape flow.** Đây là scalar accounting, chưa có tensor.

**Ví dụ số.** GLM: `34/45 ≈ 0.756`; Qwen: `36/48 = 0.75`. Hai tỉ lệ gần nhau nhưng periodic cache width khác mạnh, nên ratio không đủ để so memory.[^glm-qwen-comparison]

**Kết luận.** Ratio là hàng đầu tiên của ledger, không phải kết luận cuối.

### 7.3 Trường hợp nhỏ tính tay: `R R R A`

**Trực giác.** Giả sử mỗi `R` giữ 6 fixed elements, còn `A` giữ 3 elements cho mỗi token. Với một sequence (`B=1`) và FP16/BF16 (`p=2` bytes):

```text
S = 2 tokens: fixed = 3×6 = 18 elements; growing = 1×2×3 = 6
S = 5 tokens: fixed = 18 elements; growing = 1×5×3 = 15
```

**Công thức.** Ledger tổng quát cho request state của các mixer là:

$$
M(S)=pB\left(\sum_{l\in R} f_l + S\sum_{l\in A}c_l\right).
$$

**Ý nghĩa.** Tổng đầu không phụ thuộc `S`; tổng sau tăng tuyến tính theo `S`. Metadata, allocator fragmentation, activation workspace, model weights và vision state chưa được tính.

**Shape flow.** Recurrent state của layer `l` có tensor cố định, ví dụ `(B,H,d_k,d_v)`; attention cache có token axis, ví dụ `(B,H_KV,S,d_h)` cho K và V, cộng index state model-specific.

**Ví dụ số.** Toy `R R R A`:

$$
M(2)=2(18+6)=48\ \text{bytes},\qquad M(5)=2(18+15)=66\ \text{bytes}.
$$

**Kết luận.** Whole-model state vẫn tăng dù 75% mixers là fixed-state.

### 7.4 Áp ledger vào hai reference paths

**Trực giác.** Cùng 3:1 schedule nhưng slope phụ thuộc representation được cache tại `A`.

**Công thức slope theo thêm một token:**

$$
\frac{\Delta M}{\Delta S}=pB\sum_{l\in A}c_l.
$$

**Ví dụ số.** Với `B=1`, `p=2` và chỉ dùng raw reference counts đã kiểm tra:

- GLM: `11 × 33,025 × 2 = 726,550 bytes` cho mỗi token context thêm vào; tại `S=1,048,576`, riêng phần growing được đếm xấp xỉ `709.5 GiB`.
- Qwen: `12 × 1,152 × 2 = 27,648 bytes/token`; tại native `S=262,144`, xấp xỉ `6.75 GiB`, và nếu chỉ tuyến tính hóa cùng representation tới 1M thì `27 GiB`.

Những số rất lớn của GLM phản ánh `expand_kv()` trong **reference code**, không phải chứng minh production engine dùng layout đó. Cả hai phép tính loại trừ recurrent/conv state, weights, allocator, quantization và runtime metadata.[^glm-qwen-comparison]

**Kết luận.** `mixer ratio` giống nhau nhưng `cache slope` có thể khác hàng chục lần; vẫn không được đổi cache ratio thành latency ratio.

### 7.5 Delta correction: vì sao recurrent state không dài thêm

**Trực giác.** Memory là một bảng cố định. Token mới đọc association hiện tại tại key của nó rồi sửa lỗi thay vì nối thêm một row.

**Công thức DeltaNet cơ bản:**

$$
S_t=(I-\beta_t k_tk_t^\top)S_{t-1}+\beta_tk_tv_t^\top,
\qquad o_t=S_t^\top q_t.
$$

**Ý nghĩa.** `k_t k_tᵀ` chọn subspace cần sửa; `β_t` quyết định mức sửa; `k_t v_tᵀ` ghi association mới; `q_t` đọc state. Gated DeltaNet thêm scalar decay; KDA dùng channel-wise decay, cho retention control chi tiết hơn.[^delta-memory]

**Shape flow.** `k_t:(d_k) → k_tk_tᵀ:(d_k,d_k)`; nhân `S_{t-1}:(d_k,d_v)` vẫn ra `(d_k,d_v)`; outer product `k_tv_tᵀ` cũng `(d_k,d_v)`; output `S_tᵀq_t:(d_v)`.

**Ví dụ số.** Chọn `d_k=d_v=2`, state zero, `k=[1,0]`, `v=[7,0]`, `β=1`. Sau write, hàng được key thứ nhất chọn chứa `[7,0]`; query cùng key đọc đúng `[7,0]`. Write sau với cùng key và `v=[9,0]` thay association thành `[9,0]` thay vì append token thứ hai.

**Kết luận.** State shape không đổi từ token 1 đến token một triệu; cái mất là slot identity riêng cho từng token, nên interference vẫn có thể xảy ra.

### 7.6 Periodic sparse attention: tìm block rồi đọc token

**Trực giác.** Indexer rẻ chọn shortlist; main attention đắt chỉ chạy trên shortlist. Selection và value representation là hai bước khác nhau.

**Công thức giản lược cho QSA block size `r`:**

$$
\bar k_b=\frac{1}{r}\sum_{i\in b}k_i^{idx},\qquad
\mathcal B_t=\operatorname{TopK}_b\,s(q_t^{idx},\bar k_b),
$$

$$
o_t=\operatorname{softmax}\!\left(\frac{q_tK_{\mathcal I_t}^{\top}}{\sqrt{d_h}}+m_t\right)V_{\mathcal I_t},
\qquad \mathcal I_t=\bigcup_{b\in\mathcal B_t}b.
$$

**Ý nghĩa.** `k_idx` chỉ phục vụ indexer; `I_t` chứa token indices của selected blocks; `K,V` là main-attention cache; `m_t` giữ causality.

**Shape flow.** Với `N` cached tokens: index keys `(N,d_idx)` → block keys `(N/r,d_idx)` → scores `(N/r)` → selected indices `(Kr)` → main K/V `(Kr,d_h)` → output `(d_h)`.

**Ví dụ số.** `N=16`, `r=4`, `K=2`: indexer score 4 blocks; main attention đọc 8 token thay vì 16. Nhưng cache vẫn có 16 token K/V và indexer keys.[^qsa]

**Kết luận.** Main read giảm; storage và index scan không biến mất.

### 7.7 Derivation có thể bỏ qua: linear state cộng periodic slope

Từ ledger, tăng context từ `S` lên `S+ΔS` giữ nguyên mọi `f_l`:

$$
M(S+\Delta S)-M(S)
=pB\Delta S\sum_{l\in A}c_l.
$$

Vì vậy recurrent-state size không ảnh hưởng **slope theo context**, nhưng vẫn ảnh hưởng intercept và runtime update cost. Giảm `L_A` hoặc `c_l` giảm slope; chỉ giảm selected read budget không nhất thiết giảm `c_l` nếu vẫn cache toàn bộ K/V.

## 8. Implementation — PyTorch tối thiểu

Code dưới cụ thể hóa ba việc đã giải thích: dựng schedule, tính state ledger, và quan sát fixed delta state versus causal token cache. Nó không mô phỏng mHC/GR, MoE, vision, block indexer hay optimized kernels; `torch.cat` chỉ để dạy cache growth, không phải serving design.

```python
from dataclasses import dataclass
import torch

DTYPE = torch.float64  # verification ổn định trên CPU
RTOL, ATOL = 1e-7, 1e-9


def periodic_schedule(num_layers: int, period: int = 4, tail_recurrent: int = 0):
    """One-indexed periodic attention: period, 2*period, ...; optional R tail."""
    schedule = ["R" if (i + 1) % period else "A" for i in range(num_layers)]
    for i in range(tail_recurrent):
        schedule[-1 - i] = "R"
    return schedule


@dataclass(frozen=True)
class StateSpec:
    name: str
    schedule: tuple[str, ...]
    attention_elements_per_token: int
    recurrent_elements_per_layer: int

    @property
    def recurrent_layers(self):
        return self.schedule.count("R")

    @property
    def attention_layers(self):
        return self.schedule.count("A")

    def elements(self, seq_len: int, batch: int = 1):
        fixed = batch * self.recurrent_layers * self.recurrent_elements_per_layer
        growing = (
            batch * seq_len * self.attention_layers
            * self.attention_elements_per_token
        )
        return {"fixed": fixed, "growing": growing, "total": fixed + growing}


# Config-derived schedule; recurrent_elements_per_layer is toy-only.
GLM = StateSpec(
    "GLM-5.3-Flash reference",
    tuple(periodic_schedule(45, period=4, tail_recurrent=1)),
    attention_elements_per_token=33_025,
    recurrent_elements_per_layer=6,
)
QWEN = StateSpec(
    "Qwen3.8-Flash-Next reference",
    tuple(periodic_schedule(48, period=4)),
    attention_elements_per_token=1_152,
    recurrent_elements_per_layer=6,
)


class DeltaMemory:
    """Pedagogical fixed-state delta memory, one matrix per batch item."""
    def __init__(self, batch: int, d_key: int, d_value: int):
        self.state = torch.zeros(batch, d_key, d_value, dtype=DTYPE)

    def step(self, key, value, beta=1.0):
        # key: (B, d_key), value: (B, d_value)
        current = torch.einsum("bkv,bk->bv", self.state, key)
        error = value - current
        self.state = self.state + beta * torch.einsum("bk,bv->bkv", key, error)
        return torch.einsum("bkv,bk->bv", self.state, key)


class GrowingKV:
    """Teaching cache: token axis grows; production uses paged/preallocated storage."""
    def __init__(self, batch: int, d: int):
        self.k = torch.empty(batch, 0, d, dtype=DTYPE)
        self.v = torch.empty(batch, 0, d, dtype=DTYPE)

    def append(self, key, value):
        self.k = torch.cat([self.k, key[:, None, :]], dim=1)
        self.v = torch.cat([self.v, value[:, None, :]], dim=1)

    def read(self, query):
        scores = torch.einsum("bd,bsd->bs", query, self.k)
        weights = torch.softmax(scores, dim=-1)
        return torch.einsum("bs,bsd->bd", weights, self.v)


def causal_attention(q, k, v):
    """Full-sequence causal reference; q/k/v: (B, S, D)."""
    scores = torch.einsum("btd,bsd->bts", q, k) / (q.shape[-1] ** 0.5)
    mask = torch.triu(
        torch.ones(q.shape[1], k.shape[1], dtype=torch.bool), diagonal=1
    )
    weights = torch.softmax(scores.masked_fill(mask, float("-inf")), dim=-1)
    return torch.einsum("bts,bsd->btd", weights, v)


def run_tests():
    # 1) Config-derived layer counts and exact attention positions.
    assert (GLM.recurrent_layers, GLM.attention_layers) == (34, 11)
    assert (QWEN.recurrent_layers, QWEN.attention_layers) == (36, 12)
    assert [i + 1 for i, x in enumerate(GLM.schedule) if x == "A"] == list(range(4, 45, 4))
    assert [i + 1 for i, x in enumerate(QWEN.schedule) if x == "A"] == list(range(4, 49, 4))

    # 2) Ledger slope: adding one token changes only growing state.
    g8, g9 = GLM.elements(8), GLM.elements(9)
    torch.testing.assert_close(
        torch.tensor(g9["fixed"], dtype=DTYPE),
        torch.tensor(g8["fixed"], dtype=DTYPE), rtol=RTOL, atol=ATOL,
    )
    torch.testing.assert_close(
        torch.tensor(g9["growing"] - g8["growing"], dtype=DTYPE),
        torch.tensor(11 * 33_025, dtype=DTYPE), rtol=RTOL, atol=ATOL,
    )

    # 3) Fixed-state shape is unchanged after any number of writes.
    memory = DeltaMemory(batch=1, d_key=2, d_value=2)
    original_shape = memory.state.shape
    key = torch.tensor([[1.0, 0.0]], dtype=DTYPE)
    for value_scalar in [7.0, 8.0, 9.0, 10.0]:
        value = torch.tensor([[value_scalar, 0.0]], dtype=DTYPE)
        memory.step(key, value)
    assert memory.state.shape == original_shape

    # 4) Delta correction rewrites the addressed association exactly here.
    got = memory.step(key, torch.tensor([[11.0, 0.0]], dtype=DTYPE))
    torch.testing.assert_close(
        got, torch.tensor([[11.0, 0.0]], dtype=DTYPE), rtol=RTOL, atol=ATOL
    )

    # 5) Token cache grows by one slot per append and can read a matching key.
    cache = GrowingKV(batch=1, d=2)
    cache.append(torch.tensor([[1.0, 0.0]], dtype=DTYPE),
                 torch.tensor([[7.0, 0.0]], dtype=DTYPE))
    cache.append(torch.tensor([[0.0, 1.0]], dtype=DTYPE),
                 torch.tensor([[0.0, 3.0]], dtype=DTYPE))
    assert cache.k.shape == (1, 2, 2) and cache.v.shape == (1, 2, 2)
    expected = torch.softmax(torch.tensor([[8.0, 0.0]], dtype=DTYPE), dim=-1)
    expected = expected @ torch.tensor([[[7.0, 0.0], [0.0, 3.0]]], dtype=DTYPE)[0]
    torch.testing.assert_close(
        cache.read(torch.tensor([[8.0, 0.0]], dtype=DTYPE)),
        expected, rtol=RTOL, atol=ATOL,
    )

    # 6) Future-token perturbation cannot change earlier causal outputs.
    torch.manual_seed(0)
    q = torch.randn(1, 5, 3, dtype=DTYPE)
    k = torch.randn(1, 5, 3, dtype=DTYPE)
    v = torch.randn(1, 5, 3, dtype=DTYPE)
    before = causal_attention(q, k, v)
    k2, v2 = k.clone(), v.clone()
    k2[:, 4] += 100.0
    v2[:, 4] -= 100.0
    after = causal_attention(q, k2, v2)
    torch.testing.assert_close(before[:, :4], after[:, :4], rtol=RTOL, atol=ATOL)

    # 7) Raw per-sparse-layer accounting ratio from released reference paths.
    torch.testing.assert_close(
        torch.tensor(33_025 / 1_152, dtype=DTYPE),
        torch.tensor(28.66753472222222, dtype=DTYPE), rtol=RTOL, atol=ATOL,
    )
    print("7 tests passed")


if __name__ == "__main__":
    run_tests()
```

### Mapping code về cơ chế

| Code | Cơ chế đã học | Điều code cố ý bỏ qua |
|---|---|---|
| `periodic_schedule` | `R R R A` theo depth | config parser, irregular schedules |
| `StateSpec.elements` | fixed intercept + context-linear slope | conv/index metadata chi tiết, allocator, quantization |
| `DeltaMemory` | state shape cố định, key-addressed correction | GDN/KDA projections, decay, multi-head, chunkwise kernel |
| `GrowingKV` | token axis tăng ở periodic attention | sparse block index, paged cache, RoPE, GQA/MLA projections |
| `causal_attention` | future leakage phải bằng zero | sparse selection và optimized kernel |

## 9. Verification trước benchmark

Chạy block code thành một file, ví dụ:

```bash
python3 recurrent_majority_toy.py
```

Expected output:

```text
7 tests passed
```

Các test có mục đích khác nhau:

1. **Schedule count:** ngăn off-by-one làm sai 34/11 và 36/12.
2. **Ledger slope:** xác nhận thêm token không đổi fixed component.
3. **State-shape invariant:** nhiều write không tạo token axis trong recurrent memory.
4. **Delta rewrite:** cùng key được sửa về value mới trong toy trực giao.
5. **Growing cache:** periodic attention giữ slot theo token.
6. **Future leakage:** causal output ở positions 1–4 không đổi khi position 5 bị perturb.
7. **Reference accounting:** khóa phép chia 33,025/1,152; không biến nó thành runtime claim.

Dùng `float64` để kiểm tra semantic equality trên CPU. Nếu đổi sang BF16/FP16 hoặc fused kernels, phải nới `rtol/atol` dựa trên measured numerical error, không sao chép tolerance mù quáng.

## 10. Benchmark / Trade-offs

### 10.1 Protocol đúng phạm vi

| Sweep | Giữ cố định | Đo riêng | Câu hỏi |
|---|---|---|---|
| Context `8K→64K→256K→1M` | batch, output length, dtype | TTFT, TPOT, peak state bytes | slope xuất hiện ở đâu? |
| Concurrency `1→N` | prompt distribution | throughput, p50/p95 TPOT | recurrent/MoE kernels có batch hiệu quả không? |
| Cold vs warm prefix | prompt và output | TTFT, cache-hit rate | speed đến từ architecture hay prefix reuse? |
| Dense vs sparse attention | checkpoint/weights nếu ablation có thể | indexer time, gather time, recall | selector có bù overhead không? |
| Native vs extrapolated context | task set | short/long quality | positional scaling có regression không? |
| Text vs multimodal | text task matched | encode time, visual tokens, memory | vision path thêm cost bao nhiêu? |

### 10.2 State ledger cần báo cáo

Với standard GQA layer, raw K/V bytes thường được ghi:

$$
M_{KV}=2L_ABSH_{KV}d_hp.
$$

Nhưng GLM/Qwen ở đây cần ledger theo implementation: cộng main K/V hoặc latent representation thực sự được cache, index keys/pooling scores/validity, recurrent matrix state và convolution state. Báo cả logical bytes lẫn allocator peak. Công thức standard không được dùng để che model-specific expanded cache.[^glm-qwen-comparison]

### 10.3 Không kết luận quá phạm vi

- Toy không benchmark CUDA, sparse gather, MoE all-to-all hay vision encoder.
- FLOPs thấp hơn không bảo đảm latency thấp hơn.
- Cache bytes thấp hơn không bảo đảm throughput cao hơn nếu kernel/dispatch kém.
- Một triệu token “supported” không bảo đảm remote recall hoặc useful quality ở toàn range.
- Vendor ablation nhỏ không cô lập mọi thay đổi của released checkpoint.

## 11. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
|---|---|---|
| Count layer sai 1 | zero-index versus one-index; tail layer đặc biệt | in toàn bộ `layer_types` cùng indices |
| Gọi model 3:1 nhưng count không khớp | period rule bị áp sau layer cuối | so count từ config, không suy từ diagram |
| Cache “fixed” vẫn tăng | periodic K/V hoặc indexer cache bị bỏ khỏi ledger | log tensor shapes theo layer sau mỗi decode step |
| Sparse attention không nhanh | Python mask loop, gather rời rạc, indexer overhead | profile indexer/main attention/gather riêng |
| Long-context exact copy kém | block selection miss hoặc recurrent interference | đo index recall trước answer accuracy |
| OOM dù active params thấp | total MoE/N-gram weights và KV state | tách resident/accessed/active bytes |
| Qwen short prompt regression sau 1M config | static YaRN factor dùng mọi input | A/B native 256K config và extended config |
| Multimodal TTFT cao | vision encode/token expansion | profile encode riêng prefill |
| Output trước token tương lai đổi | causal mask/index offset/cache bug | chạy future-perturbation test |
| GLM ledger vô lý lớn | đang đếm expanded reference K/V như production layout | inspect object thực sự đưa vào cache runtime |

## 12. Giới hạn & bước tiếp theo

Bài này thiết lập một **phương pháp đọc**, không xếp hạng GLM, Qwen, Nemotron, Ling hay LongCat. Hai checkpoint chính có config/reference code nên schedule và raw ledger được kiểm tra ở mức implementation; Ling và LongCat không có disclosure tương đương. Các source concept về mHC, N-gram và MoE hiện có một số trang ở trạng thái `draft`, nên course chỉ dùng chúng để giải thích boundary đã được checkpoint/report hỗ trợ, không mở rộng thành claim phổ quát.

Bước tiếp theo:

1. Áp worksheet bảy trục cho [Qwen3.8-A95B](qwen3-8-2-4t-a95b-checkpoint-architecture.md) và [Nemotron 3.5 Lightning](nemotron-3-5-lightning-architecture-and-training.md).
2. Đọc [Workload-conditioned architecture selection](workload-conditioned-frontier-llm-architecture-selection.md) ở Stage 9.8 để biến ledger thành requirement và ablation plan.
3. Khi có target hardware, thay semantic toy bằng runtime thật và báo `prefill/decode` tách biệt.

## Relationships

- **Depends on:** [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md) — nền tảng fixed-state correction của KDA/Gated DeltaNet.
- **Uses:** [Sparse-attention architecture](sparse-attention-architecture-beginners-course.md) — tách indexer, selected read và retained cache.
- **Uses:** [Residual-path architecture comparison](residual-path-architecture-comparison.md) — phân biệt mHC và Gated Residual.
- **Uses:** [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md) — tách active compute khỏi resident weights/communication.
- **Elaborates:** Stage 9.7 of [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).
- **Prepares for:** [Workload-conditioned frontier LLM architecture selection](workload-conditioned-frontier-llm-architecture-selection.md) — Stage 9.8.

## Evidence limits

Đây là synthesis sư phạm từ wiki concepts. Config và reference code hỗ trợ schedule, dimensions, state loại nào tăng theo token, và raw reference cache accounting cho GLM/Qwen; chúng không chứng minh optimized-kernel behavior. Vendor blogs/reports hỗ trợ các con số speed, quality, context và serving chỉ trong setup được công bố. Không có controlled head-to-head GLM–Qwen, production telemetry, independent replication hoặc matched hardware benchmark. PyTorch toy xác minh invariants của mô hình giản lược, không xác minh checkpoint weights, chunkwise kernels, mHC/GR, MoE, vision hay one-million-token behavior.

[^glm-qwen-comparison]: [GLM-5.3-Flash and Qwen3.8-Flash-Next architecture comparison](glm-5-3-flash-and-qwen3-8-flash-next-architecture-comparison.md), schedule, raw reference cache accounting, residual comparison, and evidence limits.
[^glm53-arch]: [GLM-5.3-Flash hybrid multimodal architecture](glm-5-3-flash-hybrid-multimodal-architecture.md), text schedule, DSA/KDA state, MoE, mHC, vision path, and release boundaries.
[^qwen-next-arch]: [Qwen3.8-Flash-Next architecture and implementation](qwen3-8-flash-next-architecture-and-implementation.md), language schedule, QSA/GDN, Gated Residual, PLE, vision, context, and report-backed ablations.
[^qwen-a95b]: [Qwen3.8-2.4T-A95B checkpoint architecture](qwen3-8-2-4t-a95b-checkpoint-architecture.md), 92-layer text-only schedule and implementation limits.
[^nemotron]: [Nemotron 3.5 Lightning architecture and training](nemotron-3-5-lightning-architecture-and-training.md), exact 52-block schedule, state types, and context/MTP gaps.
[^ling]: [Ling-3.0-flash hybrid architecture](ling-3-0-flash-hybrid-architecture.md), model-card/diagram-bounded 35-KDA/7-MLA schedule and unresolved context claims.
[^longcat]: [LongCat-2.0 sparse-attention and embedding architecture](longcat-2-0-sparse-attention-and-embedding-architecture.md), card-bounded LSA and 135B N-gram design.
[^delta-memory]: [Delta-rule and gated associative memory](delta-rule-and-gated-associative-memory.md), delta correction, scalar versus channel-wise decay, chunkwise training, and fixed-state limits.
[^qsa]: [Qwen Sparse Attention](qwen-sparse-attention.md), block indexer, main GQA path, context-growing cache, training, and kernel evidence limits.
[^residuals]: [Residual-path architecture comparison](residual-path-architecture-comparison.md), ordinary residual, mHC, Gated Residual, AttnRes and guarantee boundaries.
[^ngram]: [N-gram embeddings and conditional memory](n-gram-embeddings-and-conditional-memory.md), lookup mechanism, Qwen PLE implementation, systems costs, and source limits.
[^moe]: [Mixture-of-Experts training and systems trade-offs](mixture-of-experts-training-and-systems-trade-offs.md), routing, capacity, resident weights, communication, and evidence limits.
[^glm53-eval]: [GLM-5.3-Flash evaluation, serving, and evidence limits](glm-5-3-flash-evaluation-serving-and-evidence-limits.md), vendor benchmark, context, EPD serving, and telemetry limits.
[^qwen-next-eval]: [Qwen3.8-Flash-Next evaluation and deployment limits](qwen3-8-flash-next-evaluation-and-deployment-limits.md), heterogeneous evaluation, native/extended context, and release boundary.
[^lifecycle]: [LLM inference lifecycle](llm-inference-lifecycle-training-prefill-decode-and-latency.md), prefill/decode state and measurement definitions.
