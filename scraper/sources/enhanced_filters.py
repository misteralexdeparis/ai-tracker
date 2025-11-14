#!/usr/bin/env python3
"""
Enhanced Filtering Module - FIXED VERSION
Fix: Curated tools (no source field) ALWAYS pass
Noise rejection + confidence scoring
"""

import logging
import re
from datetime import datetime, timedelta
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== HARD REQUIREMENTS (Must pass ALL) =====
HARD_REQUIREMENTS = {
    "must_have_url": True,
    "must_have_name": True,
    "min_name_length": 3,
}

# ===== AUTO-REJECT RULES (Reject if ANY match) =====
AUTO_REJECT_PATTERNS = [
    r"(?i)(paper|survey|thesis|dissertation|arxiv|preprint)",
    r"(?i)(seeking feedback|seeking collaborators|feedback wanted|WIP|work in progress)",
    r"(?i)(\[alpha\]|\[beta\]|\[experimental\])",
    r"(?i)(hobby project|side project|personal project|not maintained)",
]

AUTO_REJECT_INDICATORS = {
    "is_archived": True,
    "url_contains_draft": True,
    "domain_age_days": 14,
}

# ===== CONFIDENCE SCORING TIERS =====
CONFIDENCE_TIERS = {
    "curated_list": 100,
    "official_blog": 95,
    "product_hunt_500plus": 85,
    "github_trending_1k": 80,
    "techcrunch_article": 75,
    "reddit_100plus_upvotes": 40,
    "hn_showhn_under50": 30
}

def check_hard_requirements(candidate):
    """Check if candidate meets hard requirements"""
    
    # Must have URL
    url = candidate.get("url") or candidate.get("official_url")
    if not url:
        return False, "Missing URL"
    
    # Must have name
    name = candidate.get("name", "").strip()
    if not name or len(name) < HARD_REQUIREMENTS["min_name_length"]:
        return False, "Invalid name"
    
    return True, None

def check_auto_reject_rules(candidate):
    """Apply auto-reject rules"""
    
    title = candidate.get("name", "")
    description = candidate.get("description", "")
    url = candidate.get("url", "") or candidate.get("official_url", "")
    source = candidate.get("source", "")
    
    # Check title/description patterns
    text = (title + " " + description).lower()
    for pattern in AUTO_REJECT_PATTERNS:
        if re.search(pattern, text):
            return True, f"Matched pattern: {pattern}"
    
    # Check URL indicators
    if url:
        if "/archive/" in url or "/draft/" in url:
            return True, "URL contains draft/archive"
        
        if "github.com" not in url:
            if not description or len(description) < 20:
                return True, "Insufficient description for non-GitHub"
    
    # Check source quality
    if source in ["reddit", "hn"] and candidate.get("buzz_score", 0) < 30:
        return True, "Low buzz score from noisy source"
    
    return False, None

def calculate_confidence_level(candidate):
    """Assign confidence tier based on source"""
    
    source = candidate.get("source", "").lower()
    
    # Check if this is a curated tool (no source field or explicitly marked)
    if not source or source == "not_set":
        # If it has tracking_versions field, it's from curated_ai_tools.json
        if candidate.get("tracking_versions"):
            return CONFIDENCE_TIERS["curated_list"]
    
    if "curated" in source:
        return CONFIDENCE_TIERS["curated_list"]
    elif "blog" in source or source in ["openai_blog", "anthropic_blog", "google_ai", "meta_ai"]:
        return CONFIDENCE_TIERS["official_blog"]
    elif "product_hunt" in source:
        upvotes = candidate.get("upvotes", 0)
        return CONFIDENCE_TIERS["product_hunt_500plus"] if upvotes >= 500 else 60
    elif "github" in source:
        stars = candidate.get("github_stars", 0)
        return CONFIDENCE_TIERS["github_trending_1k"] if stars >= 1000 else 70
    elif "techcrunch" in source or "venturebeat" in source:
        return CONFIDENCE_TIERS["techcrunch_article"]
    elif "reddit" in source:
        upvotes = candidate.get("upvotes", 0)
        return CONFIDENCE_TIERS["reddit_100plus_upvotes"] if upvotes >= 100 else 20
    elif "hn" in source or "hacker_news" in source:
        points = candidate.get("points", 0)
        return CONFIDENCE_TIERS["hn_showhn_under50"] if points < 50 else 50
    else:
        return 50

def filter_candidates_enhanced(candidates, confidence_threshold=70):
    """
    Enhanced filtering pipeline
    KEY FIX: Curated tools are identified by tracking_versions field (from curated_ai_tools.json)
    They ALWAYS pass, no threshold applied
    """

    filtered = []
    rejected = {"hard_req": 0, "auto_reject": 0, "confidence": 0, "curated_pass": 0}

    logger.info(f"\n🔍 Enhanced filtering pipeline (confidence threshold: {confidence_threshold})...\n")

    for candidate in candidates:
        # ✨ SPECIAL: Curated tools ALWAYS pass
        # Detection: They have tracking_versions field OR source is curated/curated_list
        is_curated = (
            candidate.get("tracking_versions") or
            candidate.get("source") in ["curated", "curated_list"]
        )

        if is_curated:
            # Mark it as curated for reference
            if not candidate.get("source"):
                candidate["source"] = "curated_list"
            # Set high confidence for curated tools
            candidate["confidence_level"] = 100
            filtered.append(candidate)
            rejected["curated_pass"] += 1
            logger.debug(f"  ✅ CURATED (auto-pass): {candidate.get('name')}")
            continue
        
        # Step 1: Hard requirements
        passed, reason = check_hard_requirements(candidate)
        if not passed:
            rejected["hard_req"] += 1
            logger.debug(f"  ❌ Rejected (hard req): {candidate.get('name', 'Unknown')} - {reason}")
            continue
        
        # Step 2: Auto-reject rules
        should_reject, reason = check_auto_reject_rules(candidate)
        if should_reject:
            rejected["auto_reject"] += 1
            logger.debug(f"  ❌ Rejected (noise): {candidate.get('name', 'Unknown')} - {reason}")
            continue
        
        # Step 3: Confidence scoring
        confidence = calculate_confidence_level(candidate)
        candidate["confidence_level"] = confidence
        
        if confidence < confidence_threshold:
            rejected["confidence"] += 1
            logger.debug(f"  ⚠️  Low confidence ({confidence}): {candidate.get('name', 'Unknown')}")
            continue
        
        # ✅ Passed all filters
        filtered.append(candidate)
        logger.debug(f"  ✅ Passed: {candidate.get('name', 'Unknown')} (confidence={confidence})")
    
    logger.info(f"\n📊 Filtering Summary:")
    logger.info(f" - Input: {len(candidates)}")
    logger.info(f" - Curated (auto-pass): {rejected['curated_pass']}")
    logger.info(f" - Rejected (hard req): {rejected['hard_req']}")
    logger.info(f" - Rejected (noise): {rejected['auto_reject']}")
    logger.info(f" - Rejected (low confidence): {rejected['confidence']}")
    logger.info(f" - Output: {len(filtered)} qualified candidates\n")
    
    return filtered