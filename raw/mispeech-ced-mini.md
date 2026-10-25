---
license: apache-2.0
datasets:
- AudioSet
metrics:
- mAP
pipeline_tag: audio-classification
---

# CED-Mini Model
CED are simple ViT-Transformer-based models for audio tagging, achieving **sota** performance on Audioset.


| Model | Parameters (M) | AS-20K (mAP) | AS-2M (mAP) |
|------|-------|-------|-------|
| CED-Tiny | 5.5   | 36.5  | 48.1  |
| CED-Mini | 9.6    | 38.5  | 49.0  |
| CED-Small| 22    | 41.6  | 49.6  |
| CED-Base | 86    | 44.0  | 50.0  |


Notable differences from other available models include:
1. Simplification for finetuning: Batchnormalization of Mel-Spectrograms. During finetuning one does not need to first compute mean/variance over the dataset, which is common for AST.
1. Support for variable length inputs. Most other models use a static time-frequency position embedding, which hinders the model's generalization to segments shorter than 10s. Many previous transformers simply pad their input to 10s in order to avoid the performance impact, which in turn slows down training/inference drastically.
1. Training/Inference speedup: 64-dimensional mel-filterbanks and 16x16 patches without overlap, leading to 248 patches from a 10s spectrogram. In comparison, AST uses 128 mel-filterbanks with 16x16 (10x10 overlap) convolution, leading to 1212 patches during training/inference. CED-Tiny runs on a common CPU as fast as a comparable MobileNetV3.
1. Performance: CED with 10M parameters outperforms the majority of previous approaches (~80M).

### Model Sources
- **Repository:** https://github.com/RicherMans/CED
- **Paper:** [CED: Consistent ensemble distillation for audio tagging](https://arxiv.org/abs/2308.11957)
- **Demo:** https://huggingface.co/spaces/mispeech/ced-base

## Inference
```python
>>> from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

>>> model_name = "mispeech/ced-mini"
>>> feature_extractor = AutoFeatureExtractor.from_pretrained(model_name, trust_remote_code=True)
>>> model = AutoModelForAudioClassification.from_pretrained(model_name, trust_remote_code=True)

>>> import torchaudio
>>> audio, sampling_rate = torchaudio.load("/path-to/JeD5V5aaaoI_931_932.wav")
>>> assert sampling_rate == 16000
>>> inputs = feature_extractor(audio, sampling_rate=sampling_rate, return_tensors="pt")

>>> import torch
>>> with torch.no_grad():
...     logits = model(**inputs).logits

>>> predicted_class_id = torch.argmax(logits, dim=-1).item()
>>> model.config.id2label[predicted_class_id]
'Finger snapping'
```

## Inference (Onnx)
```python
>>> from optimum.onnxruntime import ORTModelForAudioClassification

>>> model_name = "mispeech/ced-mini"
>>> model = ORTModelForAudioClassification.from_pretrained(model_name, trust_remote_code=True)

>>> import torchaudio
>>> audio, sampling_rate = torchaudio.load("/path-to/JeD5V5aaaoI_931_932.wav")
>>> assert sampling_rate == 16000
>>> input_name = model.session.get_inputs()[0].name
>>> output = model(**{input_name: torch.randn(1, 16000)})
>>> logits = output.logits.squeeze()
>>> for idx in logits.argsort()[-2:][::-1]:
>>>   print(f"{model.config.id2label[idx]}: {logits[idx]:.4f}")
'Finger snapping: 0.9155'
'Slap: 0.0567'
```

## Fine-tuning
[`example_finetune_esc50.ipynb`](https://github.com/jimbozhang/hf_transformers_custom_model_ced/blob/main/example_finetune_esc50.ipynb) demonstrates how to train a linear head on the ESC-50 dataset with the CED encoder frozen.
