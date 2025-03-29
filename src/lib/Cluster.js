import Kroger from './Kroger.js'
import fs from 'fs';

class Cluster {
    constructor() {
        this.Kroger = new Kroger({ port: 9222  });
    }

    async init() {
        const res = await this.Kroger.query({ query: 'water' });
    }
}

export default Cluster;
