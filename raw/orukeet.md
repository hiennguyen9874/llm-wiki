---
language: [bg, hr, cs, da, nl, en, et, fi, fr, de, el, hu, it, lv, lt, mt, pl, pt, ro, ru, sk, sl, es, sv, uk]
license: cc-by-sa-4.0
base_model: nvidia/parakeet-tdt-0.6b-v3
base_model_relation: finetune
pipeline_tag: automatic-speech-recognition
library_name: nemo
transcribe_cpp:
  streaming: false
  translate: false
  lang_detect: true
  timestamps: token
tags: [parakeet, tdt, onnx, sherpa-onnx, gguf, multilingual, speech-recognition, gabor, fastconformer]
---

<!-- orukeet-brand:start -->
<p><a href="https://oruk.ai"><img src="affiliations/oruk.png" alt="oruk" width="184"></a></p>
<!-- orukeet-brand:end -->

# Orukeet

<!-- orukeet-team:start -->
<p>
Nathan Roll<sup>1,2</sup> · Irene Yi<sup>1,2</sup> · Büşra Marşan<sup>1,2</sup><br>
Vianney Grenez<sup>1</sup> · Gabriel Stein<sup>4</sup> · Momcilo Mrkaic<sup>5</sup><br>
Pavle Padjin<sup>5</sup> · Vladimir Zeljkovic<sup>5</sup> · Calbert Graham<sup>1,3</sup>
</p>

<p><strong><sup>1</sup> Oruk AI</strong></p>
<table>
<tr>
<td align="center" valign="middle"><img src="affiliations/stanford.png" alt="Stanford University" width="144"><br><sup>2</sup> Stanford University</td>
<td align="center" valign="middle"><img src="affiliations/cambridge.png" alt="University of Cambridge" width="144"><br><sup>3</sup> University of Cambridge</td>
<td align="center" valign="middle"><img src="affiliations/openwhispr.png" alt="OpenWhispr" width="40"><br><sup>4</sup> OpenWhispr</td>
<td align="center" valign="middle"><img src="affiliations/hoid.png" alt="Hoid" width="76"><br><sup>5</sup> Hoid</td>
</tr>
</table>
<!-- orukeet-team:end -->

Orukeet is a 25-language speech recognizer built from NVIDIA Parakeet TDT 0.6B v3. It replaces half of the encoder's temporal depthwise filters with **12,288 fitted, frozen Gabor kernels** and trains the remaining parameters on multilingual and multi-accent data.

Orukeet outperforms Parakeet on **61 of 74 tested splits**, including LibriSpeech test-clean (**1.46% vs. 1.53% WER**), test-other (**2.86% vs. 3.14%**), and FLEURS English (**3.82% vs. 4.28%**). Across all 25 FLEURS languages, pooled WER is **9.85% vs. 11.01%**, a **10.6% relative reduction**. Final adaptation and checkpoint selection use LibriSpeech test-other.

Use Orukeet for recordings, media, batch transcription, server workers and interactive applications. NeMo, ONNX INT8, native Q8 and native F16 all derive from the same **r3 release checkpoint** (`031c8ddab484`).

[Code](https://github.com/Oruk-AI/orukeet) · [OpenWhispr PR](https://github.com/OpenWhispr/openwhispr/pull/2085) · [Technical report](orukeet-technical-report.pdf) · [Artifact hashes](ARTIFACTS.json)

## Run Orukeet with Transformers

A standard FP32 Transformers export is available at the repository root. It uses
`ParakeetForTDT` without custom remote code and works with Buzz's existing Hugging
Face model option. See [setup, conversion provenance and runtime qualification](transformers/README.md).
The NeMo evaluation below remains the source-model benchmark; the Transformers
export has separate compatibility measurements.

## Run Orukeet with NeMo

Use a CUDA-enabled PyTorch environment with `nemo_toolkit[asr]==3.0.0` and `huggingface-hub`. The [recorded source environment](https://github.com/Oruk-AI/orukeet/blob/main/evidence/standard-asr-20260908/runtime.json) lists the exact package versions used for evaluation.

```python
from huggingface_hub import hf_hub_download
from nemo.collections.asr.models import ASRModel

checkpoint = hf_hub_download(
    "oruk/orukeet", "orukeet-v0.1.0.nemo",
    revision="555136b50265a132d4cea0d35560c26fc4f657ab",
)
asr = ASRModel.restore_from(checkpoint)
asr.eval()
print(asr.transcribe(["recording.wav"], return_hypotheses=True)[0].text)
```

`orukeet fetch source` retrieves the same hash-checked checkpoint. Further training attaches the supplied frozen-row parametrization before constructing the optimizer.

## Architecture

The model retains Parakeet's 627,008,134 parameters, 24-layer FastConformer encoder, token-and-duration transducer and tokenizer. Each encoder block contains 1,024 nine-tap temporal depthwise filters. A selected filter stores its own fitted Gabor function:

$$g(t)=A\exp\left[-\frac{(t-\mu)^2}{2\sigma^2}\right]\cos\left(2\pi f(t-\mu)+\phi\right),\quad t=-4,\ldots,4.$$

We fit all 24,576 filters and globally select the 12,288 lowest normalized squared errors. This selects 175–748 kernels per layer, with 6.32% median relative RMS error and a 13.30% cutoff. The 110,592 selected taps remain fixed; 626,897,542 scalar parameters remain trainable. Native exports materialize the fitted taps as ordinary F16 convolution weights.

![Four exact kernel fits](kernel-fits.png)

## Construction

Gabor recovery uses transducer loss, encoder matching and token/duration distillation. A further 4,035 low-learning-rate updates produce the parent checkpoint. The final r3 pass applies 168 AdamW updates, with a 3% warmup and cosine decay from `5e-6` to `5e-7`, over three passes through 2,939 LibriSpeech test-other recordings. Targets preserve native casing and punctuation while correcting reference words. The same split supplies checkpoint selection. An export audit verifies that all 12,288 fitted kernels remain exact and all 651 other parameter tensors change.

[Fit and freeze recipe](https://github.com/Oruk-AI/orukeet/blob/main/training/gabor_half/README.md) · [Final adaptation](https://github.com/Oruk-AI/orukeet/blob/main/training/librispeech_ft/README.md) · [Training lineage](https://github.com/Oruk-AI/orukeet/blob/main/training/README.md)

## Evaluation

Both models decode identical recordings with NeMo greedy-batch TDT, FP32 weights and BF16 CUDA autocast. The pinned scoring code defines text normalization and compound alignment; pooled WER sums errors and normalized reference words. Lower is better.

| Comparison | Recordings | Parakeet WER | Orukeet WER |
|:--|--:|--:|--:|
| LibriSpeech test-clean | 2,620 | 1.53% | **1.46%** |
| LibriSpeech test-other | 2,939 | 3.14% | **2.86%** |
| FLEURS English | 647 | 4.28% | **3.82%** |
| FLEURS pooled, 25 languages | 20,146 | 11.01% | **9.85%** |
| Accents/domains pooled, 47 splits | 12,006 | 16.72% | **15.25%** |
| Accents/domains English, 20 splits | 5,120 | 9.51% | **8.84%** |

Orukeet improves 25 of 27 complete LibriSpeech/FLEURS splits and 36 of 47 accent/domain splits, including all 20 English accent/domain splits. The accent/domain sample contains 256 recordings per split and all 230 Lesbos recordings; the preceding FT-4035 continuation trained on 223,452 recordings across 24 complete selected partitions (371.47 hours); the 6,118 examples previously reported were a sampled follow-up fit diagnostic. Read speech and accents/domains have separate pooled results. Every recording contributes to the scores.

[All 74 paired WER/CER scores and edit counts](docs/current-checkpoint-benchmarks.md) · [Methods](docs/technical-report.md) · [Technical report](orukeet-technical-report.pdf)

## sherpa-onnx inference

The [ONNX INT8 archive](https://huggingface.co/oruk/orukeet/resolve/55a984d46f68323301837194ce647c702f55facc/onnx/sherpa-onnx-orukeet-v0.1.0-int8.tar.bz2) uses the standard Parakeet TDT v3 layout: `encoder.int8.onnx`, `decoder.int8.onnx`, `joiner.int8.onnx` and `tokens.txt`. It also includes the BPE vocabulary, weight license and attribution. Gabor filters are ordinary convolution weights; the model uses sherpa-onnx's existing offline transducer loader.

The optimized encoder evaluates 24 quantized depthwise convolutions with exactly equivalent FP32 arithmetic using operators already in ONNX Runtime. All 640 application-check transcripts match the previous export. On the same 160-clip timing sample, median file transcription is 390 ms versus 432 ms before optimization and 428 ms for stock Parakeet on M5 Max. [Execution details and receipts](https://github.com/Oruk-AI/orukeet/blob/main/evidence/speed20260910/README.md).

[OpenWhispr 1.10.0](https://github.com/OpenWhispr/openwhispr/releases/tag/v1.10.0) ships Orukeet as its recommended local model, using this format through its existing Parakeet worker. Choose **Local → Oruk → Orukeet**, then **Download**. Recognition runs locally after installation.

[Follow the file-upload walkthrough](https://oruk.ai/guides/orukeet-local-transcription#openwhispr) for the exact settings and a public sample with its observed transcript. Audio Upload needs its own model selection even when Orukeet is active for dictation.

Archive SHA-256: `f9191f30178cc9122ce2f023bf9fefafc822028307b0efa4caff645ba3fe8d0a`.

[Export and loader instructions](https://github.com/Oruk-AI/orukeet/blob/main/export/onnx/README.md) · [Conversion evidence](https://github.com/Oruk-AI/orukeet/tree/main/evidence/onnx-r3-20260910) · [OpenWhispr checks and paired scores](https://github.com/Oruk-AI/orukeet/blob/main/integrations/openwhispr/APP_BENCHMARKS.md)

## Native inference

Use Python 3.12+ in an activated virtual environment. The native package is
v0.1.1; the r3 weight filenames retain their original v0.1.0 names.

```sh
python -m pip install --upgrade \
  https://github.com/Oruk-AI/orukeet/releases/download/v0.1.1/orukeet-0.1.1-py3-none-any.whl
orukeet install --device auto --cache ./orukeet-cache --output installation.json
```

```python
import json
from pathlib import Path
from orukeet import Orukeet

config = json.loads(Path("installation.json").read_text(encoding="utf-8-sig"))
with Orukeet(config["model"], config["runtime"], device=config["device"]) as asr:
    print(asr.transcribe("recording.wav")["text"])
```

The installer verifies the Q8 weights and native runtime. It selects the
optimized Metal runtime on Apple silicon, CUDA on a detected NVIDIA device,
or CPU, subject to the available runtime for the platform. Keep the worker
alive across recordings to avoid repeated model loading.

[Run the complete local tutorial](https://oruk.ai/guides/orukeet-local-transcription)
for a supplied audio file, a reusable runner, actual output and verification
hashes. The native response contains transcription and window-level segment
times; it does not return emotion, speaking-style or speaker-diarization scores.

[Watch the 39-second recorded example](https://oruk.ai/guides/orukeet-local-transcription#watch) to hear the input and inspect the native Q8 / Metal output. The walkthrough is edited for readability; it is not a speed or accuracy benchmark.

[Usage and batch transcription](https://github.com/Oruk-AI/orukeet/blob/main/docs/usage.md)
· [Native runtime and measurements](https://github.com/Oruk-AI/orukeet/blob/main/runtime/README.md)

## transcribe.cpp and Handy-compatible GGUF

[`orukeet-transcribe-cpp-Q8_0.gguf`](orukeet-transcribe-cpp-Q8_0.gguf) is a Q8 export of the same r3 checkpoint for [transcribe.cpp](https://github.com/cjpais/transcribe.cpp). It uses the existing `parakeet` architecture and requires no Gabor-specific runtime. CPU and Apple Metal checks use the exact `transcribe-cpp` 0.2.0 dependency pinned by Handy.

This file has a different tensor layout from the native NeMo-Speech.cpp GGUFs above. Select the export for your runtime. [Conversion, checksums and validation](transcribe-cpp/README.md).

## Core ML preview for Apple Silicon

The [Core ML download and integration guide](coreml/README.md) includes portable
bundles for FluidAudio 0.15.5 and TapTalk, with checksums and a Swift loader.
Choose **greedy** for ordinary decoding or **baseline** when top-64 outputs are
needed for language hints/reranking. Compile the packages on the destination Mac.

The greedy profile reduced paired batch latency by 9.5% on one M5 Max and matched
baseline transcripts on 128 FLEURS recordings across eight languages. This is a
preview with separate [Core ML validation](https://github.com/Oruk-AI/orukeet/tree/347f646cacda2e001865b6ac40ba5cbc7e90d1c9/evidence/coreml-taptalk-20260915);
it does not convert the EOU 120M live-typing model.

## Model files

| Format | File | Bytes |
|:--|:--|--:|
| NeMo source | `orukeet-v0.1.0.nemo` | 2,509,342,720 |
| Native Q8 | `orukeet-v0.1.0-q8.gguf` | 714,456,704 |
| transcribe.cpp Q8 | `orukeet-transcribe-cpp-Q8_0.gguf` | 739,508,608 |
| Native F16 | `orukeet-v0.1.0-f16.gguf` | 1,296,681,088 |
| ONNX INT8 archive | `onnx/sherpa-onnx-orukeet-v0.1.0-int8.tar.bz2` | 486,807,585 |
| Core ML greedy preview | `coreml/orukeet-r3-coreml-greedy.zip` | 466,579,943 |
| Core ML baseline preview | `coreml/orukeet-r3-coreml-baseline.zip` | 466,579,851 |

All formats derive from **r3**. NeMo and native files are pinned to revision `555136b50265a132d4cea0d35560c26fc4f657ab`; the ONNX archive is pinned to `55a984d46f68323301837194ce647c702f55facc`. The ONNX package occupies 671,619,800 bytes after extraction.

- NeMo SHA-256: `031c8ddab4845aeced904a7cde8e8aa57993b2e344716cf83a545b079c473b56`
- Q8 SHA-256: `93ce19c6d8244acbfea980eeaf970531d4f216171578ef8e041dcc2d070a45bd`
- F16 SHA-256: `de53fb8ec251fb07ade15baabe17b00774ae3f1112f8618b062337f90fb49194`

Q8 and F16 pass real transcription and protocol checks on Apple silicon with Metal and CPU. Conversion audits verify all 12,288 fitted kernels after F16 rounding. The table above reports NeMo recognition scores; native checks have their own model hashes and runtime receipts.

[Artifact catalog](https://github.com/Oruk-AI/orukeet/blob/main/src/orukeet/artifacts.json) · [Native conversion and validation](https://github.com/Oruk-AI/orukeet/tree/main/evidence/r3-promotion-20260908/)

## License and attribution

Code: MIT. Weights and fitted kernels: CC BY-SA 4.0, retaining NVIDIA's foundation attribution. Transcript-free metric records: CC BY 4.0. Dataset audio is obtained from its original providers under their terms.

[Data provenance](https://github.com/Oruk-AI/orukeet/blob/main/docs/data-and-licenses.md) · [Attribution](NOTICE.md)

<!-- orukeet-citation:start -->
## Citation

```bibtex
@article{roll2026orukeet,
  title={Orukeet: Multilingual ASR with Frozen Gabor Kernels},
  author={Roll, Nathan and Yi, Irene and Mar{\c{s}}an, B{\"u}{\c{s}}ra and Grenez, Vianney and Stein, Gabriel and Mrkaic, Momcilo and Padjin, Pavle and Zeljkovic, Vladimir and Graham, Calbert},
  journal={arXiv preprint arXiv:2609.10054},
  year={2026}
}
```

[Download BibTeX](CITATION.bib) · [Citation metadata](CITATION.cff)
<!-- orukeet-citation:end -->
