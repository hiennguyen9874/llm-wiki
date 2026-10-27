---
type: Concept
title: "ACAP examples: bundling libraries with using-opencv, curl-openssl and utility-libraries"
description: "How the library examples build or use third-party code in an ACAP app: OpenCV 4.10.0 cross-built with CMake and RPATH bundling, SDK-provided curl and OpenSSL with a build-time CA bundle, a custom shared library, and OpenSSL 1.1.1m plus curl 7.83.1 built from source, with defects."
tags: [edge-ai, axis, acap, examples, opencv, curl, openssl, libraries, rpath]
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

# ACAP examples: bundling libraries

Four examples show how to get a library into an ACAP package: build it in the Dockerfile under `/opt/build`, copy its shared objects into the app `lib/` directory, link with `-L./lib` and set the run-path with `-Wl,-rpath,'$$ORIGIN/lib'` so the app finds them at `/usr/local/packages/<app>/lib`; or use libraries the SDK already supplies.[^native-examples] The vendor how-to for this technique is summarized in [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md), which cites `utility-libraries` as its example source.

## using-opencv

- **Build:** installs `cmake`, fetches OpenCV `4.10.0` into `/opt/build/opencv`, installs into the SDK sysroot (`CMAKE_INSTALL_PREFIX` = `/opt/axis/acapsdk/sysroots/${ARCH}/usr`) with `BUILD_LIST=core,imgproc,video`, most I/O backends off and JPEG built in, and `OPENCV_GENERATE_PKGCONFIG=ON`. armv7hf uses `arm-gnueabi.toolchain.cmake` with `CPU_BASELINE=NEON,VFPV3`; aarch64 uses `aarch64-gnu.toolchain.cmake`. Compiler and flags are re-derived by splitting `$CC`/`$CXX`, because those variables do not combine with `CMAKE_TOOLCHAIN_FILE`. Shared objects are copied to `./lib`.
- **App** (`app/example.cpp`): `vdo_stream_y800_new` for channel 1 at 1024x576, `poll`, `vdo_stream_get_buffer`, wraps the buffer in a `cv::Mat`, runs MOG2 background subtraction and a morphological open, and logs `Motion detected: YES|NO` and `Ran opencv for N ms`. Makefile: `-Os -std=c++11`, links `opencv_video imgproc core`.
- **Limits:** only three modules are built, so other `cv::` calls fail to link unless `BUILD_LIST` grows; README tree names `building-opencv` and a non-existent `sources.list`.[^native-examples]

## curl-openssl

- Uses the SDK's OpenSSL 3 and libcurl (`PKGS = openssl libcurl`). The Dockerfile runs the host `openssl s_client -showcerts` against `www.example.com:443` (optionally through `--build-arg BUILD_PROXY`) to write `cacert.pem` and adds it with `acap-build . -a cacert.pem`.
- Runtime: a first `curl_easy_perform` without a CA store fails by design; `sslctx_function` then loads `/usr/local/packages/curl_openssl/cacert.pem` into the store and the second transfer succeeds and is saved under `localdata/`. `--build-arg APP_DEBUG=yes` enables verbose curl.
- **Defects:** `CURLOPT_SSL_VERIFYHOST` is `1L` (deprecated, treated as 2); `write_to_file` returns `-1` as `size_t`; the certificate captured at build time is short-lived, so a skewed device clock gives `CURLE_PEER_FAILED_VERIFICATION (60)`.[^native-examples]

## utility-libraries

- **`custom_lib_example`:** `custom_build/Makefile` builds `libcustom.so.1.0.0` and symlinks `libcustom.so.1` and `libcustom.so`; the Dockerfile runs it, moves the objects into `lib/`, then `acap-build`. The app only calls `log_hello_world()` (syslog "Hello World!"). The README uses `appname=mainfunc` in its log URL although the app is `customlib_example`.
- **`openssl_curl_example`:** deletes the SDK's `libcrypto`/`libssl`/`libcurl` objects, pkg-config files and headers so linking cannot silently use them, builds **OpenSSL 1.1.1m** (`./Configure linux-armv4|linux-aarch64 no-deprecated shared`) and **curl 7.83.1**, and bundles the three libraries with `RUNPATH $ORIGIN/lib`; the README shows how to verify with `objdump -p` and `ldd`. It marks OpenSSL 1.1.1 end-of-life and points to `curl-openssl` instead; the Licensekey API still needs the SDK `libcrypto`, which is why deletion happens in the build only.[^native-examples]

Which libraries the SDK image itself hides from applications is covered in [sysroot pruning](acap-native-sdk-sysroot-pruning.md); that is separate from the explicit deletion `openssl_curl_example` performs in its own build.

Evidence class: **Observed** from Dockerfiles, Makefiles and sources; no library was built.

## Relationships

- **Part of** [ACAP Native SDK examples repository](acap-native-sdk-examples-repository.md).
- **Uses** VDO capture as in [vdostream](acap-example-vdo-video-capture-and-opencl.md).
- **Illustrates** [Tích hợp third-party library vào ACAP application](acap-third-party-libraries.md) with working code, and relates to [proxy configuration](acap-proxy-configuration.md) for the `BUILD_PROXY` argument.

[^native-examples]: `using-opencv/{Dockerfile,README.md,app/{example.cpp,Makefile,manifest.json}}`; `curl-openssl/{Dockerfile,README.md,app/{curl_openssl.c,Makefile}}`; `utility-libraries/README.md`; `utility-libraries/custom_lib_example/{Dockerfile,app/custom_build/Makefile,app/Makefile,README.md}`; `utility-libraries/openssl_curl_example/{Dockerfile,app/Makefile,README.md}`.
