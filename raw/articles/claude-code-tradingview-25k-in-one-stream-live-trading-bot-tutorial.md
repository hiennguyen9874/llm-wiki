## Tóm tắt nội dung video

Video ghi lại một buổi livestream trong đó tác giả vừa **trình diễn cách kết nối Claude Code với TradingView thông qua MCP**, vừa **nói về cách đưa trading bot vào chạy thực tế**, đồng thời trong lúc livestream đã phát hiện một giao dịch thử nghiệm mang lại **khoảng 25.000 USD lợi nhuận**.

---

## 1. Mục tiêu chính của video

Video có 3 trọng tâm:

1. **Kết nối Claude Code với TradingView**
   - Dùng Claude Code điều khiển trình duyệt/TradingView qua MCP.
   - Cho AI tự tạo và chỉnh sửa indicator ngay trên biểu đồ.

2. **Giải thích tư duy đưa bot giao dịch vào vận hành thật**
   - Tác giả nhấn mạnh rằng vấn đề lớn nhất của trader thủ công là cảm xúc.
   - Bot thắng vì “không có cảm xúc”.

3. **Chia sẻ một ý tưởng chiến lược mới liên quan đến quyền chọn 0DTE**
   - Trong lúc livestream, tác giả kiểm tra một lệnh thử nghiệm và phát hiện lợi nhuận tăng rất mạnh.
   - Từ đó nảy sinh ý định tự động hóa chiến lược này.

---

## 2. Phần trình diễn Claude Code + TradingView

### Những gì tác giả làm
- Tác giả cho Claude Code chạy ở một cửa sổ riêng và để AI thao tác trên TradingView.
- Claude Code:
  - chỉnh sửa script,
  - đẩy indicator lên TradingView,
  - tạo một indicator **SMA 20/40 ribbon**,
  - hiển thị trực tiếp trên chart SPY rồi thử trên các mã khác như Amazon.

### Kết quả
- AI đã tạo được indicator hoạt động thật trên TradingView.
- Tác giả xem đây là bằng chứng rằng:
  - **Claude Code có thể “nói chuyện” với trình duyệt và TradingView**,
  - từ đó có thể nhanh chóng tạo các indicator theo ý tưởng người dùng.

### Ý nghĩa
- Tác giả không quá hứng thú với việc xây nhiều indicator thủ công.
- Điều ông đánh giá cao là:
  - nay có thể **giao việc xây indicator cho AI**,
  - còn bản thân tập trung vào ý tưởng giao dịch và hệ thống.

---

## 3. Thử nghiệm indicator liquidation lines

Tác giả tiếp tục yêu cầu Claude Code tạo một indicator khác:

### Ý tưởng
- Lấy dữ liệu vị thế và mức thanh lý từ API của MoonDev/Mundave.
- Chỉ áp dụng cho vài symbol như:
  - BTC,
  - ETH,
  - HYPE,
  - SOL,
  - Fartcoin.
- Vẽ lên TradingView các đường thể hiện những mức giá gần bị thanh lý nhất.

### Kết quả
- AI tạo ra các liquidation lines trên chart.
- Tác giả thấy tính năng này **đã hoạt động ở mức chứng minh khả năng**, dù chưa hoàn thiện đẹp hoặc đủ chính xác.
- Ông kết luận:
  - đây là dạng ý tưởng “vui”,
  - nhưng điều quan trọng hơn là đã xác nhận được **khả năng tích hợp browser + MCP + TradingView**.

---

## 4. Một số tác vụ kỹ thuật khác trong livestream

Trong khi làm việc với AI, tác giả còn để Claude Code xử lý một số việc kỹ thuật như:
- sửa bot mua token để chỉ mua những token có hậu tố “PUMP”,
- sửa redirect cho các đường dẫn website như:
  - `/vip`,
  - `/learn`,
- xử lý một số lỗi template/backend của trang web,
- cân nhắc cách khôi phục ngữ cảnh khi đang làm dở dự án mà ứng dụng bị refresh.

Phần này thể hiện cách tác giả dùng AI như một “agent” để cùng lúc hỗ trợ:
- code bot,
- làm web,
- thao tác trình duyệt,
- và tích hợp nền tảng giao dịch.

---

## 5. Quan điểm cốt lõi về giao dịch: “Bots don’t feel”

Đây là phần dài và mang tính thuyết trình nhất của video.

### Luận điểm trung tâm
Tác giả lặp lại nhiều lần thông điệp:

- **Con người không hẳn giao dịch tệ, mà là quá con người.**
- **Bot không có cảm xúc, nên bot có lợi thế.**

### Những vấn đề của trader thủ công theo tác giả
Ông cho rằng trader thủ công thường thua vì:
1. **Cảm xúc**
   - sợ hãi,
   - tham lam,
   - FOMO,
   - revenge trade,
   - hy vọng vô căn cứ.
2. **Sàn giao dịch**
   - leverage cao là cái bẫy,
   - sàn kiếm tiền khi người dùng bị thanh lý.
3. **Wall Street / tổ chức lớn**
   - trader nhỏ lẻ đóng vai “cá”,
   - còn tổ chức là “cá mập”.

### Một số ví dụ và so sánh được đưa ra
- Giao dịch thủ công với đòn bẩy giống như ngồi chơi slot machine.
- Kỷ luật của con người có giới hạn như pin điện thoại sẽ cạn dần theo ngày.
- Dùng bot trong trading giống như:
  - dùng calculator khi làm thuế,
  - dùng autopilot trong hàng không,
  - dùng dây chuyền sản xuất thay vì lao động tay chân.

### Trải nghiệm cá nhân
Tác giả kể rằng trước đây mình:
- nhiều lần bị thanh lý,
- giao dịch bằng cảm xúc,
- mất thời gian, mất ngủ, bỏ lỡ các khoảnh khắc đời sống.

Sau này, một bước ngoặt là khi gặp một người giao dịch quy mô rất lớn nhưng chỉ “ngồi chill trên ghế sofa chạy code”, từ đó tác giả nhận ra:
- người đó không nhất thiết thông minh hơn,
- khác biệt là **người đó để hệ thống làm việc thay cho cảm xúc**.

---

## 6. Framework RBI: Research – Backtest – Incubate

Tác giả trình bày framework giao dịch/bot hóa của mình gồm 3 bước:

### 1) Research
- Tìm “edge” thực sự.
- Nguồn gợi ý:
  - sách,
  - paper học thuật,
  - Google Scholar,
  - Market Wizards,
  - Chat With Traders.

### 2) Backtest
- Kiểm tra xem ý tưởng có hiệu quả trong quá khứ không.
- Nếu quá khứ không có edge, không nên đem tiền thật ra thử.
- Mục đích là loại bỏ ý tưởng tệ trước khi chúng làm mất tiền.

### 3) Incubate
- Chạy với **tiền thật nhưng size nhỏ**.
- Không dùng demo vì demo không phản ánh:
  - trượt giá,
  - phí,
  - fill xấu,
  - chậm lệnh,
  - các lỗi vận hành thực tế.

### Quan điểm triển khai
- Không nên đặt cược vào “một bot thần kỳ”.
- Nên xây nhiều bot khác nhau:
  - trend-following,
  - mean-reversion,
  - các edge độc lập,
để giảm rủi ro một bot làm hỏng toàn bộ tài khoản.

---

## 7. Dùng AI để code bot

Một thông điệp lớn khác là:

- **Hiện nay không cần biết code sâu mới có thể làm algo trading.**
- Nếu mô tả được ý tưởng, AI có thể giúp:
  - viết code,
  - backtest,
  - triển khai,
  - tạo công cụ nghiên cứu.

Tác giả cho rằng đây là thời điểm rất thuận lợi để trader chuyển sang giao dịch tự động vì:
- AI ngày càng mạnh,
- rào cản kỹ thuật giảm mạnh.

---

## 8. Phần quảng bá Zoom/khóa học/truy cập hệ sinh thái của tác giả

Một phần lớn transcript là nội dung bán hàng, lặp lại nhiều lần.

### Tác giả quảng bá:
- private Zoom trả phí,
- khóa học Algo Trade Camp,
- AI master classes,
- khóa Solana copy bot / sniper bot,
- khóa Polymarket,
- Quantt/Quantite,
- kho video cũ,
- API key trọn đời,
- GitHub bot và agent,
- ứng dụng Mundave/MoonDev app.

### Các điểm nhấn trong lời chào bán
- Có thể hỏi trực tiếp trong Zoom.
- Không bị quảng cáo chen ngang như stream công khai.
- Có cộng đồng những người cùng xây bot.
- Có replay.
- Có hoàn tiền 90 ngày.
- Tác giả nhấn mạnh giá trị gói là rất lớn so với mức giá bán.

### Dữ kiện và tuyên bố nổi bật
- Tác giả nói mình đã stream công khai 5 năm.
- Nói mình chạy node/validator trên Hyperliquid.
- Nói có học viên từng trả hết **186.000 USD nợ y tế** sau khi áp dụng hệ thống RBI.
- Lấy **Jim Simons** làm hình mẫu, thường nhắc tới con số **31 tỷ USD** tài sản ròng của Simons.

---

## 9. API và dữ liệu được nhắc tới

Tác giả nói gói của mình có API riêng, cung cấp:
- OHLCV,
- order flow,
- liquidation data,
- tick data,
- market data,
- funding data,
- dữ liệu Hyperliquid,
- dữ liệu thanh lý đa sàn,
- dữ liệu lịch sử kéo dài tới khoảng **18 tháng**.

Ông nhấn mạnh rằng loại dữ liệu này nếu mua ngoài có thể rất đắt.

---

## 10. Khoảnh khắc nổi bật nhất: giao dịch 0DTE tạo lợi nhuận lớn

### Diễn biến
Trong lúc đang thuyết trình, tác giả kiểm tra một lệnh thử nghiệm trên Robinhood và phát hiện:
- quyền chọn 0DTE đang tăng rất mạnh,
- lợi nhuận từ vị thế thử nghiệm tăng lên khoảng **1.300% đến 2.000%**,
- sau khi đóng lệnh, tổng lãi thực nhận khoảng **25.000 USD** từ vị thế ban đầu dưới **1.000 USD**.

Transcript có nhiều mốc phần trăm khác nhau do ông vừa kiểm tra vừa phản ứng, nhưng điểm chung là:
- đây là một giao dịch tăng cực mạnh trong thời gian rất ngắn,
- tác giả rất bất ngờ vì kết quả này.

### Phản ứng của tác giả
- Ông thừa nhận việc thoát lệnh đúng lúc có yếu tố **may mắn**.
- Đồng thời điều này làm ông càng tin rằng:
  - nếu có edge,
  - thì phải **tự động hóa**,
vì giao dịch thủ công kiểu này quá cảm xúc và rủi ro.

---

## 11. Ý tưởng chiến lược 0DTE mà tác giả đang nghiên cứu

### Ý tưởng sơ bộ
Tác giả đang thử một thesis liên quan đến quyền chọn **zero-day-to-expiry (0DTE)**:
- thị trường/đám đông thường bị cuốn theo hướng giá đang chạy,
- nhà đầu tư nhỏ lẻ thường thua với 0DTE,
- vì vậy có thể thử chiến lược **đi ngược đám đông**.

Ví dụ:
- nếu tâm lý cực kỳ bullish và giá intraday đang tăng mạnh, có thể mua **put 0DTE**;
- nếu tâm lý cực kỳ bearish và giá intraday đang giảm mạnh, có thể mua **call 0DTE**.

### Điều tác giả tự thừa nhận
- Hiện mới là **ý tưởng đang test bằng tay**.
- Chưa phải edge đã được chứng minh.
- Kết quả lớn hôm đó mới là một ví dụ đơn lẻ.
- Cần backtest đúng cách và loại bỏ yếu tố cảm xúc.

### Yêu cầu nghiên cứu với AI
Tác giả yêu cầu AI:
- tìm paper học thuật liên quan,
- phản biện giả thuyết,
- xác định liệu retail thua trên 0DTE như thế nào,
- phân tích lại thesis theo hướng:
  - không chỉ là “mua put chống retail call”,
  - mà là **mua phần tail protection đang bị định giá sai ở cực điểm tâm lý**,
- đề xuất quy trình:
  1. backtest tín hiệu miễn phí trước,
  2. chỉ khi tín hiệu ổn mới mua dữ liệu options lịch sử,
  3. rồi mới sang paper trading / live nhỏ.

### Kết luận tạm thời trong video
- Ý tưởng **hai chiều (bidirectional contrarian)** được AI đánh giá là hợp lý hơn bản một chiều.
- Nhưng câu hỏi lớn chưa giải quyết là:
  - edge có đủ lớn để vượt qua **theta decay, spread, phí, slippage** của 0DTE hay không.

---

## 12. So sánh Robinhood/Public với Interactive Brokers cho 0DTE

Tác giả tiếp tục yêu cầu AI phân tích chi phí giao dịch 0DTE trên các broker.

### Nội dung phân tích
AI mô hình hóa:
- tài khoản khoảng **25.000 USD**,
- mỗi lệnh khoảng **1.000 USD**,
- 1 lệnh/ngày,
- lợi nhuận giả định khoảng **5%/tháng**,
- so sánh đường cong P&L sau khi tính:
  - commission,
  - payment for order flow,
  - spread,
  - rebate.

### Kết quả chính
- Chênh lệch chi phí giữa Public và Interactive Brokers có tồn tại, nhưng:
  - mức khác biệt chỉ khoảng vài trăm đến khoảng 1.000 USD/năm tùy giả định.
- Tác giả kết luận yếu tố quyết định không phải phí thuần túy, mà là:
  - **Interactive Brokers đã có sẵn hạ tầng code**,
  - còn Public sẽ phải xây tích hợp mới từ đầu.

### Kết luận thực dụng của tác giả
- Tạm thời ưu tiên **Interactive Brokers**.
- Nếu Public tài trợ thì có thể cân nhắc build cho Public.

---

## 13. Quan điểm cuối video về 0DTE

Sau khi trải qua giao dịch lãi lớn, tác giả rút ra:
- 0DTE cực kỳ biến động và nguy hiểm.
- Giao dịch thủ công gần như không phù hợp vì:
  - dễ bị cuốn theo chart,
  - dễ quá tay,
  - chỉ cần một ngày tilt là có thể mất nhiều.
- Nếu tiếp tục theo hướng này, ông muốn:
  - **xây bot**,
  - đặt giới hạn cứng,
  - loại bỏ can thiệp cảm xúc.

---

## 14. Thông điệp tổng thể của video

### Về công cụ
- Claude Code + MCP + TradingView có thể dùng để:
  - viết indicator,
  - thao tác trình duyệt,
  - tích hợp API,
  - hỗ trợ xây hệ thống nghiên cứu và giao dịch.

### Về giao dịch
- Tác giả cho rằng vấn đề lớn nhất của trader không phải thiếu thông minh mà là **không thoát khỏi cảm xúc**.
- Giải pháp ông theo đuổi là:
  - nghiên cứu edge,
  - backtest,
  - chạy bot nhỏ,
  - mở rộng thành hệ thống nhiều bot.

### Về cơ hội mới
- Giao dịch 0DTE lãi lớn trong livestream khiến tác giả xem đây là một hướng đáng tiếp tục nghiên cứu.
- Tuy vậy, ông cũng nhiều lần nhấn mạnh:
  - kết quả đó có phần may mắn,
  - chưa đủ để khẳng định chiến lược,
  - cần kiểm chứng bằng dữ liệu và tự động hóa.

---

## Tóm tắt ngắn gọn nhất

Đây là một livestream kết hợp giữa:
- **demo kỹ thuật**: dùng Claude Code kết nối TradingView qua MCP để tạo indicator và thao tác trực tiếp trên chart;
- **bài giảng tư duy giao dịch tự động**: khẳng định bot thắng vì không có cảm xúc, giới thiệu framework **RBI = Research, Backtest, Incubate**;
- **khám phá chiến lược mới**: trong lúc stream, tác giả phát hiện một lệnh thử nghiệm 0DTE mang về khoảng **25.000 USD**, từ đó quyết định nghiên cứu và bot hóa sâu hơn ý tưởng giao dịch ngược đám đông trên quyền chọn ngắn hạn.
