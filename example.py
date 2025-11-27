"""
Example script demonstrating basic RMS usage
"""

from RealTimeMonitor import get_rms_instance
import time

def main():
    print("🔥 RMS Example - Basic Usage\n")
    
    # Initialize RMS with 5-second update interval
    print("1. Initializing RMS...")
    rms = get_rms_instance(update_interval=5)
    
    if not rms.initialize():
        print("❌ Failed to initialize RMS")
        return
    
    print("✅ RMS initialized successfully\n")
    
    # Add accounts to monitor
    print("2. Adding accounts to monitor...")
    test_accounts = [123456, 789012]  # Replace with your actual MT5 login IDs
    
    for login_id in test_accounts:
        rms.add_account(login_id)
        print(f"   Added account: {login_id}")
    
    print()
    
    # Start monitoring
    print("3. Starting real-time monitoring...")
    if not rms.start():
        print("❌ Failed to start RMS")
        return
    
    print("✅ Monitoring started\n")
    
    # Monitor for 30 seconds
    print("4. Monitoring accounts for 30 seconds...\n")
    
    try:
        for i in range(6):  # 6 iterations = 30 seconds
            time.sleep(5)
            
            # Get statistics
            stats = rms.get_stats()
            print(f"\n--- Update #{stats['total_updates']} ---")
            print(f"Monitored accounts: {stats['monitored_count']}")
            print(f"Errors: {stats['errors']}")
            
            # Get all account snapshots
            snapshots = rms.get_all_accounts_snapshot()
            
            for login_id, snapshot in snapshots.items():
                account = snapshot['account']
                positions = snapshot['positions']
                
                print(f"\nAccount {login_id}:")
                print(f"  Balance: ${account['balance']:.2f}")
                print(f"  Equity: ${account['equity']:.2f}")
                print(f"  Profit: ${account['profit']:.2f}")
                print(f"  Margin Level: {account['margin_level']:.2f}%")
                print(f"  Open Positions: {positions['position_count']}")
                
                # Show margin alert
                if account['margin_level'] < 150 and account['margin_level'] > 0:
                    print(f"  ⚠️ WARNING: Low margin level!")
                
                if account['profit'] < -100:
                    print(f"  ⚠️ WARNING: Significant loss detected!")
            
            # Show symbol exposure
            exposure = rms.get_total_exposure_by_symbol()
            if exposure:
                print(f"\nSymbol Exposure:")
                for symbol, data in exposure.items():
                    print(f"  {symbol}: {data['volume']:.2f} lots ({data['positions']} positions)")
        
        print("\n✅ Monitoring completed successfully")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Monitoring interrupted by user")
    
    finally:
        # Stop monitoring
        print("\n5. Stopping RMS...")
        rms.stop()
        print("✅ RMS stopped\n")
        
        # Export final data
        print("6. Exporting data...")
        export_file = f"rms_export_{int(time.time())}.json"
        if rms.export_data(export_file):
            print(f"✅ Data exported to: {export_file}\n")
        else:
            print("❌ Failed to export data\n")


if __name__ == "__main__":
    main()
