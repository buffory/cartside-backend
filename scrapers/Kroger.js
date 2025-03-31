import Scraper from './Scraper.js';
import { jsonrepair } from 'jsonrepair';
import axios from 'axios';
import { JSDOM } from 'jsdom';

const SEARCH_ENDPOINT = 'https://www.kroger.com/search?query={{query}}&searchType=default';

class Kroger extends Scraper {
    constructor({ port }) {
        super({ port });
    }

    async intercept_query({ query }) {
        await this.cache_requests({ target: 'products-search', url: SEARCH_ENDPOINT.replace('{{query}}', query) });
        return this.cache.requests[0];
    }

    async query({ query }) {
        await this.init();
        const gtins_request = await this.intercept_query({ query });
        const url = gtins_request.url.replace('offset=0', 'offset=24');
        const res = JSON.parse(await this.send_request({ url, headers: gtins_request.headers }));
        const gtins = res['data']['productsSearch'].map(product => product.upc);
        console.log(gtins);
    }

    async scrapeJson({ url }) {
        const html_content = await this.scrapeHTML({ url });
        const dom = new JSDOM(html_content);
        const scripts = dom.window.document.getElementsByTagName('script');
        console.log(scripts.length);

        for (let script of scripts) {
            if (script.textContent.includes('JSON.parse')) {
                const scriptText = script.textContent;
                const start = scriptText.indexOf("JSON.parse('") + 12;
                const end = scriptText.lastIndexOf("')");
                if (start > -1 && end > 1) {
                    let json_str = scriptText.slice(start, end);
                    try {
                        const fixedJson = jsonrepair(json_str);
                        return JSON.parse(fixedJson);
                    } catch (e) {
                        console.error(e)
                        return null;

                    }
                }
            }
        }
        console.error('no json found');
        return null;
    }
}

export default Kroger;
