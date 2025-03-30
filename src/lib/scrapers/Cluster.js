import Walmart from './Walmart.js'
import fs from 'fs';

class Cluster {
    constructor() {
        this.Walmart = new Walmart({ port: 9222  });
    }

    async init() {
        await this.Walmart.init();
        await this.Walmart.scrapeHTML({ url: 'https://www.walmart.com/search?q=milk' });
    }
}

export default Cluster;
