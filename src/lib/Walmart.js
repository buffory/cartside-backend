import Scraper from './Scraper.js'

const SEARCH_ENDPOINT = 'https://www.walmart.com/search?q={{query}}';

class Walmart extends Scraper {
    constructor({ port }) {
        super({ port });
    }

    async intercept_query({ query }) {
        const request = await this.intercept_urls({ target: 'products-search', urls: [SEARCH_ENDPOINT.replace('{{query}}', query)] });
        console.log(request[0]); 
    }
}

export default Walmart;

