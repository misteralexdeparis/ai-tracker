#!/usr/bin/env python3
"""
Restore Curated Scores
This script restores vision/ability/gartner_quadrant scores from curated_manual_scores.json
to ai_tracker_enhanced.json, overriding any incorrect calculated values.
"""

import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# File paths
CURATED_SCORES_FILE = Path(__file__).parent / "sources" / "curated_manual_scores.json"
TOOLS_FILE = Path(__file__).parent.parent / "public" / "ai_tracker_enhanced.json"

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save JSON file with pretty formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def restore_scores():
    """Restore curated scores to tools file"""

    print("🔧 Restoring Curated Scores")
    print("=" * 60)

    # Load data
    print("\n📂 Loading files...")
    curated_scores = load_json(CURATED_SCORES_FILE)
    tools_data = load_json(TOOLS_FILE)

    print(f"   ✅ Loaded {len(curated_scores)} curated scores")
    print(f"   ✅ Loaded {len(tools_data.get('tools', []))} tools")

    # Apply curated scores
    print(f"\n🔄 Applying curated scores...")
    restored_count = 0

    for tool in tools_data.get('tools', []):
        tool_name = tool.get('name')

        if tool_name in curated_scores:
            curated = curated_scores[tool_name]
            old_scores = {
                'vision': tool.get('vision'),
                'ability': tool.get('ability'),
                'gartner_quadrant': tool.get('gartner_quadrant')
            }

            # Apply curated scores
            tool['vision'] = curated.get('vision')
            tool['ability'] = curated.get('ability')

            # Derive gartner_quadrant from vision/ability scores
            vision = curated.get('vision', 0)
            ability = curated.get('ability', 0)

            if vision >= 75 and ability >= 75:
                gartner_quadrant = "Leader"
            elif vision >= 75 and ability < 75:
                gartner_quadrant = "Visionary"
            elif vision < 75 and ability >= 75:
                gartner_quadrant = "Challenger"
            else:
                gartner_quadrant = "Niche Player"

            tool['gartner_quadrant'] = gartner_quadrant

            # Show what changed
            if (old_scores['vision'] != tool['vision'] or
                old_scores['ability'] != tool['ability'] or
                old_scores['gartner_quadrant'] != tool['gartner_quadrant']):

                print(f"\n   🔄 {tool_name}:")
                if old_scores['vision'] != tool['vision']:
                    print(f"      Vision: {old_scores['vision']} → {tool['vision']}")
                if old_scores['ability'] != tool['ability']:
                    print(f"      Ability: {old_scores['ability']} → {tool['ability']}")
                if old_scores['gartner_quadrant'] != tool['gartner_quadrant']:
                    print(f"      Gartner: {old_scores['gartner_quadrant']} → {tool['gartner_quadrant']}")

                restored_count += 1

    # Save updated file
    if restored_count > 0:
        print(f"\n💾 Saving {TOOLS_FILE}...")
        save_json(tools_data, TOOLS_FILE)
        print(f"   ✅ Saved successfully")

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Restored scores for {restored_count} tools")
    print("=" * 60)

if __name__ == '__main__':
    restore_scores()
