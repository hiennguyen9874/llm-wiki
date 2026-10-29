# Nên chọn OCR tiếng Việt theo thứ tự nào?

Nếu mục tiêu là **chuyển tài liệu tiếng Việt thành văn bản/Markdown có cấu trúc**, tôi sẽ chọn thứ tự **ưu tiên thử nghiệm**, không phải khẳng định thứ hạng chất lượng tuyệt đối:

1. **SenOCR-Vi** — ứng viên mặc định cho tài liệu chủ yếu tiếng Việt.
2. **MonkeyOCRv2-B-Parsing** — đối thủ cần thử song song; có bằng chứng tiếng Việt đáng chú ý nhưng không nằm trong báo cáo ban đầu.
3. **PaddleOCR-VL-1.6** — baseline và phương án cân bằng, đặc biệt khi tài liệu đa ngôn ngữ hoặc ảnh chụp.
4. **Chandra OCR 2** — ứng viên chất lượng cao nếu chấp nhận model lớn hơn và điều khoản thương mại hạn chế hơn.
5. **TeleOCR** — nên thử nếu tài liệu có bảng phức tạp, trang cong hoặc ảnh chụp.
6. **MiniCPM-OCR 1.0 / Xiaomi-OCR-0** — ứng viên bổ sung khi cần thử tốc độ, ảnh biến dạng hoặc pipeline cụ thể; hiện thiếu bằng chứng tiếng Việt đủ mạnh để xếp cao hơn.

Nếu bắt buộc giữ đúng phạm vi **layout-first modular** của báo cáo, tôi sẽ thử trước **SenOCR-Vi → MonkeyOCRv2-B-Parsing → PaddleOCR-VL-1.6 → TeleOCR**. Chandra OCR 2 là phương án mở rộng để so sánh chất lượng, không mặc định coi là cùng kiến trúc layout-first.

## Bằng chứng tiếng Việt quan trọng nhất

Ngoài báo cáo trong `outputs/`, wiki có một bảng trên lát cắt tiếng Việt của [MDPBench](wiki/mdpbench.md), được ghi trong model card [SenOCR-Vi](wiki/senocr-vi.md):

| Model | Size được báo cáo | Vietnamese document composite ↑ | Vai trò trong shortlist |
|---|---:|---:|---|
| Chandra OCR 2 | 5B | **85,60** | Thử khi ưu tiên chất lượng và đủ tài nguyên |
| MonkeyOCRv2-B-Parsing | 0,7B | **83,20** | Đối thủ nhỏ, đáng thử sớm |
| SenOCR-Vi | 0,959B | **82,83** | Chuyên biệt tiếng Việt |
| PaddleOCR-VL-1.6 | ~0,9B | **80,90** | Baseline cùng họ với SenOCR |

**Phải đọc bảng này với caveat lớn:** điểm SenOCR được tính lại trên 160 trang tiếng Việt sau khi sửa lỗi tổng hợp; các hàng còn lại được dẫn từ leaderboard, không được tính lại bằng cùng pipeline đã sửa. Tất cả đều là kết quả được công bố, chưa chạy lại độc lập. Do đó, đặc biệt không nên kết luận MonkeyOCR thắng SenOCR chỉ vì hơn **0,37 điểm**, hay SenOCR chắc chắn thắng Paddle đúng **1,93 điểm**. Ngoài ra, composite đo parsing tài liệu, không chỉ đo lỗi dấu tiếng Việt. [Nguồn và giới hạn](wiki/senocr-vi.md#comparability-caveats).

MDPBench bỏ qua header, footer, số trang và page footnote khi chấm. Nếu hệ thống của bạn cần giữ các phần này, điểm benchmark cũng chưa trả lời được yêu cầu đó. [Nguồn](wiki/mdpbench.md#evaluation-protocol-and-reported-results).

## Giải thích từng lựa chọn

### 1. SenOCR-Vi — lựa chọn đầu tiên cho workload thuần Việt

Tôi đặt SenOCR đầu tiên vì đây là ứng viên trong wiki có **mục tiêu và dữ liệu fine-tune trực tiếp cho tiếng Việt**: model dựa trên PaddleOCR-VL-1.6, dữ liệu huấn luyện gồm cả chữ viết tay tiếng Việt, văn bản và dữ liệu lưu trữ. Model card báo cáo **86,7% text recognition** trên lát cắt tiếng Việt; đây là metric khác composite 82,83, không được lấy hai số để so ngang nhau. [Nguồn](wiki/senocr-vi.md#training-data).

Điểm thực dụng là có thể dùng SenOCR làm recognition model trong pipeline PaddleOCR-VL 1.6. Điều đó tạo ra phép thử hữu ích: **giữ pipeline và dữ liệu đầu vào giống nhau, chỉ đổi recognition model giữa SenOCR và Paddle base**. Nếu SenOCR tốt hơn rõ trên dấu, tên riêng và số liệu mà không làm hỏng bảng, đây là lựa chọn hợp lý.

**Điểm cần kiểm tra:** model card nêu khó khăn với bảng phức tạp, công thức, nhiều cột và ảnh suy giảm nặng. Dữ liệu huấn luyện có chữ viết tay **không chứng minh** nó tốt cho mọi loại chữ viết tay. Benchmark được nêu dùng FP32; nếu triển khai precision thấp hơn, cần đo lại. [Nguồn](wiki/senocr-vi.md#limitations).

### 2. MonkeyOCRv2-B-Parsing — ứng viên không nên bỏ sót

Báo cáo ban đầu chưa đưa MonkeyOCRv2 vào shortlist, nhưng wiki có bằng chứng đủ để tôi đặt nó **ngay cạnh SenOCR**. Bản B-Parsing dùng mô hình dự đoán vùng và thứ tự đọc, nhận dạng từng crop rồi ghép kết quả; card SenOCR dẫn điểm **83,20** trên lát cắt tiếng Việt MDPBench. Bộ dữ liệu tiền huấn luyện được mô tả có tiếng Việt trong 17 ngôn ngữ. [Nguồn kiến trúc](wiki/monkeyocrv2.md#parsing-system-and-reported-results), [nguồn dữ liệu](wiki/monkeydoc-v2.md).

Tôi vẫn xếp sau SenOCR theo **thứ tự thử**, vì SenOCR chuyên biệt tiếng Việt và có thể so trực tiếp với Paddle base bằng cách giữ chung pipeline. Nhưng nếu benchmark nội bộ cho thấy Monkey đọc dấu hoặc giữ bố cục tốt hơn, hoàn toàn có thể chọn Monkey làm phương án chính.

**Điểm cần kiểm tra:** con số 83,20 là hàng leaderboard được card SenOCR dẫn lại; chưa có cùng quy trình tính lại để khẳng định hơn SenOCR. Các kết quả wiki lưu cũng chưa được chạy lại độc lập.

### 3. PaddleOCR-VL-1.6 — baseline bắt buộc và lựa chọn cân bằng

PaddleOCR-VL-1.6 là điểm xuất phát tốt nếu tài liệu không chỉ có tiếng Việt mà còn pha tiếng Anh/Trung, hoặc gồm cả scan và ảnh chụp. Trong đánh giá EN/VI/ZH được card SenOCR dẫn, macro của Paddle base là **83,43**, so với **82,98** của SenOCR; vì vậy fine-tune tiếng Việt không đồng nghĩa cải thiện đồng đều mọi ngôn ngữ. [Nguồn](wiki/senocr-vi.md#reported-evaluation).

Ngoài ra, báo cáo Paddle ghi **93,19 trên Real5**, hữu ích như tín hiệu cho tài liệu bị biến dạng. Nhưng Real5 không phải bằng chứng riêng cho tiếng Việt; không thể lấy điểm này để kết luận Paddle đọc dấu tiếng Việt tốt hơn model khác. [Nguồn](wiki/paddleocr-vl-1.6.md#reported-results).

**Khi nào chọn trước SenOCR?** Khi tập tài liệu đa ngôn ngữ, cần một baseline tổng quát, hoặc SenOCR không cho lợi ích đủ rõ trên dữ liệu thật.

### 4. Chandra OCR 2 — thử khi chất lượng quan trọng hơn size

Chandra có điểm tiếng Việt **85,60** được dẫn trong card SenOCR, cao nhất trong các hàng ở bảng trên. Nếu tài liệu khó, phải xử lý handwriting, form hoặc bảng và có GPU phù hợp, đây là một **quality challenger** đáng benchmark. Card Chandra mô tả hỗ trợ các loại nội dung đó, nhưng đây vẫn là mô tả của nhà cung cấp. [Nguồn](wiki/chandra-ocr-2.md).

Tôi không xếp nó mặc định số một vì:

- Hàng điểm chưa được đối chiếu bằng cùng pipeline tính lại với SenOCR.
- Card SenOCR ghi **5B**, lớn hơn đáng kể các ứng viên khoảng 0,7–1B; con số này không tự cho biết VRAM hay latency thực tế.
- **License weights có hạn chế thương mại**, khác với Apache-2.0 được card SenOCR và Monkey mô tả. Cần kiểm tra điều khoản gốc cho tổ chức và mục đích sử dụng trước khi chọn. [Nguồn](wiki/chandra-ocr-2.md#licensing-and-trust-limits).

### 5. TeleOCR — ưu tiên khi bảng và ảnh chụp là bài toán chính

TeleOCR đáng thử khi tài liệu tiếng Việt có **bảng nhiều, trang cong hoặc chụp bằng điện thoại**. Kiến trúc của nó dùng polygon layout cho tài liệu chụp; trong bảng OmniDocBench do tác giả báo cáo, table TEDS của TeleOCR là **97,05**, so với **94,76** của PaddleOCR-VL-1.6. [Nguồn](wiki/teleocr.md#architecture-and-outputs), [báo cáo so sánh](outputs/so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md).

Tuy nhiên, đây là bằng chứng về benchmark tài liệu tổng quát, **không phải kết quả tiếng Việt**. Ngoài ra, paper ghi nhận sáu output Markdown không hợp lệ do lặp trên một đánh giá PureDocBench; vì vậy cần đo cả **trang lỗi, lặp và thiếu nội dung**, không chỉ điểm trung bình. [Nguồn](wiki/teleocr.md#reported-evaluation).

### 6. MiniCPM-OCR 1.0 và Xiaomi-OCR-0 — shortlist mở rộng

- **MiniCPM-OCR 1.0:** pipeline theo vùng rõ ràng, có SDK ghép trang và tùy chọn heuristic ghép bảng qua trang. Benchmark và throughput do vendor báo cáo khá tốt, nhưng model được mô tả chủ yếu cho **Trung/Anh**; wiki chưa có kết quả đủ để suy ra chất lượng tiếng Việt. Chọn thử khi cần pipeline theo vùng hoặc bảng nhiều trang. [Nguồn](wiki/minicpm-ocr-1-0.md).
- **Xiaomi-OCR-0:** model 0,8B, có cả whole-page và tùy chọn two-stage; card báo cáo Real5 cao. Nhưng chưa rõ cấu hình nào tạo điểm benchmark, và chưa có bằng chứng tiếng Việt đủ để xếp trên nhóm đầu. Nếu thử, hãy đo **riêng hai chế độ**; prompt whole-page được mô tả là bỏ header/footer. [Nguồn](wiki/xiaomi-ocr-0.md).

Tôi sẽ **không ưu tiên FalconOCR cho tiếng Việt** chỉ vì model nhỏ: bằng chứng trong báo cáo chủ yếu là tiếng Anh. Nếu bắt buộc CPU-only, có thể thử [Indra OCR](wiki/indra-ocr.md) như baseline cho tài liệu in sạch, nhưng cần đặc biệt kiểm tra dấu tiếng Việt; wiki ghi nhận hạn chế với một số ngôn ngữ Latin nhiều dấu, chữ viết tay và scan cũ, chứ không cung cấp kết quả riêng đủ để bảo đảm tiếng Việt.

## Tôi sẽ chạy thử thực tế như thế nào?

Nếu cần tiết kiệm thời gian, chạy **4 ứng viên đầu: SenOCR, MonkeyOCRv2-B, PaddleOCR-VL-1.6, TeleOCR**. Thêm Chandra nếu license và phần cứng cho phép.

1. **Chọn tập đại diện:** khoảng 20–50 PDF làm vòng sàng lọc, gồm văn bản in sạch, scan cũ, ảnh điện thoại, bảng, nhiều cột và chữ viết tay nếu thực sự có. Giữ riêng một tập kiểm tra cuối chưa dùng để chỉnh pipeline. Gợi ý chọn tài liệu khó thay vì chỉ PDF số đơn giản cũng phù hợp với [wiki về lựa chọn parser](wiki/pdf-to-markdown-tool-selection.md).
2. **Chạy cùng đầu vào và cấu hình được ghi lại:** cùng trang, độ phân giải render, phần cứng; lưu version, precision, prompt và cấu hình layout. Với SenOCR/Paddle, cố gắng giữ nguyên pipeline để tách tác động của recognition model.
3. **Chấm riêng các lỗi có ý nghĩa:**
   - **CER/WER có dấu**, quy định trước Unicode normalization và cách xử lý xuống dòng; không bỏ dấu khi chấm.
   - Tên riêng, địa danh, mã định danh, ngày tháng và số tiền: đo **exact match** riêng.
   - Bảng: cả nội dung ô lẫn hàng/cột, merged cells; reading order cho trang nhiều cột.
   - Tỷ lệ bỏ sót, sinh thêm/lặp, lỗi output và trang phải review; đo thêm latency, throughput, VRAM và chi phí.
4. **Chọn theo ngưỡng nghiệp vụ**, không chỉ composite: ví dụ model có CER tốt nhưng sai số tiền hoặc đảo hàng bảng vẫn có thể không phù hợp. Với hồ sơ pháp lý, tài chính hoặc dữ liệu quan trọng, giữ bước kiểm tra của con người.

**Chốt ngắn:** Nếu phải bắt đầu hôm nay, tôi sẽ triển khai thử **SenOCR-Vi và MonkeyOCRv2-B trước**, đồng thời dùng **PaddleOCR-VL-1.6 làm baseline**. Chọn model thắng trên dữ liệu Việt thực tế; thêm **Chandra** nếu cần đẩy chất lượng và chấp nhận license, hoặc **TeleOCR** nếu bảng/ảnh chụp là phần khó nhất.

---

**Phạm vi kiểm tra:** Tôi đã đọc báo cáo được yêu cầu và các trang wiki liên quan; không mở thêm `raw/`, truy cập web, tải model hay chạy OCR/benchmark trong lượt này. `python3 tools/wiki_check.py` báo **OK: 103 concepts, 1 index** — đây là kiểm tra cấu trúc, không xác minh benchmark. Nhiều trang liên quan ở trạng thái `draft`; các điểm trên là kết quả được nguồn công bố, chưa tái lập độc lập. Câu trả lời này để tạm thời trong hội thoại, không thay đổi wiki.

Ở câu trước, tôi dùng “không chọn” theo nghĩa **chưa đưa vào vòng thử đầu tiên**, không phải kết luận model đó OCR tiếng Việt kém hoặc không hỗ trợ tiếng Việt. Tôi ưu tiên những model có ít nhất một trong hai lợi thế: **bằng chứng trực tiếp trên tài liệu tiếng Việt** hoặc **vai trò baseline rõ ràng** để so sánh.

Dưới đây là lý do với các model còn lại **trong báo cáo layout-first mà bạn đưa**, cùng điều kiện khiến tôi đổi quyết định.

## 1. MinerU2.5-Pro — đáng thử, nhưng chưa có lý do xếp trước nhóm đầu cho tiếng Việt

Đây là model tôi thấy cần giải thích kỹ nhất vì nó vẫn là một lựa chọn mạnh.

- Trong bảng OmniDocBench của paper TeleOCR được báo cáo tổng hợp lại, MinerU2.5-Pro có **reading-order edit 0,120**, thấp nhất trong nhóm layout-first được chọn; vì vậy nó đáng chú ý với tài liệu nhiều cột hoặc cần thứ tự đọc tốt.
- Tuy nhiên, trong cùng bảng, overall và table TEDS của nó thấp hơn PaddleOCR-VL-1.6 và TeleOCR. Trong bảng Real5 từ report Paddle, điểm tổng hợp của MinerU2.5-Pro là **88,96**, so với **93,19** của PaddleOCR-VL-1.6. Những con số này là benchmark chung, **không phải benchmark riêng tiếng Việt**. [Nguồn bảng](outputs/so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md#2-so-sánh-chính-omnidocbench-v16-full).
- Model card mô tả khả năng ghép bảng qua trang nhưng quick-start lại nói tính năng đang tích hợp; wiki ghi đây là điểm **chưa thống nhất**, không nên mặc định tính năng đã hoạt động ở bản triển khai bạn dùng. [Nguồn](wiki/mineru2-5-pro.md#contradictions).

**Khi nào tôi sẽ đưa lên vòng đầu?** Bạn đang dùng MinerU, tài liệu có nhiều cột, hình/chart, hoặc cần JSON/Markdown theo hệ MinerU. Trong tình huống đó, tôi sẽ thử **MinerU2.5-Pro song song với Paddle và SenOCR**, thay vì loại nó.

## 2. GLM-OCR — có thế mạnh riêng, nhưng chưa đủ căn cứ ưu tiên cho OCR tiếng Việt

GLM-OCR cùng cỡ khoảng **0,9B** và có pipeline nhận dạng theo vùng. Tuy nhiên:

- Trong bảng OmniDocBench v1.6 được báo cáo tổng hợp từ paper TeleOCR, GLM thấp hơn PaddleOCR-VL-1.6 trên các cột được liệt kê; bảng Real5 được lưu cũng xếp GLM thấp hơn Paddle. Điều này chỉ là **tín hiệu chọn ứng viên**, không chứng minh GLM kém Paddle trên tiếng Việt.
- Trong tài liệu wiki đã kiểm tra, tôi chưa thấy benchmark tiếng Việt riêng đủ để đặt GLM trước SenOCR hay MonkeyOCRv2.
- Report GLM cũng nêu rủi ro với ngôn ngữ ít được đại diện, ảnh rất nhỏ hoặc biến dạng, bảng dày và bố cục bất thường. [Nguồn](wiki/glm-ocr.md#limitations-and-trust-limits).

**Khi nào chọn thử?** Nếu đầu ra chính là **KIE** — trích trường từ hóa đơn, biểu mẫu thành JSON — GLM có đường xử lý toàn trang theo schema riêng. Khi đó cần đánh giá **độ đúng từng trường**, không dùng điểm document parsing để kết luận. [Nguồn](wiki/glm-ocr.md#architecture-and-tasks).

## 3. Surya OCR 2 — có bằng chứng tiếng Việt, nhưng tôi vẫn xếp sau nhóm đầu

Đây là điểm tôi nên nói rõ hơn ở câu trước: wiki **có** ghi điểm tiếng Việt của Surya, không phải hoàn toàn thiếu dữ liệu. Một benchmark nội bộ của nhà cung cấp báo cáo **73,2% cho tiếng Việt**. Nhưng đó là benchmark khác MDPBench; không thể đem 73,2 so trực tiếp với 82,83 của SenOCR. [Nguồn](wiki/hybrid-ocr-systems-and-benchmarks.md).

Lý do chưa ưu tiên:

- Điểm tiếng Việt là **vendor-internal**, không có đủ phương pháp để so ngang nhóm đầu.
- Surya có block mode và output gồm polygon, bounding box, thứ tự đọc; đó là lợi thế, nhưng cần tự kiểm tra độ đúng trên trang tiếng Việt. [Nguồn](wiki/surya-ocr-2.md#capabilities-and-outputs).
- Weights có **điều khoản thương mại hạn chế**, nên tính khả thi phụ thuộc tổ chức và mục đích dùng. [Nguồn](wiki/surya-ocr-2.md#licensing-and-trust-limits).

**Khi nào chọn thử?** Khi bạn cần **tọa độ, confidence, HTML table**, hoặc muốn chạy trên CPU/Apple Silicon theo các đường inference mà card mô tả. Tôi sẽ đưa Surya vào shortlist nếu các yêu cầu đó quan trọng hơn điểm benchmark tổng hợp.

## 4. PP-StructureV3 — hợp khi cần pipeline modular, nhưng không phải mặc định cho ảnh khó

PP-StructureV3 không phải một model đơn mà là **pipeline nhiều thành phần**: OCR, layout, bảng, công thức, chart và hậu xử lý reading order. Điều này hữu ích khi cần kiểm soát từng khâu. [Nguồn](wiki/pp-structurev3.md#pipeline).

Tôi chưa ưu tiên nó cho bài toán chưa rõ dữ liệu của bạn vì:

- Kết quả tiếng Việt riêng chưa có trong trang wiki tôi kiểm tra.
- Bảng Real5 trong báo cáo tổng hợp ghi **64,45 overall**, thấp hơn đáng kể PaddleOCR-VL-1.6 ở **93,19**, đặc biệt trên lệch góc. Đây là kết quả do nguồn báo cáo trên benchmark đó, **không chứng minh khoảng cách tương tự trên mọi scan tiếng Việt**. [Nguồn](outputs/so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md#real5-omnidocbench-cùng-bảng-trong-report-paddleocr-vl-16).
- Nhiều thành phần cũng đồng nghĩa cần kiểm tra cấu hình recognizer, layout và post-processing thực tế; tổng số parameter của pipeline chưa được xác định rõ trong nguồn đã lưu.

**Khi nào chọn thử?** Nếu bạn muốn **thay hoặc fine-tune từng module**, cần output có cấu trúc từ pipeline chuyên biệt, hoặc tài liệu chủ yếu là bản in sạch và yêu cầu tài nguyên khác với VLM.

## 5. FalconOCR — nhỏ, nhưng bằng chứng đang thiên về tiếng Anh

FalconOCR có recognizer **0,3B**, là lựa chọn hấp dẫn về size. Tuy nhiên, nguồn mô tả model tập trung tiếng Anh; các bảng benchmark được lưu đã lọc tài liệu không phải tiếng Anh. [Nguồn](wiki/falcon-ocr.md#reported-evaluation).

Do đó tôi không có cơ sở dùng điểm tốt trên tiếng Anh để khẳng định model đọc đúng **dấu thanh, nguyên âm có dấu, tên người và địa danh Việt Nam**.

**Khi nào chọn thử?** Khi model size là ràng buộc rất cứng, tài liệu phần lớn tiếng Anh hoặc song ngữ, và bạn sẵn sàng kiểm chứng tiếng Việt trên tập thực tế. Lưu ý **0,3B là recognizer**, không mặc nhiên là tổng chi phí cả pipeline layout.

## 6. Indra OCR — phương án CPU, nhưng có rủi ro với dấu và tài liệu khó

Indra là lựa chọn khác nhóm VLM: pipeline CPU/ONNX, có thể tận dụng text layer của PDF. Vì vậy nó có giá trị nếu ưu tiên tốc độ, chi phí và triển khai nhẹ. [Nguồn](wiki/indra-ocr.md#pipeline-as-documented).

Tôi không chọn nó làm mặc định cho OCR tiếng Việt vì nguồn đã lưu:

- Không cung cấp kết quả tiếng Việt riêng mà tôi có thể dùng để đánh giá độ chính xác dấu.
- Nêu lỗi dấu ở một số ngôn ngữ Latin nhiều dấu, đồng thời thừa nhận chất lượng hạn chế trên chữ viết tay, scan cũ và bảng phức tạp. Điều này **không chứng minh tiếng Việt sẽ gặp cùng mức lỗi**, nhưng đủ để yêu cầu kiểm thử kỹ. [Nguồn](wiki/indra-ocr.md#limitations).
- Chế độ mặc định có thể đọc text layer; nếu so với model OCR ảnh, phải ghi rõ trang nào đi qua text layer và trang nào thực sự OCR.

**Khi nào chọn thử?** CPU-only, số lượng lớn, bản in sạch hoặc PDF có text layer tốt. Tôi sẽ dùng Indra như **baseline chi phí thấp**, rồi chuyển trang khó sang model lớn hơn nếu benchmark nội bộ cho thấy cách đó khả thi.

## 7. OXR-1.0 — chưa đủ thông tin để xếp hạng

OXR có ý tưởng hấp dẫn: layout model có thể thay thế, output Markdown/JSON kèm tọa độ và nhiều loại vùng. Nhưng nguồn lưu cục bộ không có đầy đủ **vector điểm, phiên bản benchmark, điều kiện thử hay license gốc**; cũng chưa mô tả đủ luồng trung gian để xác định chắc mức độ tương đồng với pipeline layout-first trong báo cáo. [Nguồn](wiki/oxr-1-0.md).

Vì vậy tôi chưa xếp OXR cao **không phải do có bằng chứng nó yếu**, mà do **không đủ thông tin so sánh và đánh giá triển khai**.

**Khi nào chọn thử?** Khi bạn cần thử layout model thay thế, có GPU đáp ứng yêu cầu mà README mô tả và đã kiểm tra license gốc, privacy, cùng kết quả trên dữ liệu Việt.

## 8. Các phiên bản cũ: MinerU2.5, PaddleOCR-VL và PaddleOCR-VL-1.5

Tôi không ưu tiên các phiên bản này cho một **triển khai mới**, vì trong tài liệu đã lưu chúng có phiên bản kế tiếp:

- **MinerU2.5 → MinerU2.5-Pro**
- **PaddleOCR-VL → PaddleOCR-VL-1.5 → PaddleOCR-VL-1.6**

Các bảng trong báo cáo nhìn chung cho thấy phiên bản mới hơn tốt hơn trên những benchmark được nêu. Nhưng **phiên bản mới hơn không bảo đảm tốt hơn trên mọi tài liệu tiếng Việt hoặc mọi phần cứng**. [Nguồn tổng hợp](outputs/so-sanh-cac-model-ocr-theo-huong-layout-first-modular.md#1-danh-sách-model-thời-điểm-và-kích-thước).

**Khi nào vẫn chọn bản cũ?** Bạn đã có pipeline ổn định, bản mới không tương thích, có ràng buộc latency/VRAM, hoặc benchmark nội bộ cho thấy bản cũ ít lỗi hơn trên tài liệu của bạn.

## Tóm tắt quyết định

| Model chưa ưu tiên vòng đầu | Lý do chính | Điều kiện nên đưa trở lại shortlist |
|---|---|---|
| **MinerU2.5-Pro** | Thiếu bằng chứng riêng tiếng Việt để ưu tiên hơn; ảnh biến dạng trong bảng Real5 thấp hơn Paddle | Nhiều cột, dùng hệ MinerU, cần thử reading order |
| **GLM-OCR** | Chưa có căn cứ tiếng Việt trực tiếp; bảng tổng quát chưa tạo lợi thế rõ so với Paddle | KIE, trích xuất trường theo schema |
| **Surya OCR 2** | Có điểm Việt nhưng là benchmark nội bộ khác protocol; license cần xem | Cần box/polygon, HTML, CPU/Apple Silicon |
| **PP-StructureV3** | Chưa có kết quả Việt riêng; bảng Real5 lưu cho thấy điểm ảnh khó thấp | Cần pipeline modular, tùy biến từng khâu |
| **FalconOCR** | Bằng chứng đánh giá chủ yếu tiếng Anh | Ràng buộc size rất chặt; tài liệu chủ yếu tiếng Anh |
| **Indra OCR** | Chưa có điểm Việt riêng; cần kiểm tra dấu, handwriting và scan cũ | CPU-only, bản in sạch, cần baseline nhanh |
| **OXR-1.0** | Thiếu protocol, điểm chi tiết và license gốc | Có thời gian tự benchmark và thẩm định triển khai |
| **Các bản cũ** | Đã có bản kế tiếp để thử trước | Tương thích, chi phí, hoặc kết quả nội bộ tốt hơn |

**Điều chỉnh so với câu trước:** nếu bạn muốn một vòng benchmark rộng hơn thay vì chỉ bốn model, tôi sẽ thêm **MinerU2.5-Pro và Surya OCR 2** trước các ứng viên còn lại — MinerU vì reading order và hệ sinh thái; Surya vì có kết quả tiếng Việt được báo cáo và output tọa độ hữu ích. Đây vẫn là **thứ tự ưu tiên thử**, không phải bảng xếp hạng chất lượng tiếng Việt đã xác minh.

*Giới hạn: câu trả lời dựa trên báo cáo và wiki đã đọc; không mở thêm raw hay chạy model/benchmark. “Chưa có bằng chứng trong phần đã kiểm tra” không có nghĩa là model không hỗ trợ tiếng Việt.*