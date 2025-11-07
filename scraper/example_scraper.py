"""
Example scraper for demonstration purposes.
Shows how to extend the base scraper for a new website.
"""

from typing import List, Dict, Any
from base_scraper import BaseScraper


class ExampleScraper(BaseScraper):
    """Example scraper to demonstrate the pattern."""
    
    def __init__(self):
        super().__init__(
            website_name="example.com",
            base_url="https://example.com"
        )
    
    def get_fieldnames(self) -> List[str]:
        """Get CSV column names for example data."""
        return ["Name", "Address", "Phone", "Website"]
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Example scraping implementation.
        In a real scraper, this would contain actual scraping logic.
        """
        print("🔍 Scraping example.com locations...")
        
        # Simulate scraping some data
        locations = [
            {
                "Name": "Example Location 1",
                "Address": "123 Main St, City, State",
                "Phone": "555-1234",
                "Website": "example1.com"
            },
            {
                "Name": "Example Location 2",
                "Address": "456 Oak Ave, City, State", 
                "Phone": "555-5678",
                "Website": "example2.com"
            }
        ]
        
        print(f"✅ Found {len(locations)} example locations")
        return locations


# Example of how to register the new scraper with the factory
if __name__ == "__main__":
    from scraper_factory import ScraperFactory
    
    # Register the new scraper
    ScraperFactory.register_scraper("example.com", ExampleScraper)
    
    print("✅ Example scraper registered!")
    print("📋 Available scrapers:")
    
    available = ScraperFactory.get_available_scrapers()
    for identifier, description in available.items():
        print(f"   - {identifier}: {description}")