#!/usr/bin/env python3
"""
INTELLIGENT SCORING MODULE
Based on actual Gartner dimensions:
- BUZZ_SCORE = market hype, social proof, trending
- VISION = market understanding, documentation quality, communication
- ABILITY = technical execution, code quality, maturity level
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_vision_from_source(title, description, source):
    """
    VISION = Does the project have clear vision & market understanding?
    
    Signals:
    - Clear problem statement in description
    - Use cases mentioned
    - Target audience defined
    - Documentation quality (inferred)
    """
    vision = 40  # Start conservative
    
    text = (title + " " + (description or "")).lower()
    
    # Documentation signals (from title/description length and clarity)
    desc_len = len(description or "")
    if desc_len > 200:
        vision += 15  # Good documentation
    elif desc_len > 100:
        vision += 10
    else:
        vision -= 5  # Poor documentation signal
    
    # Clarity keywords = good vision communication
    clarity_kws = ["designed for", "built to", "enables", "solves", "streamlines", "manages", "tracks", "provides"]
    clarity_count = sum(1 for kw in clarity_kws if kw in text)
    vision += min(clarity_count * 5, 20)
    
    # Source maturity impact on vision (curated > community)
    SOURCE_VISION_BOOST = {
        "product_hunt": 20,      # Curated = clear vision
        "github_trending": 15,   # Popular = likely has vision
        "hacker_news": 18,       # Tech-savvy audience = vision matters
        "reddit_MachineLearning": 12,  # Niche but informed
        "reddit_OpenAI": 14,
        "reddit_LanguageModels": 14,
    }
    source_name = source if isinstance(source, str) else source.get("source", "")
    vision += SOURCE_VISION_BOOST.get(source_name, 5)
    
    # Specific "vision" keywords
    vision_kws = ["framework", "platform", "architecture", "roadmap", "vision", "strategy"]
    vision_kw_count = sum(1 for kw in vision_kws if kw in text)
    vision += min(vision_kw_count * 3, 15)
    
    return min(100, max(20, vision))

def analyze_ability_from_source(title, description, source, language=None):
    """
    ABILITY = Can they actually execute and deliver?
    
    Signals:
    - Technical complexity indicators
    - Programming language maturity
    - Active development signals
    - Code quality indicators
    """
    ability = 45  # Start slightly higher for web discoveries
    
    text = (title + " " + (description or "")).lower()
    
    # Programming language quality impact
    if language:
        lang_lower = language.lower()
        LANG_ABILITY_SCORES = {
            "python": 75,        # Mature, great for AI/ML
            "typescript": 78,    # Type-safe, modern
            "rust": 82,          # High performance, reliability
            "javascript": 70,    # Web-first
            "go": 76,            # Concurrent, scalable
            "java": 74,          # Enterprise-ready
        }
        ability = LANG_ABILITY_SCORES.get(lang_lower, 55)
    
    # Active development signals (from description)
    active_kws = ["actively maintained", "updated", "new", "release", "version", "api", "sdk"]
    active_count = sum(1 for kw in active_kws if kw in text)
    ability += min(active_count * 4, 18)
    
    # Complexity indicators (higher = better engineering)
    complexity_kws = ["distributed", "scalable", "async", "multi-threaded", "cloud", "kubernetes", "microservices"]
    complexity_count = sum(1 for kw in complexity_kws if kw in text)
    ability += min(complexity_count * 3, 15)
    
    # Features = execution capability
    if "feature" in text or "supports" in text or "includes" in text:
        ability += 8
    
    # Source type impact on ability assessment
    SOURCE_ABILITY_BOOST = {
        "github_trending": 15,   # GitHub = proven execution
        "product_hunt": 12,      # SaaS = has to work
        "hacker_news": 12,       # Tech audience = vetted
        "reddit_MachineLearning": 5,  # Theory vs execution
    }
    source_name = source if isinstance(source, str) else source.get("source", "")
    ability += SOURCE_ABILITY_BOOST.get(source_name, 5)
    
    # Description length = better execution communication
    desc_len = len(description or "")
    if desc_len > 300:
        ability += 10
    elif desc_len > 150:
        ability += 5
    
    return min(100, max(25, ability))

def calculate_candidate_scores_v2(candidate, source):
    """
    INTELLIGENT scoring with independent Vision & Ability calculations
    
    Args:
        candidate: {name, description, url, ...}
        source: "product_hunt", "github_trending", "reddit_...", etc
    
    Returns:
        {buzz_score, vision, ability}
    """
    
    title = candidate.get("name", "")
    description = candidate.get("description", "")
    language = candidate.get("language", "")
    
    # ===== BUZZ SCORE (hype & trending) =====
    buzz = 50  # baseline
    
    # Source baseline buzz
    SOURCE_BUZZ = {
        "product_hunt": 72,
        "github_trending": 68,
        "hacker_news": 70,
        "reddit_MachineLearning": 60,
        "reddit_LanguageModels": 63,
        "reddit_OpenAI": 68,
        "reddit_ChatGPT": 62,
    }
    source_name = source if isinstance(source, str) else source.get("source", "")
    buzz = SOURCE_BUZZ.get(source_name, 50)
    
    # Trending keywords boost buzz
    trending_kws = ["new", "release", "launch", "breakthrough", "state-of-the-art", "trending", "#1"]
    trending_count = sum(1 for kw in trending_kws if kw.lower() in title.lower())
    buzz += min(trending_count * 3, 15)
    
    # AI specificity = buzz
    ai_kws = ["ai", "llm", "gpt", "ml", "neural", "transformer", "model"]
    ai_count = sum(1 for kw in ai_kws if kw.lower() in (title + " " + description).lower())
    buzz += min(ai_count * 2, 12)
    
    buzz = min(100, buzz)
    
    # ===== VISION (market understanding & clarity) =====
    vision = analyze_vision_from_source(title, description, source)
    
    # ===== ABILITY (execution capability) =====
    ability = analyze_ability_from_source(title, description, source, language)
    
    logger.debug(f"Scored '{title[:40]}': buzz={buzz}, vision={vision}, ability={ability}")
    
    return {
        "buzz_score": buzz,
        "vision": vision,
        "ability": ability
    }

# ===== TEST SCORING =====
if __name__ == "__main__":
    # Test case 1: GitHub open source
    test1 = {
        "name": "LLaMA: Open and Efficient Foundation Language Models",
        "description": "LLaMA is a collection of foundation language models released by Meta. Available in 7B, 13B, 33B, and 65B parameter sizes. Trained on 1-2 trillion tokens of public internet data.",
        "language": "Python",
    }
    scores1 = calculate_candidate_scores_v2(test1, "github_trending")
    print(f"Test 1 (GitHub LLaMA): {scores1}")
    
    # Test case 2: Product Hunt SaaS
    test2 = {
        "name": "Cursor - The AI-First Code Editor",
        "description": "Cursor is an AI-first code editor designed for pair programming with AI. Write, edit, and debug code with AI assistance. Built on VSCode foundations.",
        "language": "TypeScript",
    }
    scores2 = calculate_candidate_scores_v2(test2, "product_hunt")
    print(f"Test 2 (Product Hunt Cursor): {scores2}")
    
    # Test case 3: Reddit discussion
    test3 = {
        "name": "New Claude 3.5 Sonnet model shows 92% accuracy on MMLU",
        "description": "Anthropic released Claude 3.5 Sonnet today with impressive performance",
    }
    scores3 = calculate_candidate_scores_v2(test3, "reddit_LanguageModels")
    print(f"Test 3 (Reddit Claude): {scores3}")
