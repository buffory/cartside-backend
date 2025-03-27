import Scraper from '../Scraper.js'

class Kroger extends Scraper {
    constructor({ port, target_endpoint }) {
        super({ port, target_endpoint });
    }
}

export default Kroger;
