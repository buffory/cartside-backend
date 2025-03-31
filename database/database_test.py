from database import ProductDatabase

db = ProductDatabase()
res = db.query_product('milk')
print(res)
db.close()
