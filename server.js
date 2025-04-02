import dotenv from 'dotenv'
import cors from 'cors';

import Cluster from './scrapers/Cluster.js';

dotenv.config()

const port = process.env.PORT;
const app = express();
app.use(express.json());
app.use(cors({
    origins: "*"
}));

app.listen(port, async () => {
    //const cluster = new Cluster();
    //await cluster.init();
    console.log(`Cartside backend listening on ${port}`)
})

app.get('/products/search', async (req, res) => {
    const name  = req.query.name;
    const db_res = await fetch(`http://localhost:8000/products/similar?name=${name}`);
    const data = await db_res.json()
    console.log(data);
    return res.status(200).json(data);
});

