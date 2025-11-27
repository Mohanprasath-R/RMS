"""
Real-time Monitor System (RMS) for MT5 Trading Platform
Monitors client trades, accounts, and open positions in real-time
"""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from collections import defaultdict
import json

from Services import MT5ManagerActions, get_manager_instance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AccountMonitor:
    """Monitor individual trading account in real-time"""
    
    def __init__(self, login_id: int):
        self.login_id = login_id
        self.balance = 0.0
        self.equity = 0.0
        self.margin = 0.0
        self.free_margin = 0.0
        self.margin_level = 0.0
        self.profit = 0.0
        self.last_update = None
        self.status = "active"
        self.group = ""
        self.leverage = 0
        
    def update(self, manager: MT5ManagerActions) -> Dict:
        """Update account information from MT5"""
        try:
            # Get account details
            account_info = manager.get_account_details(self.login_id)
            
            if account_info:
                self.balance = account_info.get('balance', 0.0)
                self.equity = account_info.get('equity', 0.0)
                self.margin = account_info.get('margin', 0.0)
                self.free_margin = account_info.get('free_margin', 0.0)
                self.margin_level = account_info.get('margin_level', 0.0)
                self.profit = account_info.get('profit', 0.0)
                self.group = account_info.get('group', '')
                self.leverage = account_info.get('leverage', 0)
                self.last_update = datetime.now()
                self.status = "active"
                
                return self.to_dict()
            else:
                self.status = "unavailable"
                return None
                
        except Exception as e:
            logger.error(f"Error updating account {self.login_id}: {e}")
            self.status = "error"
            return None
    
    def to_dict(self) -> Dict:
        """Convert account data to dictionary"""
        return {
            'login_id': self.login_id,
            'balance': self.balance,
            'equity': self.equity,
            'margin': self.margin,
            'free_margin': self.free_margin,
            'margin_level': self.margin_level,
            'profit': self.profit,
            'group': self.group,
            'leverage': self.leverage,
            'status': self.status,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


class PositionMonitor:
    """Monitor open positions for an account"""
    
    def __init__(self, login_id: int):
        self.login_id = login_id
        self.positions = []
        self.last_update = None
        
    def update(self, manager: MT5ManagerActions) -> List[Dict]:
        """Update open positions from MT5"""
        try:
            positions = manager.get_open_positions(self.login_id)
            
            if positions:
                self.positions = positions
                self.last_update = datetime.now()
                return self.positions
            else:
                self.positions = []
                return []
                
        except Exception as e:
            logger.error(f"Error updating positions for account {self.login_id}: {e}")
            return []
    
    def get_positions_by_symbol(self, symbol: str) -> List[Dict]:
        """Get positions filtered by symbol"""
        return [pos for pos in self.positions if pos.get('symbol') == symbol]
    
    def get_total_volume_by_symbol(self) -> Dict[str, float]:
        """Get total volume grouped by symbol"""
        volume_by_symbol = defaultdict(float)
        for pos in self.positions:
            symbol = pos.get('symbol', '')
            volume = pos.get('volume', 0.0)
            volume_by_symbol[symbol] += volume
        return dict(volume_by_symbol)
    
    def to_dict(self) -> Dict:
        """Convert position data to dictionary"""
        return {
            'login_id': self.login_id,
            'positions': self.positions,
            'position_count': len(self.positions),
            'symbols': list(set(pos.get('symbol', '') for pos in self.positions)),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


class TradeMonitor:
    """Monitor trade history for an account"""
    
    def __init__(self, login_id: int):
        self.login_id = login_id
        self.trades = []
        self.last_update = None
        self.from_date = datetime.now() - timedelta(days=30)  # Last 30 days
        
    def update(self, manager: MT5ManagerActions) -> List[Dict]:
        """Update trade history from MT5"""
        try:
            trades = manager.get_closed_trades(self.login_id, self.from_date)
            
            if trades:
                self.trades = trades
                self.last_update = datetime.now()
                return self.trades
            else:
                self.trades = []
                return []
                
        except Exception as e:
            logger.error(f"Error updating trades for account {self.login_id}: {e}")
            return []
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """Get trades filtered by symbol"""
        return [trade for trade in self.trades if trade.get('symbol') == symbol]
    
    def get_daily_stats(self) -> Dict:
        """Calculate daily trading statistics"""
        today = datetime.now().date()
        today_trades = [t for t in self.trades 
                       if hasattr(t, 'Time') and datetime.fromtimestamp(t.Time).date() == today]
        
        total_volume = sum(getattr(t, 'Volume', 0) for t in today_trades)
        total_profit = sum(getattr(t, 'Profit', 0) for t in today_trades)
        
        return {
            'trade_count': len(today_trades),
            'total_volume': total_volume,
            'total_profit': total_profit,
            'date': today.isoformat()
        }
    
    def to_dict(self) -> Dict:
        """Convert trade data to dictionary"""
        return {
            'login_id': self.login_id,
            'trade_count': len(self.trades),
            'trades': self.trades[:100],  # Limit to last 100 trades
            'daily_stats': self.get_daily_stats(),
            'last_update': self.last_update.isoformat() if self.last_update else None
        }


class RealTimeMonitorSystem:
    """
    Main Real-time Monitor System that coordinates all monitoring activities
    """
    
    def __init__(self, update_interval: int = 5):
        """
        Initialize RMS
        
        Args:
            update_interval: Seconds between updates (default: 5)
        """
        self.update_interval = update_interval
        self.monitored_accounts = {}  # login_id -> monitors dict
        self.manager = None
        self.running = False
        self.monitor_thread = None
        self._callbacks = []
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_updates': 0,
            'last_update': None,
            'errors': 0,
            'monitored_count': 0
        }
        
    def initialize(self):
        """Initialize MT5 manager connection"""
        try:
            self.manager = MT5ManagerActions()
            if not self.manager.manager:
                raise Exception("Failed to connect to MT5 Manager")
            logger.info("RMS initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize RMS: {e}")
            return False
    
    def add_account(self, login_id: int):
        """Add an account to monitoring"""
        with self._lock:
            if login_id not in self.monitored_accounts:
                self.monitored_accounts[login_id] = {
                    'account': AccountMonitor(login_id),
                    'positions': PositionMonitor(login_id),
                    'trades': TradeMonitor(login_id)
                }
                logger.info(f"Added account {login_id} to monitoring")
                self.stats['monitored_count'] = len(self.monitored_accounts)
    
    def remove_account(self, login_id: int):
        """Remove an account from monitoring"""
        with self._lock:
            if login_id in self.monitored_accounts:
                del self.monitored_accounts[login_id]
                logger.info(f"Removed account {login_id} from monitoring")
                self.stats['monitored_count'] = len(self.monitored_accounts)
    
    def add_callback(self, callback: Callable):
        """Add a callback function to be called when data is updated"""
        self._callbacks.append(callback)
    
    def _update_all_accounts(self):
        """Update all monitored accounts"""
        if not self.manager:
            logger.error("Manager not initialized")
            return
        
        with self._lock:
            accounts_data = []
            
            for login_id, monitors in self.monitored_accounts.items():
                try:
                    # Update account info
                    account_data = monitors['account'].update(self.manager)
                    
                    # Update positions
                    positions_data = monitors['positions'].update(self.manager)
                    
                    # Update trades (less frequently - every 5th update)
                    if self.stats['total_updates'] % 5 == 0:
                        trades_data = monitors['trades'].update(self.manager)
                    else:
                        trades_data = monitors['trades'].trades
                    
                    if account_data:
                        accounts_data.append({
                            'account': account_data,
                            'positions': monitors['positions'].to_dict(),
                            'trades_summary': {
                                'trade_count': len(trades_data),
                                'last_update': monitors['trades'].last_update.isoformat() 
                                              if monitors['trades'].last_update else None
                            }
                        })
                    
                except Exception as e:
                    logger.error(f"Error updating account {login_id}: {e}")
                    self.stats['errors'] += 1
            
            self.stats['total_updates'] += 1
            self.stats['last_update'] = datetime.now()
            
            # Notify callbacks
            for callback in self._callbacks:
                try:
                    callback(accounts_data)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        logger.info(f"RMS monitor loop started (interval: {self.update_interval}s)")
        
        while self.running:
            try:
                self._update_all_accounts()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}")
                self.stats['errors'] += 1
                time.sleep(self.update_interval)
    
    def start(self):
        """Start real-time monitoring"""
        if not self.manager:
            if not self.initialize():
                logger.error("Cannot start RMS - initialization failed")
                return False
        
        if self.running:
            logger.warning("RMS already running")
            return False
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("RMS started successfully")
        return True
    
    def stop(self):
        """Stop real-time monitoring"""
        if not self.running:
            logger.warning("RMS not running")
            return
        
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("RMS stopped")
    
    def get_account_snapshot(self, login_id: int) -> Optional[Dict]:
        """Get current snapshot of an account"""
        with self._lock:
            if login_id not in self.monitored_accounts:
                return None
            
            monitors = self.monitored_accounts[login_id]
            return {
                'account': monitors['account'].to_dict(),
                'positions': monitors['positions'].to_dict(),
                'trades': monitors['trades'].to_dict()
            }
    
    def get_all_accounts_snapshot(self) -> Dict:
        """Get current snapshot of all monitored accounts"""
        with self._lock:
            snapshots = {}
            for login_id in self.monitored_accounts.keys():
                snapshot = self.get_account_snapshot(login_id)
                if snapshot:
                    snapshots[login_id] = snapshot
            return snapshots
    
    def get_positions_by_symbol(self, symbol: str) -> List[Dict]:
        """Get all open positions for a specific symbol across all accounts"""
        with self._lock:
            all_positions = []
            for login_id, monitors in self.monitored_accounts.items():
                positions = monitors['positions'].get_positions_by_symbol(symbol)
                for pos in positions:
                    pos['login_id'] = login_id
                    all_positions.append(pos)
            return all_positions
    
    def get_total_exposure_by_symbol(self) -> Dict[str, Dict]:
        """Calculate total exposure by symbol across all accounts"""
        with self._lock:
            exposure = defaultdict(lambda: {'volume': 0.0, 'accounts': 0, 'positions': 0})
            
            for login_id, monitors in self.monitored_accounts.items():
                volume_by_symbol = monitors['positions'].get_total_volume_by_symbol()
                for symbol, volume in volume_by_symbol.items():
                    exposure[symbol]['volume'] += volume
                    exposure[symbol]['accounts'] += 1
                    exposure[symbol]['positions'] += len(
                        monitors['positions'].get_positions_by_symbol(symbol)
                    )
            
            return dict(exposure)
    
    def get_stats(self) -> Dict:
        """Get RMS statistics"""
        return {
            **self.stats,
            'running': self.running,
            'update_interval': self.update_interval,
            'last_update': self.stats['last_update'].isoformat() 
                          if self.stats['last_update'] else None
        }
    
    def export_data(self, filepath: str):
        """Export all monitoring data to JSON file"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'stats': self.get_stats(),
                'accounts': self.get_all_accounts_snapshot(),
                'exposure': self.get_total_exposure_by_symbol()
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Data exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            return False


# Singleton instance
_rms_instance = None

def get_rms_instance(update_interval: int = 5) -> RealTimeMonitorSystem:
    """Get or create the global RMS instance"""
    global _rms_instance
    if _rms_instance is None:
        _rms_instance = RealTimeMonitorSystem(update_interval)
    return _rms_instance
