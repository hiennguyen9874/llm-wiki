Dưới đây là bảng so sánh theo góc nhìn **Video Analytics / Traffic Analytics / Action Recognition** sau khi đã có Detector + Tracker.

| Phương pháp | Input | Học quan hệ thời gian | Song song hóa | Chi phí | Data cần | Explainability | Realtime |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rule Engine | Track history | Hard-code | N/A | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| LSTM | (T,F) | Tốt | ❌ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| GRU | (T,F) | Tốt | ❌ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| TCN | (T,F) | Tốt | ✅ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Transformer Encoder | (T,F) | Rất tốt | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Long Transformer (Informer, PatchTST) | (T,F) | Rất tốt | ✅ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Multi-object Transformer | (T,N,F) | Xuất sắc | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ |
| Video Transformer | Video | Xuất sắc | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ |
- Append
    - **Scene-level Temporal Transformer**: Dùng feature toàn frame thay vì từng track
        
        Frame feature từ CNN/ViT
        ↓
        Temporal Transformer
        ↓
        Scene event
        
    - **Spatio-Temporal Transformer trên object tokens**: Mỗi object trong mỗi frame là một token
        
        frame t:
        [obj1, obj2, obj3]
        
        nhiều frame:
        T × N tokens
        ↓
        Transformer
        

---

# 1. Rule Engine

Pipeline:

```
Detector
↓
Tracker
↓
Track History
↓
Rule
```

Ví dụ:

```python
if speed > 50 and
   crossed_stop_line and
   traffic_light == RED:
       violation = True
```

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Vượt đèn đỏ | ⭐⭐⭐⭐⭐ |
| Sai làn | ⭐⭐⭐⭐⭐ |
| Đi ngược chiều | ⭐⭐⭐⭐⭐ |
| Đếm xe | ⭐⭐⭐⭐⭐ |
| PPE | ⭐⭐⭐⭐⭐ |
| Tai nạn | ⭐⭐⭐ |
| Fight | ⭐ |

---

# 2. LSTM / GRU

Pipeline:

```
Track Feature Sequence
↓
LSTM
↓
Action
```

Input:

```python
(B,T,F)
```

Ví dụ:

```python
32 frame
x 20 feature
```

Ưu điểm:

- Dữ liệu ít vẫn train được
- Nhẹ
- Dễ deploy

Nhược điểm:

- Khó học dependency dài
- Không parallel

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Fall Detection | ⭐⭐⭐⭐ |
| Running / Walking | ⭐⭐⭐⭐ |
| Loitering | ⭐⭐⭐ |
| PPE Temporal | ⭐⭐⭐⭐ |
| Accident | ⭐⭐ |
| Fight | ⭐⭐ |

---

# 3. TCN (Temporal Convolution Network)

Pipeline:

```
Track Sequence
↓
1D Dilated Conv
↓
Classifier
```

Ví dụ:

```python
(B,T,F)
```

↓

```python
Conv1D
kernel=3
dilation=1
```

↓

```python
Conv1D
kernel=3
dilation=2
```

↓

```python
Conv1D
kernel=3
dilation=4
```

---

Ưu điểm:

- Realtime cực tốt
- GPU utilization tốt
- Dễ train hơn Transformer

Nhược điểm:

- Receptive field hữu hạn

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Fall Detection | ⭐⭐⭐⭐⭐ |
| Running | ⭐⭐⭐⭐⭐ |
| Loitering | ⭐⭐⭐⭐ |
| Abnormal Behavior | ⭐⭐⭐ |
| PPE Sequence | ⭐⭐⭐⭐ |
| Accident | ⭐⭐⭐ |

---

# 4. Temporal Transformer Encoder

Pipeline:

```
Track Feature
↓
Transformer Encoder
↓
CLS Token
↓
Classifier
```

Input:

```python
(B,T,F)
```

Ví dụ:

```
64 frame
```

Transformer có thể attention:

```
frame 5
↕
frame 50
```

ngay lập tức.

---

Ưu điểm:

- Học dependency dài
- Hành vi phức tạp

Nhược điểm:

- Cần nhiều dữ liệu hơn TCN/LSTM

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Fall Detection | ⭐⭐⭐⭐ |
| Loitering | ⭐⭐⭐⭐⭐ |
| Unsafe Behavior | ⭐⭐⭐⭐⭐ |
| Fight | ⭐⭐⭐⭐ |
| Crowd Behavior | ⭐⭐⭐⭐ |
| Accident | ⭐⭐⭐⭐ |

---

# 5. PatchTST / Informer

Đây là Transformer tối ưu cho chuỗi dài.

Ví dụ:

```
1000 frame
5000 frame
```

---

PatchTST:

```
16 frame
↓
1 patch token
```

Informer:

```
Sparse Attention
```

---

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Long Surveillance | ⭐⭐⭐⭐⭐ |
| Traffic Flow Forecast | ⭐⭐⭐⭐⭐ |
| Queue Prediction | ⭐⭐⭐⭐⭐ |
| Long-term Behavior | ⭐⭐⭐⭐ |

Không thực sự cần cho fall detection hay accident detection thông thường.

---

# 6. Multi-Object Transformer

Pipeline:

```
Track A
Track B
Track C
↓
Transformer
↓
Interaction Event
```

Input:

```python
(B,T,N,F)
```

Ví dụ:

```
T = 64 frame
N = 20 object
```

---

Transformer học:

```
Car A
↕
Car B

Pedestrian
↕
Car
```

---

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Accident Detection | ⭐⭐⭐⭐⭐ |
| Near Miss | ⭐⭐⭐⭐⭐ |
| Vehicle Interaction | ⭐⭐⭐⭐⭐ |
| Fight | ⭐⭐⭐⭐⭐ |
| Crowd Behavior | ⭐⭐⭐⭐⭐ |

---

# 7. Video Transformer

Ví dụ:

- TimeSformer
- Video Swin
- MViT
- VideoMAE

Pipeline:

```
Raw Video
↓
Patch Embedding
↓
Spatial Attention
↓
Temporal Attention
↓
Classifier
```

---

Input:

```
32 frame
224x224
```

---

Không cần:

```
Detector
Tracker
```

---

Nhưng:

```
100 camera
T4
```

thì gần như không khả thi.

---

Phù hợp:

| Bài toán | Phù hợp |
| --- | --- |
| Action Recognition Dataset | ⭐⭐⭐⭐⭐ |
| Sports Analytics | ⭐⭐⭐⭐⭐ |
| Violence Detection | ⭐⭐⭐⭐⭐ |
| Research | ⭐⭐⭐⭐⭐ |
| Production Traffic | ⭐ |

---

# Bài toán của bạn nên dùng gì?

```jsx
Vượt đèn đỏ, line crossing, wrong lane:
Detector + Tracker + Rule

Fall, loitering, running:
Detector + Tracker + TCN hoặc Temporal Transformer

Accident, fight, near-miss:
Detector + Tracker + Multi-object Transformer + Rule verification

Scene violence / crowd panic:
Frame feature + Temporal Transformer hoặc Video Swin/MViT
```

## Helmet / PPE

```
Detector
↓
Rule
```

Đủ.

---

## Red Light Violation

```
Detector
↓
Tracker
↓
Rule
```

Tốt nhất.

---

## Wrong Lane

```
Detector
↓
Tracker
↓
Rule
```

Tốt nhất.

---

## Fall Detection

```
Detector
↓
Tracker
↓
TCN
```

hoặc

```
Detector
↓
Tracker
↓
Temporal Transformer
```

---

## Accident Detection

```
Detector
↓
Tracker
↓
Rule
```

MVP tốt nhất.

---

Nếu muốn nâng cấp:

```
Detector
↓
Tracker
↓
Multi-Object Transformer
↓
Accident
```

---

## Crowd / Fight / Abnormal Behavior

```
Detector
↓
Tracker
↓
Temporal Transformer
```

hoặc

```
Detector
↓
Tracker
↓
Multi-Object Transformer
```

---

# Xếp hạng production camera thực tế

| Phương pháp | Độ khuyến nghị |
| --- | --- |
| Detector + Rule | ⭐⭐⭐⭐⭐ |
| Detector + Tracker + Rule | ⭐⭐⭐⭐⭐ |
| Detector + Tracker + TCN | ⭐⭐⭐⭐⭐ |
| Detector + Tracker + Temporal Transformer | ⭐⭐⭐⭐ |
| Detector + Tracker + Multi-Object Transformer | ⭐⭐⭐ |
| Full Video Transformer | ⭐ |

Nếu mục tiêu là hệ thống **DeepStream + nhiều camera + T4/A100 + realtime**, thì đa số use case thực tế sẽ dừng ở:

```
YOLO/RT-DETR
↓
OC-SORT/DeepOC-SORT
↓
Track History
↓
Rule hoặc TCN
```

vì đây là điểm tối ưu nhất giữa độ chính xác, chi phí GPU, độ trễ và khả năng giải thích kết quả.