# Power Dynamics Domain Architecture

**Domain Area:** NT-DA-0022  
**Slug:** power-dynamics  
**Category:** CAT-APPLIED  
**Status:** review

## 1. Domain Purpose

How does power distribute, accumulate, and reshape behavior inside organizations without collapsing into coercion?

## 2. Core Questions

*   Law of Power Asymmetry: Quyền lực luôn phân bổ không đồng đều và tự nhiên chảy về nơi kiểm soát các nguồn lực thiết yếu.
*   Currency of Exchange: Để ảnh hưởng, bạn phải biết đối phương định giá loại tiền tệ vô hình nào.
*   The Power Matrix: Phân loại 5 nguồn gốc quyền lực cơ bản: Chuyên gia, Vị trí, Phần thưởng, Trừng phạt, Tham chiếu.
*   Information Hoarding: Cố tình che giấu thông tin để duy trì độc quyền và quyền lực cá nhân.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `dung-nhan`
*   **Secondary domain lenses:** `hop-chung`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Anti-pattern | NT-ANTI-PATTERN-2201 | Information Hoarding | review |
| Law | NT-LAW-2201 | Law of Power Asymmetry | review |
| Model | NT-MODEL-2201 | The Power Matrix | review |
| Principle | NT-PRINCIPLE-2201 | Currency of Exchange | review |

## 5. Evidence Policy

*   Evidence posture is declared in `evidence-placeholders.yaml`; inline evidence fields remain provisional.
*   External references are not fabricated; future Evidence Layer batches will link standalone evidence records.

## 6. Ethical Safeguards

1.  Behavioral statements preserve context, uncertainty, and exception handling.
2.  Knowledge must not be used to coerce, manipulate, or stereotype individuals.
3.  No claim of universal certainty about human behavior.

## 7. Blueprint Acceptance Criteria

This blueprint is accepted when:
1.  The domain registry contains the domain id and slug.
2.  All blueprint files (`status.yaml`, `CONCEPT-MAP.md`, `ARCHITECTURE.md`, `DEPENDENCIES.md`, `GLOSSARY.md`) exist.
3.  All member units pass schema validation and `validate_all.py`.
