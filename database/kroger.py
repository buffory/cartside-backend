import json5
import psycopg2
from psycopg2.extras import execute_batch
from bs4 import BeautifulSoup
from typing import Dict, List 
from dotenv import load_dotenv 
import re

def safe_get(data, *keys, default=None):
    """Safely navigate nested dictionaries"""
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, AttributeError):
            return default
    return data

# Kroger-specific extractor
class KrogerProductExtractor:
    @staticmethod
    def run(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        data = KrogerProductExtractor.extract_json(content)
        return data


       # products = KrogerProductExtractor.extract_products(data)
       # return products

    @staticmethod
    def extract_json(html_content):
       """Extracts the complete JSON data using more reliable regex"""
       soup = BeautifulSoup(html_content, 'html.parser')
       script = soup.find('script', string=re.compile('window.__INITIAL_STATE__')) 
       if not script:
           raise ValueError("Could not find window.__INITIAL_STATE__ in the HTML")
    
       # Extract all JSON-like objects using regex
j      json_objects = []
       json_pattern = re.compile(r'\{.*?\}(?=(?:\s*,\s*\{|$))', re.DOTALL)
       
       for match in json_pattern.finditer(script.string):
           try:
               # Clean the string and parse
               json_str = match.group(0)
               ## Handle escaped quotes and newlines
               #json_str = json_str.replace('\\"', '"')
               #json_str = json_str.replace('\\n', '')
              #json_obj = json.loads(json_str)
               json_objects.append(json_str)
           except json.JSONDecodeError:
               continue
       
       return json_objects
      
    @staticmethod
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
                'description': item.get('shortDescription', '').replace('<li>', '').replace('</li>', ' '),
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
    
    @staticmethod
    def clean_description(desc):
        return desc.replace('<li>', '• ').replace('</li>', '\n').strip()

    

# Example Usage
#if __name__ == "__main__":
#    # Load Kroger data
#    with open('next_data.json', 'r') as f:
#        walmart_data = json.load(f)
#    
#    # Extract products
#    walmart_products = KrogerProductExtractor.extract_products(walmart_data)
#    
#    # Save to database
#    db = ProductDatabase()
#    try:
#        db.save_products('Kroger', walmart_products)
#        print(f"Successfully saved {len(walmart_products)} Kroger products")
#    finally:
#        db.close()
