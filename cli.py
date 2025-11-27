"""
Command-line interface for Real-time Monitor System
"""

import argparse
import sys
import time
from RealTimeMonitor import get_rms_instance
from WebSocketServer import WebSocketServer
from config import RMSConfig
import logging

logger = logging.getLogger(__name__)


def start_monitor(args):
    """Start the RMS monitoring system"""
    try:
        # Initialize RMS
        rms = get_rms_instance(update_interval=args.interval)
        
        if not rms.initialize():
            logger.error("Failed to initialize RMS")
            sys.exit(1)
        
        # Add accounts if specified
        if args.accounts:
            for login_id in args.accounts:
                rms.add_account(login_id)
                logger.info(f"Added account {login_id} to monitoring")
        
        # Start monitoring
        if not rms.start():
            logger.error("Failed to start RMS")
            sys.exit(1)
        
        logger.info("RMS monitoring started successfully")
        logger.info(f"Update interval: {args.interval} seconds")
        logger.info(f"Monitoring {len(args.accounts if args.accounts else [])} accounts")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping RMS...")
            rms.stop()
            logger.info("RMS stopped")
            
    except Exception as e:
        logger.error(f"Error starting monitor: {e}")
        sys.exit(1)


def start_websocket(args):
    """Start the WebSocket server"""
    try:
        server = WebSocketServer(host=args.host, port=args.port)
        logger.info(f"Starting WebSocket server on {args.host}:{args.port}")
        server.run()
    except Exception as e:
        logger.error(f"Error starting WebSocket server: {e}")
        sys.exit(1)


def add_account_cmd(args):
    """Add account to monitoring"""
    try:
        rms = get_rms_instance()
        if not rms.initialize():
            logger.error("Failed to initialize RMS")
            sys.exit(1)
        
        rms.add_account(args.login_id)
        logger.info(f"Account {args.login_id} added to monitoring")
        
    except Exception as e:
        logger.error(f"Error adding account: {e}")
        sys.exit(1)


def remove_account_cmd(args):
    """Remove account from monitoring"""
    try:
        rms = get_rms_instance()
        rms.remove_account(args.login_id)
        logger.info(f"Account {args.login_id} removed from monitoring")
        
    except Exception as e:
        logger.error(f"Error removing account: {e}")
        sys.exit(1)


def snapshot_cmd(args):
    """Get snapshot of monitored accounts"""
    try:
        rms = get_rms_instance()
        if not rms.initialize():
            logger.error("Failed to initialize RMS")
            sys.exit(1)
        
        if args.login_id:
            snapshot = rms.get_account_snapshot(args.login_id)
            print(f"\n=== Account {args.login_id} Snapshot ===")
            print_snapshot(snapshot)
        else:
            snapshots = rms.get_all_accounts_snapshot()
            print(f"\n=== All Accounts Snapshot ({len(snapshots)} accounts) ===")
            for login_id, snapshot in snapshots.items():
                print(f"\n--- Account {login_id} ---")
                print_snapshot(snapshot)
                
    except Exception as e:
        logger.error(f"Error getting snapshot: {e}")
        sys.exit(1)


def exposure_cmd(args):
    """Get symbol exposure"""
    try:
        rms = get_rms_instance()
        if not rms.initialize():
            logger.error("Failed to initialize RMS")
            sys.exit(1)
        
        if args.symbol:
            positions = rms.get_positions_by_symbol(args.symbol)
            print(f"\n=== Positions for {args.symbol} ===")
            print(f"Total positions: {len(positions)}")
            for pos in positions:
                print(f"  Account {pos.get('login_id')}: {pos.get('volume')} lots, Profit: {pos.get('profit')}")
        else:
            exposure = rms.get_total_exposure_by_symbol()
            print(f"\n=== Total Symbol Exposure ===")
            for symbol, data in exposure.items():
                print(f"{symbol}:")
                print(f"  Volume: {data['volume']:.2f} lots")
                print(f"  Accounts: {data['accounts']}")
                print(f"  Positions: {data['positions']}")
                
    except Exception as e:
        logger.error(f"Error getting exposure: {e}")
        sys.exit(1)


def stats_cmd(args):
    """Get RMS statistics"""
    try:
        rms = get_rms_instance()
        stats = rms.get_stats()
        
        print("\n=== RMS Statistics ===")
        print(f"Running: {stats['running']}")
        print(f"Update Interval: {stats['update_interval']}s")
        print(f"Monitored Accounts: {stats['monitored_count']}")
        print(f"Total Updates: {stats['total_updates']}")
        print(f"Errors: {stats['errors']}")
        print(f"Last Update: {stats['last_update']}")
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        sys.exit(1)


def export_cmd(args):
    """Export monitoring data"""
    try:
        rms = get_rms_instance()
        if not rms.initialize():
            logger.error("Failed to initialize RMS")
            sys.exit(1)
        
        filepath = args.output if args.output else f"rms_export_{int(time.time())}.json"
        if rms.export_data(filepath):
            logger.info(f"Data exported to {filepath}")
        else:
            logger.error("Failed to export data")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        sys.exit(1)


def print_snapshot(snapshot):
    """Print snapshot in readable format"""
    if not snapshot:
        print("  No data available")
        return
    
    account = snapshot.get('account', {})
    positions = snapshot.get('positions', {})
    
    print(f"  Balance: ${account.get('balance', 0):.2f}")
    print(f"  Equity: ${account.get('equity', 0):.2f}")
    print(f"  Margin: ${account.get('margin', 0):.2f}")
    print(f"  Free Margin: ${account.get('free_margin', 0):.2f}")
    print(f"  Margin Level: {account.get('margin_level', 0):.2f}%")
    print(f"  Profit: ${account.get('profit', 0):.2f}")
    print(f"  Group: {account.get('group', 'N/A')}")
    print(f"  Leverage: 1:{account.get('leverage', 0)}")
    print(f"  Open Positions: {positions.get('position_count', 0)}")
    print(f"  Status: {account.get('status', 'unknown')}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Real-time Monitor System (RMS) for MT5 Trading',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Start monitor command
    start_parser = subparsers.add_parser('start', help='Start RMS monitoring')
    start_parser.add_argument('-i', '--interval', type=int, default=RMSConfig.UPDATE_INTERVAL,
                            help='Update interval in seconds (default: 5)')
    start_parser.add_argument('-a', '--accounts', type=int, nargs='+',
                            help='Account IDs to monitor')
    start_parser.set_defaults(func=start_monitor)
    
    # Start WebSocket server command
    ws_parser = subparsers.add_parser('websocket', help='Start WebSocket server')
    ws_parser.add_argument('--host', default=RMSConfig.WS_HOST,
                          help='WebSocket host (default: 0.0.0.0)')
    ws_parser.add_argument('--port', type=int, default=RMSConfig.WS_PORT,
                          help='WebSocket port (default: 8765)')
    ws_parser.set_defaults(func=start_websocket)
    
    # Add account command
    add_parser = subparsers.add_parser('add', help='Add account to monitoring')
    add_parser.add_argument('login_id', type=int, help='Account login ID')
    add_parser.set_defaults(func=add_account_cmd)
    
    # Remove account command
    remove_parser = subparsers.add_parser('remove', help='Remove account from monitoring')
    remove_parser.add_argument('login_id', type=int, help='Account login ID')
    remove_parser.set_defaults(func=remove_account_cmd)
    
    # Snapshot command
    snapshot_parser = subparsers.add_parser('snapshot', help='Get account snapshot')
    snapshot_parser.add_argument('-l', '--login-id', type=int,
                                help='Specific account ID (omit for all)')
    snapshot_parser.set_defaults(func=snapshot_cmd)
    
    # Exposure command
    exposure_parser = subparsers.add_parser('exposure', help='Get symbol exposure')
    exposure_parser.add_argument('-s', '--symbol', help='Specific symbol (omit for all)')
    exposure_parser.set_defaults(func=exposure_cmd)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Get RMS statistics')
    stats_parser.set_defaults(func=stats_cmd)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export monitoring data')
    export_parser.add_argument('-o', '--output', help='Output file path')
    export_parser.set_defaults(func=export_cmd)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == '__main__':
    main()
