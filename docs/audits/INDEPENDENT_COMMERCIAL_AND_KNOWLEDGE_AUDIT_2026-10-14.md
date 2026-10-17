# Thẩm định độc lập bản mở rộng Nhân Thuật

**Mã:** NT-AUDIT-COMMERCIAL-2026-10-14  
**Ngày:** 2026-10-14  
**Phạm vi:** Dịch học, Hội đồng 7 thành viên, gói thuê bao, VietQR, PWA/Capacitor  
**Kết luận:** Chưa sẵn sàng thu tiền, phát hành mobile, Approved hoặc Frozen

## 1. Kết luận điều hành

Bản mở rộng có giá trị ở mức prototype: có catalog 64 quẻ, hai cấu hình lens,
giao diện gói dịch vụ và khung Capacitor. Tuy nhiên, báo cáo hoàn tất đã đi xa
hơn bằng chứng kỹ thuật. Trước đợt thẩm định này, một người gọi API công khai có
thể tự đánh dấu đơn hàng là đã thanh toán; webhook không xác thực chữ ký; đơn
hàng và quyền lợi chỉ nằm trong RAM. Thuật toán được giới thiệu là phương pháp
ba đồng xu thực tế lại chọn quẻ theo `seed % 64`, chọn đúng một hào ngẫu nhiên và
tính quẻ biến bằng phép dịch số không phải biến âm/dương. Sáu hào của quẻ Càn
còn bị gắn cho mọi quẻ.

Những đường có thể gây mở quyền hoặc tạo chỉ đạo sai đã được đặt về trạng thái
fail-closed. Catalog giá và dữ liệu quẻ vẫn có thể được xem như bản đề xuất hoặc
tài liệu đang thẩm định; chưa có checkout hay oracle hoạt động.

## 2. Phát hiện theo mức độ

### P0 - Đã cách ly

1. **Bỏ qua thanh toán:** `/api/v1/payment/confirm-demo` cho phép nâng cấp bất kỳ
   đơn hàng biết mã; webhook không có chữ ký và chấp nhận nội dung chứa mã đơn.
   Cả hai đường hiện không còn cấp quyền.
2. **Lộ và chiếm quyền đơn hàng:** API trạng thái đơn và quyền lợi từng tin
   `user_id` do client gửi. Hiện yêu cầu Bearer session, lấy `user_id` từ session
   và kiểm tra chủ sở hữu.
3. **Tài khoản ngân hàng và secret mẫu trong production:** giá trị mặc định đã
   được bỏ. Checkout hiện trả `503 CHECKOUT_UNAVAILABLE` và không tạo đơn.
4. **Oracle tạo chỉ đạo từ phép biến đổi không đúng mô tả:** casting hiện trả
   `503 ORACLE_UNAVAILABLE`, không trả quẻ chủ, hào động, quẻ biến hay tổng hợp
   điều hành. API tra cứu được gắn `epistemic_status: unreviewed`.
5. **Hội đồng 7 thành viên dùng nội dung chưa duyệt:** API hiện buộc dùng Hội
   đồng 5 thành viên; công tắc mở rộng trên giao diện bị khóa.
6. **Hai lens draft lọt vào runtime:** `LENS-ICHING` và `LENS-TIMING` đã được hạ
   từ `active` về `draft`, confidence về `0.0` và bỏ ngày review tự khai. Router
   vẫn giữ chúng trong catalog để thẩm định nhưng không cho tham gia quyết định.
   Truy vấn nhắm vào lens draft trả `INSUFFICIENT_VERIFIED_KNOWLEDGE` và dừng
   trước bước tổng hợp AI.

### P0 - Còn là cổng chặn phát hành

1. Hai tài liệu mới không tuân envelope tri thức của Constitution: chưa có ID
   ổn định, version, status, owner, scope, conditions, exceptions, risks,
   evidence level và reference locator. Câu khẳng định “mô hình toán học” chưa
   có nguồn chứng minh. Quét ba artifact mới ghi nhận 80 lượt ngôn ngữ tuyệt đối
   hoặc tối ưu hóa (`tuyệt đối`, `chắc chắn`, `hoàn hảo`, `tối ưu`, `sẽ`, v.v.),
   cần rà từng claim theo điều kiện và ngoại lệ.
2. Validator canonical vẫn báo 379 knowledge units (373 frozen, 6 draft) và một
   evidence record. Điều đó không xác nhận hai tài liệu Markdown hoặc JSON 64
   quẻ mới. “Validation passed” không phải bằng chứng chất lượng cho phần mới.

### P1 - Thương mại chưa triển khai

1. Không có database cho order, transaction, subscription, entitlement hoặc
   webhook event; restart server sẽ mất trạng thái và không thể đối soát.
2. Chưa có hợp đồng webhook theo nhà cung cấp: signature/timestamp, idempotency,
   chiều giao dịch, tài khoản nhận, currency, exact amount, replay protection,
   refund/chargeback và audit log.
3. Auth hiện là bốn tài khoản dùng chung cấu hình bằng biến môi trường. Chưa có
   đăng ký khách hàng, xác minh email, quên mật khẩu, MFA, quản trị thiết bị,
   customer ID bền vững hoặc xóa tài khoản.
4. Các giới hạn gói mới chỉ là dữ liệu mô tả; chưa có middleware đếm quota và
   kiểm entitlement nhất quán tại từng endpoint. Vì vậy chưa được quảng cáo
   “3 lượt/ngày”, “không giới hạn” hay “mở khóa 15 lens”.
5. Chưa có điều khoản sử dụng, chính sách riêng tư, hỗ trợ, hoàn tiền, hóa đơn,
   lưu giữ dữ liệu, consent cho dữ liệu nhân sự và quy trình phản hồi sự cố.
6. Ước tính biên lợi nhuận 98,5% chưa có telemetry token, phân bố độ dài đầu
   vào/đầu ra, retry, lưu trữ, support, thuế, phí cửa hàng và chi phí giám sát.
   Đây chỉ là giả định, chưa phải unit economics đã kiểm chứng.

### P1 - Mobile/PWA chưa sẵn sàng

Repository không có `package.json`, `android/`, `ios/`, icon 192/512 hoặc service
worker. `capacitor.config.json` một mình không tạo APK/IPA. Quy trình Capacitor
còn cần cài runtime/CLI, thêm platform, sync web bundle và test trên thiết bị.
Apple còn yêu cầu Xcode cho iOS. Với thuê bao mở nội dung số trong app, VietQR
không thể mặc nhiên thay thế In-App Purchase/Google Play Billing; phải thiết kế
mô hình phân phối phù hợp quy định từng store.

Nguồn chính thức:

- Apple App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Google Play Payments policy: https://support.google.com/googleplay/android-developer/answer/9858738
- Capacitor Getting Started: https://capacitorjs.com/docs/getting-started

### P2 - Hình thức và khả năng bảo trì

Phần mới lặp lại nhiều dấu tượng hình, gradient, badge, inline style và các nhãn
“tối cao/hoàn hảo/tối ưu”. Điều này đi ngược hướng giao diện điềm tĩnh, có bằng
chứng mà Nhân Thuật đang theo đuổi. `frontend/app.html` tiếp tục phình lớn với
logic API và rendering nhúng trực tiếp; nên tách module nhưng không thực hiện
refactor lớn trong đợt thẩm định bảo mật này.

## 3. Bằng chứng kiểm thử

- Baseline do Antigravity viện dẫn: 33 test liên quan chạy đạt trước khi audit,
  nhưng chỉ kiểm happy path và vô tình xác nhận đường tự nâng cấp.
- Toàn suite sau lượt khắc phục ngày 2026-10-15: 263 test đạt trong 154,11 giây.
- `scripts/validate_all.py`: đạt, nhưng không bao phủ phần nội dung mới nêu trên.
- `scripts/audit_content_inventory.py --check`: 379 units, 373 frozen, 6 draft,
  1 evidence record.
- Catalog JSON có đủ 64 số, 64 tên và 64 ký hiệu duy nhất; đây là kiểm tra hình
  thức, không xác nhận ý nghĩa, cung, lời cảnh báo hay khuyến nghị quản trị.
- Test mới kiểm các trường hợp giả mạo `user_id`, xem đơn khác chủ, webhook giả,
  direct confirmation, dữ liệu amount sai và oracle chưa kiểm định: 17 test đạt.
- Auth và ownership chạy lại trên source cuối: 7 test đạt.
- Draft isolation cho router, API và catalog: 42 test đạt, gồm HTTP `422` và
  xác nhận không sinh action script/synthesis từ lens chưa duyệt.
- Ruff đạt với ba module/test mới; khi mở rộng sang `backend/app/main.py` còn 21
  lỗi lint có sẵn (chủ yếu broad exception và import), nên không tuyên bố toàn
  repository đã sạch lint.

### Kiểm tra tiếp nối ngày 2026-10-15

- Gỡ hai modal không có trigger/hàm điều khiển và checkbox kích hoạt Hội đồng
  mở rộng khỏi giao diện canonical; catalog thương mại vẫn chỉ tồn tại ở tầng
  API fail-closed/read-only để phục vụ thẩm định.
- Khôi phục roster Hội đồng gồm đủ 7 lăng kính trên giao diện: 5 lăng kính đang
  tham gia và 2 lăng kính Dịch học/Thời thế được ghi rõ `đang thẩm định`. Việc
  hiển thị catalog không mở đường chạy hai lens draft trong kết luận runtime.
- Xóa hoàn toàn tham số `extended` và nội dung I Ching/Timing khỏi
  `CouncilEngine`; không còn đường opt-in trực tiếp bỏ qua router governance.
- PWA được nối vào trang thật qua manifest và đăng ký service worker. Cache chỉ
  chứa application shell công khai, bỏ qua `/api/`, không lưu response nghiệp vụ
  hay hồ sơ; navigation ngoại tuyến trả trang trạng thái riêng.
- Loại bỏ sáu script/backup vá tạm ở thư mục gốc không được mã nguồn tham chiếu.
- Test tập trung sau sửa lỗi: 28 đạt; canonical validator, inventory audit và
  Ruff trên phạm vi thay đổi đều đạt. Reviewer kiến trúc chuyên biệt chưa chạy
  được do giới hạn sử dụng, vì vậy ADR-0019/0020 vẫn là `proposed` và không có
  nội dung nào được tự phê duyệt hoặc Frozen.

## 4. Handoff cho Antigravity

1. **Luồng tri thức:** chuẩn bị source register và claim-level citations; tách
   nguyên văn cổ điển, diễn giải hiện đại và khuyến nghị quản trị; thêm giới hạn,
   ngoại lệ, rủi ro và epistemic status. Draft isolation đã triển khai; không
   đặt lại `active` trước reviewer và quyết định đúng thẩm quyền.
2. **Luồng commerce:** lập ADR chọn provider và mô hình subscription; thiết kế
   schema PostgreSQL, state machine, idempotency và signed webhook; viết test đối
   kháng trước khi mở lại checkout.
3. **Luồng identity:** thay tài khoản dùng chung bằng customer identity bền vững,
   recovery, rate limit, MFA cho admin và audit trail.
4. **Luồng mobile:** ưu tiên PWA hoàn chỉnh và kiểm tra cài đặt thật. Chỉ tạo
   native projects sau khi chốt billing, privacy, account deletion và store
   distribution model.
5. **Luồng giao diện:** bỏ emoji trang trí, rút gọn ngôn ngữ khoa trương, dùng
   ảnh minh họa có nguồn/quyền sử dụng, tách checkout/oracle thành module và bổ
   sung trạng thái loading/error/empty/accessibility.

## 5. Cổng nghiệm thu đề xuất

Chỉ trình Product Owner xem xét phát hành khi: reviewer tri thức không còn P0;
commerce threat model và ADR được duyệt; test webhook đối kháng đạt; dữ liệu tồn
tại qua restart; mọi quyền lợi được enforce server-side; có legal/privacy; PWA
hoặc native build chạy trên thiết bị thật; và báo cáo chi phí dựa trên telemetry.

Knowledge Architecture Reviewer đã được gọi theo `AGENTS.md` nhưng phiên reviewer
không hoàn tất do giới hạn thực thi. Vì vậy đây là thẩm định kỹ thuật độc lập,
không thay thế review kiến trúc tri thức bắt buộc và không phải phê duyệt/Frozen.
