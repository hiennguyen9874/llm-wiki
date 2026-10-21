---
license: cc-by-nc-nd-4.0
---
# Vietnamese Speech-to-Text (ASR) — ZipFormer-150M-CR-CTC-RNNT-6000h

## 🔍 Overview
The **Vietnamese Speech-to-Text (ASR)** model is built on the **ZipFormer architecture** — an improved variant of the Conformer — featuring with **150 million parameters** yet achieving **exceptional performance** in accuracy.  
On a RTX 3090, the model can transcribe a **12-second audio clip in just 0.3 seconds**, significantly faster than most traditional ASR systems requiring a GPU with low price.

---

## ☕ Give Me a Coffee for Training Cost

This model was trained entirely on **self-funded, personal hardware** — every GPU hour and electricity bill came out of my own pocket.  
If this work is useful to you, a small contribution helps cover the cost of the next training run and keeps future models free and open. Every coffee is hugely appreciated 🙏

<p align="center">
  <img src="qr.jpg" alt="VietQR — Give me a coffee" width="320"/>
</p>

<p align="center"><i>Scan with any VietQR / Napas 247 supported banking app</i></p>

Thank you for supporting open Vietnamese ASR! ❤️

---

## 🚀 Online Demo

You can try the model directly here:  
👉 https://huggingface.co/spaces/hynt/k2-automatic-speech-recognition-demo

---

## ⚙️ Model Architecture and Training strategy:
- **Architecture:** ZipFormer  
- **Parameters:** ~153M  
- **Language:** Vietnamese  
- **Loss Function:** CR-CTC + CTC + RNN-T Loss  
- **Framework:** PyTorch + k2
- **Training strategy**: Carefully preprocess the data, apply an augmentation strategy based on the distribution of out-of-vocabulary (OOV) tokens and refine the transcriptions using Whisper.  
- **Optimized for:** High-speed GPU with low price inference  

---

## 🧠 Training Data
The model was trained on approximately **6000 hours of high-quality Vietnamese speech** collected from various public datasets:

| Dataset |  |  |
|----------|----------|----------|
| VLSP2020 | VLSP2021 | VLSP2023-voting-pseudo-labeled |
| VLSP2023 | FPT | VIET_BUD500 |
| VietSpeech | FLEURS | VietMed_Labeled |
| Sub-GigaSpeech2-Vi | ViVoice | Sub-PhoAudioBook |

---

## 🧪 Evaluation Results

| **Dataset** | **ZipFormer-150M-6000h** | **ZipFormer-30M-6000h** | **ChunkFormer-110M-3000h** | **PhoWhisper-Large-1.5B-800h** | **VietASR-ZipFormer-68M-70.000h** |
|--------------|--------------------------|--------------------------|-----------------------------|--------------------------------|---------------------------------|
| **VLSP2020-Test-T1** | 13.50 | **12.29** | 14.09 | 13.75 | 14.45 |
| **VLSP2023-PublicTest** | **6.59** | **10.40** | 16.15 | 16.83 | 14.70 |
| **VLSP2023-PrivateTest** | **7.80** | **11.10** | 17.12 | 17.10 | 15.07 |
| **VLSP2025-PublicTest** | **6.69** | **7.97** | 15.55 | 16.14 | 13.55 |
| **VLSP2025-PrivateTest** | **6.20** | **8.10** | 16.07 | 16.31 | 13.97 |
| **GigaSpeech2-Test** | 7.10 | 7.56 | 10.35 | 10.00 | **6.88** |

> Lower is better (WER %)

---

## 🏆 Achievements
By training this model architecture **with 30M parameters** on 4,000 hours of data, I **won First Place** in the **Vietnamese Language Speech Processing (VLSP)** competition **2025**.
Comprehensive details about **training data**, **optimization strategies**, **architecture improvements**, and **evaluation methodologies** are available in the paper below:

👉 [Read the full paper on ACL](https://aclanthology.org/2025.vlsp-1.4.pdf)

---

## ⚡ Inference Speed

| **Device** | **Audio Length** | **Inference Time** |
|-------------|------------------|--------------------|
| CPU (Hugging Face Basic) | 12 seconds | **1.0 s** |
| GPU (RTX 3090) | 12 seconds | **< 0.3 s** |

---

## ⚙️ How to Run This Model

Please refer to the following guides for instructions on how to run and deploy this model:  
- **For Torch JIT Script:** [https://k2-fsa.github.io/sherpa/](https://k2-fsa.github.io/sherpa/)  
- **For ONNX:** [https://k2-fsa.github.io/sherpa/onnx/](https://k2-fsa.github.io/sherpa/onnx/)

## 💬 Summary
The **ZipFormer-150M-CR-CTC-RNNT-6000h** model demonstrates that a **strong and efficient architecture** can achieve **state-of-the-art accuracy for Vietnamese ASR**.  
It is well suited for **production environments with limited and cost-efficient GPU resources**. Making it ideal for **real-time speech recognition**, **callbots**, and **embedded speech interfaces**.

---
