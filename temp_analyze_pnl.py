import pandas as pd
from datetime import datetime

# Load data
df = pd.read_csv('storage/live/angel_virtual_orders_with_pnl.csv')

# Filter today's trades
today = df[df['ts'].str.contains('2025-12-08', na=False)]

print('=' * 70)
print('TODAY PAPER TRADING PERFORMANCE - 2025-12-08')
print('=' * 70)

if len(today) == 0:
    print('\n⚠️  NO TRADES EXECUTED TODAY')
    print('\nPossible reasons:')
    print('  - System not running during market hours (9:15-15:30)')
    print('  - No signals generated')
    print('  - DRY-RUN mode prevented order placement')
else:
    # Calculate metrics using forward returns
    total_trades = len(today)
    
    # Use fwd_ret_1 as the performance metric
    valid_ret = today[today['fwd_ret_1'].notna()]
    
    if len(valid_ret) == 0:
        print('\n⚠️  NO RETURNS DATA AVAILABLE')
        print('  Positions opened but not yet closed or tracked')
    else:
        winners = len(valid_ret[valid_ret['fwd_ret_1'] > 0])
        losers = len(valid_ret[valid_ret['fwd_ret_1'] < 0])
        breakeven = len(valid_ret[valid_ret['fwd_ret_1'] == 0])
        
        win_rate = (winners / len(valid_ret) * 100) if len(valid_ret) > 0 else 0
        
        total_pnl_pct = valid_ret['fwd_ret_1'].sum()
        avg_pnl = valid_ret['fwd_ret_1'].mean()
        
        best_trade = valid_ret['fwd_ret_1'].max()
        worst_trade = valid_ret['fwd_ret_1'].min()
        
        # PnL in rupees from fwd_pnl_1
        total_pnl_rs = valid_ret['fwd_pnl_1'].sum() if 'fwd_pnl_1' in valid_ret.columns else 0
        
        print(f'\n📊 TRADE STATISTICS')
        print(f'  Total Positions: {total_trades}')
        print(f'  With Returns Data: {len(valid_ret)}')
        print(f'  🟢 Winners: {winners} ({winners/len(valid_ret)*100:.1f}%)')
        print(f'  🔴 Losers: {losers} ({losers/len(valid_ret)*100:.1f}%)')
        print(f'  ⚪ Break-even: {breakeven}')
        
        print(f'\n💰 PERFORMANCE')
        print(f'  Total PnL: ₹{total_pnl_rs:,.2f}')
        print(f'  Total PnL %: {total_pnl_pct:.2f}%')
        print(f'  Average per Trade: {avg_pnl:.2f}%')
        print(f'  Win Rate: {win_rate:.1f}%')
        
        print(f'\n📈 BEST/WORST')
        print(f'  Best Trade: +{best_trade:.2f}%')
        print(f'  Worst Trade: {worst_trade:.2f}%')
        print(f'  Risk/Reward Ratio: {abs(best_trade/worst_trade):.2f}' if worst_trade != 0 else '')
        
        print('\n' + '=' * 70)
        print('BREAKDOWN BY UNDERLYING')
        print('=' * 70)
        
        und_summary = valid_ret.groupby('underlying').agg({
            'fwd_ret_1': ['count', 'mean', 'sum']
        }).round(2)
        
        und_summary.columns = ['Trades', 'Avg_%', 'Total_%']
        print(und_summary)
        
        print('\n' + '=' * 70)
        print('BREAKDOWN BY SIDE (BUY/SELL)')
        print('=' * 70)
        
        side_summary = valid_ret.groupby('side').agg({
            'fwd_ret_1': ['count', 'mean', 'sum']
        }).round(2)
        
        side_summary.columns = ['Trades', 'Avg_%', 'Total_%']
        print(side_summary)
        
        print('\n' + '=' * 70)
        print('BREAKDOWN BY OPTION TYPE (CE/PE)')
        print('=' * 70)
        
        opt_summary = valid_ret.groupby('option_type').agg({
            'fwd_ret_1': ['count', 'mean', 'sum']
        }).round(2)
        
        opt_summary.columns = ['Trades', 'Avg_%', 'Total_%']
        print(opt_summary)
        
        print('\n' + '=' * 70)
        print('🎯 CORE FINDINGS')
        print('=' * 70)
        
        if win_rate >= 60:
            print('✅ Win rate STRONG (≥60%)')
        elif win_rate >= 50:
            print('🟡 Win rate ACCEPTABLE (50-60%)')
        else:
            print('🔴 Win rate WEAK (<50%)')
        
        if total_pnl_pct > 0:
            print('✅ Net PROFITABLE today')
        else:
            print('🔴 Net LOSS today')
        
        if avg_pnl > 0:
            print('✅ Average trade POSITIVE')
        else:
            print('🔴 Average trade NEGATIVE')
        
        # Check if any underlying is problematic
        bad_und = und_summary[und_summary['Total_%'] < 0]
        if len(bad_und) > 0:
            print(f'\n⚠️  LOSING UNDERLYING: {list(bad_und.index)}')
        
        # Risk analysis
        if abs(worst_trade) > best_trade * 2:
            print('⚠️  Worst loss exceeds best win by 2x - Review risk management')
        
        # Additional context
        print(f'\n📌 CONTEXT:')
        print(f'  Total positions opened: {total_trades}')
        print(f'  Positions with P&L: {len(valid_ret)} ({len(valid_ret)/total_trades*100:.1f}%)')
        print(f'  Positions pending: {total_trades - len(valid_ret)}')
