Khác nhau khá căn bản. Bốn tool không đơn giản là bốn implementation của cùng một PDF parser; chúng nằm ở các điểm khác nhau trên phổ **rule-based PDF parsing → specialized ML models → VLM/LLM document understanding**.

Nếu nhìn từ kiến trúc, có thể hình dung:

```text
                  Rule-based                         AI-heavy
                      │                                 │
OpenDataLoader ───────┼── Docling ───── Marker ─── MinerU
                      │                                 │
                 CPU / deterministic              GPU / models
```

### Pipeline kỹ thuật điển hình

| Thành phần              | MinerU                                   | Marker                       | Docling                               | OpenDataLoader-PDF          |
| ----------------------- | ---------------------------------------- | ---------------------------- | ------------------------------------- | --------------------------- |
| PDF text/object parsing | PyMuPDF + internal                       | **PyMuPDF**                  | internal/backend                      | **PDFBox-based/JVM core**   |
| Layout detection        | **Deep learning**                        | **Surya**                    | **DocLayNet-derived model**           | Rule/geometry + optional AI |
| Reading order           | model/algorithm                          | **Surya**                    | model + heuristics                    | **XY-Cut++**                |
| OCR                     | PaddleOCR / internal models tùy pipeline | **Surya OCR**                | RapidOCR / Tesseract / EasyOCR etc.   | optional OCR                |
| Table recognition       | specialized model                        | Surya table recognition      | **TableFormer**                       | deterministic + hybrid      |
| Formula                 | specialized formula recognition          | Surya + Texify-related stack | model/pipeline                        | hạn chế hơn                 |
| LLM/VLM                 | optional                                 | optional Gemini/Ollama/etc.  | optional VLM pipeline                 | hybrid optional             |
| Philosophy              | **AI document reconstruction**           | **modular AI pipeline**      | **structured document understanding** | **deterministic first**     |

Đây chính là lý do chúng có performance profile rất khác nhau.

---

## 1. MinerU: nhiều specialized model ghép thành document reconstruction pipeline

[MinerU GitHub](https://github.com/opendatalab/MinerU?utm_source=chatgpt.com)

MinerU gần với một **document AI system** hơn là PDF parser truyền thống.

Conceptually:

```text
PDF
 │
 ├── PDF native objects/text
 │
 ▼
Layout Detection
 │
 ├── title
 ├── paragraph
 ├── figure
 ├── caption
 ├── table
 ├── equation
 └── header/footer
 │
 ▼
OCR / Text extraction
 │
 ├──────────────┬──────────────┐
 ▼              ▼              ▼
Table model   Formula model   Image extraction
 │              │              │
 └──────────────┴──────────────┘
                │
        Reading-order recovery
                │
                ▼
       Intermediate representation
                │
                ▼
          Markdown + images
```

Điểm quan trọng là **không coi PDF đơn giản là text có tọa độ**.

Nó cố hiểu:

> vùng `(x1,y1,x2,y2)` này là figure, vùng kia là caption, cái này là equation, cái kia là table...

Sau đó mới reconstruct document.

Điều này cực kỳ quan trọng với PDF scientific:

```text
┌──────────────────────────────┐
│       PAPER TITLE            │
├──────────────┬───────────────┤
│ column 1     │ column 2      │
│ text         │ text          │
│              │               │
│ [FIGURE]     │  equation     │
│ Figure 2 ... │  E = mc²      │
├──────────────┴───────────────┤
│          TABLE               │
└──────────────────────────────┘
```

Một parser truyền thống nhìn thấy **glyph + coordinates**.

MinerU cố nhìn thấy **semantic blocks**.

Đó là lý do nó thường mạnh ở paper/sách/tài liệu phức tạp nhưng cũng nặng hơn.

---

# 2. Marker: Surya là "engine" quan trọng phía dưới

[Marker GitHub](https://github.com/datalab-to/marker?utm_source=chatgpt.com)

Marker có architecture rất thú vị vì phần AI được modular hóa khá rõ.

Một phần lớn sức mạnh đến từ hệ sinh thái **Surya** của Datalab:

[Surya GitHub](https://github.com/datalab-to/surya?utm_source=chatgpt.com)

Surya cung cấp các khả năng như:

```text
OCR
text detection
layout analysis
reading order
table recognition
```

Pipeline Marker có thể hình dung:

```text
                   PDF
                    │
                 PyMuPDF
                    │
          native PDF extraction
                    │
                    ▼
              Surya Layout
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
      OCR         Tables       Equations
     Surya         Surya        models
       │            │            │
       └────────────┼────────────┘
                    ▼
             Document blocks
                    │
             Marker processors
                    │
                    ▼
                Markdown
                 + images
```

Điểm mình thích ở Marker về engineering là **processor architecture**.

Bạn có document model gồm các block, sau đó các processor sửa/transform chúng.

Kiểu:

```python
PDF
 ↓
Block A: SectionHeader
Block B: Text
Block C: Figure
Block D: Caption
Block E: Table
 ↓
Processor
 ↓
Markdown renderer
```

Do đó custom pipeline tương đối dễ.

---

## Marker còn có một tầng LLM

Đây là điểm rất đáng chú ý.

Marker có thể chạy:

```text
PDF
 ↓
Surya / traditional models
 ↓
initial document
 ↓
        ┌─────────────┐
        │ LLM/VLM     │
        │ correction  │
        └──────┬──────┘
               ↓
       corrected document
               ↓
            Markdown
```

LLM không nhất thiết đọc toàn bộ PDF từ đầu.

Nó có thể được dùng để **sửa những block khó** sau extraction.

Ví dụ parser tạo:

```markdown
| Revenue | 2024 |
|---|---|
| USA | ??? |
```

LLM/VLM nhìn crop table và sửa thành:

```markdown
| Revenue | 2024 |
|---|---:|
| USA | $1.24M |
```

Đây là kiến trúc khá hiệu quả:

> specialized model xử lý 90% → expensive model sửa 10% khó.

---

# 3. Docling: khác Marker/MinerU ở chỗ IR/document model là trung tâm

[Docling GitHub](https://github.com/docling-project/docling?utm_source=chatgpt.com)

Docling do IBM khởi xướng và architecture của nó mang hơi hướng **document processing framework** rõ hơn.

Điểm cốt lõi không phải Markdown.

Nó là:

```text
                  PDF
                   │
                   ▼
          Document Converter
                   │
       ┌───────────┼────────────┐
       ▼           ▼            ▼
     Layout       OCR         Tables
      model      engine      TableFormer
       │           │            │
       └───────────┼────────────┘
                   ▼
            DoclingDocument
                   │
       ┌───────────┼──────────────┐
       ▼           ▼              ▼
    Markdown      JSON          HTML
                                  │
                                  ▼
                                RAG
```

**DoclingDocument** mới là sản phẩm chính.

Markdown chỉ là một serialization format.

Ví dụ conceptually:

```python
document.texts
document.tables
document.pictures
document.groups
document.pages
```

và mỗi object có metadata/layout/provenance.

Điều này rất giá trị nếu bạn làm RAG.

Thay vì:

```text
PDF → Markdown → parse Markdown → chunks
```

có thể làm:

```text
PDF
 ↓
DoclingDocument
 ↓
semantic hierarchy
 ↓
chunking
 ↓
embedding
```

Không cần mất thông tin rồi parse lại.

---

# TableFormer là điểm mạnh đặc biệt của Docling

Docling sử dụng **TableFormer** cho table structure recognition.

Bài toán table không đơn giản là OCR.

Ví dụ:

```text
┌────────────┬──────────────────┐
│            │ Revenue          │
│ Country    ├────────┬─────────┤
│            │ 2024   │ 2025    │
├────────────┼────────┼─────────┤
│ Vietnam    │ 10     │ 15      │
└────────────┴────────┴─────────┘
```

OCR chỉ cho bạn:

```text
Country
Revenue
2024
2025
Vietnam
10
15
```

Nhưng TableFormer phải suy luận:

```text
Revenue
   ├── 2024
   └── 2025
```

và:

```text
cell(row=0,col=0,rowspan=2)
cell(row=0,col=1,colspan=2)
```

Đây là **table structure recognition**, khó hơn OCR đáng kể.

---

# 4. OpenDataLoader: philosophy gần như ngược MinerU

[OpenDataLoader-PDF GitHub](https://github.com/opendataloader-project/opendataloader-pdf?utm_source=chatgpt.com)

OpenDataLoader đáng chú ý vì nó đặt câu hỏi:

> Tại sao phải dùng neural network cho mọi page nếu PDF đã chứa text + geometry?

PDF digital thường đã có:

```text
character
font
font size
bounding box
drawing
image
coordinates
```

Vì vậy có thể làm:

```text
PDF objects
     │
     ▼
geometry analysis
     │
     ▼
XY-Cut++
     │
     ▼
reading order
     │
     ├── paragraph
     ├── columns
     ├── tables
     └── figures
     │
     ▼
Markdown
```

**Không inference neural network cho mọi thứ.**

Đây là lý do CPU throughput có thể rất cao.

---

# XY-Cut là gì?

Giả sử page:

```text
┌───────────────────────────────────┐
│             TITLE                 │
├────────────────┬──────────────────┤
│                │                  │
│   COLUMN A     │    COLUMN B      │
│                │                  │
│                │                  │
└────────────────┴──────────────────┘
```

Có một khoảng trắng lớn ở giữa.

XY-Cut tìm whitespace và recursively chia:

```text
PAGE
 │
 ├── TITLE
 │
 └── BODY
      │
      ├── COLUMN A
      └── COLUMN B
```

Từ tree này suy ra reading order:

```text
TITLE
 ↓
COLUMN A
 ↓
COLUMN B
```

Không cần neural network để hiểu layout đó.

Với **digital-born PDF sạch**, cách này có thể vừa nhanh vừa rất chính xác.

Nhưng với:

```text
scan
magazine
weird layout
overlapping objects
handwriting
complex scientific figures
```

geometry/rules bắt đầu gặp giới hạn.

Khi đó ML/VLM có lợi.

---

# Sự khác biệt cốt lõi

Nếu rút bốn tool xuống philosophy:

```text
OpenDataLoader
"Trust PDF structure + geometry"
        │
        │
        ▼
Docling
"Build a structured document representation"
        │
        │
        ▼
Marker
"Use specialized ML models to reconstruct document"
        │
        │
        ▼
MinerU
"Full document AI pipeline with specialized models"
```

Nhưng ranh giới không tuyệt đối vì các project ngày càng thêm hybrid/VLM pipeline.

---

# Tại sao extract image thì cả 4 đều làm được?

Điều này thực ra **không cần AI** trong nhiều PDF.

PDF thường chứa:

```text
Page
 ├── Text object
 ├── Text object
 ├── Image XObject  ← JPEG/bitmap
 ├── Vector paths
 └── Fonts
```

Parser có thể lấy trực tiếp:

```python
image_object
    ↓
decode
    ↓
images/figure_01.png
```

Khó hơn là câu hỏi:

> "Image object nào tạo thành một Figure?"

Một figure có thể thực tế gồm:

```text
┌──────────────────────────┐
│ vector chart             │
│ + raster background      │
│ + text labels            │
│ + arrows                 │
└──────────────────────────┘
Figure 3. Architecture
```

Extract raw PDF image object có thể chỉ lấy **background** và mất arrows/text/vector.

Document AI có thể detect:

```text
Figure bounding box
(x1,y1,x2,y2)
```

rồi **render/crop cả vùng** thành:

```text
images/figure_3.png
```

Kết quả thường đúng với thứ con người gọi là "ảnh".

Đây là một tiêu chí mình khuyên bạn kiểm tra rất kỹ khi benchmark 4 tool.

---

# Nếu nhìn theo production architecture

Mình sẽ không nhất thiết chọn một engine cho mọi PDF.

Một pipeline mạnh hơn là:

```text
                         PDF
                          │
                          ▼
                  PDF classifier
                          │
             ┌────────────┴────────────┐
             │                         │
       Digital PDF                 Scan/complex
             │                         │
             ▼                         ▼
    OpenDataLoader / Docling       MinerU / Marker
             │                         │
             └────────────┬────────────┘
                          ▼
                  normalized Markdown
                          │
                ┌─────────┴────────┐
                ▼                  ▼
             images/           metadata.json
```

Thậm chí có thể thêm confidence routing:

```text
Fast parser
    │
    ▼
quality checks
    │
    ├── OK ───────────────→ Markdown
    │
    └── suspicious
            │
            ▼
       MinerU / VLM
            │
            ▼
         Markdown
```

Như vậy **80–90% PDF dễ không phải chạy model nặng**, chỉ những trang khó mới escalation.

Với yêu cầu **PDF → Markdown + folder ảnh riêng**, nếu bạn đang xây một hệ thống production chứ không phải tool dùng cá nhân, mình nghiêng về architecture hybrid kiểu này hơn là buộc toàn bộ tài liệu chạy MinerU.
