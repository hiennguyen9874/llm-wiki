Mình đã rà các thảo luận Reddit gần đây, repo chính thức và một benchmark học thuật năm 2026. Nếu mục tiêu của bạn là **PDF → Markdown chất lượng cao, giữ cấu trúc/table/formula và tách ảnh ra folder riêng**, thì mình sẽ xếp:

**🥇 MinerU ≈ Marker > Docling > OpenDataLoader-PDF** về *chất lượng Markdown tổng quát*.
Nhưng nếu ưu tiên **CPU + tốc độ cực cao + số lượng PDF rất lớn**, OpenDataLoader-PDF lại rất đáng chú ý.

### So sánh nhanh

| Thư viện           | Markdown | Table | Formula |    Scan/OCR |            Extract ảnh riêng | Tốc độ / tài nguyên  | Mình chọn khi           |
| ------------------ | -------: | ----: | ------: | ----------: | ---------------------------: | -------------------- | ----------------------- |
| **MinerU**         |    ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |   ⭐⭐⭐⭐⭐ |       ⭐⭐⭐⭐⭐ |                **✅ rất tốt** | Khá nặng, GPU có lợi | PDF khó, paper, sách    |
| **Marker**         |    ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐½ |   ⭐⭐⭐⭐⭐ |       ⭐⭐⭐⭐½ |                 **✅ rất dễ** | GPU tốt, CPU được    | PDF → MD thực dụng      |
| **Docling**        |    ⭐⭐⭐⭐½ | ⭐⭐⭐⭐⭐ |    ⭐⭐⭐⭐ |       ⭐⭐⭐⭐½ | **✅** nhưng config nhiều hơn | CPU khá ổn           | RAG / document pipeline |
| **OpenDataLoader** |     ⭐⭐⭐⭐ |  ⭐⭐⭐⭐ |    ⭐⭐⭐½ | ⭐⭐⭐⭐ hybrid |                            ✅ | **🚀 rất nhanh CPU** | Bulk processing / RAG   |

## 🥇 MinerU — lựa chọn mình nghiêng về nhất cho yêu cầu của bạn

[MinerU GitHub](https://github.com/opendatalab/MinerU?utm_source=chatgpt.com)

Điểm MinerU hợp với yêu cầu của bạn nhất là **output structure gần như đúng thứ bạn đang cần**:

```text
output/
└── document/
    └── auto/
        ├── document.md
        ├── document_content_list.json
        ├── document_middle.json
        └── images/
            ├── xxx.jpg
            ├── yyy.jpg
            └── ...
```

Markdown sử dụng relative path tới `images/`, nên có thể di chuyển nguyên folder sang Obsidian/RAG pipeline khá tiện. ([DocCompiler][1])

Ví dụ:

```markdown
## Architecture

The proposed architecture consists of...

![](images/a93f23c1.jpg)

### Experimental Results

| Model | Accuracy |
|---|---:|
| Model A | 92.3 |
```

Trên Reddit có một thread khá đúng use case của bạn: người dùng đã thử **LlamaParse, Docling, PyMuPDF4LLM, Unstructured... rồi chuyển sang MinerU** và nhận xét MinerU cho kết quả tốt nhất rõ rệt trong thử nghiệm của họ. ([Reddit][2])

Một thread tháng 6/2026 hỏi thẳng **MinerU vs Marker vs Docling** cho PDF có image + equation cũng có người chọn MinerU, trong khi người dùng Marker nói Marker có chất lượng tốt nhưng MinerU có thể tốt hơn ở một số trường hợp và cần nhiều tài nguyên hơn. ([Reddit][3])

**Nếu PDF của bạn là sách, paper, báo cáo kỹ thuật, nhiều công thức/table/multi-column → mình chọn MinerU đầu tiên.**

---

## 🥈 Marker — có thể là lựa chọn thực dụng nhất

[Marker GitHub](https://github.com/datalab-to/marker?utm_source=chatgpt.com)

Marker rất sát yêu cầu của bạn:

> PDF → `.md` + images

Repo chính thức ghi rõ Marker hỗ trợ table, form, equation, inline math, link, reference, code và **extract + save images**. Markdown tạo ra chứa image link và các ảnh được lưu cùng output. Marker chạy được GPU, CPU và Apple MPS. ([GitHub][4])

CLI cũng cực đơn giản:

```bash
marker_single input.pdf \
    --output_format markdown \
    --output_dir ./output
```

Một Reddit thread tháng 4/2026 mô tả Marker khá đúng nhu cầu của bạn: người dùng đánh giá nó giữ format, extract picture, hỗ trợ batch và nhanh. ([Reddit][5])

Một thảo luận self-hosted khác đưa ra heuristic khá hay:

**Marker cho everyday PDF, MinerU cho heavy science/math.** ([Reddit][6])

Mình khá đồng ý với cách chia này.

Marker còn có tùy chọn LLM/VLM để sửa những block khó. Vì vậy pipeline có thể đi từ:

```text
PDF
 ↓
Marker
 ↓
Markdown + images
 ↓
(optional)
LLM semantic cleanup
```

Một người dùng Reddit năm 2026 đang chạy đúng kiểu **Marker → Ollama/Qwen → semantic correction**, hoàn toàn local. ([Reddit][3])

**Nếu bạn muốn cài nhanh, API/CLI dễ, Markdown đẹp, ảnh tách sẵn → Marker có thể là lựa chọn dễ chịu nhất.**

---

## 🥉 Docling — rất mạnh nhưng mình không chọn #1 chỉ để PDF → MD

[Docling GitHub](https://github.com/docling-project/docling?utm_source=chatgpt.com)

Docling mạnh ở **document understanding**, đặc biệt table/layout, và hỗ trợ rất nhiều format ngoài PDF. Nó có unified `DoclingDocument`, OCR, VLM pipeline, layout analysis và table understanding. ([GitHub][7])

Điểm quan trọng: **Docling hoàn toàn có thể làm đúng yêu cầu tách ảnh của bạn**.

Nó hỗ trợ:

```text
image_mode =
    placeholder
    embedded
    referenced
```

`referenced` sẽ xuất PNG riêng và Markdown reference tới file đó. ([GitHub][8])

Repo thậm chí có example riêng:

```python
element.get_image(conv_res.document).save(...)

conv_res.document.save_as_markdown(
    md_filename,
    image_mode=ImageRefMode.REFERENCED
)
```

cho cả **figure và table image**. ([GitHub][9])

Điểm đáng chú ý là một nghiên cứu 2026 so sánh trực tiếp **Docling, MinerU, Marker và DeepSeek OCR** trên pipeline RAG. Trong benchmark cụ thể đó, **Docling + hierarchical splitting + image descriptions đạt accuracy tự động cao nhất: 94.1%**, so với manual Markdown 97.1%. Tuy nhiên nghiên cứu cũng phát hiện cách chunking, metadata và preprocessing ảnh hưởng kết quả RAG còn lớn hơn việc chọn parser nào. ([arXiv][10])

Nói cách khác:

**Nếu output Markdown chỉ là bước trung gian để đưa vào RAG → Docling cực kỳ đáng cân nhắc.**

Nếu mục tiêu đơn giản là:

> “Cho tôi `.md` đẹp + folder images.”

thì Marker/MinerU ít friction hơn.

---

## OpenDataLoader-PDF — dark horse rất thú vị

[OpenDataLoader-PDF GitHub](https://github.com/opendataloader-project/opendataloader-pdf?utm_source=chatgpt.com)

Project này mới hơn và đang phát triển rất nhanh. Điểm khác biệt là nó có **deterministic/rule-based mode chạy CPU**, correct reading order cho multi-column bằng XY-Cut++, table extraction và bounding boxes. Ngoài ra có hybrid mode cho OCR/table khó. ([GitHub][11])

Điểm hấp dẫn nhất:

```text
PDF
 ↓
CPU
 ↓
100+ pages/sec (claimed)
 ↓
Markdown + JSON
```

Không cần GPU trong deterministic mode. ([PyPI][12])

Nhưng mình **không lấy benchmark do chính OpenDataLoader công bố để kết luận rằng nó “đánh bại” Marker/MinerU/Docling**. Repo của họ báo hybrid đạt overall 0.907 so với Docling 0.882 và Marker 0.861, nhưng đó là benchmark do chính project cung cấp, nên nên xem như một datapoint chứ không phải kết luận độc lập. ([GitHub][11])

Ngoài ra project vẫn có những issue thực tế như table Markdown bị thiếu data ở một số trường hợp. ([GitHub][13])

Nếu bạn có **100.000 PDF và CPU farm**, mình sẽ benchmark OpenDataLoader rất nghiêm túc.

Nếu bạn có **500 PDF khó và muốn Markdown đẹp nhất**, mình vẫn bắt đầu từ MinerU/Marker.

---

# Cộng đồng Reddit đang nghiêng về cái nào?

Không có một winner tuyệt đối.

Các thread gần đây cho thấy ba nhóm khá rõ:

**MinerU:** thường được khen khi PDF phức tạp, technical/scientific, OCR/layout khó. ([Reddit][2])

**Marker:** được nhiều người dùng thực tế chọn cho PDF → Markdown hàng ngày vì output tốt, giữ format và extract ảnh thuận tiện. ([Reddit][5])

**Docling:** cũng có fan rất mạnh; có người đơn giản nói chọn Docling và dùng ổn, và thread về complex PDF cũng có người đánh giá Docling rất tốt. ([Reddit][14])

Một thread tháng 6/2026 tóm khá đúng tình hình: cùng một câu hỏi thì có người bảo **MinerU best**, người khác đã bỏ Docling để dùng Marker, trong khi người khác lại nói **Docling and never look back**. ([Reddit][3])

Vì vậy không có “community consensus” kiểu 80% chọn một tool.

---

# Với đúng yêu cầu của bạn, mình sẽ chọn thế này

Nếu requirement là:

```text
PDF
│
├── document.md
│
└── images/
    ├── image_001.png
    ├── image_002.png
    └── ...
```

và Markdown phải giữ:

```text
heading
paragraph
table
equation
image
caption
reading order
```

thì thứ tự mình **benchmark trước** sẽ là:

**1. MinerU — chất lượng extraction tổng thể**

**2. Marker — DX tốt nhất / dễ triển khai**

**3. Docling — nếu sau đó làm RAG**

**4. OpenDataLoader — nếu throughput CPU là ưu tiên lớn**

Nếu chỉ được chọn **một** cho dự án của bạn ngay bây giờ: **MinerU**.

Nếu MinerU quá nặng hoặc deployment phiền: **Marker**.

Một lưu ý quan trọng: mình sẽ **không benchmark bằng PDF text đơn giản**. Nên lấy khoảng 20–50 PDF thật của bạn, cố tình gồm 2-column, scanned, table có merged cells, công thức, chart/figure + caption, header/footer và PDF tiếng Việt. Chính tập dữ liệu của bạn mới quyết định MinerU hay Marker thắng; khác biệt giữa các loại tài liệu khá lớn.

Nếu bạn muốn, mình có thể tiếp tục **đào benchmark GitHub/Reddit sâu hơn và làm bảng MinerU vs Marker chi tiết về VRAM/RAM, tốc độ pages/s, Docker, license, OCR tiếng Việt, table/formula và code Python để batch `PDF → md + images/`**, rồi chốt luôn stack nên dùng cho production.

[1]: https://doccompiler.ai/api/v1/jobs/shared/job_1776340060874_e7a4ed24/download/opendatalab__MinerU__UserGuide.pdf?utm_source=chatgpt.com "DocCompiler.ai"
[2]: https://www.reddit.com/r/Rag/comments/1jo6vnb/thoughts_on_mineru_for_pdftomarkdown/?utm_source=chatgpt.com "Thoughts on MinerU for pdf-to-markdown?"
[3]: https://www.reddit.com/r/Markdown/comments/1u4vgec/which_pdf_to_md_converter_to_use/?utm_source=chatgpt.com "Which PDF to MD converter to use?"
[4]: https://github.com/datalab-to/marker/blob/master/README.md?plain=1&utm_source=chatgpt.com "marker/README.md at master · datalab-to/marker · GitHub"
[5]: https://www.reddit.com/r/Markdown/comments/1sl4xox/tools_for_working_with_docdocx_and_pdf_files/?utm_source=chatgpt.com "Tools for working with DOC/DOCX and PDF files?"
[6]: https://www.reddit.com/r/selfhosted/comments/1shfgw0/selfhosting_pdfdocxppt_to_markdown_service/?utm_source=chatgpt.com "Selfhosting PDF/DOCX/PPT/... to Markdown service"
[7]: https://github.com/docling-project/docling?utm_source=chatgpt.com "GitHub - docling-project/docling: Get your documents ready for gen AI · GitHub"
[8]: https://github.com/docling-project/docling/blob/main/docs/reference/cli.md?utm_source=chatgpt.com "docling/docs/reference/cli.md at main · docling-project/docling · GitHub"
[9]: https://github.com/docling-project/docling/blob/main/docs/examples/export_figures.py?utm_source=chatgpt.com "docling/docs/examples/export_figures.py at main · docling-project/docling · GitHub"
[10]: https://arxiv.org/abs/2604.04948?utm_source=chatgpt.com "From PDF to RAG-Ready: Evaluating Document Conversion Frameworks for Domain-Specific Question Answering"
[11]: https://github.com/opendataloader-project/opendataloader-pdf?utm_source=chatgpt.com "OpenDataLoader PDF"
[12]: https://pypi.org/project/opendataloader-pdf/1.12.0/?utm_source=chatgpt.com "opendataloader-pdf"
[13]: https://github.com/opendataloader-project/opendataloader-pdf/issues/359?utm_source=chatgpt.com "Getting Empty table · Issue #359 · opendataloader-project ..."
[14]: https://www.reddit.com/r/LocalLLM/comments/1u4vjj7/which_pdf_to_md_converter_to_use/?utm_source=chatgpt.com "Which PDF to MD converter to use?"
