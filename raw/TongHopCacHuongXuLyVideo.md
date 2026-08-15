Nếu nhìn “temporal learning trên video” theo góc độ nghiên cứu, nó không chỉ là action recognition. Có thể chia tương đối đầy đủ thành **8 nhóm bài toán lớn**, từ nhận dạng clip ngắn cho tới reasoning trên video dài và Video-LLM. Các survey gần đây cũng đang dịch chuyển taxonomy theo hướng này: từ backbone spatiotemporal truyền thống → Transformer → video foundation model → multimodal/LLM-based temporal reasoning. ([arXiv][1])

## 1. Video Action Recognition — “Video này đang làm gì?”

Đây là bài toán kinh điển nhất:

[
V = {I_1,\ldots,I_T}\rightarrow y
]

Input là một clip, output là một action/class label.

Điểm cốt lõi là mô hình phải học được cả **appearance/spatial information** và **motion/temporal dynamics**.

### Các nhánh phương pháp chính

**2D CNN + temporal aggregation**

Các frame được encode độc lập rồi tổng hợp theo thời gian.

Các hướng tiêu biểu:

* Two-stream: RGB + optical flow
* Temporal Segment Networks — TSN
* temporal pooling / consensus
* temporal shift / temporal convolution

TSN đặc biệt quan trọng vì nó đưa ra ý tưởng sample các segment rải khắp video nhằm bắt được long-range temporal structure thay vì chỉ nhìn một clip liên tục ngắn. ([Open Access CVF][2])

---

**3D CNN**

Convolution trực tiếp trên:

[
H\times W\times T
]

Các paper nền tảng:

* **C3D — Learning Spatiotemporal Features with 3D Convolutional Networks**
* **I3D — Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset**, Carreira & Zisserman, CVPR 2017.
* **R(2+1)D — A Closer Look at Spatiotemporal Convolutions for Action Recognition**, CVPR 2018.
* **3D ResNet**
* **SlowFast Networks for Video Recognition**, ICCV 2019.
* X3D.

I3D “inflate” 2D convolution thành 3D và cho thấy pretraining trên Kinetics đem lại bước nhảy rất lớn cho action recognition. ([Open Access CVF][3]) R(2+1)D lại tách 3D convolution thành spatial convolution và temporal convolution, giúp disentangle hai loại processing. ([Open Access CVF][4])

**SlowFast** là paper rất đáng đọc nếu nghiên cứu temporal. Nó dùng hai sampling rate:

* **Slow pathway:** frame rate thấp → semantics/appearance.
* **Fast pathway:** frame rate cao → motion.

Ý tưởng nền tảng là spatial semantics thay đổi chậm, trong khi motion cần temporal resolution cao. ([Open Access CVF][5])

---

**Non-local / attention**

Một vấn đề của convolution là receptive field temporal tăng khá chậm. Non-local networks đưa global interaction vào video:

[
y_i = \frac{1}{C(x)}
\sum_j f(x_i,x_j)g(x_j)
]

Sau này self-attention của Transformer có thể xem là sự tổng quát hóa rất tự nhiên của hướng này. TimeSformer cũng đặt Non-local Networks trong lineage trực tiếp dẫn tới space-time self-attention. ([Proceedings of Machine Learning Research][6])

---

## 2. Video Transformer / Explicit temporal attention

Khoảng 2021 trở đi, temporal modeling chuyển mạnh sang Transformer.

### TimeSformer

**Is Space-Time Attention All You Need for Video Understanding?**

Thay vì 3D convolution, video được chia thành patch tokens:

[
X \in \mathbb{R}^{T\times N\times D}
]

và thực hiện self-attention trên space-time.

Một ý tưởng quan trọng là **Divided Space-Time Attention**:

[
\text{Temporal Attention}
\rightarrow
\text{Spatial Attention}.
]

Điều này giảm đáng kể complexity so với full space-time attention. ([Proceedings of Machine Learning Research][6])

### ViViT

**ViViT: A Video Vision Transformer**

Các variant:

* full spatiotemporal attention
* factorized encoder
* factorized self-attention

Concept quan trọng:

[
\text{Spatial encoder}
\rightarrow
\text{Temporal encoder}.
]

### MViT

**Multiscale Vision Transformers**

Thay vì giữ số token cố định, MViT xây dựng hierarchy:

[
T_1H_1W_1
\rightarrow
T_2H_2W_2
\rightarrow
...
]

tương tự feature pyramid của CNN nhưng bằng Transformer. MViT trở thành một trong các backbone quan trọng của video recognition hiện đại. ([Open Access CVF][7])

### Video Swin Transformer

Window attention được mở rộng từ ảnh sang không-thời gian bằng shifted 3D windows, giúp giảm cost của global attention. ([Open Access CVF][8])

---

# 3. Temporal Action Localization / Temporal Action Detection

Đây là nhóm bài toán quan trọng hơn action recognition nếu bạn thực sự muốn nghiên cứu **temporal understanding**.

Input:

> video dài, untrimmed.

Output:

[
{(s_i,e_i,c_i)}_{i=1}^{N}
]

với:

* (s_i): start time
* (e_i): end time
* (c_i): action class.

Ví dụ:

```text
0s                    100s
|-----------------------|

     [cut onion]
              [fry]
                     [eat]
```

### Các hướng chính

**Proposal-based**

Pipeline:

[
Video
\rightarrow
Temporal features
\rightarrow
Action proposals
\rightarrow
Classification
]

Paper quan trọng:

* **BSN — Boundary Sensitive Network**
* **BMN — Boundary-Matching Network for Temporal Action Proposal Generation**, ICCV 2019.

BMN học đồng thời precise action boundaries và proposal confidence. ([Open Access CVF][9])

Một research question kinh điển ở đây là:

> Làm sao học boundary chính xác khi transition giữa hai action mờ?

---

**Anchor-free temporal detection**

Xu hướng sau này chuyển từ proposal pipeline phức tạp sang direct detection.

Paper rất đáng đọc:

### ActionFormer

**ActionFormer: Localizing Moments of Actions with Transformers**, ECCV 2022.

Concept:

```text
video features
      ↓
temporal feature pyramid
      ↓
local self-attention
      ↓
class + boundary regression
```

Local attention đặc biệt hợp với video dài vì full attention là:

[
O(T^2).
]

ActionFormer trở thành baseline rất phổ biến cho TAL; nhiều paper TAL sau đó dùng nó làm điểm so sánh. ([Open Access CVF][10])

Các hướng tiếp:

* TriDet
* TadTR
* Re2TAL
* DETR-style TAL
* Dual-DETR
* open-vocabulary TAL.

---

## 4. Weakly/Semi-supervised Temporal Action Localization

Một vấn đề lớn của TAL là annotation đắt:

```text
cut onion: 12.5s → 19.8s
pour oil: 22.1s → 25.6s
...
```

Do đó xuất hiện:

### Weakly-supervised TAL

Training chỉ biết:

```text
video → {cut, fry, eat}
```

nhưng inference phải tìm:

```text
cut → [12s, 20s]
```

Bài toán trở thành:

[
\text{video-level supervision}
\rightarrow
\text{frame/segment localization}.
]

Có nhiều hướng:

* class activation sequence
* multiple-instance learning
* pseudo labels
* contrastive learning
* semantic/text supervision.

Ví dụ paper CVPR 2023 định nghĩa WTAL chính xác theo setup video-level labels nhưng phải suy ra action boundaries trong untrimmed video. ([Open Access CVF][11])

Gần đây text/CLIP cũng được đưa vào để tăng semantic guidance. ([Open Access CVF][12])

---

# 5. Temporal Action Segmentation

Khác TAL một chút.

TAL:

[
{(s,e,c)}
]

Action segmentation:

[
I_t \rightarrow y_t,\quad \forall t.
]

Tức là **gán action label cho từng frame/timestep**.

Ví dụ:

```text
frame:
1 2 3 4 5 6 7 8 9 ...

action:
A A A A B B B C C ...
```

Bài toán đặc biệt quan trọng trong:

* cooking
* surgery
* assembly
* industrial processes
* human activities.

### MS-TCN

**Multi-Stage Temporal Convolutional Network for Action Segmentation**

Kiến trúc:

```text
Stage 1 → prediction
            ↓
Stage 2 → refine
            ↓
Stage 3 → refine
...
```

Sau MS-TCN xuất hiện:

* MS-TCN++
* ASFormer
* DiffAct
* DETR/Transformer segmentation models.

Các công trình mới vẫn xem MS-TCN, ASFormer và DiffAct như các reference families chủ yếu của temporal action segmentation. ([Open Access CVF][13])

Một vấn đề lớn ở đây là **over-segmentation**:

```text
GT:       AAAAA BBBBB CCCCC
Prediction AAA AB BB B CC CC
```

do feature noise gây ra boundary fragmentation.

---

# 6. Action Anticipation / Future Prediction

Thay vì hỏi:

> Đang xảy ra gì?

ta hỏi:

> **Sắp xảy ra gì?**

Formal:

[
V_{1:t}\rightarrow
A_{t+\Delta}.
]

Ví dụ:

```text
person opens fridge
person takes egg
person takes pan
      ↓
predict: crack egg
```

Bài toán này rất quan trọng cho:

* robotics
* autonomous driving
* wearable AI
* assistants
* egocentric video.

Một definition phổ biến là dự đoán action tương lai từ các past/current observations. ([Open Access CVF][14])

### Long-term action anticipation

Không chỉ next action mà:

[
V_{\leq t}
\rightarrow
(A_{t+1},A_{t+2},...,A_{t+k}).
]

Paper đáng đọc:

**Future Transformer for Long-Term Action Anticipation**, CVPR 2022.

Nó dùng attention để model global interaction giữa past observations và chuỗi future actions, đồng thời decode future sequence theo hướng parallel. ([Open Access CVF][15])

### Online Action Understanding

Online setting buộc model chỉ được nhìn:

[
I_1,\ldots,I_t
]

không được nhìn future frames.

Một paper tốt:

**Memory-and-Anticipation Transformer**, ICCV 2023.

Nó kết hợp historical memory với future anticipation trong online action understanding. ([Open Access CVF][16])

Các hướng mới:

* uncertainty-aware anticipation
* future object prediction
* next-active-object
* multimodal anticipation
* LLM/VLM-based future reasoning.

Ví dụ UADT CVPR 2024 dùng uncertainty-aware decoupling cho anticipation. ([Open Access CVF][17])

---

# 7. Self-Supervised Temporal Representation Learning

Đây là nhánh rất đáng chú ý nếu mục tiêu là **học temporal representation** thay vì giải một task cụ thể.

Ta muốn:

[
f(V)\rightarrow z
]

sao cho (z) encode:

* appearance
* motion
* ordering
* dynamics
* long-term semantics.

Không cần human labels.

Ba family phổ biến hiện nay là:

* transformation/order prediction
* contrastive learning
* masked video modeling. ([arXiv][18])

## VideoMAE

**VideoMAE: Masked Autoencoders are Data-Efficient Learners for Self-Supervised Video Pre-Training**, NeurIPS 2022.

Randomly mask phần rất lớn spatiotemporal tubes:

[
X_{\text{video}}
\xrightarrow{\text{mask }\sim90%}
X_{\text{visible}}
]

Encoder:

[
z=E(X_{\text{visible}})
]

Decoder reconstruct:

[
\hat X=D(z).
]

Video có redundancy temporal rất cao, nên high masking ratio vẫn hoạt động tốt. VideoMAE cho thấy masked autoencoding là một paradigm rất data-efficient cho video SSL. ([NIPS Proceedings][19])

Đây là một trong những paper mình xem là **must-read**.

---

# 8. Video Foundation Models

Xu hướng tiếp theo là:

[
\text{single task video model}
\rightarrow
\text{general-purpose video representation}.
]

Survey về Video Foundation Models đã thống kê hơn 200 model và phân chúng thành image-based ViFM, video-based ViFM và universal multimodal foundation models. ([arXiv][20])

### InternVideo

Một model rất có ảnh hưởng.

Nó kết hợp:

[
\text{Masked Video Modeling}
+
\text{Video-Language Contrastive Learning}.
]

Mục đích là lấy:

* generative temporal representation
* semantic text alignment

trong cùng foundation model. ([arXiv][21])

### InternVideo2

InternVideo2 scale hướng này lên đáng kể và sử dụng progressive training với:

* masked video modeling
* cross-modal contrastive learning
* next-token prediction.

Model được đánh giá trên hơn 60 video/audio tasks và hướng đến cả recognition, video-text tasks và video dialogue. ([arXiv][22])

Điều đáng chú ý ở đây là temporal representation không còn được tối ưu duy nhất bằng supervised action labels.

---

# 9. Video–Language Temporal Grounding

Một nhánh đang phát triển rất mạnh:

> Cho câu mô tả/query, tìm đoạn video tương ứng.

Input:

[
(V,q)
]

output:

[
(s,e).
]

Ví dụ:

```text
Query:
"the man starts cutting the onion"

Video:
|---------------------------|
          ↑            ↑
         14s          23s
```

Đây được gọi là:

* temporal grounding
* moment retrieval
* temporal sentence grounding
* natural language video localization.

Các survey gần đây ghi nhận temporal grounding đang chuyển mạnh từ các model task-specific sang multimodal LLM-based methods. ([arXiv][23])

Một paper 2025 đáng chú ý:

### UniTime

**Universal Video Temporal Grounding with Generative Multi-modal Large Language Models**

Nó đưa timestamp tokens xen kẽ với video tokens và sử dụng adaptive frame scaling để xử lý cả video ngắn và dài. ([arXiv][24])

Một hướng khác là **VideoITG**, xây supervision ở scale lớn với 40K videos và khoảng 500K temporal grounding annotations, kết hợp instruction-conditioned captions, retrieval và discriminative frame selection. ([arXiv][25])

---

# 10. Long Video Understanding

Đây có lẽ là một trong những research directions quan trọng nhất hiện nay.

Ví dụ:

```text
2-hour video
     ↓
What happened before X?
Why did X happen?
When did X occur?
What happened after X?
Which event caused Y?
```

Vấn đề đầu tiên là token complexity.

Giả sử:

[
30 FPS\times3600s =108,000\ frames/hour.
]

Nếu mỗi frame có hàng trăm visual tokens thì không thể đơn giản feed toàn bộ vào Transformer.

Do đó xuất hiện các hướng:

### Temporal compression

```text
frames
 ↓
short clips
 ↓
clip tokens
 ↓
event tokens
 ↓
long-term memory
```

### Hierarchical temporal modeling

[
frame
\rightarrow clip
\rightarrow event
\rightarrow scene
\rightarrow video.
]

### Memory architectures

[
M_t=f(M_{t-1},X_t).
]

### Query-guided sampling

Thay vì uniform sampling:

[
P(frame_i|question).
]

Các phương pháp long-video mới ngày càng dùng hierarchical compression hoặc query-dependent retrieval để tránh quadratic token growth. ([arXiv][26])

---

## LV-MAE

Một ví dụ đặc biệt sát chủ đề temporal:

**LV-MAE: Learning Long Video Representations through Masked Embedding Autoencoders**, 2025.

Nó tách temporal modeling thành hai tầng:

[
\text{short-span dependencies}
\rightarrow
\text{long-span dependencies}.
]

Nói cách khác:

```text
raw frames
   ↓
local spatiotemporal primitives
   ↓
segment representations
   ↓
long-range temporal model
```

Đây là hướng rất hợp lý cho long video vì không ép một model duy nhất học cùng lúc frame-level và hour-level relationships. ([arXiv][27])

---

# 11. Temporal Reasoning với Video-LLM

Đây là lớp bài toán cao hơn recognition.

Ví dụ:

**Ordering**

> A xảy ra trước hay sau B?

**Duration**

> A kéo dài bao lâu?

**Frequency**

> A xảy ra mấy lần?

**Causal**

> Vì sao B xảy ra?

**Multi-hop**

> Điều gì xảy ra giữa A và C?

**State transition**

[
S_t \xrightarrow{action} S_{t+1}.
]

Survey Video-LLM hiện xem temporal localization, event understanding và temporal reasoning là các capability riêng, không thể quy về image QA đơn thuần. ([arXiv][28])

Một khó khăn hiện tại là nhiều MLLM khá mạnh về semantic appearance nhưng vẫn kém ở **fine-grained temporal reasoning**. Các nghiên cứu 2025–2026 đang thử timestamp-aware training, temporal grounding supervision và RL cho vấn đề này. ([arXiv][29])

---

# 12. Neuro-symbolic / Explicit Temporal Logic

Một hướng khá thú vị và mới là không bắt LLM tự “cảm nhận” mọi relation temporal mà biểu diễn chúng một cách explicit.

Ví dụ:

[
A\ before\ B
]

[
A\ overlaps\ B
]

[
A\ during\ B.
]

Một paper đáng chú ý:

### NeuS-QA

**Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning**, 2025.

Pipeline đại ý:

```text
question
   ↓
temporal logic expression
   ↓
video event propositions
   ↓
model checking
   ↓
relevant segments
   ↓
VLM reasoning
```

Mục tiêu là enforce được event ordering/compositional relations thay vì dựa hoàn toàn vào heuristic frame sampling. ([arXiv][30])

Đây là hướng rất đáng nghiên cứu nếu bạn quan tâm đến **temporal reasoning thật sự**, chứ không chỉ video encoding.

---

# 13. Open-Vocabulary / Zero-Shot Temporal Understanding

Một xu hướng khác là không giới hạn action classes trong training set.

Truyền thống:

[
C_{\text{train}}=C_{\text{test}}.
]

Open vocabulary:

[
C_{\text{test}}
\not\subseteq
C_{\text{train}}.
]

Text encoder/CLIP tạo semantic space:

[
z_v \leftrightarrow z_t.
]

Ứng dụng:

* open-vocabulary action recognition
* open-vocabulary TAL
* text-driven moment detection.

Ví dụ, WACV 2025 nghiên cứu self-training ở scale lớn cho **Open-Vocabulary Temporal Action Localization**. ([Open Access CVF][31])

---

# 14. Efficient / Sparse Temporal Modeling

Một vấn đề nghiên cứu cực kỳ thực tế:

[
\text{Temporal information}
\uparrow
\qquad
\text{Computation}
\downarrow.
]

Các kỹ thuật:

* sparse frame sampling
* token pruning
* temporal pooling
* adaptive resolution
* local attention
* hierarchical attention
* selective memory
* state-space models.

Ví dụ có các phương pháp prune spatiotemporal token bằng semantic-aware temporal accumulation. ([Open Access CVF][32])

Đến 2025–2026, nghiên cứu tiếp tục dịch sang **adaptive temporal computation**: video có những đoạn gần như static và những đoạn dynamics rất cao, do đó không nên cấp cùng mức compute cho mọi timestamp. FlexiVideo CVPR 2026 là một ví dụ của hướng variation-aware temporal dynamics modeling. ([Open Access CVF][33])

---

# 15. State Space Models / Mamba cho Video

Một hướng thay Transformer:

[
x_t
\rightarrow
h_t
\rightarrow
h_{t+1}.
]

State-space model có complexity gần:

[
O(T)
]

so với global attention:

[
O(T^2).
]

Điều này hấp dẫn cho:

* long video
* streaming video
* dense temporal modeling.

VideoMamba và các biến thể tiếp tục được nghiên cứu; chẳng hạn ICCV 2025 có **Snakes and Ladders: Two Steps Up for VideoMamba**. ([Open Access CVF][34])

Theo mình đây là một trong những nhánh đáng theo dõi nhất nếu bài toán của bạn có sequence length lớn.

---

# Bản đồ tổng hợp

Có thể nhìn toàn bộ field như sau:

```text
VIDEO TEMPORAL LEARNING
│
├── Short clip
│   ├── Action Recognition
│   └── Motion Recognition
│
├── Untrimmed video
│   ├── Temporal Action Localization
│   ├── Temporal Action Detection
│   └── Action Segmentation
│
├── Future
│   ├── Action Anticipation
│   └── Long-term Forecasting
│
├── Representation Learning
│   ├── Contrastive Learning
│   ├── Masked Video Modeling
│   └── Video Foundation Models
│
├── Video + Language
│   ├── Temporal Grounding
│   ├── Moment Retrieval
│   ├── Video QA
│   └── Video Captioning
│
├── Long Video
│   ├── Temporal Compression
│   ├── Hierarchical Modeling
│   ├── Memory
│   └── Retrieval
│
└── Temporal Reasoning
    ├── Ordering
    ├── Duration
    ├── Frequency
    ├── State transitions
    ├── Causality
    └── Multi-hop reasoning
```

---

# Danh sách paper mình khuyên đọc

Nếu mục tiêu là đi từ **temporal modeling nền tảng → research hiện đại**, mình sẽ đọc theo thứ tự:

| Giai đoạn  | Paper                               | Ý tưởng chính                         |
| ---------- | ----------------------------------- | ------------------------------------- |
| Foundation | Two-Stream ConvNets                 | appearance + optical flow             |
| Foundation | Temporal Segment Networks           | long-range sampling                   |
| 2017       | I3D                                 | 3D convolution + Kinetics             |
| 2018       | R(2+1)D                             | factorized spatial/temporal conv      |
| 2018       | Non-local Neural Networks           | long-range interactions               |
| 2019       | SlowFast                            | multi-rate temporal pathways          |
| 2019       | BMN                                 | temporal boundary/proposal            |
| 2019       | MS-TCN                              | dense temporal segmentation           |
| 2021       | TimeSformer                         | space-time attention                  |
| 2021       | ViViT                               | video Transformer                     |
| 2021       | MViT                                | multiscale Transformer                |
| 2022       | Video Swin                          | local 3D windows                      |
| 2022       | VideoMAE                            | masked temporal pretraining           |
| 2022       | ActionFormer                        | TAL with local Transformer            |
| 2022       | Future Transformer                  | long-term anticipation                |
| 2022/23    | InternVideo                         | video foundation models               |
| 2023       | Memory-and-Anticipation Transformer | online temporal understanding         |
| 2024       | InternVideo2                        | large-scale multimodal video FM       |
| 2025       | LV-MAE                              | long-video representation learning    |
| 2025       | UniTime                             | MLLM temporal grounding               |
| 2025       | VideoITG                            | instruction-guided temporal grounding |
| 2025       | NeuS-QA                             | temporal logic + VLM                  |
| 2026       | Foresee-to-Ground                   | evidence-driven temporal grounding    |

Các paper VideoMAE, SlowFast, BMN, ActionFormer, Future Transformer, InternVideo2 và các công trình long-video/grounding mới phía trên đều trực tiếp đại diện cho những bước chuyển quan trọng của field. ([NIPS Proceedings][19])

## Nếu mục tiêu là tìm **research gap**

Mình thấy 6 hướng hiện đặc biệt đáng đào sâu:

1. **Long-range temporal modeling**: làm sao xử lý hàng chục phút/giờ mà vẫn giữ fine-grained events. LV-MAE và hierarchical compression mới giải quyết một phần. ([arXiv][27])
2. **Temporal representation vs appearance bias**: video foundation models vẫn có trade-off giữa motion understanding và appearance understanding; benchmark TWLV-I cho thấy nhiều ViFM mạnh ở một phía nhưng yếu ở phía còn lại. ([arXiv][35])
3. **Precise temporal grounding của Video-LLM**: LLM sinh timestamp dưới dạng text thường khá brittle; các nghiên cứu mới bắt đầu chuyển sang evidence/segment-based grounding. ([arXiv][36])
4. **Temporal causality**: “A trước B” tương đối dễ hơn “B xảy ra vì A”. Đây vẫn là điểm yếu rõ của long-video reasoning. ([arXiv][30])
5. **Adaptive temporal computation**: không xử lý mọi frame với cùng compute; sparse tokens, adaptive sampling và dynamic temporal resolution có tiềm năng lớn. ([Open Access CVF][32])
6. **Unified temporal model**: một representation có thể dùng đồng thời cho recognition, TAL, segmentation, anticipation, grounding và reasoning. Đây chính là motivation lớn phía sau Video Foundation Models, nhưng survey hiện tại cho thấy vẫn chưa có một kiến trúc thắng tuyệt đối trên mọi dạng video understanding. ([arXiv][20])

Nếu bạn đang muốn chọn **đề tài nghiên cứu cụ thể**, mình sẽ ưu tiên đào sâu vào trục **Long Video + Temporal Grounding + Temporal Reasoning**, thay vì chỉ action recognition. Action recognition hiện khá trưởng thành; còn việc model hiểu đúng **“khi nào – trước/sau – kéo dài bao lâu – nguyên nhân/hệ quả – sự kiện nào liên quan”** trên video dài vẫn còn nhiều khoảng trống nghiên cứu. ([arXiv][23])

[1]: https://arxiv.org/abs/2302.01921?utm_source=chatgpt.com "Transformers in Action Recognition: A Review on Temporal Modeling"
[2]: https://openaccess.thecvf.com/content_cvpr_2017_workshops/w14/papers/Lan_Deep_Local_Video_CVPR_2017_paper.pdf?utm_source=chatgpt.com "Deep Local Video Feature for Action Recognition"
[3]: https://openaccess.thecvf.com/content_cvpr_2017/html/Carreira_Quo_Vadis_Action_CVPR_2017_paper.html?utm_source=chatgpt.com "Kinetics Dataset - CVPR 2017 Open Access Repository"
[4]: https://openaccess.thecvf.com/content_cvpr_2018/CameraReady/2648.pdf?utm_source=chatgpt.com "A Closer Look at Spatiotemporal Convolutions for Action ..."
[5]: https://openaccess.thecvf.com/content_ICCV_2019/papers/Feichtenhofer_SlowFast_Networks_for_Video_Recognition_ICCV_2019_paper.pdf?utm_source=chatgpt.com "SlowFast Networks for Video Recognition"
[6]: https://proceedings.mlr.press/v139/bertasius21a/bertasius21a.pdf?utm_source=chatgpt.com "Is Space-Time Attention All You Need for Video Understanding?"
[7]: https://openaccess.thecvf.com/content/CVPR2023/papers/Zhou_How_Can_Objects_Help_Action_Recognition_CVPR_2023_paper.pdf?utm_source=chatgpt.com "How Can Objects Help Action Recognition? - CVF Open Access"
[8]: https://openaccess.thecvf.com/content/CVPR2022/papers/Yang_Temporally_Efficient_Vision_Transformer_for_Video_Instance_Segmentation_CVPR_2022_paper.pdf?utm_source=chatgpt.com "Temporally Efficient Vision Transformer for Video Instance ..."
[9]: https://openaccess.thecvf.com/content_ICCV_2019/html/Lin_BMN_Boundary-Matching_Network_for_Temporal_Action_Proposal_Generation_ICCV_2019_paper.html?utm_source=chatgpt.com "ICCV 2019 Open Access Repository"
[10]: https://openaccess.thecvf.com/content/CVPR2023/papers/Zhao_Re2TAL_Rewiring_Pretrained_Video_Backbones_for_Reversible_Temporal_Action_Localization_CVPR_2023_paper.pdf?utm_source=chatgpt.com "Re2TAL: Rewiring Pretrained Video Backbones for Reversible ..."
[11]: https://openaccess.thecvf.com/content/CVPR2023/papers/Wang_Two-Stream_Networks_for_Weakly-Supervised_Temporal_Action_Localization_With_Semantic-Aware_Mechanisms_CVPR_2023_paper.pdf?utm_source=chatgpt.com "Two-Stream Networks for Weakly-Supervised Temporal Action ..."
[12]: https://openaccess.thecvf.com/content/CVPR2023/papers/Li_Boosting_Weakly-Supervised_Temporal_Action_Localization_With_Text_Information_CVPR_2023_paper.pdf?utm_source=chatgpt.com "Boosting Weakly-Supervised Temporal Action Localization ..."
[13]: https://openaccess.thecvf.com/content/ICCV2025W/SVU/papers/Wang_End-to-End_Action_Segmentation_Transformer_ICCVW_2025_paper.pdf?utm_source=chatgpt.com "End-to-End Action Segmentation Transformer"
[14]: https://openaccess.thecvf.com/content/WACV2024/papers/Thakur_Leveraging_Next-Active_Objects_for_Context-Aware_Anticipation_in_Egocentric_Videos_WACV_2024_paper.pdf?utm_source=chatgpt.com "Leveraging Next-Active Objects for Context-Aware ..."
[15]: https://openaccess.thecvf.com/content/CVPR2022/papers/Gong_Future_Transformer_for_Long-Term_Action_Anticipation_CVPR_2022_paper.pdf?utm_source=chatgpt.com "Future Transformer for Long-Term Action Anticipation"
[16]: https://openaccess.thecvf.com/content/ICCV2023/papers/Wang_Memory-and-Anticipation_Transformer_for_Online_Action_Understanding_ICCV_2023_paper.pdf?utm_source=chatgpt.com "Memory-and-Anticipation Transformer for Online Action ..."
[17]: https://openaccess.thecvf.com/content/CVPR2024/html/Guo_Uncertainty-aware_Action_Decoupling_Transformer_for_Action_Anticipation_CVPR_2024_paper.html?utm_source=chatgpt.com "paper - CVPR 2024 Open Access Repository"
[18]: https://arxiv.org/pdf/2504.00527?utm_source=chatgpt.com "arXiv:2504.00527v1 [cs.CV] 1 Apr 2025"
[19]: https://papers.nips.cc/paper_files/paper/2022/hash/416f9cb3276121c42eebb86352a4354a-Abstract-Conference.html?utm_source=chatgpt.com "VideoMAE: Masked Autoencoders are Data-Efficient ..."
[20]: https://arxiv.org/abs/2405.03770?utm_source=chatgpt.com "Foundation Models for Video Understanding: A Survey"
[21]: https://arxiv.org/abs/2212.03191?utm_source=chatgpt.com "InternVideo: General Video Foundation Models via Generative and Discriminative Learning"
[22]: https://arxiv.org/abs/2403.15377?utm_source=chatgpt.com "InternVideo2: Scaling Foundation Models for Multimodal Video Understanding"
[23]: https://arxiv.org/abs/2508.10922?utm_source=chatgpt.com "A Survey on Video Temporal Grounding with Multimodal ..."
[24]: https://arxiv.org/abs/2506.18883?utm_source=chatgpt.com "Universal Video Temporal Grounding with Generative Multi-modal Large Language Models"
[25]: https://arxiv.org/abs/2507.13353?utm_source=chatgpt.com "VideoITG: Multimodal Video Understanding with Instructed ..."
[26]: https://arxiv.org/html/2501.00574v4?utm_source=chatgpt.com "Hierarchical Compression for Long-Context Video Modeling"
[27]: https://arxiv.org/html/2504.03501v2?utm_source=chatgpt.com "LV-MAE: Learning Long Video Representations through ..."
[28]: https://arxiv.org/html/2312.17432v5?utm_source=chatgpt.com "Video Understanding with Large Language Models:A Survey"
[29]: https://arxiv.org/pdf/2505.20715?utm_source=chatgpt.com "standing via Timestamp-Aware Multi-Segment Grounding"
[30]: https://arxiv.org/abs/2509.18041?utm_source=chatgpt.com "NeuS-QA: Grounding Long-Form Video Understanding in Temporal Logic and Neuro-Symbolic Reasoning"
[31]: https://openaccess.thecvf.com/content/WACV2025/papers/Hyun_Exploring_Scalability_of_Self-Training_for_Open-Vocabulary_Temporal_Action_Localization_WACV_2025_paper.pdf?utm_source=chatgpt.com "Exploring Scalability of Self-Training for Open-Vocabulary ..."
[32]: https://openaccess.thecvf.com/content/ICCV2023/papers/Ding_Prune_Spatio-temporal_Tokens_by_Semantic-aware_Temporal_Accumulation_ICCV_2023_paper.pdf?utm_source=chatgpt.com "Prune Spatio-temporal Tokens by Semantic-aware Temporal ..."
[33]: https://openaccess.thecvf.com/content/CVPR2026/papers/Peng_FlexiVideo_Variation-Aware_Temporal_Dynamics_Modeling_for_Efficient_Video_Understanding_CVPR_2026_paper.pdf?utm_source=chatgpt.com "FlexiVideo: Variation-Aware Temporal Dynamics Modeling for ..."
[34]: https://openaccess.thecvf.com/content/ICCV2025/papers/Lu_Snakes_and_Ladders_Two_Steps_Up_for_VideoMamba_ICCV_2025_paper.pdf?utm_source=chatgpt.com "Snakes and Ladders: Two Steps Up for VideoMamba"
[35]: https://arxiv.org/abs/2408.11318?utm_source=chatgpt.com "TWLV-I: Analysis and Insights from Holistic Evaluation on Video Foundation Models"
[36]: https://arxiv.org/abs/2605.21973?utm_source=chatgpt.com "Foresee-to-Ground: From Predictive Temporal Perception to Evidence-Driven Reasoning for Video Temporal Grounding"
