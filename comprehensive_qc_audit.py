#!/usr/bin/env python3
"""
COMPREHENSIVE QC AUDIT FOR SYSTEM3
Deep multi-layer analysis of all data, configuration, and runtime state
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path

class ComprehensiveQCAudit:
    def __init__(self):
        self.base_path = Path("c:/Genesis_System3")
        self.findings = {
            "CRITICAL": [],
            "WARNING": [],
            "INFO": []
        }
        self.stats = {}
        
    def log_finding(self, level, code, message, details=None):
        """Log a finding with severity level"""
        finding = {
            "code": code,
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "details": details
        }
        self.findings[level].append(finding)
        print(f"[{level}] {code}: {message}")
        if details:
            print(f"     Details: {details}")
    
    def audit_signals_csv(self):
        """Deep analysis of dhan_index_ai_signals.csv"""
        print("\n" + "="*80)
        print("AUDIT: SIGNALS CSV FILE")
        print("="*80)
        
        signals_path = self.base_path / "storage" / "live" / "dhan_index_ai_signals.csv"
        
        if not signals_path.exists():
            self.log_finding("INFO", "SIG-000", "Signals CSV not present (acceptable when no live/paper data)", str(signals_path))
            return
        try:
            df = pd.read_csv(signals_path)
            
            # Basic stats
            self.stats['signals_total_rows'] = len(df)
            self.stats['signals_columns'] = len(df.columns)
            
            print(f"[OK] File exists: {signals_path}")
            print(f"  - Total rows: {len(df):,}")
            print(f"  - Total columns: {len(df.columns)}")
            print(f"  - File size: {signals_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            # Check for missing columns
            critical_cols = ['underlying', 'ai_score', 'final_score', 'signal', 'ts']
            missing = [col for col in critical_cols if col not in df.columns]
            if missing:
                self.log_finding("WARNING", "SIG-001", f"Missing critical columns in signals", f"Missing: {missing}")
            else:
                print(f"[OK] All critical columns present: {critical_cols}")
            
            # Check for NaN/None values in critical columns
            for col in critical_cols:
                if col in df.columns:
                    nan_count = df[col].isna().sum()
                    if nan_count > 0:
                        self.log_finding("WARNING", "SIG-002", f"NaN values in column '{col}'", f"Count: {nan_count}")
                    else:
                        print(f"[OK] No NaN in {col}")
            
            # Analyze ai_score distribution
            if 'ai_score' in df.columns:
                ai_scores = pd.to_numeric(df['ai_score'], errors='coerce')
                print(f"\nAI Score Distribution:")
                print(f"  - Mean: {ai_scores.mean():.6f}")
                print(f"  - Std: {ai_scores.std():.6f}")
                print(f"  - Min: {ai_scores.min():.6f}")
                print(f"  - Max: {ai_scores.max():.6f}")
                print(f"  - NaN count: {ai_scores.isna().sum()}")
                
                if ai_scores.std() < 0.01:
                    self.log_finding("WARNING", "SIG-003", "AI Score has very low variance", f"Std: {ai_scores.std()}")
            
            # Check signal distribution
            if 'signal' in df.columns:
                signal_dist = df['signal'].value_counts()
                print(f"\nSignal Distribution:")
                for signal, count in signal_dist.items():
                    print(f"  - {signal}: {count} ({count/len(df)*100:.1f}%)")
                
                # Check for imbalance
                max_signal_pct = signal_dist.iloc[0] / len(df) * 100
                if max_signal_pct > 90:
                    self.log_finding("WARNING", "SIG-004", "Extreme signal imbalance detected", 
                                   f"Dominant signal: {signal_dist.index[0]} ({max_signal_pct:.1f}%)")
            
            # Check underlying distribution
            if 'underlying' in df.columns:
                underlying_dist = df['underlying'].value_counts()
                print(f"\nUnderlying Distribution:")
                for underlying, count in underlying_dist.items():
                    print(f"  - {underlying}: {count} ({count/len(df)*100:.1f}%)")
                
                # Check for missing underlyings
                expected_underlyings = ['NIFTY', 'BANKNIFTY', 'FINNIFTY', 'MIDCPNIFTY', 'SENSEX']
                present = set(underlying_dist.index)
                missing_underlyings = [u for u in expected_underlyings if u not in present]
                if missing_underlyings:
                    self.log_finding("WARNING", "SIG-005", "Some expected underlyings missing", f"Missing: {missing_underlyings}")
                else:
                    print(f"[OK] All expected underlyings present: {expected_underlyings}")
            
            # Check timestamp freshness
            if 'ts' in df.columns:
                latest_ts = df['ts'].max()
                oldest_ts = df['ts'].min()
                print(f"\nTimestamp Range:")
                print(f"  - Latest: {latest_ts}")
                print(f"  - Oldest: {oldest_ts}")
                
                # Check for duplicate timestamps
                dup_ts = df['ts'].duplicated().sum()
                if dup_ts > 0:
                    print(f"[WARNING] Duplicate timestamps found: {dup_ts}")
            
            # Analyze final_score vs ai_score relationship
            if 'final_score' in df.columns and 'ai_score' in df.columns:
                final_scores = pd.to_numeric(df['final_score'], errors='coerce')
                ai_scores_check = pd.to_numeric(df['ai_score'], errors='coerce')
                
                correlation = final_scores.corr(ai_scores_check)
                print(f"\nFinal Score vs AI Score Correlation: {correlation:.4f}")
                
                if correlation < 0.5:
                    self.log_finding("WARNING", "SIG-006", "Low correlation between final_score and ai_score", 
                                   f"Correlation: {correlation:.4f}")
            
        except Exception as e:
            self.log_finding("WARNING", "SIG-099", "Error reading signals CSV", str(e))
    
    def audit_orders_csv(self):
        """Deep analysis of dhan_virtual_orders.csv"""
        print("\n" + "="*80)
        print("AUDIT: ORDERS CSV FILE")
        print("="*80)
        
        orders_path = self.base_path / "storage" / "live" / "dhan_virtual_orders.csv"
        
        if not orders_path.exists():
            self.log_finding("INFO", "ORD-000", "Orders CSV not present (acceptable when no live/paper data)", str(orders_path))
            return
        try:
            df = pd.read_csv(orders_path, on_bad_lines='skip', engine='python')
            
            # Basic stats
            self.stats['orders_total_rows'] = len(df)
            self.stats['orders_columns'] = len(df.columns)
            
            print(f"[OK] File exists: {orders_path}")
            print(f"  - Total rows: {len(df):,}")
            print(f"  - Total columns: {len(df.columns)}")
            print(f"  - File size: {orders_path.stat().st_size / 1024 / 1024:.2f} MB")
            
            # Check critical columns
            # Note: Orders CSV may have different schema - check what columns actually exist
            available_cols = list(df.columns)
            
            # Essential columns (with alternative names)
            essential_checks = {
                'timestamp': ['ts', 'timestamp', 'time', 'datetime'],
                'underlying': ['underlying', 'symbol', 'instrument', 'ticker'],
                'side': ['side', 'direction', 'buy_sell']
            }
            
            essential_missing = []
            for essential_name, alternatives in essential_checks.items():
                found = False
                for alt in alternatives:
                    if alt in df.columns:
                        found = True
                        break
                if not found:
                    essential_missing.append(essential_name)
            
            # Optional columns
            optional_cols = ['ai_score', 'final_score']
            missing_optional = [col for col in optional_cols if col not in df.columns]
            
            if essential_missing:
                self.log_finding("WARNING", "ORD-001", f"Missing essential columns", f"Missing: {essential_missing}, Available: {available_cols[:10]}")
            elif missing_optional:
                # Optional columns missing - just info
                print(f"[INFO] Some optional columns missing: {missing_optional}")
                print(f"[OK] All essential columns present")
            else:
                print(f"[OK] All critical columns present")
            
            # Analyze approval status
            if 'approved' in df.columns:
                approved_dist = df['approved'].value_counts()
                print(f"\nApproval Distribution:")
                for status, count in approved_dist.items():
                    print(f"  - {status}: {count} ({count/len(df)*100:.1f}%)")
                
                rejection_pct = (1 - approved_dist.get(True, 0) / len(df)) * 100
                if rejection_pct > 10:
                    self.log_finding("WARNING", "ORD-002", "High order rejection rate", f"Rejection rate: {rejection_pct:.1f}%")
            
            # Analyze side distribution (should be roughly balanced)
            if 'side' in df.columns:
                side_dist = df['side'].value_counts()
                print(f"\nSide Distribution:")
                for side, count in side_dist.items():
                    print(f"  - {side}: {count} ({count/len(df)*100:.1f}%)")
                
                if len(side_dist) == 1:
                    self.log_finding("WARNING", "ORD-003", "Only one side present in orders (expected BUY and SELL)", 
                                   f"Present: {list(side_dist.index)}")
            
            # Check for risk reasons
            if 'risk_reason' in df.columns:
                risk_dist = df['risk_reason'].value_counts()
                print(f"\nRisk Reasons:")
                for reason, count in risk_dist.items():
                    print(f"  - {reason}: {count} ({count/len(df)*100:.1f}%)")
                
                non_ok = df[df['risk_reason'] != 'OK']
                if len(non_ok) > 0:
                    print(f"[WARNING] {len(non_ok)} orders with non-OK risk reason")
            
            # Analyze scores
            if 'ai_score' in df.columns:
                ai_scores = pd.to_numeric(df['ai_score'], errors='coerce')
                print(f"\nAI Score Stats (Orders):")
                print(f"  - Mean: {ai_scores.mean():.6f}")
                print(f"  - Std: {ai_scores.std():.6f}")
                print(f"  - Min: {ai_scores.min():.6f}")
                print(f"  - Max: {ai_scores.max():.6f}")
            
        except Exception as e:
            self.log_finding("WARNING", "ORD-099", "Error reading orders CSV", str(e))
    
    def audit_pnl_log(self):
        """Deep analysis of PnL log"""
        print("\n" + "="*80)
        print("AUDIT: PNL LOG FILE")
        print("="*80)
        
        pnl_path = self.base_path / "storage" / "live" / "dhan_index_ai_pnl_log.csv"
        
        if not pnl_path.exists():
            self.log_finding("INFO", "PNL-000", "PnL log not present (acceptable when no live/paper data)", str(pnl_path))
            return
        try:
            df = pd.read_csv(pnl_path)
            
            self.stats['pnl_total_rows'] = len(df)
            
            print(f"[OK] File exists: {pnl_path}")
            print(f"  - Total rows: {len(df):,}")
            print(f"  - File size: {pnl_path.stat().st_size / 1024:.2f} KB")
            
            if len(df) == 0:
                self.log_finding("INFO", "PNL-001", "PnL log is empty (no trading records yet)", "Acceptable for new/system without trades")
            else:
                # Check for critical columns
                critical_cols = ['ts', 'result', 'pnl_pct', 'entry_price', 'exit_price']
                missing = [col for col in critical_cols if col not in df.columns]
                
                if missing:
                    print(f"[WARNING] Missing columns: {missing}")
                else:
                    print(f"[OK] Critical columns present")
                
                # Analyze results
                if 'result' in df.columns:
                    result_dist = df['result'].value_counts()
                    print(f"\nTrade Results Distribution:")
                    for result, count in result_dist.items():
                        print(f"  - {result}: {count}")
                
                # Analyze PnL
                if 'pnl_pct' in df.columns:
                    pnl = pd.to_numeric(df['pnl_pct'], errors='coerce')
                    print(f"\nPnL % Statistics:")
                    print(f"  - Mean: {pnl.mean():.2f}%")
                    print(f"  - Std: {pnl.std():.2f}%")
                    print(f"  - Min: {pnl.min():.2f}%")
                    print(f"  - Max: {pnl.max():.2f}%")
                    print(f"  - Win rate: {(pnl > 0).sum() / len(pnl) * 100:.1f}%")
        
        except Exception as e:
            self.log_finding("WARNING", "PNL-99", "Error reading PnL CSV", str(e))
    
    def audit_heartbeat(self):
        """Check system heartbeat freshness"""
        print("\n" + "="*80)
        print("AUDIT: SYSTEM HEARTBEAT")
        print("="*80)
        
        heartbeat_path = self.base_path / "system3_daily_heartbeat.json"
        
        try:
            with open(heartbeat_path) as f:
                hb = json.load(f)
            
            print(f"[OK] Heartbeat file exists")
            print(f"  - File size: {heartbeat_path.stat().st_size:,} bytes")
            
            if 'last_update' in hb:
                print(f"  - Last update: {hb['last_update']}")
                
                # Parse timestamp and check freshness
                try:
                    last_update = datetime.fromisoformat(hb['last_update'])
                    age_seconds = (datetime.now() - last_update).total_seconds()
                    print(f"  - Heartbeat age: {age_seconds:.1f} seconds")
                    
                    if age_seconds > 120:
                        self.log_finding("WARNING", "HB-001", "Heartbeat is stale", 
                                       f"Age: {age_seconds:.1f}s (>120s threshold)")
                    elif age_seconds > 90:
                        self.log_finding("WARNING", "HB-002", "Heartbeat age approaching warning threshold",
                                       f"Age: {age_seconds:.1f}s")
                    else:
                        print(f"  ✓ Heartbeat is fresh (<120s)")
                except:
                    self.log_finding("WARNING", "HB-003", "Unable to parse heartbeat timestamp", hb.get('last_update'))
            
            if 'process_id' in hb:
                print(f"  - Master process ID: {hb['process_id']}")
            
            if 'status' in hb:
                print(f"  - Status: {hb['status']}")
            
            if 'autopilot_running' in hb:
                print(f"  - Autopilot running: {hb['autopilot_running']}")
        
        except FileNotFoundError:
            self.log_finding("INFO", "HB-099", "Heartbeat file not found (acceptable when runner/autopilot not running)", str(heartbeat_path))
        except Exception as e:
            self.log_finding("WARNING", "HB-98", "Error reading heartbeat", str(e))
    
    def audit_config(self):
        """Verify configuration"""
        print("\n" + "="*80)
        print("AUDIT: CONFIGURATION")
        print("="*80)
        
        env_path = self.base_path / ".env"
        
        if not env_path.exists():
            self.log_finding("INFO", "CFG-000", ".env not present (optional; safety flags apply when file exists)", str(env_path))
            return
        try:
            with open(env_path, encoding='utf-8', errors='ignore') as f:
                env_content = f.read()
            
            print(f"[OK] .env file exists")
            
            # Parse .env
            env_vars = {}
            for line in env_content.strip().split('\n'):
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            print(f"\nCritical Safety Flags:")
            safety_checks = {
                'LIVE_TRADING_ENABLED': 'False',
                'PAPER_TRADING_MODE': 'True',
                'DRY_RUN_MODE': 'True'
            }
            
            for key, expected in safety_checks.items():
                actual = env_vars.get(key, 'NOT FOUND')
                if actual == expected:
                    print(f"  [OK] {key}={actual}")
                else:
                    self.log_finding("WARNING", "CFG-001", f"Safety flag mismatch: {key}", 
                                   f"Expected: {expected}, Got: {actual}")
            
        except Exception as e:
            self.log_finding("WARNING", "CFG-99", "Error reading .env config", str(e))
    
    def audit_phase_artifacts(self):
        """Verify Phase 390/391 artifacts"""
        print("\n" + "="*80)
        print("AUDIT: PHASE 390/391 ARTIFACTS")
        print("="*80)
        
        # Phase 390 balanced dataset
        balanced_dataset_path = self.base_path / "storage" / "datasets" / "phase_390_balanced_features.csv"
        if balanced_dataset_path.exists():
            try:
                df = pd.read_csv(balanced_dataset_path)
                print(f"[OK] Phase 390 balanced dataset exists")
                print(f"  - Shape: {df.shape[0]:,} rows x {df.shape[1]:,} columns")
                
                # Check class balance
                if 'target' in df.columns or 'label' in df.columns:
                    label_col = 'target' if 'target' in df.columns else 'label'
                    class_dist = df[label_col].value_counts()
                    print(f"  - Class distribution: {dict(class_dist)}")
            except Exception as e:
                self.log_finding("WARNING", "P390-01", "Error reading Phase 390 dataset", str(e))
        else:
            self.log_finding("INFO", "P390-99", "Phase 390 balanced dataset not found (optional artifact)", str(balanced_dataset_path))
        
        # Phase 391 XGBoost models
        models_dir = self.base_path / "models" / "xgboost_v1"
        if models_dir.exists():
            pkl_files = list(models_dir.glob("*_xgb_model.pkl"))
            print(f"\n[OK] Phase 391 XGBoost models directory exists")
            print(f"  - Model files found: {len(pkl_files)}")
            
            for pkl_file in sorted(pkl_files):
                size_kb = pkl_file.stat().st_size / 1024
                print(f"    - {pkl_file.name}: {size_kb:.1f} KB")
            
            if len(pkl_files) < 5:
                self.log_finding("WARNING", "P391-01", "Not all 5 XGBoost models found", f"Found: {len(pkl_files)}/5")
            else:
                print(f"  [OK] All 5 XGBoost models present")
        else:
            self.log_finding("INFO", "P391-99", "Phase 391 models directory not found (optional artifact)", str(models_dir))
    
    def generate_summary(self):
        """Generate summary report"""
        print("\n" + "="*80)
        print("QC AUDIT SUMMARY")
        print("="*80)
        
        critical_count = len(self.findings['CRITICAL'])
        warning_count = len(self.findings['WARNING'])
        info_count = len(self.findings['INFO'])
        
        print(f"\nFindings Summary:")
        print(f"  [CRITICAL] CRITICAL: {critical_count}")
        print(f"  [WARNING] WARNING:  {warning_count}")
        print(f"  [INFO] INFO:     {info_count}")
        
        print(f"\nStatistics:")
        for key, value in self.stats.items():
            print(f"  - {key}: {value}")
        
        # Overall verdict
        print(f"\n{'='*80}")
        if critical_count > 0:
            print("[CRITICAL] VERDICT: CRITICAL ISSUES DETECTED - INVESTIGATION REQUIRED")
        elif warning_count > 0:
            print("[WARNING] VERDICT: WARNINGS DETECTED - MONITOR AND VERIFY")
        else:
            print("[OK] VERDICT: ALL CHECKS PASSED - SYSTEM READY")
        print(f"{'='*80}")
        
        return {
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "findings": self.findings,
            "stats": self.stats
        }

def main():
    """Run comprehensive QC audit"""
    print("\n" + "="*80)
    print("SYSTEM3 COMPREHENSIVE QC AUDIT")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    audit = ComprehensiveQCAudit()
    
    # Run all audits
    audit.audit_config()
    audit.audit_heartbeat()
    audit.audit_signals_csv()
    audit.audit_orders_csv()
    audit.audit_pnl_log()
    audit.audit_phase_artifacts()
    
    # Generate summary
    summary = audit.generate_summary()
    
    # Save detailed report
    report_path = Path("c:/Genesis_System3/QC_AUDIT_REPORT_DETAILED.json")
    with open(report_path, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n[OK] Detailed report saved to: {report_path}")

if __name__ == "__main__":
    main()
