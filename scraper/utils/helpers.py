"""
Helper utilities for scraper - ENHANCED
Now with proper IMMUTABLE vs EVOLVING field handling
"""

import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ FIELD CATEGORIZATION ============

IMMUTABLE_FIELDS = {
    # Never overwrite - core identity
    "name",
    "category",
    "official_url",
    "vision",           # Gartner score
    "ability",          # Gartner score
    "buzz_score",       # Gartner score
    "quadrant",         # Gartner position
    "added_date",       # When first tracked
    "twitter_handle",   # Usually doesn't change
    "discord_server",   # Usually doesn't change
    "reddit"            # Usually doesn't change
}

EVOLVING_FIELDS = {
    # Always update from Perplexity if new data available
    "status",              # active → beta → discontinued
    "pricing",             # Can change (free → paid)
    "key_features",        # New features added constantly
    "strengths",           # Competitive advantages evolve
    "limitations",         # Limitations change
    "integrations",        # New integrations
    "changelog",           # New updates
    "pricing_tiers",       # Pricing details change
    "user_base",           # Grows over time
    "founding_year"        # Only if currently empty
}

FILL_IF_EMPTY = {
    # Fill if empty, but don't overwrite existing
    "description",
    "website_description"
}

# ============ HELPER FUNCTIONS ============

def load_config():
    """Load scraper configuration"""
    config_path = Path(__file__).parent.parent / "config.json"
    try:
        with open(config_path, "r") as f:
            config_data = json.load(f)
        return config_data["scraping_config"]
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"tools_to_track": [], "sources": {}, "thresholds": {}}

def load_tools_json():
    """Load current tools JSON"""
    tools_path = Path(__file__).parent.parent.parent / "public" / "ai_tracker_enhanced.json"
    if not tools_path.exists():
        return {"tools": []}
    
    try:
        with open(tools_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading tools JSON: {e}")
        return {"tools": []}

def save_tools_json(tools_data):
    """Save updated tools JSON"""
    tools_path = Path(__file__).parent.parent.parent / "public" / "ai_tracker_enhanced.json"
    tools_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(tools_path, "w") as f:
            json.dump(tools_data, f, indent=2)
        logger.info(f"✅ Saved {len(tools_data.get('tools', []))} tools to ai_tracker_enhanced.json")
    except Exception as e:
        logger.error(f"Error saving tools JSON: {e}")

def merge_intelligently(existing_tools, enriched_data):
    """
    INTELLIGENT MERGE with field categorization
    
    Strategy:
    ✅ IMMUTABLE fields: NEVER overwrite
    ♻️ EVOLVING fields: ALWAYS update from enriched data
    ❌ FILL_IF_EMPTY: Only fill if currently empty
    
    Returns: (merged_tools, change_log)
    """
    
    change_log = {
        "timestamp": datetime.now().isoformat(),
        "total_tools": len(existing_tools),
        "immutable_preserved": [],
        "evolving_updated": [],
        "empty_filled": [],
        "new_tools": [],
        "detailed_changes": {}
    }
    
    merged_tools = []
    
    # Create dict of enriched data by tool name
    enriched_dict = {}
    for tool in enriched_data:
        enriched_dict[tool.get("name", "")] = tool
    
    # ========== PROCESS EXISTING TOOLS ==========
    for existing_tool in existing_tools:
        tool_name = existing_tool.get("name")
        merged_tool = existing_tool.copy()
        tool_changes = {
            "immutable": [],
            "evolved": [],
            "filled": []
        }
        
        # Get enriched data if available
        enriched = enriched_dict.get(tool_name, {})
        
        # ✅ IMMUTABLE FIELDS - never change
        for field in IMMUTABLE_FIELDS:
            if field in merged_tool:
                # Keep existing value - verify it's not overwritten
                if enriched.get(field) and enriched.get(field) != merged_tool.get(field):
                    logger.warning(f"⚠️ Prevented overwrite of immutable {field} for {tool_name}")
                    tool_changes["immutable"].append(field)
        
        # ♻️ EVOLVING FIELDS - update if new data available
        for field in EVOLVING_FIELDS:
            if enriched.get(field):
                old_val = merged_tool.get(field)
                new_val = enriched.get(field)
                
                # Only update if different
                if old_val != new_val:
                    merged_tool[field] = new_val
                    tool_changes["evolved"].append({
                        "field": field,
                        "old": str(old_val)[:50],
                        "new": str(new_val)[:50]
                    })
                    logger.info(f"♻️ Updated {tool_name} - {field}")
        
        # ❌ FILL_IF_EMPTY - only if currently empty
        for field in FILL_IF_EMPTY:
            if not merged_tool.get(field) and enriched.get(field):
                merged_tool[field] = enriched.get(field)
                tool_changes["filled"].append({
                    "field": field,
                    "value": str(enriched.get(field))[:50]
                })
                logger.info(f"✨ Filled empty {field} for {tool_name}")
        
        # Add last_updated timestamp for evolving data
        if tool_changes["evolved"] or tool_changes["filled"]:
            merged_tool["last_updated"] = datetime.now().isoformat()
        
        # Log changes
        if tool_changes["immutable"]:
            change_log["immutable_preserved"].append({
                "tool": tool_name,
                "fields": tool_changes["immutable"]
            })
        
        if tool_changes["evolved"]:
            change_log["evolving_updated"].append({
                "tool": tool_name,
                "changes": tool_changes["evolved"]
            })
        
        if tool_changes["filled"]:
            change_log["empty_filled"].append({
                "tool": tool_name,
                "fields": tool_changes["filled"]
            })
        
        change_log["detailed_changes"][tool_name] = tool_changes
        
        merged_tools.append(merged_tool)
    
    # ========== ADD NEW TOOLS ==========
    existing_names = {tool.get("name") for tool in existing_tools}
    for tool in enriched_data:
        if tool.get("name") not in existing_names:
            tool["added_date"] = datetime.now().isoformat()
            tool["last_updated"] = datetime.now().isoformat()
            merged_tools.append(tool)
            change_log["new_tools"].append(tool.get("name"))
            logger.info(f"➕ Added new tool: {tool.get('name')}")
    
    # ========== LOG SUMMARY ==========
    logger.info(f"\n📊 INTELLIGENT MERGE SUMMARY:")
    logger.info(f"  - Total tools: {len(merged_tools)}")
    logger.info(f"  - Immutable fields preserved: {len(change_log['immutable_preserved'])}")
    logger.info(f"  - Evolving fields updated: {len(change_log['evolving_updated'])}")
    logger.info(f"  - Empty fields filled: {len(change_log['empty_filled'])}")
    logger.info(f"  - New tools: {len(change_log['new_tools'])}")
    
    return merged_tools, change_log

def score_candidates(candidates):
    """Score and rank candidate tools"""
    scored = []
    for candidate in candidates:
        score = 0
        
        if candidate.get("official_url"):
            score += 20
        if candidate.get("twitter_handle"):
            score += 15
        if candidate.get("category"):
            score += 15
        if candidate.get("description"):
            score += 25
        if candidate.get("key_features"):
            score += 25
        
        candidate["quality_score"] = score
        scored.append(candidate)
    
    return sorted(scored, key=lambda x: x["quality_score"], reverse=True)

def apply_manual_overrides(tools, overrides_config):
    """Apply manual override configurations"""
    for override in overrides_config.get("manual_overrides", []):
        tool_name = override.get("name")
        for tool in tools:
            if tool.get("name") == tool_name:
                # Only override if explicitly defined
                for key, value in override.items():
                    if key != "name":
                        tool[key] = value
                logger.info(f"🔧 Applied manual override for {tool_name}")
    
    return tools

def remove_legacy_versions(tools):
    """Remove legacy/old versions of tools"""
    tool_groups = {}
    for tool in tools:
        base_name = tool.get("name", "").split(" ")[0]
        if base_name not in tool_groups:
            tool_groups[base_name] = []
        tool_groups[base_name].append(tool)
    
    filtered_tools = []
    for group in tool_groups.values():
        sorted_group = sorted(group, key=lambda x: x.get("ability", 0), reverse=True)
        filtered_tools.extend(sorted_group[:2])
    
    logger.info(f"Filtered to {len(filtered_tools)} tools (removed legacy versions)")
    return filtered_tools

def filter_by_max_tools(tools, max_tools=150):
    """Filter tools to maximum count"""
    if len(tools) <= max_tools:
        return tools
    
    sorted_tools = sorted(
        tools,
        key=lambda x: (x.get("buzz_score", 0) + x.get("ability", 0)) / 2,
        reverse=True
    )
    
    filtered = sorted_tools[:max_tools]
    logger.info(f"Filtered to top {max_tools} tools by relevance")
    return filtered

def export_changelog(old_tools, new_tools):
    """
    Export what changed for newsletter
    """
    changelog = {
        "timestamp": datetime.now().isoformat(),
        "updated_tools": [],
        "new_tools": [],
        "status_changes": []
    }
    
    old_dict = {t.get("name"): t for t in old_tools}
    new_dict = {t.get("name"): t for t in new_tools}
    
    # Track updates
    for name, new_tool in new_dict.items():
        if name in old_dict:
            old_tool = old_dict[name]
            
            # Check for status change
            if old_tool.get("status") != new_tool.get("status"):
                changelog["status_changes"].append({
                    "tool": name,
                    "old_status": old_tool.get("status"),
                    "new_status": new_tool.get("status")
                })
            
            # Check for feature updates
            if old_tool.get("key_features") != new_tool.get("key_features"):
                changelog["updated_tools"].append({
                    "tool": name,
                    "features_updated": True
                })
        else:
            changelog["new_tools"].append(name)
    
    return changelog
