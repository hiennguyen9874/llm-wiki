---
language: [en, es, pt, fr, de, it, sv, vi, ja, ko, id]
pipeline_tag: text-to-speech
tags: [text-to-speech, tts, voice-cloning, onnx, multilingual]
---

# LGTM-TTS

**LGTM (Looks Good To Me)** is a text-to-speech model built by Claude Opus 5.5. Claude wrote the modeling code, collected and processed the training data, designed and ran the experiments, and trained and evaluated the model.

Multilingual text-to-speech at 44.1 kHz with 10 built-in voices and zero-shot voice cloning.
Available in **PyTorch** and **ONNX** (ONNX Runtime needs no PyTorch).

**Languages:** English `en`, Spanish `es`, Portuguese `pt`, French `fr`, German `de`, Italian `it`,
Swedish `sv`, Vietnamese `vi`, Japanese `ja`, Korean `ko`, Indonesian `id`

**Built-in voices:** `F1` `F2` `F3` `F4` `F5` (female), `M1` `M2` `M3` `M4` `M5` (male)

## Samples

All 10 built-in voices across the 11 languages (44.1 kHz).

| Language | Voice | Text | Audio |
|---|---|---|---|
| English | `F1` | The quick brown fox jumps over the lazy dog, then naps in the warm afternoon sun. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/en_F1.wav"></audio> |
| English | `M2` | Could you remind me to call my sister tomorrow morning? I keep forgetting. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/en_M2.wav"></audio> |
| Spanish | `F2` | Hoy hace un día precioso. ¿Te apetece dar un paseo por el parque? | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/es_F2.wav"></audio> |
| Spanish | `M1` | La biblioteca municipal abre a las nueve y cierra a las ocho de la tarde. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/es_M1.wav"></audio> |
| Portuguese | `F3` | Que bom te ver de novo! Vamos tomar um café e conversar um pouco? | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/pt_F3.wav"></audio> |
| Portuguese | `M3` | O comboio para Lisboa parte daqui a vinte minutos, não se atrase. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/pt_M3.wav"></audio> |
| French | `F4` | Bonjour à tous, et bienvenue dans cette nouvelle émission consacrée à la science. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/fr_F4.wav"></audio> |
| French | `M4` | Je pense qu'il va pleuvoir ce soir, n'oublie pas ton parapluie. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/fr_M4.wav"></audio> |
| German | `F5` | Guten Morgen! Hast du gut geschlafen? Heute wird ein langer, aber schöner Tag. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/de_F5.wav"></audio> |
| German | `M5` | Die Bahn hat leider zwanzig Minuten Verspätung, wir sollten ein Taxi nehmen. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/de_M5.wav"></audio> |
| Italian | `F1` | Che bella giornata! Andiamo a prendere un gelato in piazza? | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/it_F1.wav"></audio> |
| Italian | `M2` | Il museo resterà chiuso per lavori fino alla fine del mese prossimo. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/it_M2.wav"></audio> |
| Swedish | `F2` | Hej! Vill du följa med och fika på det nya kaféet vid torget? | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/sv_F2.wav"></audio> |
| Swedish | `M1` | Tåget mot Göteborg är tyvärr försenat på grund av ett signalfel. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/sv_M1.wav"></audio> |
| Vietnamese | `F3` | Xin chào các bạn, hôm nay trời thật đẹp, chúng ta cùng đi dạo công viên nhé! | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/vi_F3.wav"></audio> |
| Vietnamese | `M3` | Cuốn sách này kể về hành trình của một cậu bé đi tìm ước mơ của mình. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/vi_M3.wav"></audio> |
| Japanese | `F4` | こんにちは。今日はとても良い天気ですね。一緒に散歩に行きませんか？ | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/ja_F4.wav"></audio> |
| Japanese | `M4` | 駅までの道を教えていただけますか？初めてこの町に来ました。 | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/ja_M4.wav"></audio> |
| Korean | `F5` | 안녕하세요! 오늘 날씨가 정말 좋네요. 같이 산책하러 갈까요? | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/ko_F5.wav"></audio> |
| Korean | `M5` | 이번 주말에는 가족들과 함께 바닷가에 놀러 갈 예정이에요. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/ko_M5.wav"></audio> |
| Indonesian | `F1` | Selamat pagi semuanya! Hari ini cuacanya cerah sekali, ayo kita jalan-jalan. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/id_F1.wav"></audio> |
| Indonesian | `M2` | Kereta menuju Bandung akan berangkat sepuluh menit lagi dari peron tiga. | <audio controls preload="none" src="https://huggingface.co/polyskill/LGTM/resolve/main/samples/id_M2.wav"></audio> |

## Setup

```bash
git clone https://huggingface.co/polyskill/LGTM
cd LGTM
pip install -r requirements.txt          # PyTorch backend
pip install -r requirements-onnx.txt     # ONNX backend
```

## PyTorch

```python
from lgtm import LGTMTTS

tts = LGTMTTS.from_pretrained(".")            # or "polyskill/LGTM" to download
wav = tts.synthesize("Xin chào, hôm nay trời đẹp quá!", lang="vi", voice="F1")
tts.save_wav(wav, "out.wav")                   # 44.1 kHz mono
```

## ONNX Runtime

```python
from lgtm import LGTMOnnx

tts = LGTMOnnx.from_pretrained(".", use_gpu=False)   # use_gpu=True with onnxruntime-gpu
wav = tts.synthesize("Bonjour à tous, comment allez-vous ?", lang="fr", voice="M1")
tts.save_wav(wav, "out.wav")
```

## Voice cloning

Give 5-15 seconds of clean speech; the voice can then speak any supported language.

```python
voice = tts.clone_voice("reference.wav")      # works with both backends
wav = tts.synthesize("This is my cloned voice.", lang="en", voice=voice)

from lgtm import save_voice_style              # ONNX: from lgtm.onnx_inference import save_voice_style
save_voice_style("my_voice.json", voice)       # reuse later: voice="my_voice.json"
```

## Command line

```bash
python -m lgtm.cli --text "Hej! Hur mår du idag?" --lang sv --voice F2 --out out.wav
python -m lgtm.cli --text "안녕하세요" --lang ko --ref reference.wav --save_voice my_voice.json --out out.wav
python -m lgtm.cli --text "Selamat pagi" --lang id --voice M3 --backend onnx --out out.wav
```

## Options

| argument | default | |
|---|---|---|
| `lang` | `"en"` | language code (see above) |
| `voice` | `"F1"` | preset name, path to a voice `.json`, or `clone_voice()` output |
| `steps` | `8` | denoising steps (fewer = faster, e.g. 5) |
| `speed` | `1.05` | speaking rate (higher = faster) |
| `silence` | `0.3` | seconds of silence between sentences (long text is split automatically) |

## Files

| path | contents |
|---|---|
| `pytorch/model.safetensors` | all weights (synthesis + voice cloning) |
| `onnx/text_encoder.onnx`, `duration_predictor.onnx`, `vector_estimator.onnx`, `vocoder.onnx` | synthesis graphs |
| `onnx/voice_encoder.onnx` | reference audio → voice style (cloning) |
| `voice_styles/*.json` | built-in voices |
| `config.json`, `unicode_indexer.json` | model config, text vocabulary |
| `lgtm/` | inference code (`inference.py` PyTorch, `onnx_inference.py` ONNX, `cli.py`) |

### ONNX graph I/O (for custom runtimes)

| graph | inputs | outputs |
|---|---|---|
| `text_encoder` | `text_ids` int64 [B,T], `style_ttl` [B,50,256], `text_mask` [B,1,T] | `text_emb` [B,256,T] |
| `duration_predictor` | `text_ids`, `style_dp` [B,8,16], `text_mask` | `duration` [B] (seconds) |
| `vector_estimator` | `noisy_latent` [B,144,L], `text_emb`, `style_ttl`, `latent_mask` [B,1,L], `text_mask`, `current_step` [B], `total_step` [B] | `denoised_latent` [B,144,L] |
| `vocoder` | `latent` [B,144,L] | `wav` [B, 3072·L] |
| `voice_encoder` | `wav` [1,N] (44.1 kHz) | `style_ttl` [1,50,256], `style_dp` [1,8,16] |

Sampling loop: `L = ceil(duration·44100 / 3072)`, start from Gaussian noise masked by `latent_mask`,
call `vector_estimator` for `current_step = 0 … total_step-1`, then `vocoder`. See `lgtm/onnx_inference.py`.
