"""TokenJuice-style compression engine."""

import re
from typing import Optional


def compress_html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown, significantly reducing token count."""
    try:
        from markdownify import markdownify
        return markdownify(html).strip()
    except ImportError:
        # Fallback: strip tags
        return re.sub(r'<[^>]+>', '', html)


def shorten_urls(text: str) -> str:
    """Replace long URLs with short hashes."""
    import hashlib
    
    def replacer(match):
        url = match.group(0)
        short = hashlib.sha256(url.encode()).hexdigest()[:8]
        return f"[URL:{short}]"
    
    return re.sub(r'https?://\S+', replacer, text)


def deduplicate_chunks(chunks: list) -> list:
    """Remove near-duplicate chunks using simple fuzzy matching."""
    seen = set()
    unique = []
    for chunk in chunks:
        normalized = " ".join(chunk.lower().split()[:10])
        if normalized not in seen:
            seen.add(normalized)
            unique.append(chunk)
    return unique


def compress_payload(text: str, max_size: int = 3000) -> str:
    """Main compression pipeline. Applies all strategies."""
    # Step 1: HTML to markdown
    if '<' in text and '>' in text:
        text = compress_html_to_markdown(text)
    
    # Step 2: URL shortening
    text = shorten_urls(text)
    
    # Step 3: Truncate if still too long
    if len(text) > max_size:
        text = text[:max_size] + "\n\n[... compressed: truncated]"
    
    return text


def compress_text(text: str, max_len: int = 3000) -> str:
    """CLI-friendly wrapper for compress_payload."""
    return compress_payload(text, max_size=max_len)


def compress_url(url: str, max_len: int = 3000) -> str:
    """Fetch and compress a web page."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (FRIDAY)"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            return compress_payload(html, max_size=max_len)
    except Exception as e:
        return f"Error: {e}"
