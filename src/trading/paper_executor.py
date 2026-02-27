"""
Paper Trading Executor - Executes trades in simulation mode
Simulates realistic trade execution with slippage and fills
"""
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import pytz

ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class PaperExecutor:
    """
    Executes paper trades based on trade signals.
    Simulates realistic execution with slippage.
    """
    
    def __init__(
        self,
        slippage_pct: float = 0.1,  # 0.1% slippage
        lot_size: int = 1,
        max_positions: int = 5
    ):
        """
        Initialize paper executor.
        
        Args:
            slippage_pct: Slippage percentage (default: 0.1%)
            lot_size: Default lot size per trade (default: 1)
            max_positions: Maximum concurrent positions (default: 5)
        """
        self.slippage_pct = slippage_pct
        self.lot_size = lot_size
        self.max_positions = max_positions
        self.positions = {}  # {position_id: position_dict}
        self.trade_history = []
        self.next_position_id = 1
        
    def execute_trade(
        self,
        trade_signal: Dict,
        current_data: pd.DataFrame,
        cycle_timestamp: str
    ) -> Optional[Dict]:
        """
        Execute a paper trade based on signal.
        
        Args:
            trade_signal: Trade signal dict from strategy engine
            current_data: Current option chain DataFrame
            cycle_timestamp: Current cycle timestamp
            
        Returns:
            Position dict if trade executed, None otherwise
        """
        if trade_signal.get('action') != 'TRADE':
            return None
        
        # Check max positions
        if len(self.positions) >= self.max_positions:
            logger.warning(f"Max positions ({self.max_positions}) reached, skipping trade")
            return None
        
        # Get contract details
        tokens = trade_signal.get('tokens', [])
        strikes = trade_signal.get('strikes', [])
        strategy = trade_signal.get('strategy', '')
        underlying = trade_signal.get('underlying', '')
        
        if not tokens or not strikes:
            logger.warning("No tokens or strikes in trade signal")
            return None
        
        # Find contract in current data
        contract = None
        for token in tokens:
            contract_row = current_data[current_data['token'].astype(str) == str(token)]
            if not contract_row.empty:
                contract = contract_row.iloc[0]
                break
        
        if contract is None:
            logger.warning(f"Contract not found in current data for tokens {tokens}")
            return None
        
        # Calculate entry price with slippage
        entry_mid = trade_signal.get('entry_mid', contract.get('mid_price', contract.get('ltp', 0)))
        
        # Apply slippage (buy at ask, sell at bid)
        if strategy in ['BUY_CE', 'BUY_PE']:
            # Buying: pay ask price + slippage
            ask_price = contract.get('offerPrice', entry_mid)
            entry_price = ask_price * (1 + self.slippage_pct / 100)
        else:
            # Selling: receive bid price - slippage
            bid_price = contract.get('bidPrice', entry_mid)
            entry_price = bid_price * (1 - self.slippage_pct / 100)
        
        # Get lot size
        lot_size = contract.get('lotSize', self.lot_size)
        if pd.isna(lot_size):
            lot_size = self.lot_size
        
        # Calculate quantity using position sizing
        from src.trading.advanced_position_sizing import AdvancedPositionSizing
        
        sizing = AdvancedPositionSizing()
        size_result = sizing.calculate_optimal_size(
            entry_price=entry_price,
            stop_loss_price=trade_signal.get('stop_loss', entry_price * 0.96),
            confidence=trade_signal.get('confidence', 0.8),
            iv=contract.get('iv', 0.20),
            win_rate=trade_signal.get('win_rate', 0.9),
            avg_win_pct=trade_signal.get('avg_win_pct', 0.5),
            avg_loss_pct=trade_signal.get('avg_loss_pct', 0.04)
        )
        
        # Use calculated quantity, ensure minimum 1 lot
        calculated_qty = max(1, int(size_result['quantity']))
        qty = int(calculated_qty * lot_size)  # Convert to shares
        
        # Create position
        position_id = f"POS_{self.next_position_id:04d}"
        self.next_position_id += 1
        
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        position = {
            'position_id': position_id,
            'underlying': underlying,
            'symbol': str(contract.get('symbol', '')),
            'token': str(contract.get('token', '')),
            'strike': float(strikes[0]),
            'option_type': str(contract.get('option_type', '')),
            'strategy': strategy,
            'entry_price': float(entry_price),
            'entry_mid': float(entry_mid),
            'entry_timestamp': cycle_timestamp,
            'entry_time_ist': now.strftime('%Y-%m-%d %H:%M:%S IST'),
            'qty': qty,
            'quantity': qty,  # Also store as 'quantity' for compatibility
            'lot_size': int(lot_size),
            'stop_loss': float(trade_signal.get('stop_loss', entry_price * 0.7)),
            'target': float(trade_signal.get('target', entry_price * 1.5)),
            'current_price': float(entry_price),
            'current_mid': float(entry_mid),
            'unrealized_pnl': 0.0,
            'unrealized_pnl_pct': 0.0,
            'status': 'OPEN',
            'confidence': float(trade_signal.get('confidence', 0.0))
        }
        
        self.positions[position_id] = position
        
        # Log trade
        logger.info(
            f"PAPER TRADE EXECUTED: {position_id} | {underlying} {strikes[0]} {contract.get('option_type')} | "
            f"Entry: ₹{entry_price:.2f} | Qty: {qty} | Strategy: {strategy}"
        )
        
        # Add to trade history
        trade_history_entry = {
            'position_id': position_id,
            'action': 'OPEN',
            'timestamp': cycle_timestamp,
            'time_ist': now.strftime('%Y-%m-%d %H:%M:%S IST'),
            'underlying': underlying,
            'strike': float(strikes[0]),
            'option_type': str(contract.get('option_type', '')),
            'price': float(entry_price),
            'qty': qty,
            'strategy': strategy
        }
        self.trade_history.append(trade_history_entry)
        
        # Log to comprehensive trade logger
        try:
            from dashboard.backend.trade_logger import log_trade_event
            log_trade_event(
                event_type='TRADE_EXECUTED',
                position_id=position_id,
                underlying=underlying,
                symbol=str(contract.get('symbol', '')),
                strike=float(strikes[0]),
                option_type=str(contract.get('option_type', '')),
                action='OPEN',
                entry_price=float(entry_price),
                qty=qty,
                strategy=strategy,
                timestamp=cycle_timestamp
            )
        except Exception as e:
            logger.debug(f"Failed to log trade event: {e}")
        
        return position
    
    def update_positions(
        self,
        all_data: Dict[str, pd.DataFrame],
        cycle_timestamp: str
    ) -> List[Dict]:
        """
        Update all open positions with current prices and PnL.
        
        Args:
            all_data: Dict of {underlying: DataFrame} with current option chain
            cycle_timestamp: Current cycle timestamp
            
        Returns:
            List of closed positions
        """
        closed_positions = []
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        
        for position_id, position in list(self.positions.items()):
            if position['status'] != 'OPEN':
                continue
            
            # Find contract in current data
            underlying = position['underlying']
            token = position['token']
            
            if underlying not in all_data:
                continue
            
            df = all_data[underlying]
            contract = df[df['token'].astype(str) == str(token)]
            
            if contract.empty:
                # Contract not found, use last known price
                current_price = position['current_price']
                current_mid = position['current_mid']
            else:
                contract = contract.iloc[0]
                current_mid = float(contract.get('mid_price', contract.get('ltp', position['current_price'])))
                
                # For PnL calculation, use mid price
                current_price = current_mid
            
            # Update position
            position['current_price'] = current_price
            position['current_mid'] = current_mid
            
            # Calculate unrealized PnL
            entry_price = position['entry_price']
            qty = position['qty']
            
            # PnL depends on strategy
            if position['strategy'] in ['BUY_CE', 'BUY_PE']:
                # Long position: profit if price goes up
                pnl = (current_price - entry_price) * qty
            else:
                # Short position: profit if price goes down
                pnl = (entry_price - current_price) * qty
            
            pnl_pct = ((current_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
            
            position['unrealized_pnl'] = float(pnl)
            position['unrealized_pnl_pct'] = float(pnl_pct)
            position['last_update'] = cycle_timestamp
            position['last_update_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
            
            # Check stop loss / target
            should_close = False
            exit_reason = None
            
            # For long positions (BUY_CE, BUY_PE)
            if position['strategy'] in ['BUY_CE', 'BUY_PE']:
                # Long position: close if price drops to SL or rises to target
                if current_price <= position['stop_loss']:
                    should_close = True
                    exit_reason = 'STOP_LOSS'
                elif current_price >= position['target']:
                    should_close = True
                    exit_reason = 'TARGET'
            # For other strategies, use timeout or manual close for now
            # (spreads and other complex strategies need more logic)
            
            if should_close:
                # Close position
                position['status'] = 'CLOSED'
                position['exit_price'] = current_price
                position['exit_timestamp'] = cycle_timestamp
                position['exit_time_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
                position['realized_pnl'] = float(pnl)
                position['realized_pnl_pct'] = float(pnl_pct)
                position['exit_reason'] = exit_reason
                
                closed_positions.append(position.copy())
                
                # Remove from open positions
                del self.positions[position_id]
                
                # Add to trade history
                trade_history_entry = {
                    'position_id': position_id,
                    'action': 'CLOSE',
                    'timestamp': cycle_timestamp,
                    'time_ist': now.strftime('%Y-%m-%d %H:%M:%S IST'),
                    'underlying': underlying,
                    'strike': position['strike'],
                    'option_type': position['option_type'],
                    'price': float(current_price),  # Ensure float conversion
                    'qty': qty,
                    'exit_reason': exit_reason,
                    'realized_pnl': float(pnl),
                    'realized_pnl_pct': float(pnl_pct),
                    'entry_price': float(position['entry_price']),
                    'exit_price': float(current_price)
                }
                self.trade_history.append(trade_history_entry)
                
                logger.info(
                    f"PAPER TRADE CLOSED: {position_id} | {underlying} | "
                    f"Exit: ₹{current_price:.2f} | PnL: ₹{pnl:.2f} ({pnl_pct:.2f}%) | Reason: {exit_reason}"
                )
                
                # Log to comprehensive trade logger
                try:
                    from dashboard.backend.trade_logger import log_trade_event
                    log_trade_event(
                        event_type='TRADE_CLOSED',
                        position_id=position_id,
                        underlying=underlying,
                        symbol=position.get('symbol', ''),
                        strike=position['strike'],
                        option_type=position['option_type'],
                        action='CLOSE',
                        entry_price=float(position['entry_price']),
                        exit_price=float(current_price),
                        qty=qty,
                        pnl=float(pnl),
                        strategy=position.get('strategy', ''),
                        exit_reason=exit_reason,
                        timestamp=cycle_timestamp
                    )
                except Exception as e:
                    logger.debug(f"Failed to log trade close event: {e}")
        
        return closed_positions
    
    def get_positions_summary(self) -> Dict:
        """Get summary of all positions."""
        open_positions = [p for p in self.positions.values() if p['status'] == 'OPEN']
        closed_positions = [p for p in self.trade_history if p.get('action') == 'CLOSE']
        
        total_unrealized_pnl = sum(p['unrealized_pnl'] for p in open_positions)
        total_realized_pnl = sum(p.get('realized_pnl', 0) for p in closed_positions)
        
        return {
            'open_count': len(open_positions),
            'closed_count': len(closed_positions),
            'total_unrealized_pnl': float(total_unrealized_pnl),
            'total_realized_pnl': float(total_realized_pnl),
            'total_pnl': float(total_unrealized_pnl + total_realized_pnl),
            'open_positions': open_positions,
            'closed_positions': closed_positions[-10:] if closed_positions else []  # Last 10
        }
    
    def get_trade_history(self) -> List[Dict]:
        """Get complete trade history."""
        return self.trade_history.copy()
