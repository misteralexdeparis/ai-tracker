#!/usr/bin/env python3
"""
Social Media Scraper - RAW DATA VERSION (no scoring)
Product Hunt + GitHub Trending - returns raw data, scoring done in main.py
"""

import feedparser
import requests
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def scrape_social_media(config):
    """Scrape Product Hunt + GitHub Trending with RAW data only"""
    candidates = []
    
    logger.info("🐦 Scraping social media & trending sources...\n")
    
    # ===== PRODUCT HUNT RSS =====
    try:
        logger.info("  🚀 Product Hunt RSS...")
        rss_url = "https://www.producthunt.com/feed.xml"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:12]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            
            text = (title + " " + summary).lower()
            if any(kw in text for kw in ["ai", "tool", "automation", "model", "assistant", "generator", "ml"]):
                candidate = {
                    "name": title,
                    "description": summary[:200] if summary else "",
                    "source": "product_hunt",
                    "url": link,
                    "category": "SaaS/Tools",
                    # NO scores here!
                }
                
                candidates.append(candidate)
                logger.info(f"     ✅ {title[:50]}")
    except Exception as e:
        logger.warning(f"  Error scraping Product Hunt: {e}")
    
    # ===== GITHUB TRENDING =====
    try:
        logger.info(f"\n  ⭐ GitHub Trending...")
        url = "https://github.com/trending?since=weekly"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="Box-row")
            
            for article in articles[:15]:
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
                    
                    # Try to extract stars
                    stars_elem = article.find("span", class_="d-inline-block float-sm-right")
                    github_stars = 0
                    if stars_elem:
                        stars_text = stars_elem.get_text(strip=True).replace(",", "")
                        try:
                            github_stars = int(stars_text)
                        except:
                            pass
                    
                    candidate = {
                        "name": repo_name,
                        "description": description[:150] if description else "",
                        "source": "github_trending",
                        "url": repo_url,
                        "github_url": repo_url,
                        "github_stars": github_stars,  # RAW data for scoring
                        "category": "Open Source",
                        # NO scores here!
                    }
                    
                    candidates.append(candidate)
                    logger.info(f"     ✅ {repo_name}")
                except Exception as e:
                    logger.debug(f"Error parsing GitHub repo: {e}")
        else:
            logger.warning(f"  GitHub trending returned {response.status_code}")
    except Exception as e:
        logger.warning(f"  Error scraping GitHub: {e}")
    
    logger.info(f"\n✅ Social media scraping complete: {len(candidates)} candidates found\n")
    return candidates