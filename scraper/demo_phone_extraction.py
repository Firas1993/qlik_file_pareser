#!/usr/bin/env python3
"""
Quick demo of integrated phone extraction with one business
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.phone_extractor import GoogleMapsPhoneExtractor

def demo_phone_extraction():
    """Demo phone extraction with a known business"""
    print("🧪 PHONE EXTRACTION DEMO")
    print("=" * 50)
    print("🎯 Testing with a known Canadian business")
    print("")
    
    # Test with a well-known business
    test_name = "Tim Hortons"
    test_address = "1050 Boul Le Corbusier, Laval, QC, H7N 0A8, Canada"
    
    print(f"🏢 Business: {test_name}")
    print(f"📍 Address: {test_address}")
    print("")
    
    # Initialize extractor
    extractor = GoogleMapsPhoneExtractor(headless=False, delay_range=(2, 4))
    
    try:
        if extractor.setup_driver():
            print("🔍 Searching Google Maps...")
            phone = extractor.search_google_maps(test_name, test_address)
            
            print("\n" + "=" * 50)
            print("📊 RESULT")
            print("=" * 50)
            
            if phone:
                print(f"✅ Phone found: {phone}")
                print("🎉 Phone extraction working!")
            else:
                print("❌ No phone found")
                print("💡 This could be normal - not all locations have listed phones")
                
        else:
            print("❌ Could not setup browser driver")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
    finally:
        extractor.cleanup()

def main():
    """Main function"""
    response = input("🚀 Run phone extraction demo? (opens browser) [y/N]: ").strip().lower()
    
    if response in ['y', 'yes']:
        demo_phone_extraction()
    else:
        print("👋 Demo skipped")

if __name__ == "__main__":
    main()