import psycopg2
import re
from datetime import datetime
from psycopg2 import sql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
def setup_database():
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'product_data'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )
    conn.autocommit = False
    cursor = conn.cursor()
    
    # Create tables with PostgreSQL syntax
    try:
        # Retailers table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS retailers (
            retailer_id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            base_url VARCHAR(255),
            last_scraped TIMESTAMP
        )
        ''')
        
        # Products table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            retailer_id INTEGER REFERENCES retailers(retailer_id),
            name VARCHAR(255) NOT NULL,
            description TEXT,
            category VARCHAR(100),
            brand VARCHAR(100),
            current_price DECIMAL(10, 2),
            original_price DECIMAL(10, 2),
            price_unit VARCHAR(50),
            rating DECIMAL(3, 1),
            review_count INTEGER,
            is_sponsored BOOLEAN DEFAULT FALSE,
            is_snap_eligible BOOLEAN DEFAULT FALSE,
            product_url TEXT,
            image_url TEXT,
            last_updated TIMESTAMP,
            CONSTRAINT unique_product_per_retailer UNIQUE (retailer_id, product_url)
        )
        ''')
        
        # Inventory table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            inventory_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
            fulfillment_type VARCHAR(50),  -- 'pickup', 'delivery', 'shipping'
            availability VARCHAR(50),     -- 'in_stock', 'out_of_stock', 'limited'
            estimated_delivery VARCHAR(100),
            location_id VARCHAR(100),    -- store ID or warehouse location
            last_checked TIMESTAMP,
            CONSTRAINT unique_inventory_entry UNIQUE (product_id, fulfillment_type)
        )
        ''')
        
        # Price history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            price_id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
            price DECIMAL(10, 2),
            date_recorded TIMESTAMP,
            CONSTRAINT unique_price_record UNIQUE (product_id, date_recorded)
        )
        ''')
        
        # Add Walmart to retailers if not exists
        cursor.execute('''
        INSERT INTO retailers (retailer_id, name, base_url) 
        VALUES (1, 'Walmart', 'https://www.walmart.com')
        ON CONFLICT (retailer_id) DO NOTHING
        ''')
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error setting up database: {e}")
        raise
    
    return conn

# (Keep all the scraping functions the same as in the previous version)
# Walmart scraper and helper functions would remain identical...

# Modified database operations for PostgreSQL
def save_to_database(conn, products, retailer_id=1):
    cursor = conn.cursor()
    now = datetime.now()
    
    try:
        for product in products:
            # Insert or update product (PostgreSQL UPSERT)
            cursor.execute('''
            INSERT INTO products (
                retailer_id, name, description, brand, current_price, 
                price_unit, rating, review_count, is_sponsored, 
                is_snap_eligible, product_url, image_url, last_updated
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (retailer_id, product_url) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                brand = EXCLUDED.brand,
                current_price = EXCLUDED.current_price,
                price_unit = EXCLUDED.price_unit,
                rating = EXCLUDED.rating,
                review_count = EXCLUDED.review_count,
                is_sponsored = EXCLUDED.is_sponsored,
                is_snap_eligible = EXCLUDED.is_snap_eligible,
                image_url = EXCLUDED.image_url,
                last_updated = EXCLUDED.last_updated
            RETURNING product_id
            ''', (
                retailer_id,
                product.get('name'),
                product.get('description'),
                product.get('brand'),
                product.get('price'),
                product.get('price_unit'),
                product.get('rating'),
                product.get('review_count'),
                product.get('is_sponsored', False),
                product.get('is_snap_eligible', False),
                product.get('product_url'),
                product.get('image_url'),
                now
            ))
            
            product_id = cursor.fetchone()[0] if cursor.rowcount > 0 else None
            
            if product_id and product.get('price'):
                # Record price history
                cursor.execute('''
                INSERT INTO price_history (product_id, price, date_recorded)
                VALUES (%s, %s, %s)
                ON CONFLICT (product_id, date_recorded) DO NOTHING
                ''', (product_id, product.get('price'), now))
            
            if product_id and product.get('fulfillment'):
                fulfillment = product.get('fulfillment')
                if fulfillment.get('pickup'):
                    cursor.execute('''
                    INSERT INTO inventory (
                        product_id, fulfillment_type, availability, estimated_delivery, last_checked
                    ) VALUES (%s, 'pickup', 'in_stock', %s, %s)
                    ON CONFLICT (product_id, fulfillment_type) DO UPDATE SET
                        availability = EXCLUDED.availability,
                        estimated_delivery = EXCLUDED.estimated_delivery,
                        last_checked = EXCLUDED.last_checked
                    ''', (product_id, fulfillment.get('details'), now))
                
                if fulfillment.get('delivery'):
                    cursor.execute('''
                    INSERT INTO inventory (
                        product_id, fulfillment_type, availability, estimated_delivery, last_checked
                    ) VALUES (%s, 'delivery', 'in_stock', %s, %s)
                    ON CONFLICT (product_id, fulfillment_type) DO UPDATE SET
                        availability = EXCLUDED.availability,
                        estimated_delivery = EXCLUDED.estimated_delivery,
                        last_checked = EXCLUDED.last_checked
                    ''', (product_id, fulfillment.get('details'), now))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error saving to database: {e}")
        raise

# Main execution (same as before)
if __name__ == "__main__":
    # Set up database
    conn = setup_database()
    
    try:
        # Scrape Walmart for milk products
        print("Scraping Walmart for milk products...")
        milk_products = scrape_walmart_search("milk")
        
        # Save to database
        print(f"Saving {len(milk_products)} products to database...")
        save_to_database(conn, milk_products)
        
    finally:
        # Close connection
        conn.close()
        print("Done!")
