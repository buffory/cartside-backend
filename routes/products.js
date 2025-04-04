import pg from 'pg';
import express from 'express';
import dotenv from 'dotenv';

dotenv.config()

const router = express.Router()


router.get('/', async (req, res) => {
    const product = req.query.product
    const { Client } = pg;
    const client = new Client({
        connectionString: process.env.DATABASE_URL,
        ssl: {
            rejectUnauthorized: false
        }
    });

    await client.connect()

    try {
        const result = await client.query(`SELECT * FROM products WHERE name ILIKE '%${product}%' ORDER BY price ASC LIMIT 10`);
        await client.end();
        return await res.status(200).json(result.rows);
    } catch (err) {
        console.error(err);
        await client.end();
        return await res.status(500).json(error);
    }
});

export default router;
