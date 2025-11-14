"""
Enhanced Scoring System v4 - MODULE 3
Intelligent multi-dimensional scoring with confidence weighting

IMPROVEMENTS:
- Smart fallback based on source if no data available
- Curated tools safety net (minimum 50 score to pass filters)
- Better handling of missing data

SCORING DIMENSIONS:
- buzz (25%): Trending momentum
- vision (20%): Product clarity
- ability (20%): Technical maturity
- credibility (20%): Team/company trust
- adoption (15%): Organic usage
"""

import logging
import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# SCORING WEIGHTS
# ============================================================================

DIMENSION_WEIGHTS = {
    "buzz": 0.25,
    "vision": 0.20,
    "ability": 0.20,
    "credibility": 0.20,
    "adoption": 0.15
}

# Source-based fallback scores (when no data available)
SOURCE_FALLBACK_SCORES = {
    "curated_list": {"buzz": 70, "vision": 75, "ability": 70},
    "curated": {"buzz": 70, "vision": 75, "ability": 70},
    "official_blog": {"buzz": 65, "vision": 70, "ability": 65},
    "product_hunt": {"buzz": 60, "vision": 65, "ability": 55},
    "github_trending": {"buzz": 50, "vision": 55, "ability": 50},
    "techcrunch": {"buzz": 65, "vision": 60, "ability": 55},
    "venturebeat": {"buzz": 65, "vision": 60, "ability": 55},
    "reddit": {"buzz": 35, "vision": 40, "ability": 35},
    "hacker_news": {"buzz": 40, "vision": 45, "ability": 40},
}

# Minimum scores for curated tools (safety net)
CURATED_MIN_SCORES = {
    "buzz_score": 50,
    "vision": 50,
    "ability": 50
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_curated_tool(tool: Dict) -> bool:
    """Check if tool is from curated list"""
    return (
        tool.get("tracking_versions") or 
        tool.get("source") == "curated_list" or
        tool.get("source") == "curated"
    )

def get_fallback_score(tool: Dict, dimension: str) -> float:
    """Get fallback score based on source when no data available"""
    source = tool.get("source", "").lower()
    
    # Check exact match first
    if source in SOURCE_FALLBACK_SCORES:
        return SOURCE_FALLBACK_SCORES[source].get(dimension, 50)
    
    # Check partial match
    for key, scores in SOURCE_FALLBACK_SCORES.items():
        if key in source:
            return scores.get(dimension, 50)
    
    # Default fallback
    return 50

def has_enriched_data(tool: Dict) -> bool:
    """Check if tool has enriched data (not just basic scraped data)"""
    enriched_fields = [
        "description",
        "key_features",
        "pricing",
        "founding_year",
        "github_stars"
    ]
    
    # If at least 2 enriched fields present, consider it enriched
    present = sum(1 for field in enriched_fields if tool.get(field))
    return present >= 2

# ============================================================================
# DIMENSION CALCULATORS (INTELLIGENT FALLBACKS)
# ============================================================================

def calculate_buzz_score(tool: Dict) -> float:
    """
    Calculate buzz/trending momentum (0-100)
    Smart fallback if no data available
    """
    
    # If curated, check if we have real data or use fallback
    if is_curated_tool(tool):
        # Try to calculate with real data first
        has_data = (
            tool.get("github_stars", 0) > 0 or
            tool.get("upvotes", 0) > 0 or
            tool.get("trending", False)
        )
        
        if not has_data:
            # Use fallback score
            fallback = get_fallback_score(tool, "buzz")
            logger.debug(f"  Curated tool '{tool.get('name')}': using fallback buzz={fallback}")
            return fallback
    
    score = 0.0
    
    # GitHub stars (0-40 points)
    github_stars = tool.get("github_stars", 0)
    if github_stars > 0:
        stars_score = min(40, 10 * (github_stars ** 0.3))
        score += stars_score
    
    # Product Hunt upvotes (0-30 points)
    upvotes = tool.get("upvotes", 0)
    if upvotes > 0:
        upvotes_score = min(30, 5 * (upvotes ** 0.4))
        score += upvotes_score
    
    # Reddit/HN points (0-20 points)
    reddit_score = tool.get("reddit_score", 0)
    hn_points = tool.get("points", 0)
    social_score = min(20, (reddit_score + hn_points) / 10)
    score += social_score
    
    # Recent activity bonus (0-10 points)
    if tool.get("trending", False):
        score += 10
    
    # If score still very low and we know the source, use fallback
    if score < 20:
        fallback = get_fallback_score(tool, "buzz")
        score = max(score, fallback * 0.7)  # Use 70% of fallback as minimum
    
    return min(100, score)

def calculate_vision_score(tool: Dict) -> float:
    """
    Calculate product clarity/vision (0-100)
    Smart fallback if no data available
    """
    
    # If curated, check if we have real data or use fallback
    if is_curated_tool(tool):
        has_data = (
            len(tool.get("description", "")) > 50 or
            tool.get("key_features") or
            tool.get("has_api_docs")
        )
        
        if not has_data:
            fallback = get_fallback_score(tool, "vision")
            logger.debug(f"  Curated tool '{tool.get('name')}': using fallback vision={fallback}")
            return fallback
    
    score = 0.0
    
    # Description quality (0-30 points)
    description = tool.get("description", "")
    if description:
        desc_length = len(description)
        if desc_length > 100:
            score += 30
        elif desc_length > 50:
            score += 20
        elif desc_length > 20:
            score += 10
    
    # Key features defined (0-25 points)
    features = tool.get("key_features", [])
    if features:
        features_count = len(features) if isinstance(features, list) else 1
        score += min(25, features_count * 5)
    
    # Documentation exists (0-20 points)
    if tool.get("has_api_docs") or tool.get("has_documentation"):
        score += 20
    
    # Demo/playground available (0-15 points)
    if tool.get("has_demo") or tool.get("has_playground"):
        score += 15
    
    # Use cases defined (0-10 points)
    use_cases = tool.get("use_cases", [])
    if use_cases:
        score += 10
    
    # If score still low, use fallback
    if score < 20:
        fallback = get_fallback_score(tool, "vision")
        score = max(score, fallback * 0.7)
    
    return min(100, score)

def calculate_ability_score(tool: Dict) -> float:
    """
    Calculate technical maturity/ability (0-100)
    Smart fallback if no data available
    """
    
    # If curated, check if we have real data or use fallback
    if is_curated_tool(tool):
        has_data = (
            tool.get("github_url") or
            tool.get("has_api_docs") or
            tool.get("last_known_version")
        )
        
        if not has_data:
            fallback = get_fallback_score(tool, "ability")
            logger.debug(f"  Curated tool '{tool.get('name')}': using fallback ability={fallback}")
            return fallback
    
    score = 0.0
    
    # GitHub health (0-30 points)
    if tool.get("github_url"):
        last_commit_days = tool.get("days_since_last_commit", 999)
        if last_commit_days < 7:
            score += 30
        elif last_commit_days < 30:
            score += 20
        elif last_commit_days < 90:
            score += 10
    
    # Integration count (0-25 points)
    integrations = tool.get("num_integrations", 0)
    score += min(25, integrations * 2.5)
    
    # Has stable API (0-20 points)
    if tool.get("has_api_docs") or tool.get("has_sdk"):
        score += 20
    
    # Production status (0-15 points)
    status = tool.get("status", "").lower()
    if status == "active" or status == "production":
        score += 15
    elif status == "beta":
        score += 10
    elif status == "alpha":
        score += 5
    
    # Has versioning (0-10 points)
    if tool.get("last_known_version"):
        score += 10
    
    # If score still low, use fallback
    if score < 20:
        fallback = get_fallback_score(tool, "ability")
        score = max(score, fallback * 0.7)
    
    return min(100, score)

def calculate_credibility_score(tool: Dict) -> float:
    """Calculate team/company credibility (0-100)"""
    
    score = 0.0
    
    # Curated tools automatically get high credibility
    if is_curated_tool(tool):
        score += 40
    
    # Funding stage (0-30 points)
    funding = tool.get("funding_stage", "").lower()
    if "series" in funding:
        if "c" in funding or "d" in funding:
            score += 30
        elif "b" in funding:
            score += 25
        elif "a" in funding:
            score += 20
    elif "seed" in funding:
        score += 15
    
    # Company age (0-20 points)
    founding_year = tool.get("founding_year", 0)
    if founding_year > 0:
        age = datetime.now().year - founding_year
        if age >= 5:
            score += 20
        elif age >= 3:
            score += 15
        elif age >= 1:
            score += 10
        else:
            score += 5
    
    # Has LinkedIn company page (0-15 points)
    if tool.get("linkedin_url") or tool.get("has_linkedin"):
        score += 15
    
    # Customer testimonials/case studies (0-20 points)
    testimonials = tool.get("customer_count", 0)
    if testimonials > 100:
        score += 20
    elif testimonials > 10:
        score += 15
    elif testimonials > 0:
        score += 10
    
    # Media coverage (0-15 points)
    if tool.get("media_mentions", 0) > 0:
        score += 15
    elif tool.get("source") in ["techcrunch", "venturebeat"]:
        score += 10
    
    return min(100, score)

def calculate_adoption_score(tool: Dict) -> float:
    """Calculate organic adoption/usage (0-100)"""
    
    score = 0.0
    
    # GitHub dependents (0-30 points)
    dependents = tool.get("github_dependents", 0)
    if dependents > 0:
        dep_score = min(30, 5 * (dependents ** 0.5))
        score += dep_score
    
    # Package downloads (0-30 points)
    npm_downloads = tool.get("npm_downloads", 0)
    pip_downloads = tool.get("pip_downloads", 0)
    total_downloads = npm_downloads + pip_downloads
    
    if total_downloads > 100000:
        score += 30
    elif total_downloads > 10000:
        score += 20
    elif total_downloads > 1000:
        score += 10
    
    # App store reviews (0-20 points)
    app_reviews = tool.get("app_store_reviews", 0)
    if app_reviews > 1000:
        score += 20
    elif app_reviews > 100:
        score += 15
    elif app_reviews > 10:
        score += 10
    
    # Community size (0-20 points)
    community_size = tool.get("community_size", 0)
    discord_members = tool.get("discord_members", 0)
    total_community = community_size + discord_members
    
    if total_community > 10000:
        score += 20
    elif total_community > 1000:
        score += 15
    elif total_community > 100:
        score += 10
    
    return min(100, score)

# ============================================================================
# CURATED TOOLS SAFETY NET
# ============================================================================

def apply_curated_safety_net(tool: Dict) -> None:
    """
    Apply minimum scores for curated tools to ensure they pass filters
    Modifies tool dict in-place
    """
    if not is_curated_tool(tool):
        return
    
    modified = []
    
    for dimension, min_score in CURATED_MIN_SCORES.items():
        current_score = tool.get(dimension, 0)
        if current_score < min_score:
            tool[dimension] = min_score
            modified.append(f"{dimension}={current_score:.0f}→{min_score}")
    
    if modified:
        logger.info(f"  🛡️  Safety net for '{tool.get('name')}': {', '.join(modified)}")

# ============================================================================
# MAIN SCORING FUNCTION (For final scoring with multipliers)
# ============================================================================

def calculate_enhanced_score(tool: Dict) -> Dict:
    """
    Calculate enhanced score with confidence weighting
    This is for the FINAL scoring with multipliers (MODULE 3)
    """
    
    tool_name = tool.get("name", "Unknown")
    
    # Calculate base dimension scores (recalculate with enriched data)
    dimension_scores = {
        "buzz": calculate_buzz_score(tool),
        "vision": calculate_vision_score(tool),
        "ability": calculate_ability_score(tool),
        "credibility": calculate_credibility_score(tool),
        "adoption": calculate_adoption_score(tool)
    }
    
    # Calculate weighted base score
    base_score = sum(
        dimension_scores[dim] * DIMENSION_WEIGHTS[dim]
        for dim in DIMENSION_WEIGHTS
    )
    
    # Apply confidence multiplier
    confidence_level = tool.get("confidence_level", 50)
    confidence_multiplier = get_confidence_multiplier(confidence_level)
    
    # Apply maturity penalties/bonuses
    maturity_adjustment = calculate_maturity_adjustment(tool)
    
    # Apply source credibility
    source_multiplier = get_source_multiplier(tool.get("source", ""))
    
    # Calculate final score
    final_score = base_score * confidence_multiplier * source_multiplier + maturity_adjustment
    
    # Cap at 0-100
    final_score = max(0, min(100, final_score))
    
    # Prepare detailed breakdown
    result = {
        "final_score": round(final_score, 2),
        "base_score": round(base_score, 2),
        "dimension_scores": {k: round(v, 2) for k, v in dimension_scores.items()},
        "confidence_level": confidence_level,
        "confidence_multiplier": confidence_multiplier,
        "source_multiplier": source_multiplier,
        "maturity_adjustment": maturity_adjustment,
        "penalties": get_penalties(tool),
        "bonuses": get_bonuses(tool)
    }
    
    logger.debug(f"  📊 {tool_name}: {final_score:.1f} (base={base_score:.1f})")
    
    return result

# ============================================================================
# MULTIPLIERS & ADJUSTMENTS (Same as before)
# ============================================================================

CONFIDENCE_MULTIPLIERS = {"high": 1.0, "medium": 0.9, "low": 0.7}
MATURITY_BONUSES = {"production": 10, "beta": -5, "alpha": -10, "experimental": -15}
SOURCE_CREDIBILITY = {
    "curated": 1.2, "official_blog": 1.15, "techcrunch": 1.1,
    "venturebeat": 1.1, "product_hunt": 1.05, "github": 1.0,
    "reddit": 0.8, "hn": 0.85
}

def get_confidence_multiplier(confidence_level: int) -> float:
    if confidence_level >= 90:
        return CONFIDENCE_MULTIPLIERS["high"]
    elif confidence_level >= 70:
        return CONFIDENCE_MULTIPLIERS["medium"]
    else:
        return CONFIDENCE_MULTIPLIERS["low"]

def get_source_multiplier(source: str) -> float:
    source_lower = source.lower()
    for key, multiplier in SOURCE_CREDIBILITY.items():
        if key in source_lower:
            return multiplier
    return 1.0

def calculate_maturity_adjustment(tool: Dict) -> float:
    adjustment = 0.0
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    
    if "production" in text or tool.get("status") == "production":
        adjustment += MATURITY_BONUSES["production"]
    if re.search(r'\bbeta\b', text) or tool.get("status") == "beta":
        adjustment += MATURITY_BONUSES["beta"]
    if re.search(r'\balpha\b', text) or tool.get("status") == "alpha":
        adjustment += MATURITY_BONUSES["alpha"]
    if "experimental" in text or "prototype" in text:
        adjustment += MATURITY_BONUSES["experimental"]
    
    return adjustment

def get_penalties(tool: Dict) -> List[str]:
    penalties = []
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    
    if "beta" in text:
        penalties.append("Beta stage (-5 pts)")
    if "alpha" in text:
        penalties.append("Alpha stage (-10 pts)")
    if "experimental" in text:
        penalties.append("Experimental (-15 pts)")
    
    confidence = tool.get("confidence_level", 50)
    if confidence < 70:
        penalties.append(f"Low confidence ({confidence}) (0.7x)")
    
    source = tool.get("source", "").lower()
    if "reddit" in source:
        penalties.append("Noisy source (0.8x)")
    
    return penalties

def get_bonuses(tool: Dict) -> List[str]:
    bonuses = []
    
    if tool.get("status") == "production":
        bonuses.append("Production-ready (+10 pts)")
    
    confidence = tool.get("confidence_level", 50)
    if confidence >= 90:
        bonuses.append(f"High confidence ({confidence})")
    
    source = tool.get("source", "").lower()
    if "curated" in source:
        bonuses.append("Curated list (1.2x)")
    elif "techcrunch" in source or "venturebeat" in source:
        bonuses.append("Tech news source (1.1x)")
    
    if tool.get("trending"):
        bonuses.append("Trending (+10 buzz pts)")
    
    return bonuses

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def score_all_tools(tools: List[Dict]) -> List[Dict]:
    """Score all tools and add scoring metadata"""
    
    logger.info(f"\n📊 Scoring {len(tools)} tools with Enhanced Scoring v4...\n")
    
    for tool in tools:
        scoring_result = calculate_enhanced_score(tool)
        
        tool["final_score"] = scoring_result["final_score"]
        tool["base_score"] = scoring_result["base_score"]
        tool["scoring_breakdown"] = scoring_result["dimension_scores"]
        tool["scoring_metadata"] = {
            "confidence_multiplier": scoring_result["confidence_multiplier"],
            "source_multiplier": scoring_result["source_multiplier"],
            "maturity_adjustment": scoring_result["maturity_adjustment"],
            "penalties": scoring_result["penalties"],
            "bonuses": scoring_result["bonuses"]
        }
    
    # Sort by final score (descending)
    tools.sort(key=lambda x: x.get("final_score", 0), reverse=True)
    
    # Log top 10
    logger.info(f"\n🏆 TOP 10 TOOLS:")
    for i, tool in enumerate(tools[:10], 1):
        logger.info(f"   {i}. {tool.get('name')} - {tool.get('final_score', 0):.1f} pts")
    
    logger.info(f"\n✅ Scoring complete\n")
    
    return tools

# ============================================================================
# EXPORT
# ============================================================================

__all__ = [
    'calculate_buzz_score',
    'calculate_vision_score', 
    'calculate_ability_score',
    'calculate_credibility_score',
    'calculate_adoption_score',
    'apply_curated_safety_net',
    'calculate_enhanced_score',
    'score_all_tools',
]