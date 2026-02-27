"""
Replay Engine - Generates realistic option chain snapshots for simulation
"""
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Literal
import sys
import random

ROOT_DIR = Path(__file__).parent.parent.parent  # src/sim -> src -> root
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger

IST = pytz.timezone('Asia/Kolkata')

# Scenario types
ScenarioType = Literal[
    "TREND_UP", "TREND_DOWN", "RANGE", "HIGH_VOL", 
    "LOW_LIQUIDITY", "DATA_ERROR", "WS_FAIL", "PARTIAL_FAILURE"
]


class ReplayEngine:
    """
    Generates realistic option chain snapshots for simulation.
    """
    
    def __init__(self, base_csv_path: Optional[Path] = None):
        """
        Initialize replay engine.
        
        Args:
            base_csv_path: Path to base CSV file (default: storage/live/option_chain_ALL_INDICES.csv)
        """
        if base_csv_path is None:
            # Try multiple possible locations
            possible_paths = [
                ROOT_DIR / "storage" / "live" / "option_chain_ALL_INDICES.csv",
                ROOT_DIR / "outputs" / "option_chain_ALL_INDICES.csv",
                ROOT_DIR / "option_chain_ALL_INDICES.csv"
            ]
            
            base_csv_path = None
            for path in possible_paths:
                if path.exists():
                    base_csv_path = path
                    break
            
            if base_csv_path is None:
                # Use the first path as default
                base_csv_path = possible_paths[0]
        
        self.base_csv_path = Path(base_csv_path)
        self.base_df = None
        self.current_snapshot = {}
        self.cycle_count = 0
        
        # Load base data
        self._load_base_data()
    
    def _load_base_data(self):
        """Load base CSV data."""
        if not self.base_csv_path.exists():
            logger.error(f"Base CSV not found: {self.base_csv_path}")
            raise FileNotFoundError(f"Base CSV not found: {self.base_csv_path}")
        
        logger.info(f"Loading base data from {self.base_csv_path}")
        self.base_df = pd.read_csv(self.base_csv_path)
        logger.info(f"Loaded {len(self.base_df)} rows, {len(self.base_df.columns)} columns")
        
        # Initialize current snapshot
        for underlying in self.base_df['underlying'].unique():
            df_underlying = self.base_df[self.base_df['underlying'] == underlying].copy()
            self.current_snapshot[underlying] = df_underlying
    
    def generate_snapshot(
        self,
        scenario: ScenarioType,
        cycle: int,
        total_cycles: int,
        inject_errors: bool = False
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate a realistic snapshot for given scenario.
        
        Args:
            scenario: Scenario type
            cycle: Current cycle number (0-based)
            total_cycles: Total cycles in simulation
            inject_errors: Whether to inject data errors (for DATA_ERROR scenario)
        
        Returns:
            Dict mapping underlying -> DataFrame
        """
        self.cycle_count = cycle
        progress = cycle / total_cycles if total_cycles > 0 else 0.0
        
        result = {}
        
        for underlying in self.current_snapshot.keys():
            df = self.current_snapshot[underlying].copy()
            
            # Skip if PARTIAL_FAILURE scenario and this is SENSEX
            if scenario == "PARTIAL_FAILURE" and underlying == "SENSEX" and cycle > 5:
                logger.warning(f"Simulating failure for {underlying} in PARTIAL_FAILURE scenario")
                continue
            
            # Apply scenario-specific transformations (pass cycle for timestamp)
            df = self._apply_scenario(df, scenario, progress, inject_errors, cycle)
            
            # Update current snapshot
            self.current_snapshot[underlying] = df.copy()
            
            result[underlying] = df
        
        return result
    
    def _apply_scenario(
        self,
        df: pd.DataFrame,
        scenario: ScenarioType,
        progress: float,
        inject_errors: bool,
        cycle: int = 0
    ) -> pd.DataFrame:
        """Apply scenario-specific transformations."""
        
        # Get base spot price
        if 'spot_price' in df.columns and df['spot_price'].notna().any():
            base_spot = df['spot_price'].iloc[0]
        else:
            base_spot = 25000.0  # Default
        
        # Scenario-specific spot movement
        if scenario == "TREND_UP":
            spot_change_pct = 0.5 + progress * 1.5  # 0.5% to 2% up
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 1.0 + progress * 0.3  # Increasing volatility
        
        elif scenario == "TREND_DOWN":
            spot_change_pct = -0.3 - progress * 1.2  # -0.3% to -1.5% down
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 1.0 + progress * 0.4
        
        elif scenario == "RANGE":
            # Oscillate around base
            spot_change_pct = 0.3 * np.sin(progress * 4 * np.pi)
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 0.8
        
        elif scenario == "HIGH_VOL":
            # Whipsaw movements
            spot_change_pct = 0.5 * np.sin(progress * 8 * np.pi) + 0.2 * random.gauss(0, 1)
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 2.0 + progress * 1.0
        
        elif scenario == "LOW_LIQUIDITY":
            spot_change_pct = 0.1 * progress
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 0.9
        
        else:  # DATA_ERROR, WS_FAIL, PARTIAL_FAILURE
            spot_change_pct = 0.1 * progress
            spot = base_spot * (1 + spot_change_pct / 100)
            volatility_mult = 1.0
        
        # Update spot price
        df['spot_price'] = spot
        
        # Update each contract
        for idx in df.index:
            row = df.loc[idx]
            strike = row.get('strike', 0)
            option_type = row.get('option_type', 'CE')
            
            # Calculate moneyness
            if option_type == 'CE':
                intrinsic = max(0, spot - strike)
                is_itm = spot > strike
            else:  # PE
                intrinsic = max(0, strike - spot)
                is_itm = strike > spot
            
            # Base IV (use existing or default)
            base_iv = row.get('iv', 0.20) if pd.notna(row.get('iv')) else 0.20
            iv = base_iv * volatility_mult
            
            # Calculate theoretical price using Black-Scholes approximation
            time_to_exp = row.get('time_to_expiry', 0.065) if pd.notna(row.get('time_to_expiry')) else 0.065
            if time_to_exp <= 0:
                time_to_exp = 0.065
            
            # Simple Black-Scholes approximation
            from src.metrics.iv_solver import black_scholes_price
            theoretical_price = black_scholes_price(
                spot, strike, time_to_exp, 0.06, iv, option_type
            )
            
            # Add noise and market dynamics
            price_noise = random.gauss(0, theoretical_price * 0.02)  # 2% noise
            ltp = max(0.05, theoretical_price + price_noise)
            
            # Update LTP
            df.loc[idx, 'ltp'] = ltp
            
            # Update OHLC
            if pd.isna(row.get('open')) or progress == 0:
                df.loc[idx, 'open'] = ltp
            df.loc[idx, 'high'] = max(df.loc[idx, 'high'] if pd.notna(row.get('high')) else ltp, ltp)
            df.loc[idx, 'low'] = min(df.loc[idx, 'low'] if pd.notna(row.get('low')) else ltp, ltp)
            df.loc[idx, 'close'] = ltp
            
            # Update volume (realistic growth)
            base_volume = row.get('volume', 1000) if pd.notna(row.get('volume')) else 1000
            volume_change = random.randint(-100, 500) * (1 + progress)
            volume = max(0, int(base_volume + volume_change))
            df.loc[idx, 'volume'] = volume
            
            # Update OI (based on scenario)
            base_oi = row.get('oi', 10000) if pd.notna(row.get('oi')) else 10000
            if scenario == "TREND_UP" and is_itm:
                oi_change = random.randint(500, 2000)  # Long buildup
            elif scenario == "TREND_DOWN" and not is_itm:
                oi_change = random.randint(500, 2000)  # Short buildup
            elif scenario == "RANGE":
                oi_change = random.randint(-500, 500)  # Neutral
            else:
                oi_change = random.randint(-200, 800)
            
            oi = max(0, int(base_oi + oi_change * (1 + progress * 0.5)))
            df.loc[idx, 'oi'] = oi
            
            # Update bid/ask with realistic spreads
            spread_pct = 0.5 if scenario != "LOW_LIQUIDITY" else 3.0  # Wide spreads for low liquidity
            spread = ltp * spread_pct / 100
            
            mid_price = ltp
            bid_price = max(0.05, mid_price - spread / 2)
            ask_price = mid_price + spread / 2
            
            df.loc[idx, 'bidPrice'] = bid_price
            df.loc[idx, 'offerPrice'] = ask_price
            df.loc[idx, 'mid_price'] = mid_price
            df.loc[idx, 'bid_ask_spread'] = spread
            df.loc[idx, 'bid_ask_spread_pct'] = spread_pct
            
            # Update Greeks (if available)
            from src.metrics.greeks import calculate_greeks
            try:
                greeks = calculate_greeks(spot, strike, time_to_exp, 0.06, iv, option_type)
                df.loc[idx, 'delta'] = greeks['delta']
                df.loc[idx, 'gamma'] = greeks['gamma']
                df.loc[idx, 'theta'] = greeks['theta']
                df.loc[idx, 'vega'] = greeks['vega']
                df.loc[idx, 'rho'] = greeks['rho']
                df.loc[idx, 'iv'] = iv
            except:
                pass
            
            # Update intrinsic/extrinsic
            df.loc[idx, 'intrinsic_value'] = intrinsic
            df.loc[idx, 'extrinsic_value'] = ltp - intrinsic
            
            # Update moneyness
            if is_itm:
                df.loc[idx, 'moneyness'] = 'ITM'
            elif abs(spot - strike) / spot < 0.02:
                df.loc[idx, 'moneyness'] = 'ATM'
            else:
                df.loc[idx, 'moneyness'] = 'OTM'
            
            # Inject errors for DATA_ERROR scenario
            if inject_errors and random.random() < 0.15:  # 15% error rate
                error_type = random.choice(['ask_below_bid', 'missing_iv', 'missing_oi', 'nan_field', 'stale_timestamp'])
                
                if error_type == 'ask_below_bid':
                    df.loc[idx, 'offerPrice'] = bid_price * 0.9  # Ask below bid
                elif error_type == 'missing_iv':
                    df.loc[idx, 'iv'] = None
                elif error_type == 'missing_oi':
                    df.loc[idx, 'oi'] = None
                elif error_type == 'nan_field':
                    df.loc[idx, 'ltp'] = None  # Missing LTP
                elif error_type == 'stale_timestamp':
                    # Keep old timestamp (handled in timestamp update)
                    pass
        
        # Update timestamps
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST) + timedelta(seconds=cycle * 5)  # 5s per cycle
        
        df['fetch_timestamp'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
        df['fetch_timestamp_iso'] = now.isoformat()
        df['fetch_date'] = now.strftime('%Y-%m-%d')
        df['fetch_time'] = now.strftime('%H:%M:%S')
        
        # Recalculate calculated columns that depend on updated values
        from core.utils.option_chain_calculations import add_calculated_columns
        try:
            df = add_calculated_columns(df, fetch_timestamp=df['fetch_timestamp'].iloc[0])
        except Exception as e:
            logger.warning(f"Failed to recalculate columns: {e}")
        
        return df
    
    def reset(self):
        """Reset to base state."""
        self._load_base_data()
        self.cycle_count = 0
