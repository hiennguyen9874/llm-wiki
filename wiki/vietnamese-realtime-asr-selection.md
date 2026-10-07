---
type: Synthesis
title: Vietnamese Realtime ASR Selection
description: Lựa chọn ASR realtime tiếng Việt theo chất lượng, native streaming, CPU/GPU và license, với đối chiếu primary sources của Qwen, Nemotron, ChunkFormer, PhoWhisper và ZipFormer.
tags: [stt, asr, vietnamese, streaming, selection, comparison]
status: draft
created: 2026-10-07
generated: { by: llm-wiki-agent/1, at: 2026-10-07T03:56:09Z }
stale_after: 2027-10-07
sources:
  - id: primary
    resource: ../raw/vietnamese-asr-research-2026-10-07/README.md
    scope: ../raw/vietnamese-asr-research-2026-10-07/
    kind: documentation
  - id: qwen
    resource: qwen3-asr-family.md
    kind: synthesis
  - id: nemotron
    resource: nemotron-3.5-asr-streaming-0.6b.md
    kind: synthesis
  - id: survey
    resource: asr-stt-model-survey.md
    kind: synthesis
  - id: wlk
    resource: whisperlivekit.md
    kind: synthesis
  - id: runtime
    resource: nemo-speech-cpp.md
    kind: synthesis
  - id: whisper
    resource: whisper-large-v3-turbo.md
    kind: synthesis
  - id: cohere
    resource: cohere-transcribe-03-2026.md
    kind: synthesis
  - id: usable
    resource: community-usable-stt-voice-agents.md
    kind: synthesis
  - id: noise
    resource: speech-enhancement-before-asr.md
    kind: synthesis
  - id: turn
    resource: turn-detection-models.md
    kind: synthesis
---

**Synthesis, chưa benchmark deployment:** shortlist tiếng Việt nên bắt đầu bằng Nemotron 3.5 0.6B nếu cần partial độ trễ thấp, Qwen3-ASR 1.7B nếu ưu tiên chất lượng với buffering lớn hơn, Qwen3-ASR 0.6B nếu tiết kiệm tài nguyên, và Whisper large-v3-turbo làm baseline turn-final. ChunkFormer RNNT large 113M là đối thủ chuyên Việt đáng thử cho final-pass; ONNX streaming riêng của family cần gate checkpoint/availability/license. Không có một benchmark cùng audio, normalizer, chunk và hardware để tuyên bố model nào tốt nhất realtime tiếng Việt.[^primary][^qwen][^nemotron][^whisper]

## Định nghĩa realtime

Ba lớp không đồng nhất (**Synthesis**):[^primary][^wlk][^nemotron]

1. **Native/stateful streaming:** audio đến liên tục, giữ encoder/decoder cache; Nemotron là ứng viên có evidence rõ cho vi.
2. **Buffered/policy streaming:** nhận audio liên tục nhưng chờ context và stable-prefix trước commit; Qwen benchmark dùng chunk 2s và rollback, Whisper cần WLK policies. WebSocket/SSE không biến checkpoint thành causal encoder.
3. **Turn-final:** nhận nguyên câu sau endpoint và decode nhanh; Whisper, PhoWhisper, ChunkFormer large và Cohere có thể thử trong mô hình này, không phải cam kết sub-200ms partial.

RTF <1 là điều kiện theo kịp audio, không đủ cho latency usable text. Chunk accumulation, lookahead, compute, scheduling, transport và commit policy đều đóng góp; endpoint→final khác first stable text (**Synthesis**).[^usable][^nemotron][^primary]

## Shortlist và bằng chứng tiếng Việt

| Model | Hỗ trợ vi | Evidence có thể dùng | Vai trò đề xuất / giới hạn |
|---|---|---|---|
| [Nemotron 3.5 ASR](nemotron-3.5-asr-streaming-0.6b.md), 600M | `vi-VN`, transcription-ready | FLEURS WER LangID 13.41/12.87/12.29/11.78/11.18 tại 80/160/320/560/1120ms | Native streaming đầu tiên; thử 160–320ms, tăng 560ms nếu lỗi cao; OpenMDW-1.1[^nemotron][^primary] |
| [Qwen3-ASR](qwen3-asr-family.md), 1.7B | Có | Appendix A.2 FLEURS-vi 5.55; MLC-SLM-vi 14.92 | Quality-oriented candidate; hai số này offline, không vi streaming WER; Apache-2.0[^primary][^qwen] |
| Qwen3-ASR 0.6B | Có | FLEURS-vi 8.52; MLC-SLM-vi 17.67 | Tradeoff tài nguyên; không gán TTFT 92ms thành mic latency[^primary][^qwen] |
| [Whisper Turbo](whisper-large-v3-turbo.md), 809M | Có trong multilingual scope | Không có matched vi streaming benchmark đã inspect | Baseline runtime CT2/WLK; VAD, hallucination controls và stable-prefix policy; MIT card[^survey][^whisper] |
| [ChunkFormer RNNT large](chunkformer-vietnamese.md), 113M | Chuyên vi | VIVOS 2.49, CMV 5.18, VLSP2020 T1/T2 12.75/20.47 | Final-pass chuyên Việt; CC-BY-4.0; không gán scores này cho small streaming[^primary] |
| ChunkFormer small streaming DCT | Guide nói vi streaming | Stateful ONNX graph/session, nhưng card HTTP401 | Chỉ research tier: chưa xác định size/license/availability/WER/latency[^primary] |
| [PhoWhisper](phowhisper.md), medium/large | Chuyên vi | medium VIVOS 4.97, CMV 8.27; large 4.67/8.14 | Turn-final/specialized baseline; BSD-3; conversion runtime cần thử[^primary] |
| [Fun-ASR-MLT-Nano](fun-asr-mlt-nano-2512.md), 800M | Có | Language list + hotwords/ITN, không vi-specific score | Challenger turn-final; không nhầm với Nano zh/en/ja hay WLK SenseVoice; Apache-2.0[^survey] |
| [Cohere Transcribe](cohere-transcribe-03-2026.md), 2B | Có | Language list; vi plot chưa inspect | Challenger final-pass; no timestamps/diarization, code-switch inconsistent, VAD cần thiết; Apache-2.0[^cohere] |
| [ZipFormer 30M](zipformer-30m-vietnamese.md) | Chuyên vi | 12s/0.3s CPU claimed; VLSP2020 T1 12.29 | CPU research only; CC-BY-NC-ND, no established native streaming[^primary] |

Mọi số trên là **Reported** của nguồn, chưa tái lập. Các vai trò là **Synthesis**. FLEURS vs VIVOS/CMV/VLSP/MLC-SLM không chung tập; WER khác tokenizer/normalization cũng không thể xếp hạng trực tiếp. Qwen và Nemotron FLEURS cũng khác protocol offline/streaming và LangID, nên 5.55 vs 12.29 không chứng minh Qwen thắng khi cùng latency.[^primary][^nemotron]

## Qwen: streaming và efficiency thực sự được đo gì?

Paper §4.5/Table8 dùng **2-second chunks, 5-token fallback, giữ bốn chunk cuối unfixed**. Avg WER 1.7B 2.69→3.33 và 0.6B 3.48→4.40 chỉ trên LibriSpeech/FLEURS-en/zh, không Vietnamese. Vì vậy không có căn cứ coi Qwen base là append-only sub-200ms Vietnamese recognizer (**Reported**, suy luận **Synthesis**).[^primary]

Paper §2.4/Table2: vLLM0.14, CUDA Graph/BF16, input ASR ~2 phút. 0.6B concurrency1 TTFT avg/P95=92/105ms; concurrency128=3210/6195ms và throughput2000 audio-seconds/second. Đây là request/decode efficiency với input có sẵn, không latency nhận audio live; hardware chỉ ghi “single typical computing resource”. Không ghép 92ms với concurrency128 như cùng operating point (**Reported**; interpretation **Synthesis**).[^primary]

Paper §2.1: AuT encoder 8x downsampling 128-dim Fbank→12.5Hz, dynamic attention window1–8s; model1.7B có Qwen3-1.7B + projector + encoder300M, model0.6B có decoder0.6B + encoder180M. Size tên không phải tổng params/peak VRAM (**Reported**; implication **Synthesis**).[^primary]

Toolkit gốc streaming vLLM-only, không batch/timestamps; `-hf` inference và WLK adapters là đường khác. Qwen ForcedAligner 11 languages không có vi. WLK windowed Qwen recompute default12s, causal derivative English-only: không chọn causal đó cho production vi từ coverage base (**Reported**).[^qwen][^wlk]

## Kiến trúc và hướng triển khai

| Hướng | Điểm mạnh để thử | Chi phí/rủi ro cần đo |
|---|---|---|
| Cache-aware acoustic RNNT (Nemotron; streaming-trained ChunkFormer) | Reuse cache, latency/config rõ; phù hợp nhiều phiên | Language/domain errors, streaming checkpoint license; RNNT head không đảm bảo encoder causal |
| Audio encoder + LLM decoder (Qwen) | Multilingual/context biasing, ứng viên quality | Decoder/encoder resources, rollback/commit lag, instruction hallucination/faithfulness; không mọi LLM-ASR đều streaming |
| Encoder-decoder seq2seq + policy (Whisper/PhoWhisper) | Runtime và baseline dễ đối chiếu | Recompute/context window, partial sửa, silence hallucination, end-of-turn |
| Specialized compact acoustic model (ChunkFormer/ZipFormer) | Ít params, tiềm năng CPU/domain fine-tuning | Size không bảo đảm streaming; model licenses khác runtime; chưa measured vi partial latency |

Bảng là **Synthesis** từ kiến trúc/tài liệu, không khẳng định một kiến trúc luôn chính xác hơn kiến trúc khác.[^primary][^nemotron][^whisper][^wlk]

**Khuyến nghị single-pass:** chọn Nemotron nếu ưu tiên stable-text sớm; chọn Qwen nếu có thể chờ context và benchmark vi xác nhận accuracy. **Khuyến nghị two-pass:** native streaming Nemotron cho partial; cuối lượt Qwen1.7B hoặc ChunkFormer RNNT large cho final/critical spans. Đây là thiết kế đề xuất chưa đo; tăng compute, phải reconcile transcript/version, tránh duplicate tokens và side effects từ partial. Không tự cho model final là ground truth; critical số/tên/phủ định cần confidence/clarification (**Synthesis**).[^primary][^nemotron][^usable]

## Chọn runtime và môi trường

- Nemotron: NeMo reference cache-aware path; [NeMo-Speech.cpp](nemo-speech-cpp.md) C++/GGUF/WebSocket để thử CPU hoặc GPU. Benchmark27ms CPU/160ms chunk thuộc model EN, không benchmark3.5 Vietnamese; phải đo lại. Runtime Apache không thay OpenMDW weights (**Reported/Synthesis**).[^nemotron][^runtime]
- Qwen: thử toolkit vLLM gốc hoặc WLK windowed với explicit Vietnamese; pin version/environment, đo cache và concurrency thực tế. Không dùng số online async Table2 làm committed streaming capacity (**Synthesis**).[^qwen][^wlk][^primary]
- Whisper: CT2/Faster-Whisper cho final-pass; WLK SimulStreaming/LocalAgreement khi cần live text. Không cắt audio mỗi200ms độc lập rồi coi là stable transcript (**Synthesis**).[^wlk][^whisper]
- ChunkFormer: ONNX CPU/GPU cho neural graphs, session state riêng; lấy checkpoint streaming-trained + trained chunk configuration. Large models được guide export non-streaming; không có bằng chứng large scores giữ nguyên ở tiny chunks (**Reported/Synthesis**).[^primary]
- Chưa có GPU/CPU, số phiên hay SLA đích; không ghi peak VRAM, P95 hoặc số stream như cam kết. Thử 0.6B trước nếu GPU chung LLM/TTS; quality trial1.7B cần room cho encoder/cache/workspace và contention (**Synthesis**).[^qwen][^nemotron][^primary]

## Loại khỏi shortlist vi / bằng chứng chưa đủ

Language lists trong survey không có vi cho Parakeet25-European/derivatives, Canary compiled cards, Voxtral13, Audio8Infinite zh/en, Audio8 0.1B, SenseVoiceSmall, GLM-ASR, Hojo, ARK, VibeVoice Streaming10, GraniteTurboCTC và Distil-Large-v3.5 English. Không suy ra support từ parent encoder hay chữ multilingual. Confucius4-R2T2 chưa công bố explicit vi evidence; không kết luận vi unsupported, chỉ không đủ để recommend.[^survey]

MOSS-Transcribe-Diarize có vi trong challenge list nhưng offline long-form, phù hợp meeting review thay vì agent partial; SeamlessM4Tv2 có vi speech/text nhưng noncommercial và không streaming evidence ở compiled card; Omnilingual per-language list/result chưa inspect nên không xác nhận vi từ headline1600+. Proprietary/cloud API hiện tại chưa nghiên cứu vendor language/region/streaming/pricing, không xếp hạng.[^survey]

## Gate đánh giá đề xuất

**Synthesis**, không SLA hay benchmark đã đo:[^usable][^primary][^turn][^noise]

1. Corpus holdout tiếng Việt tự nhiên: Bắc/Trung/Nam, tên riêng/domain, địa chỉ/số tiền/số điện thoại/ngày, phủ định, code-switch, mic vs8k telephony, tiếng ồn và silence.
2. Cùng ground truth/normalizer Unicode, dấu, số, punctuation và cùng policy/chunk. Báo WER/CER cùng exact accuracy của số/tên/phủ định; tránh normalizer che mất critical errors.
3. Đo first partial và first stable text riêng, tỷ lệ sửa partial, word lag, endpoint→final P50/P95, RTF, peak memory/session, concurrency, queue delay và contention LLM/TTS.
4. VAD/AEC/endpointing tách khỏi ASR; detector Smart Turn Vietnamese và denoise guidance hiện chỉ secondhand AI-report/draft. Denoise A/B thay vì mặc định luôn giúp ASR; không dùng EOU English để tuyên bố endpoint tiếng Việt.
5. Chỉ quyết định production sau gate availability, license, target-hardware performance và no-action-on-unstable-text.

## Relationships và coverage

- Uses [ASR/STT Model Survey](asr-stt-model-survey.md) và [Realtime shortlist](realtime-asr-selection.md); bổ sung tiếng Việt, primary-paper protocol và license correction.[^survey][^primary]
- Uses [PhoWhisper](phowhisper.md), [ChunkFormer Vietnamese](chunkformer-vietnamese.md) và [ZipFormer30M](zipformer-30m-vietnamese.md) làm các specialized alternatives newly captured.[^primary]
- Primary research ran2026-10-07; no model execution. Captured package README lưu inspected/pending/excluded assets, unavailable HTTP401/404 và hashes. Paper inspection là targeted, không full paper ingestion. Existing wiki snapshots không được refresh toàn bộ; không claim exhaustive latest global releases.
- Status draft vì thiếu matched Vietnamese streaming WER, target hardware/SLA và small streaming checkpoint evidence; không có verified metadata. Claim của vendor/author vẫn Reported, HTTP/check/file inspection không verify capability.

[^primary]: [Primary research package](../raw/vietnamese-asr-research-2026-10-07/README.md) — `qwen-report.html` §§2.1–2.4, Table2, §4.5/Table8, AppendixTableA.2(a/b) vi; `nemotron-card.md` Performance vi-VN row; PhoWhisper/ChunkFormer/ZipFormer files and locators in ledger.
[^qwen]: [Qwen family](qwen3-asr-family.md) — Inference and serving; Language and audio coverage; Primary-paper clarification.
[^nemotron]: [Nemotron3.5](nemotron-3.5-asr-streaming-0.6b.md) — Architecture and I/O; Supported languages; Streaming operating points; Benchmarks; Inference.
[^survey]: [Survey](asr-stt-model-survey.md) — Master catalog; Multilingual coverage; Coverage and limits; Vietnamese primary-source follow-up.
[^wlk]: [WLK](whisperlivekit.md) — Streaming policies; Backend notes Qwen/FunASR; Coverage.
[^runtime]: [NeMo-Speech.cpp](nemo-speech-cpp.md) — Performance; Server, SDK, and source build.
[^whisper]: [Whisper Turbo](whisper-large-v3-turbo.md) — Architecture; Performance, limitations, and implications; Relationships.
[^cohere]: [Cohere](cohere-transcribe-03-2026.md) — Model identity; Strengths and limitations; Benchmarks.
[^usable]: [Usable STT](community-usable-stt-voice-agents.md) — Usable-text evaluation checklist; Logging and diagnosis practice. Community evidence unverified.
[^noise]: [Enhancement](speech-enhancement-before-asr.md) — Practice; Contradictions; Coverage and limits. Secondhand AI-report evidence.
[^turn]: [Turn detection](turn-detection-models.md) — Comparison; Operating practice; Coverage and limits. Secondhand AI-report evidence.
