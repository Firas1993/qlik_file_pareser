# Canadian Store Locator Scraper - Clean Architecture

## 🏗️ **Why Simple Selectors Instead of Multiple Fallbacks?**

You asked an excellent question! We changed from multiple selectors to exact IDs because:

### **Before** (Multiple Selectors):
```python
'search_button': [
    "button[type='submit']", 
    "input[type='submit']", 
    ".search-button", 
    ".btn-search",
    "button.btn",
    ".btn",
    "button"
]
```

### **After** (Exact ID):
```python
search_button_id = "submitBtn"  # Exact ID
```

## ✅ **Benefits of Exact Selectors:**

1. **Faster execution** - No need to try multiple selectors
2. **More reliable** - Direct targeting of known elements
3. **Cleaner code** - Less complexity and better readability
4. **Predictable behavior** - Same websites, same structure

## 📁 **Cleaned Project Structure**

```
scraper/
├── main_scraper.py           # Main execution
├── scraper_factory.py        # Factory pattern
├── output/                   # CSV files go here
├── test/                     # Test files
│   └── test_structure.py
├── common/                   # Shared components
│   ├── base_scraper.py
│   └── canadian_store_scraper.py  # Generic scraper with defaults
└── websites/                 # Specific implementations
    ├── gmcollin_scraper.py
    └── ykcanada_scraper.py
```

## 🎯 **Default Selectors for Both Websites**

| Element | ID/Selector | Usage |
|---------|-------------|-------|
| Search Input | `address_search` | Where to type postal codes |
| Submit Button | `submitBtn` | Triggers the search |
| Pagination Select | `limit` | Changes results from 10 to 100 |

## 🌍 **Postal Code Constants**

```python
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
        # ... more US zip codes
    ]
    # Easy to add more countries in the future
}
```

## 🚀 **How to Use**

### **Run Both Websites:**
```bash
cd scraper
python3 main_scraper.py
```

### **Add New Website:**
1. Create new scraper class in `websites/`
2. Extend `StoreLocatorScraper`
3. Provide URL and any custom selectors (or use defaults)
4. Register in `scraper_factory.py`

### **Example - New Website:**
```python
class NewWebsiteScraper(StoreLocatorScraper):
    def __init__(self):
        super().__init__(
            website_name="newsite_com",
            base_url="https://newsite.com/store-locator/",
            # Uses defaults: address_search, submitBtn, limit
            country="canada"  # or "usa"
        )
```

## � **Target Websites**

- ✅ **GM Collin**: `https://www.gmcollin.ca/apps/store-locator/`
- ✅ **YK Canada**: `https://ykcanada.com/apps/store-locator/`

## 🎉 **Key Benefits**

1. **Clean & Focused**: Removed unused files (Shoppers, examples)
2. **Organized Output**: All CSV files go to `output/` folder
3. **Exact Selectors**: No guessing - use known IDs
4. **Extensible**: Easy to add new countries and websites
5. **Simple**: Default selectors work for both current websites
6. **Maintainable**: Clear separation of concerns

## 🔧 **Default Configuration**

Both GM Collin and YK Canada use these exact same defaults:
- **Search Input**: `id="address_search"`
- **Submit Button**: `id="submitBtn"`  
- **Pagination**: `id="limit"`
- **Country**: Canada postal codes
- **Output**: `output/` folder

This makes adding similar websites extremely easy!