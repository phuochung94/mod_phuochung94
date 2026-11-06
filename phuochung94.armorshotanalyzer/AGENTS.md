## Cải thiện độ chính xác sau phê duyệt reviewer — theo từng roll

Yêu cầu mới nhất thay thế công thức cố định ±25% và mất xuyên HEAT theo phát trung bình: dùng shell.piercingPowerRandomization thực của viên đạn hiện tại. Overlay truyền toàn bộ dải roll theo remaining(p)=scale*p-spent; mỗi lớp giáp tạo ngưỡng (spent+armor)/scale, khoảng rỗng HEAT nhân cả scale và spent với hệ số còn lại. Tích phân mô hình chuẩn được chuẩn hóa trong dải RNG thật; RNG=0 tính xác định, dữ liệu RNG lỗi/thiếu không giả định 25%. Đây vẫn là mô hình ước tính, không tuyên bố phân phối server hay damage chính xác. Nhãn giáp trở lại mức xuyên BAN ĐẦU cần có, không còn giáp ảo mất xuyên theo phát trung bình. Module/xích dùng cùng ngân sách roll. Giữ nguyên hàm client, đầu vào/kết quả/exception, cleanup, không telemetry và mọi tùy chỉnh hiển thị. Đã bỏ helper armorshotanalyzer_math.pyc cũ không còn tham chiếu để tránh sót công thức cố định trong runtime. Chi tiết res/development/ROLL_AWARE_ESTIMATE.md. 70 test nguồn + 70 test bytecode đạt; có đối chiếu mô phỏng tiến độc lập 4096 roll/ca và kiểm tra RNG hẹp/rộng/0, giáp nhiều lớp, khoảng rỗng và module. Backup before_shell_roll_accuracy_2026-11-06.zip, giữ điểm 2028. Reviewer đã phê duyệt các sửa privacy/client/cleanup trước đó; chưa gửi lại bản cải tiến mới và chưa thử trong game.

## Kiểm toán gói giao cuối — 2026-11-06

Đã rà soát trực tiếp file xuất .wotmod và ZIP, không chỉ nguồn: 62 test nguồn, 62 test bytecode workspace và 62 test bytecode giải nén từ chính gói xuất đều đạt. Không có logger/HTTP telemetry, có đối chiếu 5 nguồn với bytecode, kiểm CRC/ZIP_STORED và so nguyên byte bundle. Giữ nguyên thân hàm/kết quả client, phân tích overlay riêng. Cleanup được bổ sung session riêng cho callback sự kiện, retry unsubscribe khi host tạm lỗi và đóng window kể cả lỗi hide/destroy label. Không ghi đè hook của mod cài sau. Xem res/development/FINAL_REVIEW_2026-11-06.md và client_inspection/final_release_review.json để lấy SHA256, kết quả và cách tái kiểm toán. Có bản trả lời reviewer tiếng Anh ở res/development/REVIEWER_RESPONSE.md, CHƯA gửi. Chưa kiểm thử game thật; phải restart client khi thay bản cũ. Giữ điểm 2028. Khi cập nhật/rebuild tiếp, phải chạy lại kiểm toán gói và cập nhật report/hash, không coi hash hiện tại là xác nhận cho gói đã thay đổi.

## Quyền riêng tư và phép tính tham chiếu mới nhất — 2026-11-06

Không thu thập, lưu thống kê người dùng hoặc gửi dữ liệu khi chưa có sự đồng ý rõ ràng trước của người dùng. Áp dụng cả mã upstream và phụ thuộc bên thứ ba; chỉ công bố mô tả không thay cho opt-in. Hiện không có đồng ý cho telemetry/analytics hoặc gửi tên người chơi, server, tài khoản. Giữ runtime không logger/network reporting theo PRIVACY.md; không khôi phục khi cập nhật.

Dùng phép tính overlay của file người dùng cung cấp Downloads/pademinune-AP_Calculator-2.2.0.wotmod (SHA256 0fcf470511febe755b6b3996210a0430d00af0f5fdc05ec1bc4d389fa99823aa): Gaussian cố định 75%-125%, HEAT cộng suy giảm sức xuyên trung bình theo khoảng rỗng thay cho armor/scale. Nhãn giáp nay là giáp hiệu dụng ảo theo mod tham chiếu, không phải ngưỡng xuyên ban đầu giải ngược trước đây. Giữ điều kiện module/góc/hiển thị đã duyệt, xử lý thiếu dữ liệu an toàn. Chỉ lấy tính toán; tuyệt đối không nhập logger/menu/initializer/hook thay thế client từ bản gốc. Hàm client thật và kết quả/exception vẫn được giữ nguyên, có cleanup unload. Chi tiết res/development/REFERENCE_CALCULATION.md. Đạt 58 test nguồn + 58 test bytecode, có đối chiếu 9 ca lớp giáp và 36 điểm Gaussian với bytecode gốc. Backup before_reference_math_2026-11-06.zip; giữ điểm 2028. Quy tắc này thay thế yêu cầu công thức HEAT armor/scale và RNG thay đổi theo shell trong hồ sơ cũ.

## Sửa theo reviewer — 2026-11-06

Bỏ hoàn toàn runtime telemetry: xóa armorshotanalyzer_logger.pyc và import/logger event HTTP. Không gửi tên người chơi, server hay phiên bản mod; không tự khôi phục khi cập nhật upstream. Core initializer không tự cài hook. Loader init/fini quản lý rõ vòng đời. armorshotanalyzer_hooks hiện chỉ chứa wrapper vòng đời và đăng ký/hủy sự kiện trận, không còn bản sao thuật toán phát bắn. Shell-info gọi hàm client đang hoạt động trước, với đúng đối tượng đầu vào, giữ nguyên kết quả/exception; phân tích overlay riêng sau đó và không tiêu thụ iterator đầu vào. Unload phục hồi descriptor nếu vẫn thuộc mod, không ghi đè hook cài sau bởi mod khác; đóng window, hủy player-event subscriptions; wrapper cũ còn bị giữ trong chuỗi sẽ vô hiệu bằng session guard. Build hiện duy trì 5 nguồn (package/core initializer, loader, hooks và shell-info). Đạt 56 test nguồn + 56 test bytecode, có đối chiếu thân hàm client thực trong môi trường giả lập và kiểm thử cleanup. Chi tiết REVIEW_FIXES_2026-11-06.md. Phải khởi động lại client khi thay bản bị reviewer từ chối để bỏ hook/telemetry cũ còn trong bộ nhớ. Chưa thử game hoặc gửi lại reviewer. Backup before_review_fixes_2026-11-06.zip; giữ điểm 2028. Quy tắc này ưu tiên hơn mọi mô tả giữ logger hoặc ghi đè thuật toán cũ bên dưới.

## Dấu module và viền cùng tông hiện hành

NO HULL nhưng có khả năng damage module/xích: hiện dấu - màu cam FFC04D ở nhãn giáp; vẫn ẩn trạng thái, phần trăm và góc không hợp lệ. Không coi mọi NO HULL là damage module. Với nhãn đang hiển thị, viền được tính động từ màu chữ: mỗi kênh RGB nhân 0.25 và làm tròn, áp dụng cả gradient; trắng thành xám đậm. Giữ viền sát nét 1px quanh tám hướng và bóng đen nhẹ. Mẫu preview được render cùng quy tắc viền màu. Đã đạt 45 test nguồn + 45 test bytecode và kiểm tra JavaScript màu/visibility. Backup: res/development/backups/before_tinted_outline_2026-11-05.zip. Quy tắc này thay thế viền tối cố định và hành vi ẩn hết nhãn ở NO HULL có module trong mô tả cũ.

## Hiển thị hiện hành — ẩn toàn bộ trạng thái

Theo yêu cầu mới nhất, ẩn toàn bộ dòng probability/status trong trận và mẫu xem trước, gồm SPACED/NO PEN/NO HULL/RICOCHET/?. Giữ nhãn giáp và góc chạm trắng khi có dữ liệu hợp lệ; giữ font, viền và bóng chữ. Vẫn tính xác suất, phân loại trạng thái và module nội bộ để tô màu nhãn giáp và điều khiển chỉ báo xích. Ghi đè màu nhãn giáp theo kết quả phân loại khi nhãn được hiển thị (gradient/cam/đỏ/xám), không cần chữ trạng thái. Vô hiệu hóa row ở logic Python và CSS để tránh sót chữ. Preview chỉ có giáp 215 và góc mẫu 45 độ. Đạt 44 test nguồn và 44 test bytecode. Backup: res/development/backups/before_hide_status_2026-11-05.zip. Quy tắc này thay thế các ví dụ hiển thị chữ trạng thái bên dưới.

## Hiển thị hiện hành — trạng thái và góc chạm

Theo yêu cầu mới nhất: ẩn số phần trăm xuyên khỏi dòng thông tin; chỉ hiển thị SPACED/NO PEN/NO HULL/RICOCHET (một trạng thái ưu tiên), thiếu dữ liệu hiện ?, không có trạng thái thì ẩn dòng. Vẫn tính xác suất đầy đủ để tô màu và điều khiển chỉ báo xích. Bật góc chạm màu trắng với viền tối như HUD; có dữ liệu góc hợp lệ thì hiện kể cả 0 độ, không tạo góc giả cho va chạm chưa đến thân/thiếu dữ liệu. Dùng hitAngleCos thực cho hiển thị, độc lập với cờ tính độ nghiêng của vật liệu. Mẫu settings hiện giáp 215, trạng thái SPACED và góc mẫu 45 độ, không có %. Giữ font, palette, gradient và cơ chế sát thương đã chốt. Đạt 42 test nguồn và 42 test bytecode. Backup trước thay đổi: res/development/backups/before_status_angle_2026-11-05.zip. Quy tắc này thay thế yêu cầu tắt góc và các ví dụ có % ở hồ sơ cũ bên dưới.

## Font/màu HUD hiện hành — 2026-11-05

Theo yêu cầu mới nhất, dùng Warhelios Bold trích nguyên từ client game, đặt trước PF DIN Max Compressed fallback trong CSS; thay thế yêu cầu giữ font cũ bên dưới. Bóng tối/viền nhẹ giúp đọc trên cảnh trận. Bảng màu sáng hơn áp dụng tại extension install cho Colors và gradient nền: HIGH_CHANCE 9CFF3A, MEDIUM_CHANCE FFC04D, LOW_CHANCE/RICOCHET FF4040, GREY D0D0D0. Giữ nguyên ý nghĩa màu và cơ chế xác suất; extension đặt GRADIENT=True. Mẫu preview dùng cùng font, màu và bố cục; tái tạo mẫu bằng development/render_crosshair_sample.py nếu đổi font/palette, sau đó package. Có 39 test nguồn và 39 test bytecode đạt, gồm test dùng gradient bytecode nền thực.

Đã kiểm tra lỗi preview người dùng báo: file mod đang cài trong game có SHA256 e1b7961ccf2a55683100011e14920f23c7e9cf59b1cb41f28dd22e58c1aac520, 18 file, KHÔNG chứa settingsWindow.swf; trong khi gói đã xuất trước đó có 19 file và có preview. Vì vậy chưa có bằng chứng preview mới lỗi khi chạy; phải thay file trong mods bằng gói mới và khởi động lại client để kiểm chứng. Không tự cài đè game trong tác vụ này. Backup trước font/màu: development/backups/before_bright_hud_2026-11-05.zip. Giữ điểm 2026.

## Xem trước trong cài đặt tâm ngắm gốc

Đã thêm mẫu tĩnh giáp 215 và `72.3% - SPACED` vào vùng AimSettings của game, dùng font/bố cục mod hiện tại. Không tạo menu hay modlist riêng. Overlay trong trận vẫn dùng OpenWG đang cài. File runtime bổ sung: `res/gui/flash/settingsWindow.swf`, được crosshair_preview.py tạo lại từ SWF gốc của client mỗi lần đóng gói, giữ nguyên ActionScript và tag gốc; chỉ thêm bitmap/shape/placement mẫu vào container native. Nếu cấu trúc native thay đổi thì dừng build thay vì dùng lại SWF cũ. Mẫu không tính xuyên thực trong màn hình settings. Chi tiết và giới hạn tại res/development/CROSSHAIR_PREVIEW.md. Chưa kiểm chứng trong game. Giữ backup before_crosshair_preview_2026-11-05.zip và điểm 2026.

## Mod độc lập — không menu/modlist

Yêu cầu mới nhất: mod không đăng ký Aslain, legacy Mods Settings API, modlist hay menu thiết lập. Đã gỡ toàn bộ runtime settings_gui và các thư mục tooltips/translations chỉ phục vụ menu. Cấu hình tích hợp, overlay và tính xuyên giữ nguyên. Chỉ dùng OpenWG Gameface hiện cài trong game để hiển thị; không tự tải/chọn bản khác. ZIP vẫn chứa mod và đúng gói Gameface đang cài.

Package initializer được duy trì tại res/development/source/package_init.py, chỉ khởi tạo core và logger như nền; không import settings_gui. Build hiện biên dịch ba nguồn: shell_info, loader và package initializer. Chạy audit_no_menus.py qua inspect_client.py để kiểm tra init và tham chiếu runtime. Đã đạt 38 test nguồn + 38 test bytecode. Sao lưu trước gỡ menu: res/development/backups/before_remove_menus_2026-11-05.zip; giữ điểm 2026 và upstream. Quy tắc này thay thế mọi mô tả giữ menu legacy/tooltips/translations bên dưới. Không khôi phục menu khi cập nhật upstream.

## Gói ZIP kèm OpenWG — 2026-11-05

Mỗi lần package/build thành công phải xuất cả mod `.wotmod` và `UNZIP-phuochung94.armorshotanalyzer-<REALM> <VERSION> #<BUILD>.zip` tại thư mục xuất đã chốt. ZIP chứa đúng hai file ở cấp gốc: mod vừa tạo và nguyên file `net.openwg.gameface_<version>.wotmod` lấy từ mods/<phiên_bản_client>/ của game. ZIP ngoài dùng nén thông thường; mod bên trong vẫn ZIP_STORED. Tự kiểm tra CRC, cấu trúc và đối chiếu nguyên byte cả hai file; không thêm tài liệu/dev/backup. Nếu không tìm được đúng một gói Gameface đã cài cho client đích thì dừng đóng gói, không tự chọn bản mơ hồ. Việc đóng kèm không thay thế kiểm chứng tương thích Gameface trong game.

## Namespace hiện hành — ArmorShotAnalyzer

Đã đổi tên file/thư mục runtime theo yêu cầu người dùng. Package Python là `armorshotanalyzer`; các module `ap_*.pyc` đổi thành `armorshotanalyzer_*.pyc`. GUI ở `res/gui/ArmorShotAnalyzer/`; các file `APBattleView.*` đổi thành `ArmorShotAnalyzerBattleView.*`. Khai báo resource ở `res/gui/gen_resources/armorshotanalyzer.json`, ID `R.mods.armorshotanalyzer.views.ArmorShotAnalyzerBattleView`. Nguồn phần bổ sung là `res/development/source/armorshotanalyzer_shell_info.py`. File loader vẫn `mod_armorshotanalyzer.pyc`. Quy tắc này thay thế yêu cầu giữ namespace cũ bên dưới. Tên gói vẫn `phuochung94.armorshotanalyzer-<REALM> <VERSION> #<BUILD>.wotmod`. Giữ đường dẫn dự án, thư mục xuất, game, upstream và backup lịch sử.

Đã sao lưu trước đổi tên ở `res/development/backups/before_namespace_rename_2026-11-05.zip`; điểm sao lưu 2026 không thay đổi. Bytecode nền được đổi tên symbol/chuỗi tham chiếu bằng cấu trúc CodeType Python 2.7, giữ nguyên instruction và dữ liệu không phải tên. Chạy `inspect_client.py --run res/development/audit_namespace.py` để kiểm tra import/resource và đối chiếu 15 module nền với backup. Không chạy lại script migration một lần rename_namespace.py trên cây đã chuyển đổi.

## Tên hiện hành — 2026-11-05

Tên gói: `phuochung94.armorshotanalyzer-<REALM> <VERSION> #<BUILD>.wotmod`, hiện là `phuochung94.armorshotanalyzer-ASIA 2.4.1.1 #991.wotmod`. Xuất tại `C:\pademinune-AP_Calculator-2.2.0\`. Thay thế mọi tên gói cũ bên dưới. File khởi chạy hiện là `res/scripts/client/gui/mods/mod_armorshotanalyzer.pyc`; nguồn duy trì `res/development/source/mod_armorshotanalyzer.py`. Không đóng kèm entry point mod_AP_Calculator.pyc cũ. Giữ namespace ap_calculator và resource AP_Calculator_2 để bảo toàn liên kết runtime; không đổi tên thư mục dự án hay đường dẫn game.

Người dùng cũng cho phép cụm “cập nhật mod” thực thi quy trình kiểm tra phiên bản game, kiểm tra tương thích, sửa nếu cần, test và đóng gói; không cần nói thêm “làm việc” cho chính quy trình này. Các yêu cầu khác vẫn chờ “làm việc”.

## Quy tắc chờ lệnh thực thi của người dùng

Chỉ thực thi công việc hoặc thay đổi dự án khi người dùng nói rõ “làm việc”. Trước lệnh này, chỉ ghi nhận yêu cầu, giải thích hoặc làm rõ trong hội thoại; không chạy công cụ, sửa file, build, test, đóng gói, cài đặt hoặc xóa file cho các yêu cầu đang chờ. Lệnh “làm việc” cho phép thực hiện nhóm yêu cầu đã ghi nhận; khi hoàn tất, các yêu cầu mới lại phải chờ lệnh “làm việc”. Yêu cầu hiện tại “lưu vào bộ nhớ” cho phép ghi chính quy tắc này vào hồ sơ, không cho phép thực hiện các công việc khác.

## Thư mục xuất gói hiện hành

Người dùng yêu cầu lưu file .wotmod xuất ra tại `C:\pademinune-AP_Calculator-2.2.0\`, thay thế chỉ dẫn đặt gói trong root dự án Windows ở bên dưới. Tên vẫn là `AP_Calculator-<REALM> <VERSION> #<BUILD>.wotmod`, đọc từ client game. Công cụ windows_project.py xuất trực tiếp vào thư mục này sau khi kiểm tra gói.

## Quy tắc tên gói hiện hành — theo phiên bản game

Người dùng thay thế quy tắc 2.x.0: tên gói là `AP_Calculator-<REALM> <VERSION> #<BUILD>.wotmod`. Ví dụ client hiện tại: `AP_Calculator-ASIA 2.4.1.1 #988.wotmod`. Đọc realm và version từ version.xml của thư mục game đã lưu mỗi lần đóng gói; không tăng số phiên bản mod riêng. Quy tắc này ưu tiên hơn mọi tên cố định hoặc tăng dần trong hồ sơ cũ bên dưới. Đóng gói lại cho cùng client sẽ thay gói cùng tên sau khi kiểm tra thành công. Giữ ZIP_STORED, runtime dưới res/, loại tài liệu/development/backup/rác. Tên theo client không thay thế kiểm chứng tương thích trong game.

## Quy tắc đóng gói mới — 2026-11-03

Tên gói là `pademinune-AP_Calculator-2.x.0.wotmod`, x tăng dần qua mỗi lần đóng gói thành công. Quy tắc này thay thế mọi yêu cầu tên cố định 2.2.0 bên dưới hoặc trong hồ sơ cũ. Công cụ windows_project.py chọn x lớn hơn số lớn nhất của các gói hiện có trong root (mốc tối thiểu 2); giữ các gói trước để duy trì thứ tự. Đã tạo gói diễn tập 2.3.0 ngày 2026-11-03; gói tiếp theo là 2.4.0. Đây là phiên bản gói tùy chỉnh, không khẳng định phiên bản upstream hoặc tương thích game. Giữ ZIP_STORED và chỉ runtime dưới res/.

Khi người dùng yêu cầu cập nhật, tự tham chiếu client tại `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`, kiểm tra API, cập nhật mod và đóng gói, giữ các tùy chỉnh đã duyệt. Nguồn mod cũ chỉ dùng đối chiếu khi cần. Chưa có lịch chạy nền.

# Windows project handoff

Before working, read res/AGENTS.md, res/MOD_CUSTOMIZATIONS.md and res/development/WINDOWS_MIGRATION.md. Preserve all approved customizations when updating upstream. Zero-penetration fire blocking was canceled; do not implement it. Automatically remove .DS_Store and .DStore within this project without following symlinks outside it.

For packaging create pademinune-AP_Calculator-2.2.0.wotmod in this directory using ZIP_STORED with runtime files under res/. Exclude instructions, development, backups and junk. Prefer res/development/windows_project.py package. This ZIP handoff is a project backup, not a mod installation directory.

## Quy tắc phát hành 2026-11-07 (ưu tiên hiện hành)
ZIP UNZIP dùng ZIP_STORED, chứa đúng hai file mod và OpenWG đang cài. Tên file dùng phiên bản client. Số r tăng một khi nội dung runtime thay đổi; đóng lại cùng nội dung giữ số r. Ghi số đó trong changelog và log khởi động trước khi build. Công cụ đối chiếu release_record.json và từ chối số sai.
