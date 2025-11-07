"""
Base scraper interface that all website scrapers must implement.
Defines the common contract for all scraping operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


class BaseScraper(ABC):
    """
    Abstract base class for all website scrapers.
    Provides common functionality and enforces implementation of required methods.
    """
    
    def __init__(self, website_name: str, base_url: str):
        """
        Initialize the base scraper.
        
        Args:
            website_name: Name of the website (used for file naming)
            base_url: Base URL of the website to scrape
        """
        self.website_name = website_name
        self.base_url = base_url
        self.driver = None
        self.locations = []
        self.output_filename = self._generate_filename()
    
    def _generate_filename(self) -> str:
        """Generate CSV filename based on website name."""
        # Replace dots with underscores and add .csv extension
        safe_name = self.website_name.replace(".", "_")
        return f"{safe_name}.csv"
    
    def setup_driver(self) -> webdriver.Chrome:
        """
        Set up Chrome WebDriver with common options.
        Can be overridden by subclasses if needed.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920x1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.implicitly_wait(10)
            
            print("✅ Chrome driver setup successful")
            return driver
            
        except Exception as e:
            print(f"❌ Error setting up Chrome driver: {e}")
            raise
    
    def save_to_csv(self, fieldnames: List[str]) -> None:
        """
        Save scraped locations to CSV file.
        
        Args:
            fieldnames: List of column names for the CSV file
        """
        try:
            with open(self.output_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for location in self.locations:
                    writer.writerow(location)
            
            print(f"💾 Data saved to {self.output_filename}")
            
        except Exception as e:
            print(f"❌ Error saving to CSV: {e}")
            raise
    
    def cleanup(self) -> None:
        """Clean up resources (close browser, etc.)."""
        if self.driver:
            self.driver.quit()
            print("🔚 Browser closed")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics of the scraping operation.
        
        Returns:
            Dictionary containing summary information
        """
        return {
            "website_name": self.website_name,
            "total_locations": len(self.locations),
            "output_file": self.output_filename
        }
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping method that each scraper must implement.
        
        Returns:
            List of location dictionaries
        """
        pass
    
    @abstractmethod
    def get_fieldnames(self) -> List[str]:
        """
        Get the CSV column names specific to this scraper.
        
        Returns:
            List of field names for CSV headers
        """
        pass
    
    def run(self) -> Dict[str, Any]:
        """
        Complete scraping workflow: setup -> scrape -> save -> cleanup.
        
        Returns:
            Summary dictionary with results
        """
        try:
            print(f"🚀 Starting scraper for {self.website_name}")
            print("=" * 50)
            
            # Setup
            self.driver = self.setup_driver()
            
            # Scrape
            self.locations = self.scrape()
            
            # Save
            if self.locations:
                self.save_to_csv(self.get_fieldnames())
            else:
                print("⚠️ No locations found to save")
            
            # Get summary
            summary = self.get_summary()
            
            return summary
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            raise
        finally:
            self.cleanup()