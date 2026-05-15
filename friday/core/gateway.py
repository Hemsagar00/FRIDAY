"""FRIDAY Gateway — Multi-channel message routing.

Receives messages from Telegram, Discord, etc. and routes them
to the engine. Inspired by Hermes Agent's gateway system.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional


class BaseGateway(ABC):
    """Abstract base for all gateways."""

    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
        self._handlers: List[Callable] = []

    def on_message(self, handler: Callable):
        """Register a message handler."""
        self._handlers.append(handler)

    async def _notify(self, sender: str, text: str, meta: Dict = None):
        """Notify all handlers of an incoming message."""
        meta = meta or {}
        for handler in self._handlers:
            try:
                await handler(sender=sender, text=text, gateway=self.name, **meta)
            except Exception:
                pass

    @abstractmethod
    async def start(self):
        """Start the gateway (connect, listen)."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the gateway."""
        pass

    @abstractmethod
    async def send(self, recipient: str, text: str):
        """Send a message to a recipient."""
        pass


class GatewayRouter:
    """Manages multiple gateways and routes messages."""

    def __init__(self):
        self.gateways: Dict[str, BaseGateway] = {}
        self._handler: Optional[Callable] = None

    def add(self, gateway: BaseGateway):
        """Register a gateway."""
        self.gateways[gateway.name] = gateway
        gateway.on_message(self._route)

    def set_handler(self, handler: Callable):
        """Set the main message handler (engine)."""
        self._handler = handler

    async def _route(self, sender: str, text: str, gateway: str, **meta):
        """Route incoming message to the handler."""
        if self._handler:
            await self._handler(sender, text, gateway, **meta)

    async def start_all(self):
        await asyncio.gather(
            *(g.start() for g in self.gateways.values() if hasattr(g, 'start'))
        )

    async def stop_all(self):
        await asyncio.gather(
            *(g.stop() for g in self.gateways.values() if hasattr(g, 'stop'))
        )

    async def broadcast(self, text: str):
        """Send a message to ALL active gateways."""
        for gw in self.gateways.values():
            # Gateway-specific broadcast logic would go here
            pass


class TelegramGateway(BaseGateway):
    """Telegram bot gateway. Requires python-telegram-bot."""

    def __init__(self, token: str, config: Dict = None):
        super().__init__("telegram", config)
        self.token = token
        self._app = None

    async def start(self):
        try:
            from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

            self._app = ApplicationBuilder().token(self.token).build()

            async def handle_update(update, context):
                if update.message and update.message.text:
                    await self._notify(
                        sender=str(update.message.chat_id),
                        text=update.message.text,
                        meta={"chat_id": update.message.chat_id, "message_id": update.message.message_id}
                    )

            self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_update))
            await self._app.initialize()
            await self._app.start_polling()
        except ImportError:
            raise RuntimeError("python-telegram-bot not installed. Run: pip install python-telegram-bot")

    async def stop(self):
        if self._app:
            await self._app.stop()

    async def send(self, recipient: str, text: str):
        if self._app:
            await self._app.bot.send_message(chat_id=int(recipient), text=text)


# Singleton
_router = GatewayRouter()

def get_router() -> GatewayRouter:
    return _router
