#!/usr/bin/env python3
"""
Social Media Scraper - PRODUCT HUNT + GITHUB TRENDING
ZERO COST - RSS + Web Scrape
"""

import feedparser
import requests
import logging
from bs4 import BeautifulSoup
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def scrape_social_media(config):
    """Scrape Product Hunt + GitHub Trending"""
    candidates = []
    
    logger.info("🐦 Scraping social media & trending sources...\n")
    
    # ===== PRODUCT HUNT RSS =====
    try:
        logger.info("  🚀 Product Hunt RSS...")
        rss_url = "https://www.producthunt.com/feed.xml"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:12]:  # Top 12 products
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            
            # Filter for AI/tools
            text = (title + " " + summary).lower()
            if any(kw in text for kw in ["ai", "tool", "automation", "model", "assistant", "generator", "ml"]):
                candidates.append({
                    "name": title,
                    "description": summary[:200] if summary else "",
                    "source": "product_hunt",
                    "url": link,
                    "buzz_score": 75,
                    "vision": 70,
                    "ability": 65,
                    "category": "SaaS/Tools"
                })
                logger.info(f"     ✅ {title[:60]}")
    except Exception as e:
        logger.warning(f"  Error scraping Product Hunt: {e}")
    
    # ===== GITHUB TRENDING =====
    try:
        logger.info(f"\n  ⭐ GitHub Trending...")
        url = "https://github.com/trending?since=weekly&d=2"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="Box-row")
            
            for article in articles[:15]:  # Top 15 repos
                try:
                    h2 = article.find("h2")
                    if not h2:
                        continue
                    
                    link_elem = h2.find("a")
                    if not link_elem:
                        continue
                    
                    repo_name = link_elem.get_text(strip=True).replace("\n", "").strip()
                    repo_url = "https://github.com" + link_elem.get("href", "")
                    
                    desc_elem = article.find("p", class_="col-9")
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    lang_elem = article.find("span", attrs={"itemprop": "programmingLanguage"})
                    language = lang_elem.get_text(strip=True) if lang_elem else "Unknown"
                    
                    if any(lang in language.lower() for lang in ["python", "javascript", "rust", "go"]):
                        candidates.append({
                            "name": repo_name,
                            "description": description[:150] if description else "",
                            "source": "github_trending",
                            "url": repo_url,
                            "official_url": repo_url,
                            "buzz_score": 72,
                            "vision": 68,
                            "ability": 65,
                            "category": "Open Source"
                        })
                        logger.info(f"     ✅ {repo_name}")
                except Exception as e:
                    logger.debug(f"Error parsing GitHub repo: {e}")
        else:
            logger.warning(f"  GitHub trending returned {response.status_code}")
    except Exception as e:
        logger.warning(f"  Error scraping GitHub: {e}")
    
    logger.info(f"\n✅ Social media scraping complete: {len(candidates)} candidates found\n")
    return candidates