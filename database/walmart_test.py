from walmart import WalmartProductExtractor
from database import ProductDatabase
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv('DB_DB'))
products = WalmartProductExtractor.run('scrape.html')

db = ProductDatabase()
try:
    db.save_products('Walmart', products)
    print('saved')
finally:
    db.close()
