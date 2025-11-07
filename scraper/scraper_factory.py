"""
Scraper factory that creates appropriate scraper instances based on website.
Uses factory pattern to determine which scraper to instantiate.
"""

from typing import Dict, Type, Optional
from base_scraper import BaseScraper
from gmcollin_scraper import GMCollinScraper


class ScraperFactory:
    """
    Factory class for creating scraper instances.
    Maps website identifiers to their corresponding scraper classes.
    """
    
    # Registry of available scrapers
    _scrapers: Dict[str, Type[BaseScraper]] = {
        "gmcollin.ca": GMCollinScraper,
        "www.gmcollin.ca": GMCollinScraper,
        "gmcollin_spas_ca": GMCollinScraper,
        # Add more scrapers here as they are developed
        # "example.com": ExampleScraper,
    }
    
    @classmethod
    def create_scraper(cls, website_identifier: str) -> Optional[BaseScraper]:
        """
        Create a scraper instance for the given website.
        
        Args:
            website_identifier: Website domain, name, or identifier
            
        Returns:
            Scraper instance or None if no matching scraper found
        """
        # Normalize the identifier
        identifier = website_identifier.lower().strip()
        
        # Try exact match first
        if identifier in cls._scrapers:
            scraper_class = cls._scrapers[identifier]
            return scraper_class()
        
        # Try partial matching for domain names
        for registered_identifier, scraper_class in cls._scrapers.items():
            if identifier in registered_identifier or registered_identifier in identifier:
                return scraper_class()
        
        # No matching scraper found
        return None
    
    @classmethod
    def get_available_scrapers(cls) -> Dict[str, str]:
        """
        Get a dictionary of available scrapers and their descriptions.
        
        Returns:
            Dictionary mapping identifiers to scraper descriptions
        """
        available = {}
        for identifier, scraper_class in cls._scrapers.items():
            # Get class name as description
            class_name = scraper_class.__name__
            available[identifier] = f"{class_name} - {scraper_class.__doc__ or 'No description'}"
        
        return available
    
    @classmethod
    def register_scraper(cls, identifier: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a new scraper class.
        
        Args:
            identifier: Website identifier/domain
            scraper_class: Scraper class that extends BaseScraper
        """
        if not issubclass(scraper_class, BaseScraper):
            raise ValueError(f"Scraper class {scraper_class.__name__} must extend BaseScraper")
        
        cls._scrapers[identifier.lower().strip()] = scraper_class
    
    @classmethod
    def is_supported(cls, website_identifier: str) -> bool:
        """
        Check if a website is supported by any registered scraper.
        
        Args:
            website_identifier: Website domain, name, or identifier
            
        Returns:
            True if supported, False otherwise
        """
        return cls.create_scraper(website_identifier) is not None