import Cluster from './Cluster.js';


(async () => {
    const cluster = new Cluster()
    await cluster.init();
})();
