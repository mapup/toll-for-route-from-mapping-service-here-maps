require('dotenv').config();
const request = require("request");
const polyline = require("polyline");
const flexPoly = require("./flex_poly");
const fs = require("fs");

const HERE_API_KEY = process.env.HERE_API_KEY;
const HERE_API_URL = "https://router.hereapi.com/v8/routes";

const TOLLGURU_API_KEY = process.env.TOLLGURU_API_KEY;
const TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2";
const POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service";

/* ===================================================================
   READ INPUT FROM FILE
   =================================================================== */

let inputData;
try {
  const inputFile = fs.readFileSync('./input.json', 'utf8');
  inputData = JSON.parse(inputFile);
  console.log("✓ Input file loaded successfully");
  console.log("Description:", inputData.description);
} catch (error) {
  console.error("Error reading input.json:", error.message);
  console.error("Please make sure input.json exists and is valid JSON");
  process.exit(1);
}

// Extract configuration from input file
const source = inputData.source;
const destination = inputData.destination;
const requestParameters = {
  vehicle: inputData.vehicle,
  departure_time: inputData.departure_time
};

/* ===================================================================
   HELPER FUNCTIONS
   =================================================================== */

/**
 * Validates that a string contains alphanumeric characters
 */
const containsAlphanumeric = (str) => {
  return /[a-zA-Z0-9]/.test(str);
};

/**
 * Geocodes an address using HERE Maps Geocoding API
 */
const geocodeAddress = async (address) => {
  const geocodingAPI = "https://geocode.search.hereapi.com/v1/geocode";

  return new Promise((resolve, reject) => {
    const params = new URLSearchParams({
      q: address,
      apiKey: HERE_API_KEY
    });

    const geocodeUrl = `${geocodingAPI}?${params.toString()}`;
    console.log("Geocode query URL:", geocodeUrl);

    request.get(geocodeUrl, (error, response, body) => {
      if (error) {
        console.error("Error executing geocoding request:", error);
        return reject(new Error("Unable to geocode the address"));
      }

      try {
        const geocodedResponse = JSON.parse(body);
        console.log("Geocoded response:", geocodedResponse);

        if (!geocodedResponse.items || geocodedResponse.items.length === 0) {
          return reject(new Error("Invalid address - no results found"));
        }

        resolve(geocodedResponse);
      } catch (err) {
        console.error("Error parsing geocoding response:", err);
        reject(new Error("Unable to parse geocoding response"));
      }
    });
  });
};

/**
 * Processes location input - handles both coordinates and addresses
 */
const processLocation = async (userInput) => {
  // Check if lat/lng are provided
  if (userInput.latitude && userInput.longitude) {
    return {
      latitude: userInput.latitude,
      longitude: userInput.longitude,
      address: userInput.address || ""
    };
  }

  // If no coordinates, try to geocode the address
  if (userInput.address) {
    if (!containsAlphanumeric(userInput.address)) {
      throw new Error("Invalid address - must contain alphanumeric characters");
    }

    const geocodedResponse = await geocodeAddress(userInput.address);
    const location = geocodedResponse.items[0];

    return {
      latitude: location.position.lat,
      longitude: location.position.lng,
      address: location.address.label
    };
  }

  throw new Error("Must provide either latitude/longitude or address");
};

/* ===================================================================
   ROUTE PROCESSING FUNCTIONS
   =================================================================== */

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

const getRoute = (cb) => {
  // Process locations first, then build URL and make request
  Promise.all([
    processLocation(source),
    processLocation(destination)
  ])
  .then(([processedSource, processedDestination]) => {
    console.log("Source:", processedSource);
    console.log("Destination:", processedDestination);

    const url = `${HERE_API_URL}?${new URLSearchParams({
      transportMode: 'car',
      origin: `${processedSource.latitude},${processedSource.longitude}`,
      destination: `${processedDestination.latitude},${processedDestination.longitude}`,
      apiKey: HERE_API_KEY,
      return: 'polyline',
    }).toString()}`;

    console.log("Fetching route from HERE Maps...");
    request.get(url, cb);
  })
  .catch(error => {
    console.error("Error processing locations:", error.message);
  });
};

const handleRoute = (e, r, body) => {
  const outputData = {
    timestamp: new Date().toISOString(),
    input: inputData,
    result: {}
  };

  if (e) {
    console.error("Error fetching route:", e);
    outputData.result.error = "Error fetching route: " + e.message;
    writeOutput(outputData);
    return;
  }

  try {
    const routeData = JSON.parse(body);

    // Check if routes exist in the response
    if (!routeData.routes || routeData.routes.length === 0) {
      console.error("No routes found in response:", body);
      outputData.result.error = "No routes found in response";
      writeOutput(outputData);
      return;
    }

    const _polyline = getPolyline(body);
    console.log("Polyline:", _polyline);

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
        if (e) {
          console.error("Error calling Tollguru API:", e);
          outputData.result.error = "Error calling Tollguru API: " + e.message;
          writeOutput(outputData);
          return;
        }
        console.log("Tollguru Response:", body);

        try {
          outputData.result.tollguruResponse = JSON.parse(body);
          outputData.result.success = true;
          writeOutput(outputData);
        } catch (parseError) {
          outputData.result.error = "Error parsing Tollguru response";
          outputData.result.rawResponse = body;
          writeOutput(outputData);
        }
      }
    )
  } catch (parseError) {
    console.error("Error parsing route response:", parseError);
    console.error("Response body:", body);
    outputData.result.error = "Error parsing route response: " + parseError.message;
    writeOutput(outputData);
  }
};

// Function to write output to file
const writeOutput = (data) => {
  try {
    fs.writeFileSync('./output.json', JSON.stringify(data, null, 2));
    console.log("\n✓ Results written to output.json");
  } catch (error) {
    console.error("Error writing to output.json:", error.message);
  }
};

getRoute(handleRoute);