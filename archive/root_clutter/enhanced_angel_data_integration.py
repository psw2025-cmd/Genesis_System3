#!/usr/bin/env python3
"""
Enhanced Angel Data Integration
Ensures seamless switching between Angel (market hours) and synthetic (off-market) data
"""
import sys
from pathlib import Path
from datetime import datetime
import pytz

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

IST = pytz.timezone('Asia/Kolkata')

def check_angel_data_availability():
    """Check if Angel broker data is available"""
    try:
        from src.utils.market_hours import is_market_open
        
        is_open, reason = is_market_open()
        
        if is_open:
            # Market is open - check for real data files
            chain_file = ROOT_DIR / "outputs" / "chain_raw_live.csv"
            
            if chain_file.exists():
                # Check file freshness (should be updated within last 5 minutes during market hours)
                file_time = datetime.fromtimestamp(chain_file.stat().st_mtime, tz=IST)
                now = datetime.now(IST)
                age_minutes = (now - file_time).total_seconds() / 60
                
                if age_minutes < 5:
                    return {
                        'available': True,
                        'source': 'angel',
                        'age_minutes': age_minutes,
                        'status': 'fresh'
                    }
                else:
                    return {
                        'available': True,
                        'source': 'angel',
                        'age_minutes': age_minutes,
                        'status': 'stale'
                    }
            else:
                return {
                    'available': False,
                    'source': 'angel',
                    'status': 'file_not_found'
                }
        else:
            return {
                'available': False,
                'source': 'synthetic',
                'reason': reason,
                'status': 'market_closed'
            }
    except Exception as e:
        return {
            'available': False,
            'source': 'unknown',
            'error': str(e),
            'status': 'error'
        }

def ensure_data_switching():
    """Ensure proper data switching logic"""
    print("[Integration] Checking data switching logic...")
    
    # Check market status
    try:
        from src.utils.market_hours import is_market_open, get_market_status
        
        is_open, reason = is_market_open()
        status = get_market_status()
        
        print(f"[Info] Market: {'OPEN' if is_open else 'CLOSED'}")
        print(f"[Info] Reason: {reason}")
        
        # Check Angel data availability
        angel_status = check_angel_data_availability()
        print(f"[Info] Angel data: {angel_status.get('status', 'unknown')}")
        
        # Expected behavior
        if is_open:
            expected_source = 'angel'
            if angel_status.get('source') == expected_source:
                print("[OK] Market open - Angel data should be used")
            else:
                print("[WARNING] Market open but Angel data not available")
        else:
            expected_source = 'synthetic'
            if angel_status.get('source') == expected_source:
                print("[OK] Market closed - Synthetic data should be used")
            else:
                print("[WARNING] Market closed but wrong data source")
        
        return True
    except Exception as e:
        print(f"[ERROR] Data switching check failed: {e}")
        return False

if __name__ == "__main__":
    ensure_data_switching()
