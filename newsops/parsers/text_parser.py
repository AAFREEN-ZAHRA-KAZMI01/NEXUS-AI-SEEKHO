import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from config import MAX_TEXT_CHARS


def _validate_url(url: str) -> None:
    """Raise ValueError for non-HTTP schemes or private/loopback hostnames (SSRF guard)."""
    try:
        parsed = urlparse(url)
    except Exception:
        raise ValueError("Invalid URL format")

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http:// and https:// URLs are allowed")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValueError("URL must have a valid hostname")

    try:
        ip = socket.gethostbyname(host)
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            raise ValueError("Access to internal/private URLs is not allowed")
    except ValueError:
        raise
    except Exception:
        pass  # DNS failure or unresolvable — let httpx handle it


async def parse_text(content: str) -> dict:
    try:
        return {
            "clean_text": content.strip(),
            "word_count": len(content.split()),
            "source": "direct_text"
        }
    except Exception as e:
        return {"error": True, "reason": str(e), "clean_text": ""}

async def parse_url(url: str) -> dict:
    try:
        _validate_url(url)
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"User-Agent": "Mozilla/5.0"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        
        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
            tag.decompose()

        title = soup.title.string if soup.title else ""
        clean_text = soup.get_text(separator=" ", strip=True)

        return {
            "clean_text": clean_text[:MAX_TEXT_CHARS],
            "word_count": len(clean_text.split()),
            "source": url,
            "title": title,
            "source_type": "url"
        }
    except Exception as e:
        return {"error": True, "reason": str(e), "clean_text": ""}
