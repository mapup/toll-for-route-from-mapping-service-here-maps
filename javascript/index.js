const request = require("request");
const polyline = require("polyline");
const flexPoly = require("./flex_poly");

const HERE_API_KEY = process.env.HERE_API_KEY;
const HERE_API_URL = "https://router.hereapi.com/v8/routes";

const TOLLGURU_API_KEY = process.env.TOLLGURU_API_KEY;
const TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2";
const POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service";

const source = { latitude: -75.16218, longitude: 39.95222, }; // Philadelphia, PA
const destination = { latitude: -74.0060, longitude: 40.7128 }; // New York, NY

// Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
const requestParameters = {
  "vehicle": {
    "type": "2AxlesAuto",
  },
  // Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
  "departure_time": "2021-01-05T09:46:08Z",
}

const url = `${HERE_API_URL}?${new URLSearchParams({
  transportMode: 'car',
  origin: `${source.longitude},${source.latitude}`,
  destination: `${destination.longitude},${destination.latitude}`,
  apiKey: HERE_API_KEY,
  return: 'polyline',
}).toString()}`;

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
  console.log(body)

  const _polyline = getPolyline(body);
  console.log(_polyline);

  request.post(
    {
      url: `${TOLLGURU_API_URL}/${POLYLINE_ENDPOINT}`,
      headers: {
        'content-type': 'application/json',
        'x-api-key': TOLLGURU_API_KEY
      },
      body: JSON.stringify({
        source: "here",
        polyline: _polyline,
        ...requestParameters,
      })
    },
    (e, r, body) => {
      console.log(e);
      console.log(body)
    }
  )
};

getRoute(handleRoute)
