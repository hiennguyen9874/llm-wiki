---
type: Synthesis
title: PaddleOCR vs MinerU vs Docling
description: So sánh PaddleOCR, MinerU 4 và Docling theo kiến trúc, benchmark có giới hạn, cấu trúc đầu ra, triển khai và lựa chọn cho OCR hoặc RAG.
tags: [ml, ocr, document-parsing, comparison, rag]
status: draft
created: 2026-10-29
generated: { by: llm-wiki-agent/1, at: 2026-10-29T14:03:42+07:00 }
stale_after: 2027-01-29
sources:
  - id: paddle-repo
    resource: ../raw/PaddleOCR/README.md
    scope: ../raw/PaddleOCR/
    kind: code
    revision: dab3fe3
    title: PaddleOCR repository
  - id: mineru-repo
    resource: ../raw/MinerU/README.md
    scope: ../raw/MinerU/
    kind: code
    revision: b7f3dd0
    title: MinerU 4.0.12 repository
  - id: docling-repo
    resource: ../raw/docling/README.md
    scope: ../raw/docling/
    kind: code
    revision: 8f7ae54
    title: Docling repository
  - id: paddle-vl-report
    resource: ../raw/2606.03264_PaddleOCR-VL-1.6/main.tex
    kind: paper
    title: PaddleOCR-VL-1.6 technical report
  - id: mineru-pro-card
    resource: ../raw/MinerU2.5-Pro-2605-1.2B.md
    kind: model-card
    title: MinerU2.5-Pro-2605 model card
  - id: docling-ir
    resource: docling-document-representation.md
    title: Docling document representation
  - id: docling-chunks
    resource: docling-native-chunking.md
    title: Docling native chunking
  - id: docling-exports
    resource: docling-serialization.md
    title: Docling serialization
  - id: docling-ocr
    resource: docling-ocr-engines.md
    title: Docling OCR engines
  - id: docling-quality
    resource: docling-confidence-grades.md
    title: Docling confidence grades
  - id: ppocr-v6
    resource: pp-ocrv6.md
    title: PP-OCRv6
  - id: senocr
    resource: senocr-vi.md
    title: SenOCR-Vi
---

# PaddleOCR vs MinerU vs Docling

**Synthesis:** Chọn **PaddleOCR** khi cần OCR như một thành phần có thể huấn luyện, tối ưu và triển khai từ edge đến server; chọn **MinerU 4** để đánh giá trước cho workflow chuyển tài liệu thành nội dung có cấu trúc, thư viện cục bộ và agent reading; chọn **Docling** khi hợp đồng dữ liệu trung gian, provenance và structure-aware chunking là trọng tâm. Đây là phân loại theo kiến trúc và nhu cầu, không phải thứ hạng accuracy hoặc tốc độ đã được đo chung.[^paddle-repo][^mineru-repo][^docling-repo][^docling-ir][^docling-chunks]

## Phạm vi và evidence

- Snapshot: PaddleOCR `dab3fe3`; MinerU 4.0.12 `b7f3dd0`; Docling `8f7ae54`. Không đồng nhất API MinerU 4 với [README MinerU 3.x](mineru.md), hoặc model MinerU2.5 với cả ứng dụng MinerU.[^paddle-repo][^mineru-repo][^docling-repo]
- **Observed** nghĩa là đọc tĩnh code/artifact; **Reported** là tác giả công bố; **Synthesis** là suy luận lựa chọn từ các bằng chứng đã dẫn. Không inference, download model, benchmark hoặc project test nào được chạy cho so sánh này.
- Các repository mới được ingest một phần; external PaddleX, DocVortex, docling-core, runtime và weights chưa được audit. `draft` thể hiện giới hạn coverage, không có nghĩa mọi claim đều sai. Các trang linked bên dưới giữ ledger chi tiết.

## 1. So đúng cấp độ

| Hệ sinh thái | Nhánh cần phân biệt | Đơn vị so sánh phù hợp |
|---|---|---|
| PaddleOCR | [PP-OCRv6](pp-ocrv6.md): detect/recognize text; [PP-StructureV3](pp-structurev3.md): parser nhiều specialist; [PaddleOCR-VL-1.6](paddleocr-vl-1.6.md): layout + VLM recognition | OCR engine, modular parser hoặc VLM parser, tùy bài toán |
| MinerU | [MinerU 4](mineru-4-architecture.md): application/tier orchestration; [MinerU2.5-Pro](mineru2-5-pro.md): model 1.2B | Toàn pipeline theo tier hoặc riêng model |
| Docling | [Standard PDF pipeline](docling-standard-pdf-pipeline.md): native text + layout/OCR/table; [VLM pipeline](docling-models-and-inference-engines.md): conversion qua model preset | Cấu hình converter + model + OCR engine + export/chunk policy |

**Observed / reported:** PaddleOCR có nhiều pipeline chứ không chỉ OCR cổ điển; MinerU có cả native/model/VLM paths; Docling không chỉ là wrapper cho Granite Docling. So một lượt gọi PP-OCR với một lượt parse PDF đầy đủ sẽ đo hai công việc khác nhau.[^paddle-repo][^mineru-repo][^docling-repo]

## 2. Kiến trúc và quan hệ phụ thuộc

### PaddleOCR: toolkit và pipeline có thể cấu hình

**Observed:** Python package wrap PaddleX và pin `paddlex[ocr-core]>=3.7.0,<3.8.0`; source tree có đường huấn luyện/classic inference riêng. Wrapper OCR không chỉ định language/version mặc định chọn PP-OCRv6 medium detector và recognizer. PPStructureV3 selector chỉ nhận OCR v3–v5, không phải cứ v6 mới nhất là mặc định trong mọi pipeline.[^paddle-repo]

**Reported:** PP-StructureV3 có các module layout, OCR, bảng, công thức, chart, seal và reading order. PaddleOCR-VL-1.6 giữ layout PP-DocLayoutV3 rồi nhận dạng crop bằng VLM 0.9B. **Observed:** `PaddleOCRVL.restructure_pages` forward `merge_tables` và `relevel_titles`, mặc định `True`; đây là bằng chứng có API hậu xử lý, không phải kiểm chứng độ đúng của merge.[^paddle-repo][^paddle-vl-report]

### MinerU 4: tier routing và document application

**Observed:** `flash/basic/standard/advanced` tương ứng `flash/medium/high/xhigh`. Flash + PDF text mode bypass model; scan cần OCR. Basic dùng specialist models; Standard/Advanced thêm VLM. Model-backed processing chia window mặc định 64 trang.[^mineru-repo]

**Observed:** registry dùng PP-DocLayoutV2; PP-OCRv6 Tiny detector + Small recognizer; PP-FormulaNet plus-M; SLANet Plus và table assets; VLM MinerU2.5-Pro-2605-1.2B. **Reported:** DocVortex phụ trách native parsing, classification, deterministic postprocessing và rendering; MinerU phụ trách inference và orchestration. ModelJson → MiddleJson → render là ranh giới mô tả trong kiến trúc.[^mineru-repo]

### Docling: converter và document intermediate representation

**Observed:** standard pipeline nối preprocessing → layout → OCR → layout postprocessing → table structure → optional form fields → page assembly; sau đó document reading order và optional heading hierarchy. OCR/table mặc định bật; layout mặc định Heron; image export và form fields mặc định tắt.[^docling-repo]

**Observed:** PDF-aware selective OCR ưu tiên PDF text khi merge; full-page OCR là lựa chọn khác, không phải hành vi bắt buộc. VLM pipeline là nhánh riêng, default preset Granite Docling; có đường MinerU2 hai bước layout/crop recognition, nên không thể coi mọi cấu hình Docling là cùng một model.[^docling-repo]

**Synthesis quan trọng:** ba hệ không độc lập hoàn toàn về model: MinerU sử dụng model Paddle, Docling có thể dùng PP-OCR qua RapidOCR và có đường conversion MinerU2. So sánh cần ghi cả model và orchestration; hai sản phẩm có thể khác pipeline nhưng chung recognizer.[^mineru-repo][^docling-repo][^docling-ocr]

## 3. Chất lượng: đọc benchmark mà không ghép sai protocol

### OmniDocBench v1.6 trong cùng bảng của báo cáo PaddleOCR-VL-1.6

**Reported**, report nói lấy metric từ official leaderboard; không có leaderboard snapshot hay outputs được kiểm lại trong phiên này.[^paddle-vl-report]

| Model như được ghi trong bảng | Overall ↑ | Text edit ↓ | Formula CDM ↑ | Table TEDS ↑ | TEDS-S ↑ | Reading-order edit ↓ |
|---|---:|---:|---:|---:|---:|---:|
| PaddleOCR-VL-1.6, 0.9B | 96.33 | 0.033 | 97.49 | 94.76 | 97.11 | 0.127 |
| MinerU2.5-Pro, 1.2B, revision không rõ trong bảng | 95.75 | 0.036 | 97.45 | 93.42 | 95.92 | 0.120 |

**Synthesis:** ở riêng bảng này, Paddle dẫn overall/text/formula/table, MinerU-Pro có reading-order edit thấp hơn; không có một bên thắng mọi metric. Overall không đồng nghĩa phần trăm ký tự đúng. Không có Docling tương ứng trong bảng này, nên không thể xếp Docling thứ ba từ nó.[^paddle-vl-report]

### Discrepancy cần giữ riêng

Card **MinerU2.5-Pro-2605** ghi `v1.6_full`: **95.72 / 0.036 / 97.15 / 93.62 / 96.01 / 0.123** theo cùng thứ tự metric. Card so 2604 ở overall **95.69**, formula **97.29**. Các số này không trùng dòng MinerU-Pro **95.75 / 97.45** trong report Paddle. Revision/evaluation configuration của dòng report chưa đủ để giải thích; không chọn một nguồn làm sự thật cuối cùng hay tự gán nó cho 2605.[^mineru-pro-card][^paddle-vl-report]

### Ảnh chụp và biến dạng

Trong bảng **Real5-OmniDocBench** của report Paddle: PaddleOCR-VL-1.6 **93.19**, MinerU2.5-pro **88.96**, PP-StructureV3 **64.45**. Riêng skew: **92.66** so với **81.26** cho VL-1.6 và MinerU-Pro. **Reported**, không phải benchmark của MinerU 4 đầy đủ, không có Docling cùng bảng và không chứng minh kết quả tương tự trên tiếng Việt.[^paddle-vl-report]

**Synthesis lựa chọn:** nên thử PaddleOCR-VL-1.6 sớm cho ảnh chụp cong/nghiêng; giữ MinerU-Pro trong shortlist cho PDF phức tạp. Không dùng điểm recognition của PP-OCRv6 để thay thế điểm parsing của các VLM.[^paddle-vl-report][^ppocr-v6]

## 4. Output, RAG, bảng và provenance

| Yêu cầu | PaddleOCR | MinerU 4 | Docling |
|---|---|---|---|
| Output có cấu trúc | JSON/Markdown; README nêu PP-StructureV3 có coordinate text/cell chi tiết hơn VL | ModelJson/MiddleJson, rendering nhiều target; mỗi entry point chỉ expose một subset | DoclingDocument typed IR; export Markdown/HTML/JSON/DocTags và serializer |
| Workflow trung tâm | OCR/document-AI modules và deployment | Parse/library/cache/search/page-block continuation | Convert → structured document → serialize/chunk |
| Tái dùng downstream | Có thể tự xây adapter từ result | Có thể dùng structured result và stable locators | Có native structure-aware/token-aware chunking |

Các ô trên là **Observed / Reported**, không phải đo DX hoặc feature-completeness tuyệt đối.[^paddle-repo][^mineru-repo][^docling-repo][^docling-ir][^docling-chunks]

**Reported:** DoclingDocument giữ typed items, body/furniture trees, reading order, bounding boxes và provenance khi có. HierarchicalChunker dùng document elements/headings/captions; HybridChunker split quá token budget và merge peers; bảng trải nhiều chunks có thể lặp header. **Synthesis:** khi cần RAG có citation và metadata, giữ IR trước thay vì export Markdown rồi cố khôi phục cấu trúc.[^docling-ir][^docling-chunks]

**Reported:** Docling JSON giữ table-span metadata; HTML có `rowspan/colspan`; Markdown flatten span và LaTeX serializer hiện cũng không phát `multirow/multicolumn`. **Synthesis:** kiểm tra cả IR và export, vì bảng parse đúng vẫn có thể mất semantics khi serialize. Nên giữ JSON/HTML cho merged headers thay vì chỉ Markdown.[^docling-exports]

**Giới hạn cross-page:** Paddle có API restructure nêu trên; card MinerU-Pro vừa claim native cross-page table merging vừa ghi “Currently under integration” trong Quick Start. Chưa đủ căn cứ từ card để bảo đảm feature đã hoạt động trong MinerU 4. Không suy từ việc Docling chunker lặp header sang việc nó reconstruct bảng qua trang.[^paddle-repo][^mineru-pro-card][^docling-chunks]

## 5. Triển khai và hiệu năng

| Hệ | Đường runtime đã được tài liệu/code mô tả | Cần tránh suy ra |
|---|---|---|
| PaddleOCR | Paddle/Paddle static/dynamic, Transformers, ONNX Runtime; HPI; VL backend native/vLLM/SGLang/FastDeploy/MLX/llama.cpp servers; source-tree training | Backend selector có tên không có nghĩa mọi model/hardware đều compatible; layout vẫn là phần riêng với recognizer server |
| MinerU 4 | Small models ONNX/Torch tách khỏi VLM llama.cpp/vLLM/LMDeploy/explicit MLX hoặc remote server | Không tái dùng kết luận “VLM không chạy CPU” của README 3.x; có engine path không đồng nghĩa đủ throughput cho production |
| Docling | OCR engines thay thế được; VLM auto-inline MLX/Transformers, vLLM có điều kiện và `prefer_vllm`; API engines | `DocumentConverter()` không đồng nghĩa chạy Granite; kết quả giữa hai máy có thể khác nếu auto OCR chọn engine khác |

Các đường trên dựa trên inspection tĩnh và wiki implementation concepts; không được chạy trong phiên này.[^paddle-repo][^mineru-repo][^docling-repo]

**Reported:** PP-OCRv6 Tiny có 1.5M parameters và 0.20 s/image trên Xeon 8350C/OpenVINO trong report; MinerU-Pro card nêu 2.12 fps concurrent trên A100 nhưng thiếu workload. Đây là OCR image so với model parsing workflow, khác hardware/protocol; không chia hai số để kết luận tỷ lệ nhanh hơn.[^ppocr-v6][^mineru-pro-card]

**Synthesis:** OCR scene/text nhẹ → benchmark PP-OCR trước; PDF nhiều native text → đánh giá selective/native paths; scan/formula/table khó → so cấu hình parser đầy đủ. Đo end-to-end p50/p95, pages/s, peak RAM/VRAM, render/export và retry/review cost, không chỉ model decode.

## 6. Failure modes, privacy và licensing

- **Observed:** Docling auto OCR có thể warning rồi pass-through nếu không có engine và không gặp language rejection; conversion success không chứng minh OCR đã chạy. Auto selector không thử Tesseract. **Reported:** confidence grades có thể hỗ trợ review, nhưng tài liệu confidence nói `table_score` chưa implement; confidence không phải correctness certificate.[^docling-repo][^docling-quality]
- **Observed / reported:** MinerU remote VLM có thể gửi page images; optional LLM enhancement là một content boundary khác. “Không tự upload tới official parse service” không đồng nghĩa air-gapped. Có telemetry code được ghi nhận trong [models and engines](mineru-4-models-and-engines.md); payload/network behavior chưa audit trong so sánh này.[^mineru-repo]
- **Observed:** Docling remote OCR/VLM cần `enable_remote_services`; model download/source URL fetching tách biệt. KServe gRPC TLS mặc định off trong snapshot. Một số VLM presets cho phép `trust_remote_code`. Không suy luận default remote opt-in là bảo đảm offline.[^docling-repo]
- **Synthesis:** cả ba cần pin model/runtime/config, chuẩn bị weights offline và kiểm tra egress thực tế nếu dữ liệu nhạy cảm. Chưa có audit network của cả ba, nên không xếp hạng privacy tuyệt đối.

**Observed — code licenses trong raw:** PaddleOCR Apache-2.0; Docling MIT và README yêu cầu kiểm license từng model; MinerU áp dụng Apache-2.0 **kèm điều khoản bổ sung**: cần commercial license khi consolidated MAU với affiliates vượt **100 triệu**, hoặc consolidated monthly revenue vượt **20 triệu USD**; online service cho bên thứ ba phải attribution nổi bật; vi phạm các nghĩa vụ nêu trong license dẫn tới automatic termination. MinerU-Pro-2605 model card khai báo Apache-2.0, nhưng model license không thay thế application license hoặc license DocVortex/dependencies. Đây là đọc văn bản, không phải tư vấn pháp lý.[^paddle-repo][^docling-repo][^mineru-repo][^mineru-pro-card]

## 7. Tiếng Việt và quyết định thực dụng

**Reported:** [SenOCR-Vi](senocr-vi.md) fine-tune decoder PaddleOCR-VL-1.6 cho tiếng Việt và báo cáo 82.83 so với 80.90 của base trên Vietnamese MDPBench. Tuy nhiên 82.83 được corrected page re-aggregation, còn 80.90 lấy leaderboard, nên chênh 1.93 không phải cùng một rerun kiểm soát. Không có controlled Vietnamese comparison đủ cả ba cấu hình hiện tại trong bằng chứng đã đọc.[^senocr]

**Synthesis — shortlist theo nhu cầu:**

| Nhu cầu chính | Thử trước | Lý do và giới hạn |
|---|---|---|
| OCR boxes/text, scene/industrial, edge CPU, tự train detector/recognizer | PaddleOCR PP-OCRv6 | Toolkit và model nhỏ; không tự giải toàn bộ layout/table task |
| Ảnh chụp cong, nghiêng, seal, bảng/công thức | PaddleOCR-VL-1.6, đối chiếu MinerU-Pro | Có benchmark robustness làm tín hiệu; vẫn phải test corpus riêng |
| Chuyển PDF/books/papers thành content + local library + agent continuation | MinerU 4 standard, so thêm advanced khi cần | Tiered application, structured output và locators; pin tier và page range |
| Multi-format ingestion/RAG, metadata, chunk budget, dễ thay OCR/layout engine | Docling standard + native chunker; thử VLM cho failure cases | IR và chunking rõ; không đồng nghĩa accuracy cao nhất |
| Commercial online service cần governance đơn giản | Review PaddleOCR/Docling code licenses trước, so model licenses | MinerU có additional terms; không kết luận cấm commercial |
| Corpus tiếng Việt | Test cùng dữ liệu cả ba, thêm SenOCR như nhánh Paddle nếu phù hợp | Không lấy English/Chinese overall hoặc số language làm accuracy tiếng Việt |

Các khuyến nghị là suy luận từ những khác biệt đã dẫn, không phải kết quả thực nghiệm.

## 8. Protocol thử nghiệm đề xuất

**Synthesis, chưa thực thi:** dùng cùng corpus khoảng 20–50 tài liệu có digital/scanned/photographed, two-column, merged/borderless/multipage tables, formulas, figures/captions, và Vietnamese diacritics. Tách hai track: (1) text OCR và (2) document parsing đầy đủ. Pin version/model/tier/OCR engine, resolution, language, device, export options và page range; không để MinerU library default 10 trang bị so với parser khác chạy toàn bộ tài liệu.[^mineru-repo]

Đánh giá độc lập: CER/WER và omission; reading order; table content/structure và span preservation; formula fidelity; figure crop/caption links; headings/provenance; latency/throughput/RAM/VRAM; hard failures, silent no-OCR và manual-review rate. Với RAG, giữ embedding/retriever/query set cố định, phân biệt parser-only và end-to-end evaluation. Xây native/selective fast path → quality checks → expensive parser escalation nếu corpus thực tế cho thấy có lợi; chưa có measurement chứng minh routing này tiết kiệm trong so sánh này.

## Coverage và giới hạn

So sánh tái dùng các implementation concepts và các trang Docling IR/chunking/serialization/OCR/confidence, PP-OCRv6 và SenOCR. Raw research bổ sung đọc: README ba repository theo các mục liên quan; license MinerU và Docling; header license PaddleOCR; MinerU `tier.py` và registry matches; Paddle VL `restructure_pages`; report VL-1.6 §§Experiments/Document Parsing và hai bảng benchmark; MinerU-Pro-2605 card tới Quick Start/Performance. Badge, promotional instructions trong README, remote figures/links, unrelated docs và runtime assets không được coi là bằng chứng đã kiểm. Không sửa raw, không chạy source commands, không kiểm Obsidian rendering. Phạm vi không phải exhaustive audit toàn repository.

## Relationships

- **Uses:** [PaddleOCR repository pipelines](paddleocr-repository-pipelines.md), [training architecture](paddleocr-model-training-architecture.md) và [inference engines](paddleocr-inference-engines.md).
- **Uses:** [MinerU 4 architecture](mineru-4-architecture.md), [OCR pipeline](mineru-4-ocr-pipeline.md) và [models and engines](mineru-4-models-and-engines.md).
- **Uses:** [Docling architecture](docling-architecture.md), [standard PDF pipeline](docling-standard-pdf-pipeline.md), [models and engines](docling-models-and-inference-engines.md), [plugins](docling-plugin-extensions.md), [IR](docling-document-representation.md) và [native chunking](docling-native-chunking.md).
- **Qualifies:** [PDF-to-Markdown tool selection](pdf-to-markdown-tool-selection.md) và [parser architectures](pdf-to-markdown-parser-architectures.md) bằng revision-specific evidence; không thay toàn bộ các so sánh với Marker/OpenDataLoader/LiteParse.

[^paddle-repo]: [PaddleOCR README](../raw/PaddleOCR/README.md), §§Key Features, updates 2026.04.21/2026.01.29; `LICENSE` header; revision `dab3fe3`: `paddleocr/_pipelines/paddleocr_vl.py::PaddleOCRVL.restructure_pages`. Additional compiled static evidence: [pipelines](paddleocr-repository-pipelines.md), §§Wrapper and configuration/OCR and document flows; [engines](paddleocr-inference-engines.md), §§Engine selection and precedence/Generative and deployment paths; [training](paddleocr-model-training-architecture.md), §§Composition and concrete configurations/Boundaries and limitations. External PaddleX internals remain uninspected.
[^mineru-repo]: [MinerU README](../raw/MinerU/README.md), §§MinerU 4.0/Quick Start; revision `b7f3dd0`: `mineru/parser/tier.py::_EFFORT_BY_TIER`, `mineru/model/registry.py`; `LICENSE.md` §§1–4. Compiled implementation/coverage: [architecture](mineru-4-architecture.md), §§Boundaries and flow/Coverage and limits; [OCR](mineru-4-ocr-pipeline.md), §§PDF stages/Detection and recognition; [engines](mineru-4-models-and-engines.md), §§Model components/Runtime selection/Operational boundaries and limits. DocVortex internals and network behavior are not verified.
[^docling-repo]: [Docling README](../raw/docling/README.md), §§Features/Quickstart/License; `LICENSE`, MIT permission and notice; revision `8f7ae54`. Compiled static implementation: [standard PDF pipeline](docling-standard-pdf-pipeline.md), §§Stages and defaults/OCR region and text-layer policy/Automatic OCR selection and operational risk; [VLM engines](docling-models-and-inference-engines.md), §§Model versus engine/Runtime selection. External components remain uninspected.
[^paddle-vl-report]: [PaddleOCR-VL-1.6 report](../raw/2606.03264_PaddleOCR-VL-1.6/main.tex), §§PaddleOCR-VL-1.6 Overview/Experiments → Document Parsing; tables `tab:omni16_full_performance` and `tab:real5-omnidocbench-performance`; scores attributed by report to leaderboard, not independently reproduced.
[^mineru-pro-card]: [MinerU2.5-Pro-2605 card](../raw/MinerU2.5-Pro-2605-1.2B.md), frontmatter license; §News → Comparable Performance table; §Unmatched SOTA Performance; §1 Quick Start, §§1.2–1.4 and cross-page integration notice. Remote images not inspected.
[^docling-ir]: [Docling document representation](docling-document-representation.md), §§Content and structure/Construction and use; provenance resolves to its Docling Document documentation source, no new runtime verification.
[^docling-chunks]: [Docling native chunking](docling-native-chunking.md), §§Base interface/Built-in strategies/Selection boundary.
[^docling-exports]: [Docling serialization](docling-serialization.md), §Table-span fidelity by target.
[^docling-ocr]: [Docling OCR engines](docling-ocr-engines.md), §RapidOCR; version-specific documentation, not a runtime test.
[^docling-quality]: [Docling confidence grades](docling-confidence-grades.md), §§Operational interpretation/Report components; table-score status reflects that documentation.
[^ppocr-v6]: [PP-OCRv6](pp-ocrv6.md), §§Architecture/Reported results/Trust limits; in-house latency and quality protocols, not reproduced here.
[^senocr]: [SenOCR-Vi](senocr-vi.md), §§Identity and interface/Reported evaluation/Comparability caveats/Coverage and trust limits; vendor-run Vietnamese scores and scorer correction.
