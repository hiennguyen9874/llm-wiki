---
type: Concept
title: CSTR Qwen3-ASR-1.7B GGUF
description: GGUF quantizations (Q4_K, Q8_0, F16) of Qwen3-ASR-1.7B for the CrispASR runtime, including a 2026-07 rebake that keeps the audio encoder at Q8_0 to fix empty or repeated transcripts in the earlier Q4_K export.
tags: [stt, asr, gguf, crispasr, quantization, cpu, edge]
status: stable
created: 2026-10-13
generated: { by: llm-wiki-agent/1, at: 2026-10-13T02:35:20Z }
stale_after: 2027-10-13
sources:
  - id: cstr-qwen3-asr-1.7b-gguf-card
    resource: ../raw/cstr-qwen3-asr-1.7b-GGUF.md
    kind: documentation
    title: CSTR Qwen3-ASR-1.7B GGUF model card
---

This package converts and quantizes the non-HF `Qwen/Qwen3-ASR-1.7B` checkpoint into GGUF files for the [CrispASR](crispasr.md) runtime, in Q4_K (recommended), Q8_0, and F16. Its substantive content is a 2026-07 rebake: the earlier Q4_K export left the 24-layer audio encoder at Q4_K and could emit an empty transcript, or a repeated phrase on longer audio, while still reporting success. The rebaked Q4_K file keeps the encoder at Q8_0; the card says the Q8_0 and F16 files were never affected (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card]

## Files and quantization

| File | Quant | Size (card) | Card note |
| --- | --- | --- | --- |
| `qwen3-asr-1.7b-q4_k.gguf` | Q4_K | ~1.5 GB | "Recommended for most use cases"; audio tower kept at Q8_0 |
| `qwen3-asr-1.7b-q8_0.gguf` | Q8_0 | ~2.5 GB | "Higher quality, more memory" |
| `qwen3-asr-1.7b-f16.gguf` | F16 | ~4.7 GB | "Full precision (needs ~5 GB RAM)" |

- The rebake note says the Q8_0 encoder adds about 0.15 GB over the old Q4_K file, but the capture does not say whether the ~1.5 GB table entry predates the rebake (**Reported**; limit).[^cstr-qwen3-asr-1.7b-gguf-card]
- The card gives no file checksum, commit, or version tag, so a local Q4_K copy cannot be dated from the capture (**Synthesis**).[^cstr-qwen3-asr-1.7b-gguf-card]

## Rebake: audio encoder at Q8_0

- **Failure mode (Reported):** the pre-rebake Q4_K export could produce an empty transcript on some audio, or a repeated phrase on longer audio, without reporting an error. The card cites CrispASR issue #240 for this and attributes it to the sub-8-bit encoder drift diagnosed in issue #218; the issues themselves are not captured.[^cstr-qwen3-asr-1.7b-gguf-card]
- **Fix (Reported):** the 24-layer audio encoder is kept at Q8_0 while the LLM body stays at Q4_K.[^cstr-qwen3-asr-1.7b-gguf-card]
- **Encoder-output cosine versus the F16 reference, JFK sample (Reported):**

| Metric | Old Q4_K encoder | Rebaked Q8_0 encoder |
| --- | ---: | ---: |
| Minimum cosine | 0.9632 | 0.9989 |
| Mean cosine | 0.9913 | 0.9998 |

- The card reads these numbers as near-lossless and says decoding "no longer degenerates". The capture has one audio sample for the cosine check and no before/after transcripts or failing-audio set, so the decode-level result is a source assertion, not a tested outcome (**Reported**; scope limit **Synthesis**).[^cstr-qwen3-asr-1.7b-gguf-card]

## Usage with CrispASR

```bash
crispasr -m qwen3-1.7b -f audio.wav                      # alias; card comment says Q4_K
crispasr -m qwen3-asr-1.7b-q4_k.gguf -f audio.wav --backend qwen3
crispasr -m qwen3-1.7b -f audio.wav -l ja                # language hint
crispasr -m qwen3-1.7b -f audio.wav --translate --target-lang en
```

- These are the card's commands; none were run for this wiki (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card]
- The card's comment says the `qwen3-1.7b` alias auto-downloads the Q4_K file, but the capture does not show which repository the alias resolves to (**Synthesis**). Backend naming is catalogued in [CrispASR ASR Backend Selection](crispasr-asr-backend-selection.md).

## Performance

- **Reported:** Q4_K runs at "0.2x realtime" on CPU with 4 threads on the 11 s English JFK sample, with "perfect transcription accuracy". Read as a real-time factor near 0.2, that is roughly 2.2 s of compute for 11 s of audio; the unit is ambiguous in the card, so this reading is **Synthesis**.[^cstr-qwen3-asr-1.7b-gguf-card]
- Not established by the capture: CPU model, CrispASR build, whether the timing predates or follows the rebake, timings for Q8_0 or F16, and any WER or multi-clip result. One clip is not a benchmark.

## Conversion

The card's recipe (**Reported**; not executed):

```bash
python models/convert-qwen3-asr-to-gguf.py \
    --input Qwen/Qwen3-ASR-1.7B \
    --output qwen3-asr-1.7b-f16.gguf
crispasr-quantize qwen3-asr-1.7b-f16.gguf qwen3-asr-1.7b-q4_k.gguf q4_k
```

- The source is the non-HF `Qwen/Qwen3-ASR-1.7B`. The card says the converter also accepts the `-hf` variant (`Qwen/Qwen3-ASR-1.7B-hf`, different tensor naming) and that both produce identical results (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card] The `-hf` checkpoints are covered in [Qwen3-ASR family](qwen3-asr-family.md).
- Limit: by the card's own account, the pre-rebake file kept the encoder at Q4_K, and this recipe names no encoder exception. The capture gives no command for the Q8_0 audio-encoder variant, so how the current Q4_K file is produced cannot be confirmed (**Synthesis**).
- The converter script and `crispasr-quantize` are not in `raw/`.

## Architecture

Card-reported specification (**Reported**):

- Audio encoder: 24-layer Whisper-style encoder (d=1024, 16 heads, GELU).
- Projector: 2-layer MLP (1024 → GELU → 2048).
- LLM decoder: 28-layer Qwen3 (d=2048; 16 query and 8 KV heads; head_dim 128; SwiGLU).
- Vocabulary 151,936 tokens (GPT-2 BPE); RoPE theta 1,000,000.

The card gives no parameter totals. Parameter splits for the family are in [Qwen3-ASR family](qwen3-asr-family.md).

## Provenance and licence

- Upstream `Qwen/Qwen3-ASR-1.7B` is Apache-2.0; this package redistributes under the same terms and grants no additional rights (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card]
- The work is format conversion and quantization only: no training, fine-tuning, merging, distillation, or change to architecture, vocabulary, or capability (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card]
- The card's EU AI Act Art. 53 note says the upstream Qwen authors remain the provider and that questions on training data, copyright policy, or capability belong upstream. The legal characterization is the card's and is not checked here (**Reported**).[^cstr-qwen3-asr-1.7b-gguf-card]

## Relationships

- Quantized derivative of the 1.7B checkpoint in [Qwen3-ASR family](qwen3-asr-family.md); language coverage, benchmarks, and Transformers or vLLM serving belong to that concept, not this package (**Synthesis**).[^cstr-qwen3-asr-1.7b-gguf-card]
- Runtime: consumed through [CrispASR](crispasr.md) with the `qwen3` and `qwen3-1.7b` backends (**Synthesis**).[^cstr-qwen3-asr-1.7b-gguf-card]
- Different packaging: [audio.cpp GGUF Model Packages](audio-cpp-gguf-packages.md) lists a `Qwen3-ASR-1.7B-GGUF` directory with F16 and Q8 files for another runtime. The capture does not establish whether files are shared, so no weight identity is asserted (**Synthesis**).
- Llama.cpp-served sibling: [ggml-org Qwen3-ASR-1.7B GGUF](ggml-org-qwen3-asr-1.7b-gguf.md) packages the same base checkpoint for `llama-server -hf`. Its card names no quantization, file list, or license, so no file or quality comparison is asserted (**Synthesis**). A transcribe.cpp sibling, [handy-computer Qwen3-ASR-1.7B GGUF](handy-computer-qwen3-asr-1.7b-gguf.md), packages the same checkpoint in BF16 through Q4_K_M. Its card does not say whether the audio encoder is quantized apart from the LLM, so its Q4_K_M row is no evidence either way on the encoder-drift failure above (**Synthesis**).

## Coverage and limits

- Entry point: one model-card capture, `raw/cstr-qwen3-asr-1.7b-GGUF.md`, inspected statically (**Observed**). The capture records no revision, commit, or upload date, and does not state the Hugging Face repository URL of the package.
- Not captured or executed: the three GGUF files, the converter and quantizer, CrispASR issues #218 and #240, the JFK sample, and the CPU timing environment. Nothing was downloaded, converted, transcribed, or benchmarked.
- The rebake is dated only as "2026-07" with no day. The card's timings and cosine figures are source assertions.
- Time-sensitive: release-specific file behavior and timing; `stale_after` follows the `stt` domain rule.
- No sensitive values were found in the capture.

[^cstr-qwen3-asr-1.7b-gguf-card]: [CSTR Qwen3-ASR-1.7B GGUF model card](../raw/cstr-qwen3-asr-1.7b-GGUF.md) — locators: frontmatter (`license`, `base_model`, `pipeline_tag`, `tags`); intro paragraph (GGUF quantizations for CrispASR, upstream link); `Files` table (three quant rows, sizes, notes); `2026-07 rebake` section (Q8_0 audio-tower note, #240 and #218 references, JFK cosine table, "no longer degenerates" sentence); `Usage with CrispASR` fence (four commands, `qwen3-1.7b` alias comment); `Performance` (JFK 11 s, Q4_K "0.2x realtime" on CPU with 4 threads, "perfect transcription accuracy"); `Conversion` fence and `-hf` note; `Architecture` list; `License`; `Provenance and EU AI Act Art. 53 note`.
