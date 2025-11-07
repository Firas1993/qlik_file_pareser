"""
Quick test of the factory pattern with a simple test.
"""

from scraper_factory import ScraperFactory

def test_factory():
    print("🧪 Testing Scraper Factory Pattern")
    print("=" * 40)
    
    # Test factory functionality
    print("📋 Available scrapers:")
    available = ScraperFactory.get_available_scrapers()
    for identifier, description in available.items():
        print(f"   - {identifier}: {description}")
    
    print(f"\n🔍 Testing scraper creation:")
    
    # Test creating a scraper
    scraper = ScraperFactory.create_scraper("gmcollin.ca")
    if scraper:
        print(f"✅ Successfully created: {scraper.__class__.__name__}")
        print(f"   Website name: {scraper.website_name}")
        print(f"   Base URL: {scraper.base_url}")
        print(f"   Output filename: {scraper.output_filename}")
        print(f"   Fieldnames: {scraper.get_fieldnames()}")
    else:
        print("❌ Failed to create scraper")
    
    # Test unsupported website
    print(f"\n🔍 Testing unsupported website:")
    unsupported = ScraperFactory.create_scraper("example.com")
    if unsupported:
        print(f"✅ Created: {unsupported.__class__.__name__}")
    else:
        print("❌ No scraper available for example.com (expected)")
    
    print(f"\n✅ Factory pattern test completed!")

if __name__ == "__main__":
    test_factory()