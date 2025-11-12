#!/usr/bin/env python3
"""
QUALITY FILTER - Eliminate noise and WIP projects
Only keep REAL commercial AI tools with proper online presence
"""

import requests
import logging
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

def has_valid_website(url):
    """Check if URL is accessible and returns valid content"""
    if not url:
        return False
    
    try:
        response = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        # 200-299 = success, 301-302 = redirect OK
        return response.status_code < 400
    except:
        return False

def is_commercial_product(candidate):
    """
    Determine if candidate is a REAL commercial AI product
    vs. WIP/hobby/discussion-only project
    """
    
    name = candidate.get("name", "").lower()
    description = candidate.get("description", "").lower()
    source = candidate.get("source", "").lower()
    url = candidate.get("url", "")
    official_url = candidate.get("official_url", "")
    
    # ===== RED FLAGS (Filter OUT) =====
    RED_FLAGS = [
        "wip",  # Work In Progress
        "alpha",  # Too early
        "beta",  # Still testing
        "poc",  # Proof of concept
        "prototype",  # Not ready
        "experimental",  # Experimental only
        "personal project",  # Hobby
        "hobby",
        "side project",
        "research",
        "academic",
        "course",
        "tutorial",
        "learning",
        "test",
        "demo only",
        "coming soon",
        "not ready",
        "early stage",
        "just started",
    ]
    
    red_flag_count = sum(1 for flag in RED_FLAGS if flag in description or flag in name)
    
    if red_flag_count >= 1:
        logger.debug(f"🚩 REJECTED {name}: Red flag detected")
        return False
    
    # ===== NEGATIVE KEYWORDS (Lower confidence) =====
    NEGATIVE_KWS = [
        "github issue",
        "discussion",
        "question",
        "fork",
        "clone",
        "wrapper",
        "client",
    ]
    
    negative_count = sum(1 for kw in NEGATIVE_KWS if kw in description)
    
    # ===== POSITIVE SIGNALS (Must have at least ONE) =====
    POSITIVE_SIGNALS = {
        "official_website": official_url and has_valid_website(official_url),
        "commercial_site": source == "product_hunt",
        "established_repo": source == "github_trending" and description and len(description) > 100,
        "company_email": any(domain in description for domain in ["@anthropic", "@openai", "@meta", "@google"]),
        "pricing_mentioned": "pricing" in description or "price" in description or "$" in description,
        "team_mentioned": "team" in description or "by " in description,
    }
    
    positive_signals = sum(1 for sig, has_it in POSITIVE_SIGNALS.items() if has_it)
    
    # ===== DECISION LOGIC =====
    
    # GitHub repos need extra credibility signals
    if source == "github_trending":
        if negative_count > 0:
            logger.debug(f"🚩 REJECTED {name}: GitHub repo with negative keywords")
            return False
        
        # Must have real description + URL
        if not description or len(description) < 50:
            logger.debug(f"🚩 REJECTED {name}: GitHub repo lacks description")
            return False
        
        if not url:
            logger.debug(f"🚩 REJECTED {name}: GitHub repo missing URL")
            return False
    
    # Product Hunt items are usually good (curated)
    if source == "product_hunt":
        # Just check for obvious WIP signals
        if red_flag_count >= 1:
            logger.debug(f"🚩 REJECTED {name}: PH item is WIP")
            return False
        return True  # PH is curated = trust it
    
    # Reddit/HN discussions need official URL
    if "reddit" in source or source == "hacker_news":
        if not official_url or not has_valid_website(official_url):
            logger.debug(f"🚩 REJECTED {name}: No official website found")
            return False
        
        # Also check positive signals
        if positive_signals < 1:
            logger.debug(f"🚩 REJECTED {name}: Reddit/HN item lacks credibility signals")
            return False
    
    # ===== FINAL CHECK: Minimum credibility score =====
    credibility_score = positive_signals - (negative_count * 2)
    
    if credibility_score < 0:
        logger.debug(f"🚩 REJECTED {name}: Low credibility score ({credibility_score})")
        return False
    
    logger.info(f"✅ APPROVED {name} (score: {credibility_score})")
    return True

def filter_candidates(candidates):
    """Filter list of candidates, keeping only commercial products"""
    
    logger.info(f"\n🔍 QUALITY FILTERING: {len(candidates)} candidates input\n")
    
    qualified = []
    rejected = []
    
    for candidate in candidates:
        if is_commercial_product(candidate):
            qualified.append(candidate)
        else:
            rejected.append(candidate.get("name", "Unknown"))
    
    logger.info(f"\n📊 FILTERING RESULTS:")
    logger.info(f"   ✅ Approved: {len(qualified)}")
    logger.info(f"   ❌ Rejected: {len(rejected)}")
    
    if rejected:
        logger.info(f"\n   Rejected items:")
        for name in rejected[:10]:  # Show first 10
            logger.info(f"      - {name}")
        if len(rejected) > 10:
            logger.info(f"      ... and {len(rejected) - 10} more")
    
    logger.info(f"\n")
    
    return qualified
