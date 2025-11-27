"""
Configuration settings for Real-time Monitor System
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class RMSConfig:
    """Configuration class for RMS"""
    
    # MT5 Connection Settings
    MT5_HOST = os.getenv('MT5_HOST', 'localhost')
    MT5_PORT = int(os.getenv('MT5_PORT', 443))
    MT5_MANAGER_USER = int(os.getenv('MT5_MANAGER_USER', 0))
    MT5_MANAGER_PASS = os.getenv('MT5_MANAGER_PASS', '')
    
    # RMS Settings
    UPDATE_INTERVAL = int(os.getenv('RMS_UPDATE_INTERVAL', 5))  # seconds
    TRADE_HISTORY_DAYS = int(os.getenv('RMS_TRADE_HISTORY_DAYS', 30))  # days
    
    # WebSocket Settings
    WS_HOST = os.getenv('WS_HOST', '0.0.0.0')
    WS_PORT = int(os.getenv('WS_PORT', 8765))
    
    # Cache Settings
    CACHE_DURATION = int(os.getenv('RMS_CACHE_DURATION', 300))  # seconds
    
    # Logging Settings
    LOG_LEVEL = os.getenv('RMS_LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('RMS_LOG_FILE', 'rms.log')
    
    # Export Settings
    EXPORT_DIR = os.getenv('RMS_EXPORT_DIR', 'exports')
    
    # Alert Thresholds
    MARGIN_LEVEL_WARNING = float(os.getenv('MARGIN_LEVEL_WARNING', 150.0))
    MARGIN_LEVEL_CRITICAL = float(os.getenv('MARGIN_LEVEL_CRITICAL', 100.0))
    MAX_LOSS_THRESHOLD = float(os.getenv('MAX_LOSS_THRESHOLD', -1000.0))
    
    # Performance Settings
    MAX_MONITORED_ACCOUNTS = int(os.getenv('MAX_MONITORED_ACCOUNTS', 100000))
    BATCH_SIZE = int(os.getenv('RMS_BATCH_SIZE', 100))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.MT5_HOST:
            errors.append("MT5_HOST is not set")
        
        if not cls.MT5_MANAGER_PASS:
            errors.append("MT5_MANAGER_PASS is not set")
        
        if cls.UPDATE_INTERVAL < 1:
            errors.append("UPDATE_INTERVAL must be at least 1 second")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
    
    @classmethod
    def to_dict(cls):
        """Convert configuration to dictionary"""
        return {
            'mt5': {
                'host': cls.MT5_HOST,
                'port': cls.MT5_PORT,
                'user': cls.MT5_MANAGER_USER,
            },
            'rms': {
                'update_interval': cls.UPDATE_INTERVAL,
                'trade_history_days': cls.TRADE_HISTORY_DAYS,
                'cache_duration': cls.CACHE_DURATION,
                'max_monitored_accounts': cls.MAX_MONITORED_ACCOUNTS,
            },
            'websocket': {
                'host': cls.WS_HOST,
                'port': cls.WS_PORT,
            },
            'alerts': {
                'margin_level_warning': cls.MARGIN_LEVEL_WARNING,
                'margin_level_critical': cls.MARGIN_LEVEL_CRITICAL,
                'max_loss_threshold': cls.MAX_LOSS_THRESHOLD,
            }
        }


# Create exports directory if it doesn't exist
if not os.path.exists(RMSConfig.EXPORT_DIR):
    os.makedirs(RMSConfig.EXPORT_DIR)
