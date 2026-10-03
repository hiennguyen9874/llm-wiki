"""Prime the V100 vision kernels before serving image traffic."""
import base64
import io
import math

from PIL import Image
import requests


def warmup_vision(url):
    for size in ((352, 192), (1200, 800)):
        image = Image.new("RGB", size, (160, 50, 30))
        stream = io.BytesIO()
        image.save(stream, format="PNG")
        data = base64.b64encode(stream.getvalue()).decode()
        for count in (1, 4):
            body = {"text": ["Premise: An image: <|vision_start|><|image_pad|><|vision_end|>\n"
                             f"Hypothesis: The image contains color number {j}." for j in range(count)],
                    "image_data": [data]*count}
            r = requests.post(url + "/classify", json=body, timeout=(3, 300))
            r.raise_for_status()
            rows = r.json()
            if len(rows) != count or any(len(x["embedding"]) != 3 or
                    not all(math.isfinite(v) for v in x["embedding"]) for x in rows):
                raise ValueError("Vision warmup returned invalid logits")
            print(f"vision warmup {url} size={size} batch={count}: ok", flush=True)


if __name__ == "__main__":
    import sys
    for url in sys.argv[1:]:
        warmup_vision(url.rstrip("/"))
