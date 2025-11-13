"""
Enhanced Scoring System v4 - MODULE 3
Intelligent multi-dimensional scoring with confidence weighting

IMPROVEMENTS OVER v3:
1. Integrates confidence_level into final score
2. Dynamic weighting by tool maturity (startup vs established)
3. Penalizes "beta", "alpha", "experimental" tools
4. Rewards production-ready signals
5. Source-aware scoring (GitHub vs Product Hunt vs News)

SCORING DIMENSIONS:
- buzz (25%): Trending momentum
- vision (20%): Product clarity
- ability (20%): Technical maturity
- credibility (20%): Team/company trust
- adoption (15%): Organic usage

CONFIDENCE MULTIPLIER:
- High confidence (90+): 1.0x (no penalty)
- Medium confidence (70-89): 0.9x
- Low confidence (<70): 0.7x
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
    "buzz": 0.25,        # Trending momentum
    "vision": 0.20,      # Product clarity
    "ability": 0.20,     # Technical maturity
    "credibility": 0.20, # Team/company trust
    "adoption": 0.15     # Organic usage
}

# Confidence multipliers
CONFIDENCE_MULTIPLIERS = {
    "high": 1.0,      # 90+ confidence
    "medium": 0.9,    # 70-89 confidence
    "low": 0.7        # <70 confidence
}

# Maturity bonuses
MATURITY_BONUSES = {
    "production": 10,    # Production-ready
    "beta": -5,          # Beta stage
    "alpha": -10,        # Alpha stage
    "experimental": -15  # Experimental
}

# Source credibility multipliers
SOURCE_CREDIBILITY = {
    "curated": 1.2,           # Curated list (most trusted)
    "official_blog": 1.15,    # Company blog
    "techcrunch": 1.1,        # Tech news
    "venturebeat": 1.1,       # Tech news
    "product_hunt": 1.05,     # Community validated
    "github": 1.0,            # Standard
    "reddit": 0.8,            # Noisy
    "hn": 0.85                # Moderately noisy
}

# ============================================================================
# MAIN SCORING FUNCTION
# ============================================================================

def calculate_enhanced_score(tool: Dict) -> Dict:
    """
    Calculate enhanced score with confidence weighting
    
    Args:
        tool: Tool dict with all metadata
    
    Returns:
        Dict with:
        - final_score: Weighted score (0-100)
        - dimension_scores: Individual dimension scores
        - confidence_multiplier: Applied multiplier
        - penalties: List of applied penalties
        - bonuses: List of applied bonuses
    """
    
    tool_name = tool.get("name", "Unknown")
    
    # Calculate base dimension scores
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
    
    logger.debug(f"  📊 {tool_name}: {final_score:.1f} (base={base_score:.1f}, conf={confidence_multiplier}, source={source_multiplier})")
    
    return result

# ============================================================================
# DIMENSION CALCULATORS
# ============================================================================

def calculate_buzz_score(tool: Dict) -> float:
    """
    Calculate buzz/trending momentum (0-100)
    
    Factors:
    - GitHub stars growth
    - Product Hunt upvotes
    - Reddit/HN mentions
    - Social media velocity
    """
    
    score = 0.0
    
    # GitHub stars (0-40 points)
    github_stars = tool.get("github_stars", 0)
    if github_stars > 0:
        # Logarithmic scale
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
    
    return min(100, score)

def calculate_vision_score(tool: Dict) -> float:
    """
    Calculate product clarity/vision (0-100)
    
    Factors:
    - Clear description
    - Documentation quality
    - Demo availability
    - Use case clarity
    """
    
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
        features_count = len(features)
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
    
    return min(100, score)

def calculate_ability_score(tool: Dict) -> float:
    """
    Calculate technical maturity/ability (0-100)
    
    Factors:
    - Code quality (GitHub health)
    - Integration ecosystem
    - Uptime/reliability
    - API stability
    """
    
    score = 0.0
    
    # GitHub health (0-30 points)
    if tool.get("github_url"):
        # Active development
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
    
    return min(100, score)

def calculate_credibility_score(tool: Dict) -> float:
    """
    Calculate team/company credibility (0-100)
    
    Factors:
    - Team LinkedIn presence
    - Funding stage
    - Customer count/testimonials
    - Company age
    """
    
    score = 0.0
    
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
    """
    Calculate organic adoption/usage (0-100)
    
    Factors:
    - GitHub dependents
    - npm/pip downloads
    - App store reviews
    - Community size
    """
    
    score = 0.0
    
    # GitHub dependents (0-30 points)
    dependents = tool.get("github_dependents", 0)
    if dependents > 0:
        # Logarithmic scale
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
# MULTIPLIERS & ADJUSTMENTS
# ============================================================================

def get_confidence_multiplier(confidence_level: int) -> float:
    """Get confidence multiplier based on level"""
    
    if confidence_level >= 90:
        return CONFIDENCE_MULTIPLIERS["high"]
    elif confidence_level >= 70:
        return CONFIDENCE_MULTIPLIERS["medium"]
    else:
        return CONFIDENCE_MULTIPLIERS["low"]

def get_source_multiplier(source: str) -> float:
    """Get source credibility multiplier"""
    
    source_lower = source.lower()
    
    for key, multiplier in SOURCE_CREDIBILITY.items():
        if key in source_lower:
            return multiplier
    
    return 1.0  # Default (neutral)

def calculate_maturity_adjustment(tool: Dict) -> float:
    """Calculate maturity penalties/bonuses"""
    
    adjustment = 0.0
    
    # Check name/description for maturity signals
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
    """Get list of applied penalties"""
    
    penalties = []
    
    # Maturity penalties
    text = (tool.get("name", "") + " " + tool.get("description", "")).lower()
    
    if "beta" in text:
        penalties.append("Beta stage (-5 pts)")
    if "alpha" in text:
        penalties.append("Alpha stage (-10 pts)")
    if "experimental" in text:
        penalties.append("Experimental (-15 pts)")
    
    # Confidence penalty
    confidence = tool.get("confidence_level", 50)
    if confidence < 70:
        penalties.append(f"Low confidence ({confidence}) (0.7x multiplier)")
    
    # Source penalty
    source = tool.get("source", "").lower()
    if "reddit" in source:
        penalties.append("Noisy source (0.8x multiplier)")
    
    return penalties

def get_bonuses(tool: Dict) -> List[str]:
    """Get list of applied bonuses"""
    
    bonuses = []
    
    # Maturity bonus
    if tool.get("status") == "production":
        bonuses.append("Production-ready (+10 pts)")
    
    # Confidence bonus
    confidence = tool.get("confidence_level", 50)
    if confidence >= 90:
        bonuses.append(f"High confidence ({confidence})")
    
    # Source bonus
    source = tool.get("source", "").lower()
    if "curated" in source:
        bonuses.append("Curated list (1.2x multiplier)")
    elif "techcrunch" in source or "venturebeat" in source:
        bonuses.append("Tech news source (1.1x multiplier)")
    
    # Trending bonus
    if tool.get("trending"):
        bonuses.append("Trending (+10 buzz pts)")
    
    return bonuses

# ============================================================================
# BATCH PROCESSING
# ============================================================================

def score_all_tools(tools: List[Dict]) -> List[Dict]:
    """
    Score all tools and add scoring metadata
    
    Args:
        tools: List of tool dicts
    
    Returns:
        List of tools with added scoring fields
    """
    
    logger.info(f"\n📊 Scoring {len(tools)} tools with Enhanced Scoring v4...\n")
    
    for tool in tools:
        scoring_result = calculate_enhanced_score(tool)
        
        # Add scoring metadata to tool
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
    'calculate_enhanced_score',
    'score_all_tools',
]
