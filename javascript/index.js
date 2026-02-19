// Load environment variables from root .env file
// This allows sharing the same .env across javascript, python, and other folders
require('dotenv').config({ path: '../.env' });
const axios = require("axios");
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
  "2AxlesAuto": "car",
  "3AxlesAuto": "car",
  "4AxlesAuto": "car",
  "2AxlesDualTire": "car",
  "3AxlesDualTire": "car",
  "4AxlesDualTire": "car",
  "2AxlesEV": "car",
  "3AxlesEV": "car",
  "4AxlesEV": "car",

  // Rideshare/Taxi/Carpool
  "2AxlesTNC": "car",
  "2AxlesTNCPool": "car",
  "2AxlesTaxi": "car",
  "2AxlesTaxiPool": "car",
  "Carpool2": "car",
  "Carpool3": "car",

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
  "2AxlesBus": "bus",
  "3AxlesBus": "bus",

  "2AxlesRv": "car",  // RVs are treated as cars for HERE Maps
  "3AxlesRv": "car",
  "4AxlesRv": "car",
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
  vehicle: {
    type: inputData.vehicle?.type || "2AxlesAuto"
  }
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

  try {
    const response = await axios.get(geocodingAPI, {
      params: {
        q: address,
        apiKey: HERE_API_KEY
      }
    });

    const geocodedResponse = response.data;

    if (!geocodedResponse.items || geocodedResponse.items.length === 0) {
      throw new Error("Invalid address - no results found");
    }

    return geocodedResponse;
  } catch (error) {
    console.error("Error executing geocoding request:", error.message);
    throw new Error("Unable to geocode the address");
  }
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

const getPolyline = body => polyline.encode(getPoints(body));

// Function to write output to file
const writeOutput = (data) => {
  try {
    fs.writeFileSync('./output.json', JSON.stringify(data, null, 2));
    console.log("\n✓ Results written to output.json");
  } catch (error) {
    console.error("Error writing to output.json:", error.message);
  }
};

const getRoute = async () => {
  const outputData = {
    timestamp: new Date().toISOString(),
    input: inputData,
    result: {}
  };

  try {
    // Process locations first
    const [processedSource, processedDestination] = await Promise.all([
      processLocation(source),
      processLocation(destination)
    ]);

    console.log("Source:", processedSource);
    console.log("Destination:", processedDestination);

    // Get transport mode from vehicle type
    const transportMode = getTransportMode(inputData.vehicle?.type);
    console.log("Transport mode:", transportMode);

    console.log("Fetching route from HERE Maps...");
    const hereResponse = await axios.get(HERE_API_URL, {
      params: {
        transportMode: transportMode,
        origin: `${processedSource.latitude},${processedSource.longitude}`,
        destination: `${processedDestination.latitude},${processedDestination.longitude}`,
        apiKey: HERE_API_KEY,
        return: 'polyline,actions'
      }
    });

    const routeData = hereResponse.data;

    // Check if routes exist in the response
    if (!routeData.routes || routeData.routes.length === 0) {
      console.error("No routes found in response");
      outputData.result.error = "No routes found in response";
      writeOutput(outputData);
      return;
    }

    const _polyline = getPolyline(routeData);

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

    // Construct the payload for TollGuru API
    // FIX: Explictly construct payload to avoid data leakage from inputData
    const tollguruPayload = {
      source: "here",
      polyline: _polyline,
      vehicle: {
        type: requestParameters.vehicle.type
      },
      locTimes: locTimes
    };

    console.log("\n========================================");
    console.log("PAYLOAD SENT TO TOLLGURU API:");
    console.log("========================================");
    // Redact large fields for display
    const displayPayload = { ...tollguruPayload };
    if (displayPayload.polyline && displayPayload.polyline.length > 100) {
      displayPayload.polyline = displayPayload.polyline.substring(0, 100) + "...";
    }
    if (displayPayload.locTimes && displayPayload.locTimes.length > 5) {
      displayPayload.locTimes = `Array of ${displayPayload.locTimes.length} items`;
    }
    console.log(JSON.stringify(displayPayload, null, 2));
    console.log("========================================\n");

    try {
      const tollguruResponse = await axios.post(
        `${TOLLGURU_API_URL}/${POLYLINE_ENDPOINT}`,
        tollguruPayload,
        {
          headers: {
            'content-type': 'application/json',
            'x-api-key': TOLLGURU_API_KEY
          }
        }
      );

      outputData.result.tollguruResponse = tollguruResponse.data;
      outputData.result.success = true;
      writeOutput(outputData);

    } catch (tollguruError) {
      console.error("Error calling Tollguru API:", tollguruError.message);
      if (tollguruError.response) {
        console.error("Response data:", tollguruError.response.data);
        outputData.result.error = "Error calling Tollguru API: " + JSON.stringify(tollguruError.response.data);
      } else {
        outputData.result.error = "Error calling Tollguru API: " + tollguruError.message;
      }
      writeOutput(outputData);
    }

  } catch (error) {
    console.error("Error processing route:", error.message);
    outputData.result.error = "Error processing route: " + error.message;
    writeOutput(outputData);
  }
};

getRoute();