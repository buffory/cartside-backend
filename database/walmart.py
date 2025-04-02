import json
import psycopg2
from psycopg2.extras import execute_batch
from bs4 import BeautifulSoup
from typing import Dict, List
from dotenv import load_dotenv
import sys

from scraper import Scraper

PRODUCTS_URL = "https://www.walmart.com/search?q=QUERY"

def safe_get(data, *keys, default=None):
    """Safely navigate nested dictionaries"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, AttributeError):
            return default
    return data


def scrape(html_path="", query=None, port=None,):
    if query != None and port != None:
        sc = Scraper(port)
        html_path = sc.scrape(PRODUCTS_URL.replace("QUERY", query))
    
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    product_json = extract_json(content)
    products = extract_products(product_json)
    return products



def extract_json(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # walmart stores product json within a script tag with id __NEXT_DATA
    next_data_script = soup.find('script', {'id': '__NEXT_DATA__'})
    if next_data_script:
        json_data = json.loads(next_data_script.string)
        return json_data
    else:
        return None


def extract_products(json_data):
 # Safely navigate the nested JSON structure
    item_stacks = safe_get(json_data, 'props', 'pageProps', 'initialData', 'searchResult', 'itemStacks', default=[])
    
    if not item_stacks:
        print("Warning: No itemStacks found in JSON data")
        return []
    
    # Get items from the first stack (or empty list if none exists)
    items = safe_get(item_stacks[0], 'items', default=[])
    
    if not items:
        print("Warning: No items found in the first itemStack")
        return []
    
    products = []
    
    for item in items:
        if not isinstance(item, dict):
            continue
    
    for item in items:
        if item.get('__typename') != 'Product':
            continue
            
        products.append({
            'id': item.get('usItemId'),
            'name': item.get('name'),
            'brand': item.get('brand'),
            'price': item.get('price', 0),
            'original_price': None,  # Could extract from wasPrice if available
            'rating': item.get('rating', {}).get('averageRating'),
            'review_count': item.get('rating', {}).get('numberOfReviews'),
            'image_url': item.get('image'),
            'product_url': f"https://www.walmart.com{item.get('canonicalUrl', '')}",
           # 'is_bestseller': 'Best seller' in [b.get('text') for b in item.get('badges', {}).get('flags', [])],
           # 'is_popular': 'Popular pick' in [b.get('text') for b in item.get('badges', {}).get('flags', [])],
           # 'in_stock': item.get('availabilityStatusDisplayValue') == 'In stock',
            'description': item.get('shortDescription'),
            'category': '/'.join(item.get('category', {}).get('categoryPathId', '').split(':')[1:]),
            'fulfillment_options': [
                {
                    'type': group.get('key', '').replace('FF_', ''),
                    'time': group.get('slaText', '')
                } 
                for group in item.get('fulfillmentBadgeGroups', [])
                if isinstance(group, dict)
            ],
            'specifications': {
                'nutritional_content': [
                    val['id'] for val in 
                    next((f['values'] for f in item.get('configs', {}).get('allSortAndFilterFacets', [])
                         if f.get('name') == 'Nutritional Content'), [])
                ],
                'milk_type': item.get('catalogProductType')
            }
        })
    
    return products


def clean_description(desc):
    return desc.replace('<li>', '• ').replace('</li>', '\n').strip()

    

if __name__ == "__main__":
   product = sys.argv[1]
   port = sys.argv[2]

   products = scrape(query=product, port=port)
   print(f"{len(products)} results for {product}")
   db = ProductDatabase()
   db.save_products(retailer_name="Walmart", products=products)
