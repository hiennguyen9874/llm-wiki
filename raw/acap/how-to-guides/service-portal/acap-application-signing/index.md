---
title: "ACAP application signing | Axis developer documentation"
site: "developer.axis.com"
source: "https://developer.axis.com/acap/how-to-guides/service-portal/acap-application-signing/"
domain: "developer.axis.com"
language: "en"
description: "ACAP application signing is the process of digitally signing an ACAP application to ensure that it has not been tampered with and that it was produced by the identified software provider. This provides an additional layer of security and gives end users confidence that the application is authentic and has not been modified since it was signed."
word_count: 1371
---

Version: ACAP version 12

ACAP application signing is the process of digitally signing an ACAP application to ensure that it has not been tampered with and that it was produced by the identified software provider. This provides an additional layer of security and gives end users confidence that the application is authentic and has not been modified since it was signed.

ACAP applications can be signed via two different paths depending on your partnership status. TIP partners, members of the [Axis Technology Integration Partner (TIP)](https://www.axis.com/partner/technology-integration-partner-program) program, use the [ACAP Service Portal](#acap-service-portal), for more details see [Sign an ACAP application as a TIP partner](#sign-an-acap-application-as-a-tip-partner). Developers outside of the TIP program, non-TIP partners, can sign their applications using the [ACAP Signing Service](#acap-signing-service), for more details see [Sign an ACAP application as a non-TIP partner](#sign-an-acap-application-as-a-non-tip-partner).

## Why sign your application?

By signing your ACAP application, you can:

- Ensure that the application has not been tampered with during distribution.
- Establish the authenticity of the application by identifying its software provider.
- Increase end users' confidence that they are installing a genuine ACAP application.

> [!-secondary] -secondary
> note
> 
> When viewing installed ACAP applications in the AXIS OS 12.11 web interface, some signed applications may appear with the **unsigned** badge.
> 
> This affects signed applications originally installed on **AXIS OS 12.7 or earlier**, as the signature status was not persisted at that time. Consequently, their signature status is therefore unknown in **AXIS OS 12.11 or later**, but the application functionality is not affected.
> 
> Applications installed before **AXIS OS 12.8** must be reinstalled on **AXIS OS 12.8 or later** before upgrading to AXIS OS 13.

## Sign an ACAP application as a TIP partner

TIP partners can sign ACAP applications through [ACAP Service Portal](#acap-service-portal). Before starting, ensure that you have a registered application in the portal and that you have an active [axis.com](https://www.axis.com/) account.

Follow these steps to sign your ACAP application:

1. Access the [ACAP Service Portal](https://www.axis.com/partner_pages/compatible_applications/#/applications) page. The portal allows you to register applications, search for existing applications, upload ACAP packages for signing, and find your `vendorId`. Log in using your [axis.com](https://www.axis.com/) account.
2. Use the **Filter items by name or description** search bar to locate your registered application. If necessary, register a new application by clicking **REGISTER**.
3. Open the application details page and retrieve the required values from the `manifest.json` examples in the **Pre-requisite information to sign** section: `appId` and `vendor` are available for both manifest schema v1 and v2, while `vendorId` is available only for manifest schema v2.
4. Before uploading the `.eap` file for signing, update and build the ACAP using the `manifest.json` file with the retrieved values and ensure it complies with the [manifest schema](https://developer.axis.com/acap/reference/manifest-schemas/general-info/) requirements. Note that the `vendor` and `vendorId` values in the ACAP application's `manifest.json` file are **case-sensitive** and must exactly match the values provided by the ACAP Service Portal for the application to be successfully validated.
5. Click **SIGN PACKAGE** to proceed with signing your ACAP package. In the package upload window, upload your `.eap` file by clicking **UPLOAD A PACKAGE** or by dragging and dropping the file directly into the upload area.
6. After the `.eap` file has been uploaded successfully, click the **SIGN** to sign your application.
7. When the signing process completes successfully, a confirmation message is displayed, and the signed `.eap` package is **downloaded automatically**.

### ACAP Service Portal

The [ACAP Service Portal](https://www.axis.com/partner_pages/compatible_applications/#/applications) is available to members of the [Axis Technology Integration Partner (TIP) Program](https://www.axis.com/partner/technology-integration-partner-program). It allows TIP partners to manage their ACAP applications, including:

- Register and manage applications.
- Retrieve application information, including the `appId`, `vendor`, and `vendorId` required for signing.
- Enable and configure the licensing service, including trial and free licenses to users.
- Manage all aspects around licenses such as generating codes, and track and modify license keys.
- Declare and restrict application compatibility with Axis devices based on verified support.
- Sign ACAP applications to ensure authenticity, and to prevent tampering.

All colleagues who are members of the Technology Integration Partner Program have access to the ACAP Service Portal by default. To check who has access within your organization, use the [My Colleagues](https://www.axis.com/partner_pages/colleagues.php) tool. To add or remove users, contact [partner-services@axis.com](mailto:partner-services@axis.com).

## Sign an ACAP application as a non-TIP partner

Non-TIP partners can sign ACAP applications through the [ACAP Signing Service](#acap-signing-service) using an [axis.com](https://www.axis.com/) account. Only ACAP applications using [manifest schema v2.x](https://developer.axis.com/acap/reference/manifest-schemas/general-info/#manifest-schema-version-2) are supported. Applications using manifest schema v1.x must be upgraded before they can be signed.

Follow these steps to sign your ACAP application:

1. Access the [ACAP Signing Service](https://www.axis.com/support/acap-signing) page and click **PROCEED TO LOGIN** to log in using your [axis.com](https://www.axis.com/) account.
2. Read and accept the signing terms and conditions by selecting **I have read and understood** and clicking **AGREE**. Note that the signing terms appear each time you access the page.
3. If prompted, allow the browser **to access the local network**. This is required to load your account-specific manifest information.
4. On the welcome page, retrieve your unique `vendor` and `vendorId` values from the provided `manifest.json` example. Note that the `vendor` and `vendorId` values in the ACAP application's `manifest.json` file are **case-sensitive** and should be set to the exact values provided by ACAP Service Portal for the application to be successfully validated.
5. Before uploading the `.eap` file for signing, update the application's `manifest.json` with the retrieved values, rebuild the ACAP application and ensure the manifest complies with the [manifest schema](https://developer.axis.com/acap/reference/manifest-schemas/general-info/) requirements.
6. Click **CHOOSE YOUR EAP FILE TO SIGN**, select the `.eap` file, and then click **SIGN THE ACAP**.
7. When the signing process completes successfully, a confirmation message is displayed, and the signed `.eap` package is **downloaded automatically**.

### ACAP Signing Service

The [ACAP Signing Service](https://www.axis.com/support/acap-signing) is available to non-TIP partners who can sign ACAP applications using an [axis.com](https://www.axis.com/) account. It supports ACAP applications using **manifest schema v2.x** and provides the information required to prepare the application's `manifest.json` file before signing. The ACAP Signing Service does not store uploaded ACAP packages or signing history.

With the ACAP Signing Service, you can:

- Review and accept signing terms and conditions.
- Retrieve account-specific `vendor` and `vendorId` values required for the application's `manifest.json` file.
- Upload ACAP packages (`.eap` files) for signing.
- Sign ACAP applications without storing application or signing history.
- Download the signed ACAP package.

## Verifying the signature

ACAP applications are signed using SHA-512 and a 4096 bit RSA private key which is stored securely in a Thales Luna Network HSM 7 in the Axis datacenter.

Axis network devices are preloaded with the 4096 bit RSA public key in order to validate the ACAP signature prior to ACAP-installation. The public key is stored on the Axis network device on the Linux filesystem.

With [AXIS OS 9.20](https://help.axis.com/en-us/axis-os-release-notes#active-2019-9-20) and later, the Axis device verifies the signature of a signed ACAP application on installation. Applications without a signature are still supported. The signature is fully backward compatible, i.e. a signed application can be installed on a device with an AXIS OS version earlier than 9.20, in which case the device doesn't verify the application.

## History

With [AXIS OS 11.2](https://help.axis.com/en-us/axis-os-release-notes#axis-os-11-2), an [interface is added to VAPIX](https://developer.axis.com/vapix/applications/application-api/) to control whether an Axis device only accepts signed ACAP applications or not, improving the device's security posture.

In AXIS OS 12.0, the default value has changed to only allow signed applications by default. For more information regarding the reasoning for this change, see the [article](https://www.axis.com/for-developers/news/axis-os-root-acap-signing) on Axis For Developers. If developers want to install unsigned applications, they can do so by either using the VAPIX interface to allow unsigned applications or by manually toggling the **Allow unsigned apps** toggle through the web interface.

| AXIS OS | Signing requirement (default value) | Change signing requirement |
| --- | --- | --- |
| 9.20 - 11.1 | Both signed and unsigned applications are allowed to be installed. | Not possible to change. |
| 11.2 - 11.11 | Both signed and unsigned applications are allowed to be installed. | The VAPIX interface can be used to configure the device to only allow signed applications. |
| 12.0 - 12.11 | By default, only signed applications are allowed to be installed. | The VAPIX interface can be used to configure the device to allow both signed and unsigned applications. |

Axis recommends that you allow unsigned applications to be installed during the development of your ACAP application.

### Planned changes

In AXIS OS 13, the possibility to allow unsigned applications will be removed.
