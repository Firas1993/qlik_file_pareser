# 🍁 Canadian Store Locator Scraper

A professional factory pattern-based web scraper designed for Canadian retail store locators, specifically optimized for GM Collin and YK Canada websites.

## ✨ Features

- **🏭 Factory Pattern Architecture**: Extensible design for multiple store locators
- **📍 Enhanced Location Extraction**: Optimized for maximum results (655+ locations)
- **📞 Integrated Phone Number Extraction**: Get phone numbers from Google Maps during scraping
- **🔄 Intelligent Pagination**: Modified to 200 results per page for comprehensive coverage
- **🎯 Distance Control**: Set to "No Limit" for maximum geographic coverage
- **🍁 Canadian Focus**: Optimized for Canadian postal codes and address formats
- **🖥️ Cross-Platform**: Supports Windows, Linux, and macOS
- **📊 CSV Export**: Clean, structured data export with comprehensive location details

## 🏗️ Project Structure

```
scraper/
├── common/
│   ├── base_scraper.py              # Base scraper functionality
│   └── canadian_store_scraper.py    # Generic store locator scraper w/ phone integration
├── websites/
│   ├── gmcollin_scraper.py          # GM Collin specific implementation  
│   └── ykcanada_scraper.py          # YK Canada specific implementation
├── services/
│   ├── __init__.py                  # Services package
│   └── phone_extractor.py           # Google Maps phone number extraction
├── test/
│   └── test_structure.py            # Factory pattern validation tests
├── output/                          # Generated CSV files
├── main_scraper.py                  # Basic scraper (no phones)
├── scrape_with_phones.py            # Enhanced scraper with phone extraction
├── add_phone_numbers.py             # Add phones to existing CSV files
├── demo_phone_extraction.py         # Phone extraction demo
├── test_phone_extraction.py         # Phone validation tests
├── scraper_factory.py              # Website scraper factory
├── requirements.txt                 # Python dependencies
```
├── install.sh                       # Installation script
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** installed on your system
- **Chrome browser** (latest version recommended)
- **Internet connection**

### Installation

#### 🐧 Linux/macOS

1. **Automatic Installation** (Recommended):
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

2. **Manual Installation**:
   ```bash
   pip3 install -r requirements.txt
   ```

#### 🪟 Windows

1. **Verify Python Installation**:
   ```cmd
   python --version
   # or
   python3 --version
   ```
   If Python is not installed, download from [python.org](https://www.python.org/downloads/windows/)

2. **Install Dependencies**:
   ```cmd
   # Using Command Prompt
   pip install -r requirements.txt
   
   # Or using PowerShell
   python -m pip install -r requirements.txt
   ```

3. **Alternative with Virtual Environment** (Recommended):
   ```cmd
   # Create virtual environment
   python -m venv scraper_env
   
   # Activate virtual environment
   # For Command Prompt:
   scraper_env\Scripts\activate
   
   # For PowerShell:
   scraper_env\Scripts\Activate.ps1
   
   # Install dependencies
   pip install -r requirements.txt
   ```

### Running the Scraper

#### 🐧 Linux/macOS
```bash
# Basic scraping (no phone numbers)
python3 main_scraper.py

# Enhanced scraping with phone numbers
python3 scrape_with_phones.py

# Add phones to existing CSV files
python3 add_phone_numbers.py

# Test individual components
python3 test/test_structure.py

# Demo phone extraction
python3 demo_phone_extraction.py
```

#### 🪟 Windows
```cmd
# Basic scraping (no phone numbers)
python main_scraper.py

# Enhanced scraping with phone numbers
python scrape_with_phones.py

# Add phones to existing CSV files
python add_phone_numbers.py

# Test individual components
python test/test_structure.py

# Demo phone extraction
python demo_phone_extraction.py

# If using virtual environment (activate first):
scraper_env\Scripts\activate
```

### 📞 Phone Number Extraction

The scraper now supports **phone number extraction** from Google Maps:

#### **Method 1: Integrated Scraping** (Recommended)
```bash
python3 scrape_with_phones.py
```
- Extracts phone numbers **during** the scraping process
- Avoids rate limits by spacing requests naturally
- Creates CSV files with phone numbers included

#### **Method 2: Post-Processing**
```bash
python3 add_phone_numbers.py
```
- Adds phone numbers to **existing** CSV files
- Useful for enhancing previously scraped data
- Allows processing subsets for testing

#### **Phone Extraction Features:**
- ✅ **No API key required** - uses web scraping
- ✅ **Canadian format support** - (514) 555-1234
- ✅ **Rate limit friendly** - configurable delays
- ✅ **Multiple validation patterns** - handles various phone formats
- ✅ **Headless browser option** - runs in background
python main_scraper.py
```

### 🔧 Windows-Specific Setup Notes

1. **Chrome Driver**: The `webdriver-manager` automatically downloads and manages ChromeDriver, no manual setup needed.

2. **PATH Issues**: If you get "python is not recognized" error:
   - Add Python to your Windows PATH during installation
   - Or use full path: `C:\Python39\python.exe main_scraper.py`

3. **Permission Issues**: Run Command Prompt as Administrator if you encounter permission errors.

4. **PowerShell Execution Policy**: If scripts are blocked in PowerShell:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

5. **Firewall/Antivirus**: Ensure Chrome and Python are allowed through Windows Firewall.

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
| **GM Collin** | `https://www.gmcollin.ca/apps/store-locator/` | ✅ Active | ~418 |
| **YK Canada** | `https://ykcanada.com/apps/store-locator/` | ✅ Active | ~237 |

Both websites use identical HTML structure with exact selectors:
- Search input: `#address_search`
- Submit button: `#submitBtn` 
- Pagination: `#limit` (modified to 200 results)
- Distance limit: `#within_distance` (set to "No Limit")
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

### Common Issues (All Platforms)

**ChromeDriver errors**: 
- Ensure Chrome browser is installed
- `webdriver-manager` handles driver updates automatically
- Restart terminal/command prompt after Chrome installation

**No results found**:
- Check if postal codes are valid for the region
- Verify website accessibility and internet connection
- Review debug output for selector issues

**Import errors**:
- Run `pip install -r requirements.txt` (Windows) or `pip3 install -r requirements.txt` (Linux/macOS)
- Check Python version compatibility (3.7+)

### 🪟 Windows-Specific Issues

**"python is not recognized as an internal or external command"**:
```cmd
# Solution 1: Add Python to PATH during installation
# Solution 2: Use full Python path
C:\Python39\python.exe main_scraper.py

# Solution 3: Use Python Launcher
py main_scraper.py
py -3 main_scraper.py
```

**"Access is denied" or Permission errors**:
```cmd
# Run Command Prompt as Administrator
# Or install to user directory:
pip install --user -r requirements.txt
```

**PowerShell script execution blocked**:
```powershell
# Allow script execution for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single command
powershell -ExecutionPolicy Bypass -File script.ps1
```

**SSL Certificate errors**:
```cmd
# Upgrade pip and certificates
python -m pip install --upgrade pip
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Chrome not found errors on Windows**:
- Install Google Chrome from [chrome.google.com](https://www.google.com/chrome/)
- Restart command prompt after installation
- Check Chrome installation path: `C:\Program Files\Google\Chrome\Application\chrome.exe`

**Virtual environment issues**:
```cmd
# Create new virtual environment
python -m venv --clear scraper_env

# Activate (Command Prompt)
scraper_env\Scripts\activate.bat

# Activate (PowerShell)
scraper_env\Scripts\Activate.ps1

# Deactivate when done
deactivate
```

**Windows Defender/Antivirus blocking**:
- Add Python installation folder to antivirus exceptions
- Add project folder to antivirus exceptions
- Temporarily disable real-time protection during installation

### 🐧 Linux/macOS-Specific Issues

**Permission denied for install.sh**:
```bash
chmod +x install.sh
./install.sh
```

**pip3 not found**:
```bash
# Install pip for Python 3
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3              # macOS with Homebrew
```

### Debug Mode

Enable detailed logging by running test files:

**Windows**:
```cmd
python test/test_structure.py
```

**Linux/macOS**:
```bash
python3 test/test_structure.py
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