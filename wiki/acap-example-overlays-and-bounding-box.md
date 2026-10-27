---
type: Concept
title: "ACAP examples: drawing on video with bounding-box, axoverlay, axoverlay2 and Skia"
description: "How the four graphics examples draw onto Axis video streams: portable Bounding Box API, legacy Axoverlay with Cairo, Axoverlay 2 with a Cairo surface, and Axoverlay 2 with GPU Skia over dma-buf, including manifest resources, constants and defects."
tags: [edge-ai, axis, acap, examples, overlay, graphics, skia]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T20:00:00Z }
stale_after: 2027-04-30
sources:
  - id: native-examples
    resource: ../raw/acap-native-sdk-examples/README.md
    scope: ../raw/acap-native-sdk-examples/
    kind: code
    revision: "12.11.0-7-g3025a4e (3025a4e9db74f1af5bb878d4efc82ac0e300a792, commit date 2026-09-01)"
    title: "AxisCommunications/acap-native-sdk-examples (git submodule)"
---

# ACAP examples: drawing on video with bounding-box, axoverlay, axoverlay2 and Skia

The repository offers four ways to burn graphics into a camera stream: the portable **Bounding Box** API (`bounding-box`), the legacy **Axoverlay** API (`axoverlay`), and the newer **Axoverlay 2** API in a CPU-rendered (`axoverlay2`, Cairo) and a GPU-rendered (`axoverlay2-skia`, Skia over EGL/GLES) form.[^native-examples] They differ in portability, manifest resource model and who renders the pixels.

| Example | API and language | Renderer | Manifest resource model |
| --- | --- | --- | --- |
| `bounding-box` | `bbox` (C) | the platform | D-Bus `com.axis.Graphics2.*`, `com.axis.Overlay2.*`; `video` group |
| `axoverlay` | `axoverlay` legacy (C) | Cairo image backend | D-Bus `com.axis.Graphics2.*`, `com.axis.Overlay2.*` |
| `axoverlay2` | `axoverlay2` (C) | Cairo into an ARGB32 buffer | `resources.overlay {enabled, required}` |
| `axoverlay2-skia` | `axoverlay2` (C++20) | Skia Ganesh on GLES3, `dma_buf` import | `resources.overlay` plus `gpu` group |

## bounding-box

Portable burnt-in boxes that work independent of the chip, in contrast to the ARTPEC-specific axoverlay (README). The code (`bounding-box/app/bounding_box_example.c`) loops until SIGINT/SIGTERM through four phases: single channel with scene-normalized coordinates, clear, single channel with frame-normalized coordinates, then a two-channel batch of 32 boxes. Calls: `bbox_view_new`, `bbox_new`, `bbox_coordinates_scene_normalized`/`_frame_normalized`, `bbox_rectangle`, `bbox_quad`, `bbox_move_to`/`bbox_line_to`/`bbox_draw_path`, `bbox_color_from_rgb`, `bbox_style_outline`/`_corners`, `bbox_thickness_*`, `bbox_video_output`, `bbox_clear`, `bbox_commit`. Each phase shows for 5 seconds; box spacing assumes 1920x1080. The README says "three states" and "3 boxes" but the loop has four phases and draws a rectangle, a quadrilateral and a path.[^native-examples] The same API draws the detection boxes in the [Larod object-detection examples](acap-example-larod-object-detection.md).

## axoverlay (legacy)

- Uses `gio-2.0 glib-2.0 cairo` plus `-laxoverlay`. `main` sets `XDG_CACHE_HOME` to `/usr/local/packages/axoverlay/localdata` for fontconfig, checks `axoverlay_is_backend_supported(AXOVERLAY_CAIRO_IMAGE_BACKEND)`, calls `axoverlay_init`, defines a four-colour palette, creates one `4BIT_PALETTE` overlay (two coloured bands) and one `ARGB32` overlay ("Countdown N" text, 1 Hz timer), and tears both down on exit.
- Position type `AXOVERLAY_CUSTOM_NORMALIZED`, anchor centre, `scale_to_stream = FALSE`; `adjustment_cb` sizes the overlay from the stream (swapping width and height at 90/270 degrees).
- README limits it to ARTPEC-9/8/7/6 and says ARTPEC-6 cannot mix colour spaces.[^native-examples]
- **Defects:** README log samples are stale against the code's log lines; `draw_text` computes extents it never uses; some error paths return without destroying the first overlay.

## axoverlay2 (Cairo)

- Starts with `axo_start`, finds streams through the VDO "stream 0" event channel (`vdo_stream_get(0)` with an `overlay` filter and an event fd watched by a GLib `GIOChannel`), and creates one overlay per stream on `VDO_STREAM_EVENT_EXISTING`/`_CREATED`, removing it on `_CLOSED`.
- Overlay size is `MIN(w,h)/8`, halved with `axo_props_set_upscale_x2` above 4,000,000 pixels; for 3840x2160 that is 135x135 used inside a 136x136 aligned buffer. A 30 fps timer (`1000000/30` µs) drives `axo_get_buffer` → Cairo render → `memcpy` into the buffer → `axo_submit_buffer`; `AXO_ERR_NO_STREAM` and `AXO_ERR_WAIT` are tolerated.
- Rendering draws circles and an arc with colours `sin²` / `cos²` of the animation angle on a persistent Cairo surface (never directly into device memory).
- **Defect:** the README links `../LICENSE`, which does not exist at the example root (the licence is `app/LICENSE`, MIT).[^native-examples]

## axoverlay2-skia (GPU)

- Same stream-event and timer structure, but rendering is Skia (`chrome/m137`) on an EGL pbuffer context with GLES3. The overlay format comes from `axo_suggest_detailed_format(ARGB32, COMPRESSED|GPU)`, sizes are rounded to 16x16, and `axo_props_set_manual_dma_sync(true)` skips CPU cache maintenance. Each buffer's `dma_buf` fd becomes an `EGLImage` → GL texture → `SkSurface`, cached per buffer id; every frame ends with `flushAndSubmit(GrSyncCpu::kYes)`. Helper wrappers are in `app/axo2_wrappers.hh` and `app/gpu_error.hh`.
- **Build:** the Dockerfile (`ARCH=aarch64` default) installs `generate-ninja ninja-build git`, clones Skia at `SKIA_VERSION=chrome/m137`, syncs dependencies, runs `gn gen` with Ganesh and EGL/GL enabled and PDF/SVG/fontconfig/freetype/harfbuzz/icu/x11 disabled, and builds `libskia.a`; the app links it with `-std=c++20 -Werror`. Only the Skia branch is pinned, so builds are not bit-reproducible.
- **Defects:** the README lists `Axoverlay2_example_Skia_application_1_0_0_*` and, later, `axoverlay2_skia_1_0_0_*` as package names; the `dma_buf` fd is never closed and surface cache entries are only freed at teardown; the aligned-size call result is unchecked.[^native-examples]

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md); resource models in [shared conventions](acap-examples-build-and-manifest-conventions.md).
- **Uses** Overlay and Bounding Box APIs catalogued in [Native SDK API catalog](acap-native-sdk-api-catalog.md).
- **Compare** `vdo-opencl-filtering` in [VDO capture and OpenCL](acap-example-vdo-video-capture-and-opencl.md) for GPU use without overlays.

[^native-examples]: `bounding-box/app/bounding_box_example.c::main, example_single_channel, example_multiple_channels`, `bounding-box/README.md`; `axoverlay/app/axoverlay.c::main, adjustment_cb, render_overlay_cb`, `axoverlay/README.md` (limitations); `axoverlay2/app/axoverlay2.c::create_overlay, process_next_frame, render_frame`, `axoverlay2/README.md`; `axoverlay2-skia/app/axoverlay2_skia.cc::create_overlay, create_render_surface`, `axoverlay2-skia/Dockerfile`, `axoverlay2-skia/README.md`; `*/app/manifest.json`; `*/app/LICENSE`.
