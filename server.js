import express from 'express'
import dotenv from 'dotenv'
import ScraperController from './scraperController.js'

dotenv.config()

const port = process.env.PORT
const app = express()


app.listen(port, async () => {
    const scraperController = new ScraperController()
    scraperController.start()
    console.log(`Cartside backend listening on ${port}`)
})