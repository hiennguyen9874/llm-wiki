---
license: apache-2.0
base_model:
  - IndexTeam/Index-Echo-S2TT-2B
  - IndexTeam/Index-Echo-S2TT-9B
library_name: audio.cpp
pipeline_tag: automatic-speech-recognition
tags:
  - audio.cpp
  - gguf
  - speech-translation
  - subtitles
  - chinese
---

# Index-Echo-S2TT GGUF

GGUF packages for native speech-to-text translation with
[audio.cpp](https://github.com/0xShug0/audio.cpp). Chinese speech produces
timestamped source transcripts and English, Spanish, or Japanese translations.
This port supports **S2TT only**; it does not generate translated speech.
**There is room to improve 9B output parity and quantized quality**. Focused PRs
with reproducible C++/Python comparisons are welcome.

Note that 2B and 9B use the same C++ translation path, including the prompt, audio encoder, 
decoder implementation, and greedy sampler. 2B orig is parity safe, while 9B orig has drifts.
2B has 24 layers and tied token/output embeddings; 9B has 32 layers and a separate LM head. 
That can change how sensitive their outputs are to numerical differences, 
but I have not proved that it explains the 9B mismatch.

## Upstream and Packages

These files were converted from the official
[2B checkpoint](https://huggingface.co/IndexTeam/Index-Echo-S2TT-2B/tree/72fd8bdc9bf8251f1c35f6d6289a950eda154395)
at `72fd8bdc9bf8251f1c35f6d6289a950eda154395` and
[9B checkpoint](https://huggingface.co/IndexTeam/Index-Echo-S2TT-9B/tree/05f86cb7a38684916e193282b6cc02462ace4043)
at `05f86cb7a38684916e193282b6cc02462ace4043`. Each GGUF embeds the
audio tower, connector, text decoder, tokenizer, configuration, and audio.cpp
model spec. The unused vision weights are not included.

| File | Size | Recommendation |
|---|---:|---|
| `index-echo-s2tt-2b-orig.gguf` | 4.76 GiB | Default 2B package; original checkpoint precision. |
| `index-echo-s2tt-2b-q8_0.gguf` | 2.97 GiB | 2B Q8_0; same WER/CER as original on the 20-clip diagnostic set. |
| `index-echo-s2tt-2b-q4_k.gguf` | 2.14 GiB | Experimental 2B Q4_K; linear-attention QKV projections remain Q8_0. |
| `index-echo-s2tt-9b-orig.gguf` | 17.95 GiB | Original 9B precision and quality reference. |
| `index-echo-s2tt-9b-q8_0.gguf` | 10.44 GiB | Recommended 9B quantization in these tests. |

**9B Q4_K is not provided.** It repeated or omitted speech on short clips and
failed a long-form request with incomplete subtitle cues, despite passing the
short smoke test. The 2B Q4_K package completed the 20 clips below, but that
small set does not establish general reliability. Use Q8_0 or original
precision when transcript quality matters. The underlying model can also
repeat on some audio even at original precision; inspect subtitles before
using them as ground truth.

## C++ vs Python: Output Comparison

The test uses 20 distinct Chinese clips from the public
[FLEURS Chinese test split](https://huggingface.co/datasets/google/fleurs),
with speech windows trimmed using the official Python Silero VAD. This holds
the input window fixed across implementations. Source Chinese lines, not
translations, were scored against the FLEURS references; WER uses Jieba word
segmentation and CER uses normalized characters. This is a small diagnostic
slice, **not** a broad model-quality benchmark. The WER/CER table measures
source transcription only; it does not measure translation quality.

| Checkpoint and setting | Completed clips | Python WER / CER | C++ WER / CER |
|---|---:|---:|---:|
| 2B original, greedy | 20/20 | 16.23% / 17.26% | 16.23% / 17.26% |
| 2B Q8_0, greedy | 20/20 | 16.23% / 17.26% | 9.55% / 12.12% |
| 2B Q4_K, greedy | 20/20 | 16.23% / 17.26% | 9.07% / 11.87% |
| 9B original, greedy | 19/20 | 7.77% / 11.02% | 8.27% / 11.28% |
| 9B Q8_0, greedy | 19/20 | 7.77% / 11.02% | 8.27% / 11.41% |

Clip `zh_016` caused repetition for both Python 9B and C++ 9B variants and is
excluded from their scores. With BF16 decoder activation rounding, C++ 2B
original follows Python's five-cue output on `zh_000`, including its repeated
ending. The lower Q8_0/Q4_K WER is mostly due to those variants ending after
two cues on that clip; it is not evidence of better transcription quality.

We also compared the saved subtitle cues directly. The 2B original row uses
all 20 clips; the 2B quantized rows exclude `zh_000`, and all 9B rows exclude
`zh_016`. Each pair below has the same cue count and is
matched in order. Text agreement ignores case, spaces, and punctuation;
timestamp agreement counts start and end points within 0.1 seconds.

| C++ package vs official Python | Source cues identical | Translation cues identical | Timestamp points within 0.1 s |
|---|---:|---:|---:|
| 2B original | 52/52 | 49/52 | 103/104 |
| 2B Q8_0 | 47/47 | 42/47 | 93/94 |
| 2B Q4_K | 41/47 | 26/47 | 89/94 |
| 9B original | 45/48 | 42/48 | 94/96 |
| 9B Q8_0 | 47/48 | 42/48 | 96/96 |

These are output-agreement checks, not an independent translation-quality
score or a claim of byte-identical parity. With the same VAD-trimmed inputs and
greedy decoding, the 2B original package's 52/52 matching source cues and
103/104 close timestamp endpoints provide strong evidence that the main model
math and decoding logic agree with Python. Its translations still differ in
3/52 cues, so this does not establish identical intermediate calculations.
In particular, 2B Q4_K's similar source WER hides more translation changes.

For 9B orig and the `zh_004` test case, Python keeps the second phrase in one
cue while C++ splits it into two; the largest timestamp difference reflects
that boundary shift, not missing audio.

## Ordinary CUDA Performance

- NVIDIA RTX 5090; audio.cpp Debug build and official PyTorch inference. One
  6.2-second request warmed the loaded model, followed by **one 180.3-second
  request**. The long WAV concatenates the 20 distinct Chinese FLEURS speech
  clips above; it is a long-form workload, not a natural continuous recording.
- The table times only that second, long request, excluding model loading and
  the warmup. RTF is its wall time divided by 180.3 seconds. C++ uses its
  quiet-energy windowing; official Python uses Silero VAD, so their window
  boundaries and generated cue counts are not identical.
- Python used its packaged default BF16 loading. C++ used each GGUF's stored
  weight type; original-precision packages also round decoder activations to
  BF16, while quantized packages retain their existing execution path. Neither
  run forced TF32 or used parity-only controls. Both used greedy decoding.
- Peak VRAM was sampled with `nvidia-smi` every 50 ms across loading, warmup,
  and the long request, with no other GPU process running. It is device memory
  used, not just the PyTorch allocator's tensor count.

| Path | Long request wall | RTF | Peak VRAM |
|---|---:|---:|---:|
| Official Python 2B | 29.5 s | 0.164 | 7,138 MiB |
| audio.cpp 2B original | 9.56 s | 0.053 | 7,818 MiB |
| audio.cpp 2B Q8_0 | 7.12 s | 0.039 | 5,987 MiB |
| audio.cpp 2B Q4_K | 6.44 s | 0.036 | 5,120 MiB |
| Official Python 9B | 40.9 s | 0.227 | 20,632 MiB |
| audio.cpp 9B original | 32.46 s | 0.180 | 21,781 MiB |
| audio.cpp 9B Q8_0 | 20.94 s | 0.116 | 13,996 MiB |

All completed C++ runs produced subtitle cues through approximately 03:00.
These figures describe this input and machine, not a general latency or
accuracy guarantee.

## Usage

```bash
audiocpp_cli --task asr --family index_echo \
  --model /path/to/Index-Echo-S2TT-GGUF/index-echo-s2tt-9b-q8_0.gguf \
  --backend cuda --audio input.wav \
  --request-option target_language=en \
  --text-out subtitles.txt --log
```

Set `target_language` to `en`, `es`, or `ja`. For long input, audio.cpp uses
windowed inference and carries the previous five windows of transcript and
translation as context. Its default quiet-energy windowing is not identical
to the official Python Silero VAD, so boundaries and output may differ. See
the [model guide](https://github.com/0xShug0/audio.cpp/blob/main/docs/models/index_echo.md)
for conversion and request options.

## License

The weights retain the upstream [Apache-2.0 license](LICENSE). Conversion
does not replace the upstream license terms.
