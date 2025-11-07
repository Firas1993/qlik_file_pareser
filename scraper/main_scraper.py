"""
Main scraper orchestrator.
Manages the execution of multiple website scrapers using the factory pattern.
"""

import time
from typing import List, Dict, Any
from datetime import datetime
from scraper_factory import ScraperFactory


class MainScraper:
    """
    Main class that orchestrates scraping across multiple websites.
    Uses factory pattern to create appropriate scraper instances.
    """
    
    def __init__(self):
        """Initialize the main scraper with list of websites to scrape."""
        # List of websites to scrape
        # You can add more websites here as you develop their scrapers
        self.websites_to_scrape = [
            "gmcollin.ca",
            # "example1.com",  # Add future websites here
            # "example2.com",
        ]
        
        self.results = []
        self.factory = ScraperFactory()
    
    def scrape_website(self, website_identifier: str) -> Dict[str, Any]:
        """
        Scrape a single website using the appropriate scraper.
        
        Args:
            website_identifier: Website domain or identifier
            
        Returns:
            Dictionary containing scraping results and summary
        """
        print(f"\n{'='*60}")
        print(f"🌐 Processing website: {website_identifier}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        
        try:
            # Create appropriate scraper using factory
            scraper = self.factory.create_scraper(website_identifier)
            
            if not scraper:
                error_msg = f"No scraper available for {website_identifier}"
                print(f"❌ {error_msg}")
                return {
                    "website": website_identifier,
                    "status": "failed",
                    "error": error_msg,
                    "duration": 0,
                    "locations_found": 0,
                    "output_file": None
                }
            
            print(f"✅ Found scraper: {scraper.__class__.__name__}")
            
            # Run the scraper
            summary = scraper.run()
            
            # Calculate duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Enhance summary with additional info
            result = {
                "website": website_identifier,
                "status": "success",
                "error": None,
                "duration": duration,
                "locations_found": summary.get("total_locations", 0),
                "output_file": summary.get("output_file"),
                "scraper_class": scraper.__class__.__name__,
                "timestamp": start_time.isoformat()
            }
            
            print(f"\n✅ Successfully scraped {website_identifier}")
            print(f"   📊 Locations found: {result['locations_found']}")
            print(f"   📁 Output file: {result['output_file']}")
            print(f"   ⏱️ Duration: {duration:.2f} seconds")
            
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            error_result = {
                "website": website_identifier,
                "status": "failed",
                "error": str(e),
                "duration": duration,
                "locations_found": 0,
                "output_file": None,
                "timestamp": start_time.isoformat()
            }
            
            print(f"\n❌ Failed to scrape {website_identifier}")
            print(f"   Error: {e}")
            print(f"   Duration: {duration:.2f} seconds")
            
            return error_result
    
    def run_all_scrapers(self) -> List[Dict[str, Any]]:
        """
        Run scrapers for all configured websites.
        
        Returns:
            List of result dictionaries for each website
        """
        print("🚀 Starting Multi-Website Scraper")
        print("=" * 60)
        print(f"📋 Websites to scrape: {len(self.websites_to_scrape)}")
        
        # Show available scrapers
        available_scrapers = self.factory.get_available_scrapers()
        print(f"🔧 Available scrapers: {len(available_scrapers)}")
        for identifier, description in available_scrapers.items():
            print(f"   - {identifier}: {description}")
        
        overall_start_time = datetime.now()
        
        # Process each website
        for idx, website in enumerate(self.websites_to_scrape, 1):
            print(f"\n📍 Processing {idx}/{len(self.websites_to_scrape)}: {website}")
            
            result = self.scrape_website(website)
            self.results.append(result)
            
            # Add delay between websites to be respectful
            if idx < len(self.websites_to_scrape):
                print("⏳ Waiting 5 seconds before next website...")
                time.sleep(5)
        
        # Print final summary
        overall_end_time = datetime.now()
        total_duration = (overall_end_time - overall_start_time).total_seconds()
        
        self.print_final_summary(total_duration)
        
        return self.results
    
    def print_final_summary(self, total_duration: float) -> None:
        """
        Print a comprehensive summary of all scraping operations.
        
        Args:
            total_duration: Total time taken for all operations
        """
        print(f"\n{'='*60}")
        print("📊 FINAL SUMMARY")
        print(f"{'='*60}")
        
        successful_sites = [r for r in self.results if r["status"] == "success"]
        failed_sites = [r for r in self.results if r["status"] == "failed"]
        total_locations = sum(r["locations_found"] for r in self.results)
        
        print(f"🌐 Total websites processed: {len(self.results)}")
        print(f"✅ Successful: {len(successful_sites)}")
        print(f"❌ Failed: {len(failed_sites)}")
        print(f"📍 Total locations found: {total_locations}")
        print(f"⏱️ Total duration: {total_duration:.2f} seconds")
        
        if successful_sites:
            print(f"\n✅ Successful websites:")
            for result in successful_sites:
                print(f"   - {result['website']}: {result['locations_found']} locations → {result['output_file']}")
        
        if failed_sites:
            print(f"\n❌ Failed websites:")
            for result in failed_sites:
                print(f"   - {result['website']}: {result['error']}")
        
        print(f"\n🎉 Scraping completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def add_website(self, website_identifier: str) -> None:
        """
        Add a website to the scraping list.
        
        Args:
            website_identifier: Website domain or identifier to add
        """
        if website_identifier not in self.websites_to_scrape:
            self.websites_to_scrape.append(website_identifier)
            print(f"✅ Added {website_identifier} to scraping list")
        else:
            print(f"⚠️ {website_identifier} already in scraping list")
    
    def remove_website(self, website_identifier: str) -> None:
        """
        Remove a website from the scraping list.
        
        Args:
            website_identifier: Website domain or identifier to remove
        """
        if website_identifier in self.websites_to_scrape:
            self.websites_to_scrape.remove(website_identifier)
            print(f"✅ Removed {website_identifier} from scraping list")
        else:
            print(f"⚠️ {website_identifier} not found in scraping list")


def main():
    """Main execution function."""
    scraper = MainScraper()
    results = scraper.run_all_scrapers()
    return results


if __name__ == "__main__":
    main()