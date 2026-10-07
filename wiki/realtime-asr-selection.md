---
type: Synthesis
title: Phân nhóm ASR/STT và shortlist realtime
description: Phân nhóm ASR/STT theo kiến trúc và streaming, đề xuất dải kích thước và shortlist realtime có điều kiện theo ngôn ngữ, phần cứng và chất lượng bằng chứng.
tags: [stt, asr, streaming, realtime, selection, vietnamese]
status: draft
created: 2026-10-06
generated: { by: llm-wiki-agent/1, at: 2026-10-07T03:56:09Z }
stale_after: 2027-10-06
sources:
  - id: vi-selection
    resource: vietnamese-realtime-asr-selection.md
    kind: synthesis
  - id: survey
    resource: asr-stt-model-survey.md
    kind: synthesis
  - id: nemotron
    resource: nemotron-3.5-asr-streaming-0.6b.md
    kind: synthesis
  - id: en
    resource: nemotron-speech-streaming-en-0.6b.md
    kind: synthesis
  - id: eou
    resource: parakeet-realtime-eou-120m-v1.md
    kind: synthesis
  - id: qwen
    resource: qwen3-asr-family.md
    kind: synthesis
  - id: voxtral
    resource: voxtral-mini-4b-realtime-2602.md
    kind: synthesis
  - id: infinite
    resource: audio8-asr-infinite.md
    kind: synthesis
  - id: r2t2
    resource: confucius4-r2t2.md
    kind: synthesis
  - id: vibe
    resource: vibevoice-asr-streaming-1.5b.md
    kind: synthesis
  - id: multi
    resource: multitalker-parakeet-streaming-0.6b-v1.md
    kind: synthesis
  - id: turbo
    resource: whisper-large-v3-turbo.md
    kind: synthesis
  - id: wlk
    resource: whisperlivekit.md
    kind: synthesis
  - id: vn
    resource: vietnamese-realtime-voice-agent-stack.md
    kind: synthesis
  - id: usable
    resource: community-usable-stt-voice-agents.md
    kind: synthesis
  - id: audio01
    resource: audio8-asr-0.1b.md
    kind: synthesis
  - id: phonon
    resource: phonon-2.md
    kind: synthesis
  - id: redux
    resource: parakeet-redux.md
    kind: synthesis
  - id: ultra
    resource: parakeet-ultra.md
    kind: synthesis
  - id: orukeet
    resource: orukeet.md
    kind: synthesis
  - id: granite
    resource: granite-speech-5.0-470m-turboctc.md
    kind: synthesis
  - id: indic
    resource: indic-conformer-600m-multilingual.md
    kind: synthesis
  - id: seamless
    resource: seamless-m4t-v2-large.md
    kind: synthesis
  - id: whistle
    resource: whistle.md
    kind: synthesis
  - id: moss-audio
    resource: moss-audio.md
    kind: synthesis
  - id: moss-diarize
    resource: moss-transcribe-diarize.md
    kind: synthesis
  - id: nemo-runtime
    resource: nemo-speech-cpp.md
    kind: synthesis
  - id: transcribe-runtime
    resource: transcribe-cpp.md
    kind: synthesis
  - id: apple-diarize
    resource: speaker-diarization-coreml.md
    kind: synthesis

---

Nên tổ chức ASR/STT theo hai trục: kiến trúc nhận dạng và cơ chế xuất transcript; size, ngôn ngữ, endpointing, speaker attribution, runtime và license là các bộ lọc riêng. Với voice agent, ưu tiên thử streaming 0.1–0.6B trước, nâng lên 1–2B khi chất lượng ngôn ngữ yêu cầu; model 4B streaming vẫn khả thi trên GPU phù hợp. Đây là **Synthesis** lựa chọn ứng viên, không phải cam kết realtime hay xếp hạng benchmark đã kiểm chứng.[^survey][^nemotron][^eou][^qwen][^voxtral]

## Nhóm và hướng phát triển

Bảng là cách tổ chức kiến thức đề xuất (**Synthesis**); các nhóm không loại trừ nhau, không phải roadmap chính thức của nhà phát triển.[^survey]

| Trục kiến trúc | Đại diện đã biên dịch | Hướng đánh giá/phát triển |
|---|---|---|
| Acoustic-first CTC / RNNT / TDT | Parakeet + Phonon/Redux/Ultra/Orukeet; Nemotron; EOU; Granite TurboCTC; IndicConformer | Cache-aware streaming khi checkpoint hỗ trợ; quantization/distillation, chunk/lookahead, endpointing |
| Encoder–decoder seq2seq | Whisper; Distil-Whisper; Canary-1b-v2; Cohere Transcribe | Giảm decoder, tối ưu runtime, buffered streaming và stable-prefix |
| Audio encoder + LLM decoder / speech-LLM | Qwen3-ASR; ARK; Fun-ASR; Canary-Qwen; GLM; Hojo; Higgs; Voxtral; Audio8; R2T2; MOSS-Audio | Đa ngôn ngữ, context/hotwords, causal audio, ổn định partial, bounded KV |
| ASR có speaker attribution | VibeVoice-ASR; MOSS; Multitalker Parakeet | Who/when/what, overlap, tích hợp hoặc ghép diarization |
| Massive multilingual / low-resource | Omnilingual ASR; SeamlessM4T v2 (translation + ASR) | Coverage theo từng ngôn ngữ và từng chiều tác vụ, adaptation và xử lý dài |

Các kiến trúc/đại diện dựa trên catalog; không suy ra RNNT nào cũng streaming hoặc CTC nào cũng offline.[^survey] VibeVoice tích hợp speaker-attributed transcription, còn Multitalker cần diarizer ngoài và một instance ASR cho mỗi speaker (**Reported**).[^vibe][^multi]

Theo cơ chế vận hành, dùng ba nhãn:
- **Native/stateful streaming:** Nemotron, Parakeet EOU, Voxtral Realtime, Audio8 Infinite; R2T2 nhấn mạnh committed append-only text.[^nemotron][^eou][^voxtral][^infinite][^r2t2]
- **Buffered/policy streaming:** Whisper qua WhisperLiveKit; Qwen cần phân biệt backend gốc với windowed recompute hoặc causal derivative của WLK. Streaming ở API không tự chứng minh compute bounded hoặc chữ không sửa.[^wlk][^qwen]
- **Offline/turn-final:** Parakeet TDT, ARK, Canary, Cohere và các recognizer offline trong catalog. Xử lý nhanh hơn realtime vẫn không chứng minh latency partial thấp.[^survey]

Đặt các nhãn này trong nội dung/tags để truy hồi; không cần di chuyển path concept chỉ để phân nhóm (**Synthesis**).

## Model mới: turn-final, edge hoặc tác vụ chuyên biệt

Các mục mới trong diff index không tự động trở thành native-streaming shortlist. Thuộc tính là **Reported** từ concept; vai trò đề xuất là **Synthesis**. Giữ chúng trong nhóm thử riêng thay vì xếp hạng chung với streaming ASR.

| Model / nhóm | Vai trò nên thử | Vì sao không nâng lên native-streaming A |
|---|---|---|
| [Phonon-2](phonon-2.md) | EN turn-final, 164 MB, ~2.1-bit encoder; MLX/CPU/CUDA | 5.21 WER và 174× M5 Air là accuracy/throughput tự báo cáo; không có streaming/partial-latency evidence[^phonon] |
| [Parakeet Redux](parakeet-redux.md) | 25 ngôn ngữ châu Âu, ternary 178 MB; Photon CPU/Apple | 113× trên 8 core x86 là throughput; VAD ≤30 s segmentation không chứng minh committed partial; noise WER 9.04 vs teacher 6.72[^redux] |
| [Parakeet Ultra](parakeet-ultra.md) | GPU turn-final, 0.6B full precision; cùng 25 ngôn ngữ | English 5.80 và FLEURS avg 9.55 theo protocol riêng; B200 128-request throughput không phải single-stream latency[^ultra] |
| [Orukeet](orukeet.md) | 627M, 25 ngôn ngữ; ONNX/GGUF/Core ML preview | Offline; không phải EOU live-typing. FLEURS pooled 9.85 không chung phép gộp với Moondream; test-other được dùng cho adaptation và checkpoint selection; CC-BY-SA weights[^orukeet] |
| [Granite TurboCTC](granite-speech-5.0-470m-turboctc.md) | EN offline 470M, greedy CTC; Transformers/MLX/transcribe.cpp | Edge/low-latency positioning không chứng minh stateful streaming; benchmark chỉ ở ảnh, chưa có số WER/latency[^granite] |
| [IndicConformer](indic-conformer-600m-multilingual.md) | 600M, 22 Indic, CTC/RNNT, MIT | RNNT head không đủ để suy ra streaming; card thiếu chunk protocol và numeric benchmark[^indic] |
| [Whistle](whistle.md) | 16.9 MB blob CPU, 7 ngôn ngữ châu Âu; timestamps/hotwords | Params không được nêu; ≤30 s mỗi pass, benchmark image-only; không suy ra latency từ 80 ms embedding-frame rate[^whistle] |
| [MOSS-Transcribe-Diarize](moss-transcribe-diarize.md) | 0.9B, offline who/when/what đến 90 phút; 50+ ngôn ngữ, có vi trong challenge list | Không có streaming chunk protocol; CER/cpCER không phải DER/latency. Dùng làm meeting/turn-final candidate, không realtime vi baseline[^moss-diarize] |
| [MOSS-Audio](moss-audio.md) | ~4.6B/~8.6B tổng, timestamp ASR + audio QA | Không có streaming/VRAM/latency evidence; full language list unstated; CER/AAS khác Open ASR WER[^moss-audio] |
| [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) | 2.3B, translation + ASR, có Vietnamese speech/text hai chiều | Không có streaming hoặc numeric benchmark trong card; CC-BY-NC; không đồng nhất với một Seamless streaming checkpoint khác[^seamless] |

Không model nào trong nhóm Parakeet derivative nêu trên mở rộng sang tiếng Việt: Phonon-2 chỉ EN, Redux/Ultra/Orukeet giữ 25 ngôn ngữ châu Âu (**Reported**).[^phonon][^redux][^ultra][^orukeet]

## Size cho realtime

Dải dưới là **Synthesis / heuristic để thử nghiệm**, không phải giới hạn vật lý hay benchmark.[^survey][^eou][^nemotron][^qwen][^voxtral]

| Mục tiêu | Dải thử đầu tiên | Ràng buộc |
|---|---|---|
| CPU / edge | 120M native-streaming hoặc 0.47–0.6B với runtime/quantization phù hợp; blob cực nhỏ là trục riêng | EOU là ứng viên streaming; Granite/Parakeet derivatives là turn-final. Không suy ra parameters từ MB; chưa benchmark CPU mục tiêu |
| GPU dùng chung với LLM/TTS | 0.1–0.6B; khoảng 0.8B cho Whisper Turbo | Đo contention và bộ nhớ cả pipeline |
| GPU ASR riêng, cần ngôn ngữ/chất lượng tốt hơn | 0.6–1.7B | Nâng size chỉ khi giảm lỗi đủ để bù latency/cost |
| GPU riêng cho streaming LLM-ASR | Khoảng 4B | Voxtral card yêu cầu GPU ≥16 GB BF16; không áp dụng con số này cho mọi model |
| 7B+ | Chỉ thử khi có nhu cầu đặc thù | Không mặc định cho agent ít latency; cũng không kết luận bất khả thi |

Ước lượng trọng số thuần: params × bytes/param. 0.6B BF16 ≈1.2 GB; 1.7B ≈3.4 GB; 4B ≈8 GB, đơn vị thập phân. Đây là phép tính **Synthesis**, không phải VRAM triển khai: còn encoder chưa tính nếu size chỉ là decoder, KV/encoder cache, workspace, allocator, runtime và số phiên. Quantization không đảm bảo tốc độ tăng.

Các card mới cho thấy **Reported** 0.6B có thể đóng gói thành 164 MB (Phonon) hoặc 178 MB (Redux), còn Whistle chỉ nêu 16.9 MB mà không nêu parameter count. Vì vậy không loại model CPU chỉ theo size tên và không lấy download size làm peak RAM (**Synthesis**).[^phonon][^redux][^whistle]

Ví dụ size tên dễ gây hiểu nhầm: Audio8-ASR-0.1B là ~0.104B LM nhưng ~0.324B toàn bộ; Audio8 Infinite có decoder Qwen2.5-3B cộng audio tower và 8.17 GB BF16 weights (**Reported**).[^audio01][^infinite]

## Shortlist triển khai thử

Thông số dưới là **Reported** trong concept, chưa tái lập; mức ưu tiên là **Synthesis**.

| Ưu tiên / điều kiện | Model | Size | Streaming / latency được báo cáo | Bộ lọc |
|---|---|---|---|---|
| A — tiếng Việt / đa ngôn ngữ | Nemotron 3.5 ASR Streaming | 0.6B | Chunk 80–1120 ms; thử 160–320 ms trước | vi-VN transcription-ready; cần đo accuracy ở chunk đã chọn[^nemotron] |
| A — chỉ tiếng Anh | Nemotron Speech Streaming EN | 0.6B | Cache-aware, 80–1120 ms | Bản EN được khuyến nghị cho EN-only[^en][^nemotron] |
| A — EN nhẹ + endpointing | Parakeet Realtime EOU | 120M | ASR 80–160 ms; inline EOU | Không PnC; EOU P50 160 ms đo trên TTS tổng hợp; license NVIDIA[^eou] |
| B — tiếng Việt / nhiều ngôn ngữ | Qwen3-ASR | 0.6B → 1.7B | Unified streaming; backend gốc vLLM | Không có batch/timestamps ở streaming gốc; không ép 160 ms rồi suy ra chất lượng offline[^qwen][^r2t2] |
| B — caption stable zh/en | Confucius4-R2T2 | ~1.7B base | Append-only; chunk 80 ms–2 s; latency 200–600 ms | Benchmark tự báo cáo, hardware không rõ; review license weights; chưa có evidence vi cụ thể[^r2t2] |
| B — 13 ngôn ngữ, GPU riêng | Voxtral Mini 4B Realtime | ~4B class | Delay 80–2400 ms; default đề xuất 480 ms | GPU ≥16 GB BF16; 13-code list không có vi[^voxtral] |
| B — zh/en liên tục | Audio8 ASR Infinite | 3B decoder + tower | Clock 80/120/160 ms; delay 240–560 ms; rolling KV | Preview; semantic-perception roadmap chưa hoàn tất; 24/7 chưa được wiki kiểm chứng[^infinite] |
| C — họp, speaker attribution | VibeVoice-ASR-Streaming | 1.5B trước 7B | Streaming có hotwords và speaker attribution | 10 ngôn ngữ không có vi; thiếu numeric latency/WER trong card[^vibe][^survey] |
| C — overlap tiếng Anh | Multitalker Parakeet | 0.6B mỗi instance speaker | Benchmarks tại 1.12 s | Cần streaming diarizer, tài nguyên/latency không chỉ là ASR 0.6B[^multi] |
| C — turn-final / buffered fallback | Whisper large-v3-turbo | 809M | Faster-Whisper; WLK SimulStreaming/LocalAgreement | Không native streaming; hỗ trợ vi theo Vietnamese stack draft, cần VAD và lọc hallucination[^turbo][^wlk][^vn] |

Không đưa ARK, Hojo, Higgs, GLM, Cohere, Canary-Qwen, Voxtral 3B/24B vào shortlist native-streaming đầu tiên vì catalog chưa cung cấp cơ chế realtime tương ứng; không có nghĩa chúng không thể xử lý turn-final nhanh.[^survey] Fun-ASR có tuyên bố realtime nhưng chưa đủ bằng chứng latency/partial cho ưu tiên A. Audio8 0.1B không phải Audio8 Infinite, là short-form offline và CC-BY-NC-4.0; không chọn mặc định cho sản phẩm thương mại.[^survey][^audio01]

## Runtime và diarization: bộ lọc riêng

Đây là **Reported** khả năng runtime, không phải bằng chứng mọi checkpoint có cùng streaming semantics; lựa chọn thử là **Synthesis**.

| Path | Khi nên thử | Giới hạn cần giữ |
|---|---|---|
| [NeMo-Speech.cpp](nemo-speech-cpp.md) | Native C++ ggml cho Nemotron EN/3.5; live mic, realtime WebSocket, HTTP subsets và C SDK | Nemotron EN Q8_0 với input chunk 160 ms: compute/chunk 2.3 ms RTX 4090, 27 ms CPU (không nêu CPU/thread). Không phải endpoint→final, không phải benchmark 3.5/vi; `BENCHMARK.md` chưa có[^nemo-runtime] |
| [transcribe.cpp](transcribe-cpp.md) | Multi-vendor GGUF STT, Metal/Vulkan/CUDA/ROCm/CPU; 4 language bindings | Support tables có 20 STT families, header ghi 16; native Nemotron/Voxtral paths được nêu, Qwen family không có streaming capability token trong bảng. Không chuyển nhãn streaming cấp family Parakeet sang mọi variant; numerical/WER verification là source claim chưa tái lập[^transcribe-runtime] |
| [Speaker Diarization Core ML](speaker-diarization-coreml.md) | Apple on-device speaker segments qua FluidAudio, iOS 17/macOS 14+ | Diarization-only, không xuất transcript; thiếu DER/latency. Community-1 scope không bao gồm legacy online artifacts; không mặc định hợp với Multitalker speaker-kernel interface[^apple-diarize] |

**Synthesis:** chọn artifact theo runtime, không chỉ phần mở rộng GGUF. Orukeet ghi rõ native NeMo-Speech.cpp GGUF và Handy/transcribe.cpp export có tensor layout khác nhau. MIT/Apache của runtime không thay license model weights.[^orukeet][^nemo-runtime][^transcribe-runtime]

## Quyết định cho tiếng Việt

**Synthesis:** benchmark Nemotron 3.5 0.6B và Qwen3-ASR 0.6B trước; nâng Qwen lên 1.7B nếu giảm lỗi tên riêng, số, phủ định và code-switch đủ đáng kể. Whisper Turbo là baseline/fallback nếu chấp nhận buffered hoặc end-of-turn.[^nemotron][^qwen][^vn]

Nemotron có FLEURS-vi WER 13.41 tại 80 ms và 11.18 tại 1.12 s (**Reported**). Không đối chiếu trực tiếp với Qwen offline/AI-report để kết luận model nào tốt nhất realtime.[^nemotron][^qwen] Primary follow-up tại [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) bổ sung [PhoWhisper](phowhisper.md), [ChunkFormer Vietnamese](chunkformer-vietnamese.md) và [ZipFormer30M](zipformer-30m-vietnamese.md). Qwen paper streaming dùng2s chunks/5-token fallback/bốn unfixed chunks, không vi streaming benchmark;92ms TTFT không phải mic latency. ChunkFormer large RNNT113M có CC-BY-4.0 nhưng streaming-trained small checkpoint còn unavailable; CTC110M có NC. ZipFormer30M upstream NC-ND, chưa có native streaming protocol. Không dùng dải size120M/0.6B generic để mặc định mọi checkpoint có vi (**Reported/Synthesis**).[^vi-selection]

## Gate benchmark

**Synthesis:** chọn bằng ngôn ngữ → native/buffered phù hợp → license → runtime/phần cứng → đo thực tế, không bằng size hoặc WER leaderboard riêng.[^survey][^usable]

Đo RTF = thời gian compute / thời lượng audio; RTF <1 là điều kiện theo kịp luồng, chưa đủ cho trải nghiệm realtime. Đo thêm first stable text, tỷ lệ sửa partial, endpoint→final P50/P95, WER/CER và entity/negation errors, memory/session, queue delay và latency khi đồng thời LLM/TTS chạy. Các metric usable-text lấy cảm hứng từ checklist cộng đồng **Reported/Unverified**, không phải tiêu chuẩn đã tái lập.[^usable] Thử chunk/latency chính xác của production với noise, giọng vùng miền và số phiên mục tiêu.

## Relationships

- Uses [ASR/STT Model Survey](asr-stt-model-survey.md) làm catalog đầu vào; trang này bổ sung bộ lọc realtime thay vì bảng ranking offline.[^survey]
- Uses [Vietnamese Realtime Voice Agent Stack](vietnamese-realtime-voice-agent-stack.md) làm bối cảnh pipeline tiếng Việt; giữ nguyên giới hạn báo cáo AI/draft.[^vn]
- Depends on [Usable STT for Voice Agents](community-usable-stt-voice-agents.md) cho ý tưởng đánh giá stable-text và action-bearing spans; bằng chứng vẫn là cộng đồng, chưa đo.[^usable]

## Coverage và giới hạn

- Index-diff reconciliation: inspected các concept mới được thêm vào bảng model/runtime ở trên, catalog, index và log. Các mục đã được survey bao phủ không ingest lại; TTS-only concepts thuộc [TTS Model Survey](tts-model-survey.md), không thêm vào ASR shortlist (**Observed** inspection scope).
- Footnote trỏ section của compiled concept và giữ provenance chain về raw; phần shortlist mới dùng compiled concepts, không nghiên cứu web hoặc benchmark. Trong operation này raw NeMo-Speech.cpp, IndexTTS-2.5 và Speaker Diarization Core ML được đọc để cập nhật survey song song; không cài/chạy model.
- Các concept giữ ledger cho ảnh, checkpoints, conversion/docs và benchmark assets chưa được inspect; update này không lấp các khoảng trống ấy. Không dùng throughput offline hoặc VAD segmentation làm bằng chứng stable partial.
- Runtime/backends có thể khác semantics; WLK có Qwen HF adapter, không phủ nhận giới hạn vLLM-only của toolkit gốc. Không chuyển các tuyên bố production/validated của source thành xác minh của wiki.[^qwen][^wlk]
- Không có target CPU/GPU, ngôn ngữ ưu tiên rõ ràng, số phiên hay latency SLA. Vì vậy status draft: shortlist chưa được validate trên máy đích; không có verified metadata.
- Benchmark vendor không chung protocol; coverage/language/latency của VibeVoice còn thiếu; Confucius thiếu hardware/protocol, Audio8 còn preview; các nguồn này không chứng minh năng lực production.[^survey][^vibe][^r2t2][^infinite]

[^vi-selection]: [Vietnamese Realtime ASR Selection](vietnamese-realtime-asr-selection.md) — Shortlist; Qwen streaming/efficiency; Chọn runtime; Coverage; primary-source chain2026-10-07, no execution.

[^survey]: [asr-stt-model-survey ](asr-stt-model-survey.md) — sections: Master catalog; Streaming and latency; Selection guide; Coverage and limits.
[^nemotron]: [nemotron-3.5-asr-streaming-0.6b ](nemotron-3.5-asr-streaming-0.6b.md) — sections: Supported languages and language detection; Streaming operating points; Benchmarks (FLEURS); Coverage and limits.
[^en]: [nemotron-speech-streaming-en-0.6b ](nemotron-speech-streaming-en-0.6b.md) — sections: Architecture and streaming mechanism; Streaming operating points; Benchmarks (Open ASR Leaderboard, WER without PnC); Coverage and limits.
[^eou]: [parakeet-realtime-eou-120m-v1 ](parakeet-realtime-eou-120m-v1.md) — sections: Architecture and streaming; End-of-utterance detection; Benchmarks; Deployment requirements.
[^qwen]: [qwen3-asr-family ](qwen3-asr-family.md) — sections: Language and audio coverage; Inference and serving; Benchmark highlights; Relationships; Coverage and limits.
[^voxtral]: [voxtral-mini-4b-realtime-2602 ](voxtral-mini-4b-realtime-2602.md) — sections: Key features; Recommended settings; vLLM serving (recommended); Coverage and limits.
[^infinite]: [audio8-asr-infinite ](audio8-asr-infinite.md) — sections: Streaming operation points; Architecture and checkpoint; Roadmap and limitations; Coverage and limits.
[^r2t2]: [confucius4-r2t2 ](confucius4-r2t2.md) — sections: Streaming design; Streaming latency evidence; Language coverage; Model identity and lineage; Coverage and limits.
[^vibe]: [vibevoice-asr-streaming-1.5b ](vibevoice-asr-streaming-1.5b.md) — sections: Capabilities; Evaluation; Coverage and limits.
[^multi]: [multitalker-parakeet-streaming-0.6b-v1 ](multitalker-parakeet-streaming-0.6b-v1.md) — sections: Architecture; Streaming configuration; Benchmarks; Coverage and limits.
[^turbo]: [whisper-large-v3-turbo ](whisper-large-v3-turbo.md) — sections: Architecture and model family; Long-form transcription; Performance, limitations, and implications.
[^wlk]: [whisperlivekit ](whisperlivekit.md) — sections: Streaming policies and backend selector; Backend notes: Voxtral, FunASR, Qwen3, Canary; Coverage and limits.
[^vn]: [vietnamese-realtime-voice-agent-stack ](vietnamese-realtime-voice-agent-stack.md) — sections: Source and trust; Vietnamese coverage by component; Deployment tiers; Coverage and limits.
[^usable]: [community-usable-stt-voice-agents ](community-usable-stt-voice-agents.md) — sections: Usable-text evaluation checklist; Logging and diagnosis practice; Coverage and limits.
[^audio01]: [audio8-asr-0.1b ](audio8-asr-0.1b.md) — sections: Model identity and architecture; Files and related releases; Limitations.
[^phonon]: [Phonon-2](phonon-2.md) — sections: Quantization and size; Benchmarks (vendor-run Open ASR table); Speed (vendor-reported throughput); Coverage and limits.
[^redux]: [Parakeet Redux](parakeet-redux.md) — sections: Identity and lineage; Quantization and size; Benchmarks; Performance; Inference and usage; Coverage and limits.
[^ultra]: [Parakeet Ultra](parakeet-ultra.md) — sections: Identity and lineage; Benchmarks; Performance; Inference and usage; Coverage and limits.
[^orukeet]: [Orukeet](orukeet.md) — sections: Identity and lineage; Construction; Benchmarks; Inference and runtimes (tensor-layout warning and Core ML preview); Coverage and limits.
[^granite]: [Granite Speech 5.0 470M TurboCTC](granite-speech-5.0-470m-turboctc.md) — sections: Architecture; Benchmarks; Inference and usage; Coverage and limits.
[^indic]: [IndicConformer-600M-Multilingual](indic-conformer-600m-multilingual.md) — sections: Identity and release; Architecture and decoding; Supported languages; Inference and usage.
[^seamless]: [SeamlessM4T v2 Large](seamless-m4t-v2-large.md) — sections: Tasks and language coverage; Architecture; Trust, license, and limits; Contradictions; Coverage and limits.
[^whistle]: [Whistle](whistle.md) — sections: Capabilities; Architecture and Needle engine; Benchmark protocol and limits; Coverage and limits.
[^moss-audio]: [MOSS-Audio family](moss-audio.md) — sections: Model identity and lineage; Architecture; Benchmark highlights; Coverage and limits.
[^moss-diarize]: [MOSS-Transcribe-Diarize 0.9B](moss-transcribe-diarize.md) — sections: Capabilities; Model identity and release; Evaluation; Serving; Coverage and limits.
[^nemo-runtime]: [NeMo-Speech.cpp](nemo-speech-cpp.md) — sections: Supported applications and models; Performance; Server, SDK, and source build; Runtime identity and scope; Coverage and limits.
[^transcribe-runtime]: [transcribe.cpp](transcribe-cpp.md) — sections: Supported models; Build, backends, and dependencies; Bindings, tests, and project layout; Sponsors and license; Contradictions; Coverage and limits.
[^apple-diarize]: [Speaker Diarization Core ML](speaker-diarization-coreml.md) — sections: Supported Community-1 artifacts; Provenance status; Legacy compatibility artifacts; Technical specifications; Coverage and limits.
