from kroger import KrogerProductExtractor
from database import ProductDatabase
from dotenv import load_dotenv
import json
import os
import sys

path = sys.argv[1]

products = KrogerProductExtractor.run(path)

print('products found:', len(products))

db = ProductDatabase()
try:
    db.save_products('Kroger', products)
    print('saved')
finally:
    db.close()
