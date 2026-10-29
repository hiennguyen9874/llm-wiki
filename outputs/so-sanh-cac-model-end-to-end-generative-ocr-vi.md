# Thứ tự tôi sẽ thử cho OCR tiếng Việt

Nếu giả định bài toán là **chuyển tài liệu tiếng Việt dạng PDF, scan hoặc ảnh chụp thành text/Markdown, có thể có bảng và nhiều cột**, tôi sẽ ưu tiên như sau:

| Ưu tiên | Hệ thống | Khi nào nên chọn | Điểm cần cân nhắc |
|---:|---|---|---|
| **1** | **SenOCR-Vi + PaddleOCR-VL pipeline** | Tài liệu chủ yếu là tiếng Việt; muốn model nhỏ và có baseline chuyên Việt | Cần kiểm tra bảng phức tạp, chữ viết tay, ảnh khó; điểm số chưa chứng minh thắng bản base trong cùng protocol |
| **2** | **MonkeyOCRv2-B-Parsing** | Cần cân bằng tiếng Việt, layout, ảnh chụp và chi phí | Là pipeline nhiều bước; chênh lệch với SenOCR-Vi rất nhỏ |
| **3** | **Chandra OCR 2** | Ưu tiên chất lượng và xử lý tài liệu đa dạng, chấp nhận model lớn hơn | **Kiểm tra license weights trước**, nhất là dùng thương mại |
| **4** | **OvisOCR3** | Muốn thử **end-to-end**, model nhỏ, output đa dạng hoặc bảng qua trang | Chưa thấy điểm riêng tiếng Việt; benchmark tổng không đủ để xếp trên ba lựa chọn đầu |
| **5** | **PaddleOCR-VL-1.6** | Cần một baseline đa ngôn ngữ, layout-first, hoặc tài liệu Việt–Anh–Trung | Không nên mặc định SenOCR tốt hơn hay kém hơn trên dữ liệu của bạn |
| **6** | **OvisOCR2** | Muốn thêm đối chứng end-to-end nhỏ, đặc biệt với trang scan/ảnh | Chưa có bằng chứng tiếng Việt riêng trong các nguồn đã kiểm tra |
| **7** | **Xiaomi-OCR-0** | Muốn thử thêm model nhỏ, end-to-end, có KIE và bảng | Chưa thấy kết quả tiếng Việt riêng; cần chú ý output OTSL và prompt bỏ header/footer |

Đây là **thứ tự thử nghiệm, không phải bảng xếp hạng chất lượng đã được chứng minh**. Tôi xếp cao các lựa chọn có bằng chứng trực tiếp về tiếng Việt, rồi mới đến các model có benchmark tổng hấp dẫn. Nếu chỉ muốn dùng **end-to-end page parser thuần**, hãy bắt đầu bằng **Chandra OCR 2 → OvisOCR3 → OvisOCR2 → Xiaomi-OCR-0**; ba hệ thống SenOCR, MonkeyOCR và Paddle ở trên là các lựa chọn layout-first đáng giữ làm đối chứng.

## 1. SenOCR-Vi: lựa chọn đầu tiên để thử cho tiếng Việt

[SenOCR-Vi](../wiki/senocr-vi.md) là bản fine-tune khoảng **0,96B** từ PaddleOCR-VL-1.6, hướng tới tiếng Việt. Nó có thể dùng làm recognizer trong pipeline PaddleOCR, thay vì phải xây dựng lại toàn bộ hệ thống.

Lý do tôi đặt đầu:

- Có **đánh giá riêng tiếng Việt**: model card báo **82,83 document composite** và **86,7% text recognition** trên tập 160 trang. Hai số này đo khác nhau, không so trực tiếp.
- Dữ liệu huấn luyện được mô tả là thiên về tiếng Việt, có cả một nhánh chữ viết tay và tài liệu lưu trữ. Điều đó làm nó đáng thử cho dữ liệu Việt hơn một model chỉ có điểm tổng đa ngôn ngữ.
- Model card công bố **Apache-2.0**, thuận tiện hơn Chandra nếu cân nhắc triển khai thương mại.

**Nhưng không nên hiểu “chuyên Việt” là chắc chắn tốt nhất.** Model card lấy điểm PaddleOCR-VL-1.6 từ leaderboard, còn điểm SenOCR được tính lại sau khi sửa lỗi tổng hợp; hai điểm chưa được chứng minh chạy lại cùng pipeline đã sửa. Nguồn cũng cảnh báo bảng không đều, nhiều cột, công thức và ảnh suy giảm mạnh vẫn khó. Kết quả benchmark dùng FP32; nếu triển khai BF16/FP16 hoặc quantization, nên đo lại chất lượng. [Chi tiết và giới hạn](../wiki/senocr-vi.md).

**Tôi chọn nó trước nếu:** phần lớn tài liệu là văn bản Việt, cần giải pháp nhỏ và muốn có một baseline chuyên ngôn ngữ để quyết định tiếp.

## 2. MonkeyOCRv2-B-Parsing: đối thủ trực tiếp đáng thử nhất

[MonkeyOCRv2-B-Parsing](../wiki/monkeyocrv2.md) là lựa chọn mà tôi muốn chạy **song song với SenOCR**, chứ không chỉ thử sau khi SenOCR thất bại.

- Trong bảng tiếng Việt được SenOCR model card dẫn lại, Monkey đạt **83,20**, so với **82,83** của SenOCR. Khoảng cách **0,37 điểm** quá nhỏ để coi là thắng chắc, nhất là khi nguồn điểm và cách tổng hợp có khác biệt.
- Hệ thống dự đoán vùng và thứ tự đọc, nhận dạng trên crop rồi ghép kết quả: đây là hướng hợp lý để thử với trang nhiều vùng, chữ nhỏ hoặc layout phức tạp.
- Nguồn mô tả dữ liệu huấn luyện đa ngôn ngữ có tiếng Việt; model card công bố **Apache-2.0**. [MonkeyOCRv2](../wiki/monkeyocrv2.md), [MonkeyDoc v2](../wiki/monkeydoc-v2.md).

Điểm đánh đổi là pipeline nhiều bước có thể phát sinh lỗi ngay từ phát hiện vùng hoặc thứ tự đọc; đồng thời **0,7B trong bảng không phải thông số đủ để suy ra VRAM hay tốc độ toàn pipeline**.

**Tôi có thể đẩy Monkey lên số 1** nếu tập của bạn có nhiều ảnh chụp, trang nhiều cột, bố cục phức tạp hoặc cần một hệ thống đa ngôn ngữ hơn là chỉ chuyên Việt.

## 3. Chandra OCR 2: ứng viên chất lượng cao, nhưng license có thể loại sớm

Trong bảng Vietnamese composite mà SenOCR dẫn từ leaderboard, [Chandra OCR 2](../wiki/chandra-ocr-2.md) có **85,60**, cao nhất trong bốn lựa chọn Việt được nêu ở báo cáo. Model card cũng mô tả hỗ trợ form, checkbox, bảng, toán, chữ viết tay và layout phức tạp.

Tôi không đặt số 1 mặc định vì:

1. **License weights không phải Apache-2.0.** Wiki ghi code là Apache-2.0 nhưng weights dùng modified OpenRAIL-M, có giới hạn sử dụng thương mại và cạnh tranh với API của Datalab. Phải đọc license hiện hành theo hoàn cảnh tổ chức trước khi đầu tư triển khai.
2. Bảng so sánh ước lượng model khoảng **5B**; model card riêng trong wiki không xác nhận số tham số. Không thể suy ra trực tiếp chi phí hay VRAM từ con số đó.
3. Điểm 85,60 là **điểm được nguồn dẫn lại**, không phải phép thử độc lập trên tài liệu của bạn.

**Nếu license phù hợp và ưu tiên chất lượng hơn chi phí**, tôi sẽ chạy Chandra cùng đợt đầu với SenOCR và Monkey. Với bài toán biểu mẫu, hồ sơ nhiều loại nội dung, đây là ứng viên đặc biệt đáng kiểm tra.

## 4. OvisOCR3: lựa chọn end-to-end nhỏ tôi muốn thử đầu tiên

[OvisOCR3](../wiki/ovisocr3.md) khoảng **0,8B**, nhận ảnh trang và có các chế độ sinh Markdown, JSON layout, OCR, KIE và ghép bảng qua trang. Model card công bố Apache-2.0.

Nó hấp dẫn vì model card báo **88,80 MDPBench tổng**, cùng các kết quả tốt trên benchmark parsing khác. Nhưng ở đây có một ranh giới quan trọng:

> **88,80 là điểm MDPBench tổng, không phải điểm tiếng Việt. Không được so trực tiếp với 82,83 hay 83,20 của Vietnamese slice.**

Card cũng không nêu đủ split, prompt và preprocessing cho điểm MDPBench tổng. Vì vậy, OvisOCR3 là **ứng viên có tiềm năng cao nhưng chưa có đủ bằng chứng để tôi xếp trên nhóm có điểm riêng tiếng Việt**.

Tôi sẽ ưu tiên nó hơn nếu cần:

- Một model **page-to-Markdown/JSON** thay vì pipeline crop nhiều bước.
- Trích xuất field/KIE cùng OCR.
- Thử **bảng nối qua trang**; lưu ý đây vẫn là quy trình parse trang rồi ghép theo cặp, không phải bảo đảm toàn bộ bảng dài luôn đúng.

Cần kiểm tra đặc biệt lỗi mất dấu, bỏ sót dòng và nội dung lặp/bịa; card cũng cảnh báo output có thể sai, thiếu hoặc malformed.

## 5. PaddleOCR-VL-1.6: baseline đa ngôn ngữ và đối chứng quan trọng

[PaddleOCR-VL-1.6](../wiki/paddleocr-vl-1.6.md) là model gốc mà SenOCR-Vi fine-tune, dùng layout analysis trước khi nhận dạng từng vùng.

Tôi giữ nó trong shortlist vì nó trả lời một câu hỏi rất thực dụng: **fine-tune chuyên Việt có thực sự đem lại giá trị trên tài liệu của mình không?**

- Vietnamese composite được dẫn lại: **80,90**.
- SenOCR báo **82,83**, nhưng như đã nói, hai điểm chưa cùng đường tổng hợp.
- Model card SenOCR báo điểm trung bình ba ngôn ngữ Việt–Anh–Trung của SenOCR thấp hơn nhẹ so với base; đó là lý do đáng thử cả hai nếu dữ liệu đa ngôn ngữ. [Nguồn](../wiki/senocr-vi.md).

Nếu dùng Paddle pipeline, việc hoán đổi recognizer giữa base và SenOCR còn giúp so sánh có kiểm soát hơn: giữ layout stage và các thiết lập khác cố định.

## 6–7. Các option end-to-end bổ sung

### OvisOCR2

[OvisOCR2](../wiki/ovisocr2.md) đáng giữ như đối chứng nhỏ với OvisOCR3. Báo cáo đã đọc cho thấy nó có kết quả tổng và các thành phần parsing tốt, đồng thời có điểm PureDocBench tách điều kiện tài liệu sạch/ảnh thực tế.

Tuy nhiên, **điểm tổng đó không chứng minh khả năng tiếng Việt**. Tôi không mặc định OvisOCR3 tốt hơn OvisOCR2 trên dữ liệu Việt chỉ vì điểm tổng của OvisOCR3 cao hơn.

### Xiaomi-OCR-0

Đây là một option **mới có trong wiki mà báo cáo ở `outputs/` chưa đưa vào bảng**. [Xiaomi-OCR-0](../wiki/xiaomi-ocr-0.md) là model **0,8B**, card công bố Apache-2.0; có page parsing, OCR và KIE, cùng benchmark tổng đáng chú ý.

Tôi xếp sau Ovis vì chưa tìm thấy kết quả riêng tiếng Việt trong trang nguồn đã kiểm tra. Có hai chi tiết triển khai cần lưu ý:

- Prompt whole-page mặc định yêu cầu **bỏ header/footer**: không phù hợp nếu bạn cần bản chép đầy đủ số trang, tên cơ quan hoặc nội dung ở mép trang.
- Bảng được sinh ở dạng **OTSL**, nên cần kiểm tra bước chuyển đổi sang định dạng downstream mong muốn.

Không nên chọn model này chỉ vì hơn model khác vài phần trăm trên benchmark tổng.

## Bằng chứng tiếng Việt hiện có nói được gì?

Bảng gần câu hỏi nhất trong wiki là bảng Vietnamese composite do model card SenOCR tổng hợp:

| Hệ thống | Điểm được báo cáo |
|---|---:|
| Chandra OCR 2 | **85,60** |
| MonkeyOCRv2-B-Parsing | **83,20** |
| SenOCR-Vi | **82,83** |
| PaddleOCR-VL-1.6 | **80,90** |

[Nguồn: SenOCR-Vi](../wiki/senocr-vi.md), [bối cảnh MDPBench](../wiki/mdpbench.md).

Các điểm này hữu ích để **chọn ứng viên**, nhưng chưa đủ để tuyên bố thứ hạng production:

- SenOCR được tính lại sau sửa lỗi scorer; các dòng khác được dẫn từ leaderboard. Chưa có bằng chứng tất cả chạy lại bằng cùng pipeline đã sửa.
- Đây là **document composite**, không thuần đo độ chính xác từng dấu tiếng Việt.
- Tập này không nhất thiết đại diện cho hóa đơn, hợp đồng, hồ sơ hành chính, sách cũ hay ảnh chụp từ điện thoại của bạn.
- Wiki chưa tái lập độc lập các kết quả trên.

Vì vậy, tôi đặt **SenOCR và Monkey** trước Chandra trong thứ tự *thử thực dụng* do ưu tiên chuyên Việt/model nhỏ và license được công bố, **không phải vì có bằng chứng chúng chính xác hơn Chandra**.

## Nên benchmark thế nào để chốt lựa chọn?

Tôi sẽ bắt đầu bằng **4 hệ thống: SenOCR-Vi, MonkeyOCRv2-B, Chandra OCR 2 nếu license cho phép, và OvisOCR3**. Nếu không dùng được Chandra về license, thay bằng PaddleOCR-VL-1.6 hoặc Xiaomi-OCR-0.

1. **Chọn 100–300 trang đại diện nếu có thể**, chia theo nguồn thực tế: PDF sinh từ máy, scan, ảnh chụp; văn bản đơn giản, nhiều cột, bảng, chữ viết tay và ảnh mờ. Nếu dữ liệu ít, bắt đầu bằng 20–50 tài liệu nhưng coi kết quả là thăm dò.
2. **Tạo ground truth thủ công** cho một phần đủ đại diện. Với tiếng Việt, đánh giá riêng lỗi **dấu thanh, dấu phụ, nhầm `đ/d`, chữ hoa và tên riêng**; đo CER/WER sau khi thống nhất quy tắc Unicode, khoảng trắng và xuống dòng.
3. **Chấm riêng bảng, thứ tự đọc và bỏ sót nội dung**. Đặc biệt kiểm tra số tiền, ngày tháng, mã định danh; điểm CER tổng có thể che các lỗi rất nghiêm trọng này.
4. Dùng **cùng ảnh nguồn và ground truth**, nhưng cho mỗi model chạy đúng prompt/preprocessing được khuyến nghị; ghi lại DPI, resize, prompt, output, retry và hậu xử lý. Sau đó có thể làm thêm một lượt kiểm soát chặt hơn. Không ép mọi model dùng cùng prompt nếu interface khác nhau.
5. Đo **chất lượng và vận hành riêng**: peak VRAM, latency, throughput, lỗi cắt output, chi phí và tỷ lệ cần người sửa. Xem xét cả thời gian của layout model và postprocessing, không chỉ recognizer.
6. Với hồ sơ pháp lý/tài chính, giữ ảnh gốc và **có bước người kiểm tra**; không xem output generative là bản chép chắc chắn trung thực.

**Kết luận ngắn:** Nếu chưa có thông tin khác, tôi sẽ triển khai thử **SenOCR-Vi và MonkeyOCRv2-B trước**, thêm **Chandra OCR 2** làm đối chứng chất lượng nếu license cho phép, và **OvisOCR3** làm đối chứng end-to-end nhỏ. Sau đó để **kết quả trên tài liệu Việt của bạn**, đặc biệt lỗi dấu và bỏ sót, quyết định thứ tự cuối cùng.

*Giới hạn kiểm tra:* Tôi đã đọc báo cáo trong `outputs/`, kiểm tra index và các trang wiki liên quan; structural check báo **103 concept, không có lỗi cấu trúc**. Tôi **không mở lại raw**, không chạy model hay benchmark trong lượt này. Câu trả lời được để dưới dạng tư vấn tạm thời, không sửa wiki hay log.

Có. Trước hết, tôi muốn làm rõ: **“không chọn” ở câu trả lời trước nghĩa là chưa đưa vào vòng thử đầu, không có nghĩa các model đó OCR tiếng Việt kém hoặc không hỗ trợ tiếng Việt**.

Lý do chính là tôi đang tối ưu số hệ thống cần thử ban đầu cho một bài toán **tài liệu chủ yếu bằng tiếng Việt, chưa biết rõ loại tài liệu và phần cứng**. Với giả định đó, tôi ưu tiên bằng chứng trực tiếp trên tiếng Việt; các benchmark tổng như OmniDocBench hay olmOCR-Bench chỉ là bằng chứng bổ trợ.

Ngoài ra, tôi đồng ý rằng shortlist trước có một điểm hơi thiếu: **FireRed-OCR, Infinity-Parser2 Flash và LightOnOCR-3 đáng được nêu rõ là ứng viên vòng hai**, chứ không nên để người đọc hiểu là đã loại hẳn.

## Nhóm tôi vẫn rất muốn thử nếu có thêm thời gian

### 1. FireRed-OCR — đáng thử cho ảnh chụp và tài liệu biến dạng

[FireRed-OCR](../wiki/firered-ocr.md) là model end-to-end 2B. Tôi chưa đưa nó vào nhóm đầu vì **chưa thấy kết quả tiếng Việt riêng** trong các tài liệu đã kiểm tra, trong khi SenOCR, MonkeyOCRv2 và Chandra có số liệu Vietnamese slice được dẫn lại.

Nhưng FireRed có lý do thực tế để thử:

- Báo cáo tác giả có đánh giá trên tài liệu biến dạng và layout không chuẩn.
- Trong bảng OmniDocBench 1.5 ở báo cáo ban đầu, text edit và reading-order edit của FireRed khá tốt.
- Nó là **page-to-Markdown end-to-end**, nên có thể là lựa chọn thay thế pipeline nhiều bước.

**Khi nào đẩy lên vòng đầu?** Khi dữ liệu là ảnh chụp điện thoại, trang cong, lệch hoặc bóng sáng; đặc biệt nếu bạn muốn giải pháp end-to-end. Dù vậy, benchmark ảnh khó của FireRed là benchmark nội bộ và chưa cho biết riêng kết quả tiếng Việt. Tôi sẽ không suy ra rằng nó đọc dấu tiếng Việt tốt chỉ từ khả năng xử lý méo trang.

### 2. Infinity-Parser2 Flash/Pro — mạnh về cấu trúc, nhưng bằng chứng tiếng Việt chưa đủ

[Infinity-Parser2](../wiki/infinity-parser2.md) có output phong phú: Markdown, JSON kèm tọa độ, bảng, công thức và các loại nội dung khác. Flash là **2B**, còn Pro là **35B tổng / 3B active**.

Tôi chưa xếp chúng vào vòng đầu vì:

- Chưa thấy điểm Vietnamese slice tương ứng để đối chiếu với nhóm đầu.
- Nguồn huấn luyện được mô tả thiên về **tiếng Trung và tiếng Anh**; điều đó không chứng minh model không đọc được tiếng Việt, nhưng khiến tôi muốn đo thực tế trước. Xem [Infinity-Doc2-5M](../wiki/infinity-doc2-5m.md).
- Pro có 35B tham số tổng: **3B active không có nghĩa là footprint bộ nhớ giống model dense 3B**.
- Điểm benchmark cao của Pro/Flash đến từ protocol tác giả; không nên ghép thành bảng xếp hạng chính xác với điểm của Ovis hoặc SenOCR.

**Khi nào chọn?** Nếu yêu cầu quan trọng là **JSON có bounding box, bảng/công thức hoặc nhiều tác vụ trong cùng model**, tôi sẽ thêm **Flash** sớm. Pro đáng thử khi chất lượng cấu trúc quan trọng và hạ tầng cho phép.

### 3. LightOnOCR-3 — đặc biệt hấp dẫn nếu cần grounding

[LightOnOCR-3](../wiki/lightonocr-3.md) có các bản **0.8B, 1B, 4B**, công bố Apache-2.0. Nó không chỉ sinh transcription mà còn có chế độ `grounding` cho nhãn và bounding box của các block.

Tôi chưa xếp vào vòng đầu vì:

- Các nguồn đã kiểm tra **chưa cho thấy điểm riêng tiếng Việt hoặc phạm vi ngôn ngữ đủ rõ**.
- Điểm olmOCR-Bench và các số tốc độ trong báo cáo là do nhà phát hành chạy; có khác biệt về render và postprocessing, nên chưa trả lời model nào tốt hơn trên tiếng Việt.
- Các bản dùng cấu hình loader/render khác nhau; chọn 0.8B hay 4B cần đo theo phần cứng và tài liệu thực tế.

**Khi nào chọn?** Nếu bạn cần **vừa Markdown vừa tọa độ vùng**, LightOnOCR-3 0.8B là option đáng thêm ngay. Nếu ưu tiên chất lượng hơn footprint, thử 4B. Xem thêm [đánh giá](../wiki/lightonocr-3-evaluation.md) và [triển khai](../wiki/lightonocr-3-deployment.md).

Tôi ưu tiên **LightOnOCR-3** hơn **LightOnOCR-2-1B** cho một thử nghiệm mới vì thế hệ 3 bổ sung grounding; tuy nhiên, nếu đã có stack LightOnOCR-2 thì bản cũ vẫn là đối chứng hữu ích. Điểm 83,2 của bản 2 trong báo cáo còn loại header/footer khỏi aggregate, nên không so thẳng với các dòng dùng protocol khác. [Nguồn](../wiki/lightonocr.md).

### 4. HunyuanOCR-1.5 — đáng thử nếu triển khai PC/llama.cpp

[HunyuanOCR-1.5](../wiki/hunyuanocr-1.5.md) có hướng triển khai qua Transformers, vLLM và `llama.cpp`, cùng speculative decoding DFlash.

Tôi để sau vì model card và README được lưu **không có benchmark tiếng Việt riêng**, cũng không có bảng latency đầy đủ để kiểm chứng lợi thế triển khai. Báo cáo tổng hợp có một điểm OmniDocBench do nguồn khác chép lại, nhưng điều đó chưa giải quyết câu hỏi tiếng Việt.

Cần chú ý thêm:

- Prompt document parsing được tài liệu minh họa yêu cầu **bỏ header/footer**.
- README nói model dùng Tencent Hunyuan Community License; **file license không có trong bundle đã kiểm tra**, nên cần đọc điều khoản thực tế trước khi quyết định thương mại.

**Khi nào chọn?** Nếu ưu tiên chạy trên PC/laptop hoặc muốn thử hệ sinh thái `llama.cpp`, tôi sẽ nâng Hunyuan lên shortlist thử triển khai.

---

## Nhóm có thế mạnh riêng nhưng không ưu tiên cho bài toán Việt tổng quát

### 5. Unlimited OCR và Unlimited OCR 2 — ưu tiên khi tài liệu rất dài

[Unlimited OCR](../wiki/unlimited-ocr.md) và [Unlimited OCR 2](../wiki/unlimited-ocr-2.md) tập trung vào parsing nhiều trang, đặc biệt thế hệ 2 có chunking và sparse attention cho tài liệu dài.

**Tại sao chưa chọn đầu?**

- Chưa có bằng chứng tiếng Việt riêng trong phần tài liệu đã kiểm tra.
- Nếu bài toán chỉ là OCR từng trang, thế mạnh long-document chưa chắc bù được độ phức tạp triển khai.
- Cấu hình serving Unlimited OCR 2 trong nguồn có custom wheel và cơ chế chunk/cache; các thành phần đó chưa được kiểm tra hoặc chạy ở đây.
- Model 3B tổng / khoảng 0.5B active không đồng nghĩa chỉ cần tài nguyên như model 0.5B dense.

**Khi nào chọn?** Khi cần xử lý **sách/hồ sơ hàng trăm trang, đoạn văn hoặc bảng nối trang**, hãy thử Unlimited OCR 2 cùng OvisOCR3. Hai hệ thống có cách tiếp cận khác nhau; không nên so điểm cross-page từ benchmark khác nhau như thể cùng một phép thử.

### 6. Qianfan-OCR — ứng viên đa năng, nhưng chưa có lợi thế tiếng Việt trực tiếp

[Qianfan-OCR](../wiki/qianfan-ocr.md) là model 4B có parsing, OCR và document understanding. Nó có các benchmark tổng và bảng cho nhiều tác vụ.

Tôi chưa ưu tiên vì chưa thấy điểm riêng tiếng Việt trong phần bằng chứng đã xem. Với một vòng thử có giới hạn, tôi chọn model có Vietnamese slice trước và dùng OvisOCR3 làm đối chứng end-to-end nhỏ.

**Khi nào chọn?** Nếu ngoài transcription bạn còn cần **VQA/KIE** hoặc muốn một model 4B đa năng, Qianfan là option hợp lý để thử. Điểm PureDocBench trong báo cáo cũng không phải bằng chứng rằng nó sẽ kém trên tài liệu Việt của bạn.

### 7. Nanonets-OCR2 — hợp khi cần cả OCR và VQA/biểu diễn đặc biệt

[Nanonets-OCR2](../wiki/nanonets-ocr2.md) có bản 3B và có thể sinh bảng, công thức, checkbox, chữ ký, watermark và một số cấu trúc khác.

Tôi chưa chọn đầu vì:

- Model card liệt kê nhiều ngôn ngữ, nhưng **không liệt kê tiếng Việt trong danh sách được trang wiki trích**; điều này **không chứng minh model không hỗ trợ tiếng Việt**.
- Điểm ChartQA/DocVQA trong báo cáo đo các tác vụ VQA, không trực tiếp đo độ chính xác transcription tiếng Việt.
- Nguồn local chưa đủ cấu hình để tái lập benchmark; license và deployment của các tài nguyên liên kết chưa được xác minh tại đây.

**Khi nào chọn?** Nếu đầu ra cần đánh dấu **checkbox, signature, watermark hoặc mô tả hình**, Nanonets đáng thử. Nếu dữ liệu nhạy cảm và cân nhắc bản hosted/API, cần kiểm tra chính sách xử lý dữ liệu trước.

### 8. dots.ocr — có thể hữu ích cho layout, nhưng phải xác định đúng phiên bản

[dots.ocr](../wiki/dots-ocr.md) có khả năng tạo layout, nội dung và thứ tự đọc; đây là một ứng viên hợp lý cho document parsing.

Tôi chưa đưa vào vòng đầu vì:

- Báo cáo có các tên **dots.ocr, dots.ocr 1.5 và dots.mocr**; không nên lấy điểm một phiên bản rồi gán cho phiên bản khác.
- Chưa có điểm Vietnamese slice tương ứng trong các trang tôi đã dùng để chọn shortlist.
- Nhóm đầu đã có Monkey/Paddle làm đối chứng layout-first và Ovis làm đối chứng page-level.

**Khi nào chọn?** Nếu dự án cần output liên quan **layout, thứ tự đọc hoặc tọa độ**, nên thử đúng checkpoint/version và đánh giá trên cùng tập Việt.

### 9. DeepSeek-OCR 2 — model nén thông tin thị giác đáng thử, nhưng chưa có lý do Việt-specific để ưu tiên

[DeepSeek-OCR 2](../wiki/deepseek-ocr-2.md) dùng cơ chế nén biểu diễn thị giác và decoder MoE. Báo cáo tổng hợp có kết quả OmniDocBench, nhưng còn ghi các nguồn khác nhau báo điểm khác nhau ngay cả với nhãn v1.5.

Tôi chưa chọn đầu vì chưa thấy kết quả riêng cho tiếng Việt; đồng thời con số **decoder 3B / khoảng 0.5B active** không phải ước lượng đầy đủ chi phí toàn hệ thống. Benchmark tổng hoặc kiến trúc nén thị giác không chứng minh model giữ dấu tiếng Việt tốt hơn model khác.

**Khi nào chọn?** Nếu bạn muốn khảo sát một hướng khác về **visual-token compression**, hoặc có sẵn hạ tầng DeepSeek, hãy thêm nó làm đối chứng. Nên kiểm tra riêng chữ nhỏ, dấu và nội dung dày trên trang.

### 10. olmOCR-2-7B — baseline hệ sinh thái PDF, nhưng khá lớn cho vòng đầu

[olmOCR-2-7B-1025](../wiki/olmocr-2-7b-1025.md) có toolkit với các bước như render, rotation và retry; báo cáo có điểm BF16 và FP8.

Tôi chưa ưu tiên vì:

- Chưa thấy điểm tiếng Việt riêng trong bằng chứng đã dùng.
- **7B** là một mức kích thước đáng cân nhắc khi các đối chứng đầu có model nhỏ hơn; tuy nhiên, không thể suy ra latency/VRAM chính xác chỉ từ số tham số.
- Chất lượng của một pipeline gồm render/retry không nên quy hết cho weights.

**Khi nào chọn?** Khi bạn muốn một **baseline PDF-to-text/Markdown có toolkit rõ ràng**, hoặc đã dùng stack olmOCR. Nên so cả hệ thống end-to-end, bao gồm retry và chi phí.

### 11. Nemotron Parse 2.0 và v1.1 — đáng thử nếu cần box và đang dùng NVIDIA

[Nemotron Parse 2.0](../wiki/nemotron-parse-2-0.md) là parser dưới 1B, có output text, class và bounding box. Card báo cải thiện trên multilingual, handwriting, table và chart.

Tôi chưa đưa vào nhóm đầu vì:

- Các số multilingual là **điểm tổng**, chưa phải bằng chứng riêng cho tiếng Việt.
- Model card mô tả triển khai NVIDIA GPU và một số yêu cầu về runtime/patch; cần đánh giá độ phù hợp với stack thực tế.
- License model/config là **OpenMDW 1.1**, tokenizer có license riêng; cần xem kỹ điều khoản thay vì mặc định Apache-2.0.

Bản **v1.1** là thế hệ cũ hơn; nếu bắt đầu mới, tôi sẽ xem xét **2.0 trước**, trừ khi bạn đã có hệ thống phụ thuộc v1.1 hoặc benchmark nội bộ cho thấy v1.1 phù hợp hơn. [Nguồn v1.1](../wiki/nemotron-parse-v1-1.md).

**Khi nào chọn?** Khi cần **box + class + text** và đã vận hành inference trên NVIDIA.

### 12. Granite Docling 258M — lựa chọn nhỏ, nhưng mục tiêu khác

[Granite Docling 258M](../wiki/granite-docling-258m.md) hấp dẫn vì kích thước rất nhỏ và nằm trong hệ sinh thái Docling.

Tôi không chọn đầu vì nguồn trong báo cáo chưa cho thấy bằng chứng riêng tiếng Việt đủ mạnh để đặt cạnh SenOCR hoặc Monkey. Ngoài ra, nó được định vị gắn với **Docling/document conversion**, không nhất thiết là phép so sánh một-một với một page parser độc lập.

**Khi nào chọn?** Nếu bạn đang dùng Docling, cần document representation hoặc muốn thử phương án nhỏ hơn, đây là baseline hữu ích. Hãy đo chất lượng tiếng Việt thay vì chọn chỉ vì 258M.

### 13. Typhoon OCR 1.5 — không ưu tiên vì chuyên Thai/English

[Typhoon OCR](../wiki/typhoon-ocr.md) được định vị chuyên **Thai và English**. Đây là lý do trực tiếp nhất khiến tôi chưa ưu tiên cho tài liệu chủ yếu tiếng Việt.

Điều đó **không chứng minh nó không xử lý được tiếng Việt**; chỉ là bằng chứng được báo cáo phù hợp hơn với bài toán Thai/English.

**Khi nào chọn?** Nếu tài liệu của bạn là **Việt–Thái–Anh**, hoặc nhiều văn bản Thái, tôi sẽ đưa Typhoon vào thử nghiệm.

---

## Nếu phân bổ thêm ngân sách thử nghiệm

Sau bốn hệ thống đề xuất ban đầu, thứ tự **mở rộng** của tôi sẽ là:

| Vòng | Model/hệ thống | Lý do thêm |
|---|---|---|
| 1 | **SenOCR-Vi, MonkeyOCRv2-B, Chandra OCR 2*, OvisOCR3** | Có bằng chứng tiếng Việt trực tiếp hoặc là đối chứng end-to-end nhỏ |
| 2 | **PaddleOCR-VL-1.6** | Đối chứng base model của SenOCR |
| 2 | **FireRed-OCR** | Đáng thử trên ảnh chụp/trang biến dạng |
| 2 | **LightOnOCR-3 0.8B hoặc 4B** | Thử transcription kèm grounding |
| 2 | **Infinity-Parser2 Flash** | Thử JSON/layout và nội dung có cấu trúc |
| 3, theo nhu cầu | **Unlimited OCR 2** | Tài liệu rất dài, cross-page |
| 3, theo nhu cầu | **HunyuanOCR-1.5** | PC/`llama.cpp`, cần kiểm tra license |
| 3, theo nhu cầu | **Nemotron Parse 2.0** | NVIDIA stack, bounding boxes |
| 3, theo nhu cầu | **Nanonets, Qianfan, dots, DeepSeek, olmOCR, Granite, Typhoon** | Chọn theo định dạng, hệ sinh thái hoặc ngôn ngữ liên quan |

\* **Chandra chỉ vào vòng thử triển khai khi license weights phù hợp với mục đích sử dụng.**

Nếu ngân sách chỉ cho phép thử **ba model** và ưu tiên là **độ chính xác văn bản Việt**, tôi chọn **SenOCR-Vi + MonkeyOCRv2-B + Chandra OCR 2** nếu license cho phép; thay Chandra bằng **OvisOCR3** nếu muốn tránh rủi ro license hoặc muốn đối chứng end-to-end nhỏ.

**Giới hạn:** Tôi đã xem thêm các trang wiki cho nhóm model còn lại, nhưng **không mở lại raw và không chạy benchmark/model**. Việc một model không có điểm tiếng Việt trong các nguồn đã kiểm tra không có nghĩa là bên ngoài không tồn tại benchmark đó. Câu trả lời này không sửa wiki.