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

You MUST respond with ONLY valid JSON in exactly this format with no other text:
{{"price": 899.99, "in_stock": true, "currency": "USD"}}

Rules:
- price must be a number like 899.99 (no dollar signs, no commas)
- If you cannot find a clear price, use null
- in_stock must be true or false
- If the page says "out of stock" or "unavailable", set in_stock to false
- Look for the PRIMARY product price, ignore related items

Respond with ONLY the JSON object, nothing else."""
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
            print(f"  Invalid price format: {price_data.get('price')}")
            return {"price": None, "in_stock": False, "currency": "USD"}
        
        return price_data
        
    except json.JSONDecodeError as e:
        print(f"  JSON decode error: {e}")
        print(f"  Response was: {response_text[:
