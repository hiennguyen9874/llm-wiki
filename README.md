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
raw/       Nguồn gốc, bất biến sau khi được đưa vào repository
wiki/      Tri thức đã được tổng hợp theo OKF v0.2
  index.md Catalog đầy đủ, điểm vào cho truy vấn
  log.md   Lịch sử thay đổi theo thứ tự mới nhất
outputs/   Báo cáo và kết quả tạm thời được yêu cầu
.pi/       Skills và prompt cho agent
.qmd/      Cấu hình cache tìm kiếm QMD (database tạo ra chỉ lưu cục bộ)
tools/     Script kiểm tra cấu trúc và cập nhật QMD
```

`LLM-WIKI.md` là contract trung tâm: định nghĩa phạm vi, quyền sở hữu dữ liệu, định dạng concept, retrieval policy và các bất biến khi thay đổi wiki.

## Cách dùng cơ bản

### 1. Mở kho tri thức

Clone repository, sau đó mở thư mục bằng Obsidian nếu muốn duyệt và chỉnh sửa Markdown trực quan:

```bash
git clone <repository-url>
cd llm-wiki
```

Đọc `LLM-WIKI.md` trước khi thay đổi nội dung để tuân thủ quy ước của kho.

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
| `wiki-ingest` | Biên dịch nguồn và durable insight vào wiki |
| `wiki-query` | Truy xuất, đánh giá và tổng hợp tri thức |
| `wiki-lint` | Audit và sửa sức khỏe cấu trúc/nội dung của wiki |
| `qmd-setup` | Thiết lập QMD cache cục bộ |
| `qmd-retrieval` | Xếp hạng candidate bằng QMD khi cần |
| `wiki-learn` | Tạo bài viết hướng dẫn cho người mới từ tri thức wiki |

Chi tiết đầy đủ về chính sách và quy trình nằm trong [LLM-WIKI.md](LLM-WIKI.md).
