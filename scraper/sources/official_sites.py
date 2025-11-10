"""
Scraper for official websites and blogs
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_official_sites(config):
    """Scrape official websites for each tracked tool"""
    updates = []
    
    for tool in config["tools_to_track"]:
        tool_name = tool["name"]
        official_url = tool.get("official_url")
        
        if not official_url:
            continue
        
        try:
            logger.info(f"Scraping official site for {tool_name}...")
            
            # Scrape main website
            site_updates = scrape_website(official_url, tool_name)
            updates.extend(site_updates)
            
        except Exception as e:
            logger.warning(f"Error scraping official site for {tool_name}: {e}")
    
    return updates


def scrape_website(url, tool_name, timeout=10):
    """Scrape a website for updates"""
    updates = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Look for common changelog/news selectors
        update_selectors = [
            "div.changelog",
            "div.updates",
            "div.news",
            "article",
            "div.post"
        ]
        
        for selector in update_selectors:
            elements = soup.select(selector)
            for element in elements[:3]:
                text = element.get_text(strip=True)
                if len(text) > 50:
                    updates.append({
                        "tool_name": tool_name,
                        "source": "official_website",
                        "url": url,
                        "title": text[:100],
                        "description": text[:300],
                        "date": datetime.now().isoformat(),
                        "type": "update"
                    })
                    break
            if updates:
                break
    
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error fetching {url}: {e}")
    
    return updates