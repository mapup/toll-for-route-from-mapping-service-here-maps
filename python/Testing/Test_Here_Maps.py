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
request_parameters = {
    "vehicle": {
        "type": "2AxlesAuto",
    },
    # Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
    "departure_time": "2021-01-05T09:46:08Z",
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
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return int(dt.timestamp())

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
    """Fetching Polyline and route data from Here Maps"""
    # Get transport mode from vehicle type
    transport_mode = get_transport_mode(vehicle_type)

    # Query Here Maps with Key and Source-Destination coordinates
    url = "{a}?transportMode={b}&origin={c},{d}&destination={e},{f}&apiKey={g}&return=polyline".format(
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

    # Return both the polyline and the full response for time extraction
    return polyline_from_heremaps, response, len(decoded_polyline)

def create_loc_times(here_response, polyline_length):
    """Extract departure and arrival times and create locTimes array"""
    try:
        first_section = here_response["routes"][0]["sections"][0]
        departure_time = first_section["departure"]["time"]
        arrival_time = first_section["arrival"]["time"]

        print(f"Departure time: {departure_time}")
        print(f"Arrival time: {arrival_time}")

        # Convert to epoch timestamps
        departure_epoch = iso_to_epoch(departure_time)
        arrival_epoch = iso_to_epoch(arrival_time)

        print(f"Departure epoch: {departure_epoch}")
        print(f"Arrival epoch: {arrival_epoch}")

        # Last index is polyline_length - 1
        last_index = polyline_length - 1

        print(f"Polyline points count: {polyline_length}")
        print(f"Last index: {last_index}")

        # Create locTimes array: [[start_index, start_time], [end_index, end_time]]
        loc_times = [[0, departure_epoch], [last_index, arrival_epoch]]
        print(f"LocTimes: {loc_times}")

        return loc_times
    except Exception as e:
        print(f"Error creating locTimes: {e}")
        return None

"""Calling Tollguru API"""
def get_rates_from_tollguru(polyline, loc_times=None):
    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLLGURU_API_KEY}
    params = {
        **request_parameters,
        "source": "here",
        "polyline": polyline,  #  this is polyline that we fetched from the mapping service
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
            try:
                # Get vehicle type from CSV (index 4), default to 2AxlesAuto if not provided
                vehicle_type = i[4] if len(i) > 4 and i[4] else "2AxlesAuto"

                source_latitude, source_longitude = get_geocodes_from_here_maps(i[1])
                (
                    destination_latitude,
                    destination_longitude,
                ) = get_geocodes_from_here_maps(i[2])

                # Get polyline, HERE response, and polyline length
                polyline, here_response, polyline_length = get_polyline_from_here_maps(
                    source_latitude,
                    source_longitude,
                    destination_latitude,
                    destination_longitude,
                    vehicle_type,
                )

                # Create locTimes from HERE response
                loc_times = create_loc_times(here_response, polyline_length)

                i.append(polyline)
            except Exception as e:
                print(f"Routing Error: {e}")
                i.append("Routing Error")
                loc_times = None

            start = time.time()
            try:
                # Pass locTimes to Tollguru API
                rates = get_rates_from_tollguru(polyline, loc_times)
            except:
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
            i.append(time_taken)
        # print(f"{len(i)}   {i}\n")
        temp_list.append(i)

with open("testCases_result.csv", "w") as f:
    writer(f).writerows(temp_list)

"""Testing Ends"""
