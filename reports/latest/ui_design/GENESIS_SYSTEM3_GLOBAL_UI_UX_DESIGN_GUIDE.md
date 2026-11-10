# Genesis System3 — Global UI/UX Master Design & Architecture Guide

> **Authoritative UI/UX Repository Catalog:** Covering 8 top global design systems (Bloomberg, TradingView, Linear, Apple visionOS, Cyberpunk, Google Material 3, Palantir Holographic, and Retool DataOps).

---

## 1. Master Design System Matrix

| ID | Design Paradigm Name | Global Rating | Target Tabs | Philosophy & Origin | Recommended Stack |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DS-001** | **Bloomberg Quant Terminal** | 5.0 / 5 | Paper Trading, Positions | Bloomberg Terminal / Citadel Desks | Tailwind + JetBrains Mono + TanStack |
| **DS-002** | **Cyberpunk Neon Glassmorphism** | 4.9 / 5 | Smoke Sim, Live Radar | Cyberpunk 2077 HUD / Sci-Fi Quant | Tailwind + Backdrop Blur + Canvas |
| **DS-003** | **Linear App Minimalist Slate** | 4.95 / 5 | Signals, Genesis, Overview | Linear.app / Vercel Geist System | Tailwind + Radix UI + Framer Motion |
| **DS-004** | **TradingView Interactive Matrix** | 5.0 / 5 | Option Chain, Greek Intel | TradingView Pro / Interactive Brokers | React Virtual + Lightweight Charts |
| **DS-005** | **Google Stitch / Material 3** | 4.8 / 5 | Decision Intel, System Ops | Google Cloud / Material Design 3 | Tailwind + Material 3 Tokens |
| **DS-006** | **Holographic Quant Radar** | 4.85 / 5 | Multibagger, Breakouts | Palantir Foundry / Defense Screens | HTML5 Canvas + WebGL + Tailwind |
| **DS-007** | **DataOps Tooling Grid** | 4.75 / 5 | Performance, Data Integrity | Retool Enterprise / Appsmith | TanStack Table + Monaco Editor |
| **DS-008** | **Apple visionOS Spatial Glass** | 4.9 / 5 | Gates, Readiness, Executive | Apple visionOS / macOS Sonoma | Backdrop Blur XL + SF Pro Fonts |

---

## 2. Standardized Agent-Human Alignment Prompt Format

Whenever you want an AI agent to redesign or preview any tab without touching backend APIs, copy and use this exact standardized prompt:

```text
AGENT_COMMAND: Redesign UI for [INSERT_TAB_NAME_HERE]
DESIGN_STYLE_ID: DS-001 (or DS-002, DS-003, DS-004, DS-008)
CANVAS_BACKGROUND: [Hex code from catalog, e.g. #0B0E14]
CARD_CONTAINER: [e.g. #121824 with 1px border #1E293B]
ACCENT_COLORS: Positive=#00E676, Negative=#FF1744, Primary=#5E6AD2
MICRO_INTERACTIONS: Number-flip on P&L change, live 1.5s pulsing green dot, smooth tab transitions
REQUIREMENTS: Pure visual component styling only. Keep all API hooks, data bindings, and null-safety guards intact. Show image mockup or local CSS rendering before merge.
```

---

## 3. Global Design Inspiration Links

- **Bloomberg Terminal UI Breakdown:** [https://www.bloomberg.com/professional/solution/bloomberg-terminal/](https://www.bloomberg.com/professional/solution/bloomberg-terminal/)
- **Linear.app Design Principles:** [https://linear.app/](https://linear.app/)
- **TradingView Charting System:** [https://www.tradingview.com/](https://www.tradingview.com/)
- **Apple visionOS Human Interface Guidelines:** [https://developer.apple.com/design/human-interface-guidelines/visionos](https://developer.apple.com/design/human-interface-guidelines/visionos)
- **Google Material Design 3:** [https://m3.material.io/](https://m3.material.io/)
- **Palantir Foundry Visual System:** [https://www.palantir.com/platforms/foundry/](https://www.palantir.com/platforms/foundry/)
