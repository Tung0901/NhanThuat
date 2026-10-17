# ADR-0020: Mobile Distribution, Progressive Web App (PWA), and In-App Billing Compliance Architecture

**ID:** NT-ADR-0020

**Status:** proposed

**Owner:** Product Owner

**Created:** 2026-10-14  
**Decision scope:** Mobile client distribution, offline capabilities, progressive web app lifecycle, and app store compliance

---

## 1. Context

NhanThuat included a preliminary `capacitor.config.json` targeting iOS and Android app distribution. The independent audit (`NT-AUDIT-COMMERCIAL-2026-10-14`) identified that:

1. **Incomplete Foundation:** The repository lacked `package.json`, `android/`, `ios/`, platform SDK integrations, and mobile device build scripts.
2. **Missing PWA Lifecycle:** The web client lacked a registered Service Worker for asset caching, offline fallback, and high-resolution icons (192x192, 512x512) required for web app installation.
3. **Store In-App Billing Conflict:** For apps distributed via Google Play Store and Apple App Store that unlock digital subscriptions or access to AI intelligence tools, direct bank transfers (VietQR) inside native mobile binaries violate Apple App Store Review Guideline 3.1.1 and Google Play Payments policy, leading to instant store rejection.

A clear, compliant distribution architecture is required.

---

## 2. Decision

### 2.1 PWA-First Mobile Strategy

Before compiling native store wrappers, NhanThuat must first establish an installable,
testable Progressive Web App (PWA). The first delivery is an application shell, not an
offline case-management product:

1. **Service Worker Implementation (`frontend/sw.js`):**
   - Cache-first strategy for static runtime assets (CSS, fonts, client JavaScript libraries).
   - Network-first navigation with a dedicated offline status page.
   - No authenticated API response or confidential case data in Cache Storage.
   - Dedicated offline fallback page (`offline.html`) when navigation cannot reach the server.
2. **Web App Manifest Completeness (`frontend/manifest.json`):**
   - Provision install icons (`icon-192.png`, `icon-512.png`). A separately designed
     maskable icon remains required before store packaging.
   - Specify `display: "standalone"`, `orientation: "portrait"`, and theme colors aligned with the dark executive UI palette.
3. **Storage Security on Client:**
   - Case files and confidential executive scenarios must not be stored in unencrypted `localStorage`. Sensitive casework data must be transient in memory or stored in `sessionStorage` with explicit cleanup on logout.

### 2.2 Native Packaging Lifecycle (Capacitor Architecture)

When native binaries are required:

1. **Node & Dependency Manifest:** A formal `package.json` must be introduced declaring `@capacitor/core`, `@capacitor/cli`, `@capacitor/android`, and `@capacitor/ios`.
2. **Build Pipeline:**
   ```
   Web Assets (frontend/) ──> npm run build ──> npx cap sync ──> Native IDEs (Android Studio / Xcode)
   ```
3. **Platform Directory Governance:** Native build directories (`android/` and `ios/`) must remain derived build outputs, generated from the canonical web source, not manually modified with ad-hoc logic.

### 2.3 Store Billing & Distribution Model Compliance

NhanThuat proposes a **Multi-Platform Reader / Cross-Platform Subscription Model**.
Store rules and product classification must be revalidated against the current Apple
and Google policies before each native release:

1. **Web Direct (Tier 1 & Corporate B2B):**
   - Full checkout, corporate invoicing, and VietQR / bank wire settlement take place exclusively on the web portal (`https://nhanthuat.vn`).
2. **Mobile App Store Distribution (iOS / Android):**
   - The native app functions as a "Multi-Platform Service" under Apple Guideline 3.1.3(b): users log in with their existing enterprise credentials to access their pre-purchased workspace and casework.
   - If in-app subscription purchase is provided on mobile devices, native store billing (StoreKit 2 / Google Play Billing Library) must be integrated for consumer purchases.
   - VietQR invoice dialogs must be conditionally suppressed when running inside a native mobile runtime (`Capacitor.isNativePlatform() == true`).

---

## 3. Consequences

### Positive
- Web users gain instant, high-speed mobile installation via PWA without store delays or 30% store commission.
- Creates a reviewable path toward Apple and Google policy compliance; store approval
  remains subject to current policy and platform review.
- Provides a clear offline state without caching confidential work or implying that
  advisory workflows remain available offline.

### Negative / Required Work
- Requires designing app icons, implementing `sw.js`, and maintaining cross-platform billing abstraction layers.
- Native builds require macOS and Xcode for iOS compilation.
