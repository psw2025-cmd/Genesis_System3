# World-Class Option Chain Automation System

## 🎯 Overview

This is a production-ready, fully integrated option chain automation system that provides:

- **Real-time data fetching** (WebSocket + REST fallback)
- **Advanced option chain analysis** (Greeks, IV, OI analysis)
- **ML-powered signal generation** (Ensemble of multiple models)
- **Multi-layer risk management** (ATR-based, IV-based, dynamic stops)
- **Paper trading execution** (Realistic simulation with slippage)
- **Comprehensive monitoring** (Real-time dashboard, health checks, alerts)
- **Full testing suite** (Unit tests, integration tests, validation)

## 🚀 Quick Start

### 1. Installation

```bash
# Ensure you're in the project directory
cd C:\Genesis_System3

# Install dependencies (if not already installed)
pip install pandas numpy scipy scikit-learn xgboost pyotp smartapi-python rich

# Or use requirements file if available
pip install -r requirements.txt
```

### 2. Configuration

Create a configuration file (optional, defaults are provided):

```json
{
  "refresh_interval_seconds": 5,
  "use_websocket": true,
  "max_positions": 5,
  "min_confidence": 0.75,
  "slippage_pct": 0.1,
  "max_daily_loss_pct": 2.0,
  "max_position_size_pct": 20.0
}
```

Save as `config/option_chain_config.json`

### 3. Run the System

#### Option A: Run with Default Settings

```bash
python option_chain_automation_master.py
```

#### Option B: Run with Custom Settings

```bash
# Run for 60 minutes
python option_chain_automation_master.py --duration 60

# Run for 100 cycles
python option_chain_automation_master.py --cycles 100

# Run with 10-second refresh
python option_chain_automation_master.py --refresh 10

# Use custom config
python option_chain_automation_master.py --config config/option_chain_config.json
```

### 4. Monitor the System

In a separate terminal:

```bash
python monitor_option_chain_system.py
```

Or with custom refresh interval:

```bash
python monitor_option_chain_system.py --refresh 5
```

### 5. Run Tests

```bash
python test_option_chain_automation.py
```

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Option Chain Automation Master                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Data Fetcher │───▶│   Analyzer   │───▶│   Signals    │ │
│  │ (WS + REST)  │    │ (Greeks/IV)  │    │  (ML+Strategy)│ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                    │                    │         │
│         └────────────────────┼────────────────────┘         │
│                              │                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ Risk Manager │───▶│   Executor   │───▶│  PnL Tracker │ │
│  │ (ATR/IV/Dyn) │    │  (Paper Trade)│    │  (Real-time) │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Monitoring & Alerting (Background)            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Components

### 1. Data Fetcher
- **WebSocket**: Real-time streaming (primary)
- **REST API**: Fallback with rate limiting
- **Auto-reconnect**: Self-healing connections
- **Multi-index support**: NIFTY, BANKNIFTY, FINNIFTY, MIDCPNIFTY, SENSEX

### 2. Option Chain Analyzer
- **Greeks calculation**: Delta, Gamma, Theta, Vega, Rho
- **IV analysis**: Implied volatility calculation and ranking
- **OI analysis**: Open interest buildup tracking
- **Liquidity scoring**: Volume + OI based
- **ATM distance**: Automatic ATM identification

### 3. Signal Generator
- **ML Ensemble**: Combines Ultra, XGBoost, RandomForest models
- **Strategy Engine**: Rule-based signal generation
- **Confidence scoring**: Multi-factor confidence calculation
- **Signal filtering**: Min confidence threshold

### 4. Risk Manager
- **ATR-based stops**: Dynamic stop-loss based on volatility
- **IV-based stops**: Implied volatility adjusted stops
- **Trailing stops**: Profit protection
- **Position sizing**: Kelly criterion + risk-based sizing
- **Daily loss limits**: Automatic shutdown on breach

### 5. Paper Executor
- **Realistic simulation**: Slippage, bid-ask spread
- **Position management**: Max positions, lot sizing
- **Trade tracking**: Complete trade history
- **PnL calculation**: Real-time unrealized PnL

### 6. Monitoring Dashboard
- **Real-time status**: System health, cycles, fetches
- **Position tracking**: Current positions, PnL
- **Performance metrics**: Success rate, win rate, Sharpe ratio
- **Alert system**: Error notifications, threshold alerts

## 📈 Features

### Real-Time Data Pipeline
- ✅ WebSocket primary connection
- ✅ REST fallback with rate limiting
- ✅ Automatic reconnection
- ✅ Data validation and QC
- ✅ Multi-index support

### Advanced Analysis
- ✅ Greeks calculation (Delta, Gamma, Theta, Vega, Rho)
- ✅ Implied volatility analysis
- ✅ Open interest buildup tracking
- ✅ Liquidity scoring
- ✅ ATM distance calculation
- ✅ Moneyness analysis

### ML-Powered Signals
- ✅ Ensemble of multiple models
- ✅ Confidence scoring
- ✅ Signal filtering
- ✅ Strategy integration
- ✅ Backtesting support

### Risk Management
- ✅ ATR-based stop-loss
- ✅ IV-based adjustments
- ✅ Trailing stops
- ✅ Position sizing
- ✅ Daily loss limits
- ✅ Max position limits

### Monitoring & Alerts
- ✅ Real-time dashboard
- ✅ Health checks
- ✅ Performance metrics
- ✅ Error tracking
- ✅ Alert notifications

## 📁 File Structure

```
Genesis_System3/
├── option_chain_automation_master.py  # Main orchestrator
├── test_option_chain_automation.py    # Test suite
├── monitor_option_chain_system.py     # Monitoring dashboard
├── OPTION_CHAIN_AUTOMATION_README.md  # This file
│
├── core/
│   ├── brokers/angel_one/            # Broker integration
│   ├── engine/                        # Core engine components
│   └── models/                        # ML models
│
├── src/
│   ├── angel/                         # Angel One integration
│   ├── ml/                            # ML components
│   ├── trading/                       # Trading components
│   ├── selector/                      # Signal selection
│   └── validation/                    # QC validation
│
├── outputs/
│   ├── system_status.json             # System status
│   ├── health_check.json              # Health metrics
│   ├── positions_live.json           # Current positions
│   ├── pnl_live.json                 # PnL tracking
│   └── chain_raw_live.csv            # Option chain data
│
└── logs/
    └── option_chain_automation_*.log  # System logs
```

## ⚙️ Configuration

### System Configuration

Key parameters in `SystemConfig`:

- `refresh_interval_seconds`: Data refresh interval (default: 5s)
- `use_websocket`: Enable WebSocket (default: True)
- `max_positions`: Maximum concurrent positions (default: 5)
- `min_confidence`: Minimum signal confidence (default: 0.75)
- `slippage_pct`: Slippage percentage (default: 0.1%)
- `max_daily_loss_pct`: Daily loss limit (default: 2.0%)
- `max_position_size_pct`: Max position size (default: 20.0%)

### Environment Variables

Required for broker connection:
- `ANGELONE_API_KEY`
- `ANGELONE_CLIENT_ID`
- `ANGELONE_PIN` or `ANGELONE_PASSWORD`
- `ANGELONE_TOTP`

## 📊 Output Files

### System Status (`outputs/system_status.json`)
```json
{
  "is_running": true,
  "is_connected": true,
  "total_cycles": 100,
  "successful_fetches": 95,
  "failed_fetches": 5,
  "signals_generated": 50,
  "trades_executed": 10,
  "current_positions": 3,
  "total_pnl": 1500.50,
  "daily_pnl": 500.25
}
```

### Health Check (`outputs/health_check.json`)
```json
{
  "timestamp": "2026-02-02T10:30:00",
  "is_running": true,
  "success_rate": 95.0,
  "total_cycles": 100,
  "current_positions": 3,
  "total_pnl": 1500.50
}
```

### Positions (`outputs/positions_live.json`)
```json
{
  "POS_0001": {
    "position_id": "POS_0001",
    "underlying": "NIFTY",
    "symbol": "NIFTY25FEB19500CE",
    "entry_price": 150.50,
    "qty": 50,
    "unrealized_pnl": 250.00
  }
}
```

## 🧪 Testing

### Run All Tests
```bash
python test_option_chain_automation.py
```

### Test Coverage
- ✅ System configuration
- ✅ System status tracking
- ✅ Option chain enrichment
- ✅ Signal generation
- ✅ Risk management
- ✅ Integration tests
- ✅ Data validation

### Test Report
Test results are saved to `outputs/test_report.json`

## 🔍 Monitoring

### Real-Time Dashboard
```bash
python monitor_option_chain_system.py
```

Features:
- System status display
- Position tracking
- PnL monitoring
- Health metrics
- Error tracking

### Health Checks
- Automatic health checks every 5 minutes
- Success rate monitoring
- Connection status
- Data freshness

## 🛠️ Troubleshooting

### Issue: Broker Connection Failed
**Solution**: Check environment variables and TOTP secret

### Issue: No Data Fetched
**Solution**: 
1. Check market hours
2. Verify broker connection
3. Check expiry dates

### Issue: No Signals Generated
**Solution**:
1. Check confidence threshold
2. Verify ML models are loaded
3. Check option chain data quality

### Issue: Trades Not Executing
**Solution**:
1. Check max positions limit
2. Verify risk management settings
3. Check daily loss limits

## 📝 Best Practices

1. **Start with Paper Trading**: Always test with paper trading first
2. **Monitor Regularly**: Use the monitoring dashboard
3. **Set Appropriate Limits**: Configure risk parameters carefully
4. **Review Logs**: Check logs regularly for errors
5. **Test Before Live**: Run tests before deploying
6. **Backup Data**: Regular backups of positions and PnL

## 🔐 Safety Features

- ✅ Paper trading mode (default)
- ✅ Daily loss limits
- ✅ Max position limits
- ✅ Risk management checks
- ✅ Automatic shutdown on errors
- ✅ Health monitoring

## 📚 Additional Resources

- `OPTIONCHAIN_MASTER_GUIDE.md` - Excel output guide
- `FULLY_AUTOMATED_SYSTEM_README.md` - Full system documentation
- `LIVE_PAPER_TRADING_GUIDE.md` - Paper trading guide

## 🎯 Performance Metrics

The system tracks:
- Success rate (data fetches)
- Signal generation rate
- Trade execution rate
- Win rate
- Total PnL
- Daily PnL
- Sharpe ratio (if available)

## 📞 Support

For issues or questions:
1. Check logs in `logs/` directory
2. Review test results
3. Check system status files
4. Review monitoring dashboard

## 🚀 Next Steps

1. **Configure**: Set up your configuration file
2. **Test**: Run the test suite
3. **Monitor**: Start the monitoring dashboard
4. **Run**: Start the automation system
5. **Review**: Check outputs and logs regularly

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-02  
**Status**: Production Ready ✅
