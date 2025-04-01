import json
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


        products = KrogerProductExtractor.extract_products(data)
        return products

    @staticmethod
    def extract_json(html_content: str) -> Dict:
       """Extract the __INITIAL_STATE__ from script tags"""
       soup = BeautifulSoup(html_content, 'html.parser')
       scripts = soup.find_all('script')
       
       for script in scripts:
           if not script.string:
               continue
               
           # Look for the INITIAL_STATE pattern
           match = re.search(r'window\.__INITIAL_STATE__\s*=\s*JSON\.parse\(([\'"])(.*?)\1\)', script.string)
           if match:
               try:
                   # The JSON string might contain escaped quotes
                   json_str = match.group(2).replace(r"\'", "'")
                   json_str = json_str.replace(r"\\", "\\")
                   return json.loads(json_str)
               except json.JSONDecodeError as e:
                   # Print error details and surrounding text
                   print(f"JSON parsing error: {e}")
                   print(f"Error at position {e.pos} (char {e.pos})")
                   
                   # Show 50 characters before and after the error position

                   error_snippet = json_str[start_pos:end_pos]
                   
                   # Indicate where the error occurs with markers
                   snippet_with_marker = (
                       error_snippet[:e.pos - start_pos] + 
                       "❌>>HERE<<❌" + 
                       error_snippet[e.pos - start_pos:]
                   )
                   
                   print("Error snippet:")
                   print(snippet_with_marker)
                   raise  # Re-raise the exception if you want the program to stop
                  
       return {} 

    @staticmethod
    def extract_products(json_data):
        """Extract products from Kroger's initial state"""
        products = []
        
        # Navigate through Kroger's specific structure
        product_data = safe_get(
            json_data,
            'calypso', 'useCases', 'getProducts', 'search-grid', 'response', 'data', 'products',
            default=[]
        )
        #print(json_data.get('calypso').get('getProducts'))
        for item in product_data:
            if not isinstance(item, dict):
                continue
                
            print(item)
            #products.append(item)
            # Handle pricing - Kroger often has promo prices
            #price_info = item.get('price', {})
            #current_price = price_info.get('regular')
            #promo_price = price_info.get('promo')
            #
            try:
                products.append({
                    'id': item.get('id'),
                #    'upc': item.get('upc'),
                    'description': item.get('item').get('romanceDescription'),
                    'name': item.get('item').get('description'),
                    'brand': item.get('item').get('brand').get('name'),
                    'price': item.get('price').get('storePrices').get('regular').get('defaultDescription'),
                #    'original_price': float(current_price) if current_price and promo_price else None,
                #    'size': item.get('size'),
                    'image_url': item.get('item').get('images')[0].get('url'),
                    'product_url': item.get('item').get('shareLink'),
                #    'is_on_sale': bool(promo_price),
                #    'in_stock': item.get('inventory', {}).get('stockLevel') != 'out_of_stock',
                #    'category': safe_get(item, 'categories', 0, 'description'),
                #    'rating': float(item.get('averageRating', 0)),
                #    'review_count': int(item.get('reviewCount', 0)),
                #    'fulfillment_options': KrogerProductExtractor.get_fulfillment_options(item)
                })
            except AttributeError:
                continue
        
        return products

    @staticmethod
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
    
    @staticmethod
    def get_image_url(item: Dict) -> str:
        """Extract primary product image"""
        images = item.get('images', [])
        if images and isinstance(images, list):
            for img in images:
                if img.get('perspective') == 'front':
                    return img.get('sizes', [{}])[0].get('url', '')
        return ''

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
