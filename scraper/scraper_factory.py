"""
Focused scraper factory for GM Collin and YK Canada.
"""

from typing import Dict, Type, Optional
import sys
import os

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'common'))
sys.path.append(os.path.join(current_dir, 'websites'))

from common.base_scraper import BaseScraper
from websites.gmcollin_scraper import GMCollinScraper
from websites.ykcanada_scraper import YKCanadaScraper


class ScraperFactory:
    """Factory for creating GM Collin and YK Canada scrapers."""

    # Registry of available scrapers
    _scrapers: Dict[str, Type[BaseScraper]] = {
        # GM Collin
        "gmcollin.ca": GMCollinScraper,
        "www.gmcollin.ca": GMCollinScraper,
        "gmcollin": GMCollinScraper,
        
        # YK Canada
        "ykcanada.com": YKCanadaScraper,
        "ykcanada": YKCanadaScraper,
        "yk": YKCanadaScraper,
    }
    
    @classmethod
    def create_scraper(cls, website_identifier: str) -> Optional[BaseScraper]:
        """Create a scraper for the given website."""
        identifier = website_identifier.lower().strip()
        
        if identifier in cls._scrapers:
            return cls._scrapers[identifier]()
        
        # Try partial matching
        for registered_id, scraper_class in cls._scrapers.items():
            if identifier in registered_id or registered_id in identifier:
                return scraper_class()
        
        return None
    
    @classmethod
    def get_available_websites(cls) -> list:
        """Get list of supported websites."""
        return ["gmcollin.ca", "ykcanada.com"]