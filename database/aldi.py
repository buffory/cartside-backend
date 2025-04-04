import json
import psycopg2
from psycopg2.extras import execute_batch
from bs4 import BeautifulSoup
import requests
from typing import Dict, List 
from dotenv import load_dotenv 
import sys
import re

from scraper import Scraper
from database import ProductDatabase

PRODUCTS_URL = "https://api.aldi.us/v3/product-search?currency=USD&serviceType=pickup&q=QUERY&limit=60&offset=0&sort=relevance&testVariant=A&servicePoint=440-018"

def safe_get(data, *keys, default=None):
    """Safely navigate nested dictionaries"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, AttributeError):
            return default
    return data

# Kroger-specific extractor

def scrape(query):
    content = ''
    response = requests.get(PRODUCTS_URL.replace('QUERY', query))
    if response:
        data = response.json()
    else:
        return response

    products = extract_products(data)
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
    products_arr = json_data.get('data')

    for product_obj in products_arr:
        products.append({
            'id': product_obj.get('sku'),
            'brand': product_obj.get('brandName'),
            'name': product_obj.get('name'),
            'price': product_obj.get('price').get('amountRelevantDisplay'),
            'image_url': product_obj.get('assets')[0].get('url').replace('{width}', '500').replace("{slug}", product_obj.get('urlSlugText')),
            'product_url': f"https://new.aldi.us/product/{product_obj.get('urlSlugText')}"
        })

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

   products = scrape(query=product)
   print(f"{len(products)} results for {product}")
   db = ProductDatabase()
   db.save_products(retailer_name="Aldi", products=products)

