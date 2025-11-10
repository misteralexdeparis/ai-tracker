"""
Helper utilities for scraper
"""

import json
from pathlib import Path
from datetime import datetime


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
        print(f"Saved tools to {tools_path}")
    except Exception as e:
        print(f"Error saving tools JSON: {e}")


def score_candidates(existing_tools, candidates, config):
    """Score tools and candidates"""
    all_tools = existing_tools.copy() if existing_tools else []
    
    for candidate in candidates:
        buzz_score = candidate.get("buzz_score", 50)
        vision = candidate.get("vision", 50)
        ability = candidate.get("ability", 40)
        
        thresholds = config.get("thresholds", {})
        min_vision = thresholds.get("min_vision", 50)
        min_ability = thresholds.get("min_ability", 40)
        min_buzz = thresholds.get("min_buzz_score", 50)
        
        if vision >= min_vision and ability >= min_ability and buzz_score >= min_buzz:
            candidate["status"] = "tracked"
            candidate["added_date"] = datetime.now().isoformat()
            all_tools.append(candidate)
    
    return all_tools


def apply_manual_overrides(tools, config):
    """Apply manual add/remove overrides"""
    result = tools.copy() if tools else []
    
    manual = config.get("manual_overrides", {})
    
    # Force add
    for force_add in manual.get("force_add", []):
        if not any(t.get("name") == force_add.get("name") for t in result):
            force_add["status"] = "tracked"
            force_add["added_date"] = datetime.now().isoformat()
            result.append(force_add)
    
    # Force remove
    for force_remove in manual.get("force_remove", []):
        result = [t for t in result if t.get("name") != force_remove.get("name")]
    
    return result


def remove_legacy_versions(tools):
    """Remove tools that have been replaced by newer versions"""
    result = []
    
    for tool in tools:
        status = tool.get("status", "active")
        
        if status not in ["discontinued", "legacy", "replaced"]:
            result.append(tool)
    
    return result


def filter_by_max_tools(tools, config):
    """Filter to max tools, keeping highest scored ones"""
    thresholds = config.get("thresholds", {})
    max_tools = thresholds.get("max_tools", 100)
    
    if len(tools) <= max_tools:
        return tools
    
    sorted_tools = sorted(
        tools,
        key=lambda x: x.get("buzz_score", 0) + (x.get("vision", 0) + x.get("ability", 0)) / 2,
        reverse=True
    )
    
    return sorted_tools[:max_tools]