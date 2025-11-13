#!/usr/bin/env python3
"""
AI News Scraper - HIGH QUALITY SOURCES
TechCrunch AI + VentureBeat + Company Blogs (RSS)
Filters: "release", "announce", "launch", "v1.0"
Excludes: "paper", "survey", "arxiv", "WIP"
"""

import feedparser
import requests
import logging
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import smart scoring
sys.path.insert(0, str(Path(__file__).parent))
from smart_scoring_v3 import calculate_candidate_scores_v3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# Exclusion patterns (low-quality signals)
EXCLUDE_PATTERNS = [
    r"(?i)(paper|survey|thesis|dissertation|arxiv|preprint)",
    r"(?i)(seeking feedback|WIP|work in progress|experiment|alpha|beta)",
    r"(?i)(research|academic|course|tutorial|guide)",
]

# Inclusion patterns (high-quality signals)
INCLUDE_PATTERNS = [
    r"(?i)(release|announce|launch|new version|v\d+\.\d+|released|introducing)",
]

def should_exclude(title, description=""):
    """Check if content should be excluded"""
    text = (title + " " + description).lower()
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def should_include(title, description=""):
    """Check if content has quality signals"""
    text = (title + " " + description).lower()
    for pattern in INCLUDE_PATTERNS:
        if re.search(pattern, text):
            return True
    return False

def scrape_ai_news(config):
    """Scrape high-quality AI news sources - RSS feeds"""
    candidates = []
    
    logger.info("📰 Scraping high-quality AI news sources...\n")
    
    # ===== TECHCRUNCH AI SECTION =====
    try:
        logger.info("  📰 TechCrunch AI...")
        rss_url = "https://techcrunch.com/category/artificial-intelligence/feed/"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")
            
            # Skip if old (> 7 days)
            if published:
                try:
                    pub_date = datetime.strptime(published.split("T")[0], "%Y-%m-%d")
                    if datetime.now() - pub_date > timedelta(days=7):
                        continue
                except:
                    pass
            
            # Quality filtering
            if should_exclude(title, summary):
                continue
            
            if "ai" in title.lower() or "ml" in title.lower() or "tool" in title.lower():
                candidate = {
                    "name": title[:100],
                    "description": summary[:250] if summary else "",
                    "source": "techcrunch_ai",
                    "url": link,
                    "category": "News Announcement",
                    "published_date": published
                }
                
                # Smart scoring
                scores = calculate_candidate_scores_v3(candidate, "techcrunch_ai")
                candidate.update(scores)
                
                candidates.append(candidate)
                logger.info(f"     ✅ {title[:60]} (confidence={scores.get('confidence_level', 0)})")
    except Exception as e:
        logger.warning(f"  Error scraping TechCrunch: {e}")
    
    # ===== VENTUREBEAT AI =====
    try:
        logger.info(f"\n  📰 VentureBeat AI...")
        rss_url = "https://venturebeat.com/ai/feed/"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            published = entry.get("published", "")
            
            if should_exclude(title, summary):
                continue
            
            # Focus on announcements
            if any(kw in title.lower() for kw in ["announce", "launch", "release", "new", "update"]):
                candidate = {
                    "name": title[:100],
                    "description": summary[:250] if summary else "",
                    "source": "venturebeat_ai",
                    "url": link,
                    "category": "News Announcement",
                    "published_date": published
                }
                
                scores = calculate_candidate_scores_v3(candidate, "venturebeat_ai")
                candidate.update(scores)
                
                candidates.append(candidate)
                logger.info(f"     ✅ {title[:60]} (confidence={scores.get('confidence_level', 0)})")
    except Exception as e:
        logger.warning(f"  Error scraping VentureBeat: {e}")
    
    # ===== COMPANY ENGINEERING BLOGS =====
    company_blogs = [
        ("OpenAI", "https://openai.com/blog/feed.xml"),
        ("Anthropic", "https://www.anthropic.com/feed.xml"),
        ("Google AI", "https://ai.googleblog.com/feeds/posts/default"),
        ("Meta AI", "https://www.meta.com/blog/ai/feed/"),
    ]
    
    for company_name, blog_url in company_blogs:
        try:
            logger.info(f"  📰 {company_name} blog...")
            feed = feedparser.parse(blog_url)
            
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "")
                
                if should_exclude(title, summary):
                    continue
                
                # Company blogs = high confidence automatically
                candidate = {
                    "name": title[:100],
                    "description": summary[:250] if summary else "",
                    "source": f"{company_name.lower()}_blog",
                    "url": link,
                    "category": "Official Announcement",
                    "published_date": published,
                    "publisher": company_name
                }
                
                scores = calculate_candidate_scores_v3(candidate, f"{company_name.lower()}_blog")
                scores["confidence_level"] = 95  # Official sources = high confidence
                candidate.update(scores)
                
                candidates.append(candidate)
                logger.info(f"     ✅ {title[:60]} (confidence={scores.get('confidence_level', 0)})")
        except Exception as e:
            logger.debug(f"  Error scraping {company_name}: {e}")
    
    logger.info(f"\n✅ AI news scraping complete: {len(candidates)} high-quality candidates found\n")
    return candidates
