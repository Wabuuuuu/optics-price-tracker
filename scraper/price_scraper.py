import os
import json
import time
from datetime import datetime
from anthropic import Anthropic
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import base64

try:
    from scraper.config import PRODUCTS, DATABASE_PATH, DELAY_BETWEEN_REQUESTS
except ImportError:
    from config import PRODUCTS, DATABASE_PATH, DELAY_BETWEEN_REQUESTS

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def capture_page_screenshot(driver, url):
    try:
        driver.get(url)
        time.sleep(5)
        screenshot = driver.get_screenshot_as_png()
        return base64.b64encode(screenshot).decode('utf-8')
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def extract_price_with_ai(screenshot_base64, page_html, product_name, retailer):
    try:
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"""Look at this product page screenshot for "{product_name}" from {retailer}.

Find the main product price and tell me if it's in stock.

You MUST respond with ONLY valid JSON in exactly this format:
{{"price": 899.99, "in_stock": true, "currency": "USD"}}

Rules:
- price must be a number like 899.99
- If you cannot find a clear price, use null
- in_stock must be true or false
- Look for the PRIMARY product price

Respond with ONLY the JSON object."""
                        }
                    ],
                }
            ],
        )
        
        response_text = message.content[0].text.strip()
        print(f"  AI Response: {response_text}")
        
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        price_data = json.loads(response_text)
        
        if not isinstance(price_data.get("price"), (int, float, type(None))):
            print(f"  Invalid price format")
            return {"price": None, "in_stock": False, "currency": "USD"}
        
        return price_data
        
    except json.JSONDecodeError as e:
        print(f"  JSON decode error: {e}")
        return {"price": None, "in_stock": False, "currency": "USD"}
    except Exception as e:
        print(f"  Error extracting price: {e}")
        return {"price": None, "in_stock": False, "currency": "USD"}

def scrape_product_prices(product):
    driver = setup_selenium()
    prices = []
    
    for retailer, url in product["urls"].items():
        print(f"Scraping {retailer} for {product['name']}...")
        
        try:
            screenshot = capture_page_screenshot(driver, url)
            page_html = driver.page_source
            
            if screenshot:
                price_data = extract_price_with_ai(screenshot, page_html, product["name"], retailer)
                
                if price_data["price"]:
                    prices.append({
                        "retailer": retailer,
                        "price": price_data["price"],
                        "in_stock": price_data["in_stock"],
                        "url": url,
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"  ✓ Found price: ${price_data['price']}")
                else:
                    print(f"  ⚠ Could not extract price")
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    driver.quit()
    return prices

def update_price_database(product_id, prices):
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, 'r') as f:
            data = json.load(f)
    else:
        data = {"products": {}, "last_updated": None}
    
    if str(product_id) not in data["products"]:
        data["products"][str(product_id)] = {"price_history": []}
    
    data["products"][str(product_id)]["latest_prices"] = prices
    data["products"][str(product_id)]["price_history"].append({
        "date": datetime.now().isoformat(),
        "prices": prices
    })
    
    data["last_updated"] = datetime.now().isoformat()
    
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with open(DATABASE_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Database updated for product {product_id}")

def main():
    print("=" * 60)
    print("AI-Powered Price Scraper Starting...")
    print("=" * 60)
    
    for product in PRODUCTS:
        print(f"\nProcessing: {product['name']}")
        print("-" * 60)
        
        prices = scrape_product_prices(product)
        
        if prices:
            update_price_database(product["id"], prices)
            print(f"✓ Successfully scraped {len(prices)} prices")
        else:
            print("⚠ No prices were successfully scraped")
    
    print("\n" + "=" * 60)
    print("Scraping completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
