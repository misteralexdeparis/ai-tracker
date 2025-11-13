import json
import os
import requests
from bs4 import BeautifulSoup

def load_curated_tools(json_path="curated_ai_tools.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

from sources.version_tracker import track_tool_version, compare_versions

def get_curated_tools(config=None):
    curated = load_curated_tools()
    
    for tool in curated:
        if tool.get("tracking_versions"):
            old_version = tool.get("last_known_version", "0.0.0")
            
            # Use new tracker
            new_version, source, metadata = track_tool_version(tool)
            
            if new_version and new_version != old_version:
                # Update version
                tool["last_known_version"] = new_version
                
                # Check if major update
                update_type, is_major = compare_versions(old_version, new_version)
                
                if is_major:
                    logger.info(f"🔴 MAJOR UPDATE: {tool['name']} {old_version} → {new_version}")
                    tool["needs_major_review"] = True
                else:
                    logger.info(f"🟡 Minor update: {tool['name']} {old_version} → {new_version}")
    
    return curated

def get_curated_tools(config=None):
    curated = load_curated_tools()
    for tool in curated:
        if tool.get("tracking_versions"):
            latest = scrape_latest_version(tool)
            if latest and latest != tool["last_known_version"]:
                tool["last_known_version"] = latest
    return curated

# Usage : always include get_curated_tools() when building your global tools list