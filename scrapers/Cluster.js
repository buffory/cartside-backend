import Walmart from './Walmart.js';
import Kroger from './Kroger.js';
import fs from 'fs';

class Cluster {
    constructor() {
        //this.Walmart = new Walmart({ port: 9222  });
        this.Kroger = new Kroger({ port: 9223 });
    }

    async init() {
        await this.Kroger.init();
        const res = await this.Kroger.scrapeJson({ url: 'https://www.kroger.com/search?query=milk&searchType=default_search' });
        console.log(res);
        //await this.Walmart.init();
        //await this.Walmart.scrapeHTML({ url: 'https://www.walmart.com/search?q=milk' });
    }
}

export default Cluster;
