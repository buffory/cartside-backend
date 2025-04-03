import dotenv from 'dotenv'
import cors from 'cors';
import express from 'express';

import products_route from './routes/products.js';
import maps_route from './routes/maps.js';

dotenv.config()

const port = process.env.PORT;
const app = express();
app.use(express.json());
app.use(cors({
    origins: "http://localhost:5173",
    methods: "GET"
}));

app.use('/products', products_route);
app.use('/maps', maps_route);

app.listen(port, async () => {
    //const cluster = new Cluster();
    //await cluster.init();
    console.log(`Cartside backend listening on ${port}`);
});

