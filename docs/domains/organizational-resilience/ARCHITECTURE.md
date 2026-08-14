# Organizational Resilience Domain Architecture

**Domain Area:** NT-DA-0024  
**Slug:** organizational-resilience  
**Category:** CAT-APPLIED  
**Status:** review

## 1. Domain Purpose

How do organizations absorb shocks, adapt, and continue operating when normal conditions fail?

## 2. Core Questions

*   Law of System Redundancy: Sự bền bỉ yêu cầu một mức độ dư thừa có tính toán thay vì tối ưu hóa hoàn toàn cho sự hiệu quả.
*   Fail Gracefully: Thiết kế hệ thống sao cho một lỗi cục bộ không kéo theo sự sụp đổ toàn bộ.
*   The Adaptive Cycle: Tăng trưởng, Bảo tồn, Sụp đổ, Tái cấu trúc.
*   Single Point of Failure: Phụ thuộc toàn bộ vào một nhân sự hoặc quy trình duy nhất.

## 3. Taxonomy Alignment

*   **Primary domain lens:** `thanh-su`
*   **Secondary domain lenses:** `hop-chung`, `tri-nhan`

## 4. Knowledge Inventory

| Type | ID | Title | Status |
| --- | --- | --- | --- |
| Anti-pattern | NT-ANTI-PATTERN-2401 | Single Point of Failure | review |
| Law | NT-LAW-2401 | Law of System Redundancy | review |
| Model | NT-MODEL-2401 | The Adaptive Cycle | review |
| Principle | NT-PRINCIPLE-2401 | Fail Gracefully | review |

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
