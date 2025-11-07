"""
Focused Store Locator Scraper for websites with similar structure.
Uses exact selectors with defaults for GM Collin and YK Canada style websites.
"""

import time
from typing import List, Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, UnexpectedAlertPresentException
import os

from common.base_scraper import BaseScraper


# Postal code prefixes for different countries - extensible for future use
POSTAL_CODE_PREFIXES = {
    'canada': [
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
    ],
    'usa': [
        "10001", # New York, NY
        "90210", # Beverly Hills, CA
        "60601", # Chicago, IL
        "77001", # Houston, TX
        "33101", # Miami, FL
        "02101", # Boston, MA
        "98101", # Seattle, WA
        "30301", # Atlanta, GA
        "80201", # Denver, CO
        "85001"  # Phoenix, AZ
    ]
    # Add more countries as needed:
    # 'uk': [...],
    # 'australia': [...],
}


class StoreLocatorScraper(BaseScraper):
    """
    Generic store locator scraper with default selectors for GM Collin/YK Canada style websites.
    """
    
    def __init__(self, website_name: str, base_url: str, 
                 search_input_id: str = "address_search",
                 search_button_id: str = "submitBtn", 
                 pagination_select_id: str = "limit",
                 distance_select_id: str = "within_distance",
                 country: str = "canada"):
        """
        Initialize the store locator scraper with exact selectors.
        
        Args:
            website_name: Name of the website (used for file naming)
            base_url: Base URL of the store locator
            search_input_id: ID for search input (default: "address_search")
            search_button_id: ID for search button (default: "submitBtn")
            pagination_select_id: ID for pagination select (default: "limit")
            distance_select_id: ID for distance limit select (default: "within_distance")
            country: Country for postal codes (default: "canada")
        """
        super().__init__(website_name, base_url)
        
        # Override output filename to include output folder
        self.output_filename = os.path.join('output', self._generate_filename())
        
        # Exact selectors with defaults
        self.search_input_id = search_input_id
        self.search_button_id = search_button_id
        self.pagination_select_id = pagination_select_id
        self.distance_select_id = distance_select_id
        
        # Known selectors for GM Collin/YK Canada style websites
        self.results_container_selector = ".addresses"
        self.location_item_selector = "li"
        self.location_name_selector = "h3.name"
        self.location_address_selector = "span.address"
        self.location_city_selector = "span.city"
        self.location_province_selector = "span.prov_state"
        self.location_postal_selector = "span.postal_zip"
        self.location_country_selector = "span.country"
        
        # Postal code prefixes based on country
        self.country = country.lower()
        self.postal_prefixes = POSTAL_CODE_PREFIXES.get(self.country, POSTAL_CODE_PREFIXES['canada'])
    
    def get_fieldnames(self) -> List[str]:
        """Get CSV column names."""
        return [
            "Name", "Address", "Street", "City", 
            "Province_State", "Postal_Code", "Country", "Search_Zip"
        ]
    
    def setup_pagination_and_distance(self) -> bool:
        """
        Set up both pagination and distance limits for maximum results.
        
        Returns:
            bool: True if setup was successful
        """
        success = True
        
        # 1. Set distance limit to "No Limit" (value='0')
        try:
            distance_select_element = self.driver.find_element(By.ID, self.distance_select_id)
            distance_select = Select(distance_select_element)
            
            # Get all available distance options
            distance_options = [(opt.get_attribute('value'), opt.text) for opt in distance_select.options]
            print(f"   Available distance options: {distance_options}")
            
            # Set to "No Limit" (value='0')
            distance_select.select_by_value('0')
            print(f"   ✅ Set distance limit to 'No Limit'")
            
            time.sleep(1)  # Wait for change to take effect
            
        except Exception as e:
            print(f"   ⚠️ Could not set distance limit: {e}")
            success = False
        
        # 2. Modify pagination limit value from 10 to 200
        try:
            # First, let's try to modify the option value directly using JavaScript
            js_modify_pagination = """
            var limitSelect = document.getElementById('limit');
            if (limitSelect && limitSelect.options.length > 0) {
                // Change the first (and likely only) option value from 10 to 200
                limitSelect.options[0].value = '200';
                limitSelect.options[0].text = '200';
                return 'modified';
            }
            return 'not_found';
            """
            
            result = self.driver.execute_script(js_modify_pagination)
            
            if result == 'modified':
                print(f"   ✅ Modified pagination option from '10' to '200'")
                
                # Now select the modified option
                select_element = self.driver.find_element(By.ID, self.pagination_select_id)
                select = Select(select_element)
                select.select_by_value('200')
                print(f"   ✅ Set pagination to 200 results")
                
            else:
                print(f"   ⚠️ Could not modify pagination option")
                success = False
            
            time.sleep(1)  # Wait for change to take effect
            
        except Exception as e:
            print(f"   ⚠️ Could not set pagination: {e}")
            success = False
        
        return success
    
    def parse_address_components(self, full_address: str) -> Dict[str, str]:
        """
        Parse address into components for Canadian addresses.
        
        Args:
            full_address: Full address string
            
        Returns:
            Dictionary with parsed address components
        """
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
        
        return {
            'street': street,
            'city': city,
            'province': province,
            'postal_code': postal_code,
            'country': country
        }
    
    def extract_locations_for_postal_code(self, postal_code: str) -> List[Dict[str, Any]]:
        """
        Extract locations for a specific postal code.
        
        Args:
            postal_code: Postal code to search for
            
        Returns:
            List of location dictionaries
        """
        locations = []
        
        try:
            print(f"🔍 Searching for locations near {postal_code}...")
            
            # Navigate to the store locator
            self.driver.get(self.base_url)
            print(f"   Navigated to {self.base_url}")
            
            # Wait for and find the search input using exact ID
            wait = WebDriverWait(self.driver, 15)
            search_input = wait.until(
                EC.presence_of_element_located((By.ID, self.search_input_id))
            )
            print("   Found search input field")
            
            # Setup distance limit and pagination for maximum results
            self.setup_pagination_and_distance()
            
            # Clear and enter the postal code
            search_input.clear()
            search_input.send_keys(postal_code)
            print(f"   Entered postal code: {postal_code}")
            
            # Find and click search button using exact ID
            search_button = self.driver.find_element(By.ID, self.search_button_id)
            
            try:
                # Try regular click first
                search_button.click()
                print("   Clicked search button")
            except Exception:
                # Try JavaScript click if regular click fails
                self.driver.execute_script("arguments[0].click();", search_button)
                print("   Clicked search button (JavaScript)")
            
            # Wait for results
            print("   Waiting for results...")
            time.sleep(5)
            
            # Check for alert indicating no results
            try:
                WebDriverWait(self.driver, 2).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"   ⚠️ No results found for {postal_code}: Alert Text: {alert_text}")
                alert.accept()
                return locations
            except TimeoutException:
                # No alert means we have results, continue
                pass
            except UnexpectedAlertPresentException as e:
                print(f"   ⚠️ No results found for {postal_code}: {e}")
                return locations
            
            # Wait for results container using exact selector
            try:
                addresses_container = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.results_container_selector))
                )
                print("   Found results container")
            except TimeoutException:
                print(f"   ⚠️ No results container found for {postal_code}")
                return locations
            
            # Get all location elements using exact selector from container
            location_elements = addresses_container.find_elements(By.CSS_SELECTOR, self.location_item_selector)
            
            if not location_elements:
                print(f"   ⚠️ No location elements found for {postal_code}")
                return locations
            
            print(f"   Found {len(location_elements)} location(s)")
            
            # Extract data from each location
            for idx, element in enumerate(location_elements, 1):
                try:
                    # Get name using exact selector
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, self.location_name_selector)
                        name = name_element.text.strip()
                    except NoSuchElementException:
                        print(f"   ⚠️ Error extracting location {idx}: Could not find name element")
                        continue
                    
                    # Get individual address components using exact selectors
                    try:
                        street_element = element.find_element(By.CSS_SELECTOR, self.location_address_selector)
                        street = street_element.text.strip()
                    except NoSuchElementException:
                        print(f"   ⚠️ Error extracting location {idx}: Could not find street address")
                        continue
                    
                    # Get city, province, postal code, and country
                    try:
                        city_element = element.find_element(By.CSS_SELECTOR, self.location_city_selector)
                        city = city_element.text.strip()
                    except NoSuchElementException:
                        city = ""
                    
                    try:
                        province_element = element.find_element(By.CSS_SELECTOR, self.location_province_selector)
                        province = province_element.text.strip()
                    except NoSuchElementException:
                        province = ""
                    
                    try:
                        postal_element = element.find_element(By.CSS_SELECTOR, self.location_postal_selector)
                        postal_code_extracted = postal_element.text.strip()
                    except NoSuchElementException:
                        postal_code_extracted = ""
                    
                    try:
                        country_element = element.find_element(By.CSS_SELECTOR, self.location_country_selector)
                        country = country_element.text.strip()
                    except NoSuchElementException:
                        country = ""
                    
                    if not name or not street:
                        continue
                    
                    print(f"   ✅ Extracted: {name}")
                    
                    # Create full address string
                    address_parts = [street, city, province, postal_code_extracted, country]
                    full_address = ', '.join(part for part in address_parts if part)
                    
                    # Create location data
                    location_data = {
                        "Name": name,
                        "Address": full_address,
                        "Street": street,
                        "City": city,
                        "Province_State": province,
                        "Postal_Code": postal_code_extracted,
                        "Country": country,
                        "Search_Zip": postal_code
                    }
                    
                    locations.append(location_data)
                    
                except Exception as e:
                    print(f"   ⚠️ Error extracting location {idx}: {e}")
                    continue
        
        except Exception as e:
            print(f"   ❌ Error processing {postal_code}: {e}")
        
        return locations
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method for Canadian store locations.
        
        Returns:
            List of unique location dictionaries
        """
        print(f"🔍 Scraping {self.website_name} locations using store locator...")
        print(f"📍 Using {self.country.upper()} postal code prefixes for coverage")
        
        all_locations = []
        unique_locations = {}
        
        # Search using each postal code prefix
        for zip_prefix in self.postal_prefixes:
            print(f"\n--- Searching with postal code prefix: {zip_prefix} ---")
            
            locations = self.extract_locations_for_postal_code(zip_prefix)
            
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