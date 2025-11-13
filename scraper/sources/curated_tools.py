import json
import os
import requests
from bs4 import BeautifulSoup

def load_curated_tools(json_path="curated_ai_tools.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

def scrape_latest_version(tool):
    url = tool.get("release_notes_url")
    if not url:
        return tool.get("last_known_version", "")
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        version = None
        # Heuristique : cherche un pattern de version dans le titre/texte
        for tag in soup.find_all(["h1", "h2", "strong", "b", "li", "p"]):
            txt = tag.get_text()
            if any(x in txt.lower() for x in ["release", "version", "update"]):
                digits = [s for s in txt.split() if any(c.isdigit() for c in s)]
                if digits:
                    version = digits[0]
                    break
        return version or tool.get("last_known_version", "")
    except Exception:
        return tool.get("last_known_version", "")

def get_curated_tools(config=None):
    curated = load_curated_tools()
    for tool in curated:
        if tool.get("tracking_versions"):
            latest = scrape_latest_version(tool)
            if latest and latest != tool["last_known_version"]:
                tool["last_known_version"] = latest
    return curated

# Usage : always include get_curated_tools() when building your global tools list