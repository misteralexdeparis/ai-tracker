#!/usr/bin/env python3
"""
AI Tools Tracker - Main Scraper Orchestrator
Bi-weekly automated scraping and update system
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sources.official_sites import scrape_official_sites
from sources.social_media import scrape_social_media
from sources.forums import scrape_forums
from enrichment.perplexity_analyzer import enrich_with_perplexity
from utils.helpers import (
    load_config,
    load_tools_json,
    save_tools_json,
    score_candidates,
    apply_manual_overrides,
    remove_legacy_versions,
    filter_by_max_tools
)


def main():
    """Main orchestration function"""
    
    print("🚀 AI Tools Tracker - Scraper Starting...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # 1. Load configuration
        print("\n📋 Loading configuration...")
        config = load_config()
        tools_data = load_tools_json()
        
        if not tools_data:
            tools_data = {"tools": [], "last_scrape": None, "next_scrape": None}
        
        # 2. Scrape official websites
        print("\n🔗 Scraping official websites...")
        official_updates = scrape_official_sites(config)
        print(f"   ✅ Found {len(official_updates)} updates from official sites")
        
        # 3. Scrape social media (Twitter, Discord)
        print("\n📱 Scraping social media...")
        social_updates = scrape_social_media(config)
        print(f"   ✅ Found {len(social_updates)} updates from social media")
        
        # 4. Scrape forums (Reddit, HN, ProductHunt)
        print("\n💬 Scraping forums...")
        forum_updates = scrape_forums(config)
        print(f"   ✅ Found {len(forum_updates)} updates from forums")
        
        # 5. Discover new candidate tools
        print("\n🔍 Discovering new candidate tools...")
        candidates = discover_candidates(forum_updates, config)
        print(f"   ✅ Found {len(candidates)} candidate tools")
        
        # 6. Score candidates and existing tools
        print("\n⭐ Scoring tools...")
        scored_tools = score_candidates(tools_data["tools"], candidates, config)
        
        # 7. Apply manual overrides
        print("\n✏️  Applying manual overrides...")
        scored_tools = apply_manual_overrides(scored_tools, config)
        
        # 8. Remove legacy versions
        print("\n🗑️  Removing legacy versions...")
        scored_tools = remove_legacy_versions(scored_tools)
        
        # 9. Filter to max tools
        print("\n📊 Filtering to max tools...")
        final_tools = filter_by_max_tools(scored_tools, config)
        print(f"   ✅ Final count: {len(final_tools)} tools (max: {config['thresholds']['max_tools']})")
        
        # 10. Enrich with Perplexity analysis (optional)
        print("\n🤖 Enriching with Perplexity analysis...")
        try:
            final_tools = enrich_with_perplexity(final_tools, official_updates)
            print("   ✅ Perplexity enrichment complete")
        except Exception as e:
            print(f"   ⚠️  Perplexity enrichment failed (non-blocking): {e}")
        
        # 11. Update tools JSON
        tools_data["tools"] = final_tools
        tools_data["last_scrape"] = datetime.now().isoformat()
        tools_data["next_scrape"] = (datetime.now() + timedelta(days=3.5)).isoformat()
        
        # 12. Save updated JSON
        print("\n💾 Saving updated tools data...")
        save_tools_json(tools_data)
        print("   ✅ Saved to public/ai_tracker_enhanced.json")
        
        # 13. Generate report
        print("\n📝 Generating scrape report...")
        generate_report(official_updates, social_updates, forum_updates, candidates, final_tools)
        
        print(f"\n✅ Scraper completed successfully!")
        print(f"⏰ Finished at: {datetime.now().isoformat()}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return 1


def discover_candidates(forum_updates, config):
    """Discover new candidate tools from forum updates"""
    candidates = []
    
    # Extract tool mentions from forum updates
    for update in forum_updates:
        if update.get("type") == "new_tool" and update.get("buzz_score", 0) > config["thresholds"]["min_buzz_score"]:
            candidates.append({
                "name": update.get("tool_name"),
                "category": update.get("category", "Uncategorized"),
                "source": update.get("source"),
                "buzz_score": update.get("buzz_score"),
                "description": update.get("description"),
                "url": update.get("url"),
                "status": "candidate"
            })
    
    return candidates


def generate_report(official_updates, social_updates, forum_updates, candidates, final_tools):
    """Generate and save scraping report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "official_updates": len(official_updates),
            "social_updates": len(social_updates),
            "forum_updates": len(forum_updates),
            "new_candidates": len(candidates),
            "total_tools": len(final_tools)
        },
        "top_candidates": sorted(candidates, key=lambda x: x.get("buzz_score", 0), reverse=True)[:5],
        "tools_snapshot": [
            {
                "name": t.get("name"),
                "category": t.get("category"),
                "buzz_score": t.get("buzz_score"),
                "status": t.get("status")
            }
            for t in final_tools
        ]
    }
    
    report_path = Path(__file__).parent / "scrape_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"   Report saved to: {report_path}")
    print(f"\n📊 Summary:")
    print(f"   - Official updates: {report['summary']['official_updates']}")
    print(f"   - Social media updates: {report['summary']['social_updates']}")
    print(f"   - Forum updates: {report['summary']['forum_updates']}")
    print(f"   - New candidates: {report['summary']['new_candidates']}")
    print(f"   - Total tools tracked: {report['summary']['total_tools']}")


if __name__ == "__main__":
    sys.exit(main())