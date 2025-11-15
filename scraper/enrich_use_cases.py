#!/usr/bin/env python3
"""
Use Case Enrichment Script
Enriches AI tools with use case compatibility data using Claude API

Cost: ~$0.15-0.25 for 61 tools (one-time operation)
"""

import json
import os
import sys
import io
from pathlib import Path
import anthropic
from typing import Dict, List, Any
import time
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / '.env')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
TOOLS_FILE = Path(__file__).parent.parent / "public" / "ai_tracker_enhanced.json"
TAXONOMY_FILE = Path(__file__).parent.parent / "public" / "use_case_taxonomy.json"
OUTPUT_FILE = Path(__file__).parent.parent / "public" / "use_cases_enrichment.json"
OVERRIDES_FILE = Path(__file__).parent.parent / "public" / "use_cases_overrides.json"

# Claude API configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Sonnet 4.5 model (May 2025)
MAX_TOKENS = 4096

def load_json(file_path: Path) -> Dict:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict, file_path: Path):
    """Save JSON file with pretty formatting"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved to {file_path}")

def get_use_case_list(taxonomy: Dict) -> List[str]:
    """Extract flat list of all use case IDs from taxonomy"""
    use_cases = []
    for category_id, category in taxonomy['categories'].items():
        for use_case_id in category['use_cases'].keys():
            use_cases.append(use_case_id)
    return use_cases

def build_enrichment_prompt(tool: Dict, use_cases: List[str], taxonomy: Dict) -> str:
    """Build the prompt for Claude to analyze a tool"""

    # Build use case reference
    use_case_ref = "\n".join([
        f"- {uc_id}: {taxonomy['categories'][cat_id]['use_cases'][uc_id]['description']}"
        for cat_id, cat in taxonomy['categories'].items()
        for uc_id in cat['use_cases'].keys()
    ])

    prompt = f"""You are an expert AI tools analyst. Analyze this AI tool and determine its use case compatibility.

Tool Information:
- Name: {tool.get('name')}
- Description: {tool.get('description', 'N/A')}
- Category: {tool.get('category', 'N/A')}
- URL: {tool.get('url', 'N/A')}

Available Use Cases:
{use_case_ref}

Your task: Analyze this tool and return a JSON object with the following structure:

{{
  "use_case_compatibility": {{
    "use-case-id": {{
      "strength": 0-100,
      "type": "primary" | "secondary",
      "notes": "Brief explanation of why this tool is good for this use case",
      "limitations": ["Optional list of limitations for this specific use case"]
    }}
  }},
  "technical_profile": {{
    "coding_level": "no-code" | "low-code" | "developer" | "expert",
    "user_levels": ["beginner", "intermediate", "expert"],
    "platform": "web-based" | "desktop" | "mobile" | "api" | "ide-plugin",
    "integrations": ["list of key integrations if applicable"],
    "learning_curve": "easy" | "moderate" | "steep"
  }},
  "best_for": {{
    "primary": "One sentence describing what this tool is best for",
    "ideal_user": "Who is the ideal user for this tool",
    "key_differentiator": "What makes this tool unique or stand out"
  }},
  "limitations": [
    "List of general limitations of this tool"
  ],
  "pricing_tier": {{
    "has_free_tier": true | false,
    "free_tier_limits": "Description of free tier limitations if applicable",
    "recommended_tier": "Which pricing tier is recommended",
    "enterprise_available": true | false
  }}
}}

Guidelines:
1. Only include use cases where this tool has meaningful capability (strength >= 40)
2. Mark as "primary" if strength >= 70, "secondary" if 40-69
3. Be realistic about limitations - don't oversell the tool
4. Focus on what makes this tool unique compared to alternatives
5. For coding_level: no-code (zero coding), low-code (minimal), developer (full coding), expert (advanced)
6. Return ONLY the JSON object, no additional text

JSON Response:"""

    return prompt

def enrich_tool(tool: Dict, taxonomy: Dict, client: anthropic.Anthropic) -> Dict:
    """Enrich a single tool using Claude API"""

    print(f"\n🔍 Analyzing: {tool.get('name')}")

    use_cases = get_use_case_list(taxonomy)
    prompt = build_enrichment_prompt(tool, use_cases, taxonomy)

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract JSON from response
        response_text = response.content[0].text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]

        enrichment_data = json.loads(response_text.strip())

        # Add metadata
        enrichment_data['enrichment_meta'] = {
            'source': 'claude-api',
            'model': response.model,
            'date': time.strftime('%Y-%m-%d'),
            'version': '1.0',
            'manually_reviewed': False
        }

        print(f"   ✅ Success - {len(enrichment_data.get('use_case_compatibility', {}))} use cases identified")

        return enrichment_data

    except json.JSONDecodeError as e:
        print(f"   ❌ JSON parsing error: {e}")
        print(f"   Response: {response_text[:200]}...")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def enrich_tools(tool_names: List[str] = None, limit: int = None):
    """
    Enrich tools with use case data

    Args:
        tool_names: Optional list of specific tool names to enrich
        limit: Optional limit on number of tools to enrich (for testing)
    """

    print("🚀 Use Case Enrichment Script")
    print("=" * 60)

    # Load data
    print("\n📂 Loading data...")
    tools_data = load_json(TOOLS_FILE)
    taxonomy = load_json(TAXONOMY_FILE)

    tools = tools_data.get('tools', [])
    print(f"   ✅ Loaded {len(tools)} tools")
    print(f"   ✅ Loaded taxonomy with {len(taxonomy['categories'])} categories")

    # Filter tools if specific names provided
    if tool_names:
        tools = [t for t in tools if t.get('name') in tool_names]
        print(f"   🎯 Filtering to {len(tools)} specific tools: {tool_names}")

    # Apply limit if specified
    if limit:
        tools = tools[:limit]
        print(f"   🎯 Limiting to first {limit} tools")

    # Check for API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("\n❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("   Please set your Anthropic API key:")
        print("   export ANTHROPIC_API_KEY='your-key-here'")
        return

    # Initialize Claude client
    client = anthropic.Anthropic(api_key=api_key)

    # Load existing enrichments if available
    enrichments = {}
    if OUTPUT_FILE.exists():
        print(f"\n📂 Loading existing enrichments from {OUTPUT_FILE}")
        enrichments = load_json(OUTPUT_FILE)

    # Load overrides if available
    overrides = {}
    if OVERRIDES_FILE.exists():
        print(f"📂 Loading manual overrides from {OVERRIDES_FILE}")
        overrides = load_json(OVERRIDES_FILE)

    # Enrich each tool
    print(f"\n🔄 Enriching {len(tools)} tools...")
    print("=" * 60)

    success_count = 0
    skip_count = 0
    error_count = 0

    for i, tool in enumerate(tools, 1):
        tool_name = tool.get('name')

        # Skip if override exists
        if tool_name in overrides:
            print(f"\n[{i}/{len(tools)}] ⏭️  Skipping {tool_name} (manual override exists)")
            enrichments[tool_name] = overrides[tool_name]
            skip_count += 1
            continue

        # Skip if already enriched (unless re-enriching)
        if tool_name in enrichments and enrichments[tool_name].get('enrichment_meta'):
            print(f"\n[{i}/{len(tools)}] ⏭️  Skipping {tool_name} (already enriched)")
            skip_count += 1
            continue

        # Enrich the tool
        print(f"\n[{i}/{len(tools)}] ", end="")
        enrichment = enrich_tool(tool, taxonomy, client)

        if enrichment:
            enrichments[tool_name] = enrichment
            success_count += 1

            # Save incrementally (in case of interruption)
            save_json(enrichments, OUTPUT_FILE)
        else:
            error_count += 1

        # Rate limiting - small delay between requests
        if i < len(tools):
            time.sleep(1)

    # Final save
    save_json(enrichments, OUTPUT_FILE)

    # Summary
    print("\n" + "=" * 60)
    print("📊 Enrichment Summary")
    print("=" * 60)
    print(f"✅ Successfully enriched: {success_count}")
    print(f"⏭️  Skipped (override/existing): {skip_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📁 Total in database: {len(enrichments)}")
    print(f"\n💾 Output saved to: {OUTPUT_FILE}")

    # Estimate cost (very rough - depends on actual token usage)
    estimated_cost = success_count * 0.004  # ~$0.004 per tool
    print(f"\n💰 Estimated API cost: ${estimated_cost:.3f}")

def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(description='Enrich AI tools with use case data')
    parser.add_argument('--tools', nargs='+', help='Specific tool names to enrich')
    parser.add_argument('--limit', type=int, help='Limit number of tools to enrich (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode: enrich only 5 tools')

    args = parser.parse_args()

    if args.test:
        print("🧪 TEST MODE: Enriching first 5 tools only\n")
        enrich_tools(limit=5)
    else:
        enrich_tools(tool_names=args.tools, limit=args.limit)

if __name__ == '__main__':
    main()
