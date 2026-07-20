# Quy trình phê duyệt và Frozen

**ID:** NT-GOV-APPROVAL-001  
**Phiên bản:** 0.1.0  
**Trạng thái:** draft

Luồng chuẩn:

`Backlog → Draft → Schema Valid → Internal Review → Test Passed → Ready for Epic Review → Approved → Frozen`

Chỉ Product Owner được chuyển nội dung sang `approved` hoặc quyết định Frozen.
Nội dung Frozen không sửa trực tiếp; phải có Change Request, tăng version, ghi
lý do và phạm vi ảnh hưởng, rồi chạy lại test liên quan.

