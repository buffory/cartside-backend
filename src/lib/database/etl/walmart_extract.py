from bs4 import BeautifulSoup
import re
import json

def extract_walmart_products(html_content):
    """Extracts product data from Walmart HTML using known selectors"""
    soup = BeautifulSoup(html_content, 'html.parser')
    products = []
    
    # Main product containers - exact selector from your HTML
    product_containers = soup.select('div[role="group"][data-item-id]')
    
    for container in product_containers:
        try:
            product = {
                'id': container.get('data-item-id'),
                'name': extract_text(container, '[data-automation-id="product-title"]'),
                'price': extract_price(container, '[data-automation-id="product-price"]'),
                'original_price': extract_original_price(container, '.mr1'),
                'unit_price': extract_text(container, '.gray.f6.f5-l'),  # e.g. "2.3 ¢/fl oz"
                'rating': extract_rating(container, '[data-testid="product-ratings"]'),
                'review_count': extract_review_count(container, '[data-testid="product-reviews"]'),
                'image_url': extract_image(container, 'img[loading][src]'),
                'is_sponsored': bool(container.select_one('.f7.flex.items-center div:contains("Sponsored")')),
                'is_snap_eligible': bool(container.select_one('[data-testid="product-badge-text"]:contains("SNAP eligible")')),
                'availability': extract_availability(container),
                'product_url': extract_product_url(container, 'a[link-identifier][href]')
            }
            products.append(clean_product_data(product))
        except Exception as e:
            print(f"Skipping product {container.get('data-item-id')} due to error: {str(e)}")
            continue
    
    return products

# Extraction helpers (optimized for your HTML structure)
def extract_text(container, selector):
    element = container.select_one(selector)
    return element.get_text(' ', strip=True) if element else None

def extract_price(container, selector):
    price_text = container.select_one(selector + ' .b.black.lh-copy')
    return float(re.sub(r'[^\d.]', '', price_text.get_text())) if price_text else None

def extract_original_price(container, selector):
    original = container.select_one(selector + ' .strike')
    return float(re.sub(r'[^\d.]', '', original.get_text())) if original else None

def extract_rating(container, selector):
    rating = container.select_one(selector)
    return float(rating['data-value']) if rating and 'data-value' in rating.attrs else None

def extract_review_count(container, selector):
    reviews = container.select_one(selector)
    return int(reviews['data-value']) if reviews and 'data-value' in reviews.attrs else None

def extract_image(container, selector):
    img = container.select_one(selector)
    return img['src'] if img else None

def extract_product_url(container, selector):
    link = container.select_one(selector)
    return link['href'] if link else None

def extract_availability(container):
    fulfillment = container.select_one('[data-automation-id="fulfillment-badge"]')
    if fulfillment:
        return {
            'pickup': 'Pickup' in fulfillment.get_text(),
            'delivery': 'Delivery' in fulfillment.get_text(),
            'details': fulfillment.get_text(' ', strip=True)
        }
    return None

def clean_product_data(product):
    """Cleans and formats extracted data"""
    # Clean price strings
    for field in ['price', 'original_price']:
        if product.get(field) and isinstance(product[field], str):
            product[field] = float(re.sub(r'[^\d.]', '', product[field]))
    
    # Clean review count
    if product.get('review_count') and isinstance(product['review_count'], str):
        product['review_count'] = int(re.sub(r'\D', '', product['review_count']))
    
    return product

if __name__ == "__main__":
    # Load your HTML file
    with open('scrape.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract products
    products = extract_walmart_products(html_content)
    
    # Save results
    with open('walmart_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully extracted {len(products)} products")
    print("Sample product:", json.dumps(products[0], indent=2) if products else "No products found")
