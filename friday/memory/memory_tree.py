"""Memory Tree — Hierarchical summaries in SQLite."""

import sqlite3
from datetime import datetime
from typing import List, Optional


class MemoryTree:
    """Stores and retrieves hierarchical summaries.
    
    Inspired by OpenHuman's Memory Tree but rebuilt in Python.
    """
    
    def __init__(self, db_path: str = "friday_memory.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                type TEXT NOT NULL,
                content TEXT NOT NULL,
                summary TEXT,
                tags TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                priority REAL DEFAULT 0.0
            )
        """)
        conn.commit()
        conn.close()
    
    def add_chunk(self, source: str, type_: str, content: str, 
                  summary: Optional[str] = None, tags: Optional[List[str]] = None,
                  expires_hours: Optional[int] = None) -> int:
        """Add a canonicalized chunk to memory."""
        now = datetime.utcnow().isoformat()
        expires = None
        if expires_hours:
            from datetime import timedelta
            expires = (datetime.utcnow() + timedelta(hours=expires_hours)).isoformat()
        
        tags_str = ",".join(tags) if tags else None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute(
            "INSERT INTO chunks (source, type, content, summary, tags, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (source, type_, content, summary, tags_str, now, expires)
        )
        chunk_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chunk_id
    
    def query(self, keywords: List[str], limit: int = 10) -> List[dict]:
        """Retrieve relevant chunks by keyword match."""
        if not keywords:
            return []
        
        patterns = [f"%{k}%" for k in keywords]
        placeholders = " OR ".join(["content LIKE ?" for _ in patterns])
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            f"SELECT * FROM chunks WHERE {placeholders} ORDER BY priority DESC, created_at DESC LIMIT ?",
            patterns + [limit]
        ).fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def expire_old(self) -> int:
        """Remove expired chunks. Returns count removed."""
        now = datetime.utcnow().isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("DELETE FROM chunks WHERE expires_at IS NOT NULL AND expires_at < ?", (now,))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count
