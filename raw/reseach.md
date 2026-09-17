Mình đã rà các nguồn chính đến **17/09/2026**, ưu tiên arXiv/CVF/OpenReview, repo chính chủ và tài liệu benchmark của tác giả. Phạm vi “tất cả” theo nghĩa tuyệt đối là không khả thi vì mỗi tuần có thêm preprint; bảng dưới đây bao phủ các **dòng công trình có ảnh hưởng trực tiếp tới SOTA object detection / instance segmentation trong khoảng 2024–2026**, cùng những repo/model đáng theo dõi.

## Bức tranh tổng thể

Nếu rút gọn toàn bộ tiến triển 1–2 năm gần đây thành một câu thì đó là:

> **Object detection đang hội tụ từ “YOLO vs DETR” sang end-to-end detector dùng supervision/matching tốt hơn + representation từ vision foundation model; đồng thời detection, segmentation và tracking đang hợp nhất thành một hệ promptable/open-vocabulary perception.**

DETR real-time đã tiến rất nhanh từ RT-DETRv2 → RT-DETRv3 → D-FINE/DEIM → DEIMv2/RT-DETRv4. Trong khi đó YOLO cũng đi theo hướng attention và **NMS-free end-to-end**, rõ ở YOLOv12 và YOLO26. Ở tầng representation, DINOv3 cho thấy backbone self-supervised có dense feature đủ mạnh để một backbone đông cứng vẫn đạt kết quả rất cao trên detection/segmentation; DEIMv2 và RT-DETRv4 sau đó khai thác trực tiếp ý tưởng này. ([arXiv.org][1])

Ở một trục khác, YOLO-World → Grounding DINO 1.5/T-Rex2 → YOLOE → SAM 3 cho thấy taxonomy class cố định đang dần bị thay bởi **text prompt, visual exemplar và open vocabulary**. SAM 3 đặc biệt quan trọng vì một model có thể **detect + segment + track tất cả instance phù hợp với một concept prompt** thay vì phải ghép detector và SAM thủ công. ([Open Access CVF][2])

---

## Những paper/model/repo quan trọng nhất

| Năm     | Model / paper                           | Điểm mới đáng chú ý                                                                                                                                                                         | Code/model                                                                                           |
| ------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| 2024    | **RT-DETRv2**                           | Bag-of-freebies, sampling đa scale tốt hơn, tối ưu training/deployment cho DETR real-time. ([arXiv.org][1])                                                                                 | [RT-DETR GitHub](https://github.com/lyuwenyu/RT-DETR?utm_source=chatgpt.com)                         |
| 2024    | **YOLO-World – CVPR 2024**              | Đưa YOLO sang **real-time open-vocabulary detection** bằng vision-language pretraining; có YOLO-World-Seg. ([Open Access CVF][2])                                                           | [YOLO-World GitHub](https://github.com/AILab-CVC/YOLO-World?utm_source=chatgpt.com)                  |
| 2024    | **Grounding DINO 1.5**                  | Scale data grounding lên >20M ảnh; bản Pro cho accuracy, Edge cho real-time. Paper báo 55.7 AP zero-shot LVIS-minival cho Pro. ([arXiv.org][3])                                             | [Grounding DINO 1.5](https://github.com/IDEA-Research/Grounding-DINO-1.5-API?utm_source=chatgpt.com) |
| 2024    | **T-Rex2**                              | Kết hợp **text prompt + visual exemplar** cho generic/open-set detection. ([arXiv.org][4])                                                                                                  | [T-Rex project/API](https://github.com/IDEA-Research/T-Rex?utm_source=chatgpt.com)                   |
| 2024    | **SAM 2 / SAM 2.1**                     | Unified image/video promptable segmentation với streaming memory; paper báo nhanh hơn SAM khoảng 6× trên image segmentation. ([AI Meta][5])                                                 | [SAM 2 GitHub](https://github.com/facebookresearch/sam2?utm_source=chatgpt.com)                      |
| 2024–25 | **LW-DETR**                             | ViT encoder nhẹ + shallow DETR decoder; minh họa rằng transformer có thể thay YOLO trong regime real-time. ([GitHub][6])                                                                    | [LW-DETR GitHub](https://github.com/Atten4Vis/LW-DETR?utm_source=chatgpt.com)                        |
| 2025    | **RT-DETRv3 – WACV**                    | Giải quyết điểm yếu lớn của Hungarian O2O: **sparse supervision**, thêm dense positive supervision nhưng chỉ khi training. ([Open Access CVF][7])                                           | [RT-DETRv3 GitHub](https://github.com/clxia12/RT-DETRv3?utm_source=chatgpt.com)                      |
| 2025    | **D-FINE – ICLR Spotlight**             | Chuyển bbox regression thành **Fine-grained Distribution Refinement**, kèm self-distillation cho localization. ([GitHub][8])                                                                | [D-FINE GitHub](https://github.com/Peterande/D-FINE?utm_source=chatgpt.com)                          |
| 2025    | **DEIM – CVPR**                         | Dense O2O matching + Matchability-Aware Loss; giảm vấn đề convergence của DETR, paper báo giảm ~50% thời gian training trong các thí nghiệm. ([Open Access CVF][9])                         | [DEIM GitHub](https://github.com/Intellindust-AI-Lab/DEIM?utm_source=chatgpt.com)                    |
| 2025    | **YOLOv12 – NeurIPS**                   | YOLO **attention-centric**, cố đưa attention vào real-time detector mà không mất quá nhiều latency. YOLOv12-N báo 40.6 AP / 1.64 ms T4. ([arXiv.org][10])                                   | [YOLOv12 GitHub](https://github.com/sunsmarterjie/yolov12?utm_source=chatgpt.com)                    |
| 2025    | **YOLOv13**                             | Hypergraph Adaptive Correlation Enhancement để mô hình hóa tương quan multi-to-multi thay vì chỉ local/pairwise attention. ([arXiv.org][11])                                                | [YOLOv13 GitHub](https://github.com/iMoonLab/yolov13?utm_source=chatgpt.com)                         |
| 2025    | **YOLOE – ICCV**                        | Một model cho **text prompt + visual prompt + prompt-free**, đồng thời detection và segmentation. ([Open Access CVF][12])                                                                   | [YOLOE GitHub](https://github.com/THU-MIG/yoloe?utm_source=chatgpt.com)                              |
| 2025    | **DINOv3**                              | Self-supervised VFM tới 7B params/1.7B images; dense representation rất mạnh cho detection/segmentation, ngay cả frozen backbone. ([AI Meta][13])                                           | [DINOv3 GitHub](https://github.com/facebookresearch/dinov3?utm_source=chatgpt.com)                   |
| 2025    | **DEIMv2**                              | Ghép DEIM với **DINOv3 features**, STA adapter và model từ X xuống Atto/Pico cho edge/mobile. Paper báo DEIMv2-X 57.8 COCO AP, S 50.9 AP với <10M params. ([arXiv.org][14])                 | [DEIMv2 GitHub](https://github.com/Intellindust-AI-Lab/DEIMv2?utm_source=chatgpt.com)                |
| 2025    | **RF-DETR**                             | DINOv2 + LW-DETR + **Neural Architecture Search** để tìm Pareto accuracy/latency; paper báo 2XL vượt 60 COCO AP. ([arXiv.org][15])                                                          | [RF-DETR GitHub](https://github.com/roboflow/rf-detr?utm_source=chatgpt.com)                         |
| 2025    | **RF-DETR-Seg**                         | Mang cùng kiến trúc RF-DETR sang real-time instance segmentation; có Nano→2XL. ([GitHub][16])                                                                                               | cùng repo RF-DETR                                                                                    |
| 2025    | **SAM 3**                               | Bước chuyển lớn: **concept-prompted detection + segmentation + tracking** bằng text hoặc visual exemplar, model unified. ([AI Meta][17])                                                    | model/code được Meta công bố cùng SAM 3                                                              |
| 2025    | **MambaVision – CVPR**                  | Hybrid Mamba + Transformer làm backbone cho detection/instance/semantic segmentation; hướng alternative backbone đáng chú ý. ([Open Access CVF][18])                                        | [MambaVision GitHub](https://github.com/NVlabs/MambaVision?utm_source=chatgpt.com)                   |
| 2025    | **CAVIS – ICCV**                        | Video instance segmentation khai thác context quanh instance + cross-frame contrastive representation. ([Open Access CVF][19])                                                              | paper/CVF                                                                                            |
| 2025    | **Temporal-aware Query Routing – ICCV** | Skip transformer decoder layer tùy mức thay đổi giữa frame; tăng MinVIS 24.7→34.6 FPS trong thí nghiệm paper. ([Open Access CVF][20])                                                       | paper/CVF                                                                                            |
| 2026    | **YOLO26**                              | YOLO chính thức chuyển mạnh sang **native end-to-end/NMS-free**, bỏ DFL, Progressive Loss + STAL; unified detection/instance segmentation/semantic/depth/pose/OBB. ([Ultralytics Docs][21]) | [Ultralytics GitHub](https://github.com/ultralytics/ultralytics?utm_source=chatgpt.com)              |
| 2026    | **RT-DETRv4 – ECCV 2026**               | Distill semantic knowledge từ VFM bằng Deep Semantic Injector + Gradient-guided Adaptive Modulation mà **không tăng inference cost**. ([arXiv.org][22])                                     | [RT-DETRv4 GitHub](https://github.com/RT-DETRs/RT-DETRv4?utm_source=chatgpt.com)                     |

---

# Các hướng phát triển SOTA quan trọng nhất

### 1. End-to-end, NMS-free đang trở thành mặc định

Đây có lẽ là thay đổi kiến trúc quan trọng nhất.

DETR vốn đã giải detection như **set prediction + Hungarian matching**, vì vậy không cần NMS. Điểm yếu trước đây là convergence và latency. RT-DETR cùng các hậu duệ đã giải quyết dần latency; còn YOLO26 hiện cũng cung cấp **one-to-one NMS-free head**. ([Ultralytics Docs][21])

Nghĩa là ranh giới truyền thống:

`YOLO = dense + NMS`
`DETR = sparse queries + bipartite matching`

đang mờ đi.

Hướng nghiên cứu kế tiếp rất có khả năng là kiến trúc hybrid dùng **dense supervision khi training nhưng sparse/end-to-end predictions khi inference**. RT-DETRv3 và DEIM là minh chứng mạnh cho hướng này. ([Open Access CVF][7])

---

## 2. Bài toán lớn không còn là architecture, mà là **assignment / supervision**

Một insight rất quan trọng từ 2024–2025 là Hungarian matching O2O của DETR quá sparse.

RT-DETRv3 thêm hierarchical dense positive supervision. DEIM tạo **Dense O2O** và Matchability-Aware Loss. YOLO26 sử dụng Progressive Loss và Small-Target-Aware Label Assignment. ([Open Access CVF][7])

Đây là một hướng nghiên cứu rất tiềm năng:

**train dense → infer sparse.**

Tức là cho mạng rất nhiều positive signal khi học, nhưng giữ pipeline inference đơn giản, end-to-end và NMS-free.

---

## 3. Localization/bbox regression đang được thiết kế lại

D-FINE là paper đặc biệt đáng đọc nếu bạn nghiên cứu detection.

Thay vì xem `(x,y,w,h)` như regression scalar thuần túy, D-FINE biểu diễn localization dưới dạng **fine-grained distribution refinement**, sau đó thêm Global Optimal Localization Self-Distillation. Nó cải thiện localization mà không thêm inference cost đáng kể. ([GitHub][8])

Điều này gợi ý một hướng rộng hơn:

**classification đã dùng distribution/soft target từ lâu; localization cũng đang chuyển sang structured/distributional prediction.**

---

# 4. Vision Foundation Model trở thành backbone/teacher

Đây có thể là hướng SOTA quan trọng nhất của 2025–2026.

DINOv3 scale self-supervised learning tới **1.7B images và model 7B parameters**, tập trung đặc biệt vào chất lượng dense feature. Meta báo cáo frozen DINOv3 backbone đạt kết quả rất mạnh trên dense prediction như detection và segmentation. ([AI Meta][13])

Nhưng deploy DINOv3-7B trực tiếp vào detector là không thực tế.

Vì thế có hai nhánh:

**DEIMv2:** lấy representation của DINOv3 trực tiếp thông qua backbone/distillation + Spatial Tuning Adapter. ([arXiv.org][14])

**RT-DETRv4:** dùng VFM làm teacher, inject semantic representation trong training rồi bỏ teacher khi deploy; nhờ vậy inference detector không đắt hơn. ([arXiv.org][22])

Đây là pattern cực kỳ đáng chú ý:

**Foundation model lớn khi training → specialist model nhỏ khi inference.**

---

# 5. NAS đang quay lại, nhưng lần này để tìm Pareto cho từng dataset/hardware

RF-DETR là ví dụ rõ nhất.

Thay vì cố định một kiến trúc Nano/S/M/L/X, RF-DETR dùng **weight-sharing NAS** để khám phá accuracy-latency Pareto curve. Paper nhấn mạnh việc adaptation sang dataset thực tế thay vì chỉ benchmark COCO. ([arXiv.org][15])

Điều này đặc biệt quan trọng cho industrial CV.

Model tốt nhất cho:

* camera CCTV 1080p,
* Jetson Orin,
* server T4,
* camera 4K small-object,
* microscopy,

không nhất thiết cùng một kiến trúc.

NAS + pretrained VFM + short fine-tuning có thể trở thành pipeline rất phổ biến.

---

# 6. Open-vocabulary detection đang trở thành **generic object perception**

Progression khá rõ:

**Grounding DINO / YOLO-World**
→ text → bounding box

**T-Rex2**
→ text + exemplar → bounding box

**YOLOE**
→ text + visual prompt + prompt-free → box + segmentation

**SAM 3**
→ concept → tất cả instance → mask + identity + tracking.

YOLOE được thiết kế để giữ hiệu suất real-time trong open scenario và có ba mode prompt khác nhau trong cùng framework. ([arXiv.org][23])

SAM 3 đi xa hơn: Promptable Concept Segmentation nhận noun phrase hoặc image exemplar rồi trả về **mask và unique identity cho tất cả instance matching concept**, trên cả image lẫn video. ([AI Meta][17])

Đây là thay đổi rất lớn về formulation:

`class_id ∈ {0,...,79}`

đang chuyển thành:

`concept = embedding(text / image / exemplar)`.

---

# 7. Instance segmentation không còn là một nhánh riêng

Mask R-CNN/Mask2Former vẫn rất quan trọng về mặt nền tảng, nhưng xu hướng mới không còn coi instance segmentation là một pipeline hoàn toàn khác detection.

RF-DETR có chung family cho detection và instance segmentation. YOLO26 cũng chung backbone/framework cho detection và segmentation. YOLOE unified open detection + segmentation. SAM 3 unified detection + segmentation + tracking. ([GitHub][16])

Về real-time COCO segmentation, benchmark hiện tại của RF-DETR báo từ **40.3 mask AP / 3.4 ms** cho Seg-N tới **49.9 AP / 21.8 ms** cho Seg-2XL trên T4 TensorRT FP16. Trên cùng benchmark nội bộ đó, YOLO26-X-Seg đạt 46.8 AP / 12.92 ms. Đây là số của Roboflow và nên hiểu là một benchmark cùng protocol do họ chạy, không phải một leaderboard độc lập. ([RoboFlow][24])

---

# 8. Image → video: memory và temporal reuse

SAM 2 cho thấy một kiến trúc segmentation có **streaming memory** có thể xử lý cả image và video. ([AI Meta][25])

Ở video instance segmentation, nghiên cứu mới còn khai thác một observation đơn giản nhưng mạnh:

> hai frame liên tiếp thường rất giống nhau, vậy tại sao phải chạy toàn bộ decoder mỗi frame?

Temporal-aware Query Routing từ ICCV 2025 học cách skip decoder layer dựa trên temporal difference; paper báo vừa tăng FPS vừa giữ/cải thiện AP trên các baseline VIS. ([Open Access CVF][20])

Vì vậy real-time video perception nhiều khả năng sẽ dùng:

`state/memory + cached feature + dynamic computation`

thay vì chạy image detector độc lập 30–60 lần mỗi giây.

---

# 9. Edge/mobile đang trở thành first-class objective

DEIMv2 có model từ X xuống Nano/Pico/Femto/Atto; paper báo Pico chỉ khoảng **1.5M parameters** mà đạt 38.5 COCO AP. ([arXiv.org][14])

Grounding DINO 1.5 cũng tách Pro và Edge; paper báo Edge đạt khoảng 75 FPS TensorRT trong thiết lập của họ. ([arXiv.org][3])

YOLO26 đồng thời tối ưu CPU/ONNX và TensorRT; Ultralytics báo YOLO26n 40.9 AP với khoảng 1.7 ms T4 TensorRT trong benchmark của họ. ([Ultralytics Docs][21])

Tức SOTA không còn chỉ là “AP cao nhất” mà ngày càng là **Pareto AP–latency–memory–power**.

---

# 10. Small objects vẫn là bài toán chưa giải xong

Dù detector tổng thể tăng AP rất nhanh, small-object vẫn là điểm yếu rõ ràng trong aerial imagery, surveillance và high-resolution industrial inspection.

Một dấu hiệu đáng chú ý là YOLO26 thêm **STAL – Small-Target-Aware Label Assignment** và cung cấp P2 architecture variant cho small-object scenarios. ([Ultralytics Docs][21])

Đây là vùng vẫn còn nhiều chỗ cho research: high-resolution feature, adaptive tiling, feature pyramid, query initialization, label assignment và super-resolution/detection joint learning.

---

# Snapshot về closed-set real-time detection hiện nay

Không nên coi bảng này là ranking tuyệt đối vì protocol khác nhau, nhưng nó cho thấy mặt bằng 2025–2026.

| Model          | COCO box AP được báo cáo | Điểm đáng chú ý                                                               |
| -------------- | -----------------------: | ----------------------------------------------------------------------------- |
| RF-DETR-2XL    |                     60.1 | T4 17.2 ms trong benchmark Roboflow; model NAS lớn. ([RoboFlow][24])          |
| DEIMv2-X       |                     57.8 | 50.3M params; dùng DINOv3. ([arXiv.org][14])                                  |
| YOLO26-X       |                     57.5 | Ultralytics báo 11.8 ms T4 TensorRT. ([Ultralytics Docs][21])                 |
| RT-DETRv4-X    |                     57.0 | 78 FPS T4; VFM distillation, không thêm inference overhead. ([arXiv.org][22]) |
| DEIM-D-FINE-X  |               ≈56.4–56.5 | CVPR paper báo 78 FPS T4. ([Open Access CVF][9])                              |
| RT-DETRv3-R101 |                     54.6 | Dense supervision trong training. ([Open Access CVF][7])                      |

Điều đáng chú ý không phải model nào hơn nhau 0.5 AP, mà là **real-time detectors đã tiến vào vùng ~57–60 AP COCO**, trong khi model nhỏ cũng tiến rất nhanh.

---

# Nếu muốn nghiên cứu để tạo một model mới

Từ landscape hiện tại, mình thấy các research direction có nhiều “room” nhất là:

1. **DETR + dense training / sparse inference**: phát triển matching/assignment tốt hơn DEIM và RT-DETRv3.
2. **VFM → tiny detector distillation**: DINOv3/SAM3 teacher nhưng deploy model 1–10M params.
3. **Open-vocabulary + real-time segmentation**: kết hợp efficiency kiểu YOLOE với semantic quality kiểu SAM 3/Grounding DINO.
4. **Domain-adaptive detection**: VFM + NAS/adapters cho industrial, medical, aerial, agriculture thay vì tiếp tục squeeze COCO.
5. **Temporal detector/segmenter**: cache/memory/query routing để video inference không xử lý từng frame độc lập.
6. **Unified box-mask-track model** với cùng query representation.
7. **Visual prompting/few-shot detection**: “đưa một ví dụ vật thể → tìm tất cả vật tương tự” thay vì phải đặt tên class.
8. **Data engine + automatic annotation**: foundation model tự tạo box/mask/pseudo-label rồi specialist detector học từ dữ liệu đó.
9. **Small-object/high-resolution efficient detection**: vẫn rất có giá trị thực tế.
10. **Hardware-aware architecture search / quantization**: model được tối ưu trực tiếp cho TensorRT, NPU, Jetson, RKNN, CoreML thay vì FLOPs lý thuyết.

Trong số này, nếu mục tiêu là **paper research mới trong 2026–2027**, giao điểm hấp dẫn nhất theo landscape hiện tại là:

**DINOv3/SAM3-level representation → distillation → end-to-end DETR → unified box/mask → temporal memory → edge deployment.**

Nói cách khác, thay vì tạo thêm một “YOLOvN+1”, hướng mạnh hơn về mặt nghiên cứu là tạo một **specialist perception model nhỏ học từ foundation model lớn**, có thể detect/segment/track và thích nghi nhanh với domain mới.

### Bộ repo mình khuyên clone để làm research base

Nếu chỉ chọn một bộ codebase để bắt đầu, mình sẽ giữ: **RT-DETR/DEIM/D-FINE/DEIMv2** cho nghiên cứu DETR; **RF-DETR** cho fine-tuning/NAS/detection+segmentation; **YOLOE/YOLO-World** cho open-vocabulary real-time; **Grounding DINO** cho grounding mạnh; **SAM2/SAM3** cho promptable segmentation/video; và **DINOv3** để nghiên cứu backbone/distillation. Các repo này bao phủ gần như toàn bộ các trục SOTA hiện tại. ([GitHub][26])

Nếu bạn đang định **làm luận văn/paper**, mình có thể làm tiếp một bước hữu ích hơn: dựng cho bạn một **research map 2024–2026 khoảng 50–100 paper**, chia taxonomy `closed-set / open-vocab / DETR / YOLO / instance seg / video / VFM / small-object / edge`, kèm **paper link + GitHub + checkpoint + dataset + AP + params + FLOPs + FPS + ý tưởng chính + điểm yếu còn mở**, rồi từ đó chỉ ra khoảng **5–10 research gap cụ thể có khả năng phát triển thành đề tài mới**.

[1]: https://arxiv.org/abs/2407.17140?utm_source=chatgpt.com "RT-DETRv2: Improved Baseline with Bag-of-Freebies for Real-Time Detection Transformer"
[2]: https://openaccess.thecvf.com/content/CVPR2024/html/Cheng_YOLO-World_Real-Time_Open-Vocabulary_Object_Detection_CVPR_2024_paper.html?utm_source=chatgpt.com "CVPR 2024 Open Access Repository"
[3]: https://arxiv.org/abs/2405.10300?utm_source=chatgpt.com "Grounding DINO 1.5: Advance the \"Edge\" of Open-Set Object Detection"
[4]: https://arxiv.org/abs/2403.14610?utm_source=chatgpt.com "T-Rex2: Towards Generic Object Detection via Text-Visual Prompt Synergy"
[5]: https://ai.meta.com/research/publications/sam-2-segment-anything-in-images-and-videos/?utm_source=chatgpt.com "SAM 2: Segment Anything in Images and Videos | Research - AI at Meta"
[6]: https://github.com/Atten4Vis/LW-DETR?utm_source=chatgpt.com "GitHub - Atten4Vis/LW-DETR: This repository is an official implementation of the paper \"LW-DETR: A Transformer Replacement to YOLO for Real-Time Detection\". · GitHub"
[7]: https://openaccess.thecvf.com/content/WACV2025/html/Wang_RT-DETRv3_Real-Time_End-to-End_Object_Detection_with_Hierarchical_Dense_Positive_Supervision_WACV_2025_paper.html?utm_source=chatgpt.com "WACV 2025 Open Access Repository"
[8]: https://github.com/Peterande/D-FINE?utm_source=chatgpt.com "GitHub - Peterande/D-FINE: D-FINE: Redefine Regression Task of DETRs as Fine-grained Distribution Refinement [ICLR 2025 Spotlight] · GitHub"
[9]: https://openaccess.thecvf.com/content/CVPR2025/html/Huang_DEIM_DETR_with_Improved_Matching_for_Fast_Convergence_CVPR_2025_paper.html?utm_source=chatgpt.com "CVPR 2025 Open Access Repository"
[10]: https://arxiv.org/abs/2502.12524?utm_source=chatgpt.com "YOLOv12: Attention-Centric Real-Time Object Detectors"
[11]: https://arxiv.org/abs/2506.17733?utm_source=chatgpt.com "YOLOv13: Real-Time Object Detection with Hypergraph-Enhanced Adaptive Visual Perception"
[12]: https://openaccess.thecvf.com/content/ICCV2025/html/Wang_YOLOE_Real-Time_Seeing_Anything_ICCV_2025_paper.html?utm_source=chatgpt.com "ICCV 2025 Open Access Repository"
[13]: https://ai.meta.com/blog/dinov3-self-supervised-vision-model/?utm_source=chatgpt.com "DINOv3: Self-supervised learning for vision at unprecedented scale"
[14]: https://arxiv.org/abs/2509.20787?utm_source=chatgpt.com "Real-Time Object Detection Meets DINOv3"
[15]: https://arxiv.org/abs/2511.09554?utm_source=chatgpt.com "RF-DETR: Neural Architecture Search for Real-Time Detection Transformers"
[16]: https://github.com/roboflow/rf-detr "GitHub - roboflow/rf-detr: RF-DETR is a real-time object detection and segmentation model architecture developed by Roboflow, SOTA on COCO, designed for fine-tuning. [ICLR 2026] · GitHub"
[17]: https://ai.meta.com/research/publications/sam-3-segment-anything-with-concepts/?utm_source=chatgpt.com "SAM 3: Segment Anything with Concepts | Research - AI at Meta"
[18]: https://openaccess.thecvf.com/content/CVPR2025/html/Hatamizadeh_MambaVision_A_Hybrid_Mamba-Transformer_Vision_Backbone_CVPR_2025_paper.html?utm_source=chatgpt.com "CVPR 2025 Open Access Repository"
[19]: https://openaccess.thecvf.com/content/ICCV2025/html/Lee_CAVIS_Context-Aware_Video_Instance_Segmentation_ICCV_2025_paper.html?utm_source=chatgpt.com "ICCV 2025 Open Access Repository"
[20]: https://openaccess.thecvf.com/content/ICCV2025/html/Cheng_Temporal-aware_Query_Routing_for_Real-time_Video_Instance_Segmentation_ICCV_2025_paper.html?utm_source=chatgpt.com "ICCV 2025 Open Access Repository"
[21]: https://docs.ultralytics.com/models/yolo26?utm_source=chatgpt.com "Ultralytics YOLO26"
[22]: https://arxiv.org/abs/2510.25257?utm_source=chatgpt.com "RT-DETRv4: Painlessly Furthering Real-Time Object Detection with Vision Foundation Models"
[23]: https://arxiv.org/abs/2503.07465?utm_source=chatgpt.com "YOLOE: Real-Time Seeing Anything"
[24]: https://rfdetr.roboflow.com/latest/learn/benchmarks/?utm_source=chatgpt.com "Benchmarks - RF-DETR"
[25]: https://ai.meta.com/research/sam2/?utm_source=chatgpt.com "Meta Segment Anything Model 2"
[26]: https://github.com/RT-DETRs?utm_source=chatgpt.com "RT-DETRs · GitHub"
