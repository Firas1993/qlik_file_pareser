#!/usr/bin/env python3
"""
Quick test script for phone number extraction
Tests with a single business from our CSV data
"""

import sys
import os
import pandas as pd

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.phone_extractor import GoogleMapsPhoneExtractor

def test_single_business():
    """Test phone extraction with a single business"""
    print("🧪 PHONE EXTRACTION TEST")
    print("=" * 50)
    
    # Read first business from GM Collin data
    try:
        df = pd.read_csv("output/gmcollin_spas_ca.csv")
        if len(df) == 0:
            print("❌ No data found in CSV file")
            return
            
        first_business = df.iloc[0]
        business_name = first_business['Name']
        address = first_business['Address']
        
        print(f"🏢 Testing with: {business_name}")
        print(f"📍 Address: {address}")
        print("")
        
        # Initialize extractor (not headless so you can see what happens)
        extractor = GoogleMapsPhoneExtractor(headless=False, delay_range=(3, 5))
        
        if not extractor.setup_driver():
            print("❌ Failed to setup browser driver")
            return
            
        print("🔍 Searching Google Maps for phone number...")
        phone = extractor.search_google_maps(business_name, address)
        
        print("\n" + "=" * 50)
        print("📊 RESULTS")
        print("=" * 50)
        
        if phone:
            print(f"✅ Phone number found: {phone}")
            print("🎉 Test successful!")
        else:
            print("❌ No phone number found")
            print("💡 This could be normal - not all businesses have phone numbers listed")
            
        extractor.cleanup()
        
    except FileNotFoundError:
        print("❌ CSV file not found. Please run the main scraper first.")
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

def test_phone_validation():
    """Test phone number validation and cleaning"""
    print("\n🧪 PHONE VALIDATION TEST")
    print("=" * 50)
    
    extractor = GoogleMapsPhoneExtractor()
    
    test_numbers = [
        "+1 (514) 555-1234",
        "(514) 555-1234",
        "514-555-1234",
        "514.555.1234",
        "5145551234",
        "+1-514-555-1234",
        "Call us: (514) 555-1234",
        "invalid text",
        "123-45-6789",  # Too short
    ]
    
    print("Testing phone number patterns:")
    print("")
    
    for test_number in test_numbers:
        is_valid = extractor.is_valid_phone(test_number)
        cleaned = extractor.clean_phone_number(test_number) if is_valid else "N/A"
        
        status = "✅ Valid  " if is_valid else "❌ Invalid"
        print(f"{status} | {test_number:<20} → {cleaned}")

if __name__ == "__main__":
    print("📞 Phone Extraction Test Suite")
    print("🎯 This will test phone number extraction from Google Maps")
    print("")
    
    # Test phone validation first
    test_phone_validation()
    
    print("\n" + "="*60)
    
    # Ask user if they want to run the live test
    response = input("\n🔴 Run live Google Maps test? (opens browser) [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        test_single_business()
    else:
        print("👋 Skipping live test. Run again to test Google Maps integration.")
        
    print("\n✅ Test suite completed!")