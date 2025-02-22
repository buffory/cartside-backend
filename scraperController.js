import os from 'node:os'
import fs from 'fs'
import { spawn } from 'child_process'

class ScraperController {
    constructor() {
        this.cluster = null
        this.queueBuffer = {}
        this.scrapers = []
    }

    start() {
        // grab scraping queue
        console.log('Reading queue')
        const queue = JSON.parse(fs.readFileSync('queue.json', 'utf8'))
        this.queueBuffer = queue
        const watchlist = queue.watchlist
        console.log(watchlist[0])

        // initialize scrapers
        const config = JSON.parse(fs.readFileSync('config.json', 'utf8'))
        const scraperConfig = config.scraper
        scraperConfig.type.forEach(type => {
            switch (type) {
                case 'kroger': 
                    const process = spawn('node', ['scripts/kroger.js'])
                    process.stderr.on('data', (data) => {
                        console.log(data.toString())
                    })
                    break
            }
        })
    }
}

export default ScraperController