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

    async init_browser({ chromium_path, user_data_dir }) {
        const browser = spawn(chromium_path, [
            `--remote-debugging-port=${this.port}`,
            `--user-data-dir=${user_data_dir}`
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

    async goto({ url }) {
        await this.client.Page.navigate({ url });
        await this.client.Page.loadEventFired();
        this.log(`${url} loaded`);
    }

    async intercept_request({ target, interceptedRequests }) {
        
    }

    async intercept_urls({ target, urls }) {
        const requests = [];

        await this.client.Network.setRequestInterception({ patterns: [{ urlPattern: '*' }] });

        this.client.Network.requestIntercepted(({ interceptionId, request }) => {
            if (request.url.includes(target)) {
                requests.push(request);
                this.log(`${request.url} intercepted`);
            }
            this.client.Network.continueInterceptedRequest({ interceptionId });
        });

        this.intercepting = true;

        for (const url of urls) {
            await this.goto({ url });
        }

        this.client.Network.setRequestInterception({ patterns: [{ urlPattern: '*' }] });
        this.intercepting = false;
        this.log(`${requests.length} intercepted for ${target}`);
    }
}

export default Scraper;
