# Thiết lập đã thống nhất với người dùng

Đọc `COMPATIBILITY.md` trước khi bảo trì hoặc đóng gói mod. Đây là bộ nhớ dự án
để áp dụng cho các lần làm việc tiếp theo trong thư mục này.

- Xuất thêm ZIP phân phối `UNZIP-phuochung94.moe_calculator-ASIA <phiên bản> #<build>.zip`
  tại thư mục xuất đã thống nhất. ZIP chứa mod và OpenWG Gameface dưới dạng
  **hai file .wotmod riêng ở gốc**, không gộp Gameface vào mod. Gameface là phụ
  thuộc riêng, phải kiểm tra/cập nhật bản tương thích khi game đổi phiên bản;
  **không cố định 1.2.2**, không chỉ đổi tên phiên bản dependency. Đối chiếu
  nguồn phát hành chính thức và giao diện thực tế; nếu cần quyền ghi khi cập
  nhật/cài dependency phải tuân thủ sandbox. `tools/bundle_zip.py` dùng đúng
  file dependency và hash đã xác minh trong báo cáo client. Không mặc nhiên
  thay dependency đang cài trong game chỉ để chuẩn bị ZIP.

- Khi người dùng bấm hoặc nhắn **“cập nhật mod”**, thực hiện toàn bộ quy trình
  ngay trong lần yêu cầu đó: đọc phiên bản/build game thực tế; kiểm tra tương
  thích code mod, API ASIA, tài nguyên và OpenWG Gameface; sửa code nếu cần;
  kiểm chứng lại rồi đóng gói `.wotmod` theo phiên bản game hiện tại vào thư
  mục xuất đã thống nhất. Giữ tên phuochung94 và chế độ mặc định không menu.
  Sao lưu trước khi ghi đè và báo kết quả cùng giới hạn kiểm thử. Không chỉ
  đổi tên gói hoặc dùng lại kết quả kiểm tra cũ. Không cần hỏi lại ý nghĩa lệnh.
  Lệnh này không tạo lịch nền và không mặc nhiên yêu cầu cài vào thư mục game.

- Mod mục tiêu: **14th_ua’s MoE Calculator 8.0.0**, tính vạch/dấu nòng MoE.
  Không phải AP Calculator, bất kể tên thư mục cha.
- Tên hiển thị: **phuochung94's MoE Calculator**. Theo yêu cầu mới, ID, tên
  file JSON, thư mục Gameface, namespace cache và mọi tham chiếu runtime cũng
  dùng **phuochung94**. `tools/rename_namespace.py` thực hiện chuyển đổi nhất
  quán, kiểm tra đầy đủ marshal Python 2.7. Giữ ghi công tác giả gốc trong
  metadata và backup lịch sử. Không đổi tên thư mục workspace đang mở.
- Yêu cầu mới: **chạy với cấu hình mặc định cố định, không có menu thiết lập,
  không cho thay đổi thiết lập**. Không đọc cấu hình cũ; khóa kéo vị trí,
  phím đổi chế độ và override theo xe. Giữ mặc định gốc: garage, overlay trận
  và dòng hỗ trợ bật; thanh tiến độ riêng tắt. Không tự bật thanh này.
  `tools/fix_defaults.py` áp dụng bản sửa; giữ chế độ này khi bảo trì bản mới.
- Game: `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`.
- Đọc `version.xml` của game để xác định realm, phiên bản và build thực tế.
  Mốc đã kiểm tra: **ASIA 2.4.1.1 #988**; không cố định mốc này cho bản mới.
- Khi người dùng yêu cầu tương thích phiên bản game mới, phân tích dữ liệu/API
  client và **sửa code mod** cần thiết. Không chỉ đổi tên gói, chép sang thư mục
  game mới hoặc chờ tác giả phát hành thay cho công việc sửa code.
- Kiểm tra phụ thuộc OpenWG Gameface theo nguồn người dùng cung cấp:
  https://gitlab.com/openwg/wot.gameface/-/releases . Không mặc định một bản
  Gameface cũ vẫn tương thích hoặc đủ yêu cầu của mod.
- Nguồn mod tham khảo: https://github.com/drizzer14/moe-calculator .
  Không tự thay toàn bộ bản 8.0.0 bằng nhánh mới khi chỉ cần sửa tương thích.
- Bản ASIA đã sửa hằng `REGION` trong `adapter/moe_wgapi.pyc` từ `eu` sang
  `asia`. Giữ đúng vùng và tránh dùng ngưỡng/cache EU cho game ASIA.
- Python phía game là **2.7**. Không biên dịch `.pyc` bằng Python 3.
  `tools/build_asia.py` chạy bằng Python 3 nhưng chỉ đọc/sửa hằng marshal của
  bytecode 2.7 hiện có và đóng gói; không phải trình chuyển đổi API tự động.
- Sau khi sửa, kiểm tra phần đã thay đổi, kiểm tra cấu trúc bytecode, tài nguyên,
  API và gói. Phân biệt kiểm tra tĩnh/API với xác nhận chạy trong game. Không
  khẳng định chạy được trong garage/trận nếu chưa kiểm thử thực tế.
- File `.wotmod` xuất trực tiếp tại **`C:\pademinune-AP_Calculator-2.2.0\`**,
  tên **`phuochung94.moe_calculator-ASIA <phiên bản> #<build>.wotmod`**.
  Báo cáo, backup và tài liệu vẫn ở workspace/`dist/`. Thư mục xuất ở ngoài
  writable root hiện tại; dùng escalation khi ghi nếu quyền chưa được cấp.
  Ví dụ: `phuochung94.moe_calculator-ASIA 2.4.1.1 #991.wotmod`.
- Định dạng là **ZIP không nén, phương thức Store / ZIP_STORED (0)**, đuôi
  `.wotmod`, chứa `res/` và `meta.xml` ở gốc. Không đưa tools, source tham khảo,
  báo cáo hoặc backup vào gói. Kiểm tra CRC, phương thức nén và nội dung gói.
- Sao lưu trước khi sửa/ghi đè; giữ cấu hình người dùng. Ghi lại thay đổi,
  phiên bản game, kiểm chứng và giới hạn trong báo cáo cạnh gói.
- Lần kiểm tra trước: API ASIA trả HTTP 200/status ok; 39 module Python và
  67 file đóng gói đã được kiểm tra. Chưa kiểm thử garage/trận và chưa cài mod
  hoặc Gameface vào game. Đây là kết quả lịch sử, phải kiểm tra lại khi cần.
- **Không có lịch tự động theo dõi/cập nhật**: người dùng đã xác nhận chỉ ghi
  nhớ đường dẫn và quy trình để sau này yêu cầu sửa. Không tạo lại automation
  nếu chưa có yêu cầu mới rõ ràng.
- Mặc định chuẩn bị bản sửa và gói trong workspace. Ghi vào thư mục game phải
  tuân thủ quyền filesystem, chỉ khi game đóng và có sao lưu thích hợp.
