"""
Main scraper for GM Collin and YK Canada store locators.
Focused implementation using exact selectors.
"""

import time
import os
from typing import List, Dict, Any
from datetime import datetime
from scraper_factory import ScraperFactory


class MainScraper:
    """Main scraper for Canadian store locators."""
    
    def __init__(self):
        """Initialize with GM Collin and YK Canada websites."""
        self.websites_to_scrape = [
            "gmcollin.ca",
            "ykcanada.com".  # add any new target websites here
        ]
        self.results = []
        self.factory = ScraperFactory()
        
        # Ensure output directory exists
        os.makedirs('output', exist_ok=True)
    
    def scrape_website(self, website_identifier: str) -> Dict[str, Any]:
        """Scrape a single website."""
        print(f"\n{'='*60}")
        print(f"🌐 Processing website: {website_identifier}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            scraper = self.factory.create_scraper(website_identifier)
            
            if not scraper:
                return {
                    "website": website_identifier,
                    "status": "failed",
                    "error": f"No scraper available for {website_identifier}",
                    "duration": 0,
                    "locations_found": 0,
                    "output_file": None
                }
            
            print(f"✅ Found scraper: {scraper.__class__.__name__}")
            
            # Run the scraper
            summary = scraper.run()
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "website": website_identifier,
                "status": "success",
                "error": None,
                "duration": duration,
                "locations_found": summary.get("total_locations", 0),
                "output_file": summary.get("output_file"),
                "scraper_class": scraper.__class__.__name__
            }
            
            print(f"\n✅ Successfully scraped {website_identifier}")
            print(f"   📊 Locations found: {result['locations_found']}")
            print(f"   📁 Output file: {result['output_file']}")
            print(f"   ⏱️ Duration: {duration:.2f} seconds")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            print(f"\n❌ Failed to scrape {website_identifier}")
            print(f"   Error: {e}")
            
            return {
                "website": website_identifier,
                "status": "failed",
                "error": str(e),
                "duration": duration,
                "locations_found": 0,
                "output_file": None
            }
    
    def run_all_scrapers(self) -> List[Dict[str, Any]]:
        """Run scrapers for all websites."""
        print("🍁 Canadian Store Locator Scraper")
        print("=" * 50)
        print("🎯 Focused on: GM Collin & YK Canada")
        print("🔧 Using exact selectors (no fallbacks)")
        print(f"📁 Output files will be saved in: ./output/")
        
        overall_start_time = datetime.now()
        
        for idx, website in enumerate(self.websites_to_scrape, 1):
            print(f"\n📍 Processing {idx}/{len(self.websites_to_scrape)}: {website}")
            
            result = self.scrape_website(website)
            # here go throw the result and find the phone number and the websites and reviews if possible.
            self.results.append(result)
            
            # Add delay between websites
            if idx < len(self.websites_to_scrape):
                print("⏳ Waiting 3 seconds before next website...")
                time.sleep(3)
        
        # Print summary
        total_duration = (datetime.now() - overall_start_time).total_seconds()
        self.print_summary(total_duration)
        
        return self.results
    
    def print_summary(self, total_duration: float) -> None:
        """Print final summary."""
        print(f"\n{'='*60}")
        print("📊 SCRAPING SUMMARY")
        print(f"{'='*60}")
        
        successful = [r for r in self.results if r["status"] == "success"]
        failed = [r for r in self.results if r["status"] == "failed"]
        total_locations = sum(r["locations_found"] for r in self.results)
        
        print(f"🌐 Websites processed: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📍 Total locations found: {total_locations}")
        print(f"⏱️ Total duration: {total_duration:.2f} seconds")
        print(f"📁 Output directory: ./output/")
        
        if successful:
            print(f"\n✅ Successful websites:")
            for result in successful:
                print(f"   - {result['website']}: {result['locations_found']} locations → {result['output_file']}")
        
        if failed:
            print(f"\n❌ Failed websites:")
            for result in failed:
                print(f"   - {result['website']}: {result['error']}")
        
        print(f"\n🎉 Scraping completed!")


def main():
    """Main execution function."""
    scraper = MainScraper()
    return scraper.run_all_scrapers()


if __name__ == "__main__":
    main()