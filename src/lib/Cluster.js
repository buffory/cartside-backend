import Publix from './Publix.js'
import fs from 'fs';

class Cluster {
    constructor() {
        this.Publix = new Publix({ port: 9222  });
    }

    async init() {
        const res = await this.Publix.query({ query: 'water' });
        fs.writeFile('res.txt', res, error => console.error(error));
    }
}

export default Cluster;
