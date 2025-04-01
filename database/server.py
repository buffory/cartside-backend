from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv

from database import ProductDatabase
from kroger import KrogerProductExtractor

load_dotenv()

app = Flask(__name__)
db = ProductDatabase()

@app.route("/products/similar", methods=["GET"])
def get_similiar():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'missing name param'}), 400

    connection = None
    
    products = db.query_product(name)
    return jsonify(products), 200

@app.route("/save/kroger", methods=["POST"])
def save_data():
    scrape_path = request.path
    products = KrogerProductExtractor.run(scraped_path)
    print(products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
