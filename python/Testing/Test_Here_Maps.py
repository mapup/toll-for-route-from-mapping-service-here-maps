# Importing modules
import json
import requests
import flexpolyline as fp
import polyline as poly
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

HERE_API_KEY = os.environ.get("HERE_API_KEY")  # API key for Here Maps
HERE_API_URL = "https://router.hereapi.com/v8/routes"

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

# Explore https://tollguru.com/toll-api-docs to get best of all the parameter that tollguru has to offer
# Note: Vehicle type is read dynamically from testCases.csv for each test case
# Note: departure_time removed - we now use locTimes generated from HERE Maps response
request_parameters = {}

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
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return int(dt.timestamp())

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
    """Fetching geocodes form here maps"""
    url = "https://geocode.search.hereapi.com/v1/geocode"
    para = {"q": address, "apiKey": HERE_API_KEY}
    response_from_here = requests.get(url, params=para).json()

    # Debug: Print the response to see what we're getting
    if "items" not in response_from_here:
        print(f"Geocoding API Error for '{address}':")
        print(f"Response: {response_from_here}")
        raise Exception(f"Geocoding failed for address: {address}")

    if len(response_from_here["items"]) == 0:
        raise Exception(f"No geocoding results found for address: {address}")

    latitude, longitude = response_from_here["items"][0]["position"].values()
    return (latitude, longitude)

def get_polyline_from_here_maps(
    source_latitude, source_longitude, destination_latitude, destination_longitude, vehicle_type="2AxlesAuto"
):
    """Fetching Polyline, Actions, and route data from Here Maps"""
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
    decoded_polyline = fp.decode(flex_polyline_here)
    polyline_from_heremaps = poly.encode(decoded_polyline)  # we converted that to encoded(google) polyline

    # Return polyline and full response for actions and time extraction
    return polyline_from_heremaps, response

"""Calling Tollguru API"""
def get_rates_from_tollguru(polyline, loc_times=None, vehicle_type="2AxlesAuto"):
    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLLGURU_API_KEY}
    params = {
        **request_parameters,
        "source": "here",
        "polyline": polyline,  #  this is polyline that we fetched from the mapping service
        "vehicle": {
            "type": vehicle_type,
        },
    }

    # Add locTimes if provided
    if loc_times:
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

"""Testing"""
# Importing Functions
from csv import reader, writer
import time

print("=" * 60)
print("Starting toll calculation tests...")
print("=" * 60)

temp_list = []
with open("testCases.csv", "r") as f:
    csv_reader = reader(f)
    for count, i in enumerate(csv_reader):
        # if count>2:
        # break
        if count == 0:
            i.extend(
                (
                    "Input_polyline",
                    "Tollguru_Tag_Cost",
                    "Tollguru_Cash_Cost",
                    "Tollguru_QueryTime_In_Sec",
                )
            )
        else:
            print(f"\n[Test {count}] Processing route: {i[1]} → {i[2]}")

            try:
                # Get vehicle type from CSV (index 4), default to 2AxlesAuto if not provided
                vehicle_type = i[4] if len(i) > 4 and i[4] else "2AxlesAuto"
                print(f"  Vehicle type: {vehicle_type}")

                print(f"  Geocoding source...")
                source_latitude, source_longitude = get_geocodes_from_here_maps(i[1])
                print(f"  Geocoding destination...")
                (
                    destination_latitude,
                    destination_longitude,
                ) = get_geocodes_from_here_maps(i[2])

                print(f"  Fetching route from HERE Maps...")
                # Get polyline and HERE response
                polyline, here_response = get_polyline_from_here_maps(
                    source_latitude,
                    source_longitude,
                    destination_latitude,
                    destination_longitude,
                    vehicle_type,
                )

                # Extract actions and departure time from HERE Maps response
                first_section = here_response["routes"][0]["sections"][0]
                actions = first_section["actions"]
                departure_time = first_section["departure"]["time"]

                # Convert departure time to Unix epoch and generate locTimes
                departure_epoch = iso_to_epoch(departure_time)
                loc_times = generate_loc_times(actions, departure_epoch)
                print(f"  Generated {len(loc_times)} location timestamps")

                i.append(polyline)
            except Exception as e:
                print(f"  ❌ Routing Error: {e}")
                i.append("Routing Error")
                loc_times = None

            print(f"  Calling TollGuru API...")
            start = time.time()
            try:
                # Pass locTimes and vehicle_type to Tollguru API
                rates = get_rates_from_tollguru(polyline, loc_times, vehicle_type)
            except Exception as e:
                print(f"  ❌ TollGuru API Error: {e}")
                i.append(False)
                rates = {}
            time_taken = time.time() - start
            if rates == {}:
                i.append((None, None))
            else:
                try:
                    tag = rates["tag"]
                except:
                    tag = None
                try:
                    cash = rates["cash"]
                except:
                    cash = None
                i.extend((tag, cash))
                print(f"  ✓ Tag cost: ${tag if tag else 'N/A'}, Cash cost: ${cash if cash else 'N/A'}")
            i.append(time_taken)
            print(f"  Query completed in {time_taken:.2f}s")
        # print(f"{len(i)}   {i}\n")
        temp_list.append(i)

with open("testCases_result.csv", "w") as f:
    writer(f).writerows(temp_list)

print("\n" + "=" * 60)
print(f"Testing complete! Processed {len(temp_list) - 1} test cases.")
print(f"Results saved to: testCases_result.csv")
print("=" * 60)

"""Testing Ends"""
