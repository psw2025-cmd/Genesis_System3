# Genesis System3 — UI/UX Architecture & Multi-Validation Operating Contract

**Policy Identifier:** `SYSTEM3_UI_UX_MULTI_VALIDATION_V1`  
**Applies to:** All UI components, styling, charts, data formatting, and visual testing across all 22 tabs in Genesis System3.

---

## 1. The Core Standard

Genesis System3 requires a global institutional-grade financial dashboard standard matching Figma design precision, Bloomberg Terminal data density, and TradingView real-time fluid interactivity.

### Anti-Fragile UI Principles:
1. **Never Crash the Tab:** Every subcomponent must be isolated with `<WidgetErrorBoundary>` or defensive formatting (`safeMoney`, `safePct`, `safeNumber`, `safeText`, `safeArray`).
2. **Never Break Under Zoom or Mobile Viewports:** All layouts must be resilient across 320px to 4K resolutions and 50% to 300% browser zoom levels.
3. **Never Render Static Mock Placeholders:** All UI components must bind directly to dynamic streaming state, fail-safe backend APIs, and provide living interactive state feedback.

---

## 2. The 5-Layer Multi-Validation Contract

1. **Layer 1: Defensive Data Sanitization & Ingestion:**
   Use [`dashboard/frontend/src/utils/formatters.ts`](file:///C:/Users/ADMIN/Genesis_System3/Genesis_System3/dashboard/frontend/src/utils/formatters.ts) to guarantee zero undefined crashes.
2. **Layer 2: Component-Level Error Isolation:**
   Use [`dashboard/frontend/src/components/WidgetErrorBoundary.tsx`](file:///C:/Users/ADMIN/Genesis_System3/Genesis_System3/dashboard/frontend/src/components/WidgetErrorBoundary.tsx) to isolate individual card failures with auto-reset.
3. **Layer 3: Viewport & Zoom Resiliency:**
   Use `min-w-0`, `clamp()`, `overflow-x-auto`, and relative units for flexible responsiveness.
4. **Layer 4: Tactile Interactive 4-State Contract:**
   Enforce Default, Hover, Active/Press, and Focus-Visible states on all clickable controls.
5. **Layer 5: Tabular Numerics & Micro-Flash Transitions:**
   Use `font-mono tabular-nums` and non-layout-shifting color transitions on live tick updates.

---

## 3. Automated Multi-Validation Matrix

Run `python scripts/ui_multi_validation_runner.py` before promoting frontend code to production.
Matrix scope:
- 4 Viewports: Mobile (`375x667`), Tablet (`768x1024`), Laptop (`1280x800`), Desktop (`1920x1080`).
- 3 Zoom levels: `100%`, `125%`, `150%`.
- Assertions: 0 console errors, 0 page crashes, 100% DOM element integrity.
