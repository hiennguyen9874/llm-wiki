---
license: openrail
license_link: LICENSE
tags:
  - object-detection
  - document-layout-analysis
  - ocr
library_name: surya
---

# Surya Layout (fast)

A lightweight document **layout detection** model used by
[Surya](https://github.com/datalab-to/surya). It detects layout regions
(text, tables, figures, headers, captions, equations, etc.) on a page image and
runs on CPU or GPU.

This is the "fast" layout detector — a compact object detector that serves as a
drop-in alternative to Surya's VLM-based layout model.

➡️ **Documentation, installation, and everything else lives in the
[Surya repository](https://github.com/datalab-to/surya).**

## Usage

Install Surya:

```shell
pip install surya-ocr
```

Point the fast layout predictor at this checkpoint:

```python
from PIL import Image
from surya.fast_layout import FastLayoutPredictor

predictor = FastLayoutPredictor(checkpoint="hf://datalab-to/surya_layout2")
layout = predictor([Image.open("page.png")])

for box in layout[0].bboxes:
    print(box.label, box.bbox, box.position)  # region label, [x0,y0,x1,y1], reading-order index
```

Or make it the default so the CLI and library use it without an explicit path:

```shell
export FAST_LAYOUT_MODEL_CHECKPOINT="hf://datalab-to/surya_layout2"
```

## License

Released under the AI Pubs OpenRAIL-M license (see `LICENSE`) — the same
license as the [surya-ocr-2](https://huggingface.co/datalab-to/surya-ocr-2)
model weights.
