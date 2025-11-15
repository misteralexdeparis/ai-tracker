"""
Quick rescoring script - recalculates scores for all existing tools
without doing a full scrape. Useful for testing scoring algorithm changes.
"""

import json
import logging
import sys
import io
from pathlib import Path
from utils.scoring_v4 import score_all_tools, calculate_buzz_score, calculate_vision_score, calculate_ability_score, apply_curated_safety_net

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("=" * 70)
    print("QUICK RESCORE - Recalculate scores for all existing tools")
    print("=" * 70 + "\n")

    # Load existing tools
    data_file = Path(__file__).parent.parent / 'public' / 'ai_tracker_enhanced.json'
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tools = data['tools']
    logger.info(f"📊 Loaded {len(tools)} tools\n")

    # STEP 1: Clear old scores
    logger.info("🗑️  Clearing old scores...\n")
    for tool in tools:
        for score_field in ["buzz_score", "vision", "ability", "credibility", "adoption",
                           "final_score", "base_score", "scoring_breakdown", "scoring_metadata"]:
            tool.pop(score_field, None)

    # STEP 2: Recalculate dimension scores (buzz, vision, ability)
    logger.info("🧮 Recalculating dimension scores (buzz, vision, ability)...\n")
    for tool in tools:
        tool['buzz_score'] = calculate_buzz_score(tool)
        tool['vision'] = calculate_vision_score(tool)
        tool['ability'] = calculate_ability_score(tool)

        # Apply curated safety net
        apply_curated_safety_net(tool)

    # STEP 3: Score all tools (calculates final scores + ensures uniqueness)
    logger.info("🎯 Calculating final scores and ensuring uniqueness...\n")
    tools = score_all_tools(tools)

    # STEP 4: Save
    data['tools'] = tools
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✅ Rescoring complete! Saved to {data_file}")

    # Show score distribution
    score_counts = {}
    for tool in tools:
        vision = round(tool.get('vision', 0))
        ability = round(tool.get('ability', 0))
        key = f"{vision}/{ability}"
        score_counts[key] = score_counts.get(key, 0) + 1

    duplicates = {k: v for k, v in score_counts.items() if v > 1}
    if duplicates:
        logger.warning(f"\n⚠️  Still have {len(duplicates)} duplicate score combinations:")
        for combo, count in list(duplicates.items())[:5]:
            logger.warning(f"   {combo}: {count} tools")
    else:
        logger.info("\n✅ All vision/ability combinations are unique!")

if __name__ == '__main__':
    main()
