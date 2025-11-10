"""
Candidate tool discovery and auto-analysis with Perplexity
"""

import logging
import os
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_candidate_tool(tool_candidate, api_key):
    """
    Auto-analyze a candidate tool with Perplexity
    Returns enriched tool with estimated scores
    """
    
    tool_name = tool_candidate.get("name", "Unknown")
    
    try:
        prompt = f"""Analyze the AI tool "{tool_name}" and provide:

1. Brief description (1-2 sentences)
2. Category (LLM, Image Generation, Video Generation, AI Coding, Search & Research, Audio, Other, etc.)
3. Status (active, beta, discontinued, legacy)
4. Twitter handle (if exists, format: @handle)
5. Official website URL
6. Key features (list 3-5)
7. Estimated Vision Score (0-100): How complete is the vision/roadmap?
8. Estimated Ability Score (0-100): How mature and reliable is the product?
9. Estimated Quadrant (Leader, Visionary, Challenger, or Niche)

Format your response as JSON with keys: description, category, status, twitter_handle, website, features, vision_score, ability_score, quadrant

Be realistic with scores based on market position and maturity."""
        
        from requests import post
        
        response = post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "sonar-pro",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 800,
                "temperature": 0.3
            },
            timeout=30
        )
        
        response.raise_for_status()
        data = response.json()
        
        if "choices" not in data or not data["choices"]:
            logger.warning(f"Empty response from Perplexity for {tool_name}")
            return None
        
        analysis_text = data["choices"][0]["message"]["content"]
        
        # Parse JSON from response
        import json
        import re
        
        # Extract JSON from markdown code blocks if present
        json_match = re.search(r'```json\n?(.*?)\n?```', analysis_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            json_text = analysis_text
        
        analysis = json.loads(json_text)
        
        # Build enriched tool
        enriched_tool = {
            "name": tool_name,
            "description": analysis.get("description", ""),
            "category": analysis.get("category", "Other"),
            "status": analysis.get("status", "active"),
            "twitter_handle": analysis.get("twitter_handle", ""),
            "official_url": analysis.get("website", tool_candidate.get("url", "")),
            "discord_server": tool_candidate.get("discord_server", ""),
            "reddit": analysis.get("reddit", "r/ArtificialIntelligence"),
            "vision": int(analysis.get("vision_score", 50)),
            "ability": int(analysis.get("ability_score", 40)),
            "quadrant": analysis.get("quadrant", "Niche"),
            "features": analysis.get("features", []),
            "source": tool_candidate.get("source", "forum_discovery"),
            "buzz_score": tool_candidate.get("buzz_score", 50),
            "discovered_at": datetime.now().isoformat(),
            "added_date": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Analyzed {tool_name}: {enriched_tool['quadrant']} ({enriched_tool['vision']}/{enriched_tool['ability']})")
        return enriched_tool
    
    except Exception as e:
        logger.warning(f"Error analyzing candidate {tool_name}: {e}")
        return None


def batch_analyze_candidates(candidates, api_key, max_parallel=3):
    """
    Analyze multiple candidate tools
    """
    analyzed = []
    
    for i, candidate in enumerate(candidates):
        if i >= max_parallel:  # Limit parallel to avoid rate limits
            break
        
        logger.info(f"Analyzing candidate {i+1}/{len(candidates)}: {candidate.get('name', 'Unknown')}")
        
        result = analyze_candidate_tool(candidate, api_key)
        if result:
            analyzed.append(result)
    
    return analyzed


def filter_qualified_candidates(analyzed_candidates, config):
    """
    Filter candidates that meet criteria to be added
    """
    qualified = []
    
    for tool in analyzed_candidates:
        vision = tool.get("vision", 0)
        ability = tool.get("ability", 0)
        buzz_score = tool.get("buzz_score", 0)
        
        # Must meet vision/ability minimums AND have good buzz
        if (vision >= config["thresholds"]["min_vision"] and
            ability >= config["thresholds"]["min_ability"] and
            buzz_score >= config["thresholds"]["min_buzz_score"]):
            
            qualified.append(tool)
            logger.info(f"✅ QUALIFIED: {tool['name']} (Vision: {vision}, Ability: {ability}, Buzz: {buzz_score})")
        else:
            logger.info(f"❌ NOT QUALIFIED: {tool['name']} (Vision: {vision}, Ability: {ability}, Buzz: {buzz_score})")
    
    return qualified
