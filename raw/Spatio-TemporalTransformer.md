Đây là phần quan trọng nhất khi thiết kế **Spatio-Temporal Transformer**.

Nhiều người nghĩ input là video:

```
frame1
frame2
...
frame64
```

Nhưng trong kiến trúc:

```
Detector
↓
Tracker
↓
Spatio-Temporal Transformer
```

thì Transformer thường **không nhận ảnh** nữa.

Nó nhận:

```
Object Tokens
```

được tạo từ detector + tracker.

---

# 1. Một object token là gì?

Ví dụ frame:

```
Frame 100

Car A
Car B
Motorbike C
Person D
```

Sau tracker:

```python
track_id=11
track_id=12
track_id=13
track_id=14
```

---

Mỗi object được biến thành feature vector:

```python
object_feature =
[
   ...
]
```

---

Đó chính là:

```
Object Token
```

---

# 2. Feature thường gồm những gì?

## A. Geometry Feature

Từ bbox:

```python
x_center
y_center
width
height
```

---

Ví dụ:

```python
[
 0.52,
 0.33,
 0.10,
 0.08
]
```

(normalized)

---

## B. Motion Feature

Từ tracker:

```python
vx
vy
speed
acceleration
heading
```

---

Ví dụ:

```python
[
 3.2,
 -0.8,
 3.3,
 0.4,
 42.0
]
```

---

Đặc biệt quan trọng với:

```
accident
near miss
fight
```

---

## C. Object Class

Ví dụ:

```python
car
truck
motorbike
person
```

---

Embedding:

```python
car       -> [....]
person    -> [....]
truck     -> [....]
```

giống NLP.

---

## D. Appearance Feature

Đây là feature mạnh nhất.

---

Crop object:

```
Car A
```

↓

CNN / ViT / ReID

↓

```python
256-d
512-d
768-d
```

vector.

---

Ví dụ:

```python
appearance =
[
 0.12,
 0.88,
 ...
]
```

---

Đây là phần giúp model hiểu:

```
đối tượng trông như thế nào
```

---

# 3. Feature đầy đủ

Thường ghép:

```python
token =
[
 bbox,

 velocity,

 class_embedding,

 appearance_embedding
]
```

---

Ví dụ:

```python
4
+
5
+
32
+
512

=
553 dimension
```

---

Sau đó:

```python
Linear(553 -> 256)
```

---

Thành:

```python
d_model = 256
```

---

# 4. Input tensor như thế nào?

Giả sử:

```
64 frame
```

---

Mỗi frame:

```
20 object
```

---

Mỗi object:

```
256-d feature
```

---

Tensor:

```python
x.shape

=
(T,N,F)

=
(64,20,256)
```

---

Batch:

```python
(B,T,N,F)
```

Ví dụ:

```python
(8,64,20,256)
```

---

# 5. Transformer nhìn gì?

Ví dụ:

```
Frame1
```

---

Objects:

```
CarA
CarB
PersonC
```

---

Frame2:

```
CarA
CarB
PersonC
```

---

Object token:

```
CarA@Frame1
CarA@Frame2
CarA@Frame3
```

---

Transformer học:

```
Temporal relation
```

---

Đồng thời:

```
CarA
↕
CarB
```

---

Học:

```
Spatial relation
```

---

# 6. Có 2 cách xây token

## Cách 1

Flatten

```python
(T,N,F)

↓

(T*N,F)
```

---

Ví dụ:

```
CarA_F1
CarB_F1
CarA_F2
CarB_F2
...
```

---

Attention:

```
mọi object
nhìn mọi object
```

---

Đắt.

---

# Cách 2

Factorized Attention

Giống TimeSformer.

---

Bước 1:

```
Object Attention
```

Trong frame.

---

Ví dụ:

```
CarA
↕
CarB
↕
PersonC
```

---

Bước 2:

```
Temporal Attention
```

---

Ví dụ:

```
CarA_F1
↕
CarA_F2
↕
CarA_F3
```

---

Rẻ hơn nhiều.

---

# 7. Với bài toán Accident Detection

Token:

```python
[
 bbox,
 speed,
 heading,
 class_embedding,
 appearance_embedding
]
```

---

Shape:

```python
(T,N,F)
```

Ví dụ:

```python
(64,20,256)
```

---

Transformer học:

```
CarA
↕
CarB
```

---

theo thời gian:

```
distance

20m
↓
10m
↓
2m
↓
0m
```

---

và:

```
speed change
direction change
```

---

Từ đó suy ra:

```
Accident
```

---

# Với hệ thống giao thông của bạn

Nếu làm production:

Feature nên gồm:

```python
bbox_xywh           # 4
velocity            # 2
speed               # 1
heading             # 1
object_class_emb    # 16~32
appearance_emb      # 128~256
```

---

Tổng:

```python
~150-300 chiều
```

---

Input:

```python
(B,T,N,F)

=
(8,64,20,256)
```

đủ để xây một **Spatio-Temporal Transformer cho accident / near-miss / interaction detection** mà không cần đưa ảnh hoặc patch video trực tiếp vào Transformer. Đây cũng là cách nhẹ hơn VideoMAE/TimeSformer hàng chục lần nhưng vẫn giữ được thông tin quan hệ giữa các đối tượng.

# **Có nên đưa trực tiếp tracking_id vào model như một feature học được?**

Đây là một câu hỏi rất quan trọng khi thiết kế **Spatio-Temporal Transformer**.

Câu trả lời ngắn:

> **Thông thường KHÔNG đưa trực tiếp tracking_id vào model như một feature học được.**
> 
> 
> Nhưng phải dùng tracking_id để **tổ chức dữ liệu đầu vào**, giúp model biết token nào thuộc cùng một object qua thời gian.
> 

---

# 1. Vì sao không nên đưa track_id vào feature?

Giả sử:

```
Car A -> track_id = 17
Car B -> track_id = 25
```

Nếu đưa:

```python
feature = [
   x,
   y,
   w,
   h,
   speed,
   track_id
]
```

thì:

```
17
25
31
88
```

chỉ là số ngẫu nhiên.

---

Frame khác:

```
Car A
```

có thể thành:

```
track_id = 105
```

---

Model sẽ học:

```
id=17
```

thay vì:

```
xe màu đỏ
đang chạy nhanh
```

---

Điều này rất nguy hiểm.

---

# 2. Tracking ID thực sự dùng để làm gì?

Tracking ID dùng để xây dựng:

```
Temporal Structure
```

---

Ví dụ tracker trả:

```python
frame1:

id=17
id=25
```

---

```python
frame2:

id=17
id=25
```

---

```python
frame3:

id=17
id=25
```

---

Ta biết:

```
id=17
```

chính là cùng một object.

---

Nên xây:

```python
track_17 = [
 frame1_feature,
 frame2_feature,
 frame3_feature
]
```

---

Lúc này Transformer nhìn:

```
track 17
```

theo thời gian.

---

Không cần biết:

```
17
```

là số bao nhiêu.

---

# 3. Với Temporal Transformer

Ví dụ:

```
1 object
```

---

Input:

```python
(T,F)
```

---

Tracker dùng để tạo sequence:

```python
frame1 person
frame2 person
frame3 person
```

---

Nhưng:

```
track_id
```

không xuất hiện trong feature.

---

# 4. Với Spatio-Temporal Transformer

Đây là trường hợp thú vị hơn.

---

Giả sử:

```
Frame1

CarA
CarB
```

---

Frame2

```
CarA
CarB
```

---

Tensor:

```python
(T,N,F)
```

Ví dụ:

```python
(64,20,256)
```

---

Làm sao model biết:

```
CarA ở frame1
```

và:

```
CarA ở frame2
```

là cùng xe?

---

Có 3 cách.

---

# Cách 1 (đơn giản nhất)

Sắp xếp object theo track.

Ví dụ:

```python
index 0 = track17
index 1 = track25
index 2 = track31
```

---

Frame nào cũng giữ nguyên:

```
slot 0 = track17
slot 1 = track25
```

---

Tensor:

```python
x[t,0,:]
```

luôn là:

```
track17
```

---

Transformer tự hiểu temporal.

---

Đây là cách phổ biến nhất.

---

# Cách 2 (Track Embedding)

Tạo embedding:

```python
track17 -> e1
track25 -> e2
```

---

Thêm:

```python
feature += track_embedding
```

---

Tuy nhiên:

```
không nên dùng ID thật
```

---

Mà dùng:

```
index trong clip
```

---

Ví dụ clip hiện tại:

```
object0
object1
object2
```

---

Giống:

```
position embedding
```

---

Một số paper về multi-object transformer làm vậy.

---

# Cách 3 (Identity Embedding từ Appearance)

Đây là cách hiện đại nhất.

---

Crop:

```
CarA
```

---

Qua ReID network:

```python
appearance_emb
```

---

Ví dụ:

```python
[0.12,0.91,...]
```

---

Frame tiếp:

```
CarA
```

---

Embedding:

```python
[0.11,0.89,...]
```

---

Gần nhau trong latent space.

---

Transformer tự biết:

```
đây là cùng object
```

---

Không cần track id.

---

# Với Accident Detection

Giả sử:

```
CarA
CarB
```

---

Feature:

```python
bbox
speed
heading
appearance
```

---

Shape:

```python
(T,N,F)
```

---

Nếu:

```python
appearance_emb
```

ổn định.

---

Transformer sẽ tự học:

```
CarA frame1
↕
CarA frame2
```

---

thông qua:

```
appearance similarity
+
position continuity
```

---

# Thực tế production

Thông thường:

```
track_id
```

chỉ dùng để:

```
xây track history
```

---

Không đưa vào feature.

---

Feature:

```python
[
 bbox,
 velocity,
 speed,
 heading,
 class_embedding,
 appearance_embedding
]
```

---

là đủ.

---

# Khuyến nghị cho bài toán của bạn

Nếu làm:

```
Detector
↓
Tracker
↓
Spatio-Temporal Transformer
```

thì:

### Dùng track_id để:

```
gom object theo thời gian
```

### Không đưa track_id thô vào model

```
17
25
31
```

### Thay bằng:

```
appearance embedding
+
bbox trajectory
+
motion feature
```

Model sẽ học identity tốt hơn nhiều và không bị phụ thuộc vào giá trị ID cụ thể do tracker sinh ra.

# Làm nhãn như thế nào?

Với **Spatio-Temporal Transformer trên object tokens**, nhãn tốt nhất không chỉ là “video có tai nạn/không”, mà nên có **nhãn theo object/track và theo event window**.

## 1. Mức nhãn tối thiểu

```
Video clip 5–10s
↓
label = accident / near_miss / normal / fight / crowd_panic ...
```

Dễ làm nhất, nhưng model khó học “ai tương tác với ai”.

Phù hợp nếu bạn dùng:

```
scene-level event classification
```

Không tối ưu cho Spatio-Temporal object tokens.

---

## 2. Mức nhãn khuyến nghị

Mỗi clip nên có:

```json
{
  "clip_id": "cam01_2026_06_24_10_00_00",
  "start_frame": 1200,
  "end_frame": 1350,
  "event_type": "accident",
  "event_start_frame": 1278,
  "event_end_frame": 1310,
  "participants": [
    {
      "track_id": 12,
      "role": "vehicle_a",
      "class": "car"
    },
    {
      "track_id": 27,
      "role": "vehicle_b",
      "class": "motorbike"
    }
  ],
  "severity": "medium"
}
```

Nhãn quan trọng nhất là:

```
event_type
event time
participant track_ids
```

Vì Spatio-Temporal Transformer cần học:

```
object A
↕
object B
↕
theo thời gian
```

---

## 3. Với bài toán accident / near-miss

Nên label như sau:

| Thành phần | Ví dụ |
| --- | --- |
| Clip label | accident / near_miss / normal |
| Event frame | frame bắt đầu va chạm |
| Participant tracks | xe A, xe B |
| Object class | car, motorbike, pedestrian |
| Optional | severity, direction, speed_change |

Ví dụ:

```json
{
  "event_type": "near_miss",
  "event_start_frame": 840,
  "event_end_frame": 900,
  "participants": [5, 9],
  "negative_tracks": [2, 3, 7, 11]
}
```

---

## 4. Với fight / violence

```json
{
  "event_type": "fight",
  "event_start_frame": 320,
  "event_end_frame": 470,
  "participants": [
    {"track_id": 3, "role": "aggressor"},
    {"track_id": 8, "role": "victim"}
  ]
}
```

Nếu khó phân biệt aggressor/victim thì chỉ cần:

```json
{
  "participants": [3, 8]
}
```

---

## 5. Với crowd behavior

Không cần track participant quá chi tiết nếu quá đông.

Có thể label theo vùng:

```json
{
  "event_type": "crowd_panic",
  "event_start_frame": 120,
  "event_end_frame": 300,
  "roi": [100, 200, 900, 700],
  "density_level": "high"
}
```

---

# Format dataset nên dùng

Một sample training nên là:

```
Input:
T frame × N object × F feature

Label:
event type
participant mask
event frame/window
```

Ví dụ tensor:

```python
x.shape = (T, N, F)
```

Label:

```python
y_event = accident
y_participants = [0, 1, 1, 0, 0]
```

Trong đó:

```
N = số object tối đa trong clip
1 = object tham gia event
0 = object không tham gia
```

---

# Mức annotation theo độ tốt

| Mức | Nhãn | Chất lượng |
| --- | --- | --- |
| Level 1 | clip label | dễ, yếu |
| Level 2 | clip label + event time | khá |
| Level 3 | + participant track_ids | tốt |
| Level 4 | + role/severity/ROI | rất tốt |

Với Spatio-Temporal Transformer, nên đạt ít nhất:

```
Level 3:
event_type + event_time + participant_track_ids
```

---

# Quy trình labeling thực tế

1. Chạy detector + tracker trước.
2. Xuất video kèm track_id overlay.
3. Annotator chọn event window.
4. Annotator chọn các track_id liên quan.
5. Lưu JSON.
6. Training model bằng object tokens từ các track đó.

---

# Tóm tắt

Nếu làm **Spatio-Temporal Transformer**, nhãn nên là:

```
Không chỉ:
"clip này có accident"

Mà nên là:
"accident xảy ra từ frame A đến frame B,
liên quan track_id 12 và track_id 27"
```

Đây là loại nhãn giúp model học được quan hệ **object-object theo thời gian**, đúng với bản chất của Spatio-Temporal Transformer.