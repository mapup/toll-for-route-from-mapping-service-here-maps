// Load environment variables from root .env file
// This allows sharing the same .env across javascript, python, and other folders
require('dotenv').config({ path: '../.env' });
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
   VEHICLE TYPE MAPPING
   =================================================================== */

// Maps TollGuru vehicle types to HERE Maps transport modes
const tollGuruTypeToCategory = {
  // Car / SUV / Pickup / EV / similar
  "2AxlesAuto":   "car",
  "3AxlesAuto":   "car",
  "4AxlesAuto":   "car",
  "2AxlesDualTire": "car",
  "3AxlesDualTire": "car",
  "4AxlesDualTire": "car",
  "2AxlesEV":    "car",
  "3AxlesEV":    "car",
  "4AxlesEV":    "car",

  // Rideshare/Taxi/Carpool
  "2AxlesTNC":   "car",
  "2AxlesTNCPool": "car",
  "2AxlesTaxi":  "car",
  "2AxlesTaxiPool": "car",
  "Carpool2":    "car",
  "Carpool3":    "car",

  // Truck
  "2AxlesTruck": "truck",
  "3AxlesTruck": "truck",
  "4AxlesTruck": "truck",
  "5AxlesTruck": "truck",
  "6AxlesTruck": "truck",
  "7AxlesTruck": "truck",
  "8AxlesTruck": "truck",
  "9AxlesTruck": "truck",

  // Bus
  "2AxlesBus":   "bus",
  "3AxlesBus":   "bus",

  "2AxlesRv":   "car",  // RVs are treated as cars for HERE Maps
  "3AxlesRv":   "car",
  "4AxlesRv":   "car",
};

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
  vehicle: inputData.vehicle
};

// Add locTimes if provided
if (inputData.locTimes) {
  requestParameters.locTimes = inputData.locTimes;
}

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
 * Gets the HERE Maps transport mode from TollGuru vehicle type
 * Defaults to 'car' if the vehicle type is not found in the mapping
 */
const getTransportMode = (vehicleType) => {
  if (!vehicleType) {
    console.warn("No vehicle type provided, defaulting to 'car'");
    return 'car';
  }

  const transportMode = tollGuruTypeToCategory[vehicleType];

  if (!transportMode) {
    console.warn(`Unknown vehicle type '${vehicleType}', defaulting to 'car'`);
    return 'car';
  }

  return transportMode;
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

    request.get(geocodeUrl, (error, response, body) => {
      if (error) {
        console.error("Error executing geocoding request:", error);
        return reject(new Error("Unable to geocode the address"));
      }

      try {
        const geocodedResponse = JSON.parse(body);

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
 * Converts ISO timestamp string to Unix epoch timestamp (seconds)
 */
const isoToEpoch = (isoTimestamp) => {
  return Math.floor(new Date(isoTimestamp).getTime() / 1000);
};

/**
 * Generates locTimes array from HERE Maps actions
 * @param {Array} actions - Array of actions from HERE Maps response
 * @param {number} departureEpoch - Departure time in Unix epoch seconds
 * @returns {Array} locTimes array in format [[offset, timestamp], ...]
 */
const generateLocTimes = (actions, departureEpoch) => {
  const locTimes = [];
  let cumulativeTime = departureEpoch;

  // Generate locTimes for each action
  for (let i = 0; i < actions.length; i++) {
    const action = actions[i];
    // Add current action's offset and cumulative timestamp
    locTimes.push([action.offset, cumulativeTime]);
    // Add duration to cumulative time for next action
    cumulativeTime += action.duration;
  }

  return locTimes;
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

    // Get transport mode from vehicle type
    const transportMode = getTransportMode(inputData.vehicle?.type);
    console.log("Transport mode:", transportMode);

    const url = `${HERE_API_URL}?${new URLSearchParams({
      transportMode: transportMode,
      origin: `${processedSource.latitude},${processedSource.longitude}`,
      destination: `${processedDestination.latitude},${processedDestination.longitude}`,
      apiKey: HERE_API_KEY,
      return: 'polyline,actions'
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

    // Extract departure and arrival times from the route
    const firstSection = routeData.routes[0].sections[0];
    const departureTime = firstSection.departure.time;
    const arrivalTime = firstSection.arrival.time;

    console.log("Departure time:", departureTime);
    console.log("Arrival time:", arrivalTime);

    // Convert ISO timestamps to Unix epoch
    const departureEpoch = isoToEpoch(departureTime);
    const arrivalEpoch = isoToEpoch(arrivalTime);

    console.log("Departure epoch:", departureEpoch);
    console.log("Arrival epoch:", arrivalEpoch);

    // Extract actions from the first section
    const actions = firstSection.actions;
    console.log("Number of actions:", actions.length);

    // Generate locTimes from actions
    const locTimes = generateLocTimes(actions, departureEpoch);
    console.log("Generated locTimes with", locTimes.length, "entries");

    // Add locTimes to request parameters
    const tollguruRequestParams = {
      ...requestParameters,
      locTimes: locTimes
    };

    // Construct the payload for TollGuru API
    const tollguruPayload = {
      source: "here",
      polyline: _polyline,
      ...tollguruRequestParams,
    };

    console.log("\n========================================");
    console.log("PAYLOAD SENT TO TOLLGURU API:");
    console.log("========================================");
    console.log(JSON.stringify(tollguruPayload, null, 2));
    console.log("========================================\n");

    request.post(
      {
        url: `${TOLLGURU_API_URL}/${POLYLINE_ENDPOINT}`,
        headers: {
          'content-type': 'application/json',
          'x-api-key': TOLLGURU_API_KEY
        },
        body: JSON.stringify(tollguruPayload)
      },
      (e, r, body) => {
        if (e) {
          console.error("Error calling Tollguru API:", e);
          outputData.result.error = "Error calling Tollguru API: " + e.message;
          writeOutput(outputData);
          return;
        }

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