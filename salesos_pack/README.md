# SalesOS Industry Solution Pack (v1.0.0)

**Plugin ID:** `com.nhanthuat.salesos`  
**Governance Status:** `frozen`  
**License:** Proprietary  

## Overview
SalesOS is the first production Industry Solution Pack for BusinessOS. It operates as an external plugin without modifying the BusinessOS Kernel Core.

## Features
- **Lead Intake Workflow (SALESOS-CAP-001):** Validates, normalizes Vietnamese contact numbers, checks for duplicates, creates lead/customer records, assigns sales representatives deterministically, generates next-action recommendations, and records causal provenance traces.
- **Vietnamese Phone Normalizer Tool:** Normalizes local (`09xxxxxxxx`) and international E.164 (`+849xxxxxxxx`) Vietnamese mobile numbers.
- **Sales Operations Coordinator Persona (SALESOS-PERSONA-001):** Operates under Level 2 Authority without inventing unverified company policies.
- **Fallbacks:** Emits official error code `INSUFFICIENT_VERIFIED_KNOWLEDGE` when unverified knowledge or configuration is requested.
