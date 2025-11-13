#!/usr/bin/env python3
"""
Curated Tools Loader - Get list of essential AI leaders
Loads from curated_ai_tools.json (same directory)
Integrated with version tracking
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

def load_curated_tools(json_path=None):
    """Load raw JSON from curated_ai_tools.json"""
    
    if json_path is None:
        # Path: curated_ai_tools.json is in scraper/sources/ (same as this file)
        json_path = os.path.join(os.path.dirname(__file__), 'curated_ai_tools.json')
    
    if not os.path.exists(json_path):
        logger.warning(f"❌ curated_ai_tools.json NOT FOUND at {json_path}")
        return []
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            tools = json.load(f)
            logger.info(f"✅ Loaded {len(tools)} curated AI tools")
            return tools
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON in curated_ai_tools.json: {e}")
        return []
    except Exception as e:
        logger.error(f"❌ Error loading curated tools: {e}")
        return []

def get_curated_tools(config=None):
    """
    Get curated tools with version tracking
    Integrates with version_tracker for automatic updates
    """
    
    curated = load_curated_tools()
    
    if not curated:
        logger.warning("⚠️  No curated tools loaded")
        return []
    
    try:
        from sources.version_tracker import track_tool_version, compare_versions
        
        logger.info(f"🔍 Checking versions for {len(curated)} curated tools...")
        
        for tool in curated:
            if not tool.get("tracking_versions"):
                continue
            
            old_version = tool.get("last_known_version", "0.0.0")
            
            try:
                # Use version tracker to get latest version
                new_version, source, metadata = track_tool_version(tool)
                
                if new_version and new_version != old_version:
                    # Update version
                    tool["last_known_version"] = new_version
                    tool["version_source"] = source
                    tool["version_metadata"] = metadata
                    
                    # Check if major update
                    update_type, is_major = compare_versions(old_version, new_version)
                    
                    if is_major:
                        logger.info(f"🔴 MAJOR UPDATE: {tool['name']} {old_version} → {new_version}")
                        tool["needs_major_review"] = True
                    else:
                        logger.info(f"🟡 Minor update: {tool['name']} {old_version} → {new_version}")
                        tool["needs_major_review"] = False
            except Exception as e:
                logger.debug(f"⚠️  Could not track version for {tool.get('name')}: {e}")
                continue
        
        logger.info(f"✅ Curated tools version check complete\n")
        
    except ImportError:
        logger.warning("⚠️  version_tracker not available, skipping version check")
    except Exception as e:
        logger.warning(f"⚠️  Error during version tracking: {e}")
    
    return curated

# Usage: always include get_curated_tools() when building your global tools list