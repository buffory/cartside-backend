import CDP from 'chrome-remote-interface';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';

class Scraper {
    constructor({ port }) {
        this.port = port;
        this.target_request = {};
        this.browser = null;
        this.id = crypto.randomUUID();
        this.intercepting = false;
        this.cache = {
            requests: []
        };
    }

    async log(msg) {
        const data = `${msg} ${this.id} ${new Date()}\n`;
        await fs.appendFile(`${this.id}.log`, data);
    }

    async init() {
        await this.init_browser({ chromium_path: './scrapers/chrome-linux/chrome',
                                  user_data_dir: `${this.id}-tmp` });
        await this.init_CDP();
    }


    async init_browser({ chromium_path, user_data_dir }) {
        const browser = spawn(chromium_path, [
            `--remote-debugging-port=${this.port}`,
            `--incognito`,
            `--disk-cache-dir=/dev/null`,
            //`--headless`

        ]);

        while (1) {
            try {
                const response = await fetch(`http://localhost:${this.port}/json/version`);
                if (response.ok) {
                    this.browser = browser;
                    break;
                }
          } catch {
                await new Promise(resolve => setTimeout(resolve, 500));
            }
        }
        this.log(`Browser on ${this.port}`);
    }
    
    async init_CDP() {
        this.client = await CDP({ port: this.port });
        await Promise.all([
            this.client.Network.enable(),
            this.client.Page.enable(),
            this.client.Runtime.enable()
        ]);
        this.log(`CDP initiated`);
    }

    async scrapeHTML({ url }) {
        const host_name = new URL(url).hostname.split('.')[1]
        await this.client.Page.navigate({ url });
        await this.client.Page.loadEventFired();

        const result = await this.client.Runtime.evaluate({
            expression: 'document.documentElement.outerHTML',
            returnByValue: true
        });

        const htmlContent = result.result.value;
        const crypt = crypto.randomUUID();
        const file_name = `data/${host_name}-${crypt}.html`;
        const file_url = new URL(file_name, import.meta.url);
        try {

            await fs.writeFile(file_url, htmlContent, err => console.error(err));
            return file_url.href.replace('file://', '');
        } catch (e) {
            console.error(e);
            return null;
        }
    }
        

    async cache_requests({ target, url }) {
        const requests = [];

        await this.client.Network.setRequestInterception({ patterns: [{ urlPattern: '*' }] });

        this.client.Network.requestIntercepted(async ({ interceptionId, request}) => {
                const modHeaders = request.headers;
                modHeaders['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36";
                modHeaders['sec-ch-ua'] = '" Not A;Brand";v="99", "Windows";v="96", "Chrome";v="96"';
                modHeaders['sec-ch-ua-platform'] = '"Windows"';

                if (request.url.includes(target)) {
                    this.cache.requests.push({...request, headers: modHeaders});
                }

                await this.log(`${request.url} intercepted\n ${JSON.stringify(modHeaders)}`);
                await this.client.Network.continueInterceptedRequest({ interceptionId, headeons: modHeaders });
        });

        await this.client.Page.navigate({ url });
        await this.client.Page.loadEventFired();
    }

    async get_cache() {
        return this.cache;
    }

    async send_request({ url, headers }) {
        const str_headers = JSON.stringify(headers);
        const fetchScript = `
                fetch('${url}', {
                    method: 'GET',
                    headers: ${str_headers}
                })
                .then(response => response.text())
                .then(text => text)
                .catch(error => error)
        `;

        // Execute the fetch in browser context
        const result = await this.client.Runtime.evaluate({
            expression: fetchScript,
            awaitPromise: true // Wait for the Promise to resolve
        });

        // Get the result value
        const fetchResult = result.result.value;

        return fetchResult;
    }
}

export default Scraper;
