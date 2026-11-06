# Kiểm tra tương thích sau cập nhật World of Tanks

Phân tích tĩnh ngày 2026-11-03, dựa trên nguồn tác giả nhánh v2, commit
97e3b967a3d3465a203c3dab615ee17672ade729 (debug.VERSION 2.2.1), cùng phần
mở rộng development/source/ap_shell_info.py của bản tùy chỉnh. Không có bản
client đích cụ thể để so sánh trước/sau; tài liệu này xác định điểm phụ thuộc,
không kết luận một bản WoT mới nào đã tương thích hoặc đã hỏng.

## 1. Ưu tiên cao nhất: hàm tính phát bắn

Mod: src/res/scripts/client/ap_calculator/core/ap_hooks.py.
Game: client/AvatarInputHandler/gun_marker_ctrl.py, _CrosshairShotResults.

Kiểm tra getShotResult, __shotResultDefault, __shotResultModernHE và các helper:
_shouldRicochet, _computePenetrationArmor, _SHELL_EXTRA_DATA,
_CRIT_ONLY_SHOT_RESULT, __isDestructibleComponent,
__collectDebugPiercingData, __sendDebugInfo.

Hai hàm shot-result bị thay thế toàn bộ, không chỉ bọc để lấy dữ liệu.
Nếu game thay logic mà vẫn giữ chữ ký, mod có thể chạy nhưng tính sai hoặc
trả về kết quả tâm ngắm sai. Phải đối chiếu toàn bộ thân hàm của game mới,
chuyển các bước mới vào mod rồi ghép lại các phép theo dõi giáp/góc.
Không chỉ sửa tên/chữ ký cho hết AttributeError/TypeError.

Chữ ký đang dùng:
(cls, gunMarker, collisionsDetails, fullPiercingPower, shell, minPP, maxPP, entity).
getShotResult còn nhận excludeTeam và piercingMultiplier.
Giữ đúng enum SHOT_RESULT từ client/aih_constants.py và cách phân loại
UNDEFINED, NOT_PIERCED, LITTLE_PIERCED, GREAT_PIERCED.

Dấu hiệu: mod không nạp; lỗi AttributeError/TypeError trong python.log;
hoặc sai giáp/%/màu cho một số loại đạn dù không có lỗi.

## 2. Dữ liệu đạn, vật liệu và va chạm

Kiểm tra collision.compName, dist, hitAngleCos, matInfo.
Kiểm tra material.armor, kind, useHitAngle, collideOnceOnly,
vehicleDamageFactor và extra.
Kiểm tra shell.kind, piercingPowerRandomization, armorDamage,
type.piercingPowerLossFactorByDistance, type.shieldPenetration, type.maxDamage,
extra.hasPenetrationLoss, và entity.health.

Xác nhận lại ý nghĩa/đơn vị dist, armor, hitAngleCos và fullPiercingPower;
không chỉ xác nhận thuộc tính còn tồn tại. Kiểm tra thứ tự va chạm, entry/exit
của lớp giáp, vật liệu cần bỏ qua sau lần đầu, và cách nhận biết giáp chính.
Kiểm tra shell.kind mới/đổi tên và có nhánh tính mới ngoài default/modernHE
hay không, nhất là cơ chế đạn hoặc súng đặc biệt.

## 3. HEAT, giáp cách lớp và HE

Các file liên quan: core/ap_hooks.py, core/ap_math.py và
phần tùy chỉnh development/source/ap_shell_info.py.

HEAT: đối chiếu điều kiện bắt đầu jet, cách đặt jetStartDist, suy giảm theo
khoảng rỗng, chặn hệ số <=0 và cách xử lý nảy đạn sau lớp đầu. Phần tùy chỉnh
cần đồng bộ với thứ tự lớp và hệ số của game mới; đang quy đổi mỗi lớp về
mức xuyên ban đầu cần thiết (armor/scale).

HE hiện đại: kiểm tra type.shieldPenetration, hệ số
MODERN_HE_PIERCING_POWER_REDUCTION_FACTOR_FOR_SHIELDS trong
common/items/components/component_constants.py, và cách phân biệt xuyên hoàn
toàn với sát thương nổ không xuyên. 0% xuyên không phải 0 sát thương HE.

Xác suất: nguồn tác giả đang cố định mô hình chuẩn, giới hạn 75%-125%; phần
bổ sung dùng piercingPowerRandomization của đạn. Khi game đổi phân phối RNG,
giới hạn, làm tròn hoặc quy tắc so sánh, phải cập nhật mô hình; không được
xem tài liệu/mô tả của mod là bằng chứng cơ chế máy chủ vẫn giữ nguyên.

Dấu hiệu: AP vẫn đúng nhưng HEAT qua màn chắn sai; % không đổi khi đổi đạn;
hiển thị không xuyên cho mọi giáp cách lớp; HE bị diễn giải sai.

## 4. Chỉ báo xích

Game: client/vehicle_systems/tankStructure.py, TankPartIndexes.
Mod dùng literal compName == 0 hoặc >=4 cho xích, 3 cho súng.
Nếu game đổi chỉ số, mod có thể nhận nhầm mà không báo lỗi.
Phần bổ sung cũng dùng các chỉ số này và điều kiện hit_track + hit_body +
probability >80. Cần sửa cả bản gốc và phần bổ sung, không chỉ một chỗ.

Dấu hiệu: bốn chấm sáng khi ngắm súng/thân hoặc không hiện tại vùng xích hợp lệ.

## 5. Vòng đời trận và ẩn overlay

Game: client/PlayerEvents.py (g_playerEvents.onAvatarReady,
onAvatarBecomeNonPlayer); client/AvatarInputHandler/__init__.py
(AvatarInputHandler.activatePostmortem).

Đối chiếu tên event, số/thứ tự tham số, thời điểm gọi và quy tắc đăng ký/hủy.
Thử vào trận, chuyển chế độ ngắm, chết, quan sát và rời trận. Tránh tạo nhiều
cửa sổ hoặc để thông tin cũ tiếp tục hiện sau khi không còn mục tiêu.
Dòng shell-info dùng prob_label.visible nên phải giữ liên kết với hide_all,
hide_labels và destroy_window khi thay cấu trúc GUI của tác giả.

## 6. Gameface / Wulf và tài nguyên

Mod: gui/ap_gameface_api.py, gui/ap_gui.py,
gui/gen_resources/ap_calculator_2.json và APBattleView.js/.html/.css.

API game cần kiểm tra:
- frameworks.wulf: ViewModel, ViewSettings, ViewFlags, WindowFlags,
  WindowLayer, PositionAnchor.
- gui.impl.pub: ViewImpl, WindowImpl; các hàm load/show/destroy/center/move,
  getViewModel, onSizeChanged.
- gui.impl.gen.R: tra cứu động R.mods.ap_calculator_2.views.APBattleView;
  không giữ cứng ID số từ lần chạy/bản game trước.
- transaction, _addStringProperty, _addBoolProperty, _setString, _setBool;
  tên, thứ tự và kiểu tham số phải khớp danh sách Python và JavaScript.
- viewEnv.resizeViewRem, engine.whenReady; căn giữa/tỉ lệ UI và surface size.

Phụ thuộc ngoài mod: OpenWG Gameface, đặc biệt
`gui/gameface/mods/libs/model.js`, ModelObserver, onUpdate và subscribe.
Thư viện này không nằm trong gói mod hiện tại; cần bản phù hợp với client mới.

Trang phát hành chính thức do người dùng cung cấp ngày 2026-11-03:
https://gitlab.com/openwg/wot.gameface/-/releases
Kiểm tra ghi chú và asset của release theo client đích khi cập nhật; không
mặc định bản mới nhất phù hợp mọi client. Chưa xác nhận release cụ thể từ URL này.

Dấu hiệu: mod tính được nhưng không có chữ; model không cập nhật; lỗi import JS;
overlay lệch/cắt chữ/không ẩn. Chỉ sửa CSS nếu bố cục/engine/tỉ lệ thay đổi;
không cần sửa CSS chỉ vì số phiên bản game đổi.

## 7. Menu và phụ thuộc phụ trợ

settings_gui/aslain_settings.py phụ thuộc gui.aslainMenu;
legacy_settings.py phụ thuộc gui.modsSettingsApi. Hai menu là tùy chọn.
Nếu chúng đổi API thì cập nhật đăng ký template/callback; không nhất thiết
phải sửa bộ tính xuyên. Ngôn ngữ dùng helpers.getClientLanguage, ResMgr.

ap_logger.py dùng onAccountShowGUI và dữ liệu BigWorld.player để gửi telemetry.
Đây là phần phụ trợ; nếu nó lỗi, kiểm tra riêng, không coi là lỗi vật lý xuyên.
Không thêm/sửa luồng gửi dữ liệu ngoài phạm vi người dùng yêu cầu.

## 8. Runtime, build và cài đặt

Nhánh nguồn hiện tại yêu cầu bytecode Python 2.7. Nếu client vẫn dùng 2.7,
không cần nâng Python chỉ vì game nâng phiên bản. Nếu runtime đổi, phải đổi
công cụ biên dịch, rà cú pháp/API và xây lại tất cả module, không tái dùng pyc cũ.

Đích triển khai: mods/<version>/ cho .wotmod; res_mods/<version>/ cho file rời.
Không dùng thư mục/version mặc định cũ trong build/build.py mà chưa kiểm tra.
Kiểm tra có file rời cũ trong res_mods ghi đè bản đóng gói hoặc gói mod trùng ID.
Nếu thay format metadata/resource registration thì cập nhật meta.xml và
manifest theo client đích. Script tác giả đóng gói meta.xml ở root; bản tùy
chỉnh hiện được tạo theo yêu cầu chứa res/. Việc thiếu metadata ở gói tùy chỉnh
chưa được xác nhận trong game; khi điều tra lỗi nạp, đối chiếu gói chuẩn và
loader của client thay vì chỉ kiểm CRC.

Tên file cố định người dùng yêu cầu: pademinune-AP_Calculator-2.2.0.wotmod,
ZIP_STORED, đặt cạnh res. Tên cố định không chứng minh nội dung là phiên bản
2.2.0 hoặc tương thích với game nào; lưu riêng commit/version nguồn đã dùng.
Loại development/, AGENTS.md, hồ sơ tùy chỉnh, backup và file rác khỏi gói.

## 9. Áp dụng lại tùy chỉnh

Lấy bản game/mod mới làm nền, đọc MOD_CUSTOMIZATIONS.md rồi áp dụng lại
thiết lập và phần mở rộng sau khi đối chiếu API. Chặn bắn 0% đã bị hủy.
Không thay entry point mới bằng entry point cũ một cách máy móc.
Không giữ offset bytecode từ bản trước; dùng nguồn .py và biên dịch lại.

## 10. Kiểm tra đủ để đánh giá bản mới

- So sánh các file game mục 1-6 với bản từng hoạt động, đúng khu vực/client.
- Biên dịch đúng runtime, kiểm tra import với API phù hợp.
- Chạy 24 kiểm thử tùy chỉnh và thêm case cho cơ chế mới. Mock tests chỉ kiểm
  logic đã mô hình hóa, không chứng minh API game thực còn tương thích.
- Trong game: AP/APCR/HEAT/HE; trực diện/nghiêng/nảy; màn chắn; nhiều khoảng
  rỗng; chỉ trúng xích; đổi đạn đang nạp so với đạn chờ nạp; độ phân giải/UI
  scaling; các mốc màu; chết/rời trận. Xem python.log và lỗi JS nếu có.
- Chỉ kết luận tương thích sau kiểm thử trên phiên bản client đích; ghi rõ
  những phần mới chỉ kiểm thử tĩnh/mô phỏng.

Không phải cập nhật tất cả sau mọi bản vá: chỉ sửa phần thực sự đổi, nhưng
phải kiểm tra những chỗ có thể sai âm thầm, đặc biệt hai hàm thay thế toàn bộ,
chỉ số xích và phép tính HEAT.
