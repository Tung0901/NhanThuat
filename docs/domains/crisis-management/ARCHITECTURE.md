# Crisis Management Domain Architecture

**Domain Area:** NT-DA-0021  
**Slug:** crisis-management  
**Category:** CAT-APPLIED  
**Status:** review

## 1. Domain Purpose

How do organizations detect, contain, and recover from disruptive events under time pressure and uncertainty?

## 2. Core Questions

*   Law of Entropy in Crisis: Trong khủng hoảng, thiếu thông tin và độ trễ phản hồi sẽ luôn làm khuếch đại mức độ nghiêm trọng nếu không có sự can thiệp cắt đứt chuỗi phản ứng.
*   Over-communicate to Anchor Trust: Giao tiếp liên tục, minh bạch và có chủ đích là cách duy nhất để neo giữ niềm tin của các bên liên quan khi khủng hoảng xảy ra.
*   Crisis Response Triangle: Mô hình ba trụ cột để đánh giá và xử lý khủng hoảng: Containment, Communication, và Correction.
*   The Ostrich Strategy: Phớt lờ khủng hoảng với hy vọng nó sẽ tự qua đi hoặc không ai chú ý.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `thanh-su`
*   **Secondary domain lenses:** `tri-nhan`, `hop-chung`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Anti-pattern | NT-ANTI-PATTERN-2101 | The Ostrich Strategy | review |
| Law | NT-LAW-2101 | Law of Entropy in Crisis | review |
| Model | NT-MODEL-2101 | Crisis Response Triangle | review |
| Principle | NT-PRINCIPLE-2101 | Over-communicate to Anchor Trust | review |

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
