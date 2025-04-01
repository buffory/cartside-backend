import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { spawn } from 'child_process';

import Cluster from './Cluster.js';

dotenv.config();
const port = process.env.SC_PORT;
const app = express();
app.use(cors());
app.use(express.json());

const cluster = new Cluster();
cluster.init();

app.listen(port, async () => {
    console.log(`Scraper api listening on ${port}`);
});

app.get('/kroger', async (req, res) => {
    const product = req.query.product;
    const htmlPath = await cluster.Kroger.scrapeHTML({ url: `https://www.kroger.com/search?query=${product}&searchType=default_search` });
    console.log(htmlPath);
    if (htmlPath != null) {
        const result = await saveKroger('database/kroger_save.py', htmlPath);
        console.log(result);
    }
    return await res.status(500);
});

async function saveKroger(scriptPath, htmlPath) {
    return new Promise((resolve, reject) => {
        const pythonProcess = spawn('database/bin/python', [scriptPath, htmlPath]);
        let result = '';
        let error = '';

        pythonProcess.stdout.on('data', (data) => {
            result += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            error += data.toString();
        });

        pythonProcess.on('close', (code) => {
            if (code != 0) {
                reject(new Error(error));
            }
            resolve(result);
          });

       });
}
