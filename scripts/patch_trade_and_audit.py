import os

trade_path = os.path.join("dashboard", "frontend", "src", "components", "TradeTab.tsx")
with open(trade_path, "r", encoding="utf-8") as f:
    text = f.read()

if "PendingLifecycleBanner" not in text:
    text = text.replace(
        "import { OptionChain } from './OptionChain'",
        "import { OptionChain } from './OptionChain'\nimport { PendingLifecycleBanner } from './PendingLifecycleBanner'"
    )
    text = text.replace(
        '<div className="flex flex-col h-full min-h-0 overflow-hidden">',
        '<div className="flex flex-col h-full min-h-0 overflow-hidden">\n      <PendingLifecycleBanner />'
    )
    with open(trade_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("SUCCESS: TradeTab.tsx patched with PendingLifecycleBanner")
else:
    print("TradeTab.tsx already has PendingLifecycleBanner")
