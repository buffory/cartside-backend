// kroger product api endpoint: https://www.kroger.com/atlas/v1/search/v1/products-search?
import puppeteer from 'puppeteer';
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
        const endpoint = 'https://www.kroger.com/atlas/v1/search/v1/products-search?' 
        const browser = await puppeteer.launch({
            browser: 'firefox',
            headless: false,
            handleSIGINT: false,
            dumpio: true,
            args: ['--incognito'],
        });
        const page = await browser.newPage();
        await page.setRequestInterception(true);
        // await page.setJavaScriptEnabled(false)
        let modRequest = {
            url: '',
            headers: '',
        };

        page.on('request', async (request) => {
            log(`Request: ${request.url()}`);
            request.continue()
        })
            .on('console', (message) => log(`Console: ${message.text()}`))
            .on('pageerror', ({ message }) => log(`Page Error: ${message}`))
            .on('requestfailed', (request) =>
                log(
                    `Request Failed: ${
                        request.failure().errorText
                    }\t ${request.url()}`
                )
            )
            .on('requestfinished', (request) => {
                const response = request.response();
                log(`Request Finished: ${response.status()}\t${request.url()}`);
                if (request.url().includes(endpoint)) {
                    const data = response.json()
                    fs.writeFile(`${process.pid}-product-data.json`, JSON.stringify(data), (err) => log(err.message))
                }
            });

        // page.on('response', (response) => {
        //     const request = response.request();
        //     const url = request.url();
        //     log(url);
        // });

        await page.goto(
            'https://www.kroger.com/search?query=milk&searchType=default_search'
        );

        await page.waitForNavigation();

        // const modResponse = await page.evaluate(async (modRequest) => {
        //     console.log(modRequest.headers)
        //     const response = await fetch(modRequest.url, {headers: modRequest.headers})
        //     const data = await response.json()
        //     console.log(data)
        //     return data
        // }, modRequest)

        // log(modResponse)

        const productResponse = await page.waitForResponse(
            'https://www.kroger.com/atlas/v1/search/v1/products-search?'
        );

        console.log(productResponse.json());
    } catch (error) {
        log(error);
    }
})();
