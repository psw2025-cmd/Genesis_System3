#!/usr/bin/env python3
"""
SYSTEM3 LIVE PAPER TRADING MONITOR
Real-time dashboard showing signals, orders, PnL, and predictions vs actual
"""
import pandas as pd
import os
from datetime import datetime
import json

def main():
    print("="*80)
    print("  SYSTEM3 LIVE PAPER TRADING DASHBOARD")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 1. Check Virtual Orders
    print("\n[1] VIRTUAL ORDERS STATUS")
    print("-"*80)
    ord_file = 'storage/live/angel_virtual_orders_with_pnl.csv'
    if os.path.exists(ord_file):
        try:
            orders = pd.read_csv(ord_file)
            print(f"Total Orders: {len(orders)}")
            print(f"Columns: {list(orders.columns[:10])}")  # Show first 10 columns
            
            # Show last 10 orders with available columns
            if len(orders) > 0:
                display_cols = []
                for col in ['underlying', 'symbol', 'strike', 'side', 'ltp', 'signal', 
                           'entry_confidence', 'timestamp', 'ts']:
                    if col in orders.columns:
                        display_cols.append(col)
                
                print(f"\nLast 10 Orders:")
                print(orders[display_cols].tail(10).to_string(index=False))
        except Exception as e:
            print(f"Error reading orders: {e}")
    else:
        print("No orders file found")
    
    # 2. Check PnL Log
    print("\n\n[2] PNL TRACKING")
    print("-"*80)
    pnl_file = 'storage/live/angel_index_ai_pnl_log.csv'
    if os.path.exists(pnl_file):
        try:
            pnl = pd.read_csv(pnl_file)
            print(f"Total PnL Records: {len(pnl)}")
            if len(pnl) > 0:
                print(f"\nLatest PnL entries:")
                print(pnl.tail(10).to_string(index=False))
        except Exception as e:
            print(f"Error reading PnL: {e}")
    else:
        print("No PnL log found yet")
    
    # 3. Check Active Signals
    print("\n\n[3] ACTIVE SIGNALS")
    print("-"*80)
    sig_file = 'storage/live/angel_index_ai_signals_curated.csv'
    if os.path.exists(sig_file):
        try:
            signals = pd.read_csv(sig_file)
            print(f"Total Signals: {len(signals)}")
            
            if 'signal' in signals.columns:
                print(f"\nSignal Distribution:")
                print(signals['signal'].value_counts().to_string())
            
            if 'underlying' in signals.columns:
                print(f"\nBy Underlying:")
                print(signals['underlying'].value_counts().to_string())
                
            # Show confidence distribution
            conf_cols = [c for c in signals.columns if 'confidence' in c.lower() or 'score' in c.lower()]
            if conf_cols:
                print(f"\nConfidence/Score Stats:")
                for col in conf_cols[:3]:  # Show first 3
                    try:
                        print(f"{col}: mean={signals[col].mean():.3f}, min={signals[col].min():.3f}, max={signals[col].max():.3f}")
                    except:
                        pass
        except Exception as e:
            print(f"Error reading signals: {e}")
    else:
        print("No signals file found")
    
    # 4. Check System Heartbeat
    print("\n\n[4] SYSTEM HEARTBEAT")
    print("-"*80)
    hb_file = 'system3_daily_heartbeat.json'
    if os.path.exists(hb_file):
        try:
            with open(hb_file, 'r') as f:
                hb = json.load(f)
            print(f"Last Update: {hb.get('last_update', 'Unknown')}")
            print(f"Status: {hb.get('status', 'Unknown')}")
            print(f"Cycle Count: {hb.get('cycle_count', 'Unknown')}")
        except Exception as e:
            print(f"Error reading heartbeat: {e}")
    else:
        print("No heartbeat file found")
    
    # 5. Forward Returns Analysis (Predictions vs Actual)
    print("\n\n[5] PREDICTION ACCURACY (Forward Returns)")
    print("-"*80)
    fwd_file = 'storage/live/angel_index_ai_signals_with_forward.csv'
    if os.path.exists(fwd_file):
        try:
            fwd = pd.read_csv(fwd_file)
            print(f"Total Records with Forward Returns: {len(fwd)}")
            
            # Check prediction vs actual
            pred_cols = [c for c in fwd.columns if 'pred' in c.lower() or 'ml_' in c.lower()]
            fwd_cols = [c for c in fwd.columns if 'fwd_ret' in c.lower()]
            
            if fwd_cols:
                print(f"\nForward Return Columns: {fwd_cols}")
                for col in fwd_cols:
                    try:
                        returns = fwd[col].dropna()
                        if len(returns) > 0:
                            positive = (returns > 0).sum()
                            negative = (returns < 0).sum()
                            print(f"\n{col}:")
                            print(f"  Mean: {returns.mean():.4f}")
                            print(f"  Positive: {positive} ({positive/len(returns)*100:.1f}%)")
                            print(f"  Negative: {negative} ({negative/len(returns)*100:.1f}%)")
                    except Exception as e:
                        print(f"  Error analyzing {col}: {e}")
            
            if pred_cols:
                print(f"\nPrediction Columns: {pred_cols[:5]}")
                
        except Exception as e:
            print(f"Error reading forward returns: {e}")
    else:
        print("No forward returns file found")
    
    # 6. Live Reconciliation
    print("\n\n[6] SIGNAL RECONCILIATION")
    print("-"*80)
    rec_file = 'storage/live/angel_index_ai_signals_reconciled.csv'
    if os.path.exists(rec_file):
        try:
            rec = pd.read_csv(rec_file)
            print(f"Reconciled Records: {len(rec)}")
            
            if 'reconciled_label' in rec.columns:
                print(f"\nReconciliation Results:")
                print(rec['reconciled_label'].value_counts().to_string())
        except Exception as e:
            print(f"Error reading reconciliation: {e}")
    else:
        print("No reconciliation file found")
    
    print("\n" + "="*80)
    print("Dashboard refresh complete. Run again for updates.")
    print("="*80)

if __name__ == '__main__':
    main()
