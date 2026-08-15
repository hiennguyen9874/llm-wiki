Đây là 3 kiến trúc rất khác nhau về **mức độ trừu tượng của dữ liệu đầu vào**.

---

# Kiến trúc tổng quan

## 1. Detector + Tracker + Temporal Transformer

```
Frame
↓
Detector
↓
Tracker
↓
Track History

Track #1:
[t1,t2,t3...]

Track #2:
[t1,t2,t3...]

↓
Temporal Transformer

↓
Action
```

Transformer chỉ nhìn:

```
1 object
```

tại một thời điểm.

---

## 2. Scene-level Temporal Transformer

```
Frame
↓
CNN / ViT
↓
Frame Feature

frame1
frame2
frame3

↓
Temporal Transformer

↓
Scene Event
```

Không biết object nào là ai.

---

## 3. Spatio-Temporal Transformer on Object Tokens

```
Frame
↓
Detector
↓
Tracker

Object Tokens

car1
car2
person1
person2

↓

Spatio-Temporal Transformer

↓

Interaction Event
```

Transformer nhìn:

```
Object
+
Time
```

cùng lúc.

---

# So sánh trực quan

## Temporal Transformer

Input:

```python
[
 frame1_person_feature,
 frame2_person_feature,
 frame3_person_feature
]
```

---

Ví dụ:

```
Người đứng

↓

Người cúi

↓

Người nằm
```

---

Transformer học:

```
Fall Down
```

---

Nhưng:

```
Không biết
có xe nào bên cạnh hay không
```

---

# Scene-level Transformer

Input:

```python
[
 frame1_feature,
 frame2_feature,
 frame3_feature
]
```

---

Ví dụ:

```
Frame1:
xe + người

Frame2:
xe + người

Frame3:
xe + người
```

---

Transformer nhìn:

```
Toàn bộ scene
```

---

Không cần detector.

---

Nhưng:

```
Không biết object A
và object B
```

---

# Spatio-Temporal Transformer

Input:

```python
frame1:

car1
car2
person1

frame2:

car1
car2
person1
```

---

Transformer học:

```
car1
↔
person1

theo thời gian
```

---

Nó biết:

```
Ai đang tương tác với ai
```

---

# So sánh dữ liệu đầu vào

| Kiến trúc | Input |
| --- | --- |
| Temporal Transformer | (B,T,F) |
| Scene-level Transformer | (B,T,D) |
| Spatio-Temporal Transformer | (B,T,N,F) |

Trong đó:

```
T = frame

N = object

F = object feature

D = frame feature
```

---

# Thông tin mà model nhìn thấy

| Thông tin | Temporal | Scene | Spatio-Temporal |
| --- | --- | --- | --- |
| Object motion | ✅ | ⚠️ | ✅ |
| Object identity | ✅ | ❌ | ✅ |
| Object interaction | ❌ | ⚠️ | ✅ |
| Global scene | ❌ | ✅ | ⚠️ |
| Multi-agent reasoning | ❌ | ❌ | ✅ |

---

# Ví dụ Fall Detection

## Temporal Transformer

Track:

```
Person #17
```

---

Feature:

```
bbox
velocity
aspect ratio
```

---

Transformer:

```
đứng
↓
cúi
↓
ngã
```

---

Hoạt động rất tốt.

---

## Scene Transformer

Nhìn:

```
toàn bộ frame
```

---

Thấy:

```
người
xe
cây
```

---

Quá nhiều nhiễu.

---

Không tối ưu.

---

## Spatio-Temporal

Làm được.

Nhưng:

```
overkill
```

cho bài toán này.

---

# Ví dụ Accident Detection

## Temporal Transformer

Track A:

```
xe A
```

---

Track B:

```
xe B
```

---

Mỗi track độc lập.

---

Model không thấy:

```
A đâm B
```

---

Nên khó.

---

## Scene Transformer

Nhìn cả frame.

---

Có thể học:

```
tai nạn
```

---

Nhưng:

```
không biết
xe nào đâm xe nào
```

---

Khó giải thích.

---

## Spatio-Temporal

Transformer thấy:

```
Car A
↔
Car B
```

---

Theo thời gian:

```
20m
↓
10m
↓
2m
↓
0m
```

---

Rất phù hợp.

---

# Ví dụ Fight Detection

## Temporal Transformer

Nhìn:

```
Person A
```

---

Không thấy:

```
Person B
```

---

Khó.

---

## Scene Transformer

Thấy toàn cảnh.

---

Có thể học được.

---

Nhưng:

```
không hiểu
ai đánh ai
```

---

## Spatio-Temporal

Thấy:

```
Person A
↔
Person B
```

---

và:

```
chuyển động tương đối
```

---

Rất mạnh.

---

# Chi phí tính toán

## Temporal Transformer

Input:

```
64 frame
1 object
```

---

Token:

```
64
```

---

Attention:

```
64 x 64
```

---

Rất nhẹ.

---

## Scene Transformer

Input:

```
64 frame
```

---

Token:

```
64
```

---

Attention:

```
64 x 64
```

---

Tương đối nhẹ.

---

## Spatio-Temporal

Ví dụ:

```
64 frame
20 object
```

---

Token:

```
1280
```

---

Attention:

```
1280²

=
1.6M pair
```

---

Rất đắt.

---

# Khả năng giải thích

| Kiến trúc | Explainability |
| --- | --- |
| Temporal Transformer | ⭐⭐⭐⭐ |
| Scene Transformer | ⭐⭐ |
| Spatio-Temporal Transformer | ⭐⭐⭐ |

---

Temporal rất dễ:

```
Track #17
↓
ngã
```

---

Scene rất khó:

```
Scene event
```

---

không biết do ai.

---

# Nếu áp dụng cho các bài toán của bạn

| Bài toán | Tốt nhất |
| --- | --- |
| Helmet | Rule |
| PPE | Rule |
| Fall Detection | Temporal Transformer |
| Loitering | Temporal Transformer |
| Wrong Direction | Rule |
| Red Light | Rule |
| Near Miss | Spatio-Temporal |
| Accident Detection | Spatio-Temporal |
| Vehicle Interaction | Spatio-Temporal |
| Crowd Behavior | Spatio-Temporal |
| Fight Detection | Spatio-Temporal |
| Violence Detection | Scene hoặc Spatio-Temporal |

## Kết luận thực tế

Cho hệ thống DeepStream nhiều camera:

### Fall / Loitering

```
Detector
↓
Tracker
↓
Temporal Transformer
```

### Accident / Near Miss

```
Detector
↓
Tracker
↓
Spatio-Temporal Transformer
```

### Violence / Crowd Event

```
Detector + Tracker + Spatio-Temporal
```

hoặc

```
Video/Scene Transformer
```

nếu có dataset rất lớn.

Nếu xét tỷ lệ **accuracy / compute cost / khả năng triển khai production**, thì:

```
Temporal Transformer
>
Spatio-Temporal Transformer
>
Scene Transformer
```

cho đa số bài toán camera giao thông và smart city. Scene-level Transformer thường chỉ thực sự mạnh khi sự kiện là thuộc tính của **toàn cảnh** chứ không phải của từng đối tượng riêng lẻ.