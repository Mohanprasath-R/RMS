# RMS - Real-time Monitor System for MT5 Trading

A comprehensive real-time monitoring system for MetaTrader 5 (MT5) trading platform that tracks client accounts, trades, and open positions using the MT5 Manager Python package.

## 🚀 Features

- **Real-time Account Monitoring**: Track balance, equity, margin, profit/loss, and more
- **Position Tracking**: Monitor all open positions across multiple accounts
- **Trade History**: Access closed trades and trading statistics
- **Symbol Exposure**: View aggregated positions by trading symbol
- **WebSocket Server**: Real-time data streaming to connected clients
- **Interactive Dashboard**: Beautiful web-based interface for visualization
- **CLI Interface**: Command-line tools for system management
- **Alerts & Notifications**: Margin level and loss threshold warnings
- **Data Export**: Export monitoring data to JSON format

## 📋 Requirements

- Python 3.8+
- MetaTrader 5 Manager API
- Active MT5 Manager credentials

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd RMS
```

2. Install required packages:
```bash
pip install websockets python-dotenv
```

3. Configure environment variables in `.env`:
```env
MT5_HOST=188.240.63.221
MT5_PORT=443
MT5_MANAGER_USER=1054
MT5_MANAGER_PASS=your_password
RMS_UPDATE_INTERVAL=5
WS_PORT=8765
```

## 🎯 Quick Start

### 1. Start the WebSocket Server

```bash
python WebSocketServer.py
```

Or with custom settings:
```bash
python cli.py websocket --host 0.0.0.0 --port 8765
```

### 2. Open the Dashboard

Open `dashboard.html` in your web browser. The dashboard will automatically connect to the WebSocket server.

### 3. Add Accounts to Monitor

Using the dashboard:
- Enter MT5 Login ID in the input field
- Click "Add Account"

Using CLI:
```bash
python cli.py add 123456
```

## 📚 Usage

### Command Line Interface

**Start monitoring with specific accounts:**
```bash
python cli.py start -i 5 -a 123456 789012
```

**Get account snapshot:**
```bash
python cli.py snapshot --login-id 123456
```

**View all accounts:**
```bash
python cli.py snapshot
```

**Check symbol exposure:**
```bash
python cli.py exposure --symbol EURUSD
```

**Get system statistics:**
```bash
python cli.py stats
```

**Export data:**
```bash
python cli.py export -o my_export.json
```

### Python API

```python
from RealTimeMonitor import get_rms_instance

# Initialize RMS
rms = get_rms_instance(update_interval=5)
rms.initialize()

# Add accounts to monitor
rms.add_account(123456)
rms.add_account(789012)

# Start monitoring
rms.start()

# Get account snapshot
snapshot = rms.get_account_snapshot(123456)
print(f"Balance: {snapshot['account']['balance']}")
print(f"Equity: {snapshot['account']['equity']}")
print(f"Open Positions: {snapshot['positions']['position_count']}")

# Get positions by symbol
eurusd_positions = rms.get_positions_by_symbol('EURUSD')
print(f"EURUSD positions: {len(eurusd_positions)}")

# Get total exposure
exposure = rms.get_total_exposure_by_symbol()
for symbol, data in exposure.items():
    print(f"{symbol}: {data['volume']} lots across {data['accounts']} accounts")

# Stop monitoring
rms.stop()
```

### WebSocket API

Connect to `ws://localhost:8765` and send JSON messages:

**Add account to monitoring:**
```json
{
  "type": "add_account",
  "login_id": 123456
}
```

**Remove account:**
```json
{
  "type": "remove_account",
  "login_id": 123456
}
```

**Get snapshot:**
```json
{
  "type": "get_snapshot",
  "login_id": 123456
}
```

**Get exposure by symbol:**
```json
{
  "type": "get_exposure",
  "symbol": "EURUSD"
}
```

**Get statistics:**
```json
{
  "type": "get_stats"
}
```

## 🏗️ Architecture

### Components

1. **RealTimeMonitor.py**: Core monitoring system
   - `AccountMonitor`: Tracks individual account metrics
   - `PositionMonitor`: Monitors open positions
   - `TradeMonitor`: Handles trade history
   - `RealTimeMonitorSystem`: Coordinates all monitoring activities

2. **WebSocketServer.py**: WebSocket server for real-time updates
   - Broadcasts updates to connected clients
   - Handles client requests
   - Manages client connections

3. **dashboard.html**: Web-based monitoring interface
   - Real-time visualization
   - Account management
   - Symbol exposure analysis

4. **Services.py**: MT5 Manager integration
   - Connection management
   - API wrapper for MT5 operations

5. **config.py**: Configuration management
   - Environment variable handling
   - Default settings
   - Alert thresholds

6. **utils.py**: Utility functions
   - Data formatting
   - Calculations
   - Alert generation

7. **cli.py**: Command-line interface
   - System management
   - Data queries
   - Export functionality

### Data Flow

```
MT5 Manager API
      ↓
RealTimeMonitor (polling every 5s)
      ↓
WebSocket Server
      ↓
Dashboard / Clients
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MT5_HOST` | MT5 server host | localhost |
| `MT5_PORT` | MT5 server port | 443 |
| `MT5_MANAGER_USER` | Manager login | - |
| `MT5_MANAGER_PASS` | Manager password | - |
| `RMS_UPDATE_INTERVAL` | Update interval (seconds) | 5 |
| `RMS_TRADE_HISTORY_DAYS` | Trade history period | 30 |
| `WS_HOST` | WebSocket host | 0.0.0.0 |
| `WS_PORT` | WebSocket port | 8765 |
| `MARGIN_LEVEL_WARNING` | Warning threshold (%) | 150.0 |
| `MARGIN_LEVEL_CRITICAL` | Critical threshold (%) | 100.0 |
| `MAX_LOSS_THRESHOLD` | Max loss alert | -1000.0 |

### Alert Thresholds

Configure in `.env` or `config.py`:
- **Margin Level Warning**: 150% (default)
- **Margin Level Critical**: 100% (default)
- **Max Loss Threshold**: -$1000 (default)

## 📊 Dashboard Features

- **Real-time Updates**: Automatic refresh every 5 seconds
- **Account Cards**: Individual cards showing all account metrics
- **Position Details**: View all open positions with profit/loss
- **Symbol Exposure**: Aggregated view of positions by symbol
- **System Statistics**: Monitor system health and performance
- **Interactive Controls**: Add/remove accounts dynamically
- **Responsive Design**: Works on desktop and mobile devices

## 🔒 Security Notes

- Store sensitive credentials in `.env` file
- Never commit `.env` file to version control
- Use secure WebSocket (WSS) for production
- Implement authentication for WebSocket connections
- Restrict access to dashboard in production

## 🐛 Troubleshooting

**Connection Failed:**
- Verify MT5 credentials in `.env`
- Check MT5 server is accessible
- Ensure Manager API is properly installed

**No Data Displayed:**
- Confirm accounts are added to monitoring
- Check RMS is running (`python cli.py stats`)
- Verify WebSocket connection in browser console

**High CPU Usage:**
- Increase `RMS_UPDATE_INTERVAL` value
- Reduce number of monitored accounts
- Check for errors in logs

## 📝 Logging

Logs are written to `rms.log` and console. Configure log level:

```env
RMS_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🔗 Related Documentation

- [MT5 Manager API Documentation](https://www.metatrader5.com/en/terminal/help/manager_api)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## 💡 Examples

### Example 1: Monitor Multiple Accounts

```python
from RealTimeMonitor import get_rms_instance

rms = get_rms_instance(update_interval=3)
rms.initialize()

# Add multiple accounts
accounts = [123456, 789012, 345678]
for account in accounts:
    rms.add_account(account)

# Start monitoring
rms.start()

# Add callback for alerts
def on_update(accounts_data):
    for account in accounts_data:
        margin_level = account['account']['margin_level']
        if margin_level < 150:
            print(f"⚠️ Warning: Account {account['account']['login_id']} margin level: {margin_level}%")

rms.add_callback(on_update)
```

### Example 2: Export Daily Reports

```python
from RealTimeMonitor import get_rms_instance
from datetime import datetime

rms = get_rms_instance()
rms.initialize()

# Export snapshot
filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
rms.export_data(filename)
print(f"Report exported: {filename}")
```

### Example 3: Risk Management Alerts

```python
from utils import check_margin_alert, check_loss_alert, generate_alert_message

# Check account health
for login_id, snapshot in rms.get_all_accounts_snapshot().items():
    account = snapshot['account']
    
    # Check margin
    margin_alert = check_margin_alert(account['margin_level'])
    if margin_alert:
        print(f"Margin Alert ({margin_alert}): Account {login_id}")
    
    # Check losses
    if check_loss_alert(account['profit']):
        print(f"Loss Alert: Account {login_id} - ${account['profit']}")
    
    # Generate alert message
    alert_msg = generate_alert_message(account)
    if alert_msg:
        print(alert_msg)
```

## 🎉 Acknowledgments

Built with ❤️ for the MT5 trading community.

---

For questions or support, please open an issue on GitHub.