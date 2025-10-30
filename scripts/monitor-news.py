#!/usr/bin/env python3
"""
Monitor AI tool news feeds for updates
Runs 3x per week via GitHub Actions
"""

import feedparser
import json
from datetime import datetime
from urllib.parse import urljoin

print("📡 Starting news monitoring...")

# RSS feeds to monitor
feeds = {
    "OpenAI": "https://openai.com/blog/rss/",
    "Anthropic": "https://www.anthropic.com/news/rss",
    "Google DeepMind": "https://deepmind.google/discover/blog/rss",
}

keywords = [
    "release", "launch", "available", "update", "new",
    "announce", "introduce", "beta", "capabilities"
]

print(f"🔍 Monitoring {len(feeds)} sources...\n")

updates_found = []

for source_name, feed_url in feeds.items():
    try:
        print(f"Checking {source_name}...")
        feed = feedparser.parse(feed_url)
        
        # Check first 5 entries
        for entry in feed.entries[:5]:
            title = entry.get("title", "").lower()
            summary = entry.get("summary", "").lower()
            
            # Check if keywords match
            if any(kw in title or kw in summary for kw in keywords):
                updates_found.append({
                    "source": source_name,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "date": entry.get("published", ""),
                })
                print(f"  ✅ Found: {entry.get('title', '')[:60]}...")
    
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:50]}")

print(f"\n📊 Total updates found: {len(updates_found)}")
if updates_found:
    print("⚠️  Review these and update Notion manually (for now)")
