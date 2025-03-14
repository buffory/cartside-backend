import os
import asyncio
from aiohttp._websocket.reader import WebSocketDataQueue
import json
from nodriver import *
import aiohttp

PRODUCTS_FILE = "kroger-products.json"
LOCATION_ID = "01100638"
OFFSET_INTERVAL = 24
TARGET_ENDPOINT = "products-search"
TARGET_URL = "https://www.kroger.com/atlas/v1/search/v1/products-search?option.facets=TAXONOMY&option.facets=BRAND&option.facets=NUTRITION&option.facets=MORE_OPTIONS&option.facets=PRICE&option.facets=SAVINGS&option.facets=FLAVOR&option.facets=SCENT&option.facets=COLOR&option.groupBy=PRODUCT_VARIANT&filter.locationId=01100638&filter.query=milk&filter.fulfillmentMethods=IN_STORE&filter.fulfillmentMethods=PICKUP&filter.fulfillmentMethods=DELIVERY&filter.fulfillmentMethods=SHIP&page.offset=0&page.size=24&option.personalization=PURCHASE_HISTORY",
PAGE_SIZE = 24


endpoint_pattern = '/atlas/v1/search'
interepted_res = []
products_response = {}
test_query = "milk"

async def main():
    browser = await start(headless=True)
    version = browser.get_version()
    try:
        await browser.get('https://www.kroger.com/search?query=milk&searchType=default_search')
        tab = browser.main_tab
        tab.add_handler(uc.cdp.network.ResponseReceived, receive_handler)
        await tab.sleep(10)

        products = []
        target_res = parse_intercepted_responses(interepted_res)
        await paginate_target(target_res, products)
        # save parsed data
        print(str(len(products)) + " products found.")
        write_products(products)

    finally:
            browser.stop()

# find the response of interest
def parse_intercepted_responses(interepted_res):
    for req in interepted_res:
        url = req["url"]
        if TARGET_ENDPOINT in url:
            return req

# save products to file
def write_products(products):
    with open(PRODUCTS_FILE, "w") as f:
            json.dump({
                "products": products
            }, f, indent=2)

# trim the fat
def parse_products(data):
    return data["data"]["productsSearch"]

# dynamic url interpolation
def interpolate_url(query, location_id, offset, page_size):
    offset = str(offset)
    page_size = str(page_size)
    return f"https://www.kroger.com/atlas/v1/search/v1/products-search?option.facets=TAXONOMY&option.facets=BRAND&option.facets=NUTRITION&option.facets=MORE_OPTIONS&option.facets=PRICE&option.facets=SAVINGS&option.facets=FLAVOR&option.facets=SCENT&option.facets=COLOR&option.groupBy=PRODUCT_VARIANT&filter.locationId={location_id}&filter.query={query}&filter.fulfillmentMethods=IN_STORE&filter.fulfillmentMethods=PICKUP&filter.fulfillmentMethods=DELIVERY&filter.fulfillmentMethods=SHIP&page.offset={offset}&page.size={page_size}&option.personalization=PURCHASE_HISTORY" 

# paginate and save product information
async def paginate_target(res, products):
    headers = res["headers"]
    hasMore = True # hasMore meta wrong in the kroger response
    offset = 0
    i = 0
    async with aiohttp.ClientSession() as session:
        print("Paginating")
        while hasMore:
            url = interpolate_url(test_query, LOCATION_ID, offset, PAGE_SIZE)
            print(f"Page {i}")
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    products.extend(parse_products(data))
                else:
                    hasMore = False


            offset = offset + OFFSET_INTERVAL
            i = i+1
        print("Paginating finished")

# sniff responses
async def receive_handler(event: cdp.network.ResponseReceived):
    response = event.response
    if ('product' in response.url):
        if response.mime_type != "application/json":
            return
        if (response.encoded_data_length > 0):
            interepted_res.append({"url": response.url, "id": event.request_id, "headers": response.headers})
    
    
if __name__ == '__main__':
    loop().run_until_complete(main())
