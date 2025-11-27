"""
Utility functions for Real-time Monitor System
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from config import RMSConfig


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, RMSConfig.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(RMSConfig.LOG_FILE),
            logging.StreamHandler()
        ]
    )


def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def calculate_margin_level(equity: float, margin: float) -> float:
    """Calculate margin level percentage"""
    if margin == 0:
        return 0.0
    return (equity / margin) * 100


def calculate_free_margin(equity: float, margin: float) -> float:
    """Calculate free margin"""
    return equity - margin


def check_margin_alert(margin_level: float) -> Optional[str]:
    """Check if margin level triggers an alert"""
    if margin_level <= RMSConfig.MARGIN_LEVEL_CRITICAL:
        return 'critical'
    elif margin_level <= RMSConfig.MARGIN_LEVEL_WARNING:
        return 'warning'
    return None


def check_loss_alert(profit: float) -> bool:
    """Check if loss exceeds threshold"""
    return profit <= RMSConfig.MAX_LOSS_THRESHOLD


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def get_date_range(days: int) -> tuple:
    """Get date range for the specified number of days"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def export_to_json(data: Dict, filename: str) -> str:
    """Export data to JSON file"""
    filepath = os.path.join(RMSConfig.EXPORT_DIR, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    
    return filepath


def load_from_json(filename: str) -> Optional[Dict]:
    """Load data from JSON file"""
    filepath = os.path.join(RMSConfig.EXPORT_DIR, filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)


def calculate_account_summary(accounts: List[Dict]) -> Dict:
    """Calculate summary statistics for multiple accounts"""
    total_balance = 0.0
    total_equity = 0.0
    total_margin = 0.0
    total_profit = 0.0
    total_positions = 0
    
    for account in accounts:
        total_balance += account.get('balance', 0.0)
        total_equity += account.get('equity', 0.0)
        total_margin += account.get('margin', 0.0)
        total_profit += account.get('profit', 0.0)
        
        if 'positions' in account:
            total_positions += len(account['positions'].get('positions', []))
    
    return {
        'total_accounts': len(accounts),
        'total_balance': total_balance,
        'total_equity': total_equity,
        'total_margin': total_margin,
        'total_profit': total_profit,
        'total_positions': total_positions,
        'average_balance': total_balance / len(accounts) if accounts else 0,
        'average_equity': total_equity / len(accounts) if accounts else 0,
    }


def group_positions_by_symbol(positions: List[Dict]) -> Dict[str, List[Dict]]:
    """Group positions by symbol"""
    grouped = {}
    
    for position in positions:
        symbol = position.get('symbol', 'UNKNOWN')
        if symbol not in grouped:
            grouped[symbol] = []
        grouped[symbol].append(position)
    
    return grouped


def calculate_symbol_exposure(positions: List[Dict]) -> Dict[str, Dict]:
    """Calculate total exposure by symbol"""
    exposure = {}
    
    for position in positions:
        symbol = position.get('symbol', 'UNKNOWN')
        volume = float(position.get('volume', 0))
        profit = float(position.get('profit', 0))
        
        if symbol not in exposure:
            exposure[symbol] = {
                'total_volume': 0.0,
                'position_count': 0,
                'total_profit': 0.0,
                'buy_volume': 0.0,
                'sell_volume': 0.0
            }
        
        exposure[symbol]['total_volume'] += volume
        exposure[symbol]['position_count'] += 1
        exposure[symbol]['total_profit'] += profit
        
        # Assuming 'type' field indicates buy/sell
        pos_type = position.get('type', '').lower()
        if 'buy' in pos_type:
            exposure[symbol]['buy_volume'] += volume
        elif 'sell' in pos_type:
            exposure[symbol]['sell_volume'] += volume
    
    return exposure


def filter_accounts_by_status(accounts: List[Dict], status: str) -> List[Dict]:
    """Filter accounts by status"""
    return [acc for acc in accounts if acc.get('status') == status]


def filter_accounts_by_profit(accounts: List[Dict], min_profit: Optional[float] = None, 
                              max_profit: Optional[float] = None) -> List[Dict]:
    """Filter accounts by profit range"""
    filtered = accounts
    
    if min_profit is not None:
        filtered = [acc for acc in filtered if acc.get('profit', 0) >= min_profit]
    
    if max_profit is not None:
        filtered = [acc for acc in filtered if acc.get('profit', 0) <= max_profit]
    
    return filtered


def find_top_accounts(accounts: List[Dict], by: str = 'profit', limit: int = 10) -> List[Dict]:
    """Find top accounts by specified metric"""
    if by not in ['profit', 'balance', 'equity', 'margin_level']:
        raise ValueError(f"Invalid metric: {by}")
    
    sorted_accounts = sorted(accounts, key=lambda x: x.get(by, 0), reverse=True)
    return sorted_accounts[:limit]


def find_bottom_accounts(accounts: List[Dict], by: str = 'profit', limit: int = 10) -> List[Dict]:
    """Find bottom accounts by specified metric"""
    if by not in ['profit', 'balance', 'equity', 'margin_level']:
        raise ValueError(f"Invalid metric: {by}")
    
    sorted_accounts = sorted(accounts, key=lambda x: x.get(by, 0))
    return sorted_accounts[:limit]


def calculate_performance_metrics(trades: List[Dict]) -> Dict:
    """Calculate performance metrics from trade history"""
    if not trades:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'total_profit': 0.0,
            'total_loss': 0.0,
            'profit_factor': 0.0,
            'average_win': 0.0,
            'average_loss': 0.0,
        }
    
    winning_trades = []
    losing_trades = []
    
    for trade in trades:
        profit = getattr(trade, 'Profit', 0)
        if profit > 0:
            winning_trades.append(profit)
        elif profit < 0:
            losing_trades.append(profit)
    
    total_profit = sum(winning_trades)
    total_loss = abs(sum(losing_trades))
    
    return {
        'total_trades': len(trades),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': (len(winning_trades) / len(trades) * 100) if trades else 0.0,
        'total_profit': total_profit,
        'total_loss': total_loss,
        'profit_factor': (total_profit / total_loss) if total_loss > 0 else 0.0,
        'average_win': (total_profit / len(winning_trades)) if winning_trades else 0.0,
        'average_loss': (total_loss / len(losing_trades)) if losing_trades else 0.0,
    }


def validate_login_id(login_id: any) -> bool:
    """Validate MT5 login ID"""
    try:
        login_int = int(login_id)
        return login_int > 0
    except (ValueError, TypeError):
        return False


def sanitize_symbol(symbol: str) -> str:
    """Sanitize trading symbol"""
    return symbol.strip().upper() if symbol else ''


def get_account_health_status(account: Dict) -> str:
    """Determine account health status based on metrics"""
    margin_level = account.get('margin_level', 0)
    profit = account.get('profit', 0)
    
    if margin_level <= RMSConfig.MARGIN_LEVEL_CRITICAL:
        return 'critical'
    elif margin_level <= RMSConfig.MARGIN_LEVEL_WARNING:
        return 'warning'
    elif profit <= RMSConfig.MAX_LOSS_THRESHOLD:
        return 'warning'
    else:
        return 'healthy'


def generate_alert_message(account: Dict) -> Optional[str]:
    """Generate alert message for account"""
    alerts = []
    
    margin_level = account.get('margin_level', 0)
    profit = account.get('profit', 0)
    login_id = account.get('login_id', 'Unknown')
    
    if margin_level <= RMSConfig.MARGIN_LEVEL_CRITICAL:
        alerts.append(f"CRITICAL: Account {login_id} margin level at {margin_level:.2f}%")
    elif margin_level <= RMSConfig.MARGIN_LEVEL_WARNING:
        alerts.append(f"WARNING: Account {login_id} margin level at {margin_level:.2f}%")
    
    if profit <= RMSConfig.MAX_LOSS_THRESHOLD:
        alerts.append(f"WARNING: Account {login_id} loss at {format_currency(profit)}")
    
    return ' | '.join(alerts) if alerts else None


# Initialize logging when module is imported
setup_logging()
