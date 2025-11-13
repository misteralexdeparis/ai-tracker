#!/usr/bin/env python3
"""
Smart Scoring v3 - PHASE 1
5-Dimensional Scoring Model (Claude recommendation)
buzz (0.25) + vision (0.20) + ability (0.20) + credibility (0.20) + adoption (0.15)
"""

import logging
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_buzz_score(candidate, source):
    """
    Buzz = trending momentum
    - GitHub stars (7-day growth)
    - Product Hunt upvotes
    - Social mentions (Reddit, Twitter)
    - Search trends
    """
    
    buzz = 0
    
    # GitHub signals
    if source == "github_trending":
        stars = candidate.get("github_stars", 0)
        # 1000 stars = 50 pts, 5000 stars = 80 pts, 10000+ = 100 pts
        if stars >= 10000:
            buzz = max(buzz, 100)
        elif stars >= 5000:
            buzz = max(buzz, 80)
        elif stars >= 1000:
            buzz = max(buzz, 60)
        elif stars >= 500:
            buzz = max(buzz, 40)
    
    # Product Hunt signals
    elif source == "product_hunt":
        upvotes = candidate.get("upvotes", 0)
        buzz = min(100, (upvotes / 500) * 100)  # 500 upvotes = 100 pts
    
    # Reddit/HN community validation
    elif "reddit" in source or "hn" in source:
        community_score = candidate.get("points", candidate.get("upvotes", 0))
        buzz = min(100, (community_score / 100) * 100)  # 100 points = 100 pts
    
    # News source (TechCrunch, VentureBeat)
    elif "techcrunch" in source or "venturebeat" in source:
        buzz = 75  # News is inherently buzzy
    
    # Official/company announcement
    elif "blog" in source:
        buzz = 80  # Company announcements = high buzz
    
    # Default/other
    else:
        buzz = 50
    
    return max(0, min(100, buzz))

def calculate_vision_score(candidate, source):
    """
    Vision = product clarity
    - Clear use case
    - Documentation quality
    - Demo/video availability
    - Pricing clarity
    """
    
    vision = 50  # Default baseline
    
    # Has description?
    description = candidate.get("description", "")
    if len(description) > 100:
        vision += 15
    elif len(description) > 50:
        vision += 10
    
    # Has documentation?
    if candidate.get("docs_url"):
        vision += 20
    
    # Has demo/video?
    if candidate.get("has_demo_video") or candidate.get("has_demo"):
        vision += 15
    
    # Has pricing page?
    if candidate.get("has_pricing_page"):
        vision += 10
    
    # Company/official source clarity
    if source == "official_blog" or "blog" in source:
        vision = min(100, vision + 15)
    
    return max(0, min(100, vision))

def calculate_ability_score(candidate, source):
    """
    Ability = technical maturity
    - Code quality (GitHub health)
    - Last commit recency
    - Integration ecosystem
    - Version number (v1.0+ vs v0.x)
    """
    
    ability = 50  # Default baseline
    
    # GitHub signals
    if source == "github_trending":
        # Last commit recency
        last_commit_days = candidate.get("days_since_last_commit", 999)
        if last_commit_days < 7:
            ability += 20
        elif last_commit_days < 30:
            ability += 15
        elif last_commit_days < 90:
            ability += 10
        else:
            ability -= 20  # Abandoned = lower ability
        
        # Has documentation site?
        if candidate.get("has_docs"):
            ability += 15
    
    # Version maturity
    version = candidate.get("last_known_version", "0.0.1")
    try:
        major_version = int(version.split(".")[0])
        if major_version >= 2:
            ability += 20
        elif major_version >= 1:
            ability += 10
        # v0.x stays at baseline or lower
    except:
        pass
    
    # API/SDK availability
    if candidate.get("has_api_docs") or candidate.get("has_sdk"):
        ability += 15
    
    # Integration ecosystem
    integrations = candidate.get("integration_count", 0)
    if integrations > 0:
        ability += min(15, integrations * 2)
    
    return max(0, min(100, ability))

def calculate_credibility_score(candidate, source):
    """
    Credibility = team/company trust
    - Team LinkedIn presence
    - Funding stage
    - Company verification
    - Customer testimonials
    """
    
    credibility = 50  # Default baseline
    
    # Company-backed signals
    if candidate.get("has_linkedin_company"):
        credibility += 25
    
    if candidate.get("publisher"):
        credibility += 10
    
    # Funding stage
    funding_stage = candidate.get("funding_stage", "")
    if "series" in funding_stage.lower():
        if "b" in funding_stage.lower() or "c" in funding_stage.lower():
            credibility += 25
        elif "a" in funding_stage.lower():
            credibility += 15
    elif "seed" in funding_stage.lower():
        credibility += 10
    
    # Customer testimonials/case studies
    if candidate.get("has_testimonials") or candidate.get("case_studies_count", 0) > 0:
        credibility += 15
    
    # Official company source = automatic credibility
    if source == "official_blog" or "blog" in source:
        credibility = min(100, credibility + 20)
    
    return max(0, min(100, credibility))

def calculate_adoption_score(candidate, source):
    """
    Adoption = organic usage signals
    - GitHub dependents/forks
    - npm downloads (for JS tools)
    - App Store ratings
    - Public usage count
    """
    
    adoption = 40  # Lower default (harder to measure)
    
    # GitHub dependents
    dependents = candidate.get("github_dependents", 0)
    if dependents > 0:
        adoption += min(40, dependents * 2)
    
    # npm downloads
    npm_downloads = candidate.get("npm_weekly_downloads", 0)
    if npm_downloads > 0:
        adoption += min(40, (npm_downloads / 1000) * 10)
    
    # App Store ratings
    app_reviews = candidate.get("app_store_reviews", 0)
    if app_reviews > 100:
        adoption += 30
    elif app_reviews > 10:
        adoption += 15
    
    # Public usage indicators
    if candidate.get("public_companies_using", 0) > 0:
        adoption += 20
    
    return max(0, min(100, adoption))

def calculate_candidate_scores_v3(candidate, source):
    """
    Calculate 5-dimensional score for a candidate
    Returns: dict with individual scores + final weighted score
    """
    
    buzz = calculate_buzz_score(candidate, source)
    vision = calculate_vision_score(candidate, source)
    ability = calculate_ability_score(candidate, source)
    credibility = calculate_credibility_score(candidate, source)
    adoption = calculate_adoption_score(candidate, source)
    
    # Weighted final score
    final_score = (
        buzz * 0.25 +
        vision * 0.20 +
        ability * 0.20 +
        credibility * 0.20 +
        adoption * 0.15
    )
    
    return {
        "buzz_score": round(buzz, 1),
        "vision": round(vision, 1),
        "ability": round(ability, 1),
        "credibility": round(credibility, 1),
        "adoption": round(adoption, 1),
        "final_score": round(final_score, 1),
        "source": source
    }
