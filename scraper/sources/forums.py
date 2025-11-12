#!/usr/bin/env python3
"""
Forums Scraper - RSS VERSION (Reddit + HackerNews)
ZERO COST - No API keys needed!
"""

import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_forums(config):
    """Scrape forums for AI tool mentions - RSS feeds"""
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
            
            for entry in feed.entries[:8]:  # Top 8 posts
                title = entry.get("title", "")
                link = entry.get("link", "")
                
                # Filter for AI/tool mentions
                if any(kw in title.lower() for kw in ["tool", "ai", "gpt", "claude", "model", "new", "release"]):
                    candidates.append({
                        "name": title[:80],
                        "source": f"reddit_{subreddit.replace('r/', '')}",
                        "url": link,
                        "buzz_score": 65,
                        "vision": 60,
                        "ability": 55,
                        "category": "Community Discussion"
                    })
                    logger.info(f"     ✅ {title[:60]}")
        except Exception as e:
            logger.warning(f"  Error scraping {subreddit}: {e}")
    
    # ===== HACKER NEWS RSS =====
    try:
        logger.info(f"\n  📰 Hacker News...")
        rss_url = "https://news.ycombinator.com/rss"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:  # Top 10 stories
            title = entry.get("title", "")
            link = entry.get("link", "")
            
            if any(kw in title.lower() for kw in ["ai", "llm", "tool", "framework", "model", "open source", "gpt"]):
                candidates.append({
                    "name": title[:80],
                    "source": "hacker_news",
                    "url": link,
                    "buzz_score": 70,
                    "vision": 65,
                    "ability": 60,
                    "category": "Community"
                })
                logger.info(f"     ✅ {title[:60]}")
    except Exception as e:
        logger.warning(f"  Error scraping Hacker News: {e}")
    
    logger.info(f"\n✅ Forums scraping complete: {len(candidates)} candidates found\n")
    return candidates