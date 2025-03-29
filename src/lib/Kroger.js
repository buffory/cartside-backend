import Scraper from './Scraper.js';
import axios from 'axios';

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
        const res = await this.send_request({ url, headers: gtins_request.headers });
        console.log(res);
        
    }

}

export default Kroger;
