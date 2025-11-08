"""
YK Canada store locator scraper using default selectors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.canadian_store_scraper import StoreLocatorScraper


class YKCanadaScraper(StoreLocatorScraper):
    """YK Canada scraper using default selectors."""
    
    def __init__(self, enable_phone_extraction: bool = False):
        super().__init__(
            website_name="ykcanada_stores",
            base_url="https://ykcanada.com/apps/store-locator/",
            # Using defaults: search_input_id="address_search", search_button_id="submitBtn", pagination_select_id="limit"
            country="canada",
            enable_phone_extraction=enable_phone_extraction
        )