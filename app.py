# Replace this line:
# import requests
# API_URL = "http://127.0.0.1:8000"

# With direct imports from your local files:
from database import init_db, get_all_products, add_product
from scraper import fetch_product_price