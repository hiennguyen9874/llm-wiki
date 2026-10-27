---
type: Concept
title: "Tùy biến AXIS Object Analytics (AOA)"
description: "Phạm vi tùy biến AXIS Object Analytics: rule, vùng, event và overlay qua API, nhưng không có interface công khai để thay backbone detector."
tags: [edge-ai, axis, object-analytics, analytics]
status: stable
created: 2026-10-27
generated: { by: llm-wiki-agent/1, at: 2026-10-27T04:52:04Z }
stale_after: 2027-04-30
sources:
  - id: axis-ai-chatgpt-research
    resource: ../raw/axis-ai-chatgpt-research.md
    kind: research
    title: "Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis"
---

# Tùy biến AXIS Object Analytics (AOA)

AXIS Object Analytics là application chính thức của Axis, có sẵn trên nhiều camera, cung cấp chức năng phát hiện, phân loại và xử lý tình huống. AOA API cho phép thiết lập scenario, vùng phát hiện, trigger, rule và overlay, nhưng trong tài liệu API công khai được nguồn kiểm tra không có cơ chế được tài liệu hóa để upload model tùy ý thay thế backbone nhận diện bên trong AOA.[^axis-ai-chatgpt-research]

## Các hướng phát triển

| Hướng phát triển | Khả năng |
| --- | --- |
| Dùng AOA và custom các rule/event | Có, theo API cung cấp |
| Thay detector gốc trong AOA bằng model PyTorch riêng | Không có interface công khai được xác nhận |
| Viết ACAP application với model riêng, chạy cạnh AOA | Có, nếu tài nguyên cho phép |
| Tắt AOA và sử dụng hoàn toàn custom ACAP inference | Có, nếu camera hỗ trợ application tương ứng |

Nếu cần nhận diện một loại đối tượng đặc thù như lỗi sản phẩm, vật thể công nghiệp hoặc class ngoài tập nhãn mặc định, hướng phù hợp hơn là viết ACAP application riêng. Khi chạy song song với AOA, cần tính đến việc chia sẻ tài nguyên DLPU làm giảm latency/FPS.[^axis-ai-chatgpt-research]

## Relationships

- **Part of** hệ sinh thái application trên camera Axis.
- **Configurable through** AOA API cho scenario, vùng, trigger, rule và overlay.
- **Does not support** thay detector qua public API theo tài liệu được kiểm tra.
- **Coexists with** [custom ACAP application](axis-custom-model-deployment.md) nếu tài nguyên cho phép.
- **Alternative** là custom ACAP application cho class ngoài tập nhãn mặc định.
- **Constrained by** [tài nguyên DLPU dùng chung](axis-dlpu-model-constraints.md).

## Độ tin cậy

Trang này là **Reported** từ nguồn thứ cấp. Kết luận "không có interface công khai" chỉ phản ánh tài liệu công khai tại thời điểm nguồn được viết; không chứng minh rằng cơ chế đó không tồn tại hoặc sẽ không xuất hiện trong phiên bản AOA sau.

[^axis-ai-chatgpt-research]: Nguồn thứ cấp: [Phân tích Axis DLPU và khả năng triển khai Custom AI Models trên Camera Axis](../raw/axis-ai-chatgpt-research.md), §7 "Có thể thay model bên trong AXIS Object Analytics không?" và §6.3 về chia sẻ tài nguyên DLPU.
