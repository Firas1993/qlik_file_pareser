"""
GM Collin spa location scraper.
Scrapes spa locations from GM Collin's store locator.
"""

import time
from typing import List, Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
from bs4 import BeautifulSoup

from base_scraper import BaseScraper


class GMCollinScraper(BaseScraper):
    """Scraper for GM Collin spa locations."""
    
    def __init__(self):
        super().__init__(
            website_name="gmcollin_spas_ca",
            base_url="https://www.gmcollin.ca/apps/store-locator/"
        )
        # Canadian postal code prefixes for major cities
        self.postal_prefixes = [
            "H7N",  # Montreal/Laval area, QC
            "M5V",  # Toronto area, ON
            "K1A",  # Ottawa area, ON
            "T2P",  # Calgary area, AB
            "V6B",  # Vancouver area, BC
            "R3C",  # Winnipeg area, MB
            "S7K",  # Saskatoon area, SK
            "B3H",  # Halifax area, NS
            "A1A",  # St. John's area, NL
            "Y1A"   # Whitehorse area, YT
        ]
    
    def get_fieldnames(self) -> List[str]:
        """Get CSV column names for GM Collin data."""
        return [
            "Name", "Address", "Street", "City", 
            "Province_State", "Postal_Code", "Country", "Search_Zip"
        ]
    
    def extract_spa_locations_from_zip(self, zip_code: str) -> List[Dict[str, Any]]:
        """
        Extract spa locations for a specific postal code.
        
        Args:
            zip_code: Postal code to search for
            
        Returns:
            List of location dictionaries
        """
        locations = []
        
        try:
            print(f"🔍 Searching for locations near {zip_code}...")
            
            # Navigate to the store locator
            self.driver.get(self.base_url)
            print(f"   Navigated to {self.base_url}")
            
            # Wait for and find the search input
            wait = WebDriverWait(self.driver, 15)
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='address'], input[placeholder*='Address'], input#address"))
            )
            print("   Found search input field")
            
            # Modify pagination to show 100 results
            try:
                # Execute JavaScript to change the pagination select value
                js_script = """
                var selectElement = document.querySelector('select[name="distance_in_km"]') || 
                                  document.querySelector('select.distance-select') ||
                                  document.querySelector('select');
                if (selectElement) {
                    // Create option for 100 if it doesn't exist
                    var option100 = document.createElement('option');
                    option100.value = '100';
                    option100.text = '100';
                    selectElement.appendChild(option100);
                    selectElement.value = '100';
                    return true;
                } else {
                    return false;
                }
                """
                
                result = self.driver.execute_script(js_script)
                if result:
                    print("   ✅ Changed pagination limit from 10 to 100")
                else:
                    print("   ⚠️ Could not find pagination select element")
            except Exception as e:
                print(f"   ⚠️ Could not modify pagination: {e}")
            
            # Clear and enter the zip code
            search_input.clear()
            search_input.send_keys(zip_code)
            print(f"   Entered zip code: {zip_code}")
            
            # Find and click search button with better error handling
            search_button = None
            button_selectors = [
                "button[type='submit']", 
                "input[type='submit']", 
                ".search-button", 
                ".btn-search",
                "button.btn",
                ".btn",
                "button",
                "input[value*='Search']",
                "input[value*='search']"
            ]
            
            for selector in button_selectors:
                try:
                    search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_button.is_displayed() and search_button.is_enabled():
                        break
                except NoSuchElementException:
                    continue
            
            if search_button:
                try:
                    # Try regular click first
                    search_button.click()
                    print("   Clicked search button")
                except Exception:
                    # Try JavaScript click if regular click fails
                    self.driver.execute_script("arguments[0].click();", search_button)
                    print("   Clicked search button (JavaScript)")
            else:
                print("   ⚠️ Could not find search button")
                return locations
            
            # Wait for results
            print("   Waiting for results...")
            time.sleep(5)
            
            # Check for alert indicating no results
            try:
                WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"   ⚠️ No results found for {zip_code}: Alert Text: {alert_text}")
                alert.accept()
                return locations
            except TimeoutException:
                # No alert means we have results, continue
                pass
            except UnexpectedAlertPresentException as e:
                print(f"   ⚠️ No results found for {zip_code}: {e}")
                return locations
            
            # Wait for addresses container
            try:
                addresses_container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".addresses, .results, .store-list, .locations"))
                )
                print("   Found addresses list container")
            except TimeoutException:
                print(f"   ⚠️ No addresses container found for {zip_code}")
                return locations
            
            # Get all location elements
            location_elements = self.driver.find_elements(By.CSS_SELECTOR, ".address, .location, .store-item, .result-item")
            
            if not location_elements:
                print(f"   ⚠️ No location elements found for {zip_code}")
                return locations
            
            print(f"   Found {len(location_elements)} location(s)")
            
            # Extract data from each location
            for idx, element in enumerate(location_elements, 1):
                try:
                    # Get name
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, ".name, .store-name, .title, h3, h4")
                        name = name_element.text.strip()
                    except NoSuchElementException:
                        print(f"   ⚠️ Error extracting location {idx}: Could not find name element")
                        continue
                    
                    # Get address
                    try:
                        address_element = element.find_element(By.CSS_SELECTOR, ".address, .store-address, .location-address")
                        full_address = address_element.text.strip()
                    except NoSuchElementException:
                        print(f"   ⚠️ Error extracting location {idx}: Could not find address element")
                        continue
                    
                    if not name or not full_address:
                        continue
                    
                    print(f"   ✅ Extracted: {name}")
                    
                    # Parse address components
                    address_parts = [part.strip() for part in full_address.split(',')]
                    
                    street = address_parts[0] if len(address_parts) > 0 else ""
                    city = address_parts[1] if len(address_parts) > 1 else ""
                    province_postal = address_parts[2] if len(address_parts) > 2 else ""
                    country = address_parts[3] if len(address_parts) > 3 else "Canada"
                    
                    # Extract province and postal code
                    province = ""
                    postal_code = ""
                    
                    if province_postal:
                        parts = province_postal.strip().split()
                        if len(parts) >= 2:
                            province = parts[0]
                            postal_code = ' '.join(parts[1:])
                        else:
                            province = province_postal
                    
                    location_data = {
                        "Name": name,
                        "Address": full_address,
                        "Street": street,
                        "City": city,
                        "Province_State": province,
                        "Postal_Code": postal_code,
                        "Country": country,
                        "Search_Zip": zip_code
                    }
                    
                    locations.append(location_data)
                    
                except Exception as e:
                    print(f"   ⚠️ Error extracting location {idx}: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Error processing {zip_code}: {e}")
        
        return locations
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method for GM Collin locations.
        
        Returns:
            List of unique location dictionaries
        """
        print("🔍 Scraping GM Collin spa locations using store locator...")
        print("📍 Using postal code prefixes for broader coverage across Canada")
        
        all_locations = []
        unique_locations = {}
        
        # Search using each postal code prefix
        for zip_prefix in self.postal_prefixes:
            print(f"\n--- Searching with postal code prefix: {zip_prefix} ---")
            
            locations = self.extract_spa_locations_from_zip(zip_prefix)
            
            # Add unique locations
            for location in locations:
                location_key = location["Name"].strip().upper()
                
                if location_key not in unique_locations:
                    unique_locations[location_key] = location
                    all_locations.append(location)
                    print(f"   📍 Added: {location['Name']} ({location['City']}, {location['Province_State']})")
                # Skip duplicates silently
        
        print(f"\n✅ Extracted {len(all_locations)} unique location entries")
        
        return all_locations