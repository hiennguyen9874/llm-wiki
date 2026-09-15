# PagedAttention và vLLM trong phục vụ LLM

**PagedAttention** là kỹ thuật quản lý **KV cache** dành cho quá trình suy luận LLM. Ý tưởng trung tâm là áp dụng cơ chế **phân trang bộ nhớ ảo của hệ điều hành** vào bộ nhớ GPU: thay vì bắt mỗi request giữ một vùng KV cache lớn, liên tục và cố định, hệ thống chia KV cache thành các block nhỏ có kích thước cố định và cấp phát chúng theo nhu cầu.

Kỹ thuật được giới thiệu trong bài:

> **Efficient Memory Management for Large Language Model Serving with PagedAttention**
> Woosuk Kwon và cộng sự, SOSP 2023.

Trên PagedAttention, nhóm tác giả xây dựng hệ thống phục vụ mô hình có tên **vLLM**. Trong các thí nghiệm của bài báo, vLLM đạt throughput cao hơn khoảng **2–4 lần** so với FasterTransformer và hệ thống mô phỏng Orca ở cùng mức latency. ([arXiv][1])

---

## 1. Vấn đề mà bài báo giải quyết

### Quá trình sinh token có hai giai đoạn

Một request LLM thường trải qua:

1. **Prefill/prompt phase**
   Toàn bộ prompt được xử lý song song. GPU có thể sử dụng các phép nhân ma trận lớn nên hiệu suất tính toán tương đối tốt.

2. **Decode phase**
   Mô hình sinh từng token một. Mỗi token mới phụ thuộc vào tất cả token trước đó, nên các bước decode không thể song song theo chiều thời gian.

Trong decode, mô hình không tính lại key và value của toàn bộ token cũ. Thay vào đó, chúng được lưu trong **KV cache**. Ở mỗi bước, mô hình chỉ tính K và V cho token mới rồi đọc KV cache của tất cả token trước để thực hiện attention. Decode thường có cường độ tính toán thấp và bị giới hạn bởi băng thông bộ nhớ. ([arXiv][1])

### KV cache rất lớn

Với Transformer thông thường, dung lượng KV cache trên mỗi token có thể ước lượng:

[
M_{\text{token}}
================

2 \times L \times H_{kv} \times D_h \times S
]

Trong đó:

* (2): key và value;
* (L): số layer;
* (H_{kv}): số KV head;
* (D_h): kích thước mỗi head;
* (S): số byte mỗi phần tử, ví dụ FP16 là 2 byte.

Với kiến trúc multi-head attention cổ điển, (H_{kv}D_h) thường bằng hidden size, nên có thể viết:

[
M_{\text{token}}
================

2 \times L \times d_{\text{model}} \times S
]

Ví dụ của bài báo với **OPT-13B**:

[
2 \times 40 \times 5120 \times 2
=819,200\text{ bytes}
\approx800\text{ KB/token}
]

Một sequence dài 2.048 token có thể cần khoảng:

[
800\text{ KB}\times 2048\approx1.6\text{ GB}
]

chỉ riêng cho KV cache của một request. ([arXiv][1])

Với các model hiện đại dùng **MQA/GQA**, số KV head nhỏ hơn số query head, vì thế KV cache có thể nhỏ hơn đáng kể. Tuy nhiên, với context dài và nhiều request đồng thời, KV cache vẫn thường là một nút thắt quan trọng.

---

## 2. Tại sao cách cấp phát truyền thống gây lãng phí?

Trước PagedAttention, một cách phổ biến là dành cho mỗi sequence một vùng KV cache **liên tục** đủ lớn để chứa chiều dài output dự kiến hoặc chiều dài tối đa.

Điều này tạo ra ba loại lãng phí.

### Reserved memory

Hệ thống phải dự đoán output dài bao nhiêu. Vì chiều dài output chưa biết trước, nó thường cấp dư.

Ví dụ, request hiện mới có 200 token nhưng được dành trước chỗ cho 2.048 token. Phần chưa dùng vẫn bị giữ lại và request khác không thể sử dụng.

### Internal fragmentation

Nếu allocator cấp bộ nhớ theo chunk, chẳng hạn theo lũy thừa của 2, sequence cần 513 vị trí có thể được cấp chunk 1.024 vị trí. Phần còn lại nằm trong chunk nhưng không được sử dụng.

### External fragmentation

Tổng bộ nhớ trống có thể đủ, nhưng bị chia thành nhiều vùng nhỏ không liên tục. Một request cần vùng lớn liên tục sẽ không thể được cấp phát dù tổng dung lượng trống vẫn còn đủ.

Các vấn đề này làm giảm số sequence có thể đặt trong batch, trong khi batch size lớn lại rất quan trọng để tận dụng GPU. ([arXiv][1])

---

## 3. Ý tưởng cốt lõi của PagedAttention

PagedAttention chia KV cache của một sequence thành các **logical KV block**. Mỗi block chứa K và V của một số token cố định, chẳng hạn (B=16) token.

Các logical block không cần nằm cạnh nhau trong GPU RAM. Chúng được ánh xạ tới các **physical block** bất kỳ thông qua một **block table**.

Có thể đối chiếu với hệ điều hành:

| Hệ điều hành          | PagedAttention             |
| --------------------- | -------------------------- |
| Process               | Sequence/request           |
| Virtual address space | Logical KV cache           |
| Virtual page          | Logical KV block           |
| Physical frame        | Physical KV block trên GPU |
| Page table            | Block table                |
| Byte/data             | KV vector của token        |

Giả sử sequence gồm 35 token và block size là 16:

* Logical block 0: token 0–15
* Logical block 1: token 16–31
* Logical block 2: token 32–34

Ba logical block này có thể được ánh xạ tới physical block 7, 1 và 12. Chúng không cần liên tục:

```text
Logical blocks:   [0] [1] [2]
                   |   |   |
Physical blocks:  [7] [1] [12]
```

Attention kernel đọc block table, tìm vị trí physical block tương ứng, rồi đọc K và V từ các vùng đó.

Bài báo biểu diễn attention theo block. Với block size (B), key và value của block (j) là:

[
K_j =
(k_{(j-1)B+1},\ldots,k_{jB})
]

[
V_j =
(v_{(j-1)B+1},\ldots,v_{jB})
]

Thay vì giả định toàn bộ (K) và (V) nằm liên tục, kernel lần lượt tính attention trên các block được chỉ ra bởi block table rồi kết hợp kết quả. Về mặt toán học, kết quả attention không thay đổi; khác biệt nằm ở cách bố trí và truy cập KV cache. ([arXiv][1])

---

## 4. Cấp phát bộ nhớ theo nhu cầu

vLLM không dành trước KV cache cho chiều dài sequence tối đa.

Khi prompt được xử lý, nó cấp vừa đủ số block để chứa prompt. Trong quá trình decode:

1. Token mới được ghi vào vị trí còn trống của block cuối.
2. Khi block cuối đầy, block manager lấy một physical block trống.
3. Block table của sequence được mở rộng.
4. Token tiếp theo được ghi vào block mới.

Giả sử block size là 16:

* Sequence dài 1–16 token: dùng 1 block.
* Khi sinh token thứ 17: cấp block thứ hai.
* Khi sinh token thứ 33: cấp block thứ ba.

Do tất cả physical block có cùng kích thước:

* gần như không có external fragmentation;
* không cần reserve theo chiều dài tối đa;
* internal fragmentation chỉ còn ở block cuối cùng.

Nếu block size là (B), mỗi sequence lãng phí tối đa (B-1) vị trí token. Trung bình, khi độ dài sequence phân bố tương đối đều, lượng trống ở block cuối vào khoảng nửa block.

Bài báo gọi đây là khả năng đạt **near-zero waste**, không phải tuyệt đối bằng 0. ([arXiv][1])

---

## 5. Block table được dùng khi tính attention thế nào?

Khi decode token mới tại vị trí (i), kernel cần đọc K/V của các token từ 0 đến (i).

Quá trình khái niệm:

```text
for logical_block in sequence.block_table:
    physical_block = block_table[logical_block]
    K_block = key_cache[physical_block]
    V_block = value_cache[physical_block]

    tính score Q · K_block
    cập nhật softmax
    cộng tổng có trọng số với V_block
```

Trong implementation GPU, phép softmax không nhất thiết lưu toàn bộ attention score. Kernel có thể dùng online softmax để duy trì:

* maximum hiện tại;
* tổng exponential;
* vector output tích lũy.

Các warp được phân công đọc và xử lý từng KV block. Cách bố trí dữ liệu được thiết kế để các thread đọc bộ nhớ theo hướng coalesced. Tài liệu vLLM mô tả key cache và value cache dưới dạng các tensor gồm physical block, KV head, head dimension và block size. ([vLLM][2])

Điểm đánh đổi là có thêm một mức gián tiếp:

```text
logical block → block table → physical block
```

Điều này phức tạp hơn truy cập mảng liên tục và đòi hỏi kernel chuyên biệt. Bài báo đã triển khai các kernel để:

* fuse reshape và ghi KV vào block;
* fuse việc tra block table, đọc block và tính attention;
* gộp nhiều thao tác copy-on-write thành một kernel launch. ([arXiv][1])

---

## 6. Chia sẻ KV cache và Copy-on-Write

Một lợi ích lớn khác là các sequence có thể dùng chung physical block.

### Parallel sampling

Giả sử cùng một prompt cần sinh bốn câu trả lời:

```text
Prompt: "Giải thích Transformer"
Output 1: ...
Output 2: ...
Output 3: ...
Output 4: ...
```

Trước khi các output tách nhánh, KV cache của prompt giống hệt nhau. Nếu mỗi output giữ một bản sao, bộ nhớ prompt bị nhân lên bốn lần.

Trong vLLM, logical block của cả bốn sequence có thể trỏ tới cùng physical block:

```text
Sequence A ─┐
Sequence B ─┼──> Prompt physical blocks
Sequence C ─┤
Sequence D ─┘
```

Mỗi physical block có một **reference count**.

Khi một sequence cần sửa block đang được chia sẻ, vLLM dùng **copy-on-write**:

1. Kiểm tra reference count.
2. Nếu reference count lớn hơn 1, cấp physical block mới.
3. Sao chép block cũ sang block mới.
4. Chuyển sequence đang ghi sang block mới.
5. Giảm reference count của block cũ.

Nhờ vậy, phần prompt được chia sẻ; chỉ phần output bắt đầu phân nhánh mới dùng bộ nhớ riêng. Cơ chế này đặc biệt hữu ích cho parallel sampling, beam search và các trường hợp chia sẻ prefix. ([arXiv][1])

---

## 7. PagedAttention hỗ trợ continuous batching

PagedAttention và **continuous batching** là hai khái niệm khác nhau nhưng bổ trợ nhau.

Trong static batching, một batch thường phải đợi tất cả sequence hoàn thành. Sequence ngắn kết thúc sớm khiến GPU vẫn phải chờ sequence dài.

Continuous batching cho phép scheduler hoạt động ở mức từng iteration:

* sequence hoàn thành được loại khỏi batch ngay;
* request mới có thể được thêm vào;
* batch thay đổi động trong quá trình decode.

PagedAttention giúp cơ chế này hoạt động hiệu quả vì scheduler không phải tìm một vùng bộ nhớ liên tục lớn cho request mới. Nó chỉ cần cấp một số physical block đang trống.

Luồng tổng quát của vLLM:

```text
Requests
   ↓
Central scheduler
   ↓
Chọn sequence cho iteration hiện tại
   ↓
Block manager cấp / thu hồi / swap KV blocks
   ↓
GPU workers chạy model và PagedAttention
   ↓
Sinh token, cập nhật block tables
```

Bản thân continuous batching làm GPU bận hơn; PagedAttention làm cho KV cache đủ linh hoạt để duy trì batch lớn và thay đổi liên tục.

---

## 8. Preemption: swap hoặc recomputation

Khi GPU hết physical KV block nhưng có request ưu tiên cần chạy, vLLM có thể tạm dừng một số sequence.

Bài báo xem xét hai chiến lược chính:

### Swapping

KV blocks của sequence bị tạm dừng được chuyển từ GPU RAM sang CPU RAM. Khi sequence được chạy lại, các block được đưa trở lại GPU.

Ưu điểm: không phải tính lại KV cache.
Nhược điểm: tốn băng thông PCIe/NVLink và cần CPU RAM.

### Recomputation

Hệ thống xóa KV cache của sequence bị tạm dừng. Khi sequence quay lại, nó chạy lại phần prefill để tái tạo KV cache.

Ưu điểm: không cần lưu KV cache trên CPU.
Nhược điểm: tốn thêm computation.

Lựa chọn phù hợp phụ thuộc độ dài prompt, băng thông truyền dữ liệu, tải hệ thống và chi phí tính lại.

---

## 9. PagedAttention không làm giảm độ phức tạp attention

Một điểm thường bị hiểu nhầm:

**PagedAttention không biến standard attention từ (O(n)) thành (O(1)) cho mỗi token decode.**

Với token mới, mô hình vẫn phải attention tới toàn bộ context trước đó. Chi phí đọc KV cache và tính dot product vẫn tăng theo context length.

PagedAttention chủ yếu tối ưu:

* cách cấp phát KV cache;
* mức độ phân mảnh;
* khả năng chia sẻ prefix;
* khả năng chạy nhiều sequence đồng thời;
* khả năng thay đổi batch linh hoạt.

Do đó, lợi ích chính là **throughput toàn hệ thống**, không nhất thiết là giảm mạnh latency của một request đơn lẻ.

---

## 10. PagedAttention khác FlashAttention thế nào?

| PagedAttention                             | FlashAttention                         |
| ------------------------------------------ | -------------------------------------- |
| Tập trung vào quản lý KV cache khi serving | Tập trung vào cách tính attention      |
| Cho phép KV cache không liên tục           | Tiling để giảm đọc/ghi HBM             |
| Giảm fragmentation và duplication          | Giảm memory traffic và materialization |
| Quan trọng cho decode nhiều request        | Rất quan trọng cho training và prefill |
| Là abstraction quản lý bộ nhớ + kernel     | Chủ yếu là thuật toán/kernel attention |

Chúng không loại trừ nhau. Một serving engine có thể dùng:

* paged KV cache để quản lý memory;
* một attention kernel tối ưu để tính toán trên paged cache;
* FlashAttention hoặc biến thể tương thích cho prefill.

---

## 11. Kết quả thực nghiệm của bài báo

Bài báo đánh giá vLLM trên nhiều mô hình, workload và decoding algorithm, tập trung vào quan hệ giữa:

* request rate;
* serving throughput;
* latency chuẩn hóa theo số output token.

Các baseline gồm FasterTransformer và ba phiên bản mô phỏng Orca:

* **Orca Max:** luôn reserve tới chiều dài tối đa 2.048 token.
* **Orca Pow2:** cấp phát theo lũy thừa của 2.
* **Orca Oracle:** giả định biết trước chính xác chiều dài output — một giới hạn trên không khả thi trong thực tế. ([arXiv][1])

Kết quả tổng quát của bài báo là throughput tăng khoảng **2–4×** ở cùng mức latency. Lợi ích lớn hơn khi:

* model lớn hơn;
* sequence dài hơn;
* sampling tạo nhiều output;
* beam width lớn;
* workload có chiều dài biến động mạnh. ([arXiv][1])

Cần lưu ý đây là kết quả so với hệ thống và phần cứng tại thời điểm bài báo năm 2023, không phải cam kết rằng mọi phiên bản vLLM hiện nay luôn nhanh hơn mọi inference engine đúng 2–4 lần.

---

## 12. Hạn chế và đánh đổi

PagedAttention có một số chi phí:

* **Truy cập gián tiếp:** kernel phải tra block table.
* **Kernel phức tạp:** các attention kernel vốn giả định K/V liên tục không thể dùng trực tiếp.
* **Block-size trade-off:** block lớn giảm metadata và số lần cấp phát nhưng tăng internal fragmentation; block nhỏ giảm lãng phí nhưng tăng block table và overhead quản lý.
* **Copy-on-write:** khi nhiều sequence phân nhánh ở block chưa đầy, hệ thống phải copy block.
* **Single-request latency:** khi chỉ chạy một request, lợi ích từ tăng batch size và sharing có thể nhỏ.
* **Không giải quyết attention scaling:** context càng dài, lượng KV phải đọc vẫn càng lớn.

Tài liệu vLLM hiện tại cũng cảnh báo rằng phần mô tả PagedAttention dựa trên thiết kế gốc mang tính lịch sử và không còn mô tả đầy đủ code mới nhất; implementation hiện đại đã phát triển đáng kể so với hệ thống trong bài báo năm 2023. ([vLLM][2])

---

## Tóm tắt bằng một câu

**PagedAttention biến KV cache từ các mảng liên tục, cấp phát dư theo từng request thành một không gian block linh hoạt giống bộ nhớ ảo; nhờ đó vLLM chứa được nhiều sequence hơn trên GPU, chia sẻ prefix hiệu quả và duy trì continuous batching với throughput cao.**

[1]: https://arxiv.org/pdf/2309.06180 "Efficient Memory Management for Large Language Model Serving with PagedAttention"
[2]: https://docs.vllm.ai/en/latest/design/paged_attention/ "Paged Attention - vLLM"
