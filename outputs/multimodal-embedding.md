## Embedding multimodal (ảnh + text) hỗ trợ hơn 2 ngôn ngữ

Tôi chỉ tra trong wiki, không mở file `raw/`. Wiki có 36 checkpoint embedding multimodal, xem [Multimodal embedding model comparison](wiki/multimodal-embedding-model-comparison.md). Tôi lọc theo nguồn ghi gì về ngôn ngữ, và chia làm ba nhóm theo mức độ chắc chắn.

### Nhóm A: nguồn nêu rõ hơn 2 ngôn ngữ (đếm được hoặc liệt kê)

| Model | Ngôn ngữ | Kiến trúc | Size / output | Kết quả do tác giả công bố |
|---|---|---|---|---|
| [EmbeddingGemma 2](wiki/embeddinggemma-2.md) | Hiểu được 100+, dữ liệu train có 140+ (không cam kết chất lượng đều giữa các ngôn ngữ) | Dense, mean-pool; text, code, ảnh, video, audio | 740M; 768D Matryoshka | MMEB-v2 overall 59.01 (Image 57.28, VisDoc 67.84) |
| [DNA-VL-STEER-2B](wiki/dna-vl-steer-2b.md) | 36 ngôn ngữ XM3600 (đã đánh giá) | Dense; bản hiệu chỉnh của Qwen3-VL-Emb-2B | 2.13B; 64–2,048D | XM3600 image→text R@1 tăng 59.8 → 70.3; nhóm ngôn ngữ ít tài nguyên (LRL-5) tăng 32.8 → 51.8. Bị giảm điểm ở text-only và tác vụ thị giác chi tiết |
| [Nemotron-3.5-Embed-1B](wiki/nemotron-3-5-embed-1b-bf16.md) | Đánh giá text 34 ngôn ngữ, image retrieval 18 ngôn ngữ (có Hàn, Nhật, Thái, Hindi…) | Dense, mean-pool; chỉ nhận query dạng text | 1.55B; 2,048D | ViDoRe V3 image 58.02, MIRACL-VISION 68.93 (nDCG@10, NVIDIA tự chạy) |
| [Qwen3-VL-Embedding-2B](wiki/qwen3-vl-embedding-2b.md) / [8B](wiki/qwen3-vl-embedding-8b.md) | 30+ (không liệt kê cụ thể) | Dense; text, ảnh, video, input trộn | 2B: tới 2,048D; 8B: tới 4,096D Matryoshka; 32K context | MMEB-v2 All: 73.2–73.4 (2B), 77.9 (8B) |
| [Jina Embeddings v4](wiki/jina-embeddings-v4.md) | 30+ (không liệt kê) | Dense hoặc late-interaction, có adapter theo task | Base Qwen2.5-VL-3B; 2,048D dense / 128D token | Model card không có điểm số |
| [EVIE-Preview-4.5B](wiki/evie-preview-4-5b.md) | Query bằng 7 ngôn ngữ: EN, FR, DE, IT, ES, PT, ZH | Late-interaction MaxSim | 4.54B; 128D/token | ViDoRe V3 public 65.36 (khi chạy ở 1,792 visual token) |
| [ColQwen3.5-4.5B-v3](wiki/colqwen3-5-4-5b-v3.md) | 5: EN, FR, DE, ES, ZH | Late-interaction | 4.5B; 320D/token | ViDoRe V3 61.46 (hạng 6 trong bản chụp ngày 2026-04-20) |
| [Vintern-Embedding-1B](wiki/vintern-embedding-1b.md) | 3: **VI**, EN, ZH | Multi-vector | ~0.9B; số chiều không công bố | ViDoRe avg 82.85, không rõ protocol |

### Nhóm B: chỉ ghi "multilingual", không nêu danh sách hay số lượng

Nhiều khả năng hỗ trợ hơn 2 ngôn ngữ, nhưng nguồn chưa chứng minh. Hầu hết là model late-interaction cho tài liệu dạng ảnh:

| Model | Bằng chứng | Kết quả chính |
|---|---|---|
| [webAI-ColVec1.1-4b](wiki/webai-colvec1-1-4b.md) / [8b](wiki/webai-colvec1-1-8b.md) | ViDoRe V3 tính trung bình trên 6 tập con ngôn ngữ (không nêu tên các ngôn ngữ) | V3 final mean 63.90 / 64.95; 640D/token |
| [pplx-embed-v2-late-0.6b](wiki/pplx-embed-v2-late-0-6b.md) / [9b](wiki/pplx-embed-v2-late-9b.md) | Chỉ có tag `multilingual`; trang ở trạng thái draft | ViDoRe V3 public 62.3 / 65.2; 128D/token; license MIT |
| [Nemotron-ColEmbed-VL-8B-v2](wiki/nemotron-colembed-vl-8b-v2.md) | Có dữ liệu synthetic đa ngôn ngữ; có task Finance EN/FR | ViDoRe V3 63.54; 4,096D/token |
| [Llama-Nemotron-ColEmbed-VL-3B-v2](wiki/llama-nemotron-colembed-vl-3b-v2.md) | Ghi "multilingual" | ViDoRe V3 0.5970; 3,072D/token |
| [Tomoro ColQwen3 4B](wiki/tomoro-colqwen3-embed-4b.md) / [8B](wiki/tomoro-colqwen3-embed-8b.md) | Có tách riêng bộ ViDoRe V3 multilingual | V3 multilingual nDCG@5: 0.5708 / 0.5866 |
| [Jina v5 Omni Nano](wiki/jina-embeddings-v5-omni-nano.md) / [Small](wiki/jina-embeddings-v5-omni-small.md) | Text được align với Jina v5 Text (đa ngôn ngữ); với ảnh, video, audio thì card không xác lập được ngôn ngữ | MIEB Image 47.87 / 58.00; MTEB Multilingual v2: 65.52 / 67.00 |
| [e5-omni](wiki/e5-omni.md) | Train trên cặp text BGE-M3; ví dụ có multilingual text retrieval | MMEB-v2 66.4 (bản 7B) |

### Nhóm C: bị loại, chỉ 1–2 ngôn ngữ hoặc nguồn không nêu

- **ZH + EN:** WeMM-Embedding, Tianmu-Emb-Uni-8B.
- **Chỉ EN:** Omni-Embed-Nemotron-3B.
- **Dữ liệu train nặng EN/ZH:** UEmbed.
- **Phần lớn target là EN:** Sentio, Wianmu-3B/5B.
- **Không nêu ngôn ngữ:** Ovis-VL/Omni, GeeVec, AuroLA-Omni-3B.

WeMM có MMEB-v2 cao nhất (9B đạt 80.6) nhưng không qua tiêu chí ngôn ngữ.

### So sánh và chọn model
- **Ngôn ngữ ít tài nguyên (Hàn, Thái…):** DNA-VL-STEER-2B là model duy nhất có số đo theo từng ngôn ngữ trên 36 ngôn ngữ. Đổi lại, nó yếu hơn model gốc ở text-only.
- **Ảnh, video, visual-document tổng quát:** Qwen3-VL-Embedding-8B (77.9) có điểm MMEB-v2 cao nhất trong số các model qua tiêu chí 30+ ngôn ngữ.
- **Tìm trang tài liệu đa ngôn ngữ bằng một vector duy nhất, model nhỏ:** Nemotron-3.5-Embed-1B. Nó có danh sách 18 ngôn ngữ ảnh rõ ràng, và trong bảng của NVIDIA thì vượt Qwen3-VL-2B.
- **Recall cao nhất trên PDF hoặc ảnh trang (chấp nhận index lớn):** pplx-late-9b, EVIE, webAI-8b và Nemotron-Col-8B đều ở khoảng 63.5–65.4 trên ViDoRe V3. Protocol và token budget giữa các bảng khác nhau nên chưa xếp hạng chặt được.
- **Ưu tiên tiếng Việt:** Vintern-Embedding-1B là model duy nhất liệt kê rõ VI.
- **Chạy on-device, bao phủ nhiều ngôn ngữ nhất:** EmbeddingGemma 2 (100+), nhưng chất lượng ảnh thấp hơn rõ so với Qwen.

### Giới hạn
- Gần như mọi điểm số đều do tác giả hoặc vendor tự công bố, không có đánh giá độc lập chung.
- Chỉ so được điểm trong cùng một benchmark, phiên bản và metric. MMEB-v2, ViDoRe V3 và MIEB không quy đổi qua lại được.
- Phần lớn claim "30+" hay "multilingual" không liệt kê ngôn ngữ. Card cũng hiếm khi nói khả năng đa ngôn ngữ áp dụng cho phía ảnh hay chỉ cho text.
- Model không có trong wiki không có nghĩa là không tồn tại, chỉ là chưa được ingest.

Wiki không thay đổi gì. Bảng lọc theo ngôn ngữ này có thể lưu thành mục mới trong [trang so sánh](wiki/multimodal-embedding-model-comparison.md) qua `wiki-ingest` nếu bạn muốn.