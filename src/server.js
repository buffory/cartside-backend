import express from 'express'
import dotenv from 'dotenv'
import Scraper from './scraper.js'

dotenv.config()

const port = process.env.PORT
const app = express()


app.listen(port, async () => {
    const scraper = new Scraper('queue.json');
    scraper.start()
    console.log(`Cartside backend listening on ${port}`)
})
