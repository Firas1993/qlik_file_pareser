"""
GM Collin spa location scraper using default selectors.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.canadian_store_scraper import StoreLocatorScraper


class GMCollinScraper(StoreLocatorScraper):
    """GM Collin scraper using default selectors."""
    
    def __init__(self):
        super().__init__(
            website_name="gmcollin_spas_ca",
            base_url="https://www.gmcollin.ca/apps/store-locator/",
            # Using defaults: search_input_id="address_search", search_button_id="submitBtn", pagination_select_id="limit"
            country="canada"
        )