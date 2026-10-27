---
title: "Run computer vision models inside ACAP applications"
site: "Axis developer documentation"
source: "https://developer.axis.com/acap/how-to-guides/computer-vision-on-device/"
domain: "developer.axis.com"
language: "en"
description: "The Axis Camera Application Platform (ACAP) enables you to build and deploy applications that run deep learning models directly on Axis cameras. By integrating a trained model into an ACAP application, you can perform real-time video analysis on the device, reducing reliance on cloud-based processing."
word_count: 137
---

Version: ACAP version 12

The **Axis Camera Application Platform (ACAP)** enables you to build and deploy applications that run deep learning models directly on Axis cameras. By integrating a trained model into an ACAP application, you can perform real-time video analysis on the device, reducing reliance on cloud-based processing.

## Create and prepare your model

For guidance on training, converting, and optimizing a deep learning model for Axis devices, see the [Computer vision](https://developer.axis.com/computer-vision/) documentation.

## Integrate a model with an ACAP application

To use your model inside an ACAP application, use the [Video capture API (VDO)](https://developer.axis.com/acap/reference/supported-apis/#video-capture-api-vdo) to get frames from the camera and the [Machine Learning API (Larod)](https://developer.axis.com/acap/reference/supported-apis/#machine-learning-api-larod) to run DLPU-accelerated inference on your model. Explore the following examples in the [ACAP Native SDK examples](https://github.com/AxisCommunications/acap-native-sdk-examples) repository to get more inspiration about how this can be implemented:

- [vdo-larod](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/vdo-larod)
- [object-detection](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/object-detection)
- [object-detection-yolov5](https://github.com/AxisCommunications/acap-native-sdk-examples/tree/main/object-detection-yolov5)
