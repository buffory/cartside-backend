import Walmart from './Walmart.js'

class Cluster {
    constructor() {
        this.Walmart = new Walmart({ port: 9222  });
    }

    async init() {
        await this.Walmart.init();
        await this.Walmart.intercept_query({ query: 'milk' });
    }
}

export default Cluster;
