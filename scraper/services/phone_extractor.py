"""
Google Maps Phone Number Extractor Service
Fetches phone numbers for existing store locations using Google Maps web scraping
"""

import pandas as pd
import time
import random
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import os
import logging

class GoogleMapsPhoneExtractor:
    """Extract phone numbers from Google Maps for given addresses"""
    
    def __init__(self, headless=True, delay_range=(2, 5)):
        """
        Initialize the phone extractor
        
        Args:
            headless (bool): Run browser in headless mode
            delay_range (tuple): Random delay range between requests
        """
        self.headless = headless
        self.delay_range = delay_range
        self.driver = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('phone_extraction.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome WebDriver with optimized settings"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
                
            # Optimize for speed and stealth
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.logger.info("✅ Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup WebDriver: {str(e)}")
            return False
            
    def search_google_maps(self, business_name, address):
        """
        Search for business on Google Maps and extract phone number
        
        Args:
            business_name (str): Name of the business
            address (str): Full address of the business
            
        Returns:
            str: Phone number or None if not found
        """
        try:
            # Construct search query
            search_query = f"{business_name} {address}"
            search_url = f" "
            
            self.logger.info(f"🔍 Searching: {business_name}")
            self.driver.get(search_url)
            
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-result-index]"))
            )
            
            # Random delay to appear more human-like
            time.sleep(random.uniform(*self.delay_range))
            
            # Try to click on the first result
            try:
                first_result = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-result-index='0']"))
                )
                first_result.click()
                
                # Wait for business details to load
                time.sleep(3)
                
            except TimeoutException:
                self.logger.warning(f"⚠️ Could not click first result for {business_name}")
                
            # Extract phone number using multiple selector strategies
            phone_selectors = [
                "button[data-item-id*='phone']",
                "[data-item-id*='phone'] span",
                "span[data-phone]",
                "button[jsaction*='phone']",
                "[aria-label*='Phone']",
                "span:contains('+')",  # Common for Canadian numbers
                "button[aria-label*='Call']"
            ]
            
            phone_number = None
            
            for selector in phone_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based search
                        elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), '+')]")
                        for element in elements:
                            text = element.get_attribute('innerText')
                            if self.is_valid_phone(text):
                                phone_number = self.clean_phone_number(text)
                                break
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            text = element.get_attribute('innerText') or element.get_attribute('aria-label') or element.text
                            if text and self.is_valid_phone(text):
                                phone_number = self.clean_phone_number(text)
                                break
                                
                    if phone_number:
                        break
                        
                except Exception as e:
                    continue
                    
            # If no phone found in buttons/spans, search in all visible text
            if not phone_number:
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    phone_match = re.search(r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})', page_text)
                    if phone_match:
                        phone_number = self.clean_phone_number(phone_match.group())
                        
                except Exception:
                    pass
                    
            if phone_number:
                self.logger.info(f"✅ Found phone: {phone_number}")
            else:
                self.logger.warning(f"❌ No phone found for {business_name}")
                
            return phone_number
            
        except Exception as e:
            self.logger.error(f"❌ Error searching for {business_name}: {str(e)}")
            return None
            
    def is_valid_phone(self, text):
        """Check if text contains a valid phone number pattern"""
        if not text:
            return False
            
        # Canadian/US phone number patterns
        patterns = [
            r'\+?1[-.\s]?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-xxx-xxx-xxxx
            r'\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}',              # (xxx) xxx-xxxx
            r'[2-9]\d{2}[-.\s]?\d{3}[-.\s]?\d{4}'                     # xxx-xxx-xxxx
        ]
        
        for pattern in patterns:
            if re.search(pattern, text):
                return True
        return False
        
    def clean_phone_number(self, phone_text):
        """Clean and format phone number"""
        if not phone_text:
            return None
            
        # Extract digits and format
        digits = re.sub(r'[^\d]', '', phone_text)
        
        # Handle Canadian numbers (remove leading 1 if present)
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]
        elif len(digits) == 10:
            pass
        else:
            return phone_text.strip()  # Return original if unusual format
            
        # Format as (xxx) xxx-xxxx
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        else:
            return phone_text.strip()
            
    def process_csv_file(self, csv_file_path, output_file_path, max_records=None):
        """
        Process CSV file and add phone numbers
        
        Args:
            csv_file_path (str): Path to input CSV file
            output_file_path (str): Path to output CSV file with phone numbers
            max_records (int): Maximum number of records to process (for testing)
        """
        try:
            # Read CSV file
            df = pd.read_csv(csv_file_path)
            self.logger.info(f"📖 Loaded {len(df)} records from {csv_file_path}")
            
            # Limit records for testing
            if max_records:
                df = df.head(max_records)
                self.logger.info(f"🎯 Processing first {max_records} records for testing")
                
            # Add phone column
            df['Phone'] = None
            
            # Setup driver
            if not self.setup_driver():
                return False
                
            successful_extractions = 0
            
            for index, row in df.iterrows():
                try:
                    business_name = row['Name']
                    address = row['Address']
                    
                    self.logger.info(f"📞 Processing {index + 1}/{len(df)}: {business_name}")
                    
                    phone = self.search_google_maps(business_name, address)
                    df.at[index, 'Phone'] = phone
                    
                    if phone:
                        successful_extractions += 1
                        
                    # Add delay between requests
                    time.sleep(random.uniform(*self.delay_range))
                    
                except KeyboardInterrupt:
                    self.logger.info("⏹️ Process interrupted by user")
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error processing {business_name}: {str(e)}")
                    continue
                    
            # Save results
            df.to_csv(output_file_path, index=False)
            
            self.logger.info(f"✅ Processing complete!")
            self.logger.info(f"📊 Results: {successful_extractions}/{len(df)} phone numbers found")
            self.logger.info(f"💾 Saved to: {output_file_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error processing CSV file: {str(e)}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()


def main():
    """Main function for testing"""
    extractor = GoogleMapsPhoneExtractor(headless=False)  # Set False to see browser
    
    # Test with small sample first
    test_csv = "output/gmcollin_spas_ca.csv"
    output_csv = "output/gmcollin_spas_with_phones.csv"
    
    print("🚀 Starting phone number extraction...")
    print("📝 Processing first 5 records as test...")
    
    success = extractor.process_csv_file(test_csv, output_csv, max_records=5)
    
    if success:
        print("\n✅ Test completed successfully!")
        print(f"📁 Check results in: {output_csv}")
    else:
        print("\n❌ Test failed!")


if __name__ == "__main__":
    main()