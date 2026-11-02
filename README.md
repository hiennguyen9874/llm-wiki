# LLM Wiki

Kho tri thức cá nhân vận hành cùng LLM, lưu kiến thức theo Markdown để dễ đọc bằng Obsidian, quản lý bằng Git và truy xuất bằng agent. Repository biến nguồn thô thành các trang kiến thức có cấu trúc, nguồn gốc rõ ràng và có thể bảo trì lâu dài.

## Khả năng chính

- **Ingest nguồn kiến thức:** Biên dịch tài liệu trong `raw/` thành các concept bền vững trong `wiki/`.
- **Truy vấn và tổng hợp:** Agent tìm từ catalog, đọc các concept liên quan, đánh giá nguồn, độ mới và mâu thuẫn trước khi trả lời.
- **Provenance và trust:** Mỗi claim phụ thuộc nguồn được liên kết đến tài liệu gốc; trạng thái, mâu thuẫn và thay thế phiên bản được biểu diễn trong wiki.
- **Bảo trì wiki:** Kiểm tra metadata, index, link, provenance, lifecycle và các rủi ro như dữ liệu nhạy cảm.
- **Tìm kiếm mở rộng tùy chọn:** QMD cung cấp BM25 và semantic/hybrid retrieval bằng cache cục bộ; Markdown và index vẫn là nguồn dữ liệu chính.
- **Tương thích công cụ:** Nội dung là Markdown chuẩn, có thể mở trực tiếp bằng Obsidian và quản lý lịch sử thay đổi bằng Git.

## Cấu trúc repository

```text
AGENTS.md Contract nền tảng, dùng chung cho mọi knowledge base
SCOPE.md   Phạm vi, domain và quy ước riêng của knowledge base này
raw/       Nguồn gốc, bất biến sau khi được đưa vào repository
wiki/      Tri thức đã được tổng hợp theo OKF v0.2
  index.md Catalog đầy đủ, điểm vào cho truy vấn
  log.md   Lịch sử thay đổi theo thứ tự mới nhất
outputs/   Báo cáo và kết quả tạm thời được yêu cầu
.pi/       Skills và prompt cho agent
.qmd/      Cấu hình cache tìm kiếm QMD (database tạo ra chỉ lưu cục bộ)
tools/     Script kiểm tra cấu trúc và cập nhật QMD
```

`AGENTS.md` là contract trung tâm, không gắn với domain nào: định nghĩa quyền sở hữu dữ liệu, định dạng concept và các bất biến khi thay đổi wiki. `SCOPE.md` cấu hình riêng cho knowledge base này: phạm vi, loại trừ, danh sách domain, quy tắc theo domain, ngôn ngữ và course profile. `SCOPE.md` chỉ được bổ sung, không được nới lỏng contract.

Để tạo knowledge base mới cho chủ đề khác: sao chép repository (bỏ nội dung `raw/` và `wiki/`), giữ nguyên `AGENTS.md` và `.pi/`, rồi chạy prompt `init-wiki` (skill `wiki-init`) để viết lại `SCOPE.md`. Skill xác nhận `SCOPE.md` với bạn trước, sau đó mới tiếp tục ingest hoặc query.

```text
/init-wiki KB về tài chính cá nhân, domain: đầu tư, thuế. Ingest raw/my-source.md
```

## Các branch knowledge base

Bảng dưới đây là snapshot các branch local và remote-tracking `origin/*` hiện có trong repository, không phải danh sách được tự động đồng bộ với server. Mỗi dòng gộp branch local và `origin` cùng tên nếu có; link mở nội dung branch trên GitHub. Cột `wiki/` đếm **file được Git theo dõi**, bao gồm index, log và các file không phải concept; không đếm file chưa được track. Nội dung chủ đề được tóm tắt từ `SCOPE.md` và `wiki/index.md`: khi scope không có hoặc là scope chung, chủ đề là suy ra từ index, không phải giới hạn chính thức.

| Branch | Chủ đề / phạm vi và nội dung index | Scope | Wiki / index | File trong `wiki/` (local / origin) |
| --- | --- | --- | --- | ---: |
| `main` | Kho cá nhân tổng quát; index chưa có concept | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/main/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/main/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/main/wiki/index.md) | 2 / 2 |
| `v1` | Scaffold second brain đời đầu; index chủ yếu là navigation | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/v1/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/v1/wiki/index.md) | 7 / 7 |
| `v2` | Scaffold wiki; index chưa có concept | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/v2/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/v2/wiki/index.md) | 2 / 2 |
| `kbs/agent-finance` | AI agents và công cụ cho đầu tư, trading và tài chính | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/agent-finance/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/agent-finance/wiki/index.md) | 49 / 49 |
| `kbs/axis-camera` | AXIS cameras, ACAP SDK, ứng dụng và triển khai computer vision | [Scope chung](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/axis-camera/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/axis-camera/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/axis-camera/wiki/index.md) | 100 / 100 |
| `kbs/diffusion-model` | Diffusion và flow-matching image generation, checkpoints, adapters và local inference | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/diffusion-model/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/diffusion-model/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/diffusion-model/wiki/index.md) | 34 / 34 |
| `kbs/embedding` | Embedding, reranking, late interaction và retrieval benchmarks | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/embedding/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/embedding/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/embedding/wiki/index.md) | 68 / 86 |
| `kbs/image-generation` | Scaffold image generation; index chưa có concept | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/image-generation/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/image-generation/wiki/index.md) | 2 / 2 |
| `kbs/jev` | Jev và các decision models: APIs, calibration, serving và alternatives | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/jev/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/jev/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/jev/wiki/index.md) | 40 / 40 |
| `kbs/llm` | LLM architectures, training, reasoning và inference | [Scope chung trên origin](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/llm/SCOPE.md); local không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/llm/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/llm/wiki/index.md) | 244 / 244 |
| `kbs/llm-serving` | LLM serving engines, kernels, quantization, speculative decoding và deployment | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/llm-serving/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/llm-serving/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/llm-serving/wiki/index.md) | 254 / 254 |
| `kbs/loop-models` | Looped và recurrent-depth transformers, scaling, reasoning và inference | [Scope trên origin](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/loop-models/SCOPE.md); local không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/loop-models/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/loop-models/wiki/index.md) | 35 / 36 |
| `kbs/macroeconomics` | Kinh tế vĩ mô, chính sách, thương mại và thị trường | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/macroeconomics/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/macroeconomics/wiki/index.md) | 127 / 127 |
| `kbs/object-detection` | Object detection, kiến trúc, lineage và edge/video detection | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/object-detection/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/object-detection/wiki/index.md) | 11 / 11 |
| `kbs/ocr` | OCR models, approaches và document recognition | [Scope chung](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/ocr/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/ocr/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/ocr/wiki/index.md) | 100 / 100 |
| `kbs/pi-durable` | Pi Durable agent harness, storage, replay và deployment | [Scope chung](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/pi-durable/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/pi-durable/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/pi-durable/wiki/index.md) | — / 19 |
| `kbs/pydantic-ai` | Pydantic AI agents, ecosystem packages và vận hành production | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/pydantic-ai/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/pydantic-ai/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/pydantic-ai/wiki/index.md) | 39 / 39 |
| `kbs/rag` | Open-source RAG platforms, retrieval, ingestion, deployment và security | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/rag/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/rag/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/rag/wiki/index.md) | 147 / 147 |
| `kbs/speech` | Voice pipeline VAD → STT → LLM → TTS, streaming và deployment | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/speech/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/speech/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/speech/wiki/index.md) | 264 / 264 |
| `kbs/stock` | Cổ phiếu và phân tích đầu tư, bao gồm bối cảnh vĩ mô Việt Nam | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/stock/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/stock/wiki/index.md) | 38 / 38 |
| `kbs/stock-v2` | Phân tích cổ phiếu, định giá và rủi ro thị trường | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/stock-v2/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/stock-v2/wiki/index.md) | 10 / 10 |
| `kbs/text-based-person-search-papers` | Nghiên cứu text-based person search và các paper liên quan | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/text-based-person-search-papers/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/text-based-person-search-papers/wiki/index.md) | 43 / 43 |
| `kbs/text-based-person-search-papers-v2` | Các phương pháp và paper text-to-image person retrieval | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/text-based-person-search-papers-v2/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/text-based-person-search-papers-v2/wiki/index.md) | 14 / 14 |
| `kbs/time-series-foundation-model` | Time-series foundation models theo tên branch; index chưa có concept | [Scope chung](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/time-series-foundation-model/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/time-series-foundation-model/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/time-series-foundation-model/wiki/index.md) | 2 / 2 |
| `kbs/understand-people` | Tâm lý, hành vi và các khung hiểu con người | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/understand-people/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/understand-people/wiki/index.md) | 24 / 24 |
| `kbs/video-temporal` | Video temporal modeling, action recognition, localization và anticipation | Không có | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/video-temporal/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/video-temporal/wiki/index.md) | 43 / 43 |
| `kbs/vision-language-retrieval-classification` | Vision–language models, visual representation learning và đánh giá | [Scope](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/vision-language-retrieval-classification/SCOPE.md) | [Wiki](https://github.com/hiennguyen9874/llm-wiki/tree/kbs/vision-language-retrieval-classification/wiki) · [Index](https://github.com/hiennguyen9874/llm-wiki/blob/kbs/vision-language-retrieval-classification/wiki/index.md) | 50 / 50 |

`—` nghĩa là không có branch local. Local `kbs/agent-finance`, `kbs/embedding` và `kbs/loop-models` đang sau origin; `kbs/llm` đã phân kỳ (cả ahead và behind). Số file bằng nhau không có nghĩa nội dung hoặc commit giống nhau. Để xem đúng phiên bản local mà không checkout, dùng `git show <branch>:wiki/index.md` và `git ls-tree -r --name-only <branch> -- wiki/`.

## Cách dùng cơ bản

### 1. Mở kho tri thức

Clone repository, sau đó mở thư mục bằng Obsidian nếu muốn duyệt và chỉnh sửa Markdown trực quan:

```bash
git clone <repository-url>
cd llm-wiki
```

Agent tự động nạp `AGENTS.md`; đọc `SCOPE.md` trước khi thay đổi nội dung để tuân thủ quy ước của kho.

### 2. Thêm và ingest nguồn mới

1. Đặt tài liệu nguồn vào `raw/`. Không sửa lại file nguồn sau khi đã lưu; khi có đính chính, thêm một file nguồn mới.
2. Trong agent, dùng prompt/skill **wiki-ingest** (hoặc yêu cầu agent ingest file cụ thể).
3. Agent kiểm tra dữ liệu nhạy cảm, đối chiếu nội dung đã có, rồi chỉ tạo hoặc cập nhật các concept cần thiết trong `wiki/`.

Ví dụ yêu cầu:

```text
Ingest raw/my-source.md vào wiki.
```

Mỗi concept có YAML frontmatter, mô tả ngắn cho index, trạng thái và danh sách nguồn. `wiki/index.md` cùng `wiki/log.md` được cập nhật trong một mutation hoàn chỉnh.

### 3. Đặt câu hỏi cho wiki

Dùng **wiki-query** hoặc prompt `wiki-query` và nêu rõ câu hỏi. Agent ưu tiên đọc `wiki/index.md`, chọn concept phù hợp, kiểm tra relationship, provenance, freshness và contradictions trước khi tổng hợp.

```text
Wiki hiện có nói gì về confirmation bias? Hãy nêu nguồn và các điểm chưa chắc chắn.
```

Câu trả lời tạm thời không làm thay đổi wiki. Khi kết quả tạo ra synthesis có giá trị tái sử dụng, có thể yêu cầu agent lưu kết quả vào wiki.

### 4. Kiểm tra chất lượng

Yêu cầu agent chạy **wiki-lint** để audit và sửa các lỗi cơ học. Có thể chạy structural check trực tiếp:

```bash
python3 tools/wiki_check.py
```

Báo cáo lint được lưu tại `outputs/wiki-lint-YYYY-MM-DD.md`. Các thay đổi wiki hợp lệ phải được index, kiểm tra lại và ghi một entry vào `wiki/log.md`.

## Tìm kiếm QMD (tùy chọn)

QMD là cache tìm kiếm cục bộ cho `wiki/`, không phải nguồn sự thật. Chỉ nên dùng khi wiki lớn hoặc tìm kiếm chính xác không đủ hiệu quả.

Cần Node.js 22+ hoặc Bun 1+ và QMD CLI. Cài đặt sau khi bạn chấp thuận việc cài global package:

```bash
npm install -g @tobilu/qmd
./tools/qmd-update.sh
```

Thêm `--embed` khi cần semantic retrieval:

```bash
./tools/qmd-update.sh --embed
```

File cấu hình `.qmd/index.yml` được theo dõi bởi Git; SQLite index và model tải về là cache cục bộ, đã được bỏ qua bởi `.gitignore`.

## Quy tắc dữ liệu quan trọng

- `raw/` là evidence source of truth; `wiki/` là bản tổng hợp vận hành để truy vấn.
- Không đưa credentials, private key, token, PII hoặc thông tin confidential vào `wiki/`, `outputs/` hay `log.md`.
- Không xem kết quả search là bằng chứng cuối cùng: luôn đọc concept được chọn và kiểm tra metadata, nguồn, trạng thái và mâu thuẫn.
- Lưu insight bền vững vào `wiki/`; chỉ lưu deliverable tạm thời vào `outputs/`.

## Skills và prompts

| Thành phần | Mục đích |
| --- | --- |
| `wiki-init` | Khởi tạo hoặc đổi phạm vi knowledge base qua `SCOPE.md`, rồi chuyển sang ingest/query |
| `wiki-ingest` | Biên dịch nguồn và durable insight vào wiki |
| `wiki-query` | Truy xuất, đánh giá và tổng hợp tri thức |
| `wiki-lint` | Audit và sửa sức khỏe cấu trúc/nội dung của wiki |
| `qmd-setup` | Thiết lập QMD cache cục bộ |
| `qmd-retrieval` | Xếp hạng candidate bằng QMD khi cần |
| `wiki-learn` | Tạo bài viết hướng dẫn cho người mới từ tri thức wiki, theo course profile của domain |
| `read-arxiv-paper` | Lưu TeX source của paper arXiv vào `raw/` rồi ingest vào wiki |

Chi tiết đầy đủ về chính sách và quy trình nằm trong [AGENTS.md](AGENTS.md).
