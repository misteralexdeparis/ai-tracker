"""
Version and Update Detection Handler
Detects major updates vs minor updates, manages versions
"""

import logging
from datetime import datetime
from typing import Dict, List, Tuple
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for change detection
MAJOR_UPDATE_THRESHOLDS = {
    "vision_change": 15,          # +15 points = major update
    "ability_change": 15,         # +15 points = major update
    "quadrant_change": True,      # Any quadrant change = major
    "category_change": True,      # Any category change = major
    "status_to_active": True      # beta/discontinued → active = major
}

def detect_major_update(old_tool: Dict, new_tool: Dict) -> Tuple[bool, Dict]:
    """
    Detect if a tool has had a major update
    
    Returns: (is_major_update, change_details)
    """
    
    change_details = {
        "is_major": False,
        "reasons": [],
        "metric_changes": {}
    }
    
    if not old_tool or not new_tool:
        return False, change_details
    
    # Check Gartner scores
    old_vision = old_tool.get("vision", 0)
    new_vision = new_tool.get("vision", 0)
    vision_diff = abs(new_vision - old_vision)
    
    if vision_diff >= MAJOR_UPDATE_THRESHOLDS["vision_change"]:
        change_details["is_major"] = True
        change_details["reasons"].append(f"Vision changed significantly: {old_vision}→{new_vision} (+{vision_diff})")
        change_details["metric_changes"]["vision"] = {
            "old": old_vision,
            "new": new_vision,
            "diff": vision_diff
        }
    
    # Check ability
    old_ability = old_tool.get("ability", 0)
    new_ability = new_tool.get("ability", 0)
    ability_diff = abs(new_ability - old_ability)
    
    if ability_diff >= MAJOR_UPDATE_THRESHOLDS["ability_change"]:
        change_details["is_major"] = True
        change_details["reasons"].append(f"Ability changed significantly: {old_ability}→{new_ability} (+{ability_diff})")
        change_details["metric_changes"]["ability"] = {
            "old": old_ability,
            "new": new_ability,
            "diff": ability_diff
        }
    
    # Check quadrant
    old_quadrant = old_tool.get("quadrant")
    new_quadrant = new_tool.get("quadrant")
    
    if old_quadrant != new_quadrant:
        change_details["is_major"] = True
        change_details["reasons"].append(f"Quadrant changed: {old_quadrant}→{new_quadrant}")
        change_details["metric_changes"]["quadrant"] = {
            "old": old_quadrant,
            "new": new_quadrant
        }
    
    # Check category
    old_category = old_tool.get("category")
    new_category = new_tool.get("category")
    
    if old_category != new_category:
        change_details["is_major"] = True
        change_details["reasons"].append(f"Category changed: {old_category}→{new_category}")
        change_details["metric_changes"]["category"] = {
            "old": old_category,
            "new": new_category
        }
    
    # Check status: discontinued/beta → active
    old_status = old_tool.get("status", "unknown").lower()
    new_status = new_tool.get("status", "unknown").lower()
    
    if old_status in ["beta", "discontinued", "inactive"] and new_status == "active":
        change_details["is_major"] = True
        change_details["reasons"].append(f"Status changed to active: {old_status}→{new_status}")
        change_details["metric_changes"]["status"] = {
            "old": old_status,
            "new": new_status
        }
    
    return change_details["is_major"], change_details

def handle_major_update(tool: Dict, version_info: Dict) -> Dict:
    """
    Handle a major update:
    - Create version 2 if first major update
    - Mark old as legacy
    - Reset or preserve version history
    
    Returns: updated tool with version info
    """
    
    current_version = tool.get("version", "1.0")
    
    # Parse version
    try:
        major_ver = int(current_version.split(".")[0])
    except:
        major_ver = 1
    
    new_version = f"{major_ver + 1}.0"
    
    tool["version"] = new_version
    tool["version_history"] = tool.get("version_history", [])
    
    # Add current state to history before update
    tool["version_history"].append({
        "version": current_version,
        "snapshot_date": tool.get("last_updated", datetime.now().isoformat()),
        "vision": tool.get("vision"),
        "ability": tool.get("ability"),
        "quadrant": tool.get("quadrant")
    })
    
    # Mark when this version started
    tool["version_updated_at"] = datetime.now().isoformat()
    tool["major_update_reason"] = version_info.get("reasons", [])
    
    logger.info(f"🚀 MAJOR UPDATE: {tool.get('name')} → v{new_version}")
    logger.info(f"   Reasons: {', '.join(version_info.get('reasons', []))}")
    
    return tool

def manage_changelog(old_changelog: List, new_updates: List, max_entries: int = 4) -> List:
    """
    Merge changelog intelligently:
    - Add new updates
    - Keep only last N entries
    - Remove duplicates
    
    Returns: updated changelog (max_entries length)
    """
    
    if not old_changelog:
        old_changelog = []
    
    # Combine and deduplicate
    combined = []
    seen_updates = set()
    
    # Add new updates first (most recent)
    for update in new_updates:
        update_key = update.get("title", "") + update.get("description", "")
        if update_key not in seen_updates:
            combined.append(update)
            seen_updates.add(update_key)
    
    # Then old updates
    for update in old_changelog:
        update_key = update.get("title", "") + update.get("description", "")
        if update_key not in seen_updates:
            combined.append(update)
            seen_updates.add(update_key)
    
    # Keep only last N
    final_changelog = combined[:max_entries]
    
    logger.info(f"📝 Changelog: {len(old_changelog)} entries → {len(final_changelog)} entries")
    
    return final_changelog

def compare_features(old_features: List, new_features: List) -> Dict:
    """
    Compare feature lists
    Returns: {added: [], removed: [], unchanged: []}
    """
    
    old_set = set(old_features or [])
    new_set = set(new_features or [])
    
    return {
        "added": list(new_set - old_set),
        "removed": list(old_set - new_set),
        "unchanged": list(old_set & new_set)
    }

def update_strengths_limitations(old_tool: Dict, new_tool: Dict, 
                                change_details: Dict) -> Tuple[bool, Dict]:
    """
    Decide if strengths/limitations should be updated
    
    Only update if:
    1. Major update detected
    2. Perplexity detected significant feature changes
    3. Strengths/limitations are currently empty
    
    Returns: (should_update, recommendations)
    """
    
    recommendations = {
        "should_update": False,
        "reasons": [],
        "suggested_strengths": new_tool.get("strengths"),
        "suggested_limitations": new_tool.get("limitations")
    }
    
    # If major update detected → update
    if change_details.get("is_major"):
        recommendations["should_update"] = True
        recommendations["reasons"].append("Major update detected")
        return True, recommendations
    
    # If strengths/limitations empty → update
    if not old_tool.get("strengths") or not old_tool.get("limitations"):
        recommendations["should_update"] = True
        recommendations["reasons"].append("Fields currently empty")
        return True, recommendations
    
    # If features changed significantly → might need update
    old_features = set(old_tool.get("key_features", []))
    new_features = set(new_tool.get("key_features", []))
    
    if old_features and new_features:
        similarity = len(old_features & new_features) / len(old_features | new_features)
        
        if similarity < 0.5:  # Less than 50% overlap
            recommendations["should_update"] = True
            recommendations["reasons"].append(f"Features changed significantly ({similarity*100:.0f}% overlap)")
            return True, recommendations
    
    return False, recommendations

def smart_merge_with_versions(existing_tools: List, enriched_data: List) -> Tuple[List, Dict]:
    """
    Smart merge with version detection
    
    Returns: (merged_tools, version_log)
    """
    
    version_log = {
        "timestamp": datetime.now().isoformat(),
        "major_updates": [],
        "minor_updates": [],
        "legacy_tools": [],
        "new_tools": [],
        "changelog_updates": []
    }
    
    merged_tools = []
    enriched_dict = {t.get("name"): t for t in enriched_data}
    
    for old_tool in existing_tools:
        tool_name = old_tool.get("name")
        merged_tool = old_tool.copy()

        # IMPORTANT: Remove old scores so they get recalculated fresh
        # This prevents stale scores from old versions of the scoring algorithm
        for score_field in ["buzz_score", "vision", "ability", "credibility", "adoption",
                           "final_score", "base_score", "scoring_breakdown", "scoring_metadata"]:
            merged_tool.pop(score_field, None)

        new_tool = enriched_dict.get(tool_name, {})
        
        if new_tool:
            # 1. Detect major updates
            is_major, change_details = detect_major_update(old_tool, new_tool)
            
            if is_major:
                logger.info(f"🔴 MAJOR UPDATE DETECTED: {tool_name}")
                merged_tool = handle_major_update(merged_tool, change_details)
                version_log["major_updates"].append({
                    "tool": tool_name,
                    "changes": change_details
                })
                
                # Update all fields for major update
                for key, value in new_tool.items():
                    if key not in ["name", "added_date", "version_history"]:
                        merged_tool[key] = value
            
            else:
                # 2. Minor update: selective field updates
                logger.info(f"🟡 MINOR UPDATE: {tool_name}")
                version_log["minor_updates"].append({"tool": tool_name})
                
                # Update changelog (keep last 4)
                if new_tool.get("changelog"):
                    merged_tool["changelog"] = manage_changelog(
                        old_tool.get("changelog", []),
                        new_tool.get("changelog", []),
                        max_entries=4
                    )
                
                # Update features only if significantly changed
                if new_tool.get("key_features"):
                    feature_diff = compare_features(
                        old_tool.get("key_features", []),
                        new_tool.get("key_features", [])
                    )
                    
                    if feature_diff["added"] or feature_diff["removed"]:
                        merged_tool["key_features"] = new_tool["key_features"]
                
                # Carefully update strengths/limitations
                should_update, recs = update_strengths_limitations(
                    old_tool, new_tool, {"is_major": False}
                )
                
                if should_update:
                    merged_tool["strengths"] = new_tool.get("strengths")
                    merged_tool["limitations"] = new_tool.get("limitations")
                    version_log["changelog_updates"].append({
                        "tool": tool_name,
                        "reason": recs["reasons"]
                    })
                
                # Update pricing/status (can change frequently)
                if new_tool.get("pricing"):
                    merged_tool["pricing"] = new_tool["pricing"]
                
                if new_tool.get("status"):
                    merged_tool["status"] = new_tool["status"]
            
            merged_tool["last_updated"] = datetime.now().isoformat()
        
        merged_tools.append(merged_tool)
    
    # Add new tools
    existing_names = {t.get("name") for t in existing_tools}
    for new_tool in enriched_data:
        if new_tool.get("name") not in existing_names:
            new_tool["version"] = "1.0"
            new_tool["version_history"] = []
            new_tool["added_date"] = datetime.now().isoformat()
            merged_tools.append(new_tool)
            version_log["new_tools"].append(new_tool.get("name"))
    
    logger.info(f"\n📊 VERSION SUMMARY:")
    logger.info(f"   - Major updates: {len(version_log['major_updates'])}")
    logger.info(f"   - Minor updates: {len(version_log['minor_updates'])}")
    logger.info(f"   - New tools: {len(version_log['new_tools'])}")
    
    return merged_tools, version_log
