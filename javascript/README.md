# [HERE](https://developer.here.com/)

### Get API key to access HERE Maps APIs (if you have an API key skip this)
#### Step 1: Login/Singup
* Create an account to access [HERE Developer Portal](https://developer.here.com/)
* go to signup/login link https://developer.here.com/login
* you will need to agree to HERE's Terms of Service https://legal.here.com/en-gb/terms

#### Step 2: Getting your Key
* Login to your HERE Maps Developer Portal
* Go to https://developer.here.com/projects
* Select your project
* After selecting your project you need to select the service, select
  `REST APIs`


With this in place, make a GET request: https://router.hereapi.com/v8/routes?transportMode=car&origin=${source.latitude},${source.longitude}&destination=${destination.latitude},${destination.longitude}&apiKey=${key}&return=polyline
### Note:
* HERE accepts source and destination, as `:` seperated `${longitude,latitude}`.
* HERE maps doesn't return us route as a `endoced polyline`, but as
  `flexible polyline`, we will covert it from `flexible polyline` to
  `encoded polyline`.
* Code to play with `flexible polyline` can be found at https://github.com/heremaps/flexible-polyline/tree/master/javascript
* Since at the time of writing this article this repo was not on npm so,
  the index file is included as `flex_poly.js`

```javascript
// JSON path "$..polyline"
const getPoints = body => body.routes
  .map(route => route.sections)
  .reduce(flatten)
  .map(x => x.polyline)
  .map(x => flexPoly.decode(x))
  .map(x => x.polyline)
  .reduce(flatten)
```

```javascript
const request = require("request");
const polyline = require("polyline");
const flexPoly = require("./flex_poly");

// REST API key from Here maps
const key = process.env.HEREMAP_KEY
const tollguruKey = process.env.TOLLGURU_KEY;

// Dallas, TX
const source = {
    longitude: '-96.7970',
    latitude: '32.7767',
}

// New York, NY
const destination = {
    longitude: '-74.0060',
    latitude: '40.7128'
};

const url = `https://router.hereapi.com/v8/routes?transportMode=car&origin=${source.latitude},${source.longitude}&destination=${destination.latitude},${destination.longitude}&apiKey=${key}&return=polyline`;


const head = arr => arr[0];
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

const handleRoute = (e, r, body) => console.log(getPolyline(body));

getRoute(handleRoute);
```

Note:

We extracted the polyline for a route from HERE Maps API

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to receive a free key from TollGuru https://tollguru.com/developers/get-api-key
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.

the last line can be changed to following

```javascript

const tollguruUrl = 'https://dev.tollguru.com/v1/calc/route';

const handleRoute = (e, r, body) =>  {

  const _polyline = getPolyline(body);
  console.log(_polyline);

  request.post(
    {
      url: tollguruUrl,
      headers: {
        'content-type': 'application/json',
        'x-api-key': tollguruKey
      },
      body: JSON.stringify({
        source: "here",
        polyline: _polyline,
        vehicleType: "2AxlesAuto",
        departure_time: "2021-01-05T09:46:08Z"
      })
    },
    (e, r, body) => {
      console.log(e);
      console.log(body)
    }
  )
};
getRoute(handleRoute);
```

The working code can be found in index.js file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
