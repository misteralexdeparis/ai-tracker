# Add scraper modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enrichment.perplexity_analyzer import enrich_with_perplexity
from enrichment.version_handler import smart_merge_with_versions
from utils.cleanup_features import cleanup_tools_final
from utils.helpers import load_json, save_json, load_config
from sources.curated_tools import get_curated_tools
from sources.enhanced_filters import filter_candidates_enhanced

# Import scraper sources (from the sources/ directory)
from sources.official_sites import scrape_official_sites
from sources.forums import scrape_forums
from sources.social_media import scrape_social_media

print("\n🚀 AI Tools Tracker - Scraper Starting (v4.0 PHASE 1 - Enhanced)...")
print(f"⏰ Started at: {datetime.now().isoformat()}\n")

# ===== 1. LOAD CONFIGURATION =====
print("📋 Loading configuration...")
try:
    config = load_config()
    existing_tools = load_json('../public/ai_tracker_enhanced.json').get('tools', [])
    logger.info(f" ✅ Loaded {len(existing_tools)} existing tools")
    thresholds = config.get('scraping_config', {}).get('thresholds', {})
    buzz_threshold = thresholds.get('min_buzz_score', 40)
    vision_threshold = thresholds.get('min_vision', 40)
    ability_threshold = thresholds.get('min_ability', 40)
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
    
    # ===== SKIP AI NEWS: Articles are not tools =====
    # AI News was scraping TechCrunch/VentureBeat articles, but they're not products.
    # We focus on actual tools from official sites, forums, and social media instead.
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
    
    # ===== 4. APPLY ENHANCED FILTERING (CLAUDE PHASE 1) =====
    logger.info("🔍 APPLYING ENHANCED FILTERING (Claude recommendations)...")
    qualified_candidates = filter_candidates_enhanced(all_candidates, confidence_threshold=confidence_threshold)
    logger.info(f" ✅ After enhanced filter: {len(qualified_candidates)} qualified candidates\n")
    
    # Additional threshold filtering
    final_qualified = [
        c for c in qualified_candidates
        if c.get('buzz_score', 0) >= buzz_threshold
        and c.get('vision', 0) >= vision_threshold
        and c.get('ability', 0) >= ability_threshold
    ]
    
    logger.info(f" ✅ Qualified candidates (after dimension thresholds): {len(final_qualified)}\n")
    qualified_candidates = final_qualified
    
except Exception as e:
    logger.error(f"Error during web scraping: {e}")
    qualified_candidates = []

# ===== 5. ENRICH EXISTING TOOLS WITH PERPLEXITY =====
print("🧠 Enriching existing tools with Perplexity...\n")

print(" Strategy:")
print(" - ♻️ Update: status, pricing, features, limitations, changelog")
print(" - ✨ Fill: description, founding_year (if empty)")
print(" - 🔒 Preserve: Gartner scores, identity fields\n")

try:
    print(f" 📚 Enriching {len(existing_tools)} existing tools...")
    enriched_existing = enrich_with_perplexity(existing_tools)
    logger.info(f" ✅ Enrichment complete\n")
except Exception as e:
    logger.error(f"Error enriching tools: {e}")
    enriched_existing = existing_tools

# ===== 6. ANALYZE NEW CANDIDATES WITH PERPLEXITY =====
print("🔬 Analyzing new candidates...\n")

analyzed_candidates = []
if qualified_candidates:
    try:
        print(f" 🤖 Analyzing {len(qualified_candidates)} new candidates with Perplexity...")
        analyzed_candidates = enrich_with_perplexity(qualified_candidates)
        logger.info(f" ✅ Analysis complete\n")
    except Exception as e:
        logger.warning(f"Error analyzing candidates: {e}")
        analyzed_candidates = qualified_candidates
else:
    logger.info(" ⏭️  No candidate tools to analyze\n")

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
        logger.info(" ⏭️  Skipping for now\n")
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

# ===== 10. FILTER TO MAX TOOLS =====
print("📉 Filtering to max tools...\n")

merged_tools = merged_tools[:max_tools]
logger.info(f" ✅ Capped at {len(merged_tools)} tools\n")

# ===== 11. CONSOLIDATE FEATURES =====
print("🧹 Consolidating features...\n")

try:
    merged_tools = cleanup_tools_final(merged_tools, max_features=6)
    logger.info(f" ✅ Features consolidated\n")
except Exception as e:
    logger.warning(f"Error consolidating features: {e}")

# ===== 12. SAVE RESULTS =====
print("💾 Saving results...\n")

try:
    # Prepare metadata
    metadata = {
        'last_updated': datetime.now().isoformat(),
        'total_tools': len(merged_tools),
        'new_tools_count': len(version_log.get('new_tools', [])),
        'updated_tools_count': len(version_log.get('major_updates', [])) + len(version_log.get('minor_updates', [])),
        'version': '4.0 PHASE 1 - Enhanced Discovery & Filtering',
        'quality_thresholds': {
            'buzz_score': buzz_threshold,
            'vision': vision_threshold,
            'ability': ability_threshold,
            'confidence_level': confidence_threshold
        },
        'improvements': [
            '✅ Enhanced filtering (hard requirements + auto-reject + confidence)',
            '✅ Smart scoring v3 (5-dimensional)',
            '✅ Curated tools (39 AI leaders, always included)',
            '✅ Version tracking (GitHub releases + changelogs)',
        ]
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
    
except Exception as e:
    logger.error(f"Error saving results: {e}")

# ===== 13. PREPARE NEWSLETTER INFO =====
print("📧 Preparing newsletter info...\n")

try:
    newsletter_info = {
        'timestamp': datetime.now().isoformat(),
        'new_tools': version_log.get('new_tools', []),
        'major_updates': [u.get('tool') for u in version_log.get('major_updates', [])],
        'minor_updates': [u.get('tool') for u in version_log.get('minor_updates', [])],
        'total_tools': len(merged_tools),
        'phase': 'PHASE 1 Enhanced Discovery'
    }
    
    os.makedirs('../public', exist_ok=True)
    save_json(newsletter_info, '../public/newsletter_updates.json')
    logger.info(f" ✅ Newsletter info saved\n")
except Exception as e:
    logger.warning(f"Error preparing newsletter: {e}")

# ===== FINAL SUMMARY =====
print("=" * 70)
print("✅ SCRAPING WITH PHASE 1 IMPROVEMENTS COMPLETE!")
print("=" * 70)

print(f"\n📊 Final Statistics:")
print(f" - Total tools: {len(merged_tools)}")
print(f" - New tools discovered: {len(version_log.get('new_tools', []))}")
print(f" - Major updates (v bump): {len(version_log.get('major_updates', []))}")
print(f" - Minor updates: {len(version_log.get('minor_updates', []))}")

print(f"\n🎯 PHASE 1 Improvements:")
print(f" ✅ Enhanced filtering: {len(all_candidates)} candidates → {len(qualified_candidates)} qualified")
print(f" ✅ Confidence scoring: Only >= {confidence_threshold} included")
print(f" ✅ Curated tools: Always included (39 AI leaders)")
print(f" ✅ Version tracking: GitHub + Changelog integration")

# Cost estimation
enrichment_cost = (len(existing_tools) + len(analyzed_candidates)) * 0.0008

print(f"\n💰 Cost Estimate:")
print(f" - Enriched existing: ${len(existing_tools) * 0.0008:.4f}")
print(f" - Analyzed new: ${len(analyzed_candidates) * 0.0008:.4f}")
print(f" - Total this run: ${enrichment_cost:.4f}")

print(f"\n📁 Outputs:")
print(f" - Tools: public/ai_tracker_enhanced.json")
print(f" - Versions: logs/versions_*.json")
print(f" - Newsletter: public/newsletter_updates.json")

print(f"\n⏰ Completed at: {datetime.now().isoformat()}")
print("=" * 70)