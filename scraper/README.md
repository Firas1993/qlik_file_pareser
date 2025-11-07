# Multi-Website Scraper with Factory Pattern

A flexible, extensible web scraping framework that uses the factory pattern to handle multiple websites with different scraping requirements.

## 🏗️ Architecture

The system is built using the factory pattern with these key components:

### 1. **BaseScraper** (Abstract Base Class)
- Defines the common interface all scrapers must implement
- Provides shared functionality (driver setup, CSV saving, cleanup)
- Forces implementation of `scrape()` and `get_fieldnames()` methods

### 2. **ScraperFactory**
- Creates appropriate scraper instances based on website identifiers
- Maintains a registry of available scrapers
- Supports dynamic registration of new scrapers

### 3. **MainScraper** (Orchestrator)
- Manages the execution workflow across multiple websites
- Uses factory to get appropriate scraper instances
- Provides comprehensive reporting and error handling

### 4. **Individual Scrapers**
- Each website has its own scraper class extending `BaseScraper`
- Implements website-specific scraping logic
- Defines custom CSV field structure

## 📁 File Structure

```
scraper/
├── base_scraper.py         # Abstract base class
├── scraper_factory.py      # Factory pattern implementation  
├── main_scraper.py         # Main execution orchestrator
├── gmcollin_scraper.py     # GM Collin spa scraper
├── example_scraper.py      # Example scraper template
├── test_factory.py         # Factory pattern testing
└── README.md              # This documentation
```

## 🚀 Usage

### Basic Usage
```python
from main_scraper import MainScraper

# Create and run scraper for all configured websites
scraper = MainScraper()
results = scraper.run_all_scrapers()
```

### Adding/Removing Websites
```python
scraper = MainScraper()

# Add a website to scrape
scraper.add_website("example.com")

# Remove a website 
scraper.remove_website("unwanted-site.com")

# Run scraping
results = scraper.run_all_scrapers()
```

### Using Factory Directly
```python
from scraper_factory import ScraperFactory

# Create a specific scraper
scraper = ScraperFactory.create_scraper("gmcollin.ca")
if scraper:
    results = scraper.run()
```

## 🔧 Adding a New Scraper

To add support for a new website:

### 1. Create Scraper Class
```python
from base_scraper import BaseScraper

class YourScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            website_name="yoursite_com", 
            base_url="https://yoursite.com"
        )
    
    def get_fieldnames(self):
        return ["Name", "Address", "Phone"]
    
    def scrape(self):
        # Your scraping logic here
        locations = []
        # ... scraping implementation ...
        return locations
```

### 2. Register with Factory
```python
from scraper_factory import ScraperFactory
from your_scraper import YourScraper

ScraperFactory.register_scraper("yoursite.com", YourScraper)
```

### 3. Add to Main Scraper List
```python
# In main_scraper.py
self.websites_to_scrape = [
    "gmcollin.ca",
    "yoursite.com",  # Add here
]
```

## 📊 Output

Each scraper generates:
- **CSV file**: Named as `website_name.csv` (dots replaced with underscores)
- **Console logs**: Detailed progress and error reporting
- **Summary report**: Statistics and results overview

## 🛠️ Features

### Error Handling
- Graceful handling of website failures
- Continuation of scraping even if one site fails
- Detailed error logging and reporting

### Extensibility
- Easy addition of new scrapers
- Factory pattern allows runtime scraper registration
- Common functionality shared through base class

### Flexibility
- Each scraper can define its own field structure
- Website-specific configuration and logic
- Support for different scraping approaches (Selenium, requests, etc.)

### Data Management
- Automatic CSV generation with proper headers
- Filename sanitization (dots → underscores)
- Future support for data cleaning and filtering

## 🧪 Testing

Run the factory pattern tests:
```bash
python3 test_factory.py
```

Test with example scraper:
```bash
python3 example_scraper.py
```

## 📋 Current Scrapers

| Website | Scraper Class | Status | Locations |
|---------|---------------|--------|-----------|
| gmcollin.ca | GMCollinScraper | ✅ Active | Spa locations across Canada |
| example.com | ExampleScraper | 📝 Demo | Example implementation |

## 🔮 Future Enhancements

- Data cleaning and validation pipeline
- Database storage support
- Configurable output formats (JSON, XML)
- Scheduling and automation
- Rate limiting and respectful crawling
- Proxy rotation support
- Advanced error recovery

## 🤝 Contributing

To add a new scraper:
1. Create scraper class extending `BaseScraper`
2. Implement required methods (`scrape()`, `get_fieldnames()`)
3. Register with factory
4. Add to main scraper list
5. Test thoroughly

## 📝 Notes

- All scrapers automatically get Chrome WebDriver setup
- CSV output uses UTF-8 encoding
- Browser runs in headless mode by default
- Respects website load times with appropriate delays