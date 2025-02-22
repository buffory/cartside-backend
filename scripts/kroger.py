import os
import asyncio
import nodriver as uc

endpoint_pattern = '/atlas/v1/search'
temp_ids = []

async def main():
    browser = await uc.start()
    page = await browser.get('https://www.kroger.com/search?query=milk&searchType=default_search')
    tab = browser.main_tab
    tab.add_handler(uc.cdp.network.ResponseReceived, receive_handler)
    await tab.sleep(10)

    for temp_id in temp_ids:
        body, is_base64 = await tab.send(uc.cdp.network.get_response_body(temp_id["id"]))
        with open(f"{os.getpid()}-scraper.log", "a+") as f:
            f.write(f"Response received at {temp_id["url"]}:\n{body}\n\n")

    # body, is_base64 = await tab.send(uc.cdp.network.get_response_body(temp_id))
    


    
async def receive_handler(event: uc.cdp.network.ResponseReceived):
    response = event.response
    if ('/atlas/v1/search' in response.url):
        if (response.encoded_data_length > 0):
            temp_ids.append({"url": response.url, "id": event.request_id })
            # log = f"Product data found in {url}\n"
            # with open(f"{os.getpid()}-scraper.log", "a") as f:
            #     f.write(log + response)
    
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())