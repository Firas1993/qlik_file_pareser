#!/usr/bin/env python3
"""
Phone Number Enhancement Script
Adds phone numbers to existing CSV files using Google Maps
"""

import os
import sys
import pandas as pd
from services.phone_extractor import GoogleMapsPhoneExtractor

def display_banner():
    """Display application banner"""
    print("=" * 60)
    print("📞 PHONE NUMBER EXTRACTION SERVICE")
    print("=" * 60)
    print("🎯 Enhance your store data with phone numbers from Google Maps")
    print("🔍 Uses web scraping (no API key required)")
    print("")

def list_available_files():
    """List available CSV files to process"""
    output_dir = "output"
    csv_files = []
    
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.csv') and not file.endswith('_with_phones.csv'):
                csv_files.append(file)
    
    return csv_files

def select_file_to_process():
    """Let user select which file to process"""
    csv_files = list_available_files()
    
    if not csv_files:
        print("❌ No CSV files found in output directory!")
        return None
    
    print("📁 Available CSV files:")
    print("")
    
    for i, file in enumerate(csv_files, 1):
        # Get record count
        try:
            df = pd.read_csv(f"output/{file}")
            count = len(df)
            print(f"{i:2d}. {file:<30} ({count:3d} records)")
        except Exception as e:
            print(f"{i:2d}. {file:<30} (error reading)")
    
    print(f"{len(csv_files) + 1:2d}. Process ALL files")
    print("")
    
    while True:
        try:
            choice = input("🔢 Select file number (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                return None
            
            choice_num = int(choice)
            
            if choice_num == len(csv_files) + 1:
                return "ALL"
            elif 1 <= choice_num <= len(csv_files):
                return csv_files[choice_num - 1]
            else:
                print("❌ Invalid choice. Please try again.")
                
        except ValueError:
            print("❌ Please enter a valid number.")

def get_processing_options():
    """Get processing options from user"""
    print("⚙️ Processing Options:")
    print("")
    
    # Test mode
    while True:
        test_mode = input("🧪 Test mode (process only first 5 records)? [y/N]: ").strip().lower()
        if test_mode in ['', 'n', 'no']:
            max_records = None
            break
        elif test_mode in ['y', 'yes']:
            max_records = 5
            break
        else:
            print("❌ Please enter 'y' or 'n'")
    
    # Headless mode
    while True:
        headless = input("🖥️ Run browser in background (headless mode)? [Y/n]: ").strip().lower()
        if headless in ['', 'y', 'yes']:
            headless_mode = True
            break
        elif headless in ['n', 'no']:
            headless_mode = False
            break
        else:
            print("❌ Please enter 'y' or 'n'")
    
    return max_records, headless_mode

def process_single_file(file_name, max_records, headless_mode):
    """Process a single CSV file"""
    input_path = f"output/{file_name}"
    output_name = file_name.replace('.csv', '_with_phones.csv')
    output_path = f"output/{output_name}"
    
    print(f"\n🔄 Processing: {file_name}")
    print(f"📤 Output will be: {output_name}")
    
    # Initialize extractor
    extractor = GoogleMapsPhoneExtractor(headless=headless_mode)
    
    # Process file
    success = extractor.process_csv_file(input_path, output_path, max_records)
    
    # Cleanup
    extractor.cleanup()
    
    if success:
        # Display results
        try:
            df = pd.read_csv(output_path)
            phones_found = df['Phone'].notna().sum()
            total_records = len(df)
            success_rate = (phones_found / total_records) * 100
            
            print(f"\n✅ {file_name} processed successfully!")
            print(f"📞 Phone numbers found: {phones_found}/{total_records} ({success_rate:.1f}%)")
            print(f"💾 Saved to: {output_name}")
            
        except Exception as e:
            print(f"✅ Processing completed, but couldn't read results: {str(e)}")
    else:
        print(f"\n❌ Failed to process {file_name}")
    
    return success

def main():
    """Main application function"""
    display_banner()
    
    # Select file to process
    selected_file = select_file_to_process()
    
    if not selected_file:
        print("👋 Goodbye!")
        return
    
    # Get processing options
    max_records, headless_mode = get_processing_options()
    
    print("\n" + "=" * 60)
    print("🚀 STARTING PHONE EXTRACTION")
    print("=" * 60)
    
    success_count = 0
    total_count = 0
    
    if selected_file == "ALL":
        csv_files = list_available_files()
        total_count = len(csv_files)
        
        for file_name in csv_files:
            if process_single_file(file_name, max_records, headless_mode):
                success_count += 1
            print("\n" + "-" * 40)
            
    else:
        total_count = 1
        if process_single_file(selected_file, max_records, headless_mode):
            success_count += 1
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully processed: {success_count}/{total_count} files")
    
    if success_count > 0:
        print("\n📁 Enhanced files with phone numbers:")
        output_files = [f for f in os.listdir("output") if f.endswith('_with_phones.csv')]
        for file in output_files:
            print(f"   📞 {file}")
    
    print("\n🎉 Phone extraction completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ Process interrupted by user")
        print("👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("👋 Goodbye!")