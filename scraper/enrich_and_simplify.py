"""
Script to:
1. Merge enrichment cache into use_cases_enrichment.json
2. Simplify categories in ai_tracker_enhanced.json to 8 main categories
"""

import json
from pathlib import Path
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Category mapping to 8 simplified categories
CATEGORY_MAPPING = {
    # Content Creation & Writing
    'Text Generation / Content Creation': 'Content Creation & Writing',
    'Text Generation / Marketing': 'Content Creation & Writing',
    'Chatbot / Productivity': 'Content Creation & Writing',

    # Code Development & Engineering
    'AI Coding': 'Code Development & Engineering',
    'AI Coding Editor': 'Code Development & Engineering',
    'Coding Assistant': 'Code Development & Engineering',
    'Security/Coding Assistant': 'Code Development & Engineering',

    # Research & Analysis
    'AI Browser / Search': 'Research & Analysis',
    'AI Powered Search': 'Research & Analysis',
    'AI Search': 'Research & Analysis',
    'Research Assistant': 'Research & Analysis',
    'Knowledge Assistant': 'Research & Analysis',
    'Knowledge Management': 'Research & Analysis',
    'Knowledge Management / Productivity': 'Research & Analysis',

    # Visual & Multimedia
    'Image Generation': 'Visual & Multimedia',
    'Video Generation': 'Visual & Multimedia',
    'Video/Image Generation': 'Visual & Multimedia',
    'Design / Image / Video': 'Visual & Multimedia',
    'Music Generation': 'Visual & Multimedia',
    'Voice Generation': 'Visual & Multimedia',
    'Audio': 'Visual & Multimedia',

    # Productivity & Automation
    'Automation / No-code': 'Productivity & Automation',
    'No-code / Automation': 'Productivity & Automation',
    'Productivity / Task Management': 'Productivity & Automation',
    'Task Manager / Productivity': 'Productivity & Automation',
    'Project Management': 'Productivity & Automation',
    'App Builder': 'Productivity & Automation',

    # Data & Analytics
    'LLM': 'Data & Analytics',
    'Infrastructure': 'Data & Analytics',
    'Open Source': 'Data & Analytics',

    # Communication
    'CRM / Email Automation': 'Communication',
    'Email/CRM Assistant': 'Communication',
    'Speech-to-Text / Meetings': 'Communication',

    # Business & Strategy
    'Presentation': 'Business & Strategy',
}

def normalize_tool_name(name):
    """Normalize tool name for matching with cache"""
    return name.lower().replace(' ', '').replace('-', '') + '_nourl'

def merge_enrichments():
    """Merge cache enrichments into public file"""
    print("Step 1: Merging enrichment cache...")

    # Load cache
    cache_path = Path(__file__).parent / 'cache' / 'enrichment_cache.json'
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)

    # Load current enrichments
    enrichment_path = Path(__file__).parent.parent / 'public' / 'use_cases_enrichment.json'
    with open(enrichment_path, 'r', encoding='utf-8') as f:
        current = json.load(f)

    # Load tools list to get all tool names
    tools_path = Path(__file__).parent.parent / 'public' / 'ai_tracker_enhanced.json'
    with open(tools_path, 'r', encoding='utf-8') as f:
        tools_data = json.load(f)

    # Create enrichment dict from current (already a dict)
    enrichment_dict = current if isinstance(current, dict) else {item['tool_name']: item for item in current}

    # Add missing tools from cache
    added = 0
    for tool in tools_data['tools']:
        tool_name = tool['name']
        if tool_name not in enrichment_dict:
            # Try to find in cache
            normalized = normalize_tool_name(tool_name)
            if normalized in cache:
                enrichment_dict[tool_name] = cache[normalized]
                added += 1
                print(f"  Added: {tool_name}")

    # Save updated enrichments (keep as dict)
    with open(enrichment_path, 'w', encoding='utf-8') as f:
        json.dump(enrichment_dict, f, indent=2, ensure_ascii=False)

    print(f"✓ Merged {added} new enrichments. Total: {len(enrichment_dict)}")
    return len(enrichment_dict)

def simplify_categories():
    """Simplify categories to 8 main ones"""
    print("\nStep 2: Simplifying categories...")

    tools_path = Path(__file__).parent.parent / 'public' / 'ai_tracker_enhanced.json'
    with open(tools_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Track changes
    changes = {}

    # Update categories
    for tool in data['tools']:
        old_cat = tool['category']
        new_cat = CATEGORY_MAPPING.get(old_cat, old_cat)

        if old_cat != new_cat:
            tool['category'] = new_cat
            if old_cat not in changes:
                changes[old_cat] = new_cat

    # Save updated data
    with open(tools_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✓ Category mappings:")
    for old, new in sorted(changes.items()):
        print(f"  {old} → {new}")

    # Show final distribution
    cat_counts = {}
    for tool in data['tools']:
        cat = tool['category']
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print("\n✓ Final category distribution:")
    for cat, count in sorted(cat_counts.items()):
        print(f"  {cat}: {count} tools")

    return len(cat_counts)

def main():
    print("=" * 60)
    print("Enrichment Merge & Category Simplification")
    print("=" * 60)

    try:
        total_enriched = merge_enrichments()
        total_categories = simplify_categories()

        print("\n" + "=" * 60)
        print("✅ SUCCESS!")
        print(f"  • {total_enriched} tools enriched")
        print(f"  • {total_categories} simplified categories")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
