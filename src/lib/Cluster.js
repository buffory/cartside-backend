import Kroger from './kroger/Kroger.js'

class Cluster {
    constructor() {
        this.Kroger = new Kroger({ port: 9222  });
    }

    async init() {
        await this.Kroger.init();
        await this.Kroger.intercept_query({ query: 'milk' });
    }
}

export default Cluster;
