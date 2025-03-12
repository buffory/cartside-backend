import os
import asyncio
import nodriver as uc
import json

PRODUCTS_FILE = "kroger-products.json"
LOCATION_ID = "01100638"
endpoint_pattern = '/atlas/v1/search'
temp_ids = []

async def main():
    browser = await uc.start()
    try:
        page = await browser.get('https://www.kroger.com/search?query=milk&searchType=default_search')
        tab = browser.main_tab
        tab.add_handler(uc.cdp.network.ResponseReceived, receive_handler)
        await tab.sleep(10)

        products = []

        for temp_id in temp_ids:
            try:
                body, is_base64 = await tab.send(uc.cdp.network.get_response_body(temp_id["id"]))
                decoded_body = body.decode('utf-8') if is_base64 else body
                with open(f"{os.getpid()}-scraper.log", "a+") as f:
                    f.write(f"Response received at {temp_id["url"]}:\n{body}\n\n")
 
                data = json.loads(decoded_body)

                

                
            except Exception as e:
                print(f"Error processing {temp_id['url']}: {e}")

    # save parsed data
        print(str(len(products)) + " products found.")
        with open(PRODUCTS_FILE, "w") as f:
            json.dump({
                "products": products
            }, f, indent=2)

    finally:
            browser.stop()

async def fetch_next_page(browser, prev_offset, offset):
    current_offset = str(prev_offset + offset)
    next_url = f"https://www.kroger.com/atlas/v1/search/v1/products-search?filter.query=milk&filter.locationId={LOCATION_ID}&page.offset={current_offset}&page.size=24"
    page = await browser.get(next_url)
    await page.wait(10)

    body, is_base64 = await tab.send(uc.cdp.network.get_response_body())

async def receive_handler(event: uc.cdp.network.ResponseReceived):
    response = event.response
    if ('product' in response.url):
        if response.mime_type != "application/json":
            return
        if (response.encoded_data_length > 0):
            temp_ids.append({"url": response.url, "id": event.request_id })
            # log = f"Product data found in {url}\n"
            # with open(f"{os.getpid()}-scraper.log", "a") as f:
            #     f.write(log + response)
    
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())