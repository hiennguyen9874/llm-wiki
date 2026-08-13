Có thể chia các kiến trúc AI hiện nay thành **ba tầng khác nhau**:

1. **Backbone xử lý chuỗi**: Transformer, Mamba, RetNet…
2. **Cách mở rộng model và context**: MoE, sparse attention, memory…
3. **Cách xây hệ thống thông minh**: multimodal, RAG, agent, world model…

Việc tách ba tầng này rất quan trọng. Chẳng hạn, **GLM-5.2 không phải một backbone hoàn toàn mới**; nó vẫn là Transformer nhưng kết hợp MoE, latent/sparse attention và nhiều tối ưu inference.

---

# I. Các họ kiến trúc backbone hiện tại

## 1. Dense Transformer

Đây vẫn là kiến trúc nền tảng phổ biến nhất:

```text
Token
  ↓
Self-Attention
  ↓
Feed-Forward Network
  ↓
Residual + Normalization
```

Self-attention:

[
Y=\operatorname{softmax}
\left(
\frac{QK^T}{\sqrt d}
\right)V
]

### Điểm mạnh

* Truy xuất trực tiếp bất kỳ token nào trong context.
* Copy, associative recall và in-context learning mạnh.
* Dễ mở rộng sang text, image, audio, video.
* Hệ sinh thái phần cứng và kernel trưởng thành.

### Điểm yếu

* Full attention có chi phí:

[
O(L^2)
]

* KV cache tăng theo chiều dài sequence.
* Decode context dài tốn băng thông bộ nhớ.

### Đại diện

* Llama
* Qwen
* GLM
* Gemma
* DeepSeek
* Mistral
* GPT-like decoder models

Dense Transformer vẫn là baseline quan trọng vì các kiến trúc tuyến tính thường chưa vượt nó đồng đều ở retrieval, reasoning và copying.

---

## 2. Efficient Transformer

Đây không phải một kiến trúc duy nhất mà là nhóm các phương pháp giữ Transformer nhưng giảm chi phí.

## 2.1 Multi-Query và Grouped-Query Attention

Thay vì mỗi query head có bộ (K,V) riêng:

* **MHA**: nhiều Q, nhiều K, nhiều V;
* **GQA**: nhiều Q head dùng chung theo nhóm K/V;
* **MQA**: tất cả Q head dùng chung một K/V.

```text
MHA: Q1→K1,V1   Q2→K2,V2   Q3→K3,V3
GQA: Q1,Q2→K1,V1   Q3,Q4→K2,V2
MQA: Q1,Q2,Q3,Q4→K,V
```

Mục tiêu chính là giảm KV cache và bandwidth khi decode.

---

## 2.2 Latent/Compressed Attention

Thay vì lưu toàn bộ K/V lớn, model nén chúng vào latent representation:

[
c_t=W_{\text{down}}h_t
]

Sau đó tái tạo thành phần cần thiết cho attention.

Ví dụ tiêu biểu là **Multi-head Latent Attention — MLA**. Cách này giảm KV cache nhưng vẫn giữ content-based retrieval của attention.

---

## 2.3 Sliding-window Attention

Mỗi token chỉ nhìn một vùng gần:

[
\mathcal S_t =
{t-w,\ldots,t}
]

Chi phí gần:

[
O(Lw)
]

thay vì (O(L^2)).

Phù hợp với:

* văn bản có tính cục bộ;
* audio;
* video;
* long sequence;
* các layer thấp.

Điểm yếu là token rất xa không thể tương tác trực tiếp nếu không thêm global token hoặc layer global attention.

---

## 2.4 Sparse Attention

Mỗi query chỉ attention đến một tập token được chọn:

[
Y_t =
\operatorname{Attention}
\left(
q_t,K_{\mathcal S_t},V_{\mathcal S_t}
\right)
]

Các dạng phổ biến:

* local/window attention;
* block-sparse attention;
* strided attention;
* global token;
* learned routing;
* top-(k) token selection;
* hierarchical attention.

GLM-5/GLM-5.2 thuộc hướng giữ Transformer nhưng làm attention thưa để giảm chi phí long context. GLM-5 sử dụng DeepSeek Sparse Attention nhằm giảm chi phí mà vẫn duy trì khả năng xử lý context dài. ([arXiv][1])

---

# II. Mixture-of-Experts Transformer

## 3. MoE

MoE chủ yếu thay đổi khối FFN, không thay attention:

[
y=
\sum_{i\in\operatorname{TopK}(g(x))}
p_i(x)E_i(x)
]

Trong đó:

* (E_i): expert thứ (i);
* (g(x)): router;
* chỉ một số expert được kích hoạt cho mỗi token.

```text
Token
  ↓
Router
  ├── Expert 1
  ├── Expert 2  ← selected
  ├── Expert 3
  └── Expert 4  ← selected
```

### Ưu điểm

* Tổng capacity rất lớn.
* Compute mỗi token thấp hơn dense model cùng tổng số tham số.
* Expert có thể chuyên môn hóa ngầm theo domain hoặc loại pattern.

### Khó khăn

* Load balancing giữa expert.
* All-to-all communication trên nhiều GPU.
* Expert parallelism phức tạp.
* Có thể gặp expert collapse hoặc routing instability.
* Tổng trọng số và memory vẫn rất lớn.

### Đại diện

* Mixtral
* DeepSeek-MoE
* Qwen-MoE
* GLM-MoE
* Jamba
* Switch Transformer

GLM-5 là ví dụ điển hình của kiến trúc **MoE Transformer kết hợp sparse attention**, chứ không phải Mamba hay SSM. ([arXiv][1])

---

# III. State Space Models

## 4. S4 và họ Structured SSM

SSM mô tả sequence bằng trạng thái:

[
h_t=Ah_{t-1}+Bx_t
]

[
y_t=Ch_t+Dx_t
]

Các kiến trúc quan trọng:

* HiPPO
* S4
* S4D
* DSS
* S5
* H3
* GSS

Chúng sử dụng cấu trúc đặc biệt của ma trận trạng thái để xử lý sequence dài hiệu quả.

### Phù hợp với

* time series;
* audio;
* genomics;
* sensor stream;
* video dài;
* tín hiệu có động lực liên tục.

S4 mở ra hướng dùng state-space representation như một lựa chọn thay thế attention cho chuỗi dài; các thế hệ sau đơn giản hóa cấu trúc và cải thiện khả năng triển khai. ([arXiv][2])

---

## 5. Mamba

Mamba bổ sung **selectivity**:

[
B_t=f_B(x_t),\qquad
C_t=f_C(x_t),\qquad
\Delta_t=f_\Delta(x_t)
]

Do đó model có thể quyết định:

* ghi token nào vào state;
* quên phần nào;
* đọc thông tin nào;
* cập nhật state nhanh hay chậm.

### Các thế hệ

| Kiến trúc | Đặc điểm chính                                          |
| --------- | ------------------------------------------------------- |
| Mamba-1   | Selective SSM, selective scan                           |
| Mamba-2   | State Space Duality, cấu trúc tính toán phù hợp GPU hơn |
| Mamba-3   | Recurrence biểu cảm hơn, complex state, MIMO            |

Mamba-3 được công bố tháng 3 năm 2026, tập trung cải thiện retrieval, state tracking và hiệu quả decode thực tế bằng discretization mới, complex-valued state và multi-input multi-output recurrence. ([arXiv][3])

### Ưu điểm

* Complexity tuyến tính theo sequence.
* Decode với trạng thái gần như cố định.
* Rất phù hợp streaming.
* Không cần KV cache tăng theo thời gian.

### Hạn chế

* Exact retrieval khó hơn Transformer.
* Copying và associative recall có thể yếu.
* Toàn bộ lịch sử phải nén vào state hữu hạn.
* Khó truy xuất chính xác một token rất cũ.

---

# IV. Linear recurrent và linear attention

Đây là nhóm nằm giữa Transformer, RNN và SSM.

## 6. Linear Attention

Softmax attention được factorize:

[
\operatorname{Attention}(Q,K,V)
\approx
\phi(Q)
\left(
\phi(K)^TV
\right)
]

Ta có thể cập nhật state:

[
S_t=S_{t-1}+\phi(k_t)v_t^T
]

[
y_t=\phi(q_t)S_t
]

### Ưu điểm

* Training tuyến tính theo sequence.
* Decode recurrent.
* State không tăng theo context.

### Hạn chế

* Không còn softmax attention chính xác.
* State có thể bị xung đột khi ghi nhiều key-value.
* Retrieval thường yếu hơn full attention.

---

## 7. RetNet

RetNet đưa ra cơ chế **retention**, hỗ trợ ba chế độ:

* parallel khi training;
* recurrent khi inference;
* chunkwise recurrent cho sequence dài.

Nó cố gắng đạt đồng thời training song song và inference (O(1)) memory theo chiều dài sequence. ([arXiv][4])

Dạng khái quát:

[
S_t=\gamma S_{t-1}+k_tv_t^T
]

[
y_t=q_tS_t
]

Trong đó (\gamma) điều khiển decay của memory.

---

## 8. RWKV

RWKV kết hợp:

* RNN-style recurrence;
* Transformer-style channel mixing;
* time mixing;
* exponential decay.

```text
Token mixing: xử lý quan hệ thời gian
Channel mixing: tương tự FFN
```

Training có thể xử lý song song theo sequence, còn inference hoạt động như RNN với state nhỏ.

RWKV phù hợp với:

* local inference;
* context dài;
* thiết bị hạn chế bộ nhớ;
* streaming generation.

---

## 9. DeltaNet và Gated DeltaNet

DeltaNet xem state như một **fast-weight memory**:

[
S_t =
S_{t-1}
+
\beta_t
\left(
v_t-S_{t-1}k_t
\right)k_t^T
]

Điểm khác với linear attention đơn giản là model:

1. đọc giá trị hiện tại ứng với key;
2. tính sai số;
3. sửa memory thay vì chỉ cộng thêm.

Gated DeltaNet thêm gate để kiểm soát decay, erase và write.

Gated DeltaNet-2, công bố tháng 5 năm 2026, tách riêng gate xóa và gate ghi, nhằm giảm xung đột khi chỉnh sửa compressed memory. ([arXiv][5])

Đây là một hướng rất đáng chú ý vì nó coi sequence model như một **bộ nhớ key-value có thể cập nhật trực tuyến**.

---

## 10. Kimi Delta Attention và các delta-rule model

Hướng này kết hợp:

* linear attention;
* adaptive forgetting;
* delta-rule update;
* chunkwise parallel training;
* recurrent inference.

Ý tưởng chung:

```text
Read current memory
       ↓
Compute prediction error
       ↓
Erase/update relevant association
       ↓
Write new key-value
```

Nó cố giải quyết hạn chế lớn của linear attention: nhiều key ghi vào state cố định có thể chồng lấn và làm hỏng thông tin cũ.

---

# V. Long-convolution architectures

## 11. Hyena và implicit long convolution

Thay vì attention, Hyena sử dụng:

* long convolution;
* input-dependent gating;
* implicit parameterization của convolution kernel.

Dạng đơn giản:

[
y=x * h
]

với kernel (h) có thể trải dài toàn sequence nhưng không nhất thiết lưu trực tiếp toàn bộ hệ số.

### Ưu điểm

* Complexity gần tuyến tính hoặc (O(L\log L)).
* Phù hợp sequence cực dài.
* Tốt cho genomics và tín hiệu.

### Hạn chế

* Content-addressable retrieval khó hơn attention.
* Khó giải thích quan hệ token-token.
* Chất lượng ngôn ngữ tổng quát chưa ổn định bằng Transformer lớn.

Hyena, RWKV, RetNet và nhiều SSM có thể được nhìn như các dạng structured sequence mixer khác nhau; chúng khác nhau chủ yếu ở cách parameterize kernel, decay và state update. ([arXiv][6])

---

# VI. Hybrid architectures

## 12. Attention + Mamba/SSM

Đây là một trong những hướng thực dụng nhất:

```text
Mamba block
    ↓
Mamba block
    ↓
Attention block
    ↓
Mamba block
    ↓
Attention block
```

Mamba phụ trách:

* xử lý phần lớn sequence;
* local và temporal mixing;
* streaming state;
* giảm KV cache.

Attention phụ trách:

* exact retrieval;
* copying;
* global interaction;
* in-context learning.

### Đại diện

* Jamba
* Samba
* các Mamba-attention hybrid
* các Gated DeltaNet-attention hybrid

Jamba kết hợp Transformer, Mamba và MoE: các layer Transformer và Mamba được xen kẽ, một số layer sử dụng MoE để tăng capacity mà vẫn kiểm soát active compute. ([arXiv][7])

Samba kết hợp Mamba với sliding-window attention để vừa có recurrent global state vừa duy trì local content-based attention. ([arXiv][8])

---

## 13. Linear recurrent + sparse attention

Một cấu hình khác:

```text
80–90% linear recurrent layers
10–20% full/sparse attention layers
```

Các linear layer xử lý rẻ phần lớn token. Attention layer được đặt định kỳ để:

* sửa lỗi memory compression;
* trao đổi thông tin toàn cục;
* hỗ trợ retrieval;
* phục hồi khả năng induction và copying.

Đây có thể là hướng cân bằng hơn pure Mamba hoặc pure linear attention.

---

## 14. SSM + MoE + Attention

Kiến trúc tổng quát trong tương lai có thể có dạng:

```text
Input
  ↓
Local convolution
  ↓
SSM / Linear recurrent mixer
  ↓
Periodic sparse attention
  ↓
MoE FFN
  ↓
Output
```

Mỗi thành phần giải quyết một vấn đề riêng:

| Thành phần      | Vai trò                  |
| --------------- | ------------------------ |
| Convolution     | Pattern cục bộ           |
| SSM/recurrent   | Memory dài, streaming    |
| Attention       | Truy xuất chính xác      |
| MoE             | Tăng knowledge capacity  |
| External memory | Lưu dữ liệu vượt context |

---

# VII. Kiến trúc memory mở rộng

## 15. External memory và RAG

RAG không thay backbone. Nó thêm memory bên ngoài:

```text
Query
  ↓
Retriever
  ↓
Vector/keyword/database search
  ↓
Relevant documents
  ↓
Transformer
```

Ưu điểm:

* knowledge không cần nằm hết trong weights;
* cập nhật dữ liệu mà không retrain;
* hỗ trợ source attribution;
* mở rộng memory gần như không giới hạn.

Hạn chế:

* retrieval sai thì generation sai;
* chunking và indexing ảnh hưởng mạnh;
* nhiều bước làm tăng latency;
* không giải quyết hoàn toàn reasoning trên dữ liệu dài.

---

## 16. Test-time learned memory

Thay vì chỉ lưu token trong KV cache, model có một neural memory được cập nhật trong inference:

[
M_t = M_{t-1} - \eta\nabla_M \mathcal L_t
]

Tức memory có thể “học” từ context hiện tại.

**Titans** là một ví dụ: attention đóng vai trò short-term memory, trong khi neural memory học cách lưu thông tin dài hạn. Công trình này trình bày ba cách kết hợp attention và learned memory, đồng thời thử nghiệm context trên hai triệu token. ([arXiv][9])

Đây là hướng khác Mamba:

* Mamba cập nhật hidden state theo recurrence cố định đã học;
* test-time memory có thể cập nhật chính tham số hoặc fast weights trong lúc inference.

---

## 17. Hierarchical memory

Sequence được chia thành nhiều mức:

```text
Token memory
   ↓
Chunk summary
   ↓
Document summary
   ↓
Episode memory
   ↓
Long-term external memory
```

Model không attention trên toàn bộ lịch sử mà:

1. xử lý local window;
2. tóm tắt chunk;
3. lưu các summary;
4. retrieve chunk gốc khi cần.

Hướng này phù hợp:

* agent chạy nhiều giờ/ngày;
* video dài;
* hội thoại dài;
* codebase lớn;
* hồ sơ người dùng dài hạn.

---

# VIII. Multimodal architectures

## 18. Encoder + LLM

Kiến trúc phổ biến:

```text
Image/Video/Audio
       ↓
Modality encoder
       ↓
Projector / Adapter
       ↓
LLM decoder
```

Ví dụ:

* ViT cho image;
* audio encoder cho speech;
* video encoder hoặc frame encoder;
* projector ánh xạ feature sang token space của LLM.

Ưu điểm là tận dụng một LLM đã pretrain mạnh.

---

## 19. Unified token Transformer

Tất cả modality được biến thành token:

```text
Text tokens
Image patches
Audio tokens
Video tokens
Action tokens
        ↓
Unified Transformer
```

Model học cùng lúc:

[
p(x_{\text{text}},
x_{\text{image}},
x_{\text{audio}},
x_{\text{action}})
]

Đây là hướng tiến tới general-purpose multimodal model.

Vấn đề lớn là video và audio sinh ra quá nhiều token, khiến attention và KV cache trở nên rất đắt.

---

## 20. Multimodal hybrid SSM

Một hướng phù hợp video:

```text
Spatial Transformer per frame
          ↓
Object/frame tokens
          ↓
Temporal Mamba/SSM
          ↓
Sparse cross-frame attention
          ↓
Event prediction
```

Transformer xử lý không gian trong một frame, còn Mamba xử lý thời gian dài.

Đối với detector/tracker:

```text
Detector
   ↓
Tracker
   ↓
Per-object Mamba states
   ↓
Scene-level cross-object attention
   ↓
Action/Event classifier
```

Đây là cấu hình hợp lý cho hệ thống traffic analytics vì:

* mỗi track có state cố định;
* không cần giữ toàn bộ feature của mọi frame;
* attention chỉ dùng trên số object hiện tại hoặc keyframe.

---

# IX. Generative architectures ngoài autoregressive LLM

## 21. Diffusion models

Diffusion bắt đầu từ noise và lặp lại quá trình denoise:

[
x_T\rightarrow x_{T-1}\rightarrow \cdots\rightarrow x_0
]

Phổ biến trong:

* image generation;
* video generation;
* audio;
* 3D;
* protein;
* một số mô hình ngôn ngữ diffusion.

### Ưu điểm

* Chất lượng generation cao.
* Có thể chỉnh sửa và điều kiện hóa linh hoạt.
* Không bị ràng buộc hoàn toàn theo thứ tự trái sang phải.

### Nhược điểm

* Cần nhiều sampling step.
* Latency cao.
* Khó streaming token như autoregressive model.

---

## 22. Flow Matching và Rectified Flow

Thay vì học từng bước stochastic denoising, model học vector field biến noise thành dữ liệu:

[
\frac{dx}{dt}=v_\theta(x,t)
]

Đây đang là hướng quan trọng cho image/video generation vì có thể:

* sampling ít bước hơn;
* trajectory đơn giản hơn diffusion truyền thống;
* dễ kết hợp với Transformer backbone.

---

## 23. Diffusion Transformer — DiT

Ở đây Transformer không dự đoán token tiếp theo mà dự đoán noise hoặc velocity trên latent image/video patches:

```text
Noisy latent patches
        ↓
Transformer
        ↓
Noise / velocity prediction
```

Do đó “Transformer” là backbone, còn “diffusion” là objective và sampling process.

---

# X. World models và action models

## 24. World model

World model học động lực môi trường:

[
z_{t+1}=f(z_t,a_t)
]

Trong đó:

* (z_t): trạng thái thế giới;
* (a_t): hành động;
* (z_{t+1}): trạng thái dự đoán tiếp theo.

Có thể dùng:

* Transformer;
* SSM/Mamba;
* recurrent network;
* diffusion;
* latent dynamics model.

Ứng dụng:

* robotics;
* autonomous driving;
* game agents;
* video prediction;
* planning;
* simulation.

---

## 25. Vision-Language-Action models

Kiến trúc:

```text
Image/Video + Language Instruction
                 ↓
         Multimodal model
                 ↓
            Action tokens
```

Output không chỉ là text mà có thể là:

* robot joint;
* trajectory;
* click;
* mouse/keyboard action;
* API/tool call;
* vehicle control.

Đây là hướng chuyển từ mô hình “hiểu và trả lời” sang mô hình “quan sát và hành động”.

---

# XI. Agentic architecture

Agent không nhất thiết là một backbone mới. Nó là kiến trúc hệ thống:

```text
User task
   ↓
Planner
   ↓
Reasoning model
   ↓
Tool execution
   ↓
Observation
   ↓
Memory
   ↓
Replan
```

Các thành phần:

* LLM;
* tool calling;
* code executor;
* retrieval;
* short-term memory;
* long-term memory;
* verifier;
* planner;
* environment feedback.

GLM-5 và GLM-5.2 được định hướng nhiều hơn cho agentic coding và các tác vụ dài hạn, nhưng backbone cơ bản vẫn thuộc họ sparse-attention MoE Transformer. ([arXiv][1])

---

# XII. Các hướng phát triển chính

## Hướng 1: Transformer vẫn là lõi nhưng attention ngày càng thưa

```text
Full attention
      ↓
Sliding window
      ↓
Block sparse
      ↓
Learned sparse routing
      ↓
Hierarchical sparse attention
```

Lý do:

* vẫn cần exact retrieval;
* bảo toàn in-context learning;
* giảm chi phí context dài;
* tương thích checkpoint và phần cứng hiện có.

Đây là hướng của các model như GLM-5.x và nhiều long-context Transformer hiện đại.

---

## Hướng 2: KV cache compression

Các kỹ thuật chính:

* GQA/MQA;
* MLA hoặc latent KV;
* quantized KV cache;
* token eviction;
* token merging;
* sink tokens;
* paged attention;
* cache offloading;
* cross-layer KV sharing.

Mục tiêu không chỉ giảm FLOPs mà còn giảm memory bandwidth, vốn thường là nút thắt lớn của autoregressive decoding.

---

## Hướng 3: Hybrid attention + recurrent memory

Pure recurrent model tiết kiệm nhưng retrieval yếu. Pure attention mạnh nhưng tốn tài nguyên.

Do đó xu hướng cân bằng là:

[
\boxed{
\text{Recurrent/SSM layers}
+
\text{Periodic attention layers}
}
]

Đây là hướng Jamba, Samba và nhiều thử nghiệm hybrid hiện nay. ([arXiv][7])

---

## Hướng 4: Memory có thể chỉnh sửa

State không chỉ cộng dồn:

[
S_t=S_{t-1}+k_tv_t^T
]

mà phải có khả năng:

* erase;
* overwrite;
* update;
* consolidate;
* avoid key collision.

DeltaNet, Kimi Delta Attention và Gated DeltaNet-2 đại diện cho hướng này. Gated DeltaNet-2 đặc biệt tách gate xóa khỏi gate ghi để kiểm soát memory edit tốt hơn. ([arXiv][5])

---

## Hướng 5: Test-time learning

Model không còn hoàn toàn bất biến trong inference. Một phần memory hoặc fast weights có thể học từ context hiện tại:

[
\theta_{\text{memory}}
\leftarrow
\theta_{\text{memory}}
----------------------

\eta\nabla\mathcal L
]

Hướng này phù hợp với:

* agent dài hạn;
* adaptation theo người dùng;
* continual learning;
* xử lý context vượt giới hạn attention.

Titans là một trong các kiến trúc tiêu biểu của hướng neural long-term memory tại inference. ([arXiv][9])

---

## Hướng 6: MoE ngày càng sâu và linh hoạt

MoE tương lai không chỉ đặt trong FFN mà có thể có:

* attention experts;
* modality experts;
* memory experts;
* reasoning experts;
* tool experts;
* depth routing;
* token-dependent layer skipping.

Thay vì mọi token chạy cùng một computation graph:

[
\operatorname{Path}(x_t)
========================

g(x_t)
]

Mỗi token có thể chọn độ sâu, expert và loại memory khác nhau.

---

## Hướng 7: Adaptive compute

Không phải mọi token hoặc câu hỏi đều cần cùng lượng compute.

```text
Simple token → ít layer, ít expert
Hard token   → nhiều layer, nhiều expert
Reasoning    → nhiều inference steps
```

Các dạng:

* early exit;
* layer skipping;
* adaptive depth;
* dynamic MoE routing;
* test-time compute scaling;
* variable reasoning budget;
* speculative decoding.

GLM-5.2 có cơ chế điều chỉnh effort để cân bằng năng lực, tốc độ và chi phí cho các tác vụ dài hạn. ([z.ai][10])

---

## Hướng 8: Model nhỏ + external system

Thay vì model phải ghi nhớ và thực hiện mọi thứ:

```text
Smaller model
 + Retrieval
 + Code execution
 + Database
 + Search
 + Verifier
 + Long-term memory
```

Trong nhiều ứng dụng thực tế, cách này kinh tế và chính xác hơn một model khổng lồ hoạt động độc lập.

---

## Hướng 9: Multimodal native

Các model tương lai sẽ không còn coi image/audio/video là phụ trợ. Chúng sẽ được huấn luyện trực tiếp trên:

* text;
* image;
* audio;
* video;
* depth;
* action;
* sensor;
* UI states.

Thách thức chính là token explosion, đặc biệt với video. Vì vậy multimodal có khả năng thúc đẩy mạnh:

* temporal SSM;
* token compression;
* object-centric representation;
* hierarchical attention;
* dynamic token pruning.

---

## Hướng 10: Object-centric và event-centric video model

Thay vì biến mọi pixel/frame thành token:

```text
Pixels → millions of tokens
```

Model trích xuất:

```text
Objects
Tracks
Relationships
Events
```

Ví dụ:

[
x_t^{(i)}
=========

[
\text{appearance},
\text{position},
\text{velocity},
\text{pose},
\text{class}
]
]

Sau đó dùng:

* Mamba theo từng track;
* attention giữa object;
* graph network cho quan hệ;
* rule engine hoặc classifier cho event.

Đây là hướng hiệu quả hơn cho surveillance và traffic video so với đưa toàn bộ frame sequence vào một Video Transformer lớn.

---

# XIII. Bảng tổng hợp

| Họ kiến trúc            |                     Memory |  Training theo chiều dài |        Decode memory | Retrieval chính xác |  Streaming |
| ----------------------- | -------------------------: | -----------------------: | -------------------: | ------------------: | ---------: |
| Full Transformer        |                   KV cache |                 (O(L^2)) |               (O(L)) |            Rất mạnh | Trung bình |
| Sparse Transformer      |                  Sparse KV |              Gần (O(Lk)) | (O(L)) hoặc thấp hơn |                Mạnh |        Khá |
| MLA/GQA Transformer     |              Compressed KV |            Vẫn attention |         Giảm đáng kể |                Mạnh |        Khá |
| MoE Transformer         |               KV + experts |            Tùy attention |        Tùy attention |                Mạnh |        Khá |
| Mamba/SSM               |                Fixed state |                   (O(L)) |      (O(1)) theo (L) |          Trung bình |   Rất mạnh |
| RetNet/RWKV             |            Recurrent state |                   (O(L)) |               (O(1)) |          Trung bình |   Rất mạnh |
| DeltaNet                |      Editable fast weights |                   (O(L)) |      (O(1)) theo (L) |                 Khá |   Rất mạnh |
| Hyena/long conv         |          Convolution state | (O(L)) hoặc (O(L\log L)) |                  Nhỏ |      Trung bình/yếu |        Khá |
| Hybrid SSM-attention    |                 State + KV |           Gần tuyến tính |           Trung bình |                Mạnh |   Rất mạnh |
| Titans/test-time memory | Attention + learned memory |             Tùy cấu hình |         Memory riêng |   Có tiềm năng mạnh |        Khá |
| RAG/external memory     |             Database/index |           Ngoài backbone |   Gần không giới hạn | Phụ thuộc retriever |        Khá |

---

# XIV. Dự đoán hướng kiến trúc thực dụng

Khả năng cao không có một kiến trúc duy nhất thay thế hoàn toàn Transformer. Kiến trúc tổng hợp có thể tiến dần tới:

```text
Local convolution
        ↓
Linear recurrent / Mamba state
        ↓
Occasional sparse attention
        ↓
MoE transformation
        ↓
External/test-time memory
        ↓
Tool and environment interaction
```

Tương ứng:

[
\boxed{
\text{Future model}
===================

\text{Recurrent state}
+
\text{Sparse retrieval}
+
\text{MoE capacity}
+
\text{External memory}
+
\text{Adaptive compute}
}
]

Với bài toán cụ thể:

* **LLM reasoning/coding:** sparse-attention MoE Transformer hoặc hybrid.
* **Agent dài hạn:** attention + hierarchical/test-time/external memory.
* **Time series/sensor:** Mamba, SSM, TCN hoặc hybrid.
* **Video surveillance:** spatial Transformer + temporal Mamba + object attention.
* **Streaming realtime:** recurrent SSM/DeltaNet.
* **Exact long-context retrieval:** sparse/full attention vẫn quan trọng.
* **Multimodal generation:** Transformer kết hợp diffusion hoặc flow matching.
* **Robotics:** vision-language-action model kết hợp world model và memory.

[1]: https://arxiv.org/abs/2602.15763?utm_source=chatgpt.com "GLM-5: from Vibe Coding to Agentic Engineering"
[2]: https://arxiv.org/abs/2503.18970?utm_source=chatgpt.com "A Survey on Structured State Space Sequence (S4) Models"
[3]: https://arxiv.org/abs/2603.15569?utm_source=chatgpt.com "Mamba-3: Improved Sequence Modeling using State Space Principles"
[4]: https://arxiv.org/abs/2307.08621?utm_source=chatgpt.com "Retentive Network: A Successor to Transformer for Large Language Models"
[5]: https://arxiv.org/abs/2605.22791?utm_source=chatgpt.com "Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention"
[6]: https://arxiv.org/pdf/2312.04927?utm_source=chatgpt.com "Zoology: Measuring and Improving Recall in Efficient Language"
[7]: https://arxiv.org/abs/2403.19887?utm_source=chatgpt.com "Jamba: A Hybrid Transformer-Mamba Language Model"
[8]: https://arxiv.org/abs/2406.07522?utm_source=chatgpt.com "[2406.07522] Samba: Simple Hybrid State Space Models ..."
[9]: https://arxiv.org/abs/2501.00663?utm_source=chatgpt.com "Titans: Learning to Memorize at Test Time"
[10]: https://z.ai/blog/glm-5.2?utm_source=chatgpt.com "GLM-5.2: Built for Long-Horizon Tasks"
