import json
import psycopg2
from psycopg2.extras import execute_batch
from bs4 import BeautifulSoup
from typing import Dict, List
from dotenv import load_dotenv

class ProductDatabase:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="",
            user="your_user",
            password="your_password",
            host="your_host"
        )
        self._ensure_retailers()

    def _ensure_retailers(self):
        """Ensure common retailers exist in the database"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO retailers (name, base_url) 
                VALUES ('Walmart', 'https://www.walmart.com')
                ON CONFLICT (name) DO NOTHING
            """)
            self.conn.commit()

    def _get_retailer_id(self, retailer_name: str) -> int:
        with self.conn.cursor() as cursor:
            cursor.execute(
                "SELECT retailer_id FROM retailers WHERE name = %s",
                (retailer_name,)
            )
            return cursor.fetchone()[0]

    def save_products(self, retailer_name: str, products: List[Dict]):
        """Generic product saving method that works for any retailer"""
        retailer_id = self._get_retailer_id(retailer_name)
        
        # Prepare data for batch insertion
        product_data = []
        variant_data = []
        metric_data = []
        fulfillment_data = []
        
        for product in products:
            # Main product record
            product_data.append({
                'product_id': product['id'],
                'retailer_id': retailer_id,
                'name': product['name'],
                'brand': product['brand'],
                'description': product.get('description'),
                'category': product.get('category')
            })
            
            # Variant information
            variant_data.append({
                'product_id': product['id'],
                'price': product['price'],
                'original_price': product.get('original_price'),
                'in_stock': product.get('in_stock', True),
                'image_url': product.get('image_url'),
                'product_url': product.get('product_url'),
                'specifications': json.dumps(product.get('specifications', {}))
            })
            
            # Metrics
            metric_data.append({
                'product_id': product['id'],
                'rating': product.get('rating'),
                'review_count': product.get('review_count'),
                'bestseller': product.get('is_bestseller', False),
                'popular': product.get('is_popular', False)
            })
            
            # Fulfillment options
            for option in product.get('fulfillment_options', []):
                fulfillment_data.append({
                    'product_id': product['id'],
                    'option_type': option['type'].lower(),
                    'timeframe': option['time'],
                    'price': None  # Can be filled if shipping costs are available
                })
        
        # Execute batch inserts
        with self.conn.cursor() as cursor:
            # Insert products
            execute_batch(cursor, """
                INSERT INTO products 
                (product_id, retailer_id, name, brand, description, category)
                VALUES (%(product_id)s, %(retailer_id)s, %(name)s, %(brand)s, 
                        %(description)s, %(category)s)
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    brand = EXCLUDED.brand,
                    description = EXCLUDED.description,
                    category = EXCLUDED.category,
                    last_updated = CURRENT_TIMESTAMP
            """, product_data)
            
            # Insert variants (using CTE to get the serial ID)
            execute_batch(cursor, """
                WITH inserted_variant AS (
                    INSERT INTO product_variants 
                    (product_id, price, original_price, in_stock, image_url, product_url, specifications)
                    VALUES (%(product_id)s, %(price)s, %(original_price)s, %(in_stock)s, 
                            %(image_url)s, %(product_url)s, %(specifications)s)
                    ON CONFLICT (product_id, sku) DO UPDATE SET
                        price = EXCLUDED.price,
                        original_price = EXCLUDED.original_price,
                        in_stock = EXCLUDED.in_stock,
                        image_url = EXCLUDED.image_url,
                        specifications = EXCLUDED.specifications
                    RETURNING variant_id, product_id
                )
                SELECT variant_id, product_id FROM inserted_variant
            """, variant_data)
            
            # Insert metrics
            execute_batch(cursor, """
                INSERT INTO product_metrics
                (product_id, rating, review_count, bestseller, popular)
                VALUES (%(product_id)s, %(rating)s, %(review_count)s, 
                        %(bestseller)s, %(popular)s)
                ON CONFLICT (product_id) DO UPDATE SET
                    rating = EXCLUDED.rating,
                    review_count = EXCLUDED.review_count,
                    bestseller = EXCLUDED.bestseller,
                    popular = EXCLUDED.popular,
                    updated_at = CURRENT_TIMESTAMP
            """, metric_data)
            
            # Insert fulfillment options
            execute_batch(cursor, """
                INSERT INTO fulfillment_options
                (variant_id, option_type, timeframe, price)
                SELECT v.variant_id, %(option_type)s, %(timeframe)s, %(price)s
                FROM product_variants v
                WHERE v.product_id = %(product_id)s
                ON CONFLICT (variant_id, option_type) DO UPDATE SET
                    timeframe = EXCLUDED.timeframe,
                    price = EXCLUDED.price,
                    updated_at = CURRENT_TIMESTAMP
            """, fulfillment_data)
            
            self.conn.commit()

    def close(self):
        self.conn.close()


# Walmart-specific extractor
class WalmartProductExtractor:
    @staticmethod
    def run(html_file):
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        data = WalmartProductExtractor.extract_json(content)

        if data == None:
            return None

        products = WalmartProductExtractor.extract_json(data)
        return products

    @staticmethod
    def extract_json(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
    
        # walmart stores product json within a script tag with id __NEXT_DATA
        next_data_script: soup.find('script', {'id': '__NEXT_DATA__'})
        if next_data_script:
            json_data = JSON.loads(next_data_script.string)
            return json_data
        else:
            return None

    @staticmethod
    def extract_products(json_data):
        items = json_data['props']['pageProps']['initialData']['searchResult']['itemStacks'][0]['items']
        products = []
        
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
                'is_bestseller': 'Best seller' in [b.get('text') for b in item.get('badges', {}).get('flags', [])],
                'is_popular': 'Popular pick' in [b.get('text') for b in item.get('badges', {}).get('flags', [])],
                'in_stock': item.get('availabilityStatusDisplayValue') == 'In stock',
                'description': WalmartProductExtractor.clean_description(item.get('shortDescription', '')),
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
#    # Load Walmart data
#    with open('next_data.json', 'r') as f:
#        walmart_data = json.load(f)
#    
#    # Extract products
#    walmart_products = WalmartProductExtractor.extract_products(walmart_data)
#    
#    # Save to database
#    db = ProductDatabase()
#    try:
#        db.save_products('Walmart', walmart_products)
#        print(f"Successfully saved {len(walmart_products)} Walmart products")
#    finally:
#        db.close()
