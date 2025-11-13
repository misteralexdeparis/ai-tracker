#!/usr/bin/env python3

"""
AI Tools Tracker - Main Scraper with Web Discovery
OPTIMIZED VERSION with 3 new modules + FIX for scoring
FIX: Calculate dimension scores BEFORE filtering (not after)
"""

import json
import logging
import sys
import os
import shutil
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

# Suppress noisy loggers
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

# Add scraper modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Original imports
from enrichment.perplexity_analyzer import enrich_with_perplexity
from enrichment.version_handler import smart_merge_with_versions
from utils.cleanup_features import cleanup_tools_final
from utils.helpers import load_json, save_json, load_config
from sources.curated_tools import get_curated_tools
from sources.enhanced_filters import filter_candidates_enhanced

# NEW MODULE IMPORTS
from enrichment.smart_enrichment import smart_enrich_tools, should_enrich_tool
from sources.version_tracker import track_all_tools
from utils.scoring_v4 import score_all_tools, calculate_buzz_score, calculate_vision_score, calculate_ability_score

# Import scraper sources
from sources.official_sites import scrape_official_sites
from sources.forums import scrape_forums
from sources.social_media import scrape_social_media

print("\n🚀 AI Tools Tracker - OPTIMIZED SCRAPER v4.1 (FIXED)...")
print(f"⏰ Started at: {datetime.now().isoformat()}")
print("📦 NEW: Version Tracker Pro + Smart Enrichment + Enhanced Scoring v4")
print("🔧 FIX: Scoring before filtering\n")

# ===== 0. CHECK FORCE REFRESH FLAG =====
FORCE_REFRESH = os.getenv("FORCE_REFRESH", "false").lower() == "true"

if FORCE_REFRESH:
    print("⚠️  FORCE_REFRESH ENABLED - Clearing cache and forcing full refresh...\n")
    cache_dir = "cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        logger.info("✅ Cache cleared")

# ===== 1. LOAD CONFIGURATION =====
print("📋 Loading configuration...")
try:
    config = load_config()
    existing_tools = load_json('../public/ai_tracker_enhanced.json').get('tools', [])
    logger.info(f" ✅ Loaded {len(existing_tools)} existing tools")
    thresholds = config.get('scraping_config', {}).get('thresholds', {})
    buzz_threshold = thresholds.get('min_buzz_score', 30)  # LOWERED from 40
    vision_threshold = thresholds.get('min_vision', 30)     # LOWERED from 40
    ability_threshold = thresholds.get('min_ability', 30)   # LOWERED from 40
    max_tools = thresholds.get('max_tools', 150)
    confidence_threshold = thresholds.get('confidence_threshold', 70)
    logger.info(f" 📊 Quality thresholds loaded:")
    logger.info(f" - Buzz score: ≥ {buzz_threshold}")
    logger.info(f" - Vision: ≥ {vision_threshold}")
    logger.info(f" - Ability: ≥ {ability_threshold}")
    logger.info(f" - Confidence: ≥ {confidence_threshold}")
    logger.info(f" - Max tools: {max_tools}\n")
except Exception as e:
    logger.error(f"Error loading config: {e}")
    sys.exit(1)

# ===== 2. WEB SCRAPING - DISCOVER NEW TOOLS =====
print("🌐 Scraping from sources...\n")

all_candidates = []

try:
    print(" 🔍 Discovering new tools from web sources...")
    
    # Scrape official sites
    logger.info(" 📌 Scraping official websites...")
    try:
        official_updates = scrape_official_sites(config)
        logger.info(f" Found {len(official_updates)} updates from official sites")
        all_candidates.extend(official_updates)
    except Exception as e:
        logger.warning(f"Error scraping official sites: {e}")
    
    # Scrape forums (keep but lower priority)
    logger.info(" 💬 Scraping forums (Reddit, HackerNews)...")
    try:
        forum_updates = scrape_forums(config)
        logger.info(f" Found {len(forum_updates)} updates from forums")
        all_candidates.extend(forum_updates)
    except Exception as e:
        logger.warning(f"Error scraping forums: {e}")
    
    # AI News disabled (articles ≠ tools)
    logger.info(" 📰 [DISABLED] AI News sources (articles ≠ tools, use official/social sources)")
    
    # Scrape social media
    logger.info(" 🐦 Scraping social media (ProductHunt, GitHub Trending)...")
    try:
        social_updates = scrape_social_media(config)
        logger.info(f" Found {len(social_updates)} updates from social media")
        all_candidates.extend(social_updates)
    except Exception as e:
        logger.warning(f"Error scraping social media: {e}")
    
    logger.info(f"\n 📊 Total candidates discovered: {len(all_candidates)}")
    
    # ===== 3. LOAD AND ADD CURATED TOOLS =====
    logger.info("\n📌 Loading curated essential AI tools...")
    try:
        curated_tools = get_curated_tools()
        logger.info(f" ✅ Loaded {len(curated_tools)} curated AI tools")
        all_candidates.extend(curated_tools)
        logger.info(f" Total candidates after adding curated list: {len(all_candidates)}\n")
    except Exception as e:
        logger.warning(f"Error loading curated tools: {e}\n")
    
    # ===== 3.5. CALCULATE BASE DIMENSION SCORES (NEW - BEFORE FILTERING) =====
    print("📊 Calculating base dimension scores for filtering...\n")
    
    for candidate in all_candidates:
        # Only calculate if not already present
        if 'buzz_score' not in candidate:
            candidate['buzz_score'] = calculate_buzz_score(candidate)
        if 'vision' not in candidate:
            candidate['vision'] = calculate_vision_score(candidate)
        if 'ability' not in candidate:
            candidate['ability'] = calculate_ability_score(candidate)
    
    logger.info(f" ✅ Base scores calculated for {len(all_candidates)} candidates\n")
    logger.info(f"\n🔍 DEBUG: Checking scores after calculation...")
    curated_in_candidates = [c for c in all_candidates if c.get("tracking_versions")]
    logger.info(f"   Curated tools in all_candidates: {len(curated_in_candidates)}")
    if curated_in_candidates:
    sample = curated_in_candidates[0]
    logger.info(f"   Sample curated tool: {sample.get('name')}")
    logger.info(f"   Has buzz_score? {sample.get('buzz_score', 'MISSING')}")
    logger.info(f"   Has vision? {sample.get('vision', 'MISSING')}")
    logger.info(f"   Has ability? {sample.get('ability', 'MISSING')}")
    logger.info("")
    
    # ===== 4. APPLY ENHANCED FILTERING =====
    logger.info("🔍 APPLYING ENHANCED FILTERING (Claude recommendations)...")
    qualified_candidates = filter_candidates_enhanced(all_candidates, confidence_threshold=confidence_threshold)
    logger.info(f" ✅ After enhanced filter: {len(qualified_candidates)} qualified candidates\n")
    
    # Additional threshold filtering (NOW with calculated scores!)
    final_qualified = [
        c for c in qualified_candidates
        if c.get('buzz_score', 0) >= buzz_threshold
        and c.get('vision', 0) >= vision_threshold
        and c.get('ability', 0) >= ability_threshold
    ]
    
    logger.info(f" ✅ Qualified candidates (after dimension thresholds): {len(final_qualified)}")
    if final_qualified:
        logger.info(f"    Sample scores: buzz={final_qualified[0].get('buzz_score', 0):.1f}, vision={final_qualified[0].get('vision', 0):.1f}, ability={final_qualified[0].get('ability', 0):.1f}\n")
    else:
        logger.warning(f"    ⚠️  No candidates passed thresholds. Consider lowering thresholds in config.\n")
    
    qualified_candidates = final_qualified
    
except Exception as e:
    logger.error(f"Error during web scraping: {e}")
    qualified_candidates = []

# ===== 5. MODULE 1: VERSION TRACKING (FREE) =====
print("=" * 70)
print("📦 MODULE 1: VERSION TRACKER PRO (Free version detection)")
print("=" * 70 + "\n")

version_tracking_results = {}
try:
    # Track versions for curated tools (avoid Perplexity cost)
    curated_for_tracking = [t for t in existing_tools if t.get("source") == "curated"]
    
    if curated_for_tracking:
        logger.info(f"🔍 Tracking versions for {len(curated_for_tracking)} curated tools...")
        version_tracking_results = track_all_tools(curated_for_tracking)
        
        # Update existing tools with new versions
        for update in version_tracking_results.get("updated_tools", []):
            tool_name = update["name"]
            new_version = update["new_version"]
            
            # Find tool in existing_tools and update
            for tool in existing_tools:
                if tool.get("name") == tool_name:
                    tool["last_known_version"] = new_version
                    tool["version_updated_at"] = datetime.now().isoformat()
                    
                    if update.get("is_major"):
                        logger.info(f"  🔴 MAJOR UPDATE: {tool_name} → {new_version}")
                    else:
                        logger.info(f"  🟡 Minor update: {tool_name} → {new_version}")
        
        logger.info(f"\n✅ Version tracking complete")
        logger.info(f"  - Updated: {len(version_tracking_results.get('updated_tools', []))}")
        logger.info(f"  - Needs Perplexity: {version_tracking_results['statistics']['needs_perplexity']}")
    else:
        logger.info("⏭️  No curated tools to track\n")
        
except Exception as e:
    logger.warning(f"Error in version tracking: {e}")

# ===== 6. MODULE 2: SMART ENRICHMENT (Cost Optimization) =====
print("\n" + "=" * 70)
print("💰 MODULE 2: SMART ENRICHMENT MANAGER (70-90% cost savings)")
print("=" * 70 + "\n")

print(" Strategy:")
print(" 1. Cache hits → $0 (already enriched)")
print(" 2. Free scrapers (GitHub API, homepage) → $0")
print(" 3. Perplexity (only if needed) → $0.0008/tool\n")

# Track costs
total_cost_saved = 0.0
total_cost_spent = 0.0

try:
    # Smart enrich existing tools
    logger.info("🧠 Smart enrichment for existing tools...")
    enriched_existing, stats_existing = smart_enrich_tools(
        tools=existing_tools,
        existing_tools=existing_tools,  # Use as cache reference
        perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")
    )
    
    total_cost_saved += stats_existing.get('cost_saved', 0)
    total_cost_spent += stats_existing.get('cost_spent', 0)
    
    # Smart enrich new candidates
    if qualified_candidates:
        logger.info("\n🧠 Smart enrichment for new candidates...")
        analyzed_candidates, stats_candidates = smart_enrich_tools(
            tools=qualified_candidates,
            existing_tools=enriched_existing,  # Use enriched as cache
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY")
        )
        
        total_cost_saved += stats_candidates.get('cost_saved', 0)
        total_cost_spent += stats_candidates.get('cost_spent', 0)
    else:
        logger.info("\n⏭️  No candidate tools to analyze")
        analyzed_candidates = []
    
    # Log combined costs
    total_potential_cost = (len(existing_tools) + len(qualified_candidates)) * 0.0008
    savings_percent = (total_cost_saved / total_potential_cost * 100) if total_potential_cost > 0 else 0
    
    logger.info(f"\n💰 SMART ENRICHMENT COST SUMMARY:")
    logger.info(f"   Potential cost (without optimization): ${total_potential_cost:.4f}")
    logger.info(f"   Actual cost spent: ${total_cost_spent:.4f}")
    logger.info(f"   Cost saved: ${total_cost_saved:.4f}")
    logger.info(f"   Savings: {savings_percent:.1f}%\n")
    
except Exception as e:
    logger.error(f"Error in smart enrichment: {e}")
    enriched_existing = existing_tools
    analyzed_candidates = qualified_candidates

# ===== 7. SMART MERGE WITH VERSION DETECTION =====
print("🔄 Smart merge with version detection...\n")

print(" Strategy:")
print(" 🔴 Major update (+15 pts or quadrant change) → v2, full update")
print(" 🟡 Minor update → selective updates (changelog, features)")
print(" ✨ Changelog → keep last 4 entries\n")

try:
    merged_tools, version_log = smart_merge_with_versions(
        enriched_existing,
        analyzed_candidates
    )
    
    logger.info(f"\n 📊 Version Summary:")
    logger.info(f" - Total tools: {len(enriched_existing)} → {len(merged_tools)}")
    logger.info(f" - Major updates: {len(version_log.get('major_updates', []))}")
    logger.info(f" - Minor updates: {len(version_log.get('minor_updates', []))}")
    logger.info(f" - New tools: {len(version_log.get('new_tools', []))}\n")
except Exception as e:
    logger.error(f"Error merging: {e}")
    merged_tools = enriched_existing
    version_log = {}

# ===== 8. APPLY MANUAL OVERRIDES =====
print("🔧 Applying manual overrides...\n")

try:
    overrides_file = 'manual_overrides.json'
    if os.path.exists(overrides_file):
        overrides = load_json(overrides_file)
        for override in overrides:
            tool_idx = next(
                (i for i, t in enumerate(merged_tools) if t['name'] == override['name']),
                None
            )
            if tool_idx is not None:
                merged_tools[tool_idx].update(override)
                logger.info(f" ✅ Applied override for {override['name']}")
    else:
        logger.info(" ⏭️  No manual overrides found\n")
except Exception as e:
    logger.warning(f"Error applying overrides: {e}")

# ===== 9. REMOVE LEGACY VERSIONS =====
print("🗑️  Removing legacy versions...\n")

try:
    # Keep only latest version of each tool
    tool_names_seen = {}
    final_tools = []
    for tool in reversed(merged_tools):
        name = tool['name']
        if name not in tool_names_seen:
            tool_names_seen[name] = True
            final_tools.append(tool)
    final_tools.reverse()
    merged_tools = final_tools
    logger.info(f" ✅ Deduplicated to {len(merged_tools)} tools\n")
except Exception as e:
    logger.warning(f"Error removing legacy versions: {e}")

# ===== 10. MODULE 3: ENHANCED SCORING V4 (FINAL SCORES) =====
print("=" * 70)
print("🎯 MODULE 3: ENHANCED SCORING V4 (Final confidence-weighted scoring)")
print("=" * 70 + "\n")

print(" Dimensions:")
print(" - Buzz (25%): Trending momentum")
print(" - Vision (20%): Product clarity")
print(" - Ability (20%): Technical maturity")
print(" - Credibility (20%): Team/company trust")
print(" - Adoption (15%): Organic usage")
print("\n Multipliers:")
print(" - Confidence: High (1.0x), Medium (0.9x), Low (0.7x)")
print(" - Source: Curated (1.2x), News (1.1x), Reddit (0.8x)")
print(" - Maturity: Production (+10), Beta (-5), Alpha (-10)\n")

try:
    # Score all tools (recalculate with enriched data + apply multipliers)
    merged_tools = score_all_tools(merged_tools)
    
    logger.info(f"\n✅ All tools scored and ranked")
    
    # Log scoring stats
    avg_score = sum(t.get("final_score", 0) for t in merged_tools) / len(merged_tools) if merged_tools else 0
    logger.info(f" 📈 Average score: {avg_score:.1f}")
    
    # Count penalties/bonuses
    tools_with_penalties = sum(1 for t in merged_tools if t.get("scoring_metadata", {}).get("penalties"))
    tools_with_bonuses = sum(1 for t in merged_tools if t.get("scoring_metadata", {}).get("bonuses"))
    
    logger.info(f" ⚠️  Tools with penalties: {tools_with_penalties}")
    logger.info(f" ✨ Tools with bonuses: {tools_with_bonuses}\n")
    
except Exception as e:
    logger.error(f"Error in enhanced scoring: {e}")

# ===== 11. FILTER TO MAX TOOLS =====
print("📉 Filtering to max tools...\n")

merged_tools = merged_tools[:max_tools]
logger.info(f" ✅ Capped at {len(merged_tools)} tools (sorted by final_score)\n")

# ===== 12. CONSOLIDATE FEATURES =====
print("🧹 Consolidating features...\n")

try:
    merged_tools = cleanup_tools_final(merged_tools, max_features=6)
    logger.info(f" ✅ Features consolidated\n")
except Exception as e:
    logger.warning(f"Error consolidating features: {e}")

# ===== 13. SAVE RESULTS =====
print("💾 Saving results...\n")

try:
    # Prepare metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'total_tools': len(merged_tools),
        'new_tools_count': len(version_log.get('new_tools', [])),
        'updated_tools_count': len(version_log.get('major_updates', [])) + len(version_log.get('minor_updates', [])),
        'version': '4.1 OPTIMIZED (FIXED) - Scoring before filtering',
        'quality_thresholds': {
            'buzz_score': buzz_threshold,
            'vision': vision_threshold,
            'ability': ability_threshold,
            'confidence_level': confidence_threshold
        },
        'new_modules': [
            '✅ MODULE 1: Version Tracker Pro (free version detection)',
            '✅ MODULE 2: Smart Enrichment Manager (70-90% cost savings)',
            '✅ MODULE 3: Enhanced Scoring v4 (confidence-weighted ranking)',
        ],
        'improvements': [
            '✅ Enhanced filtering (hard requirements + auto-reject + confidence)',
            '✅ Smart scoring v4 (5-dimensional with multipliers)',
            '✅ Curated tools (39 AI leaders, always included)',
            '✅ Intelligent cost optimization',
            '🔧 FIX: Dimension scores calculated before filtering',
        ],
        'cost_optimization': {
            'potential_cost': f"${(len(existing_tools) + len(qualified_candidates)) * 0.0008:.4f}",
            'actual_cost': f"${total_cost_spent:.4f}",
            'savings': f"${total_cost_saved:.4f}",
            'savings_percent': f"{(total_cost_saved / ((len(existing_tools) + len(qualified_candidates)) * 0.0008) * 100) if (len(existing_tools) + len(qualified_candidates)) > 0 else 0:.1f}%"
        }
    }
    
    # Save main data
    output_data = {
        'metadata': metadata,
        'tools': merged_tools
    }
    
    # Create output directory if needed
    os.makedirs('../public', exist_ok=True)
    save_json(output_data, '../public/ai_tracker_enhanced.json')
    logger.info(f" ✅ Saved {len(merged_tools)} tools to ai_tracker_enhanced.json")
    
    # Save version log
    os.makedirs('../logs', exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_json(version_log, f'../logs/versions_{timestamp}.json')
    logger.info(f" ✅ Saved version log")
    
    # Save version tracking results
    if version_tracking_results:
        save_json(version_tracking_results, f'../logs/version_tracking_{timestamp}.json')
        logger.info(f" ✅ Saved version tracking results")
    
except Exception as e:
    logger.error(f"Error saving results: {e}")

# ===== 14. PREPARE NEWSLETTER INFO =====
print("\n📧 Preparing newsletter info...\n")

try:
    newsletter_info = {
        'timestamp': datetime.now().isoformat(),
        'new_tools': version_log.get('new_tools', []),
        'major_updates': [u.get('tool') for u in version_log.get('major_updates', [])],
        'minor_updates': [u.get('tool') for u in version_log.get('minor_updates', [])],
        'version_updates': version_tracking_results.get('updated_tools', []),
        'total_tools': len(merged_tools),
        'phase': 'OPTIMIZED v4.1 (FIXED) - Scoring before filtering',
        'top_10_tools': [
            {
                'name': t.get('name'),
                'final_score': t.get('final_score'),
                'category': t.get('category')
            }
            for t in merged_tools[:10]
        ]
    }
    
    os.makedirs('../public', exist_ok=True)
    save_json(newsletter_info, '../public/newsletter_updates.json')
    logger.info(f" ✅ Newsletter info saved\n")
except Exception as e:
    logger.warning(f"Error preparing newsletter: {e}")

# ===== FINAL SUMMARY =====
print("\n" + "=" * 70)
print("✅ OPTIMIZED SCRAPER COMPLETE - v4.1 (FIXED)!")
print("=" * 70)

print(f"\n📊 Final Statistics:")
print(f" - Total tools: {len(merged_tools)}")
print(f" - New tools discovered: {len(version_log.get('new_tools', []))}")
print(f" - Major updates (v bump): {len(version_log.get('major_updates', []))}")
print(f" - Minor updates: {len(version_log.get('minor_updates', []))}")
print(f" - Version tracked: {len(version_tracking_results.get('updated_tools', []))}")

print(f"\n🎯 OPTIMIZATION RESULTS:")
print(f" ✅ Enhanced filtering: {len(all_candidates)} candidates → {len(qualified_candidates)} qualified")
print(f" ✅ Confidence scoring: Only ≥ {confidence_threshold} included")
print(f" ✅ Version tracking: {version_tracking_results.get('statistics', {}).get('found_via_github', 0)} via GitHub (free)")
print(f" ✅ Smart enrichment: {savings_percent:.1f}% cost savings" if total_cost_saved > 0 else "")

print(f"\n💰 Cost Analysis:")
print(f" - Potential cost (no optimization): ${(len(existing_tools) + len(qualified_candidates)) * 0.0008:.4f}")
print(f" - Actual cost spent: ${total_cost_spent:.4f}")
print(f" - Cost saved: ${total_cost_saved:.4f}")
print(f" - Savings: {(total_cost_saved / ((len(existing_tools) + len(qualified_candidates)) * 0.0008) * 100) if (len(existing_tools) + len(qualified_candidates)) > 0 else 0:.1f}%")

print(f"\n📈 Scoring Breakdown:")
if merged_tools:
    top_score = merged_tools[0].get('final_score', 0)
    bottom_score = merged_tools[-1].get('final_score', 0)
    print(f" - Top score: {top_score:.1f} ({merged_tools[0].get('name')})")
    print(f" - Bottom score: {bottom_score:.1f} ({merged_tools[-1].get('name')})")
    print(f" - Average: {avg_score:.1f}")

print(f"\n📁 Outputs:")
print(f" - Tools: public/ai_tracker_enhanced.json")
print(f" - Versions: logs/versions_*.json")
print(f" - Version tracking: logs/version_tracking_*.json")
print(f" - Newsletter: public/newsletter_updates.json")
print(f" - Cache: cache/enrichment_cache.json")

print(f"\n⏰ Completed at: {datetime.now().isoformat()}")
print("=" * 70)

# ===== QUICK TIPS =====
print("\n💡 QUICK TIPS:")
print("  - Force refresh cache: FORCE_REFRESH=true python scraper/main.py")
print("  - Check top 10 tools: cat public/ai_tracker_enhanced.json | jq '.tools[:10]'")
print("  - Monitor costs: Check logs for 'Cost Analysis' section")
print("=" * 70 + "\n")