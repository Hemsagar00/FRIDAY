"""FRIDAY engine — Core agent reasoning loop."""

import asyncio
from typing import Any, Dict, List, Optional

from .tools import get_registry
from .skills_loader import get_loader
from .gateway import GatewayRouter, get_router
from .cron import get_scheduler
from .keyring import require


class FridayEngine:
    """Main agent reasoning loop.
    
    Wire-up: loads tools, skills, gateways, and cron on init.
    Receives messages from any channel and dispatches appropriately.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.tools = get_registry()
        self.skills = get_loader()
        self.router = get_router()
        self.cron = get_scheduler()
        self.conversations: Dict[str, List[Dict]] = {}
        self._setup_gateway()
    
    def _setup_gateway(self):
        """Register the engine as the gateway message handler."""
        self.router.set_handler(self._on_gateway_message)
    
    async def _on_gateway_message(self, sender: str, text: str, gateway: str, **meta):
        """Handle incoming messages from any gateway."""
        session_id = f"{gateway}:{sender}"
        response = await self.handle_message(text, session_id=session_id)
        # Send response back through the gateway
        gw = self.router.gateways.get(gateway)
        if gw:
            await gw.send(sender, response)
    
    async def handle_message(self, message: str, session_id: str = "default") -> str:
        """Process an incoming message and return a response."""
        # Append to conversation history
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        self.conversations[session_id].append({"role": "user", "content": message})
        
        # Phase 0: Simple dispatch — check for tool calls, skill triggers, or echo
        response = await self._dispatch(message, session_id)
        
        # Store response
        self.conversations[session_id].append({"role": "friday", "content": response})
        
        # Auto-trim conversation history to prevent context bloat
        max_history = self.config.get("memory_max_turns", 20)
        if len(self.conversations[session_id]) > max_history * 2:
            self.conversations[session_id] = self.conversations[session_id][-max_history * 2:]
        
        return response
    
    async def _dispatch(self, message: str, session_id: str) -> str:
        """Route message to tool, skill, or default response."""
        
        # 1. Check for direct tool invocation: /tool_name args
        if message.startswith("/"):
            parts = message[1:].split(None, 1)
            tool_name = parts[0]
            tool_input = parts[1] if len(parts) > 1 else ""
            
            if tool_name in self.tools.list_tools():
                try:
                    result = self.tools.call(tool_name, command=tool_input)
                    return f"**[{tool_name}]**\n```\n{result}\n```"
                except Exception as e:
                    return f"❌ Tool `{tool_name}` failed: {e}"
            else:
                available = ", ".join(f"`/{t}`" for t in self.tools.list_tools())
                return f"Unknown tool `/{tool_name}`. Available: {available}"
        
        # 2. Check for skill triggers
        skill_name = self.skills.match(message)
        if skill_name:
            skill = self.skills.get(skill_name)
            steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(skill["steps"]))
            return (
                f"🎯 **Skill matched: `{skill_name}`**\n\n"
                f"Trigger: {skill['trigger']}\n\n"
                f"Steps:\n{steps}\n\n"
                f"_(Skill execution in Phase 1 — auto-execution coming soon)_"
            )
        
        # 3. Help command
        if message.lower() in ("help", "?", "/help"):
            tools = ", ".join(f"`/{t}`" for t in self.tools.list_tools())
            skills = ", ".join(f"`{s}`" for s in self.skills.list_skills())
            return (
                f"**FRIDAY v0.1.0 — Phase 0**\n\n"
                f"**Tools:** {tools}\n"
                f"**Skills:** {skills or '(none loaded)'}\n\n"
                f"Usage:\n"
                f"- `/<tool_name> <args>` — Run a tool directly\n"
                f"- Type naturally to trigger skills\n"
                f"- `help` — This message"
            )
        
        # 4. Default: echo with context
        return (
            f"FRIDAY received: _{message}_\n\n"
            f"_(Phase 0 — full reasoning + LLM integration in progress. "
            f"Use `help` to see available tools.)_"
        )
    
    def add_telegram_gateway(self, token: str = None) -> bool:
        """Add a Telegram gateway if token is available."""
        if token is None:
            try:
                token = require("TELEGRAM_BOT_TOKEN")
            except RuntimeError:
                return False
        
        from .gateway import TelegramGateway
        gw = TelegramGateway(token)
        self.router.add(gw)
        return True
    
    async def start(self):
        """Start the engine — gateways, cron, everything."""
        print("🛠️  FRIDAY Engine v0.1.0 (Phase 0)")
        print(f"   Tools: {len(self.tools.list_tools())}")
        print(f"   Skills: {len(self.skills.list_skills())}")
        print(f"   Gateways: {len(self.router.gateways)}")
        
        await self.router.start_all()
        await self.cron.start()
        
        print("🚀 Engine running. Press Ctrl+C to stop.")
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()
    
    async def stop(self):
        """Graceful shutdown."""
        print("🛑 Stopping FRIDAY...")
        await self.router.stop_all()
        await self.cron.stop()
        print("✅ Stopped.")
