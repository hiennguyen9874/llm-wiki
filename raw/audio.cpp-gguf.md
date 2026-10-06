---
license: other
library_name: audio.cpp
pipeline_tag: text-to-speech
tags:
- gguf
- audio.cpp
- quantized
- text-to-speech
- automatic-speech-recognition
- voice-conversion
- text-to-audio
- audio-to-audio
- source-separation
- speaker-diarization
- speech
base_model_relation: quantized
base_model:
- MiniMaxAI/MiniMax-H3
- ACE-Step/Ace-Step1.5
- ACE-Step/acestep-v15-base
- Aratako/Irodori-TTS-500M-v3
- Aratako/Irodori-TTS-600M-v3-VoiceDesign
- Aratako/Irodori-TTS-v4.1-Small
- Aratako/MioCodec-25Hz-44.1kHz-v2
- Aratako/MioTTS-1.7B
- Aratako/Semantic-DACVAE-Japanese-32dim
- Banafo/Kroko-ASR
- dots-studio/dots.tts-mf
- dots-studio/dots.tts-soar
- fishaudio/s2-pro
- FunAudioLLM/Fun-ASR-Nano-2512-hf
- ai-sage/GigaAM-Multilingual
- ai-sage/GigaAM-v3
- HeartMuLa/HeartCodec-oss-20260123
- HeartMuLa/HeartMuLa-oss-3B
- HeartMuLa/HeartMuLaGen
- IndexTeam/IndexTTS-2
- IndexTeam/IndexTTS-2.5
- ASLP-lab/MeanVC2
- OpenBMB/VoxCPM2
- OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano
- OpenMOSS-Team/MOSS-Audio-Tokenizer-v2
- OpenMOSS-Team/MOSS-TTS-Local-Transformer-v1.5
- OpenMOSS-Team/MOSS-TTS-Nano-100M
- Qwen/Qwen3-ASR-0.6B
- Qwen/Qwen3-ASR-1.7B-hf
- Qwen/Qwen3-ForcedAligner-0.6B
- Qwen/Qwen3-TTS-12Hz-0.6B-Base
- Qwen/Qwen3-TTS-12Hz-1.7B-Base
- Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice
- Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
- Qwen/Qwen3-TTS-Tokenizer-12Hz
- ResembleAI/chatterbox
- RMSnow/Vevo2
- bosonai/higgs-audio-v3-stt
- bosonai/higgs-audio-v3-tts-4b
- k2-fsa/OmniVoice
- kyutai/pocket-tts
- llm-jp/llm-jp-3-150m
- microsoft/VibeVoice-1.5B
- microsoft/VibeVoice-ASR
- mistralai/Voxtral-Mini-4B-Realtime-2602
- mlx-community/SeedVC-MLX
- mlx-community/mel-roformer-mlx
- mlx-community/supertonic-3-mlx
- mlx-community/wavlm-base-plus-mlx
- MuScriptor/muscriptor-small
- neuphonic/neutts-2e
- syvai/hviske-v5.3
- nvidia/diar_sortformer_4spk-v1
- nvidia/magpie_tts_multilingual_357m
- nvidia/nemotron-3.5-asr-streaming-0.6b
- nvidia/parakeet-tdt-0.6b-v3
- nvidia/personaplex-7b-v1
- owensong/Inflect-Micro-v2
- stabilityai/stable-audio-3-medium
- stabilityai/stable-audio-3-small-music
- stabilityai/stable-audio-3-small-sfx
---

# audio.cpp GGUF Model Packages

This directory contains audio.cpp-native GGUF conversions of multiple speech models. These files are intended for use with [audio.cpp](https://github.com/0xShug0/audio.cpp).

If you enjoy the project, please star [audio.cpp on GitHub](https://github.com/0xShug0/audio.cpp) and this Hugging Face repository.

For conversion details, supported layouts, direct-file loading, sidecar embedding, and the latest compatibility notes, see the audio.cpp GGUF guide:

- https://github.com/0xShug0/audio.cpp/blob/main/docs/gguf.md

!!! Converted and quantized packages are checked with automated metrics, but perceived quality can still differ for human listeners. Please validate the exact package, backend, and route to confirm the output is acceptable for your use case.


## Files

The table lists the GGUF packages currently provided by this repository. License
names follow audio.cpp's [model license reference](https://github.com/0xShug0/audio.cpp/blob/main/docs/model_licenses.md), which also records commercial-use conditions and other important notes.

| Directory | audio.cpp family | GGUF provided | Original model license |
|---|---|---|---|
| `ACE-Step1.5-GGUF` | `ace_step` | BF16 + Q8 | MIT |
| `Apollo-GGUF` | `apollo` | original | CC-BY-SA-4.0 |
| `AudioSR-GGUF` | `audiosr` | F32 | Apache-2.0 |
| `BS-RoFormer-ep368-GGUF` | `bs_roformer` | Q8 | Apache-2.0 (checkpoint source undocumented) |
| `Breeze-TTS-2-GGUF` | `breeze_tts` | BF16 + Q8 + Q4 | [BreezeBlue Research and Non-Commercial License](https://huggingface.co/BreezeBlue/Breeze-TTS-2/blob/main/LICENSE) |
| `Canary-180M-Flash-GGUF` | `canary_asr` | F32 + Q8 | CC-BY-4.0 |
| `Chatterbox-GGUF` | `chatterbox` | F16 + Q8 | MIT |
| `Chatterbox-Turbo-GGUF` | `chatterbox_turbo` | Q8 | MIT |
| `Citrinet-ASR-GGUF` | `citrinet_asr` | Q8 | CC-BY-4.0 |
| `Cohere-Transcribe-GGUF` | `cohere_asr` | BF16 + Q8 + Q4_0 | Apache-2.0 |
| `Confucius4-TTS-GGUF` | `confucius4_tts` | original | Apache-2.0 |
| `ControlFoley-GGUF` | `controlfoley` | F32 | CC-BY-NC-4.0 |
| `CosyVoice3-GGUF` | `cosyvoice3` | F32 + Q8 | Apache-2.0 |
| `CrisperWhisper2.0-GGUF` | `crisperwhisper` | BF16 + Q8 + Q4_K | nyra health Non-Commercial Research License |
| `DotTTS-Edit-GGUF` | `dots_tts` | BF16 + Q8 | Apache-2.0 |
| `DotTTS-MF-GGUF` | `dots_tts` | BF16 | Apache-2.0 |
| `DotTTS-SOAR-GGUF` | `dots_tts` | original + BF16 | Apache-2.0 |
| `DramaBox-GGUF` | `dramabox` | Q8 | [LTX-2 Community License](https://huggingface.co/ResembleAI/Dramabox/blob/main/LICENSE) |
| `FireRedAudio-GGUF` | `firered_audio` | original + Q8 | Apache-2.0 |
| `FireRedTTS3-Base-GGUF` | `fireredtts3` | original + Q8 | Apache-2.0 |
| `FireRedTTS3-Instruct-GGUF` | `fireredtts3` | original + Q8 | Apache-2.0 |
| `Fish-Audio-S2-Pro-GGUF` | `fish_audio` | BF16 + Q8 | [Fish Audio Research License](https://huggingface.co/fishaudio/s2-pro/blob/main/LICENSE.md) |
| `Fun-ASR-Nano-2512-GGUF` | `fun_asr_nano` | F16 + Q8 | Apache-2.0 |
| `GigaAM-ASR-GGUF` | `gigaam_asr` | F16 + F32 | MIT |
| `Granite-Speech-5.0-470M-TurboCTC-GGUF` | `granite5asr` | Q8 | Apache-2.0 |
| `HeartMuLa-GGUF` | `heartmula` | F16 + Q8 | Apache-2.0 |
| `HTDemucs-GGUF` | `htdemucs` | F16 + Q8 | MIT |
| `HTDemucs-6stems-GGUF` | `htdemucs_6stems` | F16 + Q8 | MIT |
| `Higgs-Audio-v3-STT-GGUF` | `higgs_audio_stt` | F16 + Q8 | Apache-2.0 |
| `Higgs-Audio-v3-TTS-4B-GGUF` | `higgs_audio_tts` | BF16 + Q8 | [Boson Higgs TTS 3 Research and Non-Commercial License](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE) |
| `Hviske-v5.3-GGUF` | `hviske_asr` | Q8 | CC-BY-NC-4.0 |
| `IndexTTS2-GGUF` | `index_tts2` | original + F16 + Q8 | [bilibili Model Use License](https://huggingface.co/IndexTeam/IndexTTS-2.5/blob/main/LICENSE) |
| `IndexTTS2.5-GGUF` | `index_tts2` | original + F16 + Q8 | [bilibili Model Use License](https://huggingface.co/IndexTeam/IndexTTS-2.5/blob/main/LICENSE) |
| `Inflect-Micro-v2-GGUF` | `inflect_v2` | original | Apache-2.0 |
| `Irodori-TTS-500M-v3-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `Irodori-TTS-600M-v3-VoiceDesign-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `Irodori-TTS-v4-Small-GGUF` | `irodori_tts` | F16 + Q8 | MIT |
| `KittenTTS-GGUF` | `kitten_tts` | original | Apache-2.0 |
| `Kokoro-82M-GGUF` | `kokoro_tts` | BF16 + Q8 | Apache-2.0 |
| `Kroko-ASR-GGUF` | `kroko_asr` | Q8 | CC-BY-SA |
| `KugelAudio-0-Open-GGUF` | `kugelaudio` | BF16 + Q8 + Q4_K | MIT |
| `MMS-Forced-Aligner-GGUF` | `mms_forced_aligner` | F16 | CC-BY-NC-4.0 |
| `MOSS-TTS-Local-v1.5-GGUF` | `moss_tts_local` | BF16 + Q8 | Apache-2.0 |
| `MOSS-TTS-Nano-100M-GGUF` | `moss_tts_nano` | BF16 + Q8 | Apache-2.0 |
| `MOSS-Transcribe-Diarize-GGUF` | `moss_transcribe_diarize` | BF16 + Q8 + Q4_K | Apache-2.0 |
| `MOSS-VoiceGenerator-GGUF` | `moss_voicegen` | BF16 + F16 codec decode | Apache-2.0 |
| `MagpieTTS-Multilingual-357M-GGUF` | `magpie_tts` | original | [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/) |
| `Maya1-GGUF` | `maya1` | original + Q8 | Apache-2.0 (Maya1); MIT (SNAC) |
| `MeanVC2-GGUF` | `meanvc2` | F32 + Q4_K | Apache-2.0 |
| `Mel-Band-RoFormer-GGUF` | `mel_band_roformer` | F16 + Q8 | MIT |
| `MiDashengLM-Gen-GGUF` | `midashenglm_gen` | F32 + Q8 | Apache-2.0 |
| `MiniMax-H3-Q4-GGUF` | `minimax_h3` | Q4_K + INT8 DiT option | [MiniMax H3 Community License](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE) |
| `MioCodec-25Hz-44.1kHz-v2-GGUF` | `miocodec` | original + F16 + Q8 | MIT |
| `MioTTS-1.7B-GGUF` | `miotts` | original + BF16 + Q8 | Apache-2.0 |
| `Moonshine-Streaming-GGUF` | `moonshine_asr` | Q8 | MIT |
| `MuScriptor-Small-GGUF` | `muscriptor` | F32 | CC-BY-NC-4.0 |
| `Nemotron-3.5-ASR-Streaming-0.6B-GGUF` | `nemotron_asr` | F16 + Q8 | [OpenMDW-1.1](https://openmdw.ai/license/1-1/) |
| `NeuTTS-2E-GGUF` | `neutts` | original | [NeuTTS Open License v1.0](https://huggingface.co/neuphonic/neutts-2e/blob/main/LICENSE) |
| `Niagara-ASR-GGUF` | `niagara_asr` | F32 | [Applied Brain Research Open License v1.1](https://www.appliedbrainresearch.com/license) |
| `OWSM-GGUF` | `owsm` | F32 + Q8 + Q4_K (Small/Medium) | CC-BY-4.0 |
| `OWSM-CTC-GGUF` | `owsm_ctc` | F32 + Q8 | CC-BY-4.0 |
| `OmniVoice-GGUF` | `omnivoice` | BF16 + F16 + Q8 | [CC-BY-NC](https://huggingface.co/k2-fsa/OmniVoice#license) |
| `Parakeet-TDT-0.6B-v3-GGUF` | `parakeet_tdt` | F16 + Q8 | CC-BY-4.0 |
| `PersonaPlex-GGUF` | `personaplex` | Q4_K + Q8 | [NVIDIA Open Model License](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-open-model-license/) |
| `Piper-TTS-GGUF` | `piper_tts` | original | MIT |
| `PocketTTS-GGUF` | `pocket_tts` | BF16 + Q8 | CC-BY-4.0 |
| `PulseVAD-GGUF` | `pulsevad` | F32 | MIT |
| `Qwen3-ASR-0.6B-GGUF` | `qwen3_asr` | F16 + Q8 | Apache-2.0 |
| `Qwen3-ASR-1.7B-GGUF` | `qwen3_asr` | F16 + Q8 | Apache-2.0 |
| `Qwen3-ForcedAligner-0.6B-GGUF` | `qwen3_forced_aligner` | F16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-0.6B-Base-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-Base-GGUF` | `qwen3_tts` | original + BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-CustomVoice-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `Qwen3-TTS-12Hz-1.7B-VoiceDesign-GGUF` | `qwen3_tts` | BF16 + Q8 | Apache-2.0 |
| `RVC-GGUF` | `rvc` | F16 | MIT |
| `Samsone-GGUF` | `samsone` | BF16 + Q8 | Not stated |
| `SeedVC-MLX-GGUF` | `seed_vc` | original + F16 + Q8 | GPL-3.0 |
| `Sidon-GGUF` | `sidon` | F32 | MIT |
| `Smart-Turn-v3-GGUF` | `smart_turn` | F32 | BSD-2-Clause |
| `Sortformer-Diar-4spk-v1-GGUF` | `sortformer_diar` | F16 + Q8 | CC-BY-NC-4.0 |
| `Stable-Audio-3-Medium-GGUF` | `stable_audio` | F16 + Q8 | [Stability AI Community License](https://huggingface.co/stabilityai/stable-audio-3-small-sfx/blob/main/LICENSE.md) |
| `Stable-Audio-3-Small-Music-GGUF` | `stable_audio` | F16 + Q8 | [Stability AI Community License](https://huggingface.co/stabilityai/stable-audio-3-small-sfx/blob/main/LICENSE.md) |
| `Stable-Audio-3-Small-SFX-GGUF` | `stable_audio` | F16 + Q8 | [Stability AI Community License](https://huggingface.co/stabilityai/stable-audio-3-small-sfx/blob/main/LICENSE.md) |
| `Supertonic-3-GGUF` | `supertonic` | original + F16 + Q8 | [BigScience OpenRAIL-M](https://huggingface.co/Supertone/supertonic-3/blob/main/LICENSE) |
| `Tone-Color-VC-GGUF` | `tone_color_vc` | F32 + F16 | MIT |
| `UniverSR-GGUF` | `universr` | original | CC-BY-4.0 |
| `Vevo2-GGUF` | `vevo2` | original + F16 + Q8 | CC-BY-NC-ND-4.0 |
| `VibeVoice-1.5B-GGUF` | `vibevoice` | BF16 + Q8 + Q4 | MIT |
| `VibeVoice-ASR-GGUF` | `vibevoice_asr` | F16 + Q8 | MIT |
| `VoxCPM1-GGUF` | `voxcpm1` | Q8 + F16 AudioVAE | Apache-2.0 |
| `VoxCPM2-GGUF` | `voxcpm2` | original + BF16 + Q8 | Apache-2.0 |
| `Voxtral-Mini-4B-Realtime-2602-GGUF` | `voxtral_realtime` | BF16 + Q8 + Q4_K | Apache-2.0 |

## Usage

Pass a GGUF file directly as `--model`:

```bash
audiocpp_cli --task tts --family supertonic --model Supertonic-3-GGUF/supertonic-3-orig.gguf --backend cuda --language en --text "Hello." --voice-id M1 --out out.wav
```

For ASR:

```bash
audiocpp_cli --task asr --family qwen3_asr --model Qwen3-ASR-0.6B-GGUF/qwen3-asr-0.6b-f16.gguf --backend cuda --audio speech.wav --text "" --text-out transcript.txt
```

## License

Each GGUF file is a converted form of its original model. Use and redistribution are governed by the corresponding original model license listed above. Please review the original model card and license terms before using or redistributing any converted weights.
