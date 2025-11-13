#!/usr/bin/env python3
"""
Forums Scraper - RAW DATA VERSION (no scoring)
Reddit + HackerNews RSS - returns raw data, scoring done in main.py
"""

import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_forums(config):
    """Scrape forums for AI tool mentions - RSS feeds with RAW data only"""
    candidates = []
    
    logger.info("💬 Scraping forums (Reddit + HackerNews RSS)...\n")
    
    # ===== REDDIT RSS =====
    reddit_subreddits = [
        "r/MachineLearning",
        "r/LanguageModels",
        "r/ChatGPT",
        "r/StableDiffusion",
        "r/OpenAI",
    ]
    
    for subreddit in reddit_subreddits:
        try:
            rss_url = f"https://www.reddit.com/{subreddit}/.rss"
            logger.info(f"  📖 {subreddit}...")
            
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:8]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                
                # Filter for AI/tool mentions
                if any(kw in title.lower() for kw in ["tool", "ai", "gpt", "claude", "model", "new", "release", "framework"]):
                    source_id = subreddit.replace("r/", "reddit_")
                    
                    # ONLY RAW DATA - no scoring!
                    candidate = {
                        "name": title[:80],
                        "source": source_id,
                        "url": link,
                        "description": title,  # Use title as description
                        "category": "Community Discussion",
                        # NO buzz_score, vision, ability here!
                    }
                    
                    candidates.append(candidate)
                    logger.info(f"     ✅ {title[:50]}")
        except Exception as e:
            logger.warning(f"  Error scraping {subreddit}: {e}")
    
    # ===== HACKER NEWS RSS =====
    try:
        logger.info(f"\n  📰 Hacker News...")
        rss_url = "https://news.ycombinator.com/rss"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            
            if any(kw in title.lower() for kw in ["ai", "llm", "tool", "framework", "model", "open source", "gpt"]):
                candidate = {
                    "name": title[:80],
                    "source": "hacker_news",
                    "url": link,
                    "description": title,
                    "category": "Community",
                    # NO buzz_score, vision, ability here!
                }
                
                candidates.append(candidate)
                logger.info(f"     ✅ {title[:50]}")
    except Exception as e:
        logger.warning(f"  Error scraping Hacker News: {e}")
    
    logger.info(f"\n✅ Forums scraping complete: {len(candidates)} candidates found\n")
    return candidates