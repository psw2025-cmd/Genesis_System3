import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.getcwd())

try:
    from dashboard.backend.advanced_charting import get_advanced_charting
    
    charting = get_advanced_charting()
    
    # Mock chain data
    mock_chain = {
        "spot": 24000,
        "contracts": [
            {"strike": 24000, "expiry": "2026-03-05", "oi": 1000, "volume": 5000, "iv": 15, "ltp": 100, "option_type": "CE"},
            {"strike": 24000, "expiry": "2026-03-05", "oi": 800, "volume": 4000, "iv": 14, "ltp": 80, "option_type": "PE"},
            {"strike": 24100, "expiry": "2026-03-05", "oi": 1200, "volume": 6000, "iv": 16, "ltp": 50, "option_type": "CE"},
            {"strike": 24100, "expiry": "2026-03-05", "oi": 200, "volume": 1000, "iv": 13, "ltp": 150, "option_type": "PE"},
            {"strike": 24000, "expiry": "2026-03-12", "oi": 500, "volume": 2000, "iv": 18, "ltp": 120, "option_type": "CE"},
        ]
    }
    
    print("Testing Heatmap Generation...")
    heatmap = charting.generate_option_chain_heatmap(mock_chain, metric="oi")
    print(json.dumps(heatmap, indent=2))
    
    print("
Testing IV Surface Generation...")
    surface = charting.generate_iv_surface(mock_chain)
    print(json.dumps(surface, indent=2))
    
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
