"""
Perplexity AI enrichment and analysis
"""

import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enrich_with_perplexity(tools, updates):
    """
    Enrich tool data with Perplexity analysis
    Note: Requires PERPLEXITY_API_KEY environment variable
    """
    
    try:
        import requests
    except ImportError:
        logger.warning("Requests library not installed. Skipping enrichment.")
        return tools
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        logger.warning("PERPLEXITY_API_KEY not set. Skipping Perplexity enrichment.")
        return tools
    
    try:
        for tool in tools:
            tool_name = tool.get("name")
            
            # Get recent updates for this tool
            tool_updates = [u for u in updates if u.get("tool_name") == tool_name]
            
            if not tool_updates:
                continue
            
            logger.info(f"Enriching {tool_name} with Perplexity...")
            
            # Prepare update summary
            updates_text = "\n".join([
                f"- {u.get('title', '')}: {u.get('description', '')[:200]}"
                for u in tool_updates[:3]
            ])
            
            # Ask Perplexity to analyze
            prompt = f"""Analyze these recent updates for {tool_name} and provide:
1. Summary of what changed (1-2 sentences)
2. Impact level (high/medium/low)
3. Key features or improvements
4. Any breaking changes or deprecations

Updates:
{updates_text}

Respond in JSON format with keys: summary, impact, features, breaking_changes"""
            
            analysis = call_perplexity_api(api_key, prompt)
            
            if analysis:
                try:
                    import json
                    analysis_obj = json.loads(analysis)
                    tool["latest_analysis"] = {
                        "summary": analysis_obj.get("summary", ""),
                        "impact": analysis_obj.get("impact", "medium"),
                        "features": analysis_obj.get("features", []),
                        "breaking_changes": analysis_obj.get("breaking_changes", []),
                        "analyzed_at": datetime.now().isoformat(),
                        "source": "perplexity"
                    }
                except (json.JSONDecodeError, ValueError):
                    logger.warning(f"Could not parse Perplexity response for {tool_name}")
                    tool["latest_analysis"] = {
                        "raw_analysis": analysis,
                        "analyzed_at": datetime.now().isoformat(),
                        "source": "perplexity"
                    }
    
    except Exception as e:
        logger.warning(f"Error enriching with Perplexity: {e}")
    
    return tools


def call_perplexity_api(api_key, prompt):
    """Call Perplexity API"""
    try:
        import requests
        
        url = "https://api.perplexity.ai/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-pro",  # Perplexity's best model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        else:
            logger.warning("Unexpected Perplexity API response format")
            return None
    
    except Exception as e:
        logger.warning(f"Error calling Perplexity API: {e}")
        return None


def calculate_impact_score(analysis):
    """Calculate impact score from analysis"""
    impact_map = {"high": 10, "medium": 5, "low": 2}
    return impact_map.get(analysis.get("impact", "medium"), 5)


def summarize_updates(updates):
    """Summarize updates for a tool"""
    if not updates:
        return "No recent updates"
    
    titles = [u.get("title", "") for u in updates[:3]]
    return "; ".join(titles)
