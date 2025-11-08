#!/usr/bin/env python3
"""
Test the integrated phone extraction functionality
Tests with a small sample to avoid rate limits
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from websites.gmcollin_scraper import GMCollinScraper

def test_integrated_phone_extraction():
    """Test phone extraction with GM Collin scraper"""
    print("🧪 TESTING INTEGRATED PHONE EXTRACTION")
    print("=" * 60)
    print("🎯 This will test phone number extraction during scraping")
    print("⚠️ Testing with limited postal codes to avoid rate limits")
    print("")
    
    # Initialize scraper with phone extraction enabled
    scraper = GMCollinScraper(enable_phone_extraction=True)
    
    try:
        # Override postal codes to test with just one
        original_prefixes = scraper.postal_prefixes
        scraper.postal_prefixes = ["H7N"]  # Montreal/Laval area only
        
        print("🔍 Starting scraping with phone extraction...")
        print("📍 Using postal code: H7N (Montreal/Laval area)")
        print("")
        
        # Scrape locations
        locations = scraper.scrape()
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION RESULTS")
        print("=" * 60)
        
        if locations:
            print(f"✅ Found {len(locations)} locations")
            
            # Show first few results with phone numbers
            print("\n📱 Sample results with phone numbers:")
            print("-" * 40)
            
            for i, location in enumerate(locations[:5], 1):
                name = location.get('Name', 'N/A')
                address = location.get('Address', 'N/A')
                phone = location.get('Phone', 'Not found')
                
                print(f"{i}. {name}")
                print(f"   📍 {address}")
                print(f"   📞 {phone}")
                print()
            
            if len(locations) > 5:
                print(f"... and {len(locations) - 5} more locations")
            
            # Count successful phone extractions
            phones_found = sum(1 for loc in locations if loc.get('Phone'))
            success_rate = (phones_found / len(locations)) * 100
            
            print(f"\n📞 Phone extraction success rate: {phones_found}/{len(locations)} ({success_rate:.1f}%)")
            
        else:
            print("❌ No locations found")
        
        # Save results to CSV
        if locations:
            scraper.save_to_csv(locations)
            print(f"\n💾 Results saved to: {scraper.output_filename}")
            
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        
    finally:
        # Cleanup
        scraper.cleanup()
        print("\n🧹 Cleanup completed")

def main():
    """Main function"""
    response = input("🚀 Run integrated phone extraction test? [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        test_integrated_phone_extraction()
    else:
        print("👋 Test skipped")

if __name__ == "__main__":
    main()