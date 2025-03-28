import Scraper from './Scraper.js';
import { HttpsProxyAgent } from 'https-proxy-agent';

const proxyAgent = new HttpsProxyAgent('http://170.106.106.138:13001');

const url = "https://www.publix.com/search?searchTerm={{query}}&srt=products"
const method = "GET";

class Publix extends Scraper {
    constructor({ port }) {
        super({ port });
    }

    async intercept_query({ query }) {
        const request = await this.intercept_urls({ target: '', urls: [SEARCH_ENDPOINT.replace('{{query}}', query)] });
        console.log(request[0]); 
    }

    async query({ query }) {
        const nUrl = url.replace('{{query}}', `${query}`);

        const response = await fetch(nUrl, { method, agent: proxyAgent });
        return await response.text();
    }

}

export default Publix;
