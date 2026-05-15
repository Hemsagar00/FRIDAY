"""FRIDAY Tools — Built-in tool registry and execution engine.

Implements the tool-calling layer inspired by Hermes Agent's tool system.
Tools are auto-discoverable and can be called by the engine or CLI.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import urllib.request
import urllib.parse


class ToolRegistry:
    """Auto-discovers and executes tools."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict] = {}
        self._register_builtins()

    def _register_builtins(self):
        """Register all built-in tools."""
        self.register("terminal", self._tool_terminal, {
            "description": "Execute a shell command in git-bash",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run (POSIX syntax)"},
                    "timeout": {"type": "integer", "description": "Max seconds to wait", "default": 60},
                },
                "required": ["command"]
            }
        })
        self.register("read_file", self._tool_read_file, {
            "description": "Read contents of a text file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"},
                    "limit": {"type": "integer", "description": "Max lines to read", "default": 500},
                },
                "required": ["path"]
            }
        })
        self.register("write_file", self._tool_write_file, {
            "description": "Write text to a file (creates dirs, overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path"},
                    "content": {"type": "string", "description": "Text content"},
                },
                "required": ["path", "content"]
            }
        })
        self.register("web_search", self._tool_web_search, {
            "description": "Search the web (DuckDuckGo fallback) or fetch a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query or URL"},
                    "urls_only": {"type": "boolean", "description": "Return URLs only", "default": False},
                },
                "required": ["query"]
            }
        })
        self.register("list_dir", self._tool_list_dir, {
            "description": "List files in a directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path", "default": "."},
                },
                "required": []
            }
        })

    def register(self, name: str, fn: Callable, schema: Optional[Dict] = None):
        """Register a new tool."""
        self._tools[name] = fn
        self._schemas[name] = schema or {"description": "Undocumented tool"}

    def list_tools(self) -> List[str]:
        """Return list of available tool names."""
        return list(self._tools.keys())

    def get_schema(self, name: str) -> Optional[Dict]:
        return self._schemas.get(name)

    def call(self, name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        if name not in self._tools:
            raise KeyError(f"Unknown tool: {name}")
        return self._tools[name](**kwargs)

    # --- Built-in tool implementations ---

    def _tool_terminal(self, command: str, timeout: int = 60) -> Dict:
        """Run a shell command via subprocess."""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True,
                timeout=timeout
            )
            return {
                "output": result.stdout[:2000],
                "error": result.stderr[:2000] if result.stderr else None,
                "exit_code": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Command timed out", "exit_code": -1}
        except Exception as e:
            return {"output": "", "error": str(e), "exit_code": -1}

    def _tool_read_file(self, path: str, limit: int = 500) -> str:
        """Read a text file safely."""
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return f"Error: file not found: {path}"
            lines = p.read_text(encoding="utf-8").splitlines()[:limit]
            return "\n".join(lines)
        except Exception as e:
            return f"Error reading file: {e}"

    def _tool_write_file(self, path: str, content: str) -> str:
        """Write text to a file."""
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Wrote {len(content)} chars to {p}"
        except Exception as e:
            return f"Error writing file: {e}"

    def _tool_web_search(self, query: str, urls_only: bool = False) -> str:
        """Fetch a URL or perform a basic search."""
        # If it looks like a URL, fetch it
        if query.startswith("http://") or query.startswith("https://"):
            try:
                req = urllib.request.Request(
                    query,
                    headers={"User-Agent": "Mozilla/5.0 (FRIDAY)"}
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read().decode("utf-8", errors="ignore")
                    if urls_only:
                        # Extract URLs via regex
                        urls = re.findall(r'href=["\'](https?://[^"\']+)["\']', data)
                        return json.dumps(urls[:20], indent=2)
                    # Strip HTML tags for basic text extraction
                    text = re.sub(r'<[^>]+>', ' ', data)
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text[:3000]
            except Exception as e:
                return f"Error fetching URL: {e}"
        # Otherwise return a helpful message
        return (
            f"Search query: '{query}'. To search programmatically, "
            f"configure SERPER_API_KEY or BRAVE_API_KEY in D:\\Friday\\.env "
            f"and use web_search with a configured provider."
        )

    def _tool_list_dir(self, path: str = ".") -> str:
        """List directory contents."""
        try:
            p = Path(path).expanduser()
            if not p.is_dir():
                return f"Not a directory: {path}"
            items = []
            for item in sorted(p.iterdir()):
                marker = "📁" if item.is_dir() else "📄"
                items.append(f"{marker} {item.name}")
            return "\n".join(items) or "(empty)"
        except Exception as e:
            return f"Error listing directory: {e}"


# Global singleton
_registry = ToolRegistry()

def get_registry() -> ToolRegistry:
    return _registry
