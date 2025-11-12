#!/usr/bin/env python3
"""
Official Sites Scraper - MEGA VERSION
Improved User-Agent + Retry Logic
"""

import requests
import logging
import time
from datetime import datetime
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SUPER USER-AGENT that works
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}

def fetch_with_retry(url, max_retries=3):
    """Fetch URL with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            logger.warning(f"Attempt {attempt+1} failed: {e}. Retry in {wait_time}s...")
            time.sleep(wait_time)
    return None

def scrape_official_sites(config):
    """Scrape official websites for tracked tools"""
    updates = []
    
    logger.info("📌 Checking official websites...")
    
    for tool in config.get("tools_to_track", [])[:5]:  # Limit to 5
        try:
            url = tool.get("official_url") or tool.get("url")
            if not url:
                continue
            
            logger.info(f"  🔗 Checking: {tool.get('name')}")
            
            response = fetch_with_retry(url)
            
            if response:
                logger.info(f"     ✅ Accessible")
                updates.append({
                    "name": tool.get("name"),
                    "status": "active",
                    "last_checked": datetime.now().isoformat(),
                    "source": "official_site_check"
                })
            else:
                logger.warning(f"     ⚠️ Unreachable")
                
        except Exception as e:
            logger.warning(f"     ❌ Error: {e}")
    
    logger.info(f"✅ Official sites check complete: {len(updates)} tools verified\n")
    return updates