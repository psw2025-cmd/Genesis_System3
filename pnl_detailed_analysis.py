#!/usr/bin/env python3
"""
DETAILED PNL ANALYSIS - Paper Trading vs Live Data
"""
import pandas as pd
import os
from datetime import datetime

def main():
    print("="*100)
    print("  SYSTEM3 PROFIT/LOSS ANALYSIS - PAPER TRADING PERFORMANCE")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*100)
    
    # 1. Load PnL Data
    pnl_file = 'storage/live/angel_index_ai_pnl_log.csv'
    if not os.path.exists(pnl_file):
        print("\n❌ No PnL data found yet")
        return
    
    pnl = pd.read_csv(pnl_file)
    print(f"\n📊 Total Trades Analyzed: {len(pnl)}")
    
    # 2. Overall Performance
    print("\n" + "="*100)
    print("  OVERALL PERFORMANCE")
    print("="*100)
    
    if 'pnl_pct' in pnl.columns:
        total_pnl = pnl['pnl_pct'].sum()
        avg_pnl = pnl['pnl_pct'].mean()
        median_pnl = pnl['pnl_pct'].median()
        
        winners = pnl[pnl['pnl_pct'] > 0]
        losers = pnl[pnl['pnl_pct'] < 0]
        
        win_rate = len(winners) / len(pnl) * 100 if len(pnl) > 0 else 0
        
        print(f"Total PnL:        {total_pnl:+.2f}%")
        print(f"Average PnL:      {avg_pnl:+.2f}%")
        print(f"Median PnL:       {median_pnl:+.2f}%")
        print(f"\nWin Rate:         {win_rate:.1f}% ({len(winners)} wins / {len(losers)} losses)")
        
        if len(winners) > 0:
            print(f"Avg Win:          +{winners['pnl_pct'].mean():.2f}%")
            print(f"Best Win:         +{winners['pnl_pct'].max():.2f}%")
        
        if len(losers) > 0:
            print(f"Avg Loss:         {losers['pnl_pct'].mean():.2f}%")
            print(f"Worst Loss:       {losers['pnl_pct'].min():.2f}%")
        
        # Risk/Reward
        if len(winners) > 0 and len(losers) > 0:
            avg_win_amt = abs(winners['pnl_pct'].mean())
            avg_loss_amt = abs(losers['pnl_pct'].mean())
            rr_ratio = avg_win_amt / avg_loss_amt if avg_loss_amt > 0 else 0
            print(f"\nRisk/Reward:      {rr_ratio:.2f}:1")
    
    # 3. By Result Type
    print("\n" + "="*100)
    print("  OUTCOME DISTRIBUTION")
    print("="*100)
    
    if 'result' in pnl.columns:
        print("\nTrade Outcomes:")
        result_counts = pnl['result'].value_counts()
        for outcome, count in result_counts.items():
            pct = count / len(pnl) * 100
            print(f"  {outcome:12s}: {count:3d} ({pct:5.1f}%)")
    
    # 4. By Underlying
    print("\n" + "="*100)
    print("  PERFORMANCE BY UNDERLYING")
    print("="*100)
    
    if 'underlying' in pnl.columns and 'pnl_pct' in pnl.columns:
        by_underlying = pnl.groupby('underlying')['pnl_pct'].agg(['count', 'sum', 'mean', 'std']).round(2)
        by_underlying = by_underlying.sort_values('sum', ascending=False)
        print("\n", by_underlying.to_string())
    
    # 5. By Side (CE/PE)
    print("\n" + "="*100)
    print("  PERFORMANCE BY OPTION TYPE")
    print("="*100)
    
    if 'side' in pnl.columns and 'pnl_pct' in pnl.columns:
        by_side = pnl.groupby('side')['pnl_pct'].agg(['count', 'sum', 'mean']).round(2)
        print("\n", by_side.to_string())
    
    # 6. Prediction Accuracy
    print("\n" + "="*100)
    print("  ML PREDICTION ACCURACY")
    print("="*100)
    
    if 'pred_label' in pnl.columns and 'pnl_pct' in pnl.columns:
        # Check if predictions matched actual outcome
        pnl['correct'] = ((pnl['pred_label'].str.contains('BUY', na=False)) & (pnl['pnl_pct'] > 0)) | \
                        ((pnl['pred_label'].str.contains('SELL', na=False)) & (pnl['pnl_pct'] < 0))
        
        accuracy = pnl['correct'].mean() * 100 if len(pnl) > 0 else 0
        print(f"\nPrediction Accuracy: {accuracy:.1f}%")
        print(f"Correct Predictions: {pnl['correct'].sum()} / {len(pnl)}")
        
        # By confidence level
        if 'pred_confidence' in pnl.columns:
            print("\n\nPnL by Confidence Level:")
            pnl['conf_bucket'] = pd.cut(pnl['pred_confidence'], bins=[0, 0.5, 0.6, 0.7, 0.8, 1.0],
                                       labels=['<50%', '50-60%', '60-70%', '70-80%', '>80%'])
            by_conf = pnl.groupby('conf_bucket')['pnl_pct'].agg(['count', 'mean']).round(2)
            print(by_conf.to_string())
    
    # 7. Drawdown Analysis
    print("\n" + "="*100)
    print("  DRAWDOWN ANALYSIS")
    print("="*100)
    
    if 'max_adv_pct' in pnl.columns:
        max_drawdown = pnl['max_adv_pct'].min()
        avg_drawdown = pnl[pnl['max_adv_pct'] < 0]['max_adv_pct'].mean() if len(pnl[pnl['max_adv_pct'] < 0]) > 0 else 0
        
        print(f"Max Drawdown:     {max_drawdown:.2f}%")
        print(f"Avg Drawdown:     {avg_drawdown:.2f}%")
    
    # 8. Recent Trades
    print("\n" + "="*100)
    print("  RECENT TRADES (Last 10)")
    print("="*100)
    
    display_cols = ['ts', 'underlying', 'side', 'entry_price', 'exit_price', 
                   'pnl_pct', 'result', 'pred_confidence']
    available_cols = [c for c in display_cols if c in pnl.columns]
    
    if available_cols:
        print("\n", pnl[available_cols].tail(10).to_string(index=False))
    
    # 9. Forward Returns Analysis
    print("\n" + "="*100)
    print("  FORWARD RETURNS ANALYSIS (Live Data Comparison)")
    print("="*100)
    
    fwd_file = 'storage/live/angel_index_ai_signals_with_forward.csv'
    if os.path.exists(fwd_file):
        fwd = pd.read_csv(fwd_file)
        print(f"\nTotal signals with forward returns tracked: {len(fwd)}")
        
        fwd_cols = [c for c in fwd.columns if 'fwd_ret' in c.lower()]
        if fwd_cols:
            print("\nForward Return Performance:")
            for col in fwd_cols:
                returns = fwd[col].dropna()
                if len(returns) > 0:
                    positive = (returns > 0).sum()
                    negative = (returns < 0).sum()
                    mean_ret = returns.mean()
                    print(f"\n{col:12s}: {len(returns):4d} samples, Mean: {mean_ret:+.4f}, "
                          f"Positive: {positive:3d} ({positive/len(returns)*100:.1f}%), "
                          f"Negative: {negative:3d} ({negative/len(returns)*100:.1f}%)")
    else:
        print("\nNo forward returns file found")
    
    # 10. Summary Stats
    print("\n" + "="*100)
    print("  EXECUTIVE SUMMARY")
    print("="*100)
    
    if 'pnl_pct' in pnl.columns:
        print(f"\n✅ Total Trades:    {len(pnl)}")
        print(f"📈 Win Rate:        {win_rate:.1f}%")
        print(f"💰 Total Return:    {total_pnl:+.2f}%")
        print(f"📊 Avg Per Trade:   {avg_pnl:+.2f}%")
        
        if accuracy > 0:
            print(f"🎯 ML Accuracy:     {accuracy:.1f}%")
        
        if len(pnl) >= 3:
            status = "✅ PROFITABLE" if total_pnl > 0 else "⚠️  LOSING" if total_pnl < -2 else "➖ FLAT"
            print(f"\n{status}")
        else:
            print("\n⏳ Insufficient data for final assessment")
    
    print("\n" + "="*100)

if __name__ == '__main__':
    main()
