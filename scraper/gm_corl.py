# Import required libraries for web scraping and data processing
import requests          # For making HTTP requests to websites
from bs4 import BeautifulSoup  # For parsing HTML content
import csv              # For writing data to CSV files
import time             # For adding delays between requests
import re               # For regular expression pattern matching
from urllib.parse import urljoin  # For joining URLs
from selenium import webdriver  # For automating browser interactions
from selenium.webdriver.common.by import By  # For finding elements
from selenium.webdriver.support.ui import WebDriverWait  # For waiting for elements
from selenium.webdriver.support import expected_conditions as EC  # For wait conditions
from selenium.webdriver.common.keys import Keys  # For sending keyboard input
from selenium.webdriver.chrome.options import Options  # For Chrome browser options
from selenium.webdriver.chrome.service import Service  # For Chrome service
from webdriver_manager.chrome import ChromeDriverManager  # For automatic ChromeDriver management

# Target website URL - the actual store locator application
URL = "https://www.gmcollin.ca/apps/store-locator/"

# Sample postal code prefixes to try (first 3 letters for broader coverage)
# Using major Canadian city postal code prefixes for comprehensive coverage
TEST_ZIP_CODES = ["H7N", "M5V", "K1A", "T2P", "V6B", "R3C", "S7K", "B3H", "A1A", "Y1A"]  # QC, ON, ON, AB, BC, MB, SK, NS, NL, YT

def setup_driver():
    """Set up Chrome driver with appropriate options"""
    # Step 1: Configure Chrome browser options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run browser in background (no GUI)
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size
    chrome_options.add_argument("--disable-web-security")  # Disable web security for testing
    chrome_options.add_argument("--allow-running-insecure-content")  # Allow insecure content
    
    try:
        # Step 2: Use webdriver-manager to automatically get the right ChromeDriver version
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver setup successful")
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        print("   This might be because:")
        print("   - Chrome browser is not installed")
        print("   - ChromeDriver version mismatch")
        print("   - Network issues downloading ChromeDriver")
        return None

def extract_spa_locations_from_zip(driver, zip_code):
    """Extract spa locations for a specific zip code"""
    print(f"🔍 Searching for locations near {zip_code}...")
    
    try:
        # Step 1: Navigate to the store locator page
        driver.get(URL)
        print(f"   Navigated to {URL}")
        
        # Step 2: Wait for the page to load and find the search input
        wait = WebDriverWait(driver, 10)  # Wait up to 10 seconds
        search_input = wait.until(
            EC.presence_of_element_located((By.ID, "address_search"))
        )
        print("   Found search input field")
        
        # Step 3: Find and modify the pagination limit before searching
        try:
            # Find the limit select dropdown
            limit_select = driver.find_element(By.ID, "limit")
            # Find the option within the select and change its value to 100
            option = limit_select.find_element(By.TAG_NAME, "option")
            # Use JavaScript to change the option value and text
            driver.execute_script("""
                arguments[0].value = '100';
                arguments[0].text = '100';
            """, option)
            # Set the select element's value to 100
            driver.execute_script("arguments[0].value = '100';", limit_select)
            print("   ✅ Changed pagination limit from 10 to 100")
        except Exception as e:
            print(f"   ⚠️  Could not modify pagination limit: {e}")
        
        # Step 4: Clear any existing text and enter the zip code
        search_input.clear()
        search_input.send_keys(zip_code)
        print(f"   Entered zip code: {zip_code}")
        
        # Step 5: Find and click the submit button
        submit_button = driver.find_element(By.ID, "submitBtn")
        submit_button.click()
        print("   Clicked search button")
        
        # Step 6: Wait for results to load
        time.sleep(3)  # Give time for the search to complete
        print("   Waiting for results...")
        
        # Step 7: Try to find the addresses list
        try:
            addresses_container = wait.until(
                EC.presence_of_element_located((By.ID, "addresses_list"))
            )
            print("   Found addresses list container")
        except Exception as e:
            print(f"   ⚠️  No results found for {zip_code}: {e}")
            return []
        
        # Step 8: Extract location data from the results
        locations = []
        
        # Find all list items (each represents a location)
        location_items = addresses_container.find_elements(By.TAG_NAME, "li")
        print(f"   Found {len(location_items)} location(s)")
        
        # Step 9: Process each location item
        for i, item in enumerate(location_items):
            try:
                # Extract business name
                name_elem = item.find_element(By.CLASS_NAME, "name")
                name = name_elem.text.strip() if name_elem else f"Location {i+1}"
                
                # Extract address components
                address_elem = item.find_element(By.CLASS_NAME, "address")
                address = address_elem.text.strip() if address_elem else "N/A"
                
                city_elem = item.find_element(By.CLASS_NAME, "city")
                city = city_elem.text.strip() if city_elem else "N/A"
                
                province_elem = item.find_element(By.CLASS_NAME, "prov_state")
                province = province_elem.text.strip() if province_elem else "N/A"
                
                postal_elem = item.find_element(By.CLASS_NAME, "postal_zip")
                postal = postal_elem.text.strip() if postal_elem else "N/A"
                
                country_elem = item.find_element(By.CLASS_NAME, "country")
                country = country_elem.text.strip() if country_elem else "N/A"
                
                # Step 10: Combine address components into full address
                full_address = f"{address}, {city}, {province} {postal}, {country}"
                
                # Step 11: Create location data dictionary
                location_data = {
                    "Name": name,
                    "Address": full_address,
                    "Street": address,
                    "City": city,
                    "Province_State": province,
                    "Postal_Code": postal,
                    "Country": country,
                    "Search_Zip": zip_code
                }
                
                locations.append(location_data)
                print(f"   ✅ Extracted: {name}")
                
            except Exception as e:
                print(f"   ⚠️  Error extracting location {i+1}: {e}")
                continue
        
        return locations
        
    except Exception as e:
        print(f"   ❌ Error during search for {zip_code}: {e}")
        return []

def extract_spa_locations():
    """Main function to extract spa locations using multiple zip codes"""
    print("🔍 Scraping GM Collin spa locations using store locator...")
    print("📍 Using postal code prefixes for broader coverage across Canada")
    
    # Step 1: Set up the browser driver
    driver = setup_driver()
    if not driver:
        return []
    
    all_locations = []  # Store all found locations
    
    try:
        # Step 2: Search using different postal code prefixes to get comprehensive results
        for zip_code in TEST_ZIP_CODES:
            print(f"\n--- Searching with postal code prefix: {zip_code} ---")
            locations = extract_spa_locations_from_zip(driver, zip_code)
            
            # Step 3: Add locations to our master list, avoiding duplicates
            for location in locations:
                # Check if we already have this location (based on name and postal code)
                is_duplicate = any(
                    existing["Name"] == location["Name"] and 
                    existing["Postal_Code"] == location["Postal_Code"]
                    for existing in all_locations
                )
                
                if not is_duplicate:
                    all_locations.append(location)
                    print(f"   📍 Added: {location['Name']} ({location['City']}, {location['Province_State']})")
                else:
                    print(f"   🔄 Skipped duplicate: {location['Name']}")
            
            # Step 4: Add small delay between searches to be respectful
            time.sleep(2)
        
        return all_locations
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []
    
    finally:
        # Step 5: Always close the browser when done
        if driver:
            driver.quit()
            print("🔚 Browser closed")

def save_to_csv(data, filename="gmcollin_spas_ca.csv"):
    """Save data to CSV file"""
    try:
        # Step 1: Define the column headers for our CSV file
        fieldnames = ["Name", "Address", "Street", "City", "Province_State", "Postal_Code", "Country", "Search_Zip"]
        
        # Step 2: Open file for writing with UTF-8 encoding to handle special characters
        with open(filename, "w", newline="", encoding="utf-8") as file:
            # Step 3: Create a CSV writer object that will format our data
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            # Step 4: Write the header row with column names
            writer.writeheader()
            # Step 5: Write all our location data as rows
            writer.writerows(data)
        
        print(f"💾 Data saved to {filename}")  # Confirm successful save
        
    except Exception as e:
        # Step 6: Handle file writing errors
        print(f"❌ Error saving to CSV: {e}")

def main():
    """Main function to run the scraper"""
    # Step 1: Display welcome message and separator
    print("🚀 GM Collin Spa Location Scraper (Store Locator)")
    print("=" * 50)
    print("🔧 Enhanced with: 100 results/page + postal code prefixes")
    
    # Step 2: Call the extraction function to get location data
    data = extract_spa_locations()
    
    # Step 3: Check if we found any location data
    if data:
        print(f"\n✅ Extracted {len(data)} unique location entries")  # Show count of found locations
        
        # Step 4: Display results in a readable format
        print("\n📍 Found locations:")
        for i, location in enumerate(data, 1):  # enumerate(data, 1) starts counting from 1
            print(f"{i}. {location['Name']}")           # Display location name
            print(f"   Address: {location['Address']}")  # Display full address
            print(f"   Search Prefix: {location['Search_Zip']}")  # Show which postal prefix found this
            print()  # Empty line for readability
        
        # Step 5: Save the results to a CSV file
        save_to_csv(data)
        
        # Step 6: Display summary statistics
        print("\n📊 Summary:")
        print(f"   Total unique locations found: {len(data)}")
        
        # Group by search postal code prefix
        prefix_counts = {}
        for location in data:
            prefix = location['Search_Zip']
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        
        print("\n🗺️  Coverage by postal code prefix:")
        for prefix, count in prefix_counts.items():
            print(f"   {prefix}*: {count} locations")
        
        # Group by province
        province_counts = {}
        for location in data:
            province = location['Province_State']
            province_counts[province] = province_counts.get(province, 0) + 1
        
        print("\n🏛️  Coverage by province:")
        for province, count in sorted(province_counts.items()):
            print(f"   {province}: {count} locations")
        
    else:
        # Step 7: Handle case where no locations were found
        print("⚠️  No spa locations found.")
        print("This could mean:")
        print("   - The website structure has changed")
        print("   - Chrome/chromedriver is not properly installed")
        print("   - The store locator is not accessible")
        print("   - Network connectivity issues")
        print("   - Pagination modification failed")
        
        # Step 8: Create empty CSV file as a template even if no data found
        save_to_csv([], "gmcollin_spas_empty.csv")
        
        print("\n💡 To install chromedriver on macOS:")
        print("   brew install chromedriver")
        print("\n💡 Alternative: Try different postal code prefixes by modifying TEST_ZIP_CODES list")

# Entry point: This code block only runs when script is executed directly (not imported)
if __name__ == "__main__":
    main()  # Call the main function to start the scraping process
