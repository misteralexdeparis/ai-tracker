#!/usr/bin/env python3
"""
Cleanup features - consolidate, deduplicate, and limit features per tool
"""

def cleanup_tools_final(tools, max_features=6):
    """
    Clean up tools: consolidate features, remove duplicates, limit per tool
    
    Args:
        tools: List of tool dictionaries
        max_features: Max number of features per tool (default: 6)
    
    Returns:
        List of cleaned tools
    """
    for tool in tools:
        # 1. Consolidate features (merge, deduplicate)
        if 'features' in tool and tool['features']:
            # Remove duplicates, keep order
            seen = set()
            unique_features = []
            for feature in tool['features']:
                feature_lower = str(feature).lower().strip()
                if feature_lower not in seen:
                    seen.add(feature_lower)
                    unique_features.append(feature)
            
            # Limit to max_features
            tool['features'] = unique_features[:max_features]
        
        # 2. Do same for strengths
        if 'strengths' in tool and tool['strengths']:
            seen = set()
            unique_strengths = []
            for strength in tool['strengths']:
                strength_lower = str(strength).lower().strip()
                if strength_lower not in seen:
                    seen.add(strength_lower)
                    unique_strengths.append(strength)
            
            tool['strengths'] = unique_strengths[:max_features]
        
        # 3. Do same for limitations
        if 'limitations' in tool and tool['limitations']:
            seen = set()
            unique_limitations = []
            for limitation in tool['limitations']:
                limitation_lower = str(limitation).lower().strip()
                if limitation_lower not in seen:
                    seen.add(limitation_lower)
                    unique_limitations.append(limitation)
            
            tool['limitations'] = unique_limitations[:max_features]
        
        # 4. Do same for changelog
        if 'changelog' in tool and tool['changelog']:
            seen = set()
            unique_changelog = []
            for entry in tool['changelog']:
                entry_lower = str(entry).lower().strip()
                if entry_lower not in seen:
                    seen.add(entry_lower)
                    unique_changelog.append(entry)
            
            # Keep last 4 entries for changelog
            tool['changelog'] = unique_changelog[:4]
    
    return tools
