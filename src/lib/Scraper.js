import CDP from 'chrome-remote-interface';
import fetch from 'node-fetch';
import { spawn } from 'child_process';
import { promises as fs } from 'fs';

class Scraper {
    constructor({ port }) {
        this.port = port;
        this.target_request = {};
        this.browser = null;
        this.id = crypto.randomUUID();
        this.intercepting = false;
    }

    async log(msg) {
        const data = `${msg} ${this.id} ${new Date()}\n`;
        await fs.appendFile(`${this.id}.log`, data);
    }

    async init() {
        await this.init_browser({ chromium_path: 'include/chrome-linux/chrome',
                                  user_data_dir: `${this.id}-tmp` });
        await this.init_CDP();
    }


    async init_browser({ chromium_path, user_data_dir }) {
        const browser = spawn(chromium_path, [
            `--remote-debugging-port=${this.port}`,
            `--incognito`,
            `--disk-cache-dir=/dev/null`

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
        ]);
        this.log(`CDP initiated`);
    }

    async intercept_urls({ target, urls }) {
        const requests = [];

        await this.client.Network.setRequestInterception({ patterns: [{ urlPattern: '*' }] });

        this.client.Network.requestIntercepted(async ({ interceptionId, request}) => {
                
            const modHeaders = request.headers;
            modHeaders['sec-ch-ua'] = '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"';
            modHeaders['sec-ch-ua-platform'] = '"Windows"';

            if (request.url.includes(target)) {
                requests.push({...request, headers: modHeaders});
            }
            await this.log(`${request.url} intercepted\n ${JSON.stringify(modHeaders)}`);
            await this.client.Network.continueInterceptedRequest({ interceptionId, headeons: modHeaders });
        });
        
         this.client.Network.responseReceived(async ({ requestId, response }) => {
             this.log(JSON.stringify(response));
            const contentType = response.headers['content-type'] || response.headers['Content-Type'] || '';
            if (contentType.includes('application/json')) {
                try {
                    const { body, base64Encoded } = await this.client.Network.getResponseBody({ requestId });
                    const decodedBody = base64Encoded ? Buffer.from(body, 'base64').toString('utf8') : body;
                    jsonResponses.push({
                        url: response.url,
                        body: JSON.parse(decodedBody), // Parse JSON for easier use
                        headers: response.headers
                    });
                    this.log(`Intercepted JSON response from ${response.url}`);
                } catch (error) {
                    this.log(`Failed to get JSON body for ${response.url}: ${error.message}`);
                }
            }
        });


        for (const url of urls) {
            await this.client.Page.navigate({ url });
            await this.client.Page.loadEventFired();
        }

        console.log(requests);
        return requests;
    }
}

export default Scraper;
