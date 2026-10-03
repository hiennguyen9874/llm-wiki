"""Validated single-image input for Decisions. Images stay out of the text state."""
import base64
import binascii
import io

from PIL import Image, UnidentifiedImageError

from decisions_api import ApiError

IMG_MARK = "<<IMG>>"
IMG_BLOCK = "<|vision_start|><|image_pad|><|vision_end|>"
MAX_IMAGE_BYTES = 4 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000


def image_input(body):
    """Accept base64 or a data URI; never read server paths or fetch remote URLs."""
    value = body.get("image_data")
    if value is None:
        return None
    if not isinstance(value, str) or not value:
        raise ApiError(400, "image_data must be one base64 image or image data URI")
    if value.startswith("data:"):
        header, sep, value = value.partition(",")
        if not sep or not header.startswith("data:image/") or not header.endswith(";base64"):
            raise ApiError(400, "image_data must use an image base64 data URI")
    if len(value) > 4 * ((MAX_IMAGE_BYTES + 2) // 3):
        raise ApiError(413, "image_data exceeds 4 MiB decoded")
    try:
        raw = base64.b64decode(value, validate=True)
        if len(raw) > MAX_IMAGE_BYTES:
            raise ApiError(413, "image_data exceeds 4 MiB decoded")
        with Image.open(io.BytesIO(raw)) as im:
            if im.format not in {"JPEG", "PNG", "WEBP"} or getattr(im, "n_frames", 1) != 1:
                raise ApiError(400, "image_data must be a single JPEG, PNG or WebP image")
            if im.width * im.height > MAX_IMAGE_PIXELS:
                raise ApiError(413, "image_data exceeds 12 million pixels")
            im.verify()
    except (binascii.Error, ValueError, OSError, UnidentifiedImageError, Image.DecompressionBombError) as e:
        raise ApiError(400, "image_data is not a valid base64 image") from e
    return value


def image_premise(premise):
    if premise.count(IMG_MARK) > 1 or "<|image_pad|>" in premise or "<|vision_start|>" in premise:
        raise ApiError(400, "Use at most one <<IMG>> marker in the image premise")
    return premise.replace(IMG_MARK, IMG_BLOCK) if IMG_MARK in premise else premise.rstrip() + " " + IMG_BLOCK
