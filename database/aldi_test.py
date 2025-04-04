from scraper import Scraper
from browser import Browser
import aldi
import time

browser = Browser(9222)
sc = Scraper(9222)
html_path = sc.scrape('https://new.aldi.us/results?q=milk')
with open(html_path, 'r') as f:
    content = f.read()
json_data = extract_json(content)
products = extract_products(json)
print(products)
browser.kill()
