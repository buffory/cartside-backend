import Scraper from './Scraper.js';
import { spawn } from 'child_process';

const SEARCH_ENDPOINT = 'https://www.kroger.com/search?query={{query}}&searchType=default';
const PYTHON_PATH = 'database/bin/python';
const SCRIPT = 'kroger_save.py';

class Kroger extends Scraper {
    constructor({ port }) {
        super({ port });
    }

    async scrape({ product }) {
        try {
            const scraped_data = this.scrapeHTML({ url: SEARCH_ENDPOINT.replace('{{query}}', query) });

            if (!scraped_data) {
                return null;
            });
            const res = await save({ htmlPath: scraped_data });
            console.log(res);
        } catch (e) {
            console.error(e);
            return null;
        }
    }

    async save({ htmlPath }) {
        return new Promise((resolve, reject) => {
            const scriptProcess = spawn(PYTHON_PATH, [SCRIPT, htmlPath]);
            let result = '';
            let error = '';

            scriptProcess.stdout.on('data', data => result += data.toString());
            scriptProcess.stderr.on('data', data => error += data.toString());
            scriptProcess.on('close', code => code !=0 ? reject(new Error(error)) : resolve(result));
        });
}

export default Kroger;
