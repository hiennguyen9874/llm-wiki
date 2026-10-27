---
type: Concept
title: "ACAP developer FAQ: machine learning, IP protection, cloud integration and help channels"
description: "Curated answers from the archived ACAP FAQ and neighbouring pages: TensorFlow Lite as the only ML format, running several models on one DLPU, ARTPEC-7 to ARTPEC-8 migration, why quantization loses accuracy, protecting an app from copying, cloud integration examples and where to ask for help."
tags: [edge-ai, axis, acap, faq, machine-learning, security]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T15:00:00Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-repo
    resource: ../raw/acap-documentation/README.md
    scope: ../raw/acap-documentation/
    kind: code
    revision: "12.2-17-g4aa04f1 (4aa04f185618e66f493453bcd62da1788c3059e4, 2025-02-06)"
    title: "ACAP documentation (archived repository)"
  - id: acap-docs-faq
    resource: ../raw/acap-documentation/docs/faq/index.md
    scope: ../raw/acap-documentation/docs/faq/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "ACAP FAQ: machine learning, security, deployment"
  - id: acap-docs-cloud-help
    resource: ../raw/acap-documentation/docs/cloud-integrations/index.md
    scope: ../raw/acap-documentation/docs/cloud-integrations/
    kind: docs
    revision: "12.2-17-g4aa04f1"
    title: "Cloud integrations and Get help pages"
---

# ACAP developer FAQ: machine learning, IP protection, cloud integration and help channels

The archived FAQ is a short set of vendor answers. Its machine-learning page defers almost every detail to the Computer Vision documentation on `developer.axis.com`, but it states six facts that are directly useful: only TensorFlow Lite is supported as a model format, several models run concurrently but not in parallel, ARTPEC-7 models usually carry over to ARTPEC-8 after re-quantization, accuracy loss after quantization is normal, the training examples are `tensorflow-to-larod*`, and the DLPU accelerates inference relative to the CPU.[^acap-docs-faq] The security page adds the vendor's position on copying, and the cloud and help pages list integration examples and support channels.[^acap-docs-cloud-help] The repository is an archived snapshot; its pages redirect to the live site ([ACAP documentation repository](acap-documentation-repository.md)).[^acap-docs-repo]

## Machine learning

| Question | Answer in the FAQ |
| --- | --- |
| Which format? | "No, only Tensorflow Lite is supported"; other formats must be converted to TFLite |
| Recommended models per SoC | ARTPEC-7, ARTPEC-8 and CV25 have a recommended-architecture page; the Axis Model Zoo repository holds compatible models with accuracy and speed figures |
| Supported layers | Prefer simple layers; use the optimisation tips and the "test your model" guide to verify |
| Training process | Native SDK examples named `tensorflow-to-larod`, `tensorflow-to-larod-artpec8`, `tensorflow-to-larod-cv25` |
| Several models at once | Run "concurrently but not in parallel": the DLPU switches between inferences and load is not shared equally unless models are similar in size and complexity; stop AXIS Object Analytics if it is not needed |
| ARTPEC-7 (TPU) model on ARTPEC-8 | Generally works; the difference is the quantization stage, not the architecture |
| Accuracy loss after quantization | "Unfortunately normal and difficult to avoid" |
| DLPU versus CPU | The DLPU accelerates model execution, making inference "significantly faster compared to the CPU" |

Evidence class: **Reported**. All elaboration lives in pages not present locally; the local detail is in [Axis DLPU](axis-dlpu.md), [DLPU model constraints](axis-dlpu-model-constraints.md), [Deploying a custom AI model to Axis cameras](axis-custom-model-deployment.md) and [ARTPEC-9 model conversion](axis-artpec-9-model-conversion.md).[^acap-docs-faq]

**Qualification (Synthesis):** "only TensorFlow Lite" describes the deployed format for ARTPEC-7/8 (and ARTPEC-9, which accepts PyTorch, TensorFlow or JAX sources converted to TFLite). The vendor conversion pages in this wiki also name a native `.bin` path for CV25 and CV75 ([ONNX to CV75](axis-cv75-onnx-conversion.md)), so the FAQ answer is not a universal rule for every SoC. It also pre-dates ARTPEC-9, which the FAQ does not mention. The heading "Why do I loose accuracy…" contains a typo (and anchor).

## IP and licence protection

- "An ACAP application is like any software that comes in a package. It can be inspected and reverse-engineered"; it is "impossible to prevent someone from copying software available on the market". The offered defences are know-how, support, a partner network and legal action (trademark or patent).[^acap-docs-faq]
- For ML apps, the page argues the valuable assets are customer and problem knowledge, and that taking parts of a solution from a device "will not give anyone access to the training data to evolve the model".
- Axis "provides a licensing mechanism that prevents ACAP applications from running without a valid license key", which also tracks use. No mechanism details are given here; the API is the License Key API in the [Native SDK API catalog](acap-native-sdk-api-catalog.md). **Reported**, vendor assertion, not verified.
- Signing is a separate control: see [ACAP application signing](acap-application-signing.md).

## Cloud integration examples

The cloud-integrations page frames devices as parts of larger solutions and lists Axis example repositories: AWS (images to S3, telemetry to IoT Core), GCP (images to Cloud Storage) and Azure (images to a storage account, telemetry to IoT Edge and IoT Hub). They are pointers to GitHub repositories that are not local, so behaviour is not verified.[^acap-docs-cloud-help]

## Where to ask

Issues and Discussions in `acap-native-sdk`, `acap-native-sdk-examples` and `acap-computer-vision-sdk-examples`; the general ACAP Discussions category; issues and pull requests in `acap-documentation` for doc errors; and the Axis Developer Community. Each example README follows a fixed structure (description, repository structure, limitations, build and run, expected output) and examples are findable with the GitHub topic `acap`.[^acap-docs-cloud-help] See [Official ACAP application examples](acap-application-examples.md).

## Limits

The `licenses` page only credits the MIT-licensed Jekyll theme and says nothing about ACAP licensing, and its redirect points at the documentation root. The deployment FAQ is covered separately in [Deploying an ACAP application to many devices](acap-fleet-deployment-via-vapix.md).

## Relationships

- **Complements** [Hướng triển khai custom AI trên Axis](axis-edge-ai-adoption-guide.md) with vendor answers on concurrency and quantization.
- **Uses** [Axis DLPU](axis-dlpu.md) as the accelerator the FAQ describes.
- **Related to** [AXIS Object Analytics customization](axis-object-analytics.md): the FAQ advises stopping Object Analytics when it competes for the DLPU.
- **Source map**: [ACAP documentation repository](acap-documentation-repository.md).

[^acap-docs-repo]: [README](../raw/acap-documentation/README.md) archive notice; each FAQ page carries `redirect_to` to `developer.axis.com/acap/faq/…`.
[^acap-docs-faq]: [faq/index.md](../raw/acap-documentation/docs/faq/index.md); `machine-learning.md` (ten Q&A headings); `security.md` §Cybersecurity and protecting models.
[^acap-docs-cloud-help]: [cloud-integrations/index.md](../raw/acap-documentation/docs/cloud-integrations/index.md); `get-help-and-give-feedback/index.md`; `introduction/acap-examples.md`; `licenses/index.md`.
