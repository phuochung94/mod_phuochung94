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

## Viền chữ hiện hành — theo ảnh số 4.20

Áp dụng chung cho nhãn giáp, xác suất và mọi trạng thái: màu chữ sáng theo
palette/gradient hiện tại, viền tối sát nét 1px màu 171A10 quanh tám hướng,
kèm bóng đen nhẹ phía dưới. Giữ Warhelios Bold và ý nghĩa các màu hiện hành.
Mẫu settings preview được render lại cùng kiểu viền/bóng. Đã kiểm tra các chuỗi
SPACED/NO PEN/NO HULL/RICOCHET và dấu ? vừa vùng 244px kể cả viền. Chưa thử game.
Backup: development/backups/before_crisp_outline_2026-11-05.zip.

## Font/màu HUD hiện hành — 2026-11-05

Theo yêu cầu mới nhất, dùng Warhelios Bold trích nguyên từ client game, đặt trước PF DIN Max Compressed fallback trong CSS; thay thế yêu cầu giữ font cũ bên dưới. Bóng tối/viền nhẹ giúp đọc trên cảnh trận. Bảng màu sáng hơn áp dụng tại extension install cho Colors và gradient nền: HIGH_CHANCE 9CFF3A, MEDIUM_CHANCE FFC04D, LOW_CHANCE/RICOCHET FF4040, GREY D0D0D0. Giữ nguyên ý nghĩa màu và cơ chế xác suất; extension đặt GRADIENT=True. Mẫu preview dùng cùng font, màu và bố cục; tái tạo mẫu bằng development/render_crosshair_sample.py nếu đổi font/palette, sau đó package. Có 39 test nguồn và 39 test bytecode đạt, gồm test dùng gradient bytecode nền thực.

Đã kiểm tra lỗi preview người dùng báo: file mod đang cài trong game có SHA256 e1b7961ccf2a55683100011e14920f23c7e9cf59b1cb41f28dd22e58c1aac520, 18 file, KHÔNG chứa settingsWindow.swf; trong khi gói đã xuất trước đó có 19 file và có preview. Vì vậy chưa có bằng chứng preview mới lỗi khi chạy; phải thay file trong mods bằng gói mới và khởi động lại client để kiểm chứng. Không tự cài đè game trong tác vụ này. Backup trước font/màu: development/backups/before_bright_hud_2026-11-05.zip. Giữ điểm 2026.

## Xem trước trong cài đặt tâm ngắm gốc

Đã thêm mẫu tĩnh giáp 215 và `72.3% - SPACED` vào vùng AimSettings của game, dùng font/bố cục mod hiện tại. Không tạo menu hay modlist riêng. Overlay trong trận vẫn dùng OpenWG đang cài. File runtime bổ sung: `res/gui/flash/settingsWindow.swf`, được crosshair_preview.py tạo lại từ SWF gốc của client mỗi lần đóng gói, giữ nguyên ActionScript và tag gốc; chỉ thêm bitmap/shape/placement mẫu vào container native. Nếu cấu trúc native thay đổi thì dừng build thay vì dùng lại SWF cũ. Mẫu không tính xuyên thực trong màn hình settings. Chi tiết và giới hạn tại res/development/CROSSHAIR_PREVIEW.md. Chưa kiểm chứng trong game. Giữ backup before_crosshair_preview_2026-11-05.zip và điểm 2026.

## Mod độc lập — không menu/modlist

Yêu cầu mới nhất: mod không đăng ký Aslain, legacy Mods Settings API, modlist hay menu thiết lập. Đã gỡ toàn bộ runtime settings_gui và các thư mục tooltips/translations chỉ phục vụ menu. Cấu hình tích hợp, overlay và tính xuyên giữ nguyên. Chỉ dùng OpenWG Gameface hiện cài trong game để hiển thị; không tự tải/chọn bản khác. ZIP vẫn chứa mod và đúng gói Gameface đang cài.

Package initializer được duy trì tại res/development/source/package_init.py, chỉ khởi tạo core và logger như nền; không import settings_gui. Build hiện biên dịch ba nguồn: shell_info, loader và package initializer. Chạy audit_no_menus.py qua inspect_client.py để kiểm tra init và tham chiếu runtime. Đã đạt 38 test nguồn + 38 test bytecode. Sao lưu trước gỡ menu: res/development/backups/before_remove_menus_2026-11-05.zip; giữ điểm 2026 và upstream. Quy tắc này thay thế mọi mô tả giữ menu legacy/tooltips/translations bên dưới. Không khôi phục menu khi cập nhật upstream.

## Menu thiết lập — bỏ Aslain

Theo yêu cầu người dùng, không đăng ký hoặc import Aslain Settings. Đã bỏ
`settings_gui/aslain_settings.pyc`; initializer được duy trì trong
`development/source/settings_gui_init.py`, chỉ thử legacy_settings và xử lý
khi thiếu legacy API. Build hiện biên dịch ba module duy trì, gồm initializer này.
Vẫn giữ menu legacy Mods Settings API. `tooltips` và `translations` còn được
legacy_settings.pyc và language.pyc tham chiếu, nên không xóa. Đã kiểm tra
initializer khi có/không có legacy, không có import Aslain; 38 test nguồn và
38 test bytecode đạt. Backup trước thay đổi ở
`development/backups/before_remove_aslain_2026-11-05.zip`. Không tự khôi phục
Aslain khi cập nhật upstream. Quy tắc này thay thế mô tả menu cũ bên dưới.

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

# Hồ sơ tùy chỉnh Armor Penetration Calculator

Cập nhật: 2026-11-03. Đây là yêu cầu đã được người dùng chấp thuận cho dự án
pademinune AP Calculator. Khi người dùng đưa bản mới từ nhà phát triển và yêu
cầu áp dụng lại tùy chỉnh, dùng hồ sơ này làm chuẩn; không yêu cầu họ liệt kê lại.
Yêu cầu mới hơn của người dùng được ưu tiên.

## Thiết lập cần khôi phục

| Khóa | Giá trị |
|---|---|
| enabled | true |
| armor_label.enabled | true |
| prob_label.enabled | false (nhãn % cũ; dòng thông tin đạn mới vẫn bật) |
| angle_label.enabled | false |
| angle_label.display_threshold | 0 |
| angle_label.always_white | true |
| colors.gradient | true |
| colorblind.enabled | false |
| track_indicator.enabled | true |
| colors.high_chance | 6BF40D |
| colors.medium_chance | FFAD00 |
| colors.low_chance | E90000 |
| colors.ricochet | E90000 |

Góc luôn hiện khi có dữ liệu va chạm hợp lệ, không cần đạt 70 độ.
Không có dữ liệu thì không tạo góc giả.

Bảng màu rời khi tắt gradient: >80% xanh lá; >60% đến 80% cam;
<=60% đỏ; nảy đạn đỏ. Gradient hiện BẬT: giữ chuyển màu mượt.
Ở bản hiện tại hàm gradient gốc dùng các mốc 7/50/93, còn các mốc 60/80
chỉ áp dụng cho hàm màu rời. Không mô tả gradient như bảng màu rời.
Chữ góc luôn trắng.

## Không dùng file cấu hình ngoài

Vô hiệu hóa đọc và ghi:
`mods/configs/pademinune/Armor Penetration Calculator 2/config.json`.
`load_config()` trả về bản sao DEFAULT_CONFIG; `save_config()` không ghi file
và không tạo thư mục. File cũ không được ghi đè thiết lập tích hợp.
Chỉ sửa cấu hình trong mod khi cần thay đổi mặc định.

## Dòng thông tin đạn đang nạp

Quy tắc mới nhất thay thế quy tắc mọi trạng thái không xuyên đều đỏ bên dưới:
giữ gradient khi có khả năng xuyên HP. Khi không xuyên, nếu đường va chạm có
module (`matInfo.extra` hoặc va chạm module-only) còn có thể tới được theo
sức xuyên tối đa và suy giảm HEAT, dòng hiện cam FFAD00. Đây là khả năng gây
damage module, không cam kết phá module; chưa mô hình HP/saving throw module.
Nếu AP/APCR/HEAT không gây HP và không nhận thấy khả năng module thì đỏ E90000
theo mô hình đường đạn. HE/HESH chưa có mô hình sát thương nổ nên dùng xám khi
không xuyên và không thấy module, tránh khẳng định phát bắn vô ích.
Client gộp `_CRIT_ONLY_SHOT_RESULT` với NOT_PIERCED; không dùng riêng kết quả
trả về đó để phân loại. Phần trăm vẫn là xuyên thân, không phải xác suất phá module.
Hiện có 38 test nguồn và 38 test bytecode.

Quy tắc màu mới nhất: giữ hàm gradient gốc cho xác suất thông thường và SPACED.
Riêng NO PEN, NO HULL, RICOCHET luôn dùng đỏ E90000 (Colors.LOW_CHANCE),
áp dụng mọi loại đạn gồm HE/HESH, thay thế quy tắc cam cho HE/HESH 0% bên dưới.
Đỏ biểu thị không xuyên thân, không kết luận HE/HESH không gây sát thương nổ.
Thiếu dữ liệu vẫn xám. Hiện có 35 test nguồn và 35 test bytecode.

Tinh gọn tiếp theo yêu cầu người dùng: chỉ hiện MỘT trạng thái cạnh phần trăm.
Ưu tiên RICOCHET, chắn không xuyên (NO PEN), chưa đến thân (NO HULL),
xuyên thân bằng 0 (NO PEN), sau cùng SPACED. Không còn ghép nhiều trạng thái.
Màu dòng xác suất: AP/APCR/HEAT không có khả năng gây sát thương HP trực tiếp
theo đường va chạm đang tính dùng LOW_CHANCE (đỏ E90000); không bao gồm damage
xích/module hoặc kết quả máy chủ. RICOCHET giữ đỏ. HE/HESH có 0% xuyên dùng
MEDIUM_CHANCE (cam FFAD00) vì chưa tính sát thương nổ, không kết luận 0 damage.
Dữ liệu chưa biết dùng xám, các xác suất khác giữ gradient. Nhãn giáp vẫn giữ
cách tô màu của nền. Có 34 test nguồn và 34 test bytecode đã đạt; chưa thử game.
Quy tắc một trạng thái này thay thế các ví dụ ghép trạng thái cũ bên dưới.

Yêu cầu đã thực hiện ngày 2026-11-04: dòng chỉ hiện xác suất và trạng thái,
ví dụ `72.3% - SPACED`; không hiện tên đạn hoặc sức xuyên mm. Không có trạng thái
thì chỉ hiện `72.3%`. Giữ `NO PEN`, `NO HULL`, `RICOCHET`, dấu phân cách ` - `,
và `?` khi thiếu dữ liệu. Tắt góc va chạm; vẫn giữ nhãn giáp.

Người dùng xác nhận tên HESH (không phải HEST). HESH được tính theo nhánh HE
và thuộc tính shell thực của client, bao gồm nhánh modern HE khi game chọn,
shieldPenetration và hệ số xuyên chắn; không tự coi là HEAT hay thêm công thức
sát thương nổ riêng. Khả năng này đã có trong nhánh HE; đã bổ sung test riêng
cho HESH xuyên thân, RNG, chắn có khoảng rỗng và chắn không thể xuyên. Test
dùng dữ liệu giả lập theo cấu trúc client, chưa xác nhận bằng bắn HESH trong game.
Hiện có 30 test nguồn và 30 test bytecode. Giữ nguyên kết quả trả về của game.

Nguồn duy trì: `development/source/ap_shell_info.py` và
`development/source/mod_AP_Calculator.py`.

- Dùng shell truyền vào hàm tính phát bắn của game, không dùng loại đạn đang
  chờ nạp. Hỗ trợ các nhánh AP/APCR/HEAT/HE mà game cung cấp trong default và
  modern-HE shot-result; kiểm tra lại các nhánh của bản mới (kể cả HE đặc biệt).
- Ví dụ: `72.3% - SPACED`.
- Không hiển thị loại đạn hoặc số mm trong dòng probability. Dữ liệu fullPiercingPower vẫn dùng cho tính toán, không phải sức xuyên còn
  lại sau lớp chắn. Nhãn giáp chính hiển thị mức xuyên ban đầu cần có.
- Xác suất giữ mô hình phân phối chuẩn giới hạn của mod, dùng độ ngẫu nhiên
  sức xuyên của đúng loại đạn. Đây là ước tính xuyên tại điểm ngắm, không phải
  xác suất bắn trúng hoặc cam kết kết quả từ máy chủ.
- HEAT: xét giáp chắn, hệ số suy giảm của đạn và khoảng rỗng giữa các lớp.
  Với hệ số sức xuyên còn lại scale, cộng armor/scale vào mức xuyên ban đầu
  cần thiết; không chỉ cộng phần sức xuyên trung bình đã mất.
- SPACED: gặp lớp giáp không thuộc giáp thân chính. Không mặc định HEAT gặp
  giáp cách lớp là không xuyên.
- NO PEN: xác suất xuyên hoàn toàn được tính là 0; không đồng nghĩa HE không
  gây sát thương nổ.
- NO HULL: đường va chạm chưa đến giáp thân, ví dụ chỉ trúng xích/bộ phận ngoài.
- RICOCHET: theo helper của game, hiển thị đỏ.
- Dữ liệu không hỗ trợ/không đủ: hiện `?` hoặc ẩn dòng, không bịa ra 0%/100%.
- Giữ xử lý riêng của HE hiện đại và hệ số xuyên giáp chắn từ game.
- Dùng lại dòng probability trong ViewModel, cập nhật trạng thái visible để
  các luồng ẩn tâm, xe bị phá hủy, rời trận cũng ẩn dòng mới.
- Chỉ bổ sung tính toán/hiển thị; giữ nguyên giá trị trả về hàm đánh giá phát
  bắn của game/mod. Cài wrapper một lần, lỗi phần bổ sung không đổi kết quả gốc.
- Chỉ báo xích: bật khi hit_track, hit_body và xác suất >80%, tránh phụ thuộc
  phép so sánh bằng màu endpoint khi đang bật gradient.

## Giao diện

Yêu cầu mới nhất của người dùng: dùng lại font cũ PF DIN Max Compressed Bold.
Đã khôi phục nguyên CSS từ điểm sao lưu 2026 (bao gồm bóng chữ cũ) và bỏ file
Warhelios vừa thêm khỏi runtime. Không áp dụng lựa chọn Warhelios mô tả bên dưới.
Điểm sao lưu 2026 vẫn được giữ nguyên.

Theo ảnh HUD người dùng cung cấp, dùng Warhelios Bold từ client game để chữ
rộng và dễ đọc hơn PF DIN Max Compressed cũ. Font được đóng kèm tại
`gui/AP_Calculator_2/gameface/Warhelios-Bold.ttf`, CSS đặt Warhelios trước,
PF DIN Max Compressed làm fallback; font-weight 700, bóng tối nhẹ. Giữ kích thước,
vị trí nhãn và toàn bộ logic/màu đã chốt. Đây là lựa chọn đối chiếu hình ảnh,
không khẳng định nhận diện chính xác font từ screenshot.
Điểm sao lưu trước thay đổi: `development/backups/2026/project_before_font_change.zip`,
kèm manifest SHA256. Snapshot gồm runtime, nguồn, test và hồ sơ; loại các backup
cũ và thư viện client sinh tạm. Không ghi đè điểm 2026 khi thay đổi tiếp.

`gui/AP_Calculator_2/gameface/APBattleView.css`: dòng thông tin đạn đặt ở
top 204px, width 244px, font-size 15px, line-height 17px, căn giữa và cho
xuống dòng (`white-space: normal`) trong cửa sổ 256x256. Bản mới có bố cục khác
thì điều chỉnh tương đương, tránh chồng lên nhãn giáp/góc hoặc bị cắt chữ.

## Quy trình áp dụng vào bản từ nhà phát triển

1. Giữ hồ sơ này, AGENTS.md, mã nguồn tùy chỉnh, bộ kiểm thử và bản sao mod
   đang dùng trước khi thay thế tệp. Làm việc từ bản mới của tác giả.
2. Kiểm tra phiên bản Python/bytecode, tên và chữ ký hàm shot-result, cấu trúc
   collisionsDetails, shell, material và API Gameface/Wulf. Ưu tiên mã nguồn
   của tác giả; nếu chỉ có .pyc, phân tích/decompile và kiểm tra cấu trúc.
3. Áp dụng thiết lập và vô hiệu hóa persistence như trên. Không dùng lại
   offset bytecode, chỉ số constants/names hoặc chuỗi hex của bản 2.2.0 cho
   bản mới nếu chưa xác minh. Không ghi đè toàn bộ logic mới bằng .pyc cũ.
4. Ghép bộ khởi tạo phần bổ sung vào entry point mới, giữ các bước khởi tạo
   mới của tác giả. Tệp entry point trong development/source của bản 2.2.0
   chỉ là tham chiếu; không thay thế mù quáng entry point mới.
5. Chuyển phần phân tích đạn/HEAT và bố cục sang API mới nếu cần. Giữ sửa lỗi
   và tính năng của tác giả. Nếu không có đủ API, báo rõ phần chưa tương thích.
6. Biên dịch đúng phiên bản Python của game. Với bản 2.2.0 hiện tại dùng
   Python 2.7: chạy `development/build_bytecode.py`. Script này chỉ xây dựng
   hai module bổ sung, KHÔNG tự áp dụng các sửa đổi cấu hình/màu lên mod mới.
7. Chạy kiểm thử nguồn và bytecode. Lệnh hiện tại:
   `python2.7 -B development/tests/test_shell_info.py` và
   `AP_TEST_BYTECODE=1 python2.7 -B development/tests/test_shell_info.py`.
   24 kiểm thử hiện có dùng API game giả lập, không thay cho kiểm thử trong WoT.
8. Khi có client/log, thử đổi đạn, HEAT qua nhiều lớp/khoảng rỗng, trúng xích
   không trúng thân, nảy đạn, HE, chuyển ngắm, xe bị phá hủy và rời trận.
   Phân biệt rõ kiểm thử mô phỏng và xác nhận trong game khi báo kết quả.
9. Xóa .DS_Store/.DStore trong dự án, không theo symlink ra ngoài.
10. Khi được yêu cầu đóng gói, dùng đúng tên cố định
    `pademinune-AP_Calculator-2.2.0.wotmod`, ZIP_STORED (ZIP không nén), đặt
    cạnh thư mục res. Nội dung runtime nằm dưới res/gui và res/scripts.
    Loại AGENTS.md, hồ sơ này, development/, backup, file rác và archive cũ.
    Kiểm tra CRC, cấu trúc res/ và compression type của mọi entry.

## Phạm vi lưu nhớ

Hồ sơ được lưu cùng dự án, không tự động theo một thư mục tải về hoàn toàn
khác. Khi thay cả dự án, giữ/copy AGENTS.md, MOD_CUSTOMIZATIONS.md và development/
sang chỗ mới, hoặc cung cấp đường dẫn dự án này để đọc lại hồ sơ.

## Nguồn tác giả do người dùng cung cấp

Nguồn gốc 2.2.0 trên Windows (người dùng cung cấp 2026-11-03):
`C:\pademinune-AP_Calculator-2.2.0\Armor-Penetration-Calculator-2.2.0`.
Đã kiểm tra `src/res/scripts/client/ap_calculator/debug.py` khai báo 2.2.0.
Người dùng xác nhận nguồn này chỉ phù hợp phiên bản game hiện tại; khi game
cập nhật phiên bản mới, nguồn này sẽ không còn hoạt động. Chỉ giữ làm mốc đối
chiếu lịch sử. Khi cập nhật phải lấy nguồn mod phù hợp client mới, kiểm tra API
game thực tế rồi chuyển các tùy chỉnh sang; không mặc định nguồn 2.2.0 hoặc
snapshot 2.2.1 bên dưới tương thích. Chưa ghi nhận số phiên bản client hiện tại.
Dùng để tham chiếu nền gốc khi bảo trì/cập nhật; không build rồi ghi đè bản tùy chỉnh.
Đây là thư mục ngoài dự án bàn giao, cần giữ riêng khi chuyển máy.
Chi tiết các điểm tham chiếu: `development/UPSTREAM_SOURCE.md`.

Repo: https://github.com/justinnitoi/Armor-Penetration-Calculator.git
Nhánh v2, snapshot commit 97e3b967a3d3465a203c3dab615ee17672ade729
(phiên bản nguồn 2.2.1). Xem development/UPSTREAM_SOURCE.md.
Chưa tự thay runtime 2.2.0 bằng bản nguồn này.
Người dùng đã hủy yêu cầu chặn bắn khi xác suất xuyên bằng 0%.
Không triển khai hoặc áp dụng lại chức năng chặn bắn khi cập nhật mod,
trừ khi người dùng yêu cầu lại. Mã nguồn tác giả vẫn được giữ để bảo trì.

Phân tích chi tiết các điểm phụ thuộc khi game cập nhật: development/GAME_UPDATE_COMPATIBILITY.md.

## Chuyển máy Windows

### Nguồn phát hành OpenWG Gameface

Người dùng cung cấp ngày 2026-11-03:
https://gitlab.com/openwg/wot.gameface/-/releases

Khi cập nhật mod, dùng trang phát hành chính thức này để kiểm tra phụ thuộc
OpenWG Gameface phù hợp với client đích. Không mặc định bản mới nhất tương thích
mọi phiên bản game; đối chiếu ghi chú phát hành và kiểm thử thực tế. Đã mở được
trang nhưng công cụ đọc web không trích xuất được nội dung release, nên chưa
xác nhận phiên bản/asset tương thích. Chưa tải hoặc cài Gameface từ đường dẫn này.

### Client Windows đã được người dùng chỉ định

- Đường dẫn game: `C:\Program Files (x86)\Steam\steamapps\common\World of Tanks\asia`.
- Người dùng cung cấp ngày 2026-11-03 để dùng lại khi cập nhật mod cho phiên bản game mới.
- Khi thực hiện cập nhật, tự dùng đường dẫn này và hồ sơ tùy chỉnh, không hỏi lại
  đường dẫn nếu thư mục vẫn tồn tại. Xác định phiên bản client/thư mục mods thực tế,
  kiểm tra tương thích theo `development/GAME_UPDATE_COMPATIBILITY.md`, giữ mọi
  tùy chỉnh đã duyệt và không thêm chặn bắn 0%.
- Chưa thiết lập tác vụ chạy nền hoặc lịch tự kiểm tra phiên bản mới.

Gói bàn giao dự án: pademinune-AP_Calculator-Windows.zip.
Giữ toàn bộ res/ và development/, không chỉ file .wotmod. Đọc
development/WINDOWS_MIGRATION.md; dùng development/windows_project.py để check,
test, build hai module bổ sung và package. Công cụ tự xác định đường dẫn dự án,
không dùng đường dẫn /Users hoặc /tmp của Mac. Nguồn tác giả 2.2.1 vẫn chỉ là
tham chiếu; chưa tự nâng nền tùy chỉnh đang dùng.
