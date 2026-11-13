# 14 — Browser Screenshot, HAR & Console Proof (Desktop & Mobile)

- **Generated At (IST)**: `2026-11-04T16:36:14.478277+05:30`
- **Target URL**: `http://127.0.0.1:8008/ui`
- **Engine**: Playwright Headless Chromium

## 1. Captured Visual & Network Artifacts

| Artifact | Path | Viewport / Scope | SHA-256 |
|---|---|---|---|
| Desktop Full UI (After Fixes) | `02_UI_BEFORE_AFTER/after_ui_desktop_1440x900.png` | `1440x900` | `68bb5afebb832d605b112e453ab18e978605ba757f9d8b1bc8af5cc96ea2b65c` |
| Mobile Full UI (After Fixes) | `02_UI_BEFORE_AFTER/after_ui_mobile_390x844.png` | `390x844` | `a93757eeb05aa569bb35cad0bca655c8c94f938358fd86676e5cf8975679ea47` |
| Tab 2 Dhan Broker Portfolio | `02_UI_BEFORE_AFTER/after_ui_tab2_dhan_1440x900.png` | `1440x900` | `15ac23abcdbc849f1f7f68a88ebb24a74fe875d7a580dcc5e1a8d1dc6386174c` |
| Order Ticket Submission Proof | `02_UI_BEFORE_AFTER/after_ui_order_ticket_response.png` | `1440x900` | `fce4033b076dc429e9ce779be7f2945cf2ac7e8d1161ca85a0759bf22fcef3cc` |
| Sanitized Network HAR JSON | `02_UI_BEFORE_AFTER/sanitized_ui_network.har.json` | `48` requests (`5xx = 0`) | `6e000fe8ca2d23624a38b8f601cbc64d3e539a07d2f4a46d77bf20efbfcd692e` |
| Browser Console & Assertions | `02_UI_BEFORE_AFTER/console_logs.json` | Console Errors: `1`, Page Errors: `0` | `1ca249b19b650c7425cbeb3ee6a41a869abb8e09c2b00535a468258e1291383a` |

## 2. Verified UI DOM State Assertions

```json
{
  "ws_stream_status_badge": "MARKET CLOSED \u2014 LAST VERIFIED CLOSE (2026-11-04T16:35:45+05:30)",
  "initial_order_symbol": "NIFTY 05NOV2026 23450 CE",
  "initial_order_exchange_segment": "NSE_FNO",
  "initial_order_security_id": "43891",
  "initial_order_expiry": "2026-11-05",
  "initial_order_strike": "23450",
  "initial_order_option_type": "CE",
  "initial_order_lot_size": "75",
  "after_contract_click_symbol": "RELIANCE 26NOV2026 1300 CE",
  "after_contract_click_lot_size": "500",
  "order_submit_response_msg": "Order Blocked by Backend Safety Gate: Live trading is locked (LIVE_TRADING_ENABLED=0)",
  "console_error_count": 1,
  "page_error_count": 0,
  "network_request_count": 48,
  "network_5xx_count": 0
}
```
