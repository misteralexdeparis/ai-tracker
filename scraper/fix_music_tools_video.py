#!/usr/bin/env python3
"""
Fix Music Tools Video Compatibility
Removes video-generation use case from music tools (Suno, AIVA)
as they only provide audio/soundtracks, not actual video creation.
"""

import json
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# File paths
ENRICHMENT_FILE = Path(__file__).parent.parent / "public" / "use_cases_enrichment.json"

def load_json(file_path):
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """Save JSON file with pretty formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def fix_music_tools():
    """Remove video-generation from music tools"""

    print("🔧 Fixing Music Tools Video Compatibility")
    print("=" * 60)

    # Load enrichment data
    print("\n📂 Loading enrichment data...")
    enrichment = load_json(ENRICHMENT_FILE)
    print(f"   ✅ Loaded {len(enrichment)} tools")

    # Audio/Music tools to fix (tools that only provide audio, not actual video)
    audio_tools = ['Suno', 'AIVA', 'ElevenLabs', 'Riffusion']

    print(f"\n🔄 Removing video-generation from audio/music tools...")

    for tool_name in audio_tools:
        if tool_name in enrichment:
            tool_data = enrichment[tool_name]
            use_cases = tool_data.get('use_case_compatibility', {})

            if 'video-generation' in use_cases:
                old_strength = use_cases['video-generation']['strength']
                del use_cases['video-generation']
                print(f"\n   ✅ {tool_name}:")
                print(f"      Removed video-generation (was strength: {old_strength})")
            else:
                print(f"\n   ⏭️  {tool_name}: no video-generation to remove")
        else:
            print(f"\n   ⚠️  {tool_name}: not found in enrichment data")

    # Also remove video-editing if present
    print(f"\n🔄 Checking for video-editing...")

    for tool_name in audio_tools:
        if tool_name in enrichment:
            tool_data = enrichment[tool_name]
            use_cases = tool_data.get('use_case_compatibility', {})

            if 'video-editing' in use_cases:
                old_strength = use_cases['video-editing']['strength']
                del use_cases['video-editing']
                print(f"   ✅ {tool_name}: Removed video-editing (was strength: {old_strength})")

    # Save updated file
    print(f"\n💾 Saving {ENRICHMENT_FILE}...")
    save_json(enrichment, ENRICHMENT_FILE)
    print(f"   ✅ Saved successfully")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Fixed audio/music tools - removed video use cases")
    print("=" * 60)

if __name__ == '__main__':
    fix_music_tools()
