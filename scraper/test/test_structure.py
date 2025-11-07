"""
Quick test of the updated scraper structure.
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from scraper_factory import ScraperFactory
from common.canadian_store_scraper import POSTAL_CODE_PREFIXES

def test_structure():
    print("🧪 Testing Updated Scraper Structure")
    print("=" * 50)
    
    # Test postal code constants
    print("📮 Postal Code Prefixes:")
    for country, codes in POSTAL_CODE_PREFIXES.items():
        print(f"   {country.upper()}: {len(codes)} codes - {codes[:3]}...")
    
    # Test factory
    print(f"\n🏭 Factory Test:")
    factory = ScraperFactory()
    
    print(f"   Available websites: {factory.get_available_websites()}")
    
    # Test scraper creation
    print(f"\n🔍 Testing Scraper Creation:")
    
    gm_scraper = factory.create_scraper("gmcollin.ca")
    if gm_scraper:
        print(f"   ✅ GM Collin: {gm_scraper.__class__.__name__}")
        print(f"      Search Input ID: {gm_scraper.search_input_id}")
        print(f"      Search Button ID: {gm_scraper.search_button_id}")
        print(f"      Pagination Select ID: {gm_scraper.pagination_select_id}")
        print(f"      Country: {gm_scraper.country}")
        print(f"      Output file: {gm_scraper.output_filename}")
    
    yk_scraper = factory.create_scraper("ykcanada.com")
    if yk_scraper:
        print(f"   ✅ YK Canada: {yk_scraper.__class__.__name__}")
        print(f"      Search Input ID: {yk_scraper.search_input_id}")
        print(f"      Search Button ID: {yk_scraper.search_button_id}")
        print(f"      Pagination Select ID: {yk_scraper.pagination_select_id}")
        print(f"      Country: {yk_scraper.country}")
        print(f"      Output file: {yk_scraper.output_filename}")
    
    print(f"\n✅ Structure test completed!")

if __name__ == "__main__":
    test_structure()