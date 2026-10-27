---
title: "Axis devices & compatibility | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/reference/develop-container-applications/axis-devices-and-compatibility/"
domain: "developer.axis.com"
language: "en"
description: "Note on container applications:"
word_count: 450
---

Version: ACAP version 12

> [!-warning] -warning
> warning
> 
> **Note on container applications:**
> 
> - New Axis products released on AXIS OS 12.x will not have container support.
> - [All products with existing container support](https://www.axis.com/support/tools/product-selector/shared/%5B%7B%22index%22%3A%5B10%2C0%5D%2C%22value%22%3A%22ARTPEC-8%22%7D%2C%7B%22index%22%3A%5B10%2C2%5D%2C%22value%22%3A%22Yes%22%7D%5D) will be supported until end of 2031 when [AXIS OS 2026 LTS](https://help.axis.com/en-us/axis-os) reaches end of life.
> - The recommended way to build analytics, computer vision and machine learning applications on Axis devices with ACAP support, is to use the ACAP Native SDK. For usage see the [acap-native-sdk-examples](https://github.com/AxisCommunications/acap-native-sdk-examples) repository.
> - The ACAP Computer Vision SDK has been archived as its components have been refactored: utility libraries and scripts are now available in [ACAP Runtime](https://github.com/AxisCommunications/acap-runtime). For usage of the new setup, see the [examples](https://github.com/AxisCommunications/acap-computer-vision-sdk-examples) repository.

## Computer Vision solution and device compatibility

For containerized applications using the ACAP Computer Vision solution, compatibility is limited to specific devices and AXIS OS versions.

> [!-info] -info
> info
> 
> - Support for containerized applications using `armv7hf` are no longer supported after AXIS OS 11.11.

To get a list of devices that are compatible with the ACAP Computer Vision solution, you can use Axis [Product selector](https://www.axis.com/support/tools/product-selector).

More than one filter can be combined in a search, for example in the **Hardware platform** section it's possible to filter on:

- Products equipped with `DLPU` using the field **Compute capabilities**
- Products with `aarch64` by choosing `ARTPEC-8` in field **System-on-chip**
- Products with container support by checking the **Container support** checkbox.

For convenience, here are direct links to a few specific filters you can apply to list supported products for `aarch64`:

- [Container support](https://www.axis.com/support/tools/product-selector/shared/%5B%7B%22index%22%3A%5B10%2C0%5D%2C%22value%22%3A%22ARTPEC-8%22%7D%2C%7B%22index%22%3A%5B10%2C2%5D%2C%22value%22%3A%22Yes%22%7D%5D)
- [Container + DLPU support](https://www.axis.com/support/tools/product-selector/shared/%5B%7B%22index%22%3A%5B10%2C0%5D%2C%22value%22%3A%22ARTPEC-8%22%7D%2C%7B%22index%22%3A%5B10%2C1%5D%2C%22value%22%3A%22DLPU%22%7D%2C%7B%22index%22%3A%5B10%2C2%5D%2C%22value%22%3A%22Yes%22%7D%5D)

## ACAP Computer Vision solution software compatibility

> [!-info] -info
> info
> 
> - From AXIS OS 12.0, the ACAP Computer Vision SDK has been archived as its components have been refactored: utility libraries and scripts are now available in [ACAP Runtime](https://github.com/AxisCommunications/acap-runtime). For usage of the new setup, see the [examples](https://github.com/AxisCommunications/acap-computer-vision-sdk-examples) repository.

The following information and compatibility table are provided for reference and to support legacy applications using versions prior to AXIS OS 12.0:

The **Image version** referred to in the table below is the Docker image release tag available from Docker Hub:

- [ACAP Computer Vision SDK](https://hub.docker.com/r/axisecp/acap-computer-vision-sdk/tags)

The tag format is `<image-version>-<architecture>-<sdk_type>`. In the tag examples below, `1.5` maps to the image version.

| ACAP Release | ACAP CV SDK Image version | Compatible with AXIS OS version |
| --- | --- | --- |
| 4.0 | 1.0 | 10.7 and later |
| 4.1 | 1.1 | 10.9 and later |
| 4.2 | 1.2 | 10.10 and later |
| 4.3 | 1.3 | 10.12 (LTS) |
| 4.4 | 1.4 | 11.0 and later |
| 4.5 | 1.5 | 11.1 and later |
| 4.6 | 1.6 | 11.2 and later |
| 4.7 | 1.7 | 11.3 and later |
| 4.8 | 1.8 | 11.4 and later |
| 4.9 | 1.9 | 11.5 and later |
| 4.10 | 1.10 | 11.6 and later |
| 4.11 | 1.11 | 11.7 and later |
| 4.12 | 1.12 | 11.8 (breaking change) |
| 4.13 | 1.13 | 11.9 and later |
| 4.14 | 1.14 | 11.10 and later |
| 4.15 | 1.15 | 11.11 (LTS) |
