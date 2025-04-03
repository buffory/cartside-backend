import pg from 'pg';
import express from 'express';

const router = express.Router()


router.get('/', async (req, res) => {
    const product = req.query.product
    const { Client } = pg;
    const client = new Client({
        user: process.env.DB_USER,
        password: process.env.DB_PASSWORD,
        host: process.env.DB_HOST,
        database: process.env.DB_DB,
        port: process.env.DB_PORT
    });

    await client.connect()

    try {
        const result = await client.query(`SELECT * FROM products WHERE name ILIKE '%${product}%' ORDER BY price ASC LIMIT 10`);
        await client.end();
        return await res.status(200).json(result);
    } catch (err) {
        console.error(err);
        await client.end();
        return await res.status(500).json(error);
    }
});

export default router
