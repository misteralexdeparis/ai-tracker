"""
Smart Enrichment Manager - MODULE 2
Intelligent enrichment strategy to minimize Perplexity API costs

COST OPTIMIZATION STRATEGIES:
1. Cache-based enrichment (avoid re-enriching unchanged tools)
2. Selective enrichment (only enrich what's missing/outdated)
3. Free scrapers for curated tools (GitHub, official sites)
4. Perplexity only for new/ambiguous tools
5. Batch optimization (group similar requests)

EXPECTED SAVINGS: 70-80% reduction in API costs
"""

import logging
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTS
# ============================================================================

CACHE_DIR = "cache"
CACHE_TTL_DAYS = 7  # Cache enrichment for 7 days
GITHUB_API_BASE = "https://api.github.com"
REQUEST_TIMEOUT = 10
USER_AGENT = "AI-Tools-Tracker/1.0"

# Fields that can be scraped for free (no Perplexity needed)
FREE_SCRAPABLE_FIELDS = {
    "description",      # From GitHub/homepage
    "github_stars",     # From GitHub API
    "github_url",       # Extract from URLs
    "founding_year",    # Often on homepage/about page
    "status",           # From GitHub activity
}

# Fields that require Perplexity (complex analysis)
PERPLEXITY_REQUIRED_FIELDS = {
    "pricing",          # Requires understanding of pricing models
    "key_features",     # Requires analysis and summarization
    "limitations",      # Requires critical analysis
    "use_cases",        # Requires domain understanding
    "changelog",        # Requires synthesis
}

# ============================================================================
# ENRICHMENT DECISION ENGINE
# ============================================================================

def smart_enrich_tools(
    tools: List[Dict],
    existing_tools: List[Dict],
    perplexity_api_key: Optional[str] = None
) -> Tuple[List[Dict], Dict]:
    """
    Smart enrichment with cost optimization
    
    Decision tree:
    1. Check if tool already enriched (cache hit)
    2. Try free scrapers first (GitHub, homepage)
    3. Only use Perplexity if necessary
    
    Args:
        tools: New/updated tools to enrich
        existing_tools: Previously enriched tools (for cache)
        perplexity_api_key: API key for Perplexity
    
    Returns:
        Tuple of (enriched_tools, stats)
    """
    
    logger.info(f"\n🧠 Smart Enrichment Manager - Processing {len(tools)} tools\n")
    
    # Initialize stats
    stats = {
        "total_tools": len(tools),
        "cache_hits": 0,
        "free_enriched": 0,
        "perplexity_needed": 0,
        "perplexity_used": 0,
        "fully_enriched": 0,
        "cost_saved": 0.0,
        "cost_spent": 0.0
    }
    
    # Create cache index from existing tools
    cache_index = _build_cache_index(existing_tools)
    
    enriched_tools = []
    perplexity_batch = []
    
    for tool in tools:
        tool_name = tool.get("name", "Unknown")
        tool_url = tool.get("url", "")

        # Check if this is a curated tool
        is_curated = (
            tool.get("tracking_versions") or
            tool.get("source") in ["curated", "curated_list"]
        )

        # STEP 1: Check cache (existing enrichment)
        cache_key = _generate_cache_key(tool_name, tool_url)
        cached_enrichment = cache_index.get(cache_key)

        if cached_enrichment and _is_cache_valid(cached_enrichment):
            logger.info(f"  💾 Cache HIT: {tool_name}")
            # Merge cached data
            tool.update(cached_enrichment.get("enrichment", {}))
            enriched_tools.append(tool)
            stats["cache_hits"] += 1
            stats["cost_saved"] += 0.0008  # Saved one API call
            continue

        # STEP 2: Try free enrichment (scrapers)
        logger.info(f"  🔍 Free scraping: {tool_name}")
        free_enrichment = _enrich_with_free_scrapers(tool)

        if free_enrichment:
            tool.update(free_enrichment)
            stats["free_enriched"] += 1
            stats["cost_saved"] += 0.0008

        # STEP 3: Check if Perplexity needed
        missing_critical_fields = _get_missing_critical_fields(tool)

        # PRIORITY: Curated tools ALWAYS get Perplexity enrichment for quality scoring
        if missing_critical_fields or is_curated:
            if is_curated:
                logger.info(f"  ⭐ CURATED - Force Perplexity: {tool_name}")
            else:
                logger.info(f"  🤖 Needs Perplexity: {tool_name} (missing: {', '.join(missing_critical_fields)})")
            perplexity_batch.append({
                "tool": tool,
                "missing_fields": missing_critical_fields,
                "is_curated": is_curated
            })
            stats["perplexity_needed"] += 1
        else:
            logger.info(f"  ✅ Fully enriched (free): {tool_name}")
            enriched_tools.append(tool)
            stats["fully_enriched"] += 1
    
    # STEP 4: Batch Perplexity enrichment (if needed and API key available)
    if perplexity_batch and perplexity_api_key:
        logger.info(f"\n🤖 Calling Perplexity for {len(perplexity_batch)} tools...")
        
        from enrichment.perplexity_analyzer import enrich_with_perplexity
        
        # Extract tools from batch
        tools_to_enrich = [item["tool"] for item in perplexity_batch]
        
        # Call Perplexity
        perplexity_enriched = enrich_with_perplexity(tools_to_enrich)
        
        enriched_tools.extend(perplexity_enriched)
        stats["perplexity_used"] = len(perplexity_batch)
        stats["cost_spent"] = len(perplexity_batch) * 0.0008
    
    elif perplexity_batch and not perplexity_api_key:
        logger.warning(f"⚠️  {len(perplexity_batch)} tools need Perplexity but no API key provided")
        # Add tools without full enrichment
        enriched_tools.extend([item["tool"] for item in perplexity_batch])
    
    # Update cache
    _update_cache(enriched_tools)
    
    # Log summary
    _log_enrichment_summary(stats)
    
    return enriched_tools, stats

# ============================================================================
# FREE ENRICHMENT SCRAPERS
# ============================================================================

def _enrich_with_free_scrapers(tool: Dict) -> Dict:
    """
    Try to enrich tool using free sources (GitHub, homepage)
    
    Returns dict of enriched fields
    """
    
    enrichment = {}
    tool_name = tool.get("name", "")
    
    # Try GitHub scraping (if GitHub URL available)
    github_url = tool.get("github_url") or _extract_github_url(tool.get("url", ""))
    if github_url:
        github_data = _scrape_github_data(github_url, tool_name)
        enrichment.update(github_data)
    
    # Try homepage scraping
    homepage_url = tool.get("url") or tool.get("official_url")
    if homepage_url:
        homepage_data = _scrape_homepage_data(homepage_url, tool_name)
        enrichment.update(homepage_data)
    
    return enrichment

def _scrape_github_data(github_url: str, tool_name: str) -> Dict:
    """Scrape GitHub for free metadata"""
    
    enrichment = {}
    
    try:
        # Extract owner/repo
        match = re.search(r'github\.com/([^/]+)/([^/]+)', github_url)
        if not match:
            return enrichment
        
        owner, repo = match.groups()
        repo = repo.rstrip('/')
        
        # Call GitHub API
        api_url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}"
        response = requests.get(
            api_url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract useful fields
            if not enrichment.get("description"):
                enrichment["description"] = data.get("description", "")
            
            enrichment["github_stars"] = data.get("stargazers_count", 0)
            enrichment["github_url"] = github_url
            
            # Determine status from activity
            updated_at = data.get("updated_at", "")
            if updated_at:
                from dateutil import parser
                last_update = parser.parse(updated_at)
                days_since_update = (datetime.now(last_update.tzinfo) - last_update).days
                
                if days_since_update < 30:
                    enrichment["status"] = "active"
                elif days_since_update < 180:
                    enrichment["status"] = "maintained"
                else:
                    enrichment["status"] = "stale"
            
            # Extract founding year from created_at
            created_at = data.get("created_at", "")
            if created_at and not enrichment.get("founding_year"):
                from dateutil import parser
                created_date = parser.parse(created_at)
                enrichment["founding_year"] = created_date.year
            
            logger.debug(f"    GitHub: {len(enrichment)} fields scraped")
        
    except Exception as e:
        logger.debug(f"GitHub scraping failed for {tool_name}: {e}")
    
    return enrichment

def _scrape_homepage_data(url: str, tool_name: str) -> Dict:
    """Scrape homepage for free metadata"""
    
    enrichment = {}
    
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            return enrichment
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to extract description from meta tags
        if not enrichment.get("description"):
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if not meta_desc:
                meta_desc = soup.find("meta", property="og:description")
            
            if meta_desc:
                desc = meta_desc.get("content", "").strip()
                if len(desc) > 20:
                    enrichment["description"] = desc
        
        # Try to find founding year (common patterns)
        if not enrichment.get("founding_year"):
            text = soup.get_text()
            year_patterns = [
                r'(?:founded|established|launched|since)\s+(?:in\s+)?(\d{4})',
                r'©\s*(\d{4})',
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    year = int(match.group(1))
                    if 1990 <= year <= datetime.now().year:
                        enrichment["founding_year"] = year
                        break
        
        logger.debug(f"    Homepage: {len(enrichment)} fields scraped")
    
    except Exception as e:
        logger.debug(f"Homepage scraping failed for {tool_name}: {e}")
    
    return enrichment

# ============================================================================
# CACHE MANAGEMENT
# ============================================================================

def _build_cache_index(existing_tools: List[Dict]) -> Dict:
    """Build cache index from existing tools"""
    
    cache = {}
    
    for tool in existing_tools:
        tool_name = tool.get("name", "")
        tool_url = tool.get("url", "")
        
        if not tool_name:
            continue
        
        cache_key = _generate_cache_key(tool_name, tool_url)
        
        cache[cache_key] = {
            "tool_name": tool_name,
            "enrichment": tool,
            "cached_at": tool.get("last_enriched", datetime.now().isoformat()),
            "cache_key": cache_key
        }
    
    return cache

def _generate_cache_key(tool_name: str, tool_url: str) -> str:
    """Generate unique cache key for tool"""
    
    # Normalize name (lowercase, no spaces)
    normalized_name = tool_name.lower().replace(" ", "").replace("-", "")
    
    # Use name + URL hash for uniqueness
    url_hash = hashlib.md5(tool_url.encode()).hexdigest()[:8] if tool_url else "nourl"
    
    return f"{normalized_name}_{url_hash}"

def _is_cache_valid(cached_data: Dict) -> bool:
    """Check if cached enrichment is still valid"""
    
    try:
        cached_at = datetime.fromisoformat(cached_data.get("cached_at", ""))
        age_days = (datetime.now() - cached_at).days
        
        return age_days < CACHE_TTL_DAYS
    
    except Exception:
        return False

def _update_cache(enriched_tools: List[Dict]) -> None:
    """Update cache file with newly enriched tools"""
    
    try:
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        cache_file = os.path.join(CACHE_DIR, "enrichment_cache.json")
        
        # Load existing cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
        else:
            cache_data = {}
        
        # Update with new enrichments
        for tool in enriched_tools:
            cache_key = _generate_cache_key(
                tool.get("name", ""),
                tool.get("url", "")
            )
            
            cache_data[cache_key] = {
                "tool_name": tool.get("name"),
                "enrichment": tool,
                "cached_at": datetime.now().isoformat(),
                "cache_key": cache_key
            }
        
        # Save cache
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.debug(f"✅ Cache updated: {len(cache_data)} entries")
    
    except Exception as e:
        logger.warning(f"Failed to update cache: {e}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _get_missing_critical_fields(tool: Dict) -> List[str]:
    """Determine which critical fields are missing"""
    
    missing = []
    
    # Check Perplexity-required fields
    for field in PERPLEXITY_REQUIRED_FIELDS:
        value = tool.get(field)
        
        # Consider field missing if:
        # - Not present
        # - Empty string
        # - Empty list
        # - Placeholder values
        if not value or \
           (isinstance(value, str) and len(value) < 5) or \
           (isinstance(value, list) and len(value) == 0) or \
           value in ["Unknown", "N/A", "TBD"]:
            missing.append(field)
    
    return missing

def _extract_github_url(url: str) -> Optional[str]:
    """Extract GitHub URL if present"""
    if 'github.com' in url:
        return url
    return None

def _log_enrichment_summary(stats: Dict) -> None:
    """Log enrichment summary with cost analysis"""
    
    logger.info(f"\n{'='*70}")
    logger.info(f"💰 SMART ENRICHMENT SUMMARY")
    logger.info(f"{'='*70}")
    logger.info(f"\n📊 Statistics:")
    logger.info(f"   Total tools processed: {stats['total_tools']}")
    logger.info(f"   Cache hits: {stats['cache_hits']} ({stats['cache_hits']/stats['total_tools']*100:.1f}%)")
    logger.info(f"   Free enriched: {stats['free_enriched']} ({stats['free_enriched']/stats['total_tools']*100:.1f}%)")
    logger.info(f"   Perplexity needed: {stats['perplexity_needed']}")
    logger.info(f"   Perplexity used: {stats['perplexity_used']}")
    
    logger.info(f"\n💰 Cost Analysis:")
    logger.info(f"   Cost saved (cache + free): ${stats['cost_saved']:.4f}")
    logger.info(f"   Cost spent (Perplexity): ${stats['cost_spent']:.4f}")
    
    total_potential_cost = stats['total_tools'] * 0.0008
    savings_percent = (stats['cost_saved'] / total_potential_cost * 100) if total_potential_cost > 0 else 0
    
    logger.info(f"   Total potential cost: ${total_potential_cost:.4f}")
    logger.info(f"   Savings: {savings_percent:.1f}%")
    logger.info(f"\n{'='*70}\n")

# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def should_enrich_tool(tool: Dict, existing_tools: List[Dict]) -> bool:
    """
    Decide if a tool needs enrichment
    
    Use this in your main.py to filter before calling enrich
    """
    
    # Check if tool exists in existing_tools
    tool_name = tool.get("name", "")
    existing = next((t for t in existing_tools if t.get("name") == tool_name), None)
    
    if not existing:
        # New tool, needs enrichment
        return True
    
    # Check if existing enrichment is stale
    last_enriched = existing.get("last_enriched")
    if last_enriched:
        try:
            enriched_date = datetime.fromisoformat(last_enriched)
            age_days = (datetime.now() - enriched_date).days
            
            if age_days > CACHE_TTL_DAYS:
                return True
        except Exception:
            pass
    
    # Check if critical fields are missing
    missing_fields = _get_missing_critical_fields(existing)
    
    return len(missing_fields) > 0

# ============================================================================
# MAIN EXPORT
# ============================================================================

__all__ = [
    'smart_enrich_tools',
    'should_enrich_tool',
]
