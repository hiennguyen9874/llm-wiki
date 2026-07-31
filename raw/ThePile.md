## Tổng quan bài báo

**“The Pile: An 800GB Dataset of Diverse Text for Language Modeling”** là bài báo của Leo Gao, Stella Biderman, Sid Black và các cộng sự thuộc EleutherAI, được công bố dưới dạng bản thảo arXiv vào ngày **31/12/2020**. Công trình giới thiệu **The Pile**, một tập dữ liệu văn bản tiếng Anh quy mô **825 GiB**, được thiết kế để tiền huấn luyện các mô hình ngôn ngữ lớn. ([arXiv][1])

Tên bài báo dùng “800GB” theo cách gọi làm tròn; kích thước thực tế được nhóm tác giả báo cáo là khoảng **825 GiB**.

## 1. Vấn đề bài báo muốn giải quyết

Trước The Pile, nhiều mô hình ngôn ngữ chủ yếu được huấn luyện trên dữ liệu web tổng quát như Common Crawl. Loại dữ liệu này rất lớn nhưng có một số nhược điểm:

* Chất lượng văn bản không đồng đều.
* Chứa nhiều nội dung lặp, spam hoặc văn bản được trích xuất kém.
* Thiếu các miền chuyên môn như khoa học, luật, toán học và mã nguồn.
* Mô hình có thể làm tốt trên văn bản web thông thường nhưng yếu ở văn bản học thuật hoặc chuyên ngành.

Giả thuyết trung tâm của bài báo là:

> Không chỉ kích thước, mà **sự đa dạng và chất lượng của dữ liệu tiền huấn luyện** cũng quyết định khả năng khái quát hóa của mô hình.

Do đó, nhóm tác giả xây dựng một corpus kết hợp nhiều kiểu văn bản, thay vì phụ thuộc gần như hoàn toàn vào dữ liệu web.

## 2. The Pile gồm những gì?

The Pile kết hợp **22 tập dữ liệu thành phần**. Mỗi tài liệu thường có hai trường chính:

```text
text: nội dung văn bản
meta: thông tin nguồn hoặc tập dữ liệu thành phần
```

Ví dụ, metadata có thể chỉ ra tài liệu đến từ Pile-CC, GitHub, PubMed hay Stack Exchange. Tập dữ liệu có các phần train, validation và test. ([Hugging Face][2])

### Các thành phần lớn nhất

| Thành phần     | Nội dung                           | Kích thước thô | Tỷ trọng sau lấy mẫu |
| -------------- | ---------------------------------- | -------------: | -------------------: |
| Pile-CC        | Dữ liệu web đã lọc từ Common Crawl |     227.12 GiB |               18.11% |
| PubMed Central | Toàn văn bài báo y sinh            |      90.27 GiB |               14.40% |
| Books3         | Sách                               |     100.96 GiB |               12.07% |
| OpenWebText2   | Trang web được liên kết từ Reddit  |      62.77 GiB |               10.01% |
| arXiv          | Bài báo khoa học                   |      56.21 GiB |                8.96% |
| GitHub         | Mã nguồn và tài liệu kỹ thuật      |      95.16 GiB |                7.59% |
| FreeLaw        | Ý kiến và hồ sơ pháp lý            |      51.15 GiB |                6.12% |
| Stack Exchange | Hỏi đáp chuyên môn                 |      32.20 GiB |                5.13% |

Các thành phần còn lại bao gồm USPTO Backgrounds, PubMed Abstracts, Project Gutenberg, OpenSubtitles, Wikipedia tiếng Anh, DeepMind Mathematics, Ubuntu IRC, BookCorpus2, EuroParl, Hacker News, phụ đề YouTube, PhilPapers, NIH ExPorter và Enron Emails. ([GitHub][3])

Nhìn theo loại nội dung, The Pile bao phủ:

* **Web:** Pile-CC, OpenWebText2, Hacker News.
* **Khoa học:** arXiv, PubMed, PhilPapers.
* **Lập trình:** GitHub, Stack Exchange, Ubuntu IRC.
* **Luật và hành chính:** FreeLaw, USPTO, NIH ExPorter.
* **Sách và văn học:** Books3, BookCorpus2, Gutenberg.
* **Hội thoại và ngôn ngữ đời thường:** phụ đề phim, phụ đề YouTube, email Enron.
* **Toán học:** DeepMind Mathematics.
* **Tri thức bách khoa:** Wikipedia.

Đây là đặc điểm quan trọng nhất của The Pile: nó không xem “văn bản Internet” là một miền dữ liệu đồng nhất.

## 3. Cách phối trộn dữ liệu

Nhóm tác giả không đơn giản nối 22 tập dữ liệu với nhau. Họ gán cho mỗi thành phần một **trọng số lấy mẫu**, thể hiện qua số “epoch” mà dữ liệu đó được lặp lại.

Ví dụ:

* Pile-CC: 1 epoch.
* PubMed Central: 2 epoch.
* arXiv: 2 epoch.
* Wikipedia: 3 epoch.
* Project Gutenberg: 2.5 epoch.
* Books3: 1.5 epoch.

Điều này khiến những tập nhỏ nhưng được đánh giá là giàu thông tin, như Wikipedia hoặc PhilPapers, xuất hiện nhiều lần hơn tương đối so với kích thước ban đầu. Sau khi áp dụng trọng số, lượng dữ liệu “hiệu dụng” của hỗn hợp được mô tả là khoảng **1.25 TiB cho một chu kỳ phối trộn hoàn chỉnh**. ([GitHub][3])

Có thể hiểu đây là một dạng **data curriculum tĩnh**: nhóm nghiên cứu chủ động quyết định mô hình nên nhìn thấy bao nhiêu dữ liệu từ từng miền.

## 4. Quy trình xử lý

Tùy từng nguồn, nhóm tác giả thực hiện các bước khác nhau:

### Chuẩn hóa

Dữ liệu được chuyển về một định dạng thống nhất để có thể trộn, xáo trộn và đọc theo luồng trong quá trình huấn luyện.

### Lọc chất lượng

Các nguồn web như Pile-CC và OpenWebText2 được xử lý để loại bỏ:

* HTML hoặc thành phần không phải văn bản.
* Trang chất lượng thấp.
* Một số loại nội dung spam.
* Dữ liệu không phù hợp với tiêu chí của corpus.

Tuy nhiên, mức độ lọc không giống nhau giữa các thành phần. Một bài báo khoa học từ arXiv có cấu trúc và chất lượng tương đối rõ ràng, trong khi dữ liệu web cần nhiều heuristic hơn.

### Khử trùng lặp

Nhóm tác giả áp dụng deduplication nhằm hạn chế các tài liệu giống hoặc gần giống nhau. Việc này có hai mục đích:

1. Tránh mô hình ghi nhớ quá mức các nội dung được lặp lại.
2. Giảm nguy cơ dữ liệu kiểm thử xuất hiện trong tập huấn luyện.

Dù vậy, bài báo không khẳng định rằng toàn bộ trùng lặp hoặc rò rỉ benchmark đã được loại bỏ hoàn toàn.

### Xáo trộn và phối trộn

Các tập thành phần được xáo trộn và interleave theo trọng số đã thiết lập. Mã nguồn tái tạo quy trình này được công bố trong kho GitHub của dự án. ([GitHub][3])

## 5. Phương pháp đánh giá

Bài báo tiến hành hai nhóm thí nghiệm chính.

### Đánh giá mô hình có sẵn trên từng thành phần

Nhóm nghiên cứu đo khả năng mô hình hóa từng miền của GPT-2 và GPT-3 thông qua **perplexity**.

Perplexity thấp hơn thường cho thấy mô hình dự đoán văn bản tốt hơn. Tuy nhiên, khi so sánh giữa các tập dữ liệu có kiểu văn bản hoặc quá trình tiền xử lý khác nhau, perplexity cần được diễn giải cẩn thận.

Kết quả cho thấy các mô hình có sẵn gặp nhiều khó khăn với một số miền của The Pile, đặc biệt là:

* Văn bản khoa học.
* Văn bản học thuật.
* Tài liệu pháp lý.
* Mã nguồn.
* Nội dung toán học hoặc kỹ thuật.

Điều này củng cố lập luận rằng dữ liệu web phổ thông không đủ để mô hình học tốt tất cả các miền tri thức. ([arXiv][1])

### Huấn luyện mô hình trên các corpus khác nhau

Nhóm tác giả huấn luyện các mô hình có kiến trúc tương đương trên:

* The Pile.
* Raw Common Crawl.
* CC-100.

Sau đó, họ so sánh hiệu quả trên từng thành phần của The Pile và trên các tác vụ downstream.

Kết luận chính là mô hình huấn luyện trên The Pile:

* Đạt perplexity tốt hơn trên tất cả hoặc gần như tất cả các miền thành phần.
* Cải thiện trên các đánh giá downstream.
* Không chỉ giỏi hơn ở văn bản chuyên ngành mà vẫn giữ được khả năng trên văn bản tổng quát.

Theo nhóm tác giả, kết quả này cho thấy **corpus đa miền được tuyển chọn** có thể hiệu quả hơn một corpus web thô có quy mô tương tự. ([arXiv][1])

## 6. Đóng góp quan trọng

Bài báo có bốn đóng góp nổi bật.

### Một corpus mở, đủ lớn cho LLM

Vào thời điểm công bố, phần lớn corpus dùng cho những mô hình rất lớn không được phát hành công khai. The Pile cung cấp một tập dữ liệu có quy mô đủ lớn để cộng đồng độc lập huấn luyện các mô hình hàng tỷ tham số.

### Đưa dữ liệu chuyên ngành vào tiền huấn luyện

The Pile khiến việc đưa khoa học, y sinh, luật, toán và mã nguồn vào một corpus chung trở thành một lựa chọn có hệ thống, thay vì bổ sung tùy ý.

### Chứng minh vai trò của thành phần dữ liệu

Bài báo giúp chuyển sự chú ý từ câu hỏi:

> “Mô hình cần bao nhiêu dữ liệu?”

sang câu hỏi:

> “Dữ liệu đó đến từ đâu, có chất lượng ra sao và được phối trộn như thế nào?”

### Công bố mã xây dựng

Kho mã chính thức được thiết kế để người dùng có thể tái tạo hoặc xây dựng các biến thể của The Pile. ([GitHub][3])

## 7. Hạn chế và vấn đề đạo đức

Đây cũng là phần cần đọc kỹ nhất của công trình.

### Chủ yếu là tiếng Anh

Phiên bản đầu tiên được định hướng là corpus tiếng Anh. Vì vậy, nó không đại diện tốt cho sự đa dạng ngôn ngữ toàn cầu. Kho mã dự án cũng nói rõ các đề xuất dữ liệu không phải tiếng Anh được hoãn cho các phiên bản tương lai. ([GitHub][3])

### Thiên kiến xã hội

Dữ liệu lấy từ Internet, sách, diễn đàn và tài liệu lịch sử có thể chứa:

* Phân biệt giới tính.
* Phân biệt chủng tộc.
* Thành kiến tôn giáo.
* Ngôn ngữ xúc phạm.
* Quan điểm chính trị hoặc văn hóa mất cân đối.

Nhóm tác giả phân tích một số đặc điểm đáng lo ngại của dữ liệu, nhưng không tuyên bố đã loại bỏ hoàn toàn các thiên kiến này. ([arXiv][1])

### Dữ liệu cá nhân và nhạy cảm

Những thành phần như email Enron, diễn đàn, IRC hoặc dữ liệu web có thể chứa tên, địa chỉ liên hệ và thông tin cá nhân. “Công khai trên Internet” không đồng nghĩa với việc người tạo nội dung đã đồng ý cho dữ liệu được dùng để huấn luyện mô hình.

### Giấy phép không đồng nhất

The Pile là một **tập hợp nhiều nguồn**, không phải toàn bộ 825 GiB đều có một giấy phép thống nhất. Dataset card yêu cầu người dùng xem giấy phép của từng thành phần cụ thể. ([Hugging Face][2])

### Books3 và tranh chấp bản quyền

Books3 bao gồm một lượng lớn sách và về sau trở thành tâm điểm của các tranh luận, yêu cầu gỡ bỏ và kiện tụng liên quan đến dữ liệu huấn luyện AI. Đây là diễn biến sau khi bài báo gốc được công bố, nhưng nó cho thấy một hạn chế lớn của quan niệm “dữ liệu mở”: dữ liệu có thể được truy cập công khai mà vẫn không có quyền rõ ràng để tái phân phối hoặc sử dụng cho huấn luyện.

Vì thế, hiện nay không nên hiểu “open source dataset” trong bài báo là “mọi tài liệu bên trong đều được cấp phép mở”.

## 8. Ảnh hưởng của The Pile

The Pile đã được sử dụng để huấn luyện hoặc nghiên cứu nhiều họ mô hình mở, tiêu biểu như GPT-Neo, GPT-J, GPT-NeoX và Pythia. Trang dữ liệu của Hugging Face hiện liệt kê hàng trăm mô hình liên quan tới corpus này. ([Hugging Face][2])

Ảnh hưởng lớn hơn của công trình nằm ở phương pháp luận:

* Corpus nên được mô tả theo từng nguồn.
* Tỷ lệ phối trộn là một siêu tham số quan trọng.
* Dữ liệu chuyên ngành có thể cải thiện năng lực tổng quát.
* Cần phát hành datasheet, mã xử lý và phân tích rủi ro.
* Quyền sử dụng dữ liệu phải được xem xét riêng, không thể suy ra chỉ từ khả năng truy cập.

## 9. Đánh giá tổng quát

**Điểm mạnh**

* Quy mô rất lớn tại thời điểm công bố.
* Thành phần đa dạng và có chủ đích.
* Bao gồm nhiều dữ liệu chuyên môn chất lượng cao.
* Có thí nghiệm so sánh với Common Crawl.
* Công bố mã xây dựng và phân tích dữ liệu tương đối chi tiết.

**Điểm yếu**

* Chỉ tập trung chủ yếu vào tiếng Anh.
* Trọng số phối trộn phần nào dựa trên lựa chọn thủ công.
* Chất lượng và giấy phép không đồng đều giữa các nguồn.
* Khử trùng lặp và loại bỏ dữ liệu benchmark không tuyệt đối.
* Chứa nội dung độc hại, thông tin cá nhân và tài liệu có tình trạng bản quyền gây tranh cãi.
* Đánh giá thực nghiệm chưa thể tách hoàn toàn ảnh hưởng của chất lượng, miền dữ liệu và mức độ lặp lại.

## Kết luận

Thông điệp quan trọng nhất của bài báo không đơn giản là “hãy dùng 800GB dữ liệu”. Đó là:

> **Việc lựa chọn, làm sạch và phối trộn nhiều miền dữ liệu có thể quan trọng không kém việc tăng kích thước mô hình hoặc tăng tổng lượng dữ liệu.**

The Pile là một cột mốc quan trọng đối với phong trào mô hình ngôn ngữ mở. Đồng thời, những tranh luận sau đó về Books3, quyền riêng tư và giấy phép cho thấy xây dựng dữ liệu LLM không chỉ là một bài toán kỹ thuật, mà còn là bài toán pháp lý và đạo đức.

[1]: https://arxiv.org/abs/2101.00027?utm_source=chatgpt.com "The Pile: An 800GB Dataset of Diverse Text for Language Modeling"
[2]: https://huggingface.co/datasets/EleutherAI/pile "EleutherAI/pile · Datasets at Hugging Face"
[3]: https://github.com/EleutherAI/the-pile "GitHub - EleutherAI/the-pile · GitHub"
