# FRIDAY Architecture

## Overview

FRIDAY is a modular Python agent framework combining:

- **OpenHuman-inspired**: Auto-sync connectors, memory tree, token compression
- **Hermes Agent-inspired**: Engineering tools, subagents, cron, skills system
- **OpenClaw-inspired**: Multi-channel gateway, sandboxing, plugin architecture

## Design Principles

1. **Reference only, never copy** — Read docs, understand ideas, implement fresh
2. **MIT forever** — Permissive license for all code
3. **Python-first** — Fast to prototype, huge ecosystem
4. **Local-first, cloud-optional** — Data stays on your machine
5. **Modular by design** — Every subsystem is swappable
6. **CLI is king, UI is optional** — Terminal for power users, web UI as gravy
7. **Integration ≠ Lock-in** — Connect to services, but survive without them
8. **Memory is the product** — Agent quality = what it remembers about you

## Module Diagram

```
friday/
├── core/         — Agent engine, tool dispatch, subagents, skills, gateway, cron, sandbox
├── memory/       — Memory tree, obsidian bridge, embeddings, session store
├── sync/         — Connectors, sync daemon, canonicalizer, OAuth manager
├── compress/     — TokenJuice engine, summarization, deduplication
├── voice/        — STT, TTS, wake word (optional)
├── ui/           — FastAPI + React web interface (optional)
└── config/       — Settings and schema validation

skills/           — User-defined SKILL.md playbooks
tests/            — pytest suite
docs/             — Documentation
scripts/          — Install scripts
```

## Data Flow

```
User Message
    │
    v
Gateway (Telegram/Discord/Web)
    │
    v
Agent Engine
    ├── Memory Tree query (relevant context)
    ├── Tool dispatch (if needed)
    └── Subagent spawn (if parallel work needed)
    │
    v
Response → Gateway → User
```

## Security Model

- Credential storage: OS keychain (keyring) or encrypted env vars
- Memory: AES-256-GCM at rest
- Sandboxing: Docker for non-main sessions
- Network: TLS 1.3 for all outbound
- OAuth: PKCE flow, short-lived tokens
- Multi-user: Session isolation

## License

MIT
