const request = require("request");
const polyline = require("polyline");
const flexPoly = require("./flex_poly");

const HERE_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const HERE_API_URL = "https://router.hereapi.com/v8/routes";

const TOLLGURU_API_KEY = process.env.TOLLGURU_API_KEY;
const TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2";
const POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service";

const source = { longitude: '-96.7970', latitude: '32.7767' }; // Dallas, TX
const destination = { longitude: '-74.0060', latitude: '40.7128' }; // New York, NY

const url = `${HERE_API_URL}?transportMode=car&origin=${source.latitude},${source.longitude}&destination=${destination.latitude},${destination.longitude}&apiKey=${HERE_API_KEY}&return=polyline`;


const flatten = (arr, x) => arr.concat(x);

// JSON path "$..points"
const getPoints = body => body.routes
  .map(route => route.sections)
  .reduce(flatten)
  .map(x => x.polyline)
  .map(x => flexPoly.decode(x))
  .map(x => x.polyline)
  .reduce(flatten)

const getPolyline = body => polyline.encode(getPoints(JSON.parse(body)));


const getRoute = (cb) => request.get(url, cb);

const handleRoute = (e, r, body) => {

  const _polyline = getPolyline(body);
  console.log(_polyline);

  request.post(
    {
      url: `${TOLLGURU_API_URL}/${POLYLINE_ENDPOINT}`,
      headers: {
        'content-type': 'application/json',
        'x-api-key': TOLLGURU_API_KEY
      },
      body: JSON.stringify({ source: "here", polyline: _polyline })
    },
    (e, r, body) => {
      console.log(e);
      console.log(body)
    }
  )
};

getRoute(handleRoute)
