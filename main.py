"""
Main entry point for Salesforce sync
"""

import sys
from dotenv import load_dotenv
from sync_data import SalesforceSync

# Load .env file
load_dotenv()


def main():
    """Main function"""
    sync = SalesforceSync()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'full':
            # Full sync
            sync.sync_all()

        elif command == 'incremental':
            # Incremental sync
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            sync.sync_incremental(hours)

        else:
            print("Usage:")
            print("  python main.py full                 # Sync all data")
            print("  python main.py incremental [hours]  # Sync recent changes")
            print()
            print("Examples:")
            print("  python main.py full")
            print("  python main.py incremental 24")
            print("  python main.py incremental 6")
    else:
        # Default: full sync
        print("Running full sync...")
        sync.sync_all()


if __name__ == "__main__":
    main()