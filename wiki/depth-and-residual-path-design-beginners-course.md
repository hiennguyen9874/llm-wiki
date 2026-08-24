---
type: Synthesis
title: "Depth and residual-path design — khóa học cho người mới"
description: A top-down beginner course on standard residual flow, Attention Residuals depth retrieval, and manifold-constrained multi-channel mixing, from mechanism and deployment impact to derivation, PyTorch, and verification.
tags: [learning-roadmap, residual-connections, attention-residuals, hyper-connections, depth, pytorch]
status: stable
created: 2026-08-15
generated:
  by: llm-wiki-agent/1
  at: 2026-08-24T12:00:00Z
sources:
  - id: transformer-concept
    resource: transformer-sequence-transduction-architecture.md
    title: "Transformer sequence transduction architecture"
  - id: attnres-concept
    resource: attention-residuals.md
    title: "Attention Residuals"
  - id: attnres-eval
    resource: attention-residuals-evaluation-and-systems-trade-offs.md
    title: "Attention Residuals evaluation and systems trade-offs"
  - id: mhc-concept
    resource: manifold-constrained-hyper-connections.md
    title: "Manifold-constrained Hyper-Connections"
  - id: kimi-k3-concept
    resource: kimi-k3-hybrid-retrieval-architecture.md
    title: "Kimi K3 hybrid retrieval architecture"
  - id: deepseek-v4-concept
    resource: deepseek-v4-hybrid-architecture-and-pretraining.md
    title: "DeepSeek-V4 hybrid architecture and pretraining"
---

# Depth and residual-path design — khóa học cho người mới

`Residual path` (đường truyền tắt theo chiều sâu) quyết định representation nào được mang từ các layer cũ đến layer mới. `Standard residual` cộng dồn mọi update; `Attention Residuals` (`AttnRes`) cho layer mới chọn giữa các nguồn theo **depth**; `manifold-constrained Hyper-Connections` (`mHC`) giữ nhiều `residual channels` và trộn chúng bằng một mapping có ràng buộc. Cả ba đều xử lý information flow giữa các layer, không thay thế `causal token attention`, `KV cache` hay positional mechanism.[^transformer-concept][^attnres-concept][^mhc-concept]

> [!success] Sau bài này
> 1. Bạn có thể giải thích **vấn đề → cơ chế → tác động → khác biệt → cách dùng thực tế** trước khi dùng công thức.
> 2. Bạn có thể theo dõi một token qua `standard residual`, Full/Block `AttnRes`, và `mHC` mà không nhầm `sequence axis` với `depth axis`.
> 3. Bạn có thể derive các update quan trọng, theo dõi tensor shapes, chạy PyTorch toy implementation và kiểm chứng bằng `torch.testing.assert_close`.
> 4. Bạn có thể tách hệ quả trực tiếp của thiết kế khỏi benchmark và systems result chỉ được tác giả báo cáo.

## 1. Điều cần biết trước

Bạn chỉ cần hiểu trực giác về một `decoder-only Transformer block`: `self-attention` trao đổi thông tin giữa token positions, `FFN` biến đổi từng position, còn residual connection đưa input của sublayer đi tiếp. Nếu chưa quen, đọc [Attention: beginner's guide](attention-beginner-guide.md) và [Modern decoder-block recipe](modern-decoder-block-recipe-beginners-course.md).

Bài này không triển khai token attention, `RoPE`, `KV cache`, `MoE`, distributed kernels hay full production model. Vì code không có positional attention nên không có `position_ids` hoặc quy ước `interleaved RoPE`; đó là omission có chủ ý, không phải phần bị ẩn trong residual mixer.

## 2. Bức tranh toàn cảnh

### 2.1 Vấn đề: model sâu cần vừa giữ, vừa biến đổi thông tin

Mỗi layer nhận một representation, tạo một update, rồi chuyển kết quả cho layer tiếp theo. Nếu layer mới phải xây representation lại từ đầu, information và gradient khó có đường đi trực tiếp qua stack sâu. `Standard residual` giải quyết bằng một identity highway: giữ input cũ và cộng update mới. Original Transformer dùng residual connection quanh từng sublayer, cùng `LayerNorm`.[^transformer-concept]

Nhưng phép cộng mặc định không hỏi update cũ nào hữu ích hơn cho token hiện tại. Khi model rất sâu, layer trên chỉ nhận một tổng đã gộp; contribution từ các depth trước không còn là các nguồn riêng để chọn. `AttnRes` biến các representation theo depth thành nguồn có thể retrieval. `mHC` đi theo hướng khác: duy trì nhiều lanes song song và kiểm soát cách chúng được carry, read và write.[^attnres-concept][^mhc-concept]

**Ý tưởng cốt lõi trong một câu:** residual design chọn cách information được **giữ, chọn hoặc trộn qua depth**, trong khi token attention chọn information qua **sequence positions**.

### 2.2 Mental model: tòa nhà nhiều tầng

Hãy tưởng tượng một hồ sơ đi qua tòa nhà:

```text
standard residual
  mỗi tầng ghi thêm vào cùng một hồ sơ đang tích lũy
  tầng trên nhận: một hồ sơ tổng

Full AttnRes
  mỗi tầng cũ giữ một bản ghi riêng trên kệ
  tầng trên nhận: mixture được chọn từ mọi bản ghi cũ

Block AttnRes
  mỗi cụm tầng nộp một bản tóm tắt
  tầng trên nhận: mixture từ vài bản tóm tắt + phần đang viết

mHC
  hồ sơ chạy trên nhiều làn song song
  mỗi tầng đọc mixture của các làn, xử lý, rồi ghi lại vào các làn
```

Mental model này cho thấy hai trade-off khác nhau:

- `AttnRes` đổi **source granularity theo depth**: một tổng, từng layer, hay từng block.
- `mHC` đổi **số residual channels tại mỗi depth**: một lane hay nhiều lanes.

### 2.3 Hai trục tuyệt đối không được nhầm

```text
sequence axis — bên trong một layer

token 0 ─ token 1 ─ token 2 ─ ... ─ token T-1
             causal attention chọn token positions được đọc


depth axis — qua nhiều layers, cho cùng một token position

embedding ─ layer 1 ─ layer 2 ─ ... ─ layer L
             residual design quyết định representation nào đi tiếp
```

`AttnRes` có chữ “Attention” nhưng không tạo score matrix giữa mọi cặp token. Nó trộn sources theo depth cho từng token position. Nếu token-attention branch nhìn lén tương lai, residual mixer không sửa được lỗi causality đó.[^attnres-concept]

### 2.4 Ví dụ xuyên suốt

Xét token **“Paris”** trong câu: “Paris là thủ đô của Pháp”. Qua stack, ta minh họa các update như sau:

| Depth source | Thông tin minh họa mà update nhấn mạnh |
| --- | --- |
| embedding | identity và lexical features của “Paris” |
| layer 1 | entity type: thành phố |
| layer 2 | relation: “thủ đô của” |
| layer 3 | country link: Pháp |

Đây là analogy về representation, không phải claim rằng mỗi layer thật có đúng một vai trò. Ta sẽ theo cùng token này qua mọi cơ chế.

## 3. Cách hoạt động — nhìn từ input đến output

### 3.1 Baseline: `standard residual`

```text
input representation ───────────────┐
        │                            │ identity path
        └─► Norm ─► layer branch ───┤
                                     ▼
                              element-wise add ─► output
```

Luồng đầu đến cuối:

1. Layer nhận representation hiện tại của mọi token.
2. `Norm` chuẩn bị scale cho attention hoặc FFN branch trong `pre-norm` variant.
3. Branch tạo một update có cùng shape với input.
4. Identity path mang input đi thẳng.
5. Hai tensor được cộng để tạo input cho bước tiếp theo.

Trong ví dụ “Paris”, hồ sơ sau layer 3 chứa embedding cộng các update về entity, relation và country. Layer 4 không được chọn riêng update của layer 2; nó nhận hồ sơ tổng đã tích lũy.

### 3.2 Full `AttnRes`: retrieval trên depth

```text
embedding source ─ normalize ─ score ─┐
layer-1 update  ─ normalize ─ score ──┼─► softmax trên depth
layer-2 update  ─ normalize ─ score ──┤           │
layer-3 update  ─ normalize ─ score ──┘           ▼
                                      weighted mixture ─► layer input
```

Luồng đầu đến cuối:

1. **Retain:** giữ embedding và các earlier layer outputs như các depth sources riêng.
2. **Normalize for scoring:** chuẩn hóa từng source để magnitude đơn thuần không quyết định score.
3. **Score:** target layer dùng một learned `pseudo-query` để chấm mỗi source, riêng tại từng batch item và token position.
4. **Compete:** `softmax` chạy trên depth sources; trọng số không âm và tổng bằng một.
5. **Mix:** weighted sum của source gốc tạo input cho target layer.
6. **Transform:** attention/FFN branch bên trong layer vẫn chạy như trước.

Với token “Paris”, target layer có thể đặt weight cao hơn cho source mang country relation và thấp hơn cho update ít liên quan. Đây là selective depth retrieval; token “Pháp” ở position khác vẫn chỉ được truy cập qua token attention bên trong branch.[^attnres-concept]

`Pseudo-query` được học theo target layer nhưng không được tạo mới từ input token. Dù query parameter giống nhau giữa positions, source contents khác nhau nên scores và weights vẫn có thể khác theo token. Zero initialization làm mọi source có score bằng nhau lúc đầu, vì vậy mixture ban đầu là average đều, không phải residual sum.[^attnres-concept]

### 3.3 Block `AttnRes`: retrieval từ summaries

Full form giữ từng earlier layer output. Block form gộp nhiều consecutive layers thành một summary:

```text
layers 1–4  ─► summary A ─┐
layers 5–8  ─► summary B ─┼─► depth softmax ─► mixture
layers 9–... đang chạy ───┘
```

Tại một layer bên trong block hiện tại, sources gồm:

- embedding source;
- summaries của completed blocks;
- partial sum của current block sau khi đã có update trong block.

Ví dụ 12 layers chia thành 3 blocks, mỗi block 4 layers: layer 6 có thể đọc embedding, summary của layers 1–4, và partial summary đang có từ layer 5. Nó không thể tách layer 2 ra khỏi summary đầu tiên. Đổi lại, số persistent depth sources tăng theo số blocks thay vì số layers.[^attnres-concept]

### 3.4 `mHC`: nhiều channels, rồi read–carry–write

```text
residual channels X
       │
       ├─► READ map A ─► một layer input ─► inner branch ─► update ─► WRITE map C ─┐
       │                                                                          │
       └─► CARRY/MIX map B ────────────────────────────────────────────────────────┤
                                                                                  ▼
                                                                       next channels
```

Luồng đầu đến cuối:

1. **Expand:** mỗi token có nhiều residual channels cùng width, thay vì một channel.
2. **Read:** map `A` trộn channels thành một vector width chuẩn để đưa vào inner Transformer/MoE layer.
3. **Transform:** inner layer giữ interface width cũ; nó không tự động rộng lên theo số channels.
4. **Carry:** map `B` chuyển và trộn state cũ giữa channels.
5. **Write:** map `C` phân phối branch update mới trở lại các channels.
6. **Constrain:** `B` được chuẩn hóa để không âm, mỗi hàng và mỗi cột tổng bằng một; constraint áp lên linear residual mixing map.[^mhc-concept]

Trong ví dụ “Paris”, ta có thể hình dung một channel thiên về lexical identity, một channel mang relation, và các channels khác giữ context mixtures. Đây chỉ là mental model; channels không có semantic label được bảo đảm. Điểm thật sự là layer đọc một mixture, còn state qua depth vẫn giữ nhiều lanes.

## 4. Tác động: behavior, quality và systems cost

### 4.1 Hệ quả trực tiếp từ thiết kế

| Cơ chế | Lợi ích trực tiếp | Chi phí trực tiếp | Điều kiện để lợi ích xuất hiện |
| --- | --- | --- | --- |
| Standard residual | identity path đơn giản; state theo depth chỉ là running representation | không chọn riêng earlier updates | đủ khi fixed accumulation phù hợp và simplicity quan trọng |
| Full `AttnRes` | earlier layer outputs vẫn individually addressable theo depth | giữ và score nhiều depth sources; communication khó hơn | learned weights phải tìm được selection hữu ích |
| Block `AttnRes` | vẫn chọn giữa block summaries; state được bounded theo số blocks | mất resolution bên trong completed block | block boundaries phải cân bằng quality và systems cost |
| `mHC` | nhiều residual channels; constrained carry map là non-expansive | activation và communication tăng theo channels; thêm mixing | dynamic mappings và systems implementation phải tận dụng channels ổn định |

Các dòng trên là hệ quả cấu trúc hoặc mathematical property của mechanism.[^attnres-concept][^mhc-concept]

### 4.2 Điều không thay đổi trực tiếp

Đổi residual path **không tự động**:

- giảm token `KV cache`;
- bỏ autoregressive decode order;
- tăng context window;
- sửa causal mask;
- thay token-attention FLOPs;
- bảo đảm downstream quality tăng.

Một architecture có thể đồng thời đổi attention, MoE, optimizer và residual path. Khi đó headline result của full model không thể gán riêng cho residual mechanism nếu thiếu matched ablation.

### 4.3 Kết quả benchmark được báo cáo, không phải định luật

Trong matched experiments của báo cáo `AttnRes`, Full và Block variants có validation loss thấp hơn `PreNorm` baseline ở năm MoE sizes. Một matched 48B-total/3B-active Kimi Linear comparison báo cáo variant có `AttnRes` cao hơn ở 14/15 listed benchmarks và hòa một benchmark. Report cũng đo dưới 4% training overhead với pipeline parallelism và dưới 2% inference-latency overhead trên typical workloads của họ.[^attnres-eval]

Những số này không suy ra chỉ từ softmax depth mixing. Chúng phụ thuộc model, data, optimizer, block count, kernels, pipeline schedule, hardware, context và evaluation harness; chưa được independent replication trong wiki evidence.[^attnres-eval]

Với `mHC`, constraint cho phép kết luận về spectral behavior của `B` map, nhưng không chứng minh toàn network ổn định hay tốt hơn. DeepSeek-V4 report một systems overhead cụ thể và dùng `mHC` cùng nhiều thay đổi khác; không có public component-isolated ablation đủ để gán headline model quality cho riêng `mHC`.[^mhc-concept][^deepseek-v4-concept]

## 5. Sự khác biệt với baseline và khái niệm gần nhất

### 5.1 Bảng so sánh

| Cơ chế | Giống nhau | Khác nhau | Trade-off | Khi phù hợp |
| --- | --- | --- | --- | --- |
| Standard residual | branch vẫn nhận và trả cùng hidden width | cộng running state với coefficient cố định | đơn giản, ít depth state; không selective | baseline, model nhỏ, serving ưu tiên simplicity |
| Full `AttnRes` | inner attention/FFN vẫn giữ nguyên | retrieval từ từng earlier depth source | granularity cao; state và scoring lớn nhất | research, ablation, stack không quá sâu |
| Block `AttnRes` | cùng softmax retrieval idea như Full | source là summaries thay vì mọi layer | bounded source count; mất within-block resolution | deep production stack cần depth retrieval |
| `mHC` | inner layer vẫn có width chuẩn | nhiều channels và read/carry/write maps | state tăng theo channels; không truy hồi layer history riêng | muốn multi-channel residual flow với constrained carry |

### 5.2 Thay đổi nằm ở đâu trong data flow?

```text
embedding
   │
[token attention / FFN branch]  ← giữ nguyên category
   │
[RESIDUAL AGGREGATION]          ← thay đổi ở đây
   │
[token attention / FFN branch]
```

- `AttnRes` thay **cách tạo layer input từ depth history**.
- `mHC` thay **representation và mapping của residual stream**.
- Q/K/V token projections, causal mask, positional encoding, FFN, MoE router và output head có thể giữ nguyên về vai trò.

### 5.3 Ba nhầm lẫn cần dẹp trước khi vào kỹ thuật

1. **Depth attention không phải token attention.** `AttnRes` chọn representations của cùng token position qua layers; token attention chọn positions qua sequence.
2. **Block summary không phải KV-cache compression.** Nó nén history theo model depth, không nén danh sách tokens theo context.
3. **`mHC` không phải Full `AttnRes` nhiều heads.** `mHC` carry/mix fixed channels tại mỗi depth; Full `AttnRes` retrieval từ growing set of earlier layer sources.

## 6. Trong thực tế

### 6.1 Cơ chế nằm ở đâu trong model thật?

Kimi K3 dùng Block `AttnRes` như component retrieval theo depth, bên cạnh KDA cho fixed-state sequence memory, periodic MLA cho global token retrieval và sparse MoE cho channel capacity. Các cơ chế giải quyết các axes khác nhau; `AttnRes` không làm global token memory của MLA biến mất.[^kimi-k3-concept]

DeepSeek-V4 dùng `mHC` cho residual stream, trong khi compressed attention xử lý long-context token retrieval và DeepSeekMoE xử lý sparse capacity. Vì nhiều thay đổi cùng xuất hiện, architecture report không isolate causal contribution của riêng `mHC`.[^deepseek-v4-concept]

### 6.2 Walkthrough: chọn residual design cho model 96 layers

Giả sử bạn thiết kế một 96-layer decoder phục vụ long prompts:

1. **Bắt đầu bằng standard residual.** Đây là control dễ train, profile và debug nhất.
2. **Đo bottleneck thật.** Theo dõi validation loss theo depth, activation norm, gradient norm, per-layer contribution, pipeline communication, prefill memory và decode latency.
3. **Nếu muốn selective depth retrieval**, thử Full `AttnRes` ở scale nhỏ để xem weights và ablation signal.
4. **Nếu Full form giúp quality nhưng depth-state quá lớn**, chia 96 layers thành ví dụ 8 blocks, rồi sweep block count; đừng coi 8 là universal optimum chỉ vì một report dùng cấu hình gần đó.[^attnres-eval]
5. **Nếu mục tiêu là multi-channel signal propagation thay vì layer retrieval**, thử `mHC` như một hypothesis khác, với matched parameter/compute controls.
6. **Giữ token mechanism cố định trong ablation.** Nếu cùng lúc đổi attention, data hoặc optimizer, bạn mất khả năng kết luận residual change gây ra khác biệt.
7. **Promote chỉ sau end-to-end measurement.** Một mixer có FLOPs nhỏ vẫn có thể làm chậm do activation traffic, synchronization hoặc unfused kernels.

### 6.3 Khi nào nên và không nên dùng?

**Cân nhắc `AttnRes` khi:**

- stack sâu và bạn có evidence rằng fixed depth accumulation là bottleneck;
- training quality đáng giá hơn một phần state/communication tăng thêm;
- có khả năng implement block caching, sharding hoặc fusion;
- có matched ablation và observability cho depth weights.

**Không nên mặc định dùng khi:**

- model nhỏ hoặc latency budget rất chặt;
- bottleneck thực là token KV cache, attention kernel hoặc MoE communication;
- serving stack không hỗ trợ extra depth state hiệu quả;
- bạn chỉ có headline benchmark của architecture khác.

**Cân nhắc `mHC` khi:** bạn muốn thử expanded residual channels và constrained carry mapping, có budget activation/communication, đồng thời có thể đo stability và quality trong matched setup. Không nên dùng chỉ vì `B` non-expansive; property đó không bao phủ nonlinear branch, optimizer hay toàn training dynamics.[^mhc-concept]

### 6.4 Measurement bắt buộc

| Nhóm | Measurement |
| --- | --- |
| Quality | validation loss, task metrics, matched seeds, confidence/variance nếu có |
| Behavior | depth weights, source entropy, layer-output norms, gradient norms |
| Memory | peak training activation, retained summaries, per-request prefill state |
| Compute | branch FLOPs tách khỏi mixer FLOPs; recomputation |
| Latency | prefill và one-token decode riêng; batch/concurrency sweep |
| Distributed | bytes giữa pipeline stages, collective time, overlap efficiency |

> [!warning] Gate trước phần toán
> Đến đây, bạn phải trả lời được: residual design giải quyết information flow qua depth; standard cộng dồn, `AttnRes` retrieval từ layer/block sources, `mHC` trộn nhiều channels; lợi ích đi kèm state/communication; chúng khác token attention; và deployment chỉ đáng làm sau matched measurement. Nếu chưa, hãy đọc lại Sections 2–6 trước khi zoom in.

## 7. Toán học — zoom in sau trực giác

### 7.1 Bảng ký hiệu

| Ký hiệu | Nghĩa | Shape ví dụ |
| --- | --- | --- |
| $B$ | batch size | scalar, ví dụ 2 |
| $T$ | sequence length | scalar, ví dụ 5 |
| $D$ | hidden width | scalar, ví dụ 8 |
| $L$ | số layers | scalar, ví dụ 96 |
| $S$ | số depth sources đang được retrieval | scalar, ví dụ 3 |
| $N$ | số blocks trong Block `AttnRes` | scalar, ví dụ 8 |
| $h_l$ | hidden representation tại depth $l$ | $(B,T,D)$ |
| $F_l$ | branch transformation tại layer $l$ | $(B,T,D)\to(B,T,D)$ |
| $v_i$ | embedding hoặc layer update làm depth source | $(B,T,D)$ |
| $X_l$ | expanded `mHC` state | $(B,T,n_{hc},D)$ |

### 7.2 Standard residual: trường hợp nhỏ nhất

**Trực giác.** Layer giữ representation cũ và thêm update mới.

**Công thức.**

$$
h_{l+1}=h_l+F_l(\operatorname{Norm}(h_l)). \tag{1}
$$

**Ý nghĩa ký hiệu.** $h_l$ là input; `Norm` chuẩn hóa; $F_l$ là attention hoặc FFN branch; dấu cộng là element-wise.

**Shape flow.**

```text
h_l                  (B,T,D)
Norm(h_l)            (B,T,D)
F_l(Norm(h_l))       (B,T,D)
h_{l+1}              (B,T,D)
```

**Ví dụ số.** Bỏ batch và token dimensions, dùng width 2:

```text
h_l    = [1.0, 0.5]
update = [0.2, -0.1]
next   = [1.2, 0.4]
```

**Kết luận.** Branch phải trả cùng shape; residual path không đổi sequence length hay width.

Để thấy fixed accumulation, đặt $v_0=h_0$ và $v_{i+1}=F_i(h_i)$, tạm bỏ `Norm` khỏi notation.

**Trực giác.** Mỗi layer ghi thêm một update vào cùng running sum.

**Công thức.**

$$
h_l=\sum_{i=0}^{l-1}v_i. \tag{2}
$$

**Ý nghĩa ký hiệu.** $v_0$ là embedding source; các $v_i$ sau là layer updates; mọi coefficient bằng một.

**Shape flow.** Mỗi $v_i$ có shape $(B,T,D)$; sum trên depth index $i$ vẫn cho $(B,T,D)$.

**Ví dụ số.**

```text
v0 = [1.0, 0.0]
v1 = [0.5, 0.5]
v2 = [0.0, 1.0]
h3 = [1.5, 1.5]
```

**Kết luận.** Layer trên nhận tổng, không nhận một selector cho từng $v_i$.

**Derivation ngắn bằng induction.** Với một bước, $h_1=v_0$. Giả sử $h_l=\sum_{i=0}^{l-1}v_i$; residual step kế tiếp cộng $v_l$, nên $h_{l+1}=h_l+v_l=\sum_{i=0}^{l}v_i$. Vì vậy fixed accumulation đúng cho mọi depth trong simplified no-norm notation.

### 7.3 Full `AttnRes`: score, softmax và mixture

#### Bước A — score một source

**Trực giác.** Chuẩn hóa source rồi hỏi learned pseudo-query của target layer xem source đó phù hợp đến đâu.

**Công thức.**

$$
s_{i\to l}=w_l^\top\operatorname{RMSNorm}(v_i). \tag{3}
$$

**Ý nghĩa ký hiệu.** $w_l$ là pseudo-query width $D$ của target layer; $v_i$ là source $i$; $s_{i\to l}$ là scalar score tại mỗi batch item và token position.[^attnres-concept]

**Shape flow.**

```text
v_i                         (B,T,D)
RMSNorm(v_i)                (B,T,D)
w_l                         (D,)
dot trên D                  (B,T)
stack S source scores       (B,T,S)
```

**Ví dụ số.** Với normalized source `[1, 0]` và pseudo-query `[2, 1]`, score là `2`.

**Kết luận.** Scoring không tạo tensor cặp token `(T,T)`; nó tạo một score cho mỗi depth source tại mỗi token.

#### Bước B — biến scores thành weights

**Trực giác.** Sources cạnh tranh để tổng weight bằng một.

**Công thức.**

$$
\alpha_{i\to l}=\frac{\exp(s_{i\to l})}{\sum_{j=0}^{S-1}\exp(s_{j\to l})}. \tag{4}
$$

**Ý nghĩa ký hiệu.** $S$ là số sources; denominator cộng trên depth index $j$, không phải token positions.

**Shape flow.** `scores` và `weights` đều $(B,T,S)`; `softmax` chạy trên dimension $S$.

**Ví dụ số.** Với scores `[1.0, 2.0, 0.5]`, weights xấp xỉ `[0.231, 0.629, 0.140]`, tổng bằng `1.0`.

**Kết luận.** Weight là content-dependent qua source representation nhưng dùng layer-specific learned pseudo-query.

#### Bước C — mix source values

**Trực giác.** Mỗi source đóng góp theo weight vừa tính.

**Công thức.**

$$
h_l=\sum_{i=0}^{S-1}\alpha_{i\to l}v_i. \tag{5}
$$

**Ý nghĩa ký hiệu.** $\alpha_{i\to l}$ là scalar cho từng `(batch, token, source)`; $v_i$ là vector width $D$.

**Shape flow.**

```text
weights                     (B,T,S)
stacked values              (B,T,S,D)
weights[...,None] * values  (B,T,S,D)
sum trên S                  (B,T,D)
```

**Ví dụ số.** Với values `[[1,0], [0,1], [1,1]]` và weights `[0.2, 0.5, 0.3]`, output là `[0.5, 0.8]`.

**Kết luận.** Output giữ hidden shape nhưng source coefficients không còn cố định.

> [!note] Zero initialization
> Nếu $w_l=0$, mọi score bằng `0`, nên mỗi weight bằng $1/S$ và output là arithmetic mean của sources. Đây là initialization behavior được báo cáo của Full `AttnRes`, không phải equivalence với standard residual sum.[^attnres-concept]

### 7.4 Block `AttnRes`: summary và limits

**Trực giác.** Gộp updates trong cùng block trước khi cho layer sau retrieval.

**Công thức.**

$$
b_n=\sum_{j\in\mathcal{B}_n}F_j(h_j). \tag{6}
$$

**Ý nghĩa ký hiệu.** $\mathcal{B}_n$ là tập layers thuộc block $n$; $b_n$ là completed summary.

**Shape flow.** Mỗi update và mỗi summary đều $(B,T,D)`; hệ thống giữ khoảng $N$ summaries thay vì $L$ individual layer sources.[^attnres-concept]

**Ví dụ số.** Với updates scalar `1, 2, 3, 4` trong block đầu, summary là `10`. Layer sau có thể weight summary `10`, nhưng không thể gán weight riêng cho update `2`.

**Kết luận.** Block form giảm depth-state order từ $O(LD)$ xuống $O(ND)$ per token representation nhưng mất within-block resolution.[^attnres-concept]

Hai limits giúp kiểm tra:

- $N=L$: một layer mỗi block, granularity tiến về Full form.
- $N=1$: một accumulated block, selective depth resolution gần như biến mất ngoài embedding source.[^attnres-concept]

### 7.5 `mHC`: expanded state và constrained carry

**Trực giác.** Đọc một mixture từ nhiều channels, chạy branch, carry state cũ và ghi update mới.

**Công thức.**

$$
X_{l+1}=B_lX_l+C_lF_l(A_lX_l). \tag{7}
$$

**Ý nghĩa ký hiệu.** $A_l$ đọc channels thành layer input; $B_l$ carry/mix channels; $C_l$ ghi branch output vào channels.[^mhc-concept]

**Shape flow.** Với $X_l$ shape $(B,T,n_{hc},D)$:

```text
A_l                         (n_hc,)
A_l X_l                     (B,T,D)
F_l(A_l X_l)                (B,T,D)
B_l                         (n_hc,n_hc)
B_l X_l                     (B,T,n_hc,D)
C_l F_l(...)                (B,T,n_hc,D)
X_{l+1}                     (B,T,n_hc,D)
```

**Ví dụ số.** Với 2 channels scalar `[2, 0]`, read weights `[0.5, 0.5]` cho layer input `1`. Nếu branch update là `3` và write weights `[1, 0]`, update chỉ được ghi vào channel đầu trong toy example.

**Kết luận.** Inner branch vẫn width $D$; expanded state tăng theo $n_{hc}$.

Constraint quan trọng của carry map là:

**Trực giác.** Mỗi output channel là mixture không âm của input channels, đồng thời mass không bị dồn hoặc mất qua rows/columns.

**Công thức.**

$$
B_l\ge0,\qquad B_l\mathbf{1}=\mathbf{1},\qquad \mathbf{1}^{\top}B_l=\mathbf{1}^{\top}. \tag{8}
$$

**Ý nghĩa ký hiệu.** Mỗi row và column của $B_l$ cộng bằng một; đây là `doubly stochastic` constraint.

**Shape flow.** $B_l$ là matrix $(n_{hc},n_{hc})$ tác động trên channel axis, độc lập với hidden dimension $D$.

**Ví dụ số.** Matrix `[[0.7, 0.3], [0.3, 0.7]]` có row sums và column sums đều `[1,1]`.

**Kết luận.** Spectral norm của constrained $B_l$ không vượt một, nên riêng linear carry map là non-expansive; điều này không phải proof cho toàn nonlinear network.[^mhc-concept]

**Proof sketch có thể bỏ qua.** Theo Birkhoff–von Neumann, một doubly stochastic matrix là convex combination của permutation matrices. Mỗi permutation matrix có spectral norm bằng một; tính lồi của matrix norm cho $\lVert B_l\rVert_2\le\sum_k\lambda_k\lVert P_k\rVert_2=1$. Proof chỉ áp dụng cho $B_l$; nhánh $F_l$, maps $A_l/C_l$ và optimizer vẫn có dynamics riêng.[^mhc-concept]

`mHC` tạo matrix dương từ raw scores rồi lặp row/column normalization kiểu Sinkhorn–Knopp; source concept ghi nhận 20 iterations trong reported design.[^mhc-concept]

## 8. Implementation — PyTorch tối thiểu và inspectable

Code dưới đây cụ thể hóa đúng ba data flows đã giải thích. `FullDepthAttention` chỉ là depth mixer; `StaticMHCPath` chỉ dùng static maps để lộ rõ mechanism. Production `mHC` tạo dynamic maps từ current state, còn production Block `AttnRes` có caching, batched queries và online softmax.[^attnres-concept][^mhc-concept]

```python
import torch
import torch.nn as nn

class RMSNorm(nn.Module):
    def __init__(self, d, eps=1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(d))
        self.eps = eps

    def forward(self, x):
        rms = x.square().mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.weight


class PreNormResidual(nn.Module):
    """Section 3.1: identity path + normalized branch update."""
    def __init__(self, d, branch):
        super().__init__()
        self.norm = RMSNorm(d)
        self.branch = branch

    def forward(self, h):
        update = self.branch(self.norm(h))       # (B,T,D)
        return h + update                        # (B,T,D)


class FullDepthAttention(nn.Module):
    """Sections 3.2/7.3: score -> depth softmax -> weighted mixture."""
    def __init__(self, d):
        super().__init__()
        self.score_norm = RMSNorm(d)
        self.pseudo_query = nn.Parameter(torch.zeros(d))

    def forward(self, sources, return_weights=False):
        assert len(sources) > 0
        values = torch.stack(sources, dim=2)     # (B,T,S,D)
        keys = self.score_norm(values)           # (B,T,S,D)
        scores = torch.einsum(
            "btsd,d->bts", keys, self.pseudo_query
        )                                        # (B,T,S)
        weights = scores.softmax(dim=-1)         # softmax trên S
        mixed = torch.einsum(
            "bts,btsd->btd", weights, values
        )                                        # (B,T,D)
        return (mixed, weights) if return_weights else mixed


def completed_block_summaries(layer_updates, block_size):
    """Section 3.3: toy completed summaries; không model current partial state."""
    summaries = []
    for start in range(0, len(layer_updates), block_size):
        block = layer_updates[start:start + block_size]
        summaries.append(torch.stack(block, dim=0).sum(dim=0))
    return summaries                             # mỗi item (B,T,D)


def sinkhorn(raw, steps=20):
    """Positive matrix -> approximately doubly stochastic matrix."""
    matrix = raw.exp()
    for _ in range(steps):
        matrix = matrix / matrix.sum(dim=0, keepdim=True).clamp_min(1e-12)
        matrix = matrix / matrix.sum(dim=1, keepdim=True).clamp_min(1e-12)
    return matrix


class StaticMHCPath(nn.Module):
    """Sections 3.4/7.5: static-map teaching version, not production mHC."""
    def __init__(self, d, n_channels=4, sinkhorn_steps=20):
        super().__init__()
        self.steps = sinkhorn_steps
        self.raw_a = nn.Parameter(torch.zeros(n_channels))
        self.raw_b = nn.Parameter(torch.eye(n_channels))
        self.raw_c = nn.Parameter(torch.zeros(n_channels))
        self.branch = nn.Sequential(RMSNorm(d), nn.Linear(d, d))

    def residual_map(self):
        return sinkhorn(self.raw_b, self.steps)   # (n,n)

    def forward(self, x):
        # x: (B,T,n,D)
        a = self.raw_a.sigmoid()                  # (n,), bounded
        b = self.residual_map()                   # (n,n), doubly stochastic
        c = self.raw_c.sigmoid()                  # (n,), bounded

        layer_input = torch.einsum("n,btnd->btd", a, x)
        update = self.branch(layer_input)         # (B,T,D)
        carried = torch.einsum("ij,btjd->btid", b, x)
        written = torch.einsum("i,btd->btid", c, update)
        return carried + written                  # (B,T,n,D)
```

> [!note] Ranh giới toy/production
> Code dùng Python lists, `torch.stack` và materialized tensors để dễ inspect. Serving thật cần pre-allocation, sharding, fusion, block caching và có thể online softmax; mini-lab không đưa ra latency claim.

## 9. Verification trước benchmark

Chạy sau implementation block. Tất cả numeric comparisons dùng tolerance tường minh; `float32` được dùng để kiểm tra reference behavior.

```python
torch.manual_seed(7)
torch.set_default_dtype(torch.float32)
RTOL, ATOL = 1e-5, 1e-6

# Test 1 — standard residual đúng identity + update
h = torch.randn(2, 3, 4)
class ConstantBranch(nn.Module):
    def forward(self, x):
        return torch.full_like(x, 0.25)

standard = PreNormResidual(4, ConstantBranch())
out = standard(h)
torch.testing.assert_close(out, h + 0.25, rtol=RTOL, atol=ATOL)
assert out.shape == h.shape

# Test 2 — zero pseudo-query => uniform weights => arithmetic mean
sources = [torch.randn(2, 3, 4) for _ in range(3)]
depth = FullDepthAttention(4)
mixed, weights = depth(sources, return_weights=True)
expected_weights = torch.full((2, 3, 3), 1.0 / 3.0)
expected_mean = torch.stack(sources, dim=2).mean(dim=2)
torch.testing.assert_close(weights, expected_weights, rtol=RTOL, atol=ATOL)
torch.testing.assert_close(mixed, expected_mean, rtol=RTOL, atol=ATOL)

# Test 3 — implementation khớp phép tính manual khi query khác 0
with torch.no_grad():
    depth.pseudo_query.copy_(torch.tensor([0.5, -0.2, 0.1, 0.3]))
values = torch.stack(sources, dim=2)
keys = depth.score_norm(values)
manual_scores = (keys * depth.pseudo_query).sum(dim=-1)
manual_weights = manual_scores.softmax(dim=-1)
manual_mixed = (manual_weights.unsqueeze(-1) * values).sum(dim=2)
actual_mixed, actual_weights = depth(sources, return_weights=True)
torch.testing.assert_close(actual_weights, manual_weights, rtol=RTOL, atol=ATOL)
torch.testing.assert_close(actual_mixed, manual_mixed, rtol=RTOL, atol=ATOL)

# Test 4 — block summaries giữ tổng nhưng mất individual resolution
updates = [torch.randn(2, 3, 4) for _ in range(8)]
summaries = completed_block_summaries(updates, block_size=4)
assert len(summaries) == 2
torch.testing.assert_close(
    summaries[0], torch.stack(updates[:4]).sum(dim=0),
    rtol=RTOL, atol=ATOL,
)
torch.testing.assert_close(
    summaries[1], torch.stack(updates[4:]).sum(dim=0),
    rtol=RTOL, atol=ATOL,
)

# Test 5 — Sinkhorn map có row/column sums gần 1 và spectral norm <= 1
mhc = StaticMHCPath(d=4, n_channels=4, sinkhorn_steps=40)
x = torch.randn(2, 3, 4, 4)
x_next = mhc(x)
b_map = mhc.residual_map().detach()
torch.testing.assert_close(
    b_map.sum(dim=0), torch.ones(4), rtol=1e-4, atol=1e-5,
)
torch.testing.assert_close(
    b_map.sum(dim=1), torch.ones(4), rtol=1e-4, atol=1e-5,
)
assert x_next.shape == x.shape
assert torch.linalg.svdvals(b_map)[0].item() <= 1.001

# Test 6 — depth mixer tự nó không trộn token positions
# Đổi future position cuối; outputs ở positions trước phải giữ nguyên.
future_changed = [s.clone() for s in sources]
for s in future_changed:
    s[:, -1, :] += 100.0
before = depth(sources)
after = depth(future_changed)
torch.testing.assert_close(
    before[:, :-1, :], after[:, :-1, :], rtol=RTOL, atol=ATOL,
)

print("All six residual-path reference tests passed.")
```

Test 6 chỉ chứng minh `FullDepthAttention` toy không trộn sequence positions. Khi tích hợp với real attention branch, cần thêm whole-model `future perturbation test`: thay token cuối rồi xác nhận logits ở các positions trước không đổi. Residual test không thay thế causal-mask test.

## 10. Benchmark và trade-offs đúng phạm vi

### 10.1 Bảng cost model

| Hạng mục | Standard | Full `AttnRes` | Block `AttnRes` | `mHC` |
| --- | --- | --- | --- | --- |
| Depth source state per token | một running state | order $LD$ | order $ND$ | order $n_{hc}D$ |
| Depth mixing arithmetic | cộng tuyến tính qua stack | order $L^2D$ qua stack | order $NLD$ ở mức khái quát | small channel maps, phụ thuộc implementation |
| Source granularity | accumulated | individual layers | block summaries | channels, không phải layer history |
| Token KV cache | không đổi | không đổi | không đổi | không đổi |
| Main systems risk | baseline traffic | activation + pipeline transfer | summary cache + communication | expanded activation + channel mixing |

Các asymptotic rows của `AttnRes` theo source concept; dòng `mHC` là synthesis từ tensor shapes, không phải measured end-to-end cost.[^attnres-concept][^mhc-concept]

### 10.2 Mini-benchmark local

```python
import time

@torch.no_grad()
def bench_depth_sources(device="cpu"):
    results = []
    for s_count in [1, 4, 8, 32]:
        sources = [torch.randn(2, 128, 512, device=device)
                   for _ in range(s_count)]
        mixer = FullDepthAttention(512).to(device).eval()
        for _ in range(5):
            mixer(sources)
        if device.startswith("cuda"):
            torch.cuda.synchronize()
        start = time.perf_counter()
        for _ in range(20):
            mixer(sources)
        if device.startswith("cuda"):
            torch.cuda.synchronize()
        ms = (time.perf_counter() - start) * 1000 / 20
        results.append((s_count, ms))
    return results

print(bench_depth_sources("cpu"))
```

Để measurement có ý nghĩa, ghi `device`, dtype, PyTorch/CUDA version, warm-up, batch, sequence length, width, source count và synchronization. Kết quả toy này chỉ cho thấy implementation local thay đổi khi source count tăng; nó không reproduce reported pipeline overhead hay quality.

### 10.3 Reported systems numbers phải đọc có điều kiện

`AttnRes` report nêu dưới 4% training overhead và dưới 2% inference-latency overhead trong typical measured settings; long-context prefill vẫn phải giữ block representations per token. `mHC` concept ghi nhận DeepSeek-V4 report giới hạn overhead xuống 6.7% của một overlapped 1F1B pipeline stage bằng fused kernels và selective recomputation. Không số nào là portable guarantee cho hardware hoặc stack khác.[^attnres-eval][^mhc-concept]

## 11. Debug checklist

| Triệu chứng | Nguyên nhân có thể | Check đầu tiên |
| --- | --- | --- |
| Depth weights tổng không bằng 1 | `softmax` sai axis | xác nhận `scores.shape == (B,T,S)` và softmax trên `S` |
| Zero-init output bằng sum thay vì mean | expectation sai | so với `stack(...).mean(dim=depth)` |
| Shape bị đổi sau residual | branch không trả `(B,T,D)` | log input/update/output shapes |
| Block form dùng memory gần Full form | vẫn giữ individual updates | inspect object lifetime và retained tensors |
| Muốn chọn riêng layer cũ nhưng chỉ có summary | hiểu sai block granularity | liệt kê sources thật tại block boundary |
| `mHC` row sums đúng, column sums sai | Sinkhorn chỉ normalize một hướng | kiểm tra cả `sum(dim=0)` và `sum(dim=1)` |
| `mHC` chậm bất ngờ | unfused channel maps/traffic | profile kernel launches và memory bandwidth |
| Earlier logits đổi khi sửa future token | causal bug trong token branch | whole-model future-perturbation test |
| Quality tăng nhưng không biết vì sao | ablation thay nhiều biến | giữ data, optimizer, width, depth và compute matched |
| Prefill OOM dù mixer FLOPs nhỏ | retained state nhân với tokens | account batch × tokens × sources × width × bytes |

## 12. Giới hạn và bước tiếp theo

Mini-lab chứng minh algebra, shape invariants, uniform initialization behavior, block sums, Sinkhorn constraints và token-axis independence của toy mixer. Nó không chứng minh trainability ở scale, benchmark quality, production latency, distributed efficiency hay full-model causality.

Evidence mạnh nhất cho `AttnRes` trong wiki là primary-report-backed mechanism, matched author-run ablations và systems measurements; chưa có independent replication tại đây.[^attnres-eval] Evidence cho `mHC` mô tả mechanism và reported implementation, nhưng concept đang ở `draft` và không có public ablation isolate khỏi các thay đổi khác của DeepSeek-V4.[^mhc-concept][^deepseek-v4-concept]

Bước tiếp theo:

1. Trace một 4-layer standard stack và lưu từng update để kiểm tra unrolled sum.
2. Thay chỉ depth aggregator bằng Full `AttnRes`; plot weights và entropy theo layer/token.
3. Sweep block count với matched model/data/compute; đo quality, peak memory và prefill/decode riêng.
4. Đọc [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md) để luyện evidence discipline.
5. Xem [Kimi K3 integrated architecture course](kimi-k3-integrated-architecture-information-path-beginners-course.md) để đặt depth retrieval cạnh sequence memory, global token retrieval và MoE.

## Relationships

- **Depends on:** [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md) — baseline residual connection và phân vai attention/FFN/residual.
- **Uses:** [Attention Residuals](attention-residuals.md) — Full và Block depth retrieval mechanism.
- **Uses:** [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md) — constrained multi-channel residual mixing.
- **Applied by:** [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md) — Block `AttnRes` trong architecture thật.
- **Applied by:** [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md) — `mHC` trong architecture thật.
- **Elaborates:** Stage 8.1 của [LLM architecture learning roadmap](llm-architecture-learning-roadmap.md).

## Evidence limits

Đây là pedagogical synthesis từ maintained wiki concepts. `AttnRes` quality và systems results là author-run, workload-specific và chưa được independently replicated trong knowledge base. `mHC` mechanism có mathematical support cho constrained linear carry map, nhưng không có public component-isolated quality ablation và không chứng minh stability của toàn nonlinear model. Toy PyTorch code được viết để inspect và verify mechanism, không phải source implementation hoặc serving benchmark.[^attnres-eval][^mhc-concept]

[^transformer-concept]: [Transformer sequence transduction architecture](transformer-sequence-transduction-architecture.md), maintained synthesis từ “Attention Is All You Need”, phần architecture và residual sublayers.
[^attnres-concept]: [Attention Residuals](attention-residuals.md), maintained synthesis từ primary AttnRes/Kimi K3 reports và released reference code, phần Full form, Block form và systems implications.
[^attnres-eval]: [Attention Residuals evaluation and systems trade-offs](attention-residuals-evaluation-and-systems-trade-offs.md), matched author-run experiments, ablations, overhead measurements và evidence limits.
[^mhc-concept]: [Manifold-constrained Hyper-Connections](manifold-constrained-hyper-connections.md), maintained synthesis từ DeepSeek-V4 report, residual update, doubly stochastic constraint và implementation boundary; concept status `draft`.
[^kimi-k3-concept]: [Kimi K3 hybrid retrieval architecture](kimi-k3-hybrid-retrieval-architecture.md), division of labor giữa KDA, MLA, Block AttnRes và MoE.
[^deepseek-v4-concept]: [DeepSeek-V4 hybrid architecture and pretraining](deepseek-v4-hybrid-architecture-and-pretraining.md), reported use of `mHC` cùng compressed attention, MoE và other co-design changes; concept status `draft`.
