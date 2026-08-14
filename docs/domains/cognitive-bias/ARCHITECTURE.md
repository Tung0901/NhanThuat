# Cognitive Bias Domain Architecture

**Domain Area:** NT-DA-0023  
**Slug:** cognitive-bias  
**Category:** CAT-BEHAVIORAL  
**Status:** review

## 1. Domain Purpose

How do systematic distortions in judgment and perception degrade decisions, and how can structures guard against them?

## 2. Core Questions

*   Law of Anchoring: Con người có xu hướng bám víu quá mức vào mẩu thông tin đầu tiên họ nhận được.
*   Red Teaming: Xây dựng đội ngũ chuyên đóng vai phản biện để chống lại thiên kiến xác nhận.
*   The Cynefin Framework: Khung nhận thức giúp phân loại vấn đề (Rõ ràng, Phức tạp, Rối rắm, Hỗn loạn).
*   Sunk Cost Fallacy: Tiếp tục đầu tư vào nỗ lực thất bại vì đã đầu tư quá nhiều trước đó.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `thanh-su`
*   **Secondary domain lenses:** `tri-nhan`, `hop-chung`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Anti-pattern | NT-ANTI-PATTERN-2301 | Sunk Cost Fallacy | review |
| Law | NT-LAW-2301 | Law of Anchoring | review |
| Model | NT-MODEL-2301 | The Cynefin Framework | review |
| Principle | NT-PRINCIPLE-2301 | Red Teaming | review |

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
