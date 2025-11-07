# 🍁 Canadian Store Locator Scraper

A professional factory pattern-based web scraper designed for Canadian retail store locators, specifically optimized for GM Collin and YK Canada websites.

## 🎯 Features

- **Factory Pattern Architecture**: Clean, extensible design for multiple websites
- **Exact Selectors**: Uses precise element targeting for reliable data extraction  
- **Canadian Postal Code Coverage**: Covers major Canadian regions with strategic postal codes
- **Duplicate Management**: Intelligent deduplication based on name and location
- **CSV Export**: Clean, structured output with comprehensive location data
- **Error Handling**: Robust error handling with detailed logging
- **Browser Automation**: Selenium-based automation with Chrome WebDriver

## 🏗️ Project Structure

```
scraper/
├── common/
│   ├── base_scraper.py              # Base scraper functionality
│   └── canadian_store_scraper.py    # Generic store locator scraper
├── websites/
│   ├── gmcollin_scraper.py          # GM Collin specific implementation  
│   └── ykcanada_scraper.py          # YK Canada specific implementation
├── test/
│   └── test_structure.py            # Factory pattern validation tests
├── output/                          # Generated CSV files
├── main_scraper.py                  # Main execution orchestrator
├── scraper_factory.py              # Website scraper factory
├── requirements.txt                 # Python dependencies
├── install.sh                       # Installation script
└── README.md                        # This file
```

## 🚀 Quick Start

### Installation

1. **Automatic Installation** (Recommended):
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **Manual Installation**:
   ```bash
   pip3 install -r requirements.txt
   ```

### Running the Scraper

```bash
# Run all scrapers (GM Collin + YK Canada)
python3 main_scraper.py

# Test individual scrapers
python3 test_gmcollin.py
python3 test_ykcanada.py
```

## 📋 Requirements

- Python 3.7+
- Chrome browser
- Internet connection

### Python Dependencies

- `selenium>=4.36.0` - Browser automation
- `webdriver-manager>=4.0.0` - Chrome driver management
- `beautifulsoup4>=4.12.0` - HTML parsing
- `requests>=2.31.0` - HTTP requests
- `pandas>=2.0.0` - Data processing
- `lxml>=4.9.0` - XML parsing

## 🌐 Supported Websites

| Website | URL | Status | Locations Found |
|---------|-----|--------|----------------|
| **GM Collin** | `https://www.gmcollin.ca/apps/store-locator/` | ✅ Active | ~34 |
| **YK Canada** | `https://ykcanada.com/apps/store-locator/` | ✅ Active | ~41 |

Both websites use identical HTML structure with exact selectors:
- Search input: `#address_search`
- Submit button: `#submitBtn` 
- Pagination: `#limit`
- Results container: `.addresses`
- Location items: `li`
- Business name: `h3.name`
- Address components: `span.address`, `span.city`, etc.

## 📍 Coverage Strategy

The scraper uses strategic Canadian postal code prefixes to ensure comprehensive coverage:

- **H7N** - Montreal/Laval area, QC
- **M5V** - Toronto area, ON  
- **K1A** - Ottawa area, ON
- **T2P** - Calgary area, AB
- **V6B** - Vancouver area, BC
- **R3C** - Winnipeg area, MB
- **S7K** - Saskatoon area, SK
- **B3H** - Halifax area, NS
- **A1A** - St. John's area, NL
- **Y1A** - Whitehorse area, YT

## 📊 Output Format

Generated CSV files include the following columns:

| Column | Description |
|--------|-------------|
| `Name` | Business/salon name |
| `Address` | Complete formatted address |
| `Street` | Street address only |
| `City` | City name |
| `Province_State` | Province/state code |
| `Postal_Code` | Postal/ZIP code |
| `Country` | Country name |
| `Search_Zip` | Postal code used for search |

## 🔧 Extending the Scraper

### Adding New Websites

1. **Check Compatibility**: Verify if the new website uses the same store locator structure (same selectors)

2. **Create Scraper Class**:
   ```python
   # websites/newsite_scraper.py
   from common.canadian_store_scraper import StoreLocatorScraper
   
   class NewSiteScraper(StoreLocatorScraper):
       def __init__(self):
           super().__init__(
               website_name="newsite_stores",
               base_url="https://newsite.com/apps/store-locator/"
               # Use defaults for selectors if same structure
           )
   ```

3. **Register in Factory**:
   ```python
   # scraper_factory.py
   def create_scraper(website_name: str) -> BaseScraper:
       scrapers = {
           # ... existing scrapers
           "newsite.com": NewSiteScraper,
       }
   ```

4. **Add to Main Scraper**:
   ```python
   # main_scraper.py
   WEBSITES = {
       # ... existing websites  
       "newsite.com": "🆕 New Site",
   }
   ```

### Custom Selectors

If a website uses different selectors, override them in the constructor:

```python
class CustomScraper(StoreLocatorScraper):
    def __init__(self):
        super().__init__(
            website_name="custom_site",
            base_url="https://custom.com/locator/",
            search_input_id="find_address",      # Custom input ID
            search_button_id="find_button",      # Custom button ID  
            pagination_select_id="results_per_page"  # Custom pagination
        )
        
        # Override selectors if needed
        self.location_name_selector = ".business-name"
        self.location_address_selector = ".street-addr"
```

## 🧪 Testing

### Factory Pattern Test
```bash
python3 test/test_structure.py
```

### Individual Website Tests  
```bash
python3 test_gmcollin.py
python3 test_ykcanada.py
```

### Debug Selectors
```bash
python3 debug_selectors.py      # Inspect website structure
python3 debug_gmcollin.py       # GM Collin specific debugging
```

## 📈 Performance

- **Average scraping time**: ~2 minutes per website
- **Locations per minute**: ~15-20 locations
- **Memory usage**: ~50-100MB during execution
- **Network efficient**: Batches postal codes to minimize requests

## ⚠️ Important Notes

1. **Rate Limiting**: Built-in delays between requests to respect website policies
2. **Browser Requirements**: Requires Chrome browser for Selenium automation
3. **Network Dependency**: Requires stable internet connection
4. **Selector Stability**: Designed for current website structures (as of 2024)

## 🛠️ Troubleshooting

### Common Issues

**ChromeDriver errors**: 
- Ensure Chrome browser is installed
- `webdriver-manager` handles driver updates automatically

**No results found**:
- Check if postal codes are valid for the region
- Verify website accessibility
- Review debug output for selector issues

**Import errors**:
- Run `pip3 install -r requirements.txt` 
- Check Python version compatibility (3.7+)

### Debug Mode

Enable detailed logging by running individual test files:
```bash
python3 test_gmcollin.py    # See detailed extraction process
```

## 📝 License

This project is designed for educational and research purposes. Please respect website terms of service and implement appropriate rate limiting for production use.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-website`)  
3. Add your scraper following the factory pattern
4. Test thoroughly with `test_structure.py`
5. Submit pull request

---

**Built with ❤️ for Canadian retail data extraction**