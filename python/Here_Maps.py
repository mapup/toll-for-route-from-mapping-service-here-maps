# Importing modules
import json
import requests
import flexpolyline as fp
import polyline as poly
import os

HERE_API_KEY = os.environ.get("HERE_API_KEY")  # API key for Here Maps
HERE_API_URL = "https://router.hereapi.com/v8/routes"
HERE_GEOCODE_API_URL = "https://geocode.search.hereapi.com/v1/geocode"

TOLLGURU_API_KEY = os.environ.get("TOLLGURU_API_KEY")  # API key for Tollguru
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"
POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service"

# Vehicle type mapping: Maps TollGuru vehicle types to HERE Maps transport modes
TOLLGURU_TYPE_TO_CATEGORY = {
    # Car / SUV / Pickup / EV / similar
    "2AxlesAuto": "car",
    "3AxlesAuto": "car",
    "4AxlesAuto": "car",
    "2AxlesDualTire": "car",
    "3AxlesDualTire": "car",
    "4AxlesDualTire": "car",
    "2AxlesEV": "car",
    "3AxlesEV": "car",
    "4AxlesEV": "car",
    # Rideshare/Taxi/Carpool
    "2AxlesTNC": "car",
    "2AxlesTNCPool": "car",
    "2AxlesTaxi": "car",
    "2AxlesTaxiPool": "car",
    "Carpool2": "car",
    "Carpool3": "car",
    # Truck
    "2AxlesTruck": "truck",
    "3AxlesTruck": "truck",
    "4AxlesTruck": "truck",
    "5AxlesTruck": "truck",
    "6AxlesTruck": "truck",
    "7AxlesTruck": "truck",
    "8AxlesTruck": "truck",
    "9AxlesTruck": "truck",
    # Bus
    "2AxlesBus": "bus",
    "3AxlesBus": "bus",
    # RV
    "2AxlesRv": "car",
    "3AxlesRv": "car",
    "4AxlesRv": "car",
}

# From and To locations
source = "Philadelphia, PA"
destination = "New York, NY"

# Vehicle type configuration
# For vehicle types refer https://tollguru.com/toll-api-docs#vehicle-types-supported-by-tollguru
vehicle_type = "2AxlesAuto"  # You can change this dynamically

# Explore https://tollguru.com/toll-api-docs to get best of all the parameter that tollguru has to offer
# Refer https://github.com/mapup/tollguru-api-parameter-examples/tree/main/request-bodies/02-Complete-Polyline-To-Toll for more examples
request_parameters = {
    "vehicle": {
        "type": vehicle_type,
    },
    # Note: departure_time removed - we now use locTimes generated from HERE Maps response
}

def get_transport_mode(vehicle_type):
    """Gets the HERE Maps transport mode from TollGuru vehicle type"""
    if not vehicle_type:
        print("Warning: No vehicle type provided, defaulting to 'car'")
        return "car"

    transport_mode = TOLLGURU_TYPE_TO_CATEGORY.get(vehicle_type)

    if not transport_mode:
        print(f"Warning: Unknown vehicle type '{vehicle_type}', defaulting to 'car'")
        return "car"

    return transport_mode

def iso_to_epoch(iso_timestamp):
    """Converts ISO timestamp string to Unix epoch timestamp (seconds)"""
    from datetime import datetime
    return int(datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00')).timestamp())

def generate_loc_times(actions, departure_epoch):
    """
    Generates locTimes array from HERE Maps actions

    Args:
        actions: Array of actions from HERE Maps response
        departure_epoch: Departure time in Unix epoch seconds

    Returns:
        locTimes array in format [[offset, timestamp], ...]
    """
    loc_times = []
    cumulative_time = departure_epoch

    # Generate locTimes for each action
    for action in actions:
        # Add current action's offset and cumulative timestamp
        loc_times.append([action['offset'], cumulative_time])
        # Add duration to cumulative time for next action
        cumulative_time += action['duration']

    return loc_times

def get_geocodes_from_here_maps(address):
    """Fetching geocodes form Here maps"""
    params = {"q": address, "apiKey": HERE_API_KEY}
    response_from_here = requests.get(HERE_GEOCODE_API_URL, params=params).json()
    latitude, longitude = response_from_here["items"][0]["position"].values()
    return (latitude, longitude)

def get_polyline_from_here_maps(
    source_latitude, source_longitude, destination_latitude, destination_longitude, vehicle_type="2AxlesAuto"
):
    """Fetching Polyline and Actions from Here Maps"""
    # Get transport mode from vehicle type
    transport_mode = get_transport_mode(vehicle_type)

    # Query Here Maps with Key and Source-Destination coordinates
    # Note: We request both polyline and actions
    url = "{a}?transportMode={b}&origin={c},{d}&destination={e},{f}&apiKey={g}&return=polyline,actions".format(
        a=HERE_API_URL,
        b=transport_mode,
        c=source_latitude,
        d=source_longitude,
        e=destination_latitude,
        f=destination_longitude,
        g=HERE_API_KEY,
    )
    # converting the response to json
    response = requests.get(url).json()
    # Extracting polyline
    flex_polyline_here = response["routes"][0]["sections"][0][
        "polyline"
    ]  # heremaps provide a flexpolyline
    polyline_from_heremaps = poly.encode(
        fp.decode(flex_polyline_here)
    )  # we converted that to encoded(google) polyline

    # Return both polyline and full response for accessing actions and departure time
    return polyline_from_heremaps, response

# Calling Tollguru API
def get_rates_from_tollguru(polyline, loc_times=None):
    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLLGURU_API_KEY}
    params = {
        **request_parameters,
        "source": "here",
        "polyline": polyline,  #  this is polyline that we fetched from the mapping service
    }

    # Add locTimes if provided
    if loc_times is not None:
        params["locTimes"] = loc_times

    # Requesting Tollguru with parameters
    response_tollguru = requests.post(
        f"{TOLLGURU_API_URL}/{POLYLINE_ENDPOINT}",
        json=params,
        headers=headers,
    ).json()

    # checking for errors or printing rates
    if str(response_tollguru).find("message") == -1:
        return response_tollguru["route"]["costs"]
    else:
        raise Exception(response_tollguru["message"])


"""Program Starts"""
# Step 1 : Provide source and destination and get geocodes from heremaps
source_latitude, source_longitude = get_geocodes_from_here_maps(source)
destination_latitude, destination_longitude = get_geocodes_from_here_maps(destination)

# Step 2 : Get polyline and route data for given source-destination route
polyline_from_heremaps, route_response = get_polyline_from_here_maps(
    source_latitude, source_longitude, destination_latitude, destination_longitude, vehicle_type
)

# Step 3 : Extract actions and departure time from HERE Maps response
first_section = route_response["routes"][0]["sections"][0]
actions = first_section["actions"]
departure_time = first_section["departure"]["time"]

# Step 4 : Convert departure time to Unix epoch and generate locTimes
departure_epoch = iso_to_epoch(departure_time)
loc_times = generate_loc_times(actions, departure_epoch)

print(f"Generated {len(loc_times)} locTimes entries from {len(actions)} actions")

# Step 5 : Get rates from tollguru with locTimes
rates_from_tollguru = get_rates_from_tollguru(polyline_from_heremaps, loc_times)

# Print the rates of all the available modes of payment
if rates_from_tollguru == {}:
    print("The route doesn't have tolls")
else:
    print(f"The rates are \n {rates_from_tollguru}")

"""Program Ends"""
