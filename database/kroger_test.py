from kroger import KrogerProductExtractor
from database import ProductDatabase
from dotenv import load_dotenv
import json
import os

products = KrogerProductExtractor.run('kroger.html')

with open('kroger.json', 'w') as file:
    json.dump(products, file, indent=4)

#db = ProductDatabase()
#try:
#    db.save_products('Kroger', products)
#    print('saved')
#finally:
#    db.close()
