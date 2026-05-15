"""FRIDAY CLI entrypoint."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="friday",
        description="FRIDAY — Your Personal AI Infrastructure",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    parser.add_argument("--setup", action="store_true", help="Run first-time setup")
    parser.add_argument("--chat", action="store_true", help="Start interactive chat")
    parser.add_argument("--gateway", type=str, help="Start gateway (e.g., telegram)")
    parser.add_argument("--config", type=str, help="Path to config file")
    
    args = parser.parse_args()
    
    if args.setup:
        print("🛠️  FRIDAY setup wizard — coming in Phase 1")
        return 0
    
    if args.chat:
        print("💬 FRIDAY chat — engine coming in Phase 0")
        return 0
    
    if args.gateway:
        print(f"📡 Starting {args.gateway} gateway — coming in Phase 1")
        return 0
    
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
