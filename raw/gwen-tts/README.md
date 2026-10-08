# Gwen-TTS: Natural Vietnamese Voice Cloning

[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20HuggingFace-Model-yellow)](https://huggingface.co/g-group-ai-lab/gwen-tts-0.6B)
[![Demo](https://img.shields.io/badge/Demo-g--voice.g--ailab.com-blue)](https://g-voice.g-ailab.com/tts)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Gwen-TTS** is a Vietnamese text-to-speech model with natural voice cloning capability.

**Key highlights:**
- Natural and expressive Vietnamese voice cloning
- Clone any voice with just a few seconds of reference audio
- Finetuned from [Qwen3-TTS-0.6B](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base) on ~1,000 hours of Vietnamese audio data crawled from TikTok

## Demo

Try it out: **[https://g-voice.g-ailab.com/tts](https://g-voice.g-ailab.com/tts)**

> The demo has been integrated with TTS text normalization and serving.

## Installation

> Tested environment: Python 3.11, CUDA 12.4, NVIDIA driver ≥ 550.54, VRAM ≥ 4 GB

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/ggroup-ai-lab/gwen-tts.git
cd gwen-tts

# Install core dependencies (torch cu124)
uv sync --python 3.11

# Install flash-attn
uv pip install setuptools && uv pip install flash-attn --no-build-isolation

# Activate the virtual environment
source .venv/bin/activate
```

## Quick Start

### Python API

> **Note:** For best quality, proactively apply **TTS text normalization** (numbers, symbols, abbreviations, etc.) and **split input into chunks** before passing to the model.


```python
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

# Load model (auto-downloads from HuggingFace)
model = Qwen3TTSModel.from_pretrained(
    "g-group-ai-lab/gwen-tts-0.6B",
    device_map="cuda:0",
    dtype=torch.bfloat16,
    attn_implementation="flash_attention_2",
)

# Recommended generation config for Gwen-TTS
generation_config = dict(
    temperature=0.3,
    top_k=20,
    top_p=0.9,
    max_new_tokens=4096,
    repetition_penalty=2.0,
    subtalker_do_sample=True,
    subtalker_temperature=0.1,
    subtalker_top_k=20,
    subtalker_top_p=1.0,
)

# Voice cloning
wavs, sr = model.generate_voice_clone(
    text="<your text to synthesize>",
    language="Vietnamese",
    ref_audio="<path/to/reference.wav>",
    ref_text="<transcript of the reference audio>",
    **generation_config,
)

sf.write("output.wav", wavs[0], sr)
```

### CLI

```bash
# Using a built-in reference speaker
python inference.py --text "Your text here" --speaker yen_nhi

# Using a custom reference audio
python inference.py \
    --text "Your text here" \
    --ref_audio path/to/your_voice.wav \
    --ref_text "transcript of the reference audio"

# List available built-in speakers
python inference.py --list_speakers
```

## Voice Samples

Each speaker shows the **reference audio** (voice input) and the **generated inference audio** (output).

<!-- ───────────────── Yến Nhi ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Yến Nhi &nbsp;<code>yen_nhi</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/yen_nhi.wav">play</a><br>
<audio controls src="data/ref_audio/yen_nhi.wav" style="width:100%"></audio><br>
<i>sao lại không liên quan. các anh lấy vợ rồi các anh cứ đội chị lên đầu làm nóc nhà ấy, suốt ngày hỏi ý kiến các chị thì làm sao mà ra vấn đề được cho em đúng không.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/yen_nhi.wav">play</a><br>
<audio controls src="data/infer-audio/yen_nhi.wav" style="width:100%"></audio><br>
<i>Dạ chào anh, em gọi trực tiếp từ bộ phận phê duyệt hồ sơ thẻ tín dụng. Hiện tại hồ sơ của mình đang nằm trong danh sách ưu tiên nhận hạn mức lên đến hai trăm triệu đồng, kèm ưu đãi miễn phí thường niên trọn đời. Không biết mình có tiện trao đổi hai phút để em hướng dẫn nhận thẻ ngay không ạ?</i>
</td>
</tr>
</table>

<!-- ───────────────── Mỹ Vân ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Mỹ Vân &nbsp;<code>my_van</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/my_van.wav">play</a><br>
<audio controls src="data/ref_audio/my_van.wav" style="width:100%"></audio><br>
<i>bạn thân mến, chúng ta sẽ đến với một bài tập tiếp theo để giúp cho các bạn có hơi thở dài, sâu và đầy đặn hơn.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/my_van.wav">play</a><br>
<audio controls src="data/infer-audio/my_van.wav" style="width:100%"></audio><br>
<i>Dạ chào anh, em gọi trực tiếp từ bộ phận phê duyệt hồ sơ thẻ tín dụng. Hiện tại hồ sơ của mình đang nằm trong danh sách ưu tiên nhận hạn mức lên đến hai trăm triệu đồng, kèm ưu đãi miễn phí thường niên trọn đời. Không biết mình có tiện trao đổi hai phút để em hướng dẫn nhận thẻ ngay không ạ?</i>
</td>
</tr>
</table>

<!-- ───────────────── Ái Vy ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Ái Vy &nbsp;<code>ai_vy</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/ai_vy.wav">play</a><br>
<audio controls src="data/ref_audio/ai_vy.wav" style="width:100%"></audio><br>
<i>việt nam đang kiêu hãnh bước vào kỷ nguyên vươn mình rực rỡ với khát vọng mãnh liệt, trí tuệ đổi mới và tinh thần đoàn kết đất nước, tự tin bứt phá, kiến tạo một tương lai thịnh vượng và vươn tầm quốc tế.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/ai_vy.wav">play</a><br>
<audio controls src="data/infer-audio/ai_vy.wav" style="width:100%"></audio><br>
<i>Dạ chào anh, em gọi trực tiếp từ bộ phận phê duyệt hồ sơ thẻ tín dụng. Hiện tại hồ sơ của mình đang nằm trong danh sách ưu tiên nhận hạn mức lên đến hai trăm triệu đồng, kèm ưu đãi miễn phí thường niên trọn đời. Không biết mình có tiện trao đổi hai phút để em hướng dẫn nhận thẻ ngay không ạ?</i>
</td>
</tr>
</table>

<!-- ───────────────── An Nhi ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>An Nhi &nbsp;<code>an_nhi</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/an_nhi.wav">play</a><br>
<audio controls src="data/ref_audio/an_nhi.wav" style="width:100%"></audio><br>
<i>việt nam đang kiêu hãnh bước vào kỷ nguyên vươn mình rực rỡ với khát vọng mãnh liệt, trí tuệ đổi mới và tinh thần đoàn kết đất nước, tự tin bứt phá, kiến tạo một tương lai thịnh vượng và vươn tầm quốc tế.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/an_nhi.wav">play</a><br>
<audio controls src="data/infer-audio/an_nhi.wav" style="width:100%"></audio><br>
<i>Thưa quý vị, sáng nay tại TP.HCM, Diễn đàn Kinh tế số đã chính thức khai mạc. Phát biểu tại hội nghị, các chuyên gia nhấn mạnh việc ứng dụng Trí tuệ nhân tạo sẽ là đòn bẩy chiến lược giúp doanh nghiệp tối ưu hóa quy trình sản xuất và nâng cao năng lực cạnh tranh trong kỷ nguyên công nghệ bốn chấm không.</i>
</td>
</tr>
</table>

<!-- ───────────────── Diệu Linh ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Diệu Linh &nbsp;<code>dieu_linh</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/dieu_linh.wav">play</a><br>
<audio controls src="data/ref_audio/dieu_linh.wav" style="width:100%"></audio><br>
<i>việt nam đang kiêu hãnh bước vào một kỷ nguyên vươn mình rực rỡ với khát vọng mãnh liệt, trí tuệ đổi mới và tinh thần đoàn kết.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/dieu_linh.wav">play</a><br>
<audio controls src="data/infer-audio/dieu_linh.wav" style="width:100%"></audio><br>
<i>Thưa quý vị, sáng nay tại TP.HCM, Diễn đàn Kinh tế số đã chính thức khai mạc. Phát biểu tại hội nghị, các chuyên gia nhấn mạnh việc ứng dụng Trí tuệ nhân tạo sẽ là đòn bẩy chiến lược giúp doanh nghiệp tối ưu hóa quy trình sản xuất và nâng cao năng lực cạnh tranh trong kỷ nguyên công nghệ bốn chấm không.</i>
</td>
</tr>
</table>

<!-- ───────────────── Khánh Toàn ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Khánh Toàn &nbsp;<code>khanh_toan</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/khanh_toan.wav">play</a><br>
<audio controls src="data/ref_audio/khanh_toan.wav" style="width:100%"></audio><br>
<i>việt nam đang kiêu hãnh bước vào kỷ nguyên vươn mình rực rỡ với khát vọng mãnh liệt, trí tuệ đổi mới, tinh thần đoàn kết.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/khanh_toan.wav">play</a><br>
<audio controls src="data/infer-audio/khanh_toan.wav" style="width:100%"></audio><br>
<i>Thưa quý vị, sáng nay tại TP.HCM, Diễn đàn Kinh tế số đã chính thức khai mạc. Phát biểu tại hội nghị, các chuyên gia nhấn mạnh việc ứng dụng Trí tuệ nhân tạo sẽ là đòn bẩy chiến lược giúp doanh nghiệp tối ưu hóa quy trình sản xuất và nâng cao năng lực cạnh tranh trong kỷ nguyên công nghệ bốn chấm không.</i>
</td>
</tr>
</table>

<!-- ───────────────── Trần Lâm ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>Trần Lâm &nbsp;<code>tran_lam</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/tran_lam.wav">play</a><br>
<audio controls src="data/ref_audio/tran_lam.wav" style="width:100%"></audio><br>
<i>trí tuệ đổi mới và tinh thần đoàn kết, đất nước tự tin bứt phá, kiến tạo một tương lai thịnh vượng và vươn tầm quốc tế.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/tran_lam.wav">play</a><br>
<audio controls src="data/infer-audio/tran_lam.wav" style="width:100%"></audio><br>
<i>Trên tay mình lúc này là siêu phẩm mới nhất trong năm nay. Cảm giác cầm nắm cực kỳ đầm tay với khung viền titan sang trọng. Điểm ăn tiền nhất chính là cụm camera được nâng cấp mạnh mẽ, cho khả năng quay phim chuẩn điện ảnh ngay cả trong điều kiện thiếu sáng. Một thiết bị thực sự đáng đồng tiền bát gạo!</i>
</td>
</tr>
</table>

<!-- ───────────────── NSND Hà Phương ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>NSND Hà Phương &nbsp;<code>nsnd_ha_phuong</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/nsnd_ha_phuong.wav">play</a><br>
<audio controls src="data/ref_audio/nsnd_ha_phuong.wav" style="width:100%"></audio><br>
<i>đây là những lời cuối cùng của típ rót người sáng lập ra ai phôn áp bồ chấn động cả thế giới.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/nsnd_ha_phuong.wav">play</a><br>
<audio controls src="data/infer-audio/nsnd_ha_phuong.wav" style="width:100%"></audio><br>
<i>Khi thành phố đã chìm sâu vào giấc ngủ, chỉ còn tiếng gió khẽ lay những tán lá bên cửa sổ. Hãy gạt bỏ mọi lo âu của ngày dài, thả mình vào sự tĩnh lặng tuyệt đối. Trong giấc mơ đêm nay, bạn sẽ thấy mình đi lạc vào một cánh rừng nguyên sơ, nơi chỉ có tiếng suối róc rách và hương hoa cỏ dịu nhẹ...</i>
</td>
</tr>
</table>

<!-- ───────────────── NSND Kim Cúc ───────────────── -->
<table>
<tr>
<td colspan="2"><h3>NSND Kim Cúc &nbsp;<code>nsnd_kim_cuc</code></h3></td>
</tr>
<tr>
<td width="50%">
<b>Reference</b>&ensp;<a href="data/ref_audio/nsnd_kim_cuc.wav">play</a><br>
<audio controls src="data/ref_audio/nsnd_kim_cuc.wav" style="width:100%"></audio><br>
<i>đi họp người ta đả thông mãi rồi. lão dòng tai nghe, rồi lão rủm cả người. lão làm như vô tình kéo ghế xích lại đám đông.</i>
</td>
<td width="50%">
<b>Inference</b>&ensp;<a href="data/infer-audio/nsnd_kim_cuc.wav">play</a><br>
<audio controls src="data/infer-audio/nsnd_kim_cuc.wav" style="width:100%"></audio><br>
<i>Khi thành phố đã chìm sâu vào giấc ngủ, chỉ còn tiếng gió khẽ lay những tán lá bên cửa sổ. Hãy gạt bỏ mọi lo âu của ngày dài, thả mình vào sự tĩnh lặng tuyệt đối. Trong giấc mơ đêm nay, bạn sẽ thấy mình đi lạc vào một cánh rừng nguyên sơ, nơi chỉ có tiếng suối róc rách và hương hoa cỏ dịu nhẹ...</i>
</td>
</tr>
</table>

## Supported Languages

Vietnamese (primary), Chinese, English, Japanese, Korean, French, German, Italian, Portuguese, Russian, Spanish.

> **Note:** This model is optimized for Vietnamese. Performance on other languages may differ from the base Qwen3-TTS model.

## Citation

```bibtex
@misc{gwen-tts,
    title={Gwen-TTS: Natural Vietnamese Voice Cloning},
    author={G-Group AI Lab},
    year={2026},
    url={https://github.com/ggroup-ai-lab/gwen-tts}
}
```

## License

This model is released under the [MIT License](LICENSE).

## Acknowledgments

- [Qwen Team](https://github.com/QwenLM) for the Qwen3-TTS base model
- [G-Group AI Lab](https://github.com/ggroup-ai-lab) for training and releasing this model
