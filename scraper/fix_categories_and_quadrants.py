#!/usr/bin/env python3
"""
Fix Categories and Gartner Quadrants

1. Consolidate duplicate/similar categories into canonical names
2. Calculate Gartner quadrant from vision/ability scores (not manual values)
"""

import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# File paths
TOOLS_FILE = Path(__file__).parent.parent / "public" / "ai_tracker_enhanced.json"

# Category mapping: old_name -> canonical_name
CATEGORY_MAPPING = {
    # Coding/Development consolidation
    "Coding Assistant": "AI Coding Assistant",
    "Security/Coding Assistant": "AI Coding Assistant",
    "AI Coding": "AI Coding Assistant",
    "AI Coding Editor": "AI Code Editor",

    # Productivity consolidation
    "Productivity / Task Management": "Productivity & Task Management",
    "Task Manager / Productivity": "Productivity & Task Management",
    "Chatbot / Productivity": "Productivity & Task Management",
    "Project Management": "Productivity & Task Management",

    # Knowledge/Research consolidation
    "Knowledge Assistant": "Knowledge Management",
    "Knowledge Management / Productivity": "Knowledge Management",
    "Research Assistant": "Research Assistant",

    # Search consolidation
    "AI Powered Search": "AI Search",
    "AI Browser / Search": "AI Search",
    "AI Search": "AI Search",

    # Automation/No-code consolidation
    "No-code / Automation": "Automation & No-code",
    "Automation / No-code": "Automation & No-code",
    "App Builder": "Automation & No-code",

    # Content creation consolidation
    "Text Generation / Content Creation": "Content Creation",
    "Text Generation / Marketing": "Marketing Content",

    # Media generation consolidation
    "Video/Image Generation": "Image & Video Generation",
    "Video Generation": "Video Generation",
    "Image Generation": "Image Generation",
    "Design / Image / Video": "Image & Video Generation",
    "Music Generation": "Audio Generation",
    "Voice Generation": "Audio Generation",
    "Audio": "Audio Generation",

    # Meeting/transcription consolidation
    "Speech-to-Text / Meetings": "Meeting Assistant",

    # Email/CRM consolidation
    "Email/CRM Assistant": "CRM & Email Assistant",
    "CRM / Email Automation": "CRM & Email Assistant",

    # Keep as-is (already canonical)
    "Presentation": "Presentation",
    "LLM": "LLM Platform",
    "Open Source": "Open Source",
    "Infrastructure": "Infrastructure",
}

def calculate_gartner_quadrant(vision, ability):
    """Calculate Gartner quadrant from vision/ability scores"""
    vision = vision or 0
    ability = ability or 0

    if vision >= 75 and ability >= 75:
        return "Leader"
    elif vision >= 75 and ability < 75:
        return "Visionary"
    elif vision < 75 and ability >= 75:
        return "Challenger"
    else:
        return "Niche Player"

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save JSON file with pretty formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fix_tools():
    """Fix categories and Gartner quadrants"""

    print("🔧 Fixing Categories and Gartner Quadrants")
    print("=" * 60)

    # Load data
    print("\n📂 Loading tools...")
    tools_data = load_json(TOOLS_FILE)
    tools = tools_data.get('tools', [])
    print(f"   ✅ Loaded {len(tools)} tools")

    # Track changes
    category_changes = {}
    quadrant_changes = {}

    print(f"\n🔄 Processing tools...")

    for tool in tools:
        tool_name = tool.get('name')

        # Fix category
        old_category = tool.get('category')
        if old_category in CATEGORY_MAPPING:
            new_category = CATEGORY_MAPPING[old_category]
            if old_category != new_category:
                tool['category'] = new_category
                if old_category not in category_changes:
                    category_changes[old_category] = []
                category_changes[old_category].append(tool_name)

        # Calculate and fix Gartner quadrant
        vision = tool.get('vision', 0)
        ability = tool.get('ability', 0)
        old_quadrant = tool.get('gartner_quadrant')
        new_quadrant = calculate_gartner_quadrant(vision, ability)

        if old_quadrant != new_quadrant:
            tool['gartner_quadrant'] = new_quadrant
            quadrant_changes[tool_name] = {
                'old': old_quadrant,
                'new': new_quadrant,
                'vision': vision,
                'ability': ability
            }

    # Save updated file
    print(f"\n💾 Saving {TOOLS_FILE}...")
    save_json(tools_data, TOOLS_FILE)
    print(f"   ✅ Saved successfully")

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if category_changes:
        print(f"\n✅ Category consolidation ({len(category_changes)} categories updated):")
        for old_cat, tool_names in sorted(category_changes.items()):
            new_cat = CATEGORY_MAPPING[old_cat]
            print(f"\n   '{old_cat}' → '{new_cat}'")
            print(f"   ({len(tool_names)} tools)")
    else:
        print("\n✅ No category changes needed")

    if quadrant_changes:
        print(f"\n✅ Gartner quadrant recalculated ({len(quadrant_changes)} tools updated):")
        for tool_name, change in sorted(quadrant_changes.items()):
            print(f"\n   {tool_name}:")
            print(f"      Vision: {change['vision']}, Ability: {change['ability']}")
            print(f"      {change['old']} → {change['new']}")
    else:
        print("\n✅ All Gartner quadrants already correct")

    # Show final unique categories
    print(f"\n📋 Final unique categories:")
    final_categories = sorted(set(t.get('category', 'Unknown') for t in tools))
    for cat in final_categories:
        count = sum(1 for t in tools if t.get('category') == cat)
        print(f"   - {cat} ({count} tools)")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    fix_tools()
