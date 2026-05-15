# FRIDAY — Personal AI Assistant Framework

> **"Your Personal AI Infrastructure. Private. Extensible. Yours."**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## What is FRIDAY?

FRIDAY is an open-source, MIT-licensed personal AI assistant framework built in Python. It learns from your data, works with your tools, and talks on your channels — without vendor lock-in.

Inspired by the best ideas from [OpenHuman](https://github.com/tinyhumansai/openhuman), [Hermes Agent](https://github.com/NousResearch/hermes-agent), and [OpenClaw](https://github.com/openclaw/openclaw) — but rebuilt from scratch in clean-room fashion.

## Core Features

- 🔧 **Engineering Tools**: Terminal, file ops, code execution, web browsing, cron jobs
- 🧠 **Memory System**: Hierarchical summaries, session persistence, vector search
- 🔌 **Auto-Sync Connectors**: Gmail, Calendar, Slack, Notion, GitHub — auto-fetched every 20 minutes
- 📦 **Token Compression**: 70-80% token savings before hitting the LLM
- 📡 **Multi-Channel Gateway**: Telegram (primary), Discord, Web UI, WhatsApp
- 🎯 **Skills System**: Reusable `SKILL.md` playbooks
- 🤖 **Subagents**: Spawn parallel AI workers for complex tasks
- 🔒 **Local-First**: Your data stays on your machine

## Quick Start

```bash
# Install
pip install friday-ai

# Configure
friday --setup

# Run
friday --chat

# Or with gateway
friday --gateway telegram
```

## Architecture

```
friday-core/          Agent reasoning loop, tools, subagents, skills
friday-memory/        Hierarchical memory tree, embeddings, sessions
friday-sync/          Auto-fetch connectors (Gmail, Slack, Notion, etc.)
friday-compress/      TokenJuice-style compression engine
friday-voice/         Optional STT/TTS/wake word (optional)
friday-ui/            Optional FastAPI + React web interface
skills/              User-defined SKILL.md playbooks
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Asyncio |
| Web Framework | FastAPI |
| Database | SQLite (default), ChromaDB (vectors) |
| Task Queue | APScheduler |
| Connectors | httpx + pydantic + async OAuth2 |
| Gateway | python-telegram-bot, discord.py |
| UI (optional) | React + Vite + Tailwind |

## License

MIT © [Hemsagar](https://github.com/Hemsagar00)

> **Disclaimer:** FRIDAY is an independent project. The name is a cultural reference, not an affiliation with Marvel/Disney.

---

**Status:** Phase 0 (Foundation) — Active Development
