#!/usr/bin/env python3

"""
AI Tools Tracker - Main Scraper Orchestrator - v3.1 FINAL

Smart versioning + Perplexity enrichment + Features cleanup
Newsletter updates integration
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# 👈 LOAD .ENV FIRST - WITH EXPLICIT PATH
from dotenv import load_dotenv

# Load .env from parent directory
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path)

# Then add path
sys.path.insert(0, str(Path(__file__).parent))

from enrichment.perplexity_analyzer import enrich_with_perplexity
from utils.helpers import (
    load_config,
    load_tools_json,
    save_tools_json,
    score_candidates,
    remove_legacy_versions,
    filter_by_max_tools,
)
from enrichment.version_handler import smart_merge_with_versions
from utils.cleanup_features import cleanup_tools_final

def main():
    """Main orchestration function with smart versioning & cleanup"""
    print("🚀 AI Tools Tracker - Scraper Starting (v3.1 with Features Cleanup)...")
    print(f"⏰ Started at: {datetime.now().isoformat()}")
    
    try:
        # 1. Load configuration & existing data
        print("\n📋 Loading configuration...")
        existing_tools_data = load_tools_json()
        existing_tools = existing_tools_data.get("tools", [])
        
        print(f"   ✅ Loaded {len(existing_tools)} existing tools")
        
        # BACKUP for changelog
        backup_tools = [t.copy() for t in existing_tools]
        
        # 2. NO SCRAPING FOR NOW - just enrichment
        print("\n🌐 Scraping from sources...")
        print("   ⏭️  Skipping web scraping for now - focusing on enrichment")
        candidates = []
        
        # 3. ENRICH EXISTING TOOLS WITH PERPLEXITY
        print("\n🧠 Enriching with Perplexity...")
        print("   Strategy:")
        print("   - ♻️ Update: status, pricing, features, limitations, changelog")
        print("   - ✨ Fill: description, founding_year (if empty)")
        print("   - 🔒 Preserve: Gartner scores, identity fields")
        
        api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if api_key:
            print(f"   📚 Enriching {len(existing_tools)} existing tools...")
            enriched_existing = enrich_with_perplexity(existing_tools, api_key)
        else:
            print("   ⚠️  PERPLEXITY_API_KEY not set - using existing data")
            enriched_existing = existing_tools
        
        # 4. INTELLIGENT MERGE WITH VERSION DETECTION
        print("\n🔄 Smart merge with version detection...")
        print("   Strategy:")
        print("   🔴 Major update (+15 pts or quadrant change) → v2, full update")
        print("   🟡 Minor update → selective updates (changelog, features)")
        print("   ✨ Changelog → keep last 4 entries")
        
        merged_tools, version_log = smart_merge_with_versions(
            enriched_existing,
            candidates
        )
        
        # Log major updates
        print(f"\n   📊 Version Summary:")
        print(f"      - Total tools: {len(existing_tools)} → {len(merged_tools)}")
        print(f"      - Major updates: {len(version_log['major_updates'])}")
        print(f"      - Minor updates: {len(version_log['minor_updates'])}")
        print(f"      - New tools: {len(version_log['new_tools'])}")
        
        if version_log['major_updates']:
            print(f"\n   🔴 MAJOR UPDATES DETECTED:")
            for item in version_log['major_updates']:
                tool_name = item['tool']
                changes = item['changes']['reasons']
                print(f"      - {tool_name}:")
                for reason in changes:
                    print(f"        • {reason}")
        
        # 5. Skip manual overrides
        print("\n🔧 Applying manual overrides...")
        print("   ⏭️  Skipping for now")
        
        # 6. Remove legacy versions
        print("\n🗑️  Removing legacy versions...")
        merged_tools = remove_legacy_versions(merged_tools)
        
        # 7. Filter to max tools
        print("\n📉 Filtering to max tools...")
        final_tools = filter_by_max_tools(merged_tools, 150)
        
        # 8. 🆕 CLEANUP FEATURES (merge + deduplicate + limit)
        print("\n🧹 Consolidating features...")
        final_tools = cleanup_tools_final(final_tools)
        
        # 9. Save results
        print("\n💾 Saving results...")
        output_data = {
            "tools": final_tools,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_tools": len(final_tools),
                "scrape_run": datetime.now().isoformat()
            }
        }
        
        save_tools_json(output_data)
        
        # 10. Save version log
        print("\n📋 Saving version log...")
        log_path = Path(__file__).parent.parent.parent / "logs" / f"versions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, "w") as f:
            json.dump(version_log, f, indent=2)
        
        print(f"   ✅ Saved to {log_path}")
        
        # 11. Generate newsletter info
        print("\n📧 Preparing newsletter info...")
        newsletter_data = {
            "timestamp": datetime.now().isoformat(),
            "major_updates": version_log['major_updates'],
            "new_tools": version_log['new_tools'],
            "minor_updates_count": len(version_log['minor_updates']),
            "changelog_updates": version_log['changelog_updates']
        }
        
        # Create public dir if doesn't exist
        newsletter_path = Path(__file__).parent.parent / "public" / "newsletter_updates.json"
        newsletter_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(newsletter_path, "w") as f:
            json.dump(newsletter_data, f, indent=2)
        
        print(f"   ✅ Newsletter info saved to {newsletter_path}")
        
        # FINAL SUMMARY
        print("\n" + "="*70)
        print("✅ SCRAPING WITH SMART VERSIONING COMPLETE!")
        print("="*70)
        print(f"📊 Final Statistics:")
        print(f"   - Total tools: {len(final_tools)}")
        print(f"   - Major updates (v bump): {len(version_log['major_updates'])}")
        print(f"   - Minor updates: {len(version_log['minor_updates'])}")
        print(f"   - New tools: {len(version_log['new_tools'])}")
        print(f"\n📁 Outputs:")
        print(f"   - Tools: public/ai_tracker_enhanced.json")
        print(f"   - Versions: logs/versions_*.json")
        print(f"   - Newsletter: public/newsletter_updates.json")
        print(f"\n⏰ Completed at: {datetime.now().isoformat()}")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
