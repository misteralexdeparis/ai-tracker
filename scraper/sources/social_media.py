"""
Scraper for social media (Twitter, Discord)
"""

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_social_media(config):
    """Scrape social media for each tracked tool"""
    updates = []
    
    # Placeholder: Twitter/Discord scraping requires API keys
    # For MVP, we skip this or return empty
    logger.info("Social media scraping disabled (requires API keys)")
    
    return updates