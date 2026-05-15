"""FRIDAY CLI entrypoint."""

import argparse
import asyncio
import sys

from friday.core.engine import FridayEngine
from friday.core.keyring import get as get_key
from friday.memory.memory_tree import MemoryTree
from friday.compress.tokenjuice import compress_text


def main():
    parser = argparse.ArgumentParser(
        prog="friday",
        description="FRIDAY — Your Personal AI Infrastructure",
    )
    parser.add_argument("--version", action="version", version="FRIDAY 0.1.0")
    
    sub = parser.add_subparsers(dest="command")
    
    # chat — interactive mode
    chat = sub.add_parser("chat", help="Interactive chat session")
    chat.add_argument("--gateway", action="store_true", help="Start Telegram gateway too")
    
    # setup — install, config, init
    setup = sub.add_parser("setup", help="One-time setup wizard")
    
    # gateway — start just the gateway
    gw = sub.add_parser("gateway", help="Start gateway listener")
    gw.add_argument("--telegram", action="store_true", default=True)
    
    # tool — run a single tool
    tool = sub.add_parser("tool", help="Run a tool directly")
    tool.add_argument("name", help="Tool name")
    tool.add_argument("args", nargs="?", default="", help="Tool arguments")
    
    # memory — memory tree ops
    mem = sub.add_parser("memory", help="Memory tree operations")
    mem.add_argument("action", choices=["add", "search", "list", "expire"])
    mem.add_argument("text", nargs="?", default="", help="Text to store or search")
    mem.add_argument("--tag", default="", help="Optional tag")
    
    # compress — compress text
    comp = sub.add_parser("compress", help="Token-compress text or URL")
    comp.add_argument("input", help="Text or URL to compress")
    comp.add_argument("--max-len", type=int, default=5000, help="Max output length")
    
    # cron — manage scheduled jobs
    cron = sub.add_parser("cron", help="Manage background jobs")
    cron.add_argument("action", choices=["list", "add", "cancel"], default="list", nargs="?")
    cron.add_argument("--name", default="")
    cron.add_argument("--interval", type=int, default=60)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to handler
    handlers = {
        "setup": cmd_setup,
        "chat": cmd_chat,
        "gateway": cmd_gateway,
        "tool": cmd_tool,
        "memory": cmd_memory,
        "compress": cmd_compress,
        "cron": cmd_cron,
    }
    
    handler = handlers.get(args.command)
    if handler:
        return handler(args)
    
    parser.print_help()
    return 1


def cmd_setup(args) -> int:
    """Run the setup wizard."""
    print("🛠️  FRIDAY Setup Wizard")
    print("=" * 40)
    print()
    print("1. Check D:\\Friday\\.env has your API keys")
    print("2. Install dependencies: pip install -e .")
    print("3. Test: friday --version")
    print("4. Start chat: friday chat")
    print()
    print("Status checks:")
    
    # Check .env
    from pathlib import Path
    env_path = Path("D:/Friday/.env")
    if env_path.exists():
        print("  ✅ D:\\Friday\\.env found")
    else:
        print("  ❌ D:\\Friday\\.env not found — copy .env.example and fill in keys")
    
    # Check python version
    import platform
    py = platform.python_version()
    print(f"  ✅ Python {py}")
    
    # Check key env vars
    for key in ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN"]:
        val = get_key(key)
        status = "✅" if val else "⬜"
        print(f"  {status} {key}")
    
    print()
    print("Setup complete. Run: friday chat")
    return 0


def cmd_chat(args) -> int:
    """Interactive chat session."""
    engine = FridayEngine()
    
    if args.gateway:
        # Try to add Telegram gateway
        if engine.add_telegram_gateway():
            print("📡 Telegram gateway connected")
        else:
            print("⚠️  No TELEGRAM_BOT_TOKEN found. Gateway mode disabled.")
        
        # Run in async mode
        try:
            asyncio.run(engine.start())
        except KeyboardInterrupt:
            print("\n👋 Goodbye")
        return 0
    
    # Simple CLI chat loop
    print("🤖 FRIDAY Chat (Phase 0)")
    print("Type 'help' for commands, 'quit' to exit\n")
    
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye")
            break
        
        if not message:
            continue
        if message.lower() in ("quit", "exit", "bye"):
            print("👋 Goodbye")
            break
        
        # Run synchronously for CLI
        response = asyncio.run(engine.handle_message(message))
        print(f"Friday: {response}\n")
    
    return 0


def cmd_gateway(args) -> int:
    """Start gateway listener."""
    engine = FridayEngine()
    
    if args.telegram:
        if engine.add_telegram_gateway():
            print("📡 Telegram gateway connected")
        else:
            print("❌ No TELEGRAM_BOT_TOKEN in D:\\Friday\\.env")
            return 1
    
    print("🚀 Gateway running. Press Ctrl+C to stop.")
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        print("\n👋 Gateway stopped")
    return 0


def cmd_tool(args) -> int:
    """Run a single tool."""
    from friday.core.tools import get_registry
    registry = get_registry()
    
    if args.name == "list":
        print("Available tools:")
        for name in registry.list_tools():
            schema = registry.get_schema(name)
            desc = schema.get("description", "") if schema else ""
            print(f"  /{name:15} — {desc}")
        return 0
    
    try:
        result = registry.call(args.name, command=args.args)
        print(result)
        return 0
    except KeyError:
        print(f"Unknown tool: {args.name}")
        print(f"Available: {', '.join(registry.list_tools())}")
        return 1


def cmd_memory(args) -> int:
    """Memory tree operations."""
    tree = MemoryTree(db_path="friday_memory.db")
    
    if args.action == "add":
        tree.add(args.text, tag=args.tag)
        print("✅ Stored in memory")
    elif args.action == "search":
        results = tree.search(args.text)
        if not results:
            print("No matches")
        for r in results:
            print(f"[{r['timestamp']}] {r['text'][:100]}... (tag: {r['tag']})")
    elif args.action == "list":
        results = tree.search("")
        print(f"{len(results)} stored items")
        for r in results[:10]:
            print(f"  [{r['timestamp']}] {r['text'][:60]}...")
    elif args.action == "expire":
        count = tree.expire_old()
        print(f"✅ Expired {count} old items")
    
    return 0


def cmd_compress(args) -> int:
    """Compress text or URL."""
    result = compress_text(args.input, max_len=args.max_len)
    print(result)
    return 0


def cmd_cron(args) -> int:
    """Manage cron jobs."""
    from friday.core.cron import get_scheduler
    scheduler = get_scheduler()
    
    if args.action == "list":
        jobs = scheduler.list_jobs()
        if not jobs:
            print("No scheduled jobs")
        for j in jobs:
            print(f"  {j['id']}: {j['name']} (every {j['interval_sec']}s, run {j['run_count']}x)")
    elif args.action == "add":
        if not args.name:
            print("--name required")
            return 1
        def dummy_task():
            print(f"[cron] Running {args.name}")
        scheduler.schedule(args.name, args.interval, dummy_task)
        print(f"✅ Scheduled '{args.name}' every {args.interval}s")
    elif args.action == "cancel":
        if not args.name:
            print("--name required")
            return 1
        cancelled = False
        for jid, job in scheduler.jobs.items():
            if job.name == args.name:
                scheduler.cancel(jid)
                cancelled = True
        print(f"✅ Cancelled '{args.name}'" if cancelled else f"No job named '{args.name}'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
