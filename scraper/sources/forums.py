"""
Scraper for forums (HackerNews, Reddit, ProductHunt)
"""

import requests
import feedparser
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_forums(config):
    """Scrape forums for AI tool discussions"""
    updates = []
    
    # Scrape Reddit RSS feeds
    reddit_updates = scrape_reddit(config)
    updates.extend(reddit_updates)
    
    return updates


def scrape_reddit(config):
    """Scrape Reddit for AI tool mentions via RSS"""
    updates = []
    
    subreddits = config["sources"].get("forums", [])
    reddit_subreddits = [s for s in subreddits if "reddit.com" in s]
    
    for subreddit_url in reddit_subreddits[:3]:  # Limit to 3
        try:
            subreddit_name = subreddit_url.split("/")[-1]
            logger.info(f"Scraping Reddit: {subreddit_name}...")
            
            rss_url = f"https://reddit.com/r/{subreddit_name}/.rss"
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:5]:
                updates.append({
                    "source": f"reddit_{subreddit_name}",
                    "title": entry.get("title", ""),
                    "description": entry.get("summary", "")[:200],
                    "url": entry.get("link", ""),
                    "date": datetime.now().isoformat(),
                    "type": "discussion",
                    "buzz_score": 55
                })
        
        except Exception as e:
            logger.warning(f"Error scraping Reddit {subreddit_name}: {e}")
    
    return updates