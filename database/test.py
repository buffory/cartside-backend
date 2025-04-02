from kroger import Kroger

k = Kroger(9222)
results = k.scrape(query='milk')
print(results)
