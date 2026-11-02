---
type: Synthesis
title: So sánh benchmark các model embedding trong wiki
description: Bản đối chiếu text, multimodal và late-interaction embedding theo từng benchmark, snapshot và protocol, kèm phạm vi model và giới hạn bằng chứng.
tags: [embedding, benchmark, retrieval, multimodal, comparison, synthesis]
status: draft
created: 2026-11-02
generated: { by: llm-wiki-agent/1, at: 2026-11-02T04:55:00Z }
stale_after: 2027-01-31
sources:
  - id: catalog
    resource: index.md
    kind: wiki
    title: Wiki model catalog
  - id: text-snapshot
    resource: ../raw/MTEB_Multilingual_v2_summary.csv
    kind: dataset
    title: MTEB Multilingual v2 summary CSV
  - id: f2-report
    resource: ../raw/2603.19223_F2LLM-v2/main.tex
    scope: ../raw/2603.19223_F2LLM-v2/
    kind: paper
    title: F2LLM-v2 technical report
  - id: qwen-report
    resource: ../raw/2506.05176_Qwen3Embedding/main.tex
    kind: paper
    title: Qwen3 Embedding technical report
  - id: harrier
    resource: harrier-oss-v1-0-6b.md
    kind: wiki
    title: Harrier family model card concept
  - id: octen
    resource: octen-embedding-8b.md
    kind: wiki
    title: Octen Embedding 8B concept
  - id: octen-06
    resource: octen-embedding-0-6b.md
    kind: wiki
    title: Octen Embedding 0.6B concept
  - id: nvidia-text-1
    resource: nemotron-3-embed-1b-bf16.md
    kind: wiki
    title: Nemotron 3 Embed 1B concept
  - id: nvidia-text-8
    resource: nemotron-3-embed-8b-bf16.md
    kind: wiki
    title: Nemotron 3 Embed 8B concept
  - id: llama
    resource: llama-embed-nemotron-8b.md
    kind: wiki
    title: Llama Embed Nemotron 8B concept
  - id: kalm
    resource: kalm-embedding-gemma3-12b-2511.md
    kind: wiki
    title: KaLM Embedding Gemma3 12B concept
  - id: granite-97
    resource: granite-embedding-97m-multilingual-r2.md
    kind: wiki
    title: Granite 97M concept
  - id: granite-311
    resource: granite-embedding-311m-multilingual-r2.md
    kind: wiki
    title: Granite 311M concept
  - id: lfm
    resource: lfm2-5-colbert-350m.md
    kind: wiki
    title: LFM ColBERT concept
  - id: lfm-dense
    resource: lfm2-5-embedding-350m.md
    kind: wiki
    title: LFM dense concept
  - id: mlateon
    resource: mlateon.md
    kind: wiki
    title: mLateOn concept
  - id: deepx
    resource: deepx-embedding-v1.md
    kind: wiki
    title: DeepX concept
  - id: dek21
    resource: dek21-hcmute-embedding.md
    kind: wiki
    title: DEk21 concept
  - id: vietnamese
    resource: vietnamese-embedding.md
    kind: wiki
    title: Vietnamese Embedding concept
  - id: jina-code-05
    resource: jina-code-embeddings-0-5b.md
    kind: wiki
    title: Jina Code 0.5B concept
  - id: jina-code-15
    resource: jina-code-embeddings-1-5b.md
    kind: wiki
    title: Jina Code 1.5B concept
  - id: context-preview
    resource: pplx-embed-v2-context-9b-preview.md
    kind: wiki
    title: Perplexity contextual preview concept
  - id: multimodal-comparison
    resource: multimodal-embedding-model-comparison.md
    kind: wiki
    title: Multimodal embedding model comparison
  - id: wemm
    resource: ../raw/WeMM-Embedding/README.md
    kind: documentation
    title: WeMM evaluation tables
  - id: ovis-vl-image
    resource: ../raw/benchmark-figures-2026-11-02/ovis-vl.png
    kind: image
    title: Ovis VL MMEB-v2 table image
  - id: ovis-omni-image
    resource: ../raw/benchmark-figures-2026-11-02/ovis-omni.png
    kind: image
    title: Ovis Omni MMEB-v3 table image
  - id: geevec
    resource: geevec-embeddings-mm-1-0.md
    kind: wiki
    title: GeeVec concept
  - id: sentio
    resource: sentio.md
    kind: wiki
    title: Sentio concept
  - id: mmeb-snapshot
    resource: mmeb-v3-ranking-snapshot.md
    kind: wiki
    title: MMEB v3 ranking snapshot concept
  - id: e5
    resource: e5-omni.md
    kind: wiki
    title: e5-omni concept
  - id: jina-report
    resource: ../raw/2605.08384_jina-embeddings-v5-omni/main.tex
    scope: ../raw/2605.08384_jina-embeddings-v5-omni/
    kind: paper
    title: Jina v5 Omni report
  - id: jina-figure
    resource: ../raw/benchmark-figures-2026-11-02/jina-frontier.png
    kind: image
    title: Jina Omni card frontier figure
  - id: nemotron-visual
    resource: nemotron-3-5-embed-1b-bf16.md
    kind: wiki
    title: Nemotron 3.5 Embed 1B concept
  - id: webai4
    resource: webai-colvec1-1-4b.md
    kind: wiki
    title: webAI ColVec 4B concept
  - id: webai8
    resource: webai-colvec1-1-8b.md
    kind: wiki
    title: webAI ColVec 8B concept
  - id: evie
    resource: evie-preview-4-5b.md
    kind: wiki
    title: EVIE visual retrieval concept
  - id: pplx-late
    resource: pplx-embed-v2-late-0-6b.md
    kind: wiki
    title: Perplexity late interaction concept
  - id: tomoro
    resource: tomoro-colqwen3-embed-8b.md
    kind: wiki
    title: Tomoro 8B concept
  - id: dna
    resource: dna-vl-steer-2b.md
    kind: wiki
    title: DNA VL STEER concept
  - id: community
    resource: translation-memory-embedding-reranker-pairing-benchmark.md
    kind: wiki
    title: Translation memory community benchmark
---

# So sánh benchmark các model embedding trong wiki

Tổng hợp ngày 2026-11-02 cho các model text, code, multimodal, contextual và late-interaction được mô tả trong wiki, kể cả checkpoint thuộc family chỉ có một concept chung. Không có benchmark chung cho tất cả: **không suy ra một bảng xếp hạng toàn cục**. Số liệu là **Reported** từ model card/paper/snapshot, chưa được chạy lại; diễn giải và gợi ý chọn model là **Synthesis**. Danh mục gồm concept model, không biến mọi baseline chỉ xuất hiện trong leaderboard thành model đã được wiki mô tả.[^catalog][^multimodal-comparison]

## Cách đọc và phạm vi

- So sánh ưu tiên **cùng một bảng nguồn, tập, metric và cấu hình**. MTEB Mean (Task) là đa nhiệm, không đồng nghĩa retrieval-only; nDCG@5 khác nDCG@10; điểm 0–1 chỉ được nhân 100 khi giữ nguyên metric.
- MMEB-v2 78 dataset, MMEB-v2 44 dataset retrieval-only, MMEB-v3 190 task, và ViDoRe là các phép đo khác nhau. Không trộn điểm. Visual-token budget, image resolution, query instruction, split, precision và hỗ trợ modality làm thay đổi kết quả.
- Reranker cross-encoder không thuộc phạm vi; ColBERT/MaxSim là embedding multi-vector và được tính. mmBERT-small là backbone; GELATO là phương pháp, không tính là checkpoint. Model có tên trong family nhưng chưa có concept riêng được gắn nhãn; `—` là chưa tìm thấy điểm cùng protocol, không có nghĩa model kém hoặc bằng 0.[^catalog][^multimodal-comparison]
- Snapshot MTEB không ghi ngày chụp, task/config cụ thể hoặc nguồn phát hành. `Rank` **không đơn điệu theo Mean (Task)**: harrier-270M 66.55 có rank 8 nhưng F2LLM-1.7B 65.21 có rank 6. Chỉ sắp xếp lại các con số hiện có, không gọi đó là rank gốc hay kết quả leaderboard mới nhất.[^text-snapshot]

## Text: snapshot MTEB Multilingual v2

Cột **Mean** và **Retrieval** sao chép từ cùng CSV, sắp theo Mean giảm dần; retrieval là cột task-type, không phải toàn bộ Mean. Các giá trị không chứng minh kết quả trên tiếng Việt hay một workload cụ thể.[^text-snapshot]

| Model | Params lớp công bố | Mean | Retrieval |
|---|---:|---:|---:|
| [Qwen3-Embedding-4B](qwen3-embedding-4b.md) | 4B | 69.45 | 69.60 |
| [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md) | 0.6B | 69.01 | 70.75 |
| [F2LLM-v2-4B](f2llm-v2.md) | 4B | 67.06 | 64.84 |
| [Jina v5 Text Small](jina-embeddings-v5-text-small.md) | 677M | 67.00 | 64.88 |
| [harrier-oss-v1-270m](harrier-oss-v1-270m.md) | 270M | 66.55 | 66.38 |
| [Jina v5 Text Nano](jina-embeddings-v5-text-nano.md) | 239M | 65.52 | 63.26 |
| [F2LLM-v2-1.7B](f2llm-v2.md) | 1.7B | 65.21 | 61.97 |
| [Qwen3-Embedding-0.6B](qwen3-embedding-0-6b.md) | 0.6B | 64.34 | 64.65 |
| [F2LLM-v2-0.6B](f2llm-v2.md) | 0.6B | 62.74 | 59.30 |
| [EmbeddingGemma 300M](embeddinggemma-300m.md) | 300M | 61.15 | 62.49 |
| [F2LLM-v2-330M](f2llm-v2.md) | 330M | 60.84 | 56.50 |
| [F2LLM-v2-160M](f2llm-v2.md) | 160M | 57.98 | 54.08 |
| [Granite 311M R2](granite-embedding-311m-multilingual-r2.md) | 311M | 55.96 | 65.21 |

Jina Omni Small/Nano có cùng các cột text lần lượt **67.00/64.88** và **65.52/63.26** như text sibling trong CSV; không biết đây là lần đánh giá độc lập hay sử dụng kết quả shared tower. Jina Text Small card lại nêu 67.7, khác report/CSV 67.0; không tự hòa giải. CSV ghi CC-BY-NC-4.0 cho Jina v5 text/omni, cần kiểm tra điều khoản checkpoint trước thương mại.[^text-snapshot][^jina-report]

### Text: các model không có dòng tương ứng trong snapshot

| Model / family | Kết quả riêng và giới hạn |
|---|---|
| [Qwen3-Embedding-8B](qwen3-embedding-8b.md) | Report: Multilingual 70.58; English v2 75.22; Code v1 80.68. Báo cáo 131 multilingual tasks; không có hàng 8B trong CSV trên.[^qwen-report] |
| [F2LLM-v2](f2llm-v2.md) **80M / 8B / 14B** | Report: multilingual 55.23 / 68.09 / 68.74; eight-size family cũng bao gồm các variant trong CSV. Giá trị từ bảng ngày truy cập leaderboard 2026-03-19, không tự ghép thành rank chung với snapshot không ngày.[^f2-report] |
| [harrier-oss-v1 27B](harrier-oss-v1-0-6b.md) | Family card báo Multilingual MTEB v2 **74.3**; 27B chỉ được mô tả như sibling trong card, không có concept/checkpoint riêng trong wiki và không có hàng trong CSV.[^harrier] |
| [Llama-Embed-Nemotron-8B](llama-embed-nemotron-8b.md) | Bảng MMTEB v2 131 task ngày 2025-10-21: Mean 69.46, Borda #1; Qwen3-8B 70.58 nhưng Borda #3. Borda không phải mean score.[^llama] |
| [KaLM-Embedding-Gemma3-12B](kalm-embedding-gemma3-12b-2511.md) | Card: MMTEB Mean 72.32, Retrieval 75.66; chưa rõ release, task set, protocol, không xếp chung CSV.[^kalm] |
| [Octen 0.6B](octen-embedding-0-6b.md) / [4B](octen-embedding-4b.md) / [8B](octen-embedding-8b.md) | Octen card RTEB snapshot 2026-01-12: 8B **80.45**, 4B **78.34**, Qwen3-8B **75.47**, Jina v4 **71.05** Mean (Task), gốc 0–1; 0.6B chỉ có Public 72.41, không có Mean để xếp cùng.[^octen][^octen-06] |
| [Nemotron-3-Embed-1B](nemotron-3-embed-1b-bf16.md) / [8B](nemotron-3-embed-8b-bf16.md) | Card: RTEB 16 public task NDCG@10 **72.38 / 78.46**, MMTEB retrieval **71.04 / 75.45**, ở 4,096 tokens. Không xếp với Octen Public+Private Mean hoặc cột Retrieval CSV vì protocol chưa được xác nhận giống nhau.[^nvidia-text-1][^nvidia-text-8] |
| [Granite 97M R2](granite-embedding-97m-multilingual-r2.md) / [311M R2](granite-embedding-311m-multilingual-r2.md) | IBM table: Multilingual MTEB Retrieval 18 tasks **60.3 / 65.2**. 311M có bảng truncation khác báo 63.9 tại full 768D, chưa giải thích.[^granite-97][^granite-311] |
| [LFM2.5 dense 350M](lfm2-5-embedding-350m.md) / [ColBERT 350M](lfm2-5-colbert-350m.md) | Vendor NanoBEIR multilingual nDCG@10 **57.7 / 60.5**, MKQA-11 Recall@20 **69.1 / 69.4**. ColBERT dùng nhiều vector, không có cùng chi phí index.[^lfm-dense][^lfm] |
| [mLateOn](mlateon.md) | Card nDCG@10: BEIR 57.56, MIRACL all languages 67.04, MLDR all languages 77.92, MTEB Code 73.48; không ghép với NanoBEIR/MKQA.[^mlateon] |
| [DeepX](deepx-embedding-v1.md) / [DEk21](dek21-hcmute-embedding.md) / [Vietnamese_Embedding](vietnamese-embedding.md) | Các model pháp lý tiếng Việt báo Zalo nDCG@10 0.8162; VMTEB-Zalo word-segmented nDCG@10 0.785101; Legal Zalo 2021 MRR@10 0.8181 tương ứng. Split/segmentation/metric khác; **không xếp trực tiếp**. DeepX có nêu Zalo trong metadata training.[^deepx][^dek21][^vietnamese] |
| [Jina Code 0.5B](jina-code-embeddings-0-5b.md) / [1.5B](jina-code-embeddings-1-5b.md) | Hai card không có benchmark số; chuyên code nhưng không suy ra mạnh hơn model khác.[^jina-code-05][^jina-code-15] |
| [pplx-context-9b-preview](pplx-embed-v2-context-9b-preview.md) | Contextual chunk embedding, không có benchmark số trong capture; không chứng minh tương thích với bản 9B non-preview.[^context-preview] |

### F2LLM-v2: tiếng Việt và code trong cùng report

Bảng của tác giả, leaderboard accessed 2026-03-19, gồm Multilingual 131 task, Vietnamese 50 task và Code 12 task; không coi cột Vietnamese là retrieval-only.[^f2-report]

| F2LLM-v2 | Multilingual | Vietnamese | Code |
|---|---:|---:|---:|
| 80M | 55.23 | 50.52 | 67.97 |
| 160M | 57.98 | 52.56 | 70.38 |
| 330M | 60.84 | 57.46 | 75.74 |
| 0.6B | 62.74 | 59.56 | 77.41 |
| 1.7B | 65.21 | 61.54 | 78.76 |
| 4B | 67.06 | 62.74 | 80.15 |
| 8B | 68.09 | 63.32 | 80.16 |
| 14B | 68.74 | 63.56 | 80.75 |

## Multimodal dense: MMEB-v2 78 dataset

Bảng đầu là **một bảng WeMM**: Image/Video Hit@1, VisDoc nDCG@5, AVG trên 78 dataset, toàn bộ do tác giả công bố; chữ B là class chứ không nhất thiết là tổng tham số checkpoint.[^wemm]

| Model | Image | Video | VisDoc | AVG |
|---|---:|---:|---:|---:|
| [WeMM 9B](wemm-embedding.md) | 81.9 | 74.3 | 83.3 | 80.6 |
| [WeMM 4B](wemm-embedding.md) | 80.8 | 72.1 | 82.0 | 79.2 |
| [WeMM 2B](wemm-embedding.md) | 79.6 | 70.8 | 80.7 | 77.9 |
| [Qwen3-VL 8B](qwen3-vl-embedding-8b.md) | 80.1 | 67.1 | 82.4 | 77.8 |
| [Qwen3-VL 2B](qwen3-vl-embedding-2b.md) | 75.0 | 61.9 | 79.2 | 73.2 |

**Bảng Ovis VL được đọc từ ảnh** cùng tên benchmark nhưng khác nguồn/cấu hình chưa đối chiếu: [Ovis-VL-2B](ovis-vl-embedding-2b.md) **77.46**, UEmbed-2B dense **66.49**, Qwen3-VL-2B **73.25**, DME-Small **74.75**, Octen-VL **75.42**. Ovis Image/Video/VisDoc **80.62/67.12/80.47**. Bảng không chứa WeMM hay Qwen 8B; khác biệt nhỏ giữa bảng độc lập không chứng minh thứ hạng có ý nghĩa thống kê.[^ovis-vl-image]

Bằng chứng riêng: [UEmbed](uembed.md) 2B/4B/9B dense **66.5/70.4/71.8**, sparse **65.5/69.7/71.0**; [e5-omni](e5-omni.md) 3B/7B **63.1/66.4**; [EmbeddingGemma 2](embeddinggemma-2.md) **59.01** với protocol card chưa nêu đủ. Không xem là phép chạy chung với bảng WeMM.[^multimodal-comparison][^e5]

### MMEB-v2 retrieval-only: 44 dataset

Card GeeVec công bố AVG equal-weight, Image/Video Hit@1, VisDoc nDCG@5: [Sentio](sentio.md) **79.57**, [WeMM 9B](wemm-embedding.md) **79.38**, [GeeVec 9.41B](geevec-embeddings-mm-1-0.md) **78.78**, [WeMM 4B](wemm-embedding.md) **78.19**, [Wianmu-5B](wianmu-5b.md) **77.89**, [Qwen3-VL 8B](qwen3-vl-embedding-8b.md) **77.28**. GeeVec Image **81.82**, VisDoc **83.63** cao nhất bảng nhưng Video **59.66** dưới WeMM 9B **64.03** và Sentio **65.45**. Đây là tập con 44, không so thẳng với AVG 78 phía trên.[^geevec]

## Omni và MMEB-v3: giữ riêng nguồn

**Bảng ảnh Ovis**, 190 dataset, text/image/video/visdoc/audio/agent: Ovis-Omni-3B **58.46** overall và **50.08** audio; Tianmu **53.27/38.94**; e5-omni-7B **47.14/43.04**; Omni-Embed-Nemotron **43.60/36.52**; LCO-7B **43.14/43.17**. Bảng không có Sentio hoặc Wianmu.[^ovis-omni-image]

**Bảng Sentio**, snapshot 2026-10-16, 190 task: Sentio **61.69** overall / **36.81** audio; Wianmu-5B **60.45 / 42.93**; WeMM-9B **59.33 / —**; Wianmu-3B **58.16 / 41.16**. Sentio có tổng thể cao nhất trong bảng nhưng audio thấp hơn hai Wianmu; card nói các adapter weights cần thiết không được phân phối trong repo, và audio tower có license riêng. Không ghép số này với bảng Ovis để lập rank chung.[^sentio]

**CSV MMEB-v3 89 entries** không ghi ngày snapshot/protocol: Tianmu Overall **52.83**; UEmbed-9B hybrid **51.54**, dense **51.50**; UEmbed-4B dense **50.10**; UEmbed-2B dense **47.82**; e5-omni 7B/3B **46.53/44.03**; Omni-Embed **42.83**. Chỉ 13/89 có cột v3 nonzero; 0 có thể là thiếu đánh giá, không mặc định thất bại. Ovis v0.1 **52.55** không chứng minh là cùng checkpoint với card 58.46.[^mmeb-snapshot]

**Paper Jina**, bảng bốn modality với MMEB-video **subset 9 task**: [Omni Nano](jina-embeddings-v5-omni-nano.md) text/image/video/audio **65.52/47.87/26.87/49.69**, trung bình **47.49**; [Omni Small](jina-embeddings-v5-omni-small.md) **67.00/58.00/41.20/49.96**, trung bình **54.04**. Không trộn với MMEB-v3 hoặc trung bình ba modality trong ảnh card.[^jina-report]

Riêng [AuroLA-Omni-3B](aurola-omni-3b.md) báo Average 46.7 nhưng thiếu task count/aggregation; không xếp vào ba bảng trên. [Tianmu](tianmu-emb-uni-8b.md) có bất nhất về bundled weights; [Jina v5 Omni Nano/Small](jina-embeddings-v5-omni-small.md) có thể bỏ tower không dùng; [EmbeddingGemma 2](embeddinggemma-2.md) 740M hỗ trợ audio/video. `main` upstream figure là bản có thể thay đổi.[^multimodal-comparison]

### Ảnh và nguồn kiểm tra

- Ovis VL và Omni là các bảng ảnh được tải từ URL `resolve/main` trong model-page capture ngày 2026-11-02 và lưu bất biến tại `raw/benchmark-figures-2026-11-02/`; chi tiết URL/hash ở hai concept Ovis. Các bảng cung cấp tên baseline trước đây wiki bỏ trống.[^ovis-vl-image][^ovis-omni-image]
- Hai hình [e5 MMEB-v2](../raw/benchmark-figures-2026-11-02/e5-mmeb.png) / [AudioCaps](../raw/benchmark-figures-2026-11-02/e5-audiocaps.png) đã được đọc: AudioCaps text→audio R@1 e5 3B **34.3**, 7B **37.7**, Omni-Embed **20.5**; không trộn với MAEB hoặc MMEB Audio. Bản 3B và 7B có ảnh byte-identical.[^e5]
- [Ảnh Jina card](../raw/benchmark-figures-2026-11-02/jina-frontier.png) vẽ image/video/audio và không gắn nhãn số từng điểm; [paper frontier](../raw/2605.08384_jina-embeddings-v5-omni/figures/omni_average_frontier.pdf) cộng thêm text. Paper Table `omni-frontier`: Nano **47.49**, Small **54.04** theo bốn cột; không chuyển điểm giữa hai biểu đồ. Cả hai là author-reported.[^jina-figure][^jina-report]
- [WeMM performance-overview PDF](../raw/WeMM-Embedding/2608.24053-WeMM-Embedding/figs/performance-overview.pdf) và [MRL PNG](../raw/WeMM-Embedding/2608.24053-WeMM-Embedding/figs/mrl-performance-trend.png) đã được đọc trực quan; phù hợp xu hướng nêu trong [concept WeMM](wemm-embedding.md).[^wemm]

## Visual-document late interaction

Các giá trị là **Reported**; các cột trong mỗi nhóm dưới đây khác split, token budget, hoặc metric nên không tạo leaderboard chung. Chi phí index tăng theo số token × số chiều, không so 128D/token như 2,048D/vector dense.[^multimodal-comparison]

| Model | Điểm và cấu hình |
|---|---|
| [pplx-late 0.6B / 9B](pplx-embed-v2-late-0-6b.md) | Cùng bảng public ViDoRe v3 nDCG@10: image **62.3/65.2**, markdown **61.2/64.7**; 128D/token, budget không nêu; shared space theo card.[^pplx-late] |
| [EVIE 4.5B](evie-preview-4-5b.md) | Public ViDoRe v3 nDCG@10 **64.56** tại 768 visual token; **65.36** tại 1,792. Không so 65.36 với các cấu hình chưa biết budget.[^evie] |
| [webAI-ColVec1.1 4B / 8B](webai-colvec1-1-8b.md) | ViDoRe v3 **63.90 / 64.95** final mean, 1,792 token; 640D/token; public 64.24/65.32.[^webai4][^webai8] |
| [ColQwen3.5 4.5B v3](colqwen3-5-4-5b-v3.md) | ViDoRe v3 Mean(Task) **61.46**, 320D/token; snapshot và setup khác.[^multimodal-comparison] |
| [Llama-Nemotron-ColEmbed-VL-3B-v2](llama-nemotron-colembed-vl-3b-v2.md) / [Nemotron-ColEmbed-VL-8B-v2](nemotron-colembed-vl-8b-v2.md) | ViDoRe v3 nDCG@10 **59.70 / 63.54**, 3,072/4,096D/token; các card và configs riêng.[^multimodal-comparison] |
| [Tomoro 4B / 8B](tomoro-colqwen3-embed-8b.md) | ViDoRe v3 multilingual **0.5708/0.5866 nDCG@5**; khác @10. 320D/token và visual budget riêng.[^multimodal-comparison][^tomoro] |
| [Vintern-Embedding-1B](vintern-embedding-1b.md) | Vietnamese/English/Chinese; ViDoRe **82.85** nhưng version/protocol không rõ. Không đặt cạnh v3 ở trên.[^multimodal-comparison] |
| [Jina Embeddings v4](jina-embeddings-v4.md) | Có dense 2,048D và multi-vector 128D; card riêng không có điểm. Octen card liệt kê RTEB Mean(Task) **71.05**, nhưng không phải ViDoRe.[^multimodal-comparison][^octen] |
| [pplx-context 0.6B / 9B](pplx-embed-v2-context-0-6b.md) | Các vector chunk/band dense, không phải MaxSim; card chưa có benchmark số. 9B preview là checkpoint khác.[^multimodal-comparison][^context-preview] |

NVIDIA chạy cùng một bảng **dense** [Nemotron-3.5-Embed-1B](nemotron-3-5-embed-1b-bf16.md) vs Qwen3-VL 2B/8B: ViDoRe v3 image nDCG@10 **58.02 / 52.89 / 58.29**, MIRACL-VISION image **68.93 / 58.42 / 68.33**; ViDoRe gồm 8 public + 2 private, resolution hai family khác. Không gộp với ViDoRe public ở bảng late-interaction.[^nemotron-visual]

## Phủ toàn bộ model và lựa chọn

Ngoài các bảng trên, các checkpoint multimodal đã biên soạn gồm [Qwen3-VL 2B/8B](qwen3-vl-embedding-2b.md), [WeMM 2B/4B/9B](wemm-embedding.md), [UEmbed 2B/4B/9B](uembed.md), [Ovis VL 2B](ovis-vl-embedding-2b.md), [Ovis Omni 3B](ovis-omni-embedding-3b.md), [DNA-VL-STEER-2B](dna-vl-steer-2b.md), [EmbeddingGemma 2](embeddinggemma-2.md), [GeeVec](geevec-embeddings-mm-1-0.md), [Nemotron-3.5-Embed-1B](nemotron-3-5-embed-1b-bf16.md), [Tianmu](tianmu-emb-uni-8b.md), [Sentio](sentio.md), [Wianmu 3B/5B](wianmu-3b.md), [e5-omni 3B/7B](e5-omni.md), [AuroLA](aurola-omni-3b.md), [Omni-Embed-Nemotron](omni-embed-nemotron-3b.md), [Jina v4](jina-embeddings-v4.md), [Jina v5 Omni Nano/Small](jina-embeddings-v5-omni-small.md), và tất cả model late/contextual trong bảng. Variant 9B UEmbed và các variant trong các family có thể không có trang riêng; xem ma trận từng checkpoint trong [multimodal comparison](multimodal-embedding-model-comparison.md).[^multimodal-comparison]

**Synthesis, shortlist cần thử trên dữ liệu thật:**

- Text multilingual nhỏ: harrier 270M hoặc 0.6B; dùng Qwen3-4B / F2LLM-v2 4B để đối chứng. Khác biệt số snapshot không thay cho đánh giá retrieval tiếng Việt.[^text-snapshot]
- Vietnamese legal: thử DeepX, DEk21, Vietnamese_Embedding cùng split mới và có decontamination; không kết luận từ các điểm Zalo không cùng protocol.[^deepx][^dek21][^vietnamese]
- Text+ảnh/video dense: WeMM khi chất lượng MMEB-v2 và hai ngôn ngữ được liệt kê phù hợp; Qwen3-VL khi cần claim 30+ languages; cân nhắc Ovis-VL-2B và Nemotron-3.5-Embed-1B cho visual pages. Language claim không bảo đảm chất lượng tiếng Việt.[^multimodal-comparison][^nemotron-visual]
- Cross-language image/text: DNA-VL-STEER tự báo XM3600 36 ngôn ngữ image→text R@1 **59.8→70.3**, nhưng đánh đổi text-only và phân biệt hình fine-grained; có calibrate trên XM3600, cần đánh giá độc lập.[^dna]
- Audio+image+video: benchmark Ovis Omni, Jina Omni, e5, Wianmu theo audio retrieval thực tế; Sentio báo tổng thể tốt nhưng thiếu adapter weights trong capture. Mỗi model có license/training/hardware khác.[^ovis-omni-image][^sentio][^jina-report][^e5]
- PDF/chart: thử pplx-late nhỏ, EVIE hoặc webAI với cùng page rendering và token budget; thêm dense Nemotron làm baseline, đo recall và cả chi phí lưu/trễ. Trường hợp dùng F2LLM+zerank cho translation memory có MRR **0.919/0.922**, nhưng là kết quả pipeline từ một báo cáo community dữ liệu riêng, không chứng minh embedding đơn lẻ tốt nhất.[^pplx-late][^evie][^community]

## Relationships

- **Uses:** [MTEB Multilingual v2 snapshot](mteb-multilingual-v2-leaderboard-snapshot.md), [MMEB v3 snapshot](mmeb-v3-ranking-snapshot.md), [Multimodal embedding model comparison](multimodal-embedding-model-comparison.md).
- **Complements:** [embedding architecture taxonomy](embedding-model-architecture-taxonomy.md) và [translation-memory pairing benchmark](translation-memory-embedding-reranker-pairing-benchmark.md).

## Giới hạn

Các nguồn và benchmark chỉ là bằng chứng tự báo hoặc snapshot không xác thực; không chạy model hay đo latency/VRAM, không kiểm định thống kê và không khẳng định leaderboard hiện tại. Một số ảnh khác, paper, code, dataset và weights không được kiểm tra; các card có ghi thiếu protocol không thể được bổ sung bằng suy đoán. Các ảnh tải từ `main` là snapshot ngày 2026-11-02, không có commit bất biến từ nguồn. Bản này `draft` vì phạm vi benchmark và protocol còn thiếu.

[^catalog]: [Catalog](index.md), toàn bộ mục Concepts, đã kiểm tra bằng `tools/wiki_check.py` ngày 2026-11-02.
[^text-snapshot]: [CSV MTEB Multilingual v2](../raw/MTEB_Multilingual_v2_summary.csv), các trường `Model`, `Rank`, `Mean (Task)`, `Retrieval`, `License`. Snapshot không nêu publisher, capture date hoặc task configuration.
[^f2-report]: [F2LLM report](../raw/2603.19223_F2LLM-v2/main.tex), `tables/results.tex` bảng multilingual 80M/8B/14B và ngày truy cập leaderboard. Author-reported.
[^qwen-report]: [Qwen3 report](../raw/2506.05176_Qwen3Embedding/main.tex), evaluation tables; xem [Qwen3 8B](qwen3-embedding-8b.md) mục Benchmarks. Author-reported.
[^harrier]: [harrier-oss-v1-0.6b](harrier-oss-v1-0-6b.md), Benchmarks family table, 27B row; author-reported.
[^octen]: [Octen 8B](octen-embedding-8b.md), Benchmarks, RTEB table; author-reported snapshot 2026-01-12.
[^octen-06]: [Octen 0.6B](octen-embedding-0-6b.md), Benchmarks; Public only.
[^nvidia-text-1]: [Nemotron 1B](nemotron-3-embed-1b-bf16.md), Benchmarks; vendor-reported.
[^nvidia-text-8]: [Nemotron 8B](nemotron-3-embed-8b-bf16.md), Benchmarks; vendor-reported.
[^llama]: [Llama Embed Nemotron](llama-embed-nemotron-8b.md), Benchmarks and Borda table.
[^kalm]: [KaLM 12B](kalm-embedding-gemma3-12b-2511.md), Benchmarks and limits.
[^granite-97]: [Granite 97M](granite-embedding-97m-multilingual-r2.md), Benchmarks.
[^granite-311]: [Granite 311M](granite-embedding-311m-multilingual-r2.md), Benchmarks and truncation discrepancy.
[^lfm]: [LFM ColBERT](lfm2-5-colbert-350m.md), Benchmarks and Model architecture.
[^lfm-dense]: [LFM dense](lfm2-5-embedding-350m.md), Benchmarks.
[^mlateon]: [mLateOn](mlateon.md), Benchmarks table.
[^deepx]: [DeepX](deepx-embedding-v1.md), Benchmarks and training metadata.
[^dek21]: [DEk21](dek21-hcmute-embedding.md), Benchmarks and word segmentation.
[^vietnamese]: [Vietnamese Embedding](vietnamese-embedding.md), Evaluation and split note.
[^jina-code-05]: [Jina Code 0.5B](jina-code-embeddings-0-5b.md), Benchmarks: no numerical results in supplied card.
[^jina-code-15]: [Jina Code 1.5B](jina-code-embeddings-1-5b.md), Benchmarks: no numerical results in supplied card.
[^context-preview]: [Perplexity context preview](pplx-embed-v2-context-9b-preview.md), Specification and Limits.
[^multimodal-comparison]: [Multimodal comparison](multimodal-embedding-model-comparison.md), architecture matrix, comparable-results table, multilingual filter and limits; all results provider-reported.
[^wemm]: [WeMM README](../raw/WeMM-Embedding/README.md), Evaluation → MMEB-v2, MMEB-v3 and Matryoshka; [WeMM concept](wemm-embedding.md) records the inspected figures.
[^ovis-vl-image]: [Ovis VL comparison figure](../raw/benchmark-figures-2026-11-02/ovis-vl.png), model columns and Overall rows; retrieved 2026-11-02. URL and SHA-256: [Ovis VL concept](ovis-vl-embedding-2b.md).
[^ovis-omni-image]: [Ovis Omni comparison figure](../raw/benchmark-figures-2026-11-02/ovis-omni.png), model columns, ALL and AUD rows; retrieved 2026-11-02. URL and SHA-256: [Ovis Omni concept](ovis-omni-embedding-3b.md).
[^geevec]: [GeeVec](geevec-embeddings-mm-1-0.md), Evaluation, 44 retrieval dataset table.
[^sentio]: [Sentio](sentio.md), Reported results and Limitations; snapshot 2026-10-16.
[^mmeb-snapshot]: [MMEB v3 snapshot](mmeb-v3-ranking-snapshot.md), Highest reported entries and Data-quality limits.
[^e5]: [e5-omni](e5-omni.md), Reported evaluation and image provenance.
[^jina-report]: [Jina Omni report](../raw/2605.08384_jina-embeddings-v5-omni/main.tex), `sections/experiments.tex` Table `omni-frontier`, benchmark definitions and per-modality subsets.
[^jina-figure]: [Jina model-card frontier](../raw/benchmark-figures-2026-11-02/jina-frontier.png), axes and legend; caption in [Jina Small card](../raw/jina-embeddings-v5-omni-small.md), benchmark section. Image URL and hash: [Jina Omni Small](jina-embeddings-v5-omni-small.md).
[^nemotron-visual]: [Nemotron 3.5 Embed](nemotron-3-5-embed-1b-bf16.md), Benchmarks and evaluated image resolution.
[^webai4]: [webAI 4B](webai-colvec1-1-4b.md), Benchmarks and token budget.
[^webai8]: [webAI 8B](webai-colvec1-1-8b.md), Benchmarks and token budget.
[^evie]: [EVIE](evie-preview-4-5b.md), Benchmarks and visual token budget.
[^pplx-late]: [pplx late 0.6B](pplx-embed-v2-late-0-6b.md), Reported results table and Limits; includes both sibling variants.
[^tomoro]: [Tomoro 8B](tomoro-colqwen3-embed-8b.md), Reported benchmarks, metric nDCG@5.
[^dna]: [DNA VL STEER](dna-vl-steer-2b.md), Reported results, training/calibration disclosure and Honest limitations.
[^community]: [Translation-memory community report](translation-memory-embedding-reranker-pairing-benchmark.md), Results all 15 languages and Protocol.
