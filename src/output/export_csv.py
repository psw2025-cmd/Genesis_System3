"""
CSV Exporters for Excel compatibility
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import pytz
from typing import Optional, Dict
import sys

# Get project root (go up from src/output/export_csv.py to project root)
ROOT_DIR = Path(__file__).parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.utils.logger import logger


class CSVExporter:
    """
    Export option chain data to CSV files for Excel import.
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize exporter.
        
        Args:
            output_dir: Output directory (default: outputs/)
        """
        if output_dir is None:
            output_dir = ROOT_DIR / "outputs"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_chain_raw(
        self,
        df: pd.DataFrame,
        filename: str = "chain_raw_live.csv"
    ) -> Path:
        """
        Export option chain to chain_raw_live.csv (Excel-ready).
        
        Args:
            df: DataFrame with option chain data
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename
        
        # Ensure required columns exist
        required_cols = [
            'underlying', 'exchange', 'token', 'symbol', 'strike', 'option_type',
            'expiry', 'ltp', 'oi', 'volume', 'bidPrice', 'offerPrice', 'mid_price',
            'delta', 'gamma', 'theta', 'vega', 'iv', 'intrinsic_value', 'extrinsic_value'
        ]
        
        # Add missing columns as None
        for col in required_cols:
            if col not in df.columns:
                df[col] = None
        
        # Select and order columns for Excel
        excel_cols = [
            'timestamp_ist', 'timestamp_epoch',
            'underlying', 'exchange', 'token', 'symbol', 'strike', 'option_type', 'expiry',
            'spot_price', 'ltp', 'oi', 'volume',
            'bidPrice', 'offerPrice', 'mid_price', 'bid_ask_spread', 'bid_ask_spread_pct',
            'intrinsic_value', 'extrinsic_value', 'intrinsic_pct',
            'atm_distance', 'atm_distance_pct',
            'delta', 'gamma', 'theta', 'vega', 'rho', 'iv',
            'dOI', 'dVolume', 'dMid', 'dLTP', 'oi_buildup',
            'days_to_expiry', 'time_to_expiry',
            'volume_oi_ratio', 'premium_pct_of_strike', 'premium_pct_of_spot'
        ]
        
        # Keep only columns that exist
        export_cols = [col for col in excel_cols if col in df.columns]
        df_export = df[export_cols].copy()
        
        # Add timestamp if missing
        if 'timestamp_ist' not in df_export.columns:
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            df_export['timestamp_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
            df_export['timestamp_epoch'] = now.timestamp()
        
        # Save to CSV
        df_export.to_csv(output_path, index=False)
        logger.info(f"Exported chain_raw to {output_path} ({len(df_export)} rows)")
        
        return output_path
    
    def export_underlying_rank(
        self,
        rankings_df: pd.DataFrame,
        filename: str = "underlying_rank_live.csv"
    ) -> Path:
        """
        Export underlying rankings.
        
        Args:
            rankings_df: DataFrame with rankings
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename
        
        # Ensure timestamp
        if 'timestamp_ist' not in rankings_df.columns:
            ist = pytz.timezone('Asia/Kolkata')
            now = datetime.now(ist)
            rankings_df['timestamp_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
            rankings_df['timestamp_epoch'] = now.timestamp()
        
        rankings_df.to_csv(output_path, index=False)
        logger.info(f"Exported rankings to {output_path}")
        
        return output_path
    
    def export_trade_signal(
        self,
        signal: Dict,
        filename: str = "top_trade_signal.json"
    ) -> Path:
        """
        Export trade signal to JSON.
        
        Args:
            signal: Trade signal dict
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        import json
        
        output_path = self.output_dir / filename
        
        # Add timestamp
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        signal['timestamp_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
        signal['timestamp_epoch'] = now.timestamp()
        
        with open(output_path, 'w') as f:
            json.dump(signal, f, indent=2, default=str)
        
        logger.info(f"Exported trade signal to {output_path}")
        
        return output_path
    
    def export_qc_report(
        self,
        qc_results: Dict,
        filename: str = "qc_report_live.json"
    ) -> Path:
        """
        Export QC report to JSON.
        
        Args:
            qc_results: QC results dict
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        import json
        
        output_path = self.output_dir / filename
        
        # Add timestamp
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        qc_results['timestamp_ist'] = now.strftime('%Y-%m-%d %H:%M:%S IST')
        qc_results['timestamp_epoch'] = now.timestamp()
        
        with open(output_path, 'w') as f:
            json.dump(qc_results, f, indent=2, default=str)
        
        logger.info(f"Exported QC report to {output_path}")
        
        return output_path
