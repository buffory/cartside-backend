import Kroger from './kroger/Kroger.js'

class Cluster {
    constructor() {
        this.Kroger = new Kroger({ port: 9222  });
    }

    async init() {
        await this.Kroger.init_browser({ chromium_path: 'include/chrome-linux/chrome',
                                         user_data_dir: 'kroger' });
        await this.Kroger.init_CDP();
        const urls = [
            'https://www.kroger.com/search?query=milk&searchType=default'
        ];
        const requests = await this.Kroger.intercept_urls({ target: 'products-search', urls });
    }
}

export default Cluster;
