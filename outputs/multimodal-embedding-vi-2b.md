Dưới đây là các model từ **3B trở xuống** trong danh sách trước (multimodal, hơn 2 ngôn ngữ). Tôi xếp theo kích thước.

## Thông số chính

| Model | Params | Ngôn ngữ (theo nguồn) | Dạng retrieval | Output | Context | Modality | License |
|---|---|---|---|---|---|---|---|
| [pplx-embed-v2-late-0.6b](wiki/pplx-embed-v2-late-0-6b.md) | 0.59B lưu trữ / 340M active | Chỉ ghi "multilingual" | Late-interaction (MaxSim) | 128D/token | Không nêu | Text, ảnh tài liệu | MIT |
| [EmbeddingGemma 2](wiki/embeddinggemma-2.md) | 740M (bản chỉ text: 270M) | Hiểu 100+, train 140+ | Dense, 1 vector | 768D Matryoshka | 8K | Text, code, ảnh, video, audio | Apache 2.0 + Gemma policy |
| [Vintern-Embedding-1B](wiki/vintern-embedding-1b.md) | ~0.9B | **VI**, EN, ZH | Multi-vector | Không công bố | Không công bố | Text, ảnh | Không nêu |
| [Jina v5 Omni Nano](wiki/jina-embeddings-v5-omni-nano.md) | ~1.04B (leaderboard ghi 0.986B) | "multilingual" (đã kiểm chứng ở phía text) | Dense + adapter | 768D | 8K | Text, ảnh, video, audio | Không nêu |
| [Nemotron-3.5-Embed-1B](wiki/nemotron-3-5-embed-1b-bf16.md) | 1.55B | Text 34, ảnh **18** | Dense, query chỉ nhận text | 2,048D | 32K | Text, ảnh, ảnh+text | OpenMDW-1.1 |
| [Jina v5 Omni Small](wiki/jina-embeddings-v5-omni-small.md) | ~1.74B (leaderboard ghi 1.63B) | "multilingual" (phía text) | Dense + adapter | 1,024D (cắt xuống tới 32D) | 32K | Text, ảnh, video, audio | Không nêu |
| [Qwen3-VL-Embedding-2B](wiki/qwen3-vl-embedding-2b.md) | 2B | 30+ | Dense | 64–2,048D Matryoshka | 32K | Text, ảnh, video, input trộn | Không nêu |
| [DNA-VL-STEER-2B](wiki/dna-vl-steer-2b.md) | 2.13B | **36** (có danh sách) | Dense, thay thế trực tiếp cho Qwen3-VL-2B | 64–2,048D | 32K | Text, ảnh, video | Apache 2.0 |
| [Jina Embeddings v4](wiki/jina-embeddings-v4.md) ⚠️ | Base Qwen2.5-VL-3B (tổng số params không công bố) | 30+ | Dense hoặc late-interaction | 2,048D / 128D/token | Không nêu | Text, ảnh, tài liệu | Không nêu |

Bị loại vì số params thực tế vượt 3B dù tên ghi "3B": e5-omni-3B (4.70B), Llama-Nemotron-ColEmbed-3B (~4.4B).

## Kết quả do tác giả công bố (chỉ so được trong cùng một dòng)

| Benchmark | Kết quả |
|---|---|
| **MMEB-v2 (78 task)** | Qwen3-VL-2B: **73.2–73.4** All (Image 75.0) > EmbeddingGemma 2: 59.01 (Image 57.28, VisDoc 67.84) |
| **ViDoRe V3, bảng của NVIDIA (nDCG@10)** | Nemotron-3.5-1B: image **58.02**, MIRACL-VISION 68.93 > Qwen3-VL-2B: 52.89 / 58.42 |
| **ViDoRe V3 public, bảng của Perplexity** | pplx-late-0.6b: 62.3 (Image) / 61.2 (Markdown). Khác protocol với bảng NVIDIA nên không so trực tiếp được |
| **MIEB** | Jina Omni Small 58.00 > Nano 47.87 (Image). DNA-STEER MIEB-Multilingual 67.86 (Qwen gốc 66.71) |
| **Đa ngôn ngữ ảnh↔text (XM3600, 36 ngôn ngữ)** | DNA-STEER R@1 **70.3** so với Qwen3-VL-2B 59.8. Nhóm ngôn ngữ ít tài nguyên: 51.8 so với 32.8 |
| **ViDoRe (V1, protocol không rõ)** | Vintern 82.85 |
| Jina v4 | Card không có điểm số |

## Điểm mạnh và yếu

- **Qwen3-VL-2B:** đa dụng nhất. Có MMEB-v2 cao nhất nhóm, Matryoshka, 32K context, 30+ ngôn ngữ. Đổi lại, các ngôn ngữ ít tài nguyên yếu.
- **DNA-VL-STEER-2B:** giữ nguyên kiến trúc của Qwen nhưng cải thiện mạnh các ngôn ngữ ít tài nguyên (VI, KO, TH, SW…). Kém hơn Qwen gốc ở text-only (−7.9 R@1), phân loại video và tác vụ thị giác chi tiết.
- **Nemotron-3.5-1B:** tốt nhất cho tìm trang tài liệu đa ngôn ngữ bằng một vector, với size nhỏ hơn Qwen-2B mà điểm cao hơn trong bảng của NVIDIA. Query chỉ nhận text, không có video hay audio.
- **pplx-late-0.6b:** nhỏ nhất (340M active), ViDoRe V3 cao. Là late-interaction nên index lớn hơn nhiều. Trang wiki đang ở trạng thái draft và không có danh sách ngôn ngữ.
- **EmbeddingGemma 2:** nhẹ nhất trong nhóm omni (gồm cả audio), nhiều ngôn ngữ nhất, có thể bỏ encoder không dùng. Chất lượng ảnh thấp hơn rõ, và card khuyến cáo không dùng float16.
- **Jina v5 Omni Nano/Small:** dùng khi cần adapter theo task và có video/audio. Đa ngôn ngữ mới được xác lập ở phía text; MIEB không so được với MMEB.
- **Vintern-1B:** model duy nhất liệt kê rõ tiếng Việt. Thiếu thông tin triển khai (số chiều, context, license).
- **Jina v4:** sát ngưỡng 3B, có cả dense và multi-vector nhưng card không có điểm số.

## Gợi ý chọn

| Nhu cầu | Model |
|---|---|
| Mặc định cho ảnh, video, tài liệu tổng quát | Qwen3-VL-Embedding-2B |
| Tiếng Việt hoặc ngôn ngữ ít tài nguyên, ảnh↔text | DNA-VL-STEER-2B; Vintern-1B nếu tiếng Việt là chính |
| Tìm trang PDF/ảnh đa ngôn ngữ, một vector | Nemotron-3.5-Embed-1B |
| Recall tài liệu cao, chấp nhận index lớn | pplx-embed-v2-late-0.6b |
| On-device hoặc cần audio trong cùng index | EmbeddingGemma 2; Jina Omni Nano/Small |

**Lưu ý:** mọi điểm số đều do tác giả công bố và các benchmark khác nhau không quy đổi được. Với tiếng Việt, nên đánh giá DNA-STEER, Vintern, Nemotron-3.5 và Qwen-2B trên chính corpus của bạn. Wiki không thay đổi gì.