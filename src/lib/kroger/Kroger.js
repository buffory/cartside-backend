import Scraper from '../Scraper.js'

const SEARCH_ENDPOINT = 'https://www.kroger.com/search?query=placeholder&searchType=default';

class Kroger extends Scraper {
    constructor({ port }) {
        super({ port });
    }

    async intercept_query({ query }) {
        const request = await this.intercept_urls({ target: 'products-search', urls: [SEARCH_ENDPOINT.replace('placeholder', query)] });
        console.log(request[0]); 
    }
}

export default Kroger;
