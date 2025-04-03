import { Client } from '@googlemaps/google-maps-services-js';
import express from 'express';

const router = express.Router();
const client = new Client({})

router.get('/', async (req, res) => {
    console.log(req.query);
    const { lat, lng, retailers } = req.query;
    const retailers_arr = typeof retailers === 'string' ? [retailers] : retailers;
    const response = await fetch('https://places.googleapis.com/v1/places:searchNearby', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': process.env.GOOGLE_API,
            'X-Goog-FieldMask': 'places.displayName',
        },
        body: JSON.stringify({
            'includedTypes': retailers,
            'maxResultCount': 10,
            'locationRestriction': {
                'circle': {
                    'center': {
                        'latitude': lat,
                        'longitude': lng
                    },
                    'radius': 500.0
                }
            }
        })
    });
    const data = await response.json();
    console.log(data);

});


export default router;

