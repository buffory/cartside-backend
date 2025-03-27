import express from 'express'
import dotenv from 'dotenv'

import Cluster from './lib/Cluster.js';

dotenv.config()

const port = process.env.PORT
const app = express()


app.listen(port, async () => {
    const cluster = new Cluster();
    await cluster.init();
    console.log(`Cartside backend listening on ${port}`)
})
