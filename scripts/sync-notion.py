#!/usr/bin/env python3
"""
Sync Notion database to JSON for website
Runs daily via GitHub Actions
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

print("🔄 Starting Notion sync...")
print(f"⏰ Timestamp: {datetime.now().isoformat()}")

# For now, we'll use the local JSON
# Later we'll add real Notion API integration
data_file = "data/ai_tracker_enhanced.json"

if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        data = json.load(f)
    print(f"✅ Loaded {len(data)} tools from {data_file}")
    
    # Add sync timestamp
    sync_metadata = {
        "lastSync": datetime.now().isoformat(),
        "toolCount": len(data),
        "categories": {}
    }
    
    for tool in data:
        cat = tool.get("category", "Unknown")
        sync_metadata["categories"][cat] = sync_metadata["categories"].get(cat, 0) + 1
    
    print(f"📊 Categories: {sync_metadata['categories']}")
    print(f"✨ Sync complete!")
else:
    print(f"❌ Data file not found: {data_file}")
    exit(1)
