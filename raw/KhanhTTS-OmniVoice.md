---
license: apache-2.0
language:
- vi
- en
base_model:
- k2-fsa/OmniVoice
pipeline_tag: text-to-speech
---
# KhanhTTS 🗣️🔥

**KhanhTTS** là mô hình Text-to-Speech (TTS) dựa trên **OmniVoice**, được fine-tune để tổng hợp giọng nói **tiếng Việt và tiếng Anh**, hỗ trợ **voice cloning**.

## 🧠 Thông tin huấn luyện

- **Base model**: k2-fsa/OmniVoice  
- **Dataset**: ~1500 giờ audio tiếng **Việt + Anh**
- **Steps**: ~500.000
- **Mục tiêu**:
  - Phát âm tiếng Việt + Anh tự nhiên
  - Voice cloning ổn định với reference ngắn

---

## ☕ Ủng hộ dự án này
Việc huấn luyện các mô hình TTS chất lượng cao đòi hỏi tài nguyên GPU đáng kể. Nếu bạn thấy mô hình này hữu ích, vui lòng xem xét hỗ trợ quá trình phát triển: 

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-Support-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/khanh20017n)

<img src="https://huggingface.co/kjanh/ViVoxCPM-1.5/resolve/main/asserts/aa8d6020dd54530a0a45.jpg" width="100"/>

Mọi sự ủng hộ của các bạn là niềm động lực giúp mình phát triển các mô hình tốt hơn trong tương lai ❤️


---

## 🦜 Sample

**Reference Voice (Speaker Example):**  
<audio controls src="https://huggingface.co/kjanh/ViVoxCPM-1.5/resolve/main/asserts/ref_voice.wav"></audio>

**Input Text:**  

> Đêm đó, anh xoá số cô khỏi danh bạ.  
> Nhưng khi màn hình tối đi, anh vẫn nhớ rất rõ… số ấy nằm ở đâu trong tim mình.
>
> Ngoài cửa sổ, gió thổi khẽ.  
> Có những thứ đã rời đi rồi,  
> nhưng cảm giác thì ở lại lâu hơn ta tưởng.

**Generated Output (Cloned Voice):**  
<audio controls src="https://huggingface.co/kjanh/ViVoxCPM-1.5/resolve/main/asserts/demo_clone .wav"></audio>


## 🚀 Cài đặt & chạy inference

### 1. Cài đặt môi trường

```bash
pip install omnivoice
```

### 2. Load model & Inference

```python
from omnivoice import OmniVoice
import soundfile as sf
import torch

# Load the model
model = OmniVoice.from_pretrained(
    "kjanh/KhanhTTS-OmniVoice",
    device_map="cuda:0",
    dtype=torch.float16
)
```
```python
audio = model.generate(
    text="Xin chào các bạn.",
    # ref_audio="refvoice.wav",
    # ref_text="có người từng nói với cô, đó là hơi thở của mùa đông, hơi thở của đất trời, hơi thở của tình yêu.",
) # audio is a list of `np.ndarray` with shape (T,) at 24 kHz.

sf.write("out.wav", audio[0], 24000)
```




## ⚠️ Miễn trừ trách nhiệm & Khuyến cáo sử dụng (TTS)

Mô hình Text-to-Speech (TTS) này được cung cấp chỉ nhằm phục vụ mục đích nghiên cứu, thử nghiệm và phát triển công nghệ. Mọi nội dung âm thanh do mô hình tạo ra không phản ánh, đại diện hay ngụ ý giọng nói, danh tính, quan điểm hoặc sự chấp thuận của bất kỳ cá nhân hay tổ chức có thật nào. Tác giả và các bên liên quan không chịu bất kỳ trách nhiệm pháp lý nào đối với các hành vi sử dụng sai mục đích, vi phạm pháp luật, xâm phạm quyền riêng tư, quyền nhân thân, quyền sở hữu trí tuệ, hoặc các thiệt hại trực tiếp hay gián tiếp phát sinh từ việc sử dụng mô hình này.

Người dùng chịu hoàn toàn trách nhiệm pháp lý đối với việc triển khai, phân phối và sử dụng mô hình. Nghiêm cấm sử dụng mô hình cho các hành vi mạo danh, sao chép hoặc mô phỏng giọng nói cá nhân khi chưa có sự đồng ý hợp pháp, tạo nội dung gây hiểu lầm, lừa đảo, thao túng dư luận hoặc bất kỳ hành vi nào trái với quy định pháp luật hiện hành. Khi sử dụng hoặc chia sẻ âm thanh được tạo ra, khuyến nghị bắt buộc phải công bố rõ ràng rằng nội dung là âm thanh được tạo bởi trí tuệ nhân tạo (AI), đồng thời tuân thủ đầy đủ các quy định pháp luật, chính sách nền tảng và chuẩn mực đạo đức có liên quan.

Mẫu mô hình này được phát hành chỉ cho mục đích nghiên cứu và phát triển. Chúng tôi không khuyến khích việc sử dụng trong môi trường sản xuất hoặc cho mục đích thương mại nếu chưa trải qua quy trình thử nghiệm, đánh giá rủi ro và kiểm định an toàn một cách nghiêm ngặt. Vui lòng sử dụng mô hình một cách có trách nhiệm.

## 📚 Trích dẫn (Citation)

Nếu bạn sử dụng mô hình này hoặc dựa trên OmniVoice cho nghiên cứu/sản phẩm, vui lòng trích dẫn bài OmniVoice gốc:

```bibtex
@article{zhu2026omnivoice,
      title={OmniVoice: Towards Omnilingual Zero-Shot Text-to-Speech with Diffusion Language Models},
      author={Zhu, Han and Ye, Lingxuan and Kang, Wei and Yao, Zengwei and Guo, Liyong and Kuang, Fangjun and Han, Zhifeng and Zhuang, Weiji and Lin, Long and Povey, Daniel},
      journal={arXiv preprint arXiv:2604.00688},
      year={2026}
}