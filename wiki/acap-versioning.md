---
type: Concept
title: "Phiên bản ACAP và tương thích với AXIS OS"
description: "Quy tắc chọn phiên bản ACAP theo AXIS OS LTS, và việc số phiên bản ACAP trùng với AXIS OS từ bản 12.0."
tags: [edge-ai, axis, acap, compatibility, versioning]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T04:56:41Z }
stale_after: 2027-04-30
sources:
  - id: acap-docs-index-v12
    resource: ../raw/acap/index/index.md
    scope: ../raw/acap/index/
    kind: docs
    revision: "ACAP version 12"
    title: "ACAP version 12 | Axis developer documentation"
---

# Phiên bản ACAP và tương thích với AXIS OS

Phiên bản ACAP phải chọn theo AXIS OS LTS mà thiết bị đích chạy, không chọn độc lập. Từ AXIS OS 12.0 trở đi — và không áp dụng cho các bản trước đó — số phiên bản ACAP trùng với số phiên bản AXIS OS, nên AXIS OS 12.x đi với ACAP 12.x. Tài liệu ACAP được xuất bản theo từng phiên bản, và một bộ tài liệu chỉ đúng trong phạm vi phiên bản của nó.[^acap-docs-index-v12]

## Quy tắc chọn phiên bản

Đây là quy tắc mà tài liệu Axis nêu trực tiếp, kèm hệ quả thực hành:[^acap-docs-index-v12]

| Tình huống | Phiên bản ACAP |
| --- | --- |
| Thiết bị đích chạy AXIS OS 12.x | ACAP 12.x, theo quy tắc trùng số từ AXIS OS 12.0 |
| Thiết bị đích chạy AXIS OS trước 12.0 | Không suy ra được từ quy tắc trùng số; phải tra version history của bộ tài liệu ACAP |
| Sản phẩm phải chạy trên nhiều AXIS OS LTS | Không có một phiên bản ACAP duy nhất; mỗi LTS cần build và kiểm tra theo bộ SDK, manifest schema và API của phiên bản tương ứng |

**Synthesis:** Ba bước thực dụng là (1) xác định AXIS OS LTS của thiết bị đích, (2) chọn bộ tài liệu ACAP cùng số phiên bản, (3) đối chiếu trang version history và trang thiết bị/tương thích trong chính bộ tài liệu đó trước khi khóa toolchain. Bước 3 cần thiết vì quy tắc trùng số chỉ nói về quan hệ phiên bản, không nói camera cụ thể có được hỗ trợ hay không.

## Hệ quả khi triển khai

- Phiên bản ACAP là một biến của quyết định nền tảng, không phải chi tiết build: cùng một ứng dụng phải được kiểm tra lại khi AXIS OS LTS của thiết bị đích thay đổi.
- Nâng **major** AXIS OS (ví dụ 12.11 → 13.x) không chỉ đổi số phiên bản mà còn là thay đổi breaking ở mức manifest và API; xem [chuẩn bị cho AXIS OS 13 và 14](acap-axis-os-13-14-migration.md).
- Manifest schema, supported APIs và supported operators có thể khác nhau giữa các phiên bản, nên ví dụ hoặc manifest của một phiên bản không nên sao chép nguyên sang phiên bản khác.
- Với dự án dài hạn, việc chọn phiên bản ACAP gắn với lộ trình AXIS OS của khách hàng; xem thêm [hướng triển khai và PoC](axis-edge-ai-adoption-guide.md) và [ACAP Native SDK](axis-acap-native-sdk.md).

## Độ phủ nguồn

- Entry point: `raw/acap/index/index.md` (672 từ), bộ tài liệu "ACAP version 12", site `developer.axis.com/acap/`.
- Nguồn dẫn tới một hình minh họa ánh xạ ACAP version ↔ AXIS OS LTS, nhưng hình này **không có trong** `raw/acap/index/assets/`; do đó wiki không ghi lại bảng ánh xạ cụ thể nào.
- Trang version history và trang thiết bị/tương thích được nguồn trỏ tới nhưng chưa có trong `raw/`, nên chưa được kiểm chứng độc lập.
- Bản capture không có ngày xuất bản hay ngày cập nhật; `revision` chỉ suy ra từ tiêu đề bộ tài liệu.

## Độ tin cậy

Quy tắc trùng số phiên bản và yêu cầu dùng phiên bản ACAP được hỗ trợ là **Reported** từ tài liệu chính thức của Axis (bộ ACAP 12). Suy luận về nhiều LTS song song và ba bước chọn phiên bản là **Synthesis**. Không có claim nào **Reproduced** trong lần ingest này.

## Relationships

- **Constrains** [ACAP Native SDK](axis-acap-native-sdk.md): toolchain, manifest schema và API phải khớp phiên bản ACAP của AXIS OS LTS đích.
- **Depends on** AXIS OS LTS của thiết bị đích.
- **Guides** [quyết định triển khai](axis-edge-ai-adoption-guide.md) khi khóa nền tảng cho sản phẩm dài hạn.
- **Constrained by** [breaking changes của AXIS OS 13/14](acap-axis-os-13-14-migration.md) và [Upgrading an ACAP manifest to schema v2](acap-manifest-schema-v2-upgrade.md): `compatibleOsVersions` bắt buộc từ AXIS OS 13, kéo theo yêu cầu manifest schema v2 và thủ tục nâng cấp manifest.
- **Constrains** [Migrating ACAP applications from package.conf to manifest.json](acap-package-conf-to-manifest-migration.md): the SDK-to-schema mapping selects `--schema-version`, and `package.conf` support ends with AXIS OS 13.
- **Constrains** [ACAP application signing](acap-application-signing.md): whether a device verifies the signature and whether it accepts unsigned packages depends on its AXIS OS version, and schema v2 is required to obtain a `vendorId`.

[^acap-docs-index-v12]: Tài liệu chính thức: [ACAP version 12 — Axis developer documentation](../raw/acap/index/index.md), §Introduction (câu về "supported ACAP version" và AXIS OS LTS) và §ACAP versioning.
