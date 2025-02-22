import os
import asyncio
import nodriver as uc

async def main():
    browser = await uc.start()
    page = await browser.get('https://www.kroger.com/search?query=milk&searchType=default_search')
    tab = browser.main_tab
    tab.add_handler(uc.cdp.network.ResponseReceived, receive_handler)
    await tab.sleep(10)
    
async def receive_handler(event: uc.cdp.network.ResponseReceived):
    print(event.response)
    with open(f"{os.getpid()}-scraper.log", "a") as f:
        f.write(event.response.url)
    
if __name__ == '__main__':
    uc.loop().run_until_complete(main())