#!/usr/bin/env python3
"""
Enhanced scraper with integrated phone number extraction
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from websites.gmcollin_scraper import GMCollinScraper
from websites.ykcanada_scraper import YKCanadaScraper

def run_scraper_with_phones(scraper_class, scraper_name, enable_phones=True):
    """Run a scraper with optional phone extraction"""
    print(f"\n🏢 SCRAPING {scraper_name.upper()}")
    print("=" * 60)
    
    # Initialize scraper
    scraper = scraper_class(enable_phone_extraction=enable_phones)
    
    try:
        print(f"🎯 Phone extraction: {'Enabled' if enable_phones else 'Disabled'}")
        print("🚀 Starting scraper...")
        
        # Run scraping
        locations = scraper.scrape()
        
        if locations:
            print(f"✅ Found {len(locations)} locations")
            
            # Count successful phone extractions
            if enable_phones:
                phones_found = sum(1 for loc in locations if loc.get('Phone'))
                success_rate = (phones_found / len(locations)) * 100 if locations else 0
                print(f"📞 Phone numbers found: {phones_found}/{len(locations)} ({success_rate:.1f}%)")
                
                # Show sample results
                print(f"\n📱 Sample results:")
                for i, location in enumerate(locations[:3], 1):
                    name = location.get('Name', 'N/A')
                    phone = location.get('Phone', 'Not found')
                    print(f"  {i}. {name} → {phone}")
            
            # Save to CSV
            scraper.save_to_csv(locations)
            print(f"💾 Saved to: {scraper.output_filename}")
            
        else:
            print("❌ No locations found")
            
        return len(locations) if locations else 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 0
        
    finally:
        scraper.cleanup()

def main():
    """Main function"""
    print("📞 ENHANCED STORE SCRAPER WITH PHONE EXTRACTION")
    print("=" * 60)
    print("🎯 Scrape store locations and extract phone numbers from Google Maps")
    print("")
    
    # Ask user about phone extraction
    phone_choice = input("📱 Enable phone number extraction? [y/N]: ").strip().lower()
    enable_phones = phone_choice in ['y', 'yes']
    
    if enable_phones:
        print("⚠️ Phone extraction will slow down the process but provide more data")
        confirm = input("   Continue? [y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            enable_phones = False
            print("📞 Phone extraction disabled")
    
    # Ask which scrapers to run
    print("\n🎯 Select scrapers to run:")
    print("1. GM Collin only")
    print("2. YK Canada only") 
    print("3. Both scrapers")
    
    while True:
        choice = input("\nChoice [1-3]: ").strip()
        if choice in ['1', '2', '3']:
            break
        print("❌ Please enter 1, 2, or 3")
    
    total_locations = 0
    
    # Run selected scrapers
    if choice in ['1', '3']:
        total_locations += run_scraper_with_phones(GMCollinScraper, "GM Collin", enable_phones)
    
    if choice in ['2', '3']:
        total_locations += run_scraper_with_phones(YKCanadaScraper, "YK Canada", enable_phones)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"🎯 Total locations scraped: {total_locations}")
    print(f"📞 Phone extraction: {'Enabled' if enable_phones else 'Disabled'}")
    print("\n📁 Check the 'output' folder for CSV files")
    print("🎉 Scraping completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
    finally:
        print("👋 Goodbye!")