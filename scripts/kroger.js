// kroger product api endpoint: https://www.kroger.com/atlas/v1/search/v1/products-search?
import { chromium } from 'playwright';
import fs from 'fs';

function log(message) {
    fs.writeFile(
        `${process.pid}-scraper.log`,
        `${new Date()}\t ${message}\n`,
        { flag: 'a+' },
        (err) => console.log(err)
    );
}

(async () => {
    try {
        const endpoint =
            'https://www.kroger.com/atlas/v1/search/v1/products-search?';
        const browser = await chromium.launch({ headless: false });
        const context = await browser.newContext({
            proxy: {
                server: '136.226.84.89:10002',
            },
        });
        const page = await browser.newPage();   
        // await page.setJavaScriptEnabled(false)
        let modRequest = {
            url: '',
            headers: '',
        };

        // page.on('request', async (request) => {
        //     log(`Request: ${request.url()}`);
        // })
        //     .on('console', (message) => log(`Console: ${message.text()}`))
        //     .on('pageerror', ({ message }) => log(`Page Error: ${message}`))
        //     .on('requestfailed', (request) =>
        //         log(
        //             `Request Failed: ${
        //                 request.failure().errorText
        //             }\t ${request.url()}`
        //         )
        //     );
        // .on('requestfinished', (request) => {
        // try {
        //     const response = request.response();
        //     log(`Request Finished: ${response.status()}\t${request.url()}`);
        //     if (request.url().includes(endpoint)) {
        //         const data = response.json()
        //         console.log(data)
        //         // fs.writeFile(`${process.pid}-product-data.json`, JSON.stringify(data), (err) => log(err.message))
        //     }
        // } catch (err) {
        //     log(err)
        // }
        // })
        // .on('response', (response) => {
        //     try {
        //         log(
        //             `Request Finished: ${response.status()}\t${response.url()}`
        //         );
        //         if (response.url().includes(endpoint)) {
        //             const data = response.json()
        //             fs.writeFile(`${process.pid}-product-data.txt`, JSON.stringify(data), (err) => log(err))
        //         }
        //     } catch (err) {
        //         log(err);
        //     }
        // });
        await page.goto(
            'https://www.kroger.com/search?query=milk&searchType=default_search'
        );

        // const responsePromise = page.waitForResponse('**/atlas/v1/search');
        // const response = await responsePromise;
        // const data = await response.json();
        
        // fs.writeFile(
        //     `${process.pid}-product-data.txt`,
        //     JSON.stringify(data),
        //     (err) => log(err)
        // );

    } catch (error) {
        log(error);
    }
})();
