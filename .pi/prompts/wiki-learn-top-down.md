---
description: Generate a top-down wiki course that explains intuition and practical impact before mathematics.
skills:
  - wiki-learn
skills-position: before
---

Tạo một `course top-down` cho người mới từ yêu cầu bên dưới. Giữ technical keywords bằng tiếng Anh và viết prose bằng tiếng Việt. Mục tiêu là giúp người đọc hiểu **vấn đề → cơ chế → tác động → khác biệt → cách dùng thực tế** trước khi đi vào toán học, implementation và verification.

## Trình tự giảng dạy bắt buộc

Tổ chức nội dung theo các tầng sau, từ tổng quan đến chi tiết:

1. **Bức tranh toàn cảnh**
   - Chủ đề này giải quyết vấn đề gì?
   - Ý tưởng cốt lõi trong một câu là gì?
   - Dùng một `mental model`, ví dụ đời thường hoặc `text diagram` để người mới hình dung.
   - Nêu rõ người đọc sẽ hiểu được gì sau bài học.

2. **Cách hoạt động — nhìn từ đầu đến cuối**
   - Đi theo luồng `input → các bước xử lý → output` bằng ngôn ngữ trực giác.
   - Giải thích vai trò của từng thành phần và chúng phối hợp với nhau ra sao.
   - Dùng một ví dụ cụ thể chạy xuyên suốt toàn bộ luồng.
   - Ưu tiên sơ đồ, bảng và ví dụ số đơn giản; để ký hiệu đại số và tensor shapes cho tầng toán học.

3. **Tác động**
   - Cơ chế này thay đổi điều gì về behavior, quality, memory, compute, latency hoặc khả năng mở rộng?
   - Tách rõ lợi ích, chi phí và điều kiện để lợi ích xuất hiện.
   - Phân biệt hệ quả trực tiếp của thiết kế với kết quả chỉ được báo cáo qua benchmark.

4. **Sự khác biệt**
   - So sánh với baseline hoặc cơ chế gần nhất bằng một bảng: `giống nhau`, `khác nhau`, `trade-off`, `khi nào phù hợp`.
   - Chỉ ra thay đổi nằm ở đâu trong data flow và phần nào của hệ thống vẫn giữ nguyên.
   - Giải thích các khái niệm dễ nhầm trước khi đưa ra chi tiết kỹ thuật.

5. **Trong thực tế**
   - Cơ chế nằm ở đâu trong một model hoặc system thật?
   - Khi nào nên dùng, khi nào không nên dùng, và workload nào hưởng lợi?
   - Cho ít nhất một walkthrough thực tế hoặc scenario cụ thể.
   - Nêu các giới hạn triển khai, measurement cần kiểm tra và claim nào không thể suy ra chỉ từ lý thuyết.

6. **Toán học — zoom in sau cùng**
   - Công thức LaTeX đầu tiên chỉ xuất hiện sau khi năm tầng trên đã trả lời đầy đủ các câu hỏi tương ứng.
   - Mở đầu bằng bảng ký hiệu ngay trước công thức đầu tiên.
   - Đi từ trường hợp nhỏ nhất có thể tính tay → công thức tổng quát → derivation hoặc proof.
   - Với mỗi công thức quan trọng, trình bày theo thứ tự: **trực giác → công thức → ý nghĩa từng ký hiệu → shape flow → ví dụ số → kết luận**.
   - Chỉ derive những công thức cần để giải thích cơ chế và trade-off; đặt proof dài hoặc biến thể nâng cao ở cuối phần toán học để người đọc có thể bỏ qua mà vẫn hiểu bài.

7. **Implementation, verification và trade-offs**
   - Tiếp tục theo `wiki-learn`: PyTorch tối thiểu, code có thể inspect, tests có `torch.testing.assert_close`, benchmark/trade-off đúng phạm vi, debug checklist, giới hạn, relationships và evidence limits.
   - Nối mỗi đoạn code với cơ chế đã giải thích ở các tầng trước; code là bước cụ thể hóa, không phải nơi giới thiệu khái niệm lần đầu.

## Tiêu chí hoàn thành

Trước khi lưu bài, đọc từ H1 đến công thức đầu tiên và kiểm tra rằng người mới đã có thể trả lời đủ năm câu: **nó giải quyết gì, hoạt động ra sao, tác động gì, khác baseline thế nào, và dùng trong thực tế khi nào**. Phần trước toán phải tự đứng vững như một bài giải thích ngắn; phần toán là lượt đọc thứ hai để làm chính xác trực giác, không phải điều kiện để hiểu ý chính.

$ARGUMENTS
