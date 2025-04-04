import json
import psycopg2
from psycopg2.extras import execute_batch
from bs4 import BeautifulSoup
from typing import Dict, List 
from dotenv import load_dotenv 
import sys
import re

from scraper import Scraper
from database import ProductDatabase

PRODUCTS_URL = "https://new.aldi.us/results?q=QUERY"

def safe_get(data, *keys, default=None):
    """Safely navigate nested dictionaries"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, AttributeError):
            return default
    return data

# Kroger-specific extractor

def scrape(html_path="", query=None, port=None,):
    if query != None and port != None:
        sc = Scraper(port)
        html_path = sc.scrape(PRODUCTS_URL.replace("QUERY", query))
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    product_json = extract_json(content)
    products = extract_products(product_json)
    return products


def extract_json(html_content: str) -> List:
    """Extract the product data array from ALDI's script tags."""
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script')
    
    for script in scripts:
        if not script.string:
            continue
        
        # Look for a large array-like structure at the end of the script
        # ALDI's data is a raw array, not explicitly named like INITIAL_STATE
        match = re.search(r'\[.*\]\s*</script>', script.string, re.DOTALL)
        if match:
            try:
                json_str = match.group(0).replace('</script>', '').strip()
                # Clean up any trailing commas or malformed JSON
                json_str = re.sub(r',\s*\]', ']', json_str)  # Remove trailing commas before ]
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Error at position {e.pos}")
                # Show snippet around error
                start_pos = max(0, e.pos - 50)
                end_pos = min(len(json_str), e.pos + 50)
                error_snippet = json_str[start_pos:end_pos]
                snippet_with_marker = (
                    error_snippet[:e.pos - start_pos] + 
                    "❌>>HERE<<❌" + 
                    error_snippet[e.pos - start_pos:]
                )
                print("Error snippet:")
                print(snippet_with_marker)
                raise
    
    return []

def extract_products(json_data: List) -> List[Dict]:
    """Extract products from ALDI's product array."""
    products = []
    
    # ALDI's array alternates between product metadata and related objects
    # We need to iterate and group related data
    i = 0
    while i < len(json_data):
        # Look for product identifier (SKU-like string)
        if isinstance(json_data[i], str) and json_data[i].startswith('00000000'):
            sku = json_data[i]
            i += 1
            # Next item should be the name
            if i < len(json_data) and isinstance(json_data[i], str):
                name = json_data[i]
                i += 1
                # Next item might be URL slug or price object
                brand = "Unknown"  # ALDI data doesn't consistently provide brand here
                price = None
                image_url = None
                
                # Look for price object
                while i < len(json_data):
                    if isinstance(json_data[i], dict) and 'amount' in json_data[i]:
                        price = json_data[i]['amount'] / 100  # Convert cents to dollars
                        i += 1
                        break
                    i += 1
                
                # Look for image URL in assets
                while i < len(json_data):
                    if isinstance(json_data[i], list):
                        for asset in json_data[i]:
                            if isinstance(asset, dict) and 'url' in asset:
                                image_url = asset['url'].replace('{width}', '300')  # Default width
                                break
                        i += 1
                        break
                    i += 1
                
                # Look for brand in subsequent dict
                while i < len(json_data):
                    if isinstance(json_data[i], dict) and 'brandName' in json_data[i]:
                        brand = json_data[i]['brandName']
                        i += 1
                        break
                    i += 1
                
                # Add product to list
                products.append({
                    'id': sku,
                    'name': name,
                    'brand': brand,
                    'price': price,
                    'image_url': image_url,
                    'product_url': f"https://www.aldi.us/en/products/{sku}"  # Placeholder URL
                })
            else:
                break
        else:
            i += 1
    
    return products
def get_fulfillment_options(item: Dict) -> List[Dict]:
    """Extract fulfillment options (pickup/delivery)"""
    options = []
    fulfillment = item.get('fulfillment', {})
    
    if fulfillment.get('availableForPickup'):
        options.append({
            'type': 'pickup',
            'timeframe': fulfillment.get('pickupDate')
        })
        
    if fulfillment.get('availableForDelivery'):
        options.append({
            'type': 'delivery',
            'timeframe': fulfillment.get('deliveryDate')
        })
        
    if fulfillment.get('availableForShipping'):
        options.append({
            'type': 'shipping',
            'timeframe': fulfillment.get('shippingEstimate')
        })
        
    return options

def get_image_url(item: Dict) -> str:
    """Extract primary product image"""
    images = item.get('images', [])
    if images and isinstance(images, list):
        for img in images:
            if img.get('perspective') == 'front':
                return img.get('sizes', [{}])[0].get('url', '')
    return ''

def clean_description(desc):
    return desc.replace('<li>', '• ').replace('</li>', '\n').strip()

if __name__ == "__main__":
   product = sys.argv[1]
   port = sys.argv[2]

   products = scrape(query=product, port=port)
   print(f"{len(products)} results for {product}")
   db = ProductDatabase()
   db.save_products(retailer_name="Kroger", products=products)

