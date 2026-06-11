import pandas as pd
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class ProductionValidator:
    def __init__(self):
        self.issues = []
        self.passed_checks = []
        self.storage_path = 'storage'
        self.live_path = os.path.join(self.storage_path, 'live')

    def log_issue(self, category, message, severity='ERROR'):
        self.issues.append({
            'category': category,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        print(f"[{severity}] {category}: {message}")

    def log_pass(self, category, message):
        self.passed_checks.append({
            'category': category,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        print(f"[PASS] {category}: {message}")

    def validate_csv_headers(self):
        """Validate CSV file headers and schemas"""
        required_files = [
            'angel_index_ai_signals.csv',
            'angel_index_ai_pnl_log.csv',
            'angel_virtual_orders.csv',
            'phase221_forward_returns.csv'
        ]

        expected_schemas = {
            'angel_index_ai_signals.csv': [
                'underlying', 'index_exch', 'opt_exch', 'spot', 'expiry', 'strike', 'side',
                'symbol', 'token', 'ltp', 'ts', 'moneyness', 'ce_pe_ratio', 'atm_dist_pct',
                'atm_dist_abs', 'ce_pe_diff', 'spot_chg_1_pct', 'ltp_chg_1_pct', 'spot_roll_std_5',
                'ltp_roll_std_5', 'pred_label', 'pred_confidence', 'prob_BUY_CE', 'prob_BUY_PE',
                'prob_HOLD', 'expected_move_score', 'time_to_expiry', 'iv_estimate', 'iv',
                'delta', 'gamma', 'theta', 'vega', 'trend_score', 'multi_tf_trend_score',
                'rsi', 'macd', 'macd_signal', 'macd_histogram', 'vwap', 'price_vs_vwap',
                'supertrend', 'supertrend_direction', 'sma_5', 'sma_10', 'sma_20',
                'trend_strength', 'trend_1m', 'trend_3m', 'trend_5m', 'trend_15m',
                'iv_percentile', 'iv_rank', 'volatility_regime', 'volatility_score',
                'iv_change_rate', 'iv_spike', 'regime_transition', 'breakout_score',
                'momentum_score', 'roc_1', 'roc_3', 'roc_5', 'roc_10', 'acceleration',
                'momentum_strength', 'momentum_direction', 'ai_score', 'greeks_score',
                'final_score', 'signal', 'signal_strength', 'entry_buy', 'entry_sell',
                'entry_hold', 'entry_confidence', 'stop_loss', 'target_price', 'risk_amount',
                'entry_price', 'exit_sl_hit', 'exit_target_hit', 'trailing_sl', 'exit_signal',
                'ml_prediction', 'ml_probability', 'fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5',
                'reconciled_label', 'fwd_ret_2', 'timestamp', 'confidence', 'score',
                'pred_proba', 'rho', 'data_source'
            ],
            'angel_index_ai_pnl_log.csv': [
                'timestamp', 'underlying', 'symbol', 'side', 'entry_price', 'exit_price',
                'quantity', 'pnl', 'pnl_pct', 'entry_time', 'exit_time', 'trade_id',
                'strategy', 'signal_strength', 'confidence', 'market_condition'
            ],
            'angel_virtual_orders.csv': [
                'timestamp', 'order_id', 'symbol', 'side', 'quantity', 'price', 'order_type',
                'status', 'pnl_realized', 'pnl_unrealized', 'entry_time', 'exit_time'
            ],
            'phase221_forward_returns.csv': [
                'underlying', 'index_exch', 'opt_exch', 'spot', 'expiry', 'strike', 'side',
                'symbol', 'token', 'ltp', 'ts', 'moneyness', 'ce_pe_ratio', 'atm_dist_pct',
                'atm_dist_abs', 'ce_pe_diff', 'spot_chg_1_pct', 'ltp_chg_1_pct', 'spot_roll_std_5',
                'ltp_roll_std_5', 'pred_label', 'pred_confidence', 'prob_BUY_CE', 'prob_BUY_PE',
                'prob_HOLD', 'expected_move_score', 'time_to_expiry', 'iv_estimate', 'iv',
                'delta', 'gamma', 'theta', 'vega', 'trend_score', 'multi_tf_trend_score',
                'rsi', 'macd', 'macd_signal', 'macd_histogram', 'vwap', 'price_vs_vwap',
                'supertrend', 'supertrend_direction', 'sma_5', 'sma_10', 'sma_20',
                'trend_strength', 'trend_1m', 'trend_3m', 'trend_5m', 'trend_15m',
                'iv_percentile', 'iv_rank', 'volatility_regime', 'volatility_score',
                'iv_change_rate', 'iv_spike', 'regime_transition', 'breakout_score',
                'momentum_score', 'roc_1', 'roc_3', 'roc_5', 'roc_10', 'acceleration',
                'momentum_strength', 'momentum_direction', 'ai_score', 'greeks_score',
                'final_score', 'signal', 'signal_strength', 'entry_buy', 'entry_sell',
                'entry_hold', 'entry_confidence', 'stop_loss', 'target_price', 'risk_amount',
                'entry_price', 'exit_sl_hit', 'exit_target_hit', 'trailing_sl', 'exit_signal',
                'ml_prediction', 'ml_probability', 'fwd_ret_1', 'fwd_ret_3', 'fwd_ret_5',
                'reconciled_label', 'fwd_ret_2', 'timestamp', 'confidence', 'score',
                'pred_proba', 'rho', 'data_source', 'u_moneyness_sq', 'u_moneyness_cube',
                'u_moneyness_sqrt', 'u_momentum_1', 'u_momentum_3', 'u_momentum_5',
                'u_momentum_10', 'u_spot_momentum_1', 'u_spot_momentum_3', 'u_spot_momentum_5',
                'u_spot_momentum_10', 'u_momentum_ratio_1_5', 'u_vol_short', 'u_vol_long',
                'u_vol_ratio', 'u_spot_vol_short', 'u_spot_vol_long', 'u_spot_vol_ratio',
                'u_regime_high_vol', 'u_regime_low_vol', 'u_hour', 'u_minute',
                'u_moneyness_x_score', 'u_moneyness_x_conf', 'u_score_x_conf', 'u_is_win',
                'u_rolling_win_rate_5', 'u_rolling_win_rate_10', 'u_ltp_percentile', 'date',
                'fwd_ret_10', 'fwd_ret_15'
            ]
        }

        for file in required_files:
            file_path = os.path.join(self.live_path, file)
            if not os.path.exists(file_path):
                self.log_issue('CSV_HEADERS', f"Required file {file} not found")
                continue

            try:
                df = pd.read_csv(file_path, nrows=5)  # Read first 5 rows to check headers
                actual_headers = list(df.columns)

                if file in expected_schemas:
                    expected = expected_schemas[file]
                    missing = set(expected) - set(actual_headers)
                    extra = set(actual_headers) - set(expected)

                    if missing:
                        self.log_issue('CSV_HEADERS', f"{file} missing columns: {missing}")
                    if extra:
                        self.log_issue('CSV_HEADERS', f"{file} extra columns: {extra}")
                    if not missing and not extra:
                        self.log_pass('CSV_HEADERS', f"{file} schema matches expected")
                else:
                    self.log_pass('CSV_HEADERS', f"{file} exists with {len(actual_headers)} columns")

            except Exception as e:
                self.log_issue('CSV_HEADERS', f"Error reading {file}: {str(e)}")

    def validate_prediction_model_performance(self):
        """Validate prediction model performance metrics"""
        signals_file = os.path.join(self.live_path, 'angel_index_ai_signals.csv')
        if not os.path.exists(signals_file):
            self.log_issue('MODEL_PERFORMANCE', "Signals file not found")
            return

        try:
            df = pd.read_csv(signals_file)

            # Check prediction accuracy
            if 'pred_label' in df.columns and 'reconciled_label' in df.columns:
                accuracy = (df['pred_label'] == df['reconciled_label']).mean()
                if accuracy < 0.5:
                    self.log_issue('MODEL_PERFORMANCE', f"Low prediction accuracy: {accuracy:.3f}")
                else:
                    self.log_pass('MODEL_PERFORMANCE', f"Prediction accuracy: {accuracy:.3f}")

            # Check signal distribution
            if 'signal' in df.columns:
                signal_dist = df['signal'].value_counts(normalize=True)
                if len(signal_dist) < 2:
                    self.log_issue('MODEL_PERFORMANCE', "Insufficient signal diversity")
                else:
                    self.log_pass('MODEL_PERFORMANCE', f"Signal distribution: {signal_dist.to_dict()}")

            # Check forward returns correlation
            if 'final_score' in df.columns and 'fwd_ret_1' in df.columns:
                corr = df['final_score'].corr(df['fwd_ret_1'])
                if abs(corr) < 0.1:
                    self.log_issue('MODEL_PERFORMANCE', f"Weak score-returns correlation: {corr:.3f}")
                else:
                    self.log_pass('MODEL_PERFORMANCE', f"Score-returns correlation: {corr:.3f}")

        except Exception as e:
            self.log_issue('MODEL_PERFORMANCE', f"Error analyzing model performance: {str(e)}")

    def validate_feature_consistency(self):
        """Validate feature consistency across files"""
        signals_file = os.path.join(self.live_path, 'angel_index_ai_signals.csv')
        forward_file = os.path.join(self.live_path, 'phase221_forward_returns.csv')

        if not os.path.exists(signals_file) or not os.path.exists(forward_file):
            self.log_issue('FEATURE_CONSISTENCY', "Required files not found")
            return

        try:
            signals_df = pd.read_csv(signals_file, nrows=100)
            forward_df = pd.read_csv(forward_file, nrows=100)

            # Check common features
            common_cols = set(signals_df.columns) & set(forward_df.columns)
            if len(common_cols) < 50:
                self.log_issue('FEATURE_CONSISTENCY', f"Low feature overlap: {len(common_cols)} common columns")
            else:
                self.log_pass('FEATURE_CONSISTENCY', f"Feature overlap: {len(common_cols)} common columns")

            # Check data types consistency for common columns
            dtype_mismatches = []
            for col in common_cols:
                if signals_df[col].dtype != forward_df[col].dtype:
                    dtype_mismatches.append(col)

            if dtype_mismatches:
                self.log_issue('FEATURE_CONSISTENCY', f"Data type mismatches: {dtype_mismatches}")
            else:
                self.log_pass('FEATURE_CONSISTENCY', "Data types consistent across files")

        except Exception as e:
            self.log_issue('FEATURE_CONSISTENCY', f"Error checking feature consistency: {str(e)}")

    def validate_time_related_issues(self):
        """Validate time-related data integrity"""
        files_to_check = [
            'angel_index_ai_signals.csv',
            'angel_index_ai_pnl_log.csv',
            'angel_virtual_orders.csv'
        ]

        for file in files_to_check:
            file_path = os.path.join(self.live_path, file)
            if not os.path.exists(file_path):
                continue

            try:
                df = pd.read_csv(file_path)

                # Check timestamp columns
                time_cols = [col for col in df.columns if 'time' in col.lower() or 'ts' in col.lower() or 'date' in col.lower()]

                for col in time_cols:
                    if col in df.columns:
                        null_count = df[col].isnull().sum()
                        if null_count > 0:
                            self.log_issue('TIME_VALIDATION', f"{file}:{col} has {null_count} null timestamps")
                        else:
                            self.log_pass('TIME_VALIDATION', f"{file}:{col} has no null timestamps")

                        # Check for future timestamps
                        try:
                            if 'timestamp' in col.lower():
                                max_ts = pd.to_datetime(df[col]).max()
                                now = datetime.now()
                                if max_ts > now + timedelta(hours=1):
                                    self.log_issue('TIME_VALIDATION', f"{file}:{col} has future timestamps")
                                else:
                                    self.log_pass('TIME_VALIDATION', f"{file}:{col} timestamps are valid")
                        except:
                            pass

            except Exception as e:
                self.log_issue('TIME_VALIDATION', f"Error validating time data in {file}: {str(e)}")

    def validate_data_integrity(self):
        """Validate data integrity and consistency"""
        signals_file = os.path.join(self.live_path, 'angel_index_ai_signals.csv')
        if not os.path.exists(signals_file):
            return

        try:
            df = pd.read_csv(signals_file)

            # Check for duplicate symbols/tokens
            if 'symbol' in df.columns:
                dup_symbols = df['symbol'].duplicated().sum()
                if dup_symbols > 0:
                    self.log_issue('DATA_INTEGRITY', f"Found {dup_symbols} duplicate symbols")
                else:
                    self.log_pass('DATA_INTEGRITY', "No duplicate symbols found")

            # Check price reasonableness
            price_cols = ['ltp', 'spot', 'strike']
            for col in price_cols:
                if col in df.columns:
                    prices = df[col].dropna()
                    if len(prices) > 0:
                        min_price = prices.min()
                        max_price = prices.max()
                        if min_price <= 0 or max_price > 100000:
                            self.log_issue('DATA_INTEGRITY', f"{col} has unreasonable values: min={min_price}, max={max_price}")
                        else:
                            self.log_pass('DATA_INTEGRITY', f"{col} values are reasonable")

            # Check signal strength bounds
            if 'signal_strength' in df.columns:
                strength = df['signal_strength'].dropna()
                if len(strength) > 0:
                    if strength.min() < 0 or strength.max() > 1:
                        self.log_issue('DATA_INTEGRITY', "Signal strength out of [0,1] bounds")
                    else:
                        self.log_pass('DATA_INTEGRITY', "Signal strength within valid bounds")

        except Exception as e:
            self.log_issue('DATA_INTEGRITY', f"Error validating data integrity: {str(e)}")

    def validate_production_readiness(self):
        """Validate production readiness"""
        # Check for required configuration files
        config_files = [
            'config/live_trade_config.py',
            'runtime_flags.json',
            'kill_switch.json'
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                self.log_pass('PRODUCTION_READINESS', f"Config file exists: {config_file}")
            else:
                self.log_issue('PRODUCTION_READINESS', f"Missing config file: {config_file}")

        # Check model files
        model_dirs = ['models', 'storage/models']
        models_found = False
        for model_dir in model_dirs:
            if os.path.exists(model_dir):
                models = [f for f in os.listdir(model_dir) if f.endswith(('.pkl', '.joblib', '.h5'))]
                if models:
                    self.log_pass('PRODUCTION_READINESS', f"Found {len(models)} model files in {model_dir}")
                    models_found = True
                else:
                    self.log_issue('PRODUCTION_READINESS', f"No model files found in {model_dir}")

        if not models_found:
            self.log_issue('PRODUCTION_READINESS', "No trained models found")

        # Check for monitoring setup
        monitor_files = ['continuous_monitor.py', 'monitor_live.py']
        for monitor_file in monitor_files:
            if os.path.exists(monitor_file):
                self.log_pass('PRODUCTION_READINESS', f"Monitoring script exists: {monitor_file}")
            else:
                self.log_issue('PRODUCTION_READINESS', f"Missing monitoring script: {monitor_file}")

    def generate_report(self):
        """Generate comprehensive validation report"""
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'total_checks': len(self.passed_checks) + len(self.issues),
            'passed_checks': len(self.passed_checks),
            'failed_checks': len(self.issues),
            'success_rate': len(self.passed_checks) / (len(self.passed_checks) + len(self.issues)) * 100 if self.passed_checks or self.issues else 0,
            'issues': self.issues,
            'passed': self.passed_checks
        }

        # Save report
        report_file = 'PRODUCTION_VALIDATION_REPORT.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n{'='*50}")
        print("PRODUCTION VALIDATION REPORT")
        print(f"{'='*50}")
        print(f"Total Checks: {report['total_checks']}")
        print(f"Passed: {report['passed_checks']}")
        print(f"Failed: {report['failed_checks']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")

        if report['issues']:
            print(f"\n{'='*30} ISSUES FOUND {'='*30}")
            for issue in report['issues']:
                print(f"[{issue['severity']}] {issue['category']}: {issue['message']}")
        else:
            print("\n✅ ALL CHECKS PASSED - PRODUCTION READY!")

        return report

    def run_all_validations(self):
        """Run all validation checks"""
        print("Starting comprehensive production validation...")

        self.validate_csv_headers()
        self.validate_prediction_model_performance()
        self.validate_feature_consistency()
        self.validate_time_related_issues()
        self.validate_data_integrity()
        self.validate_production_readiness()

        return self.generate_report()

if __name__ == "__main__":
    validator = ProductionValidator()
    report = validator.run_all_validations()

    # Exit with error code if there are critical issues
    if report['failed_checks'] > 0:
        exit(1)
    else:
        print("\n🎉 SYSTEM IS PRODUCTION READY!")
