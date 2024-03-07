# Importing modules
import json
import requests
import flexpolyline as fp
import polyline as poly
import os

HERE_API_KEY = os.environ.get("HERE_API_KEY")  # API key for Here Maps
HERE_API_URL = "https://router.hereapi.com/v8/routes"
HERE_GEOCODE_API_URL = "https://geocoder.ls.hereapi.com/6.2/geocode.json"

TOLLGURU_API_KEY = os.environ.get("TOLLGURU_API_KEY")  # API key for Tollguru
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"
POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service"

source = "Philadelphia, PA"
destination = "New York, NY"

# Explore https://tollguru.com/toll-api-docs to get best of all the parameter that tollguru has to offer
request_parameters = {
    "vehicle": {
        "type": "2AxlesAuto",
    },
    # Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
    "departure_time": "2021-01-05T09:46:08Z",
}


def get_geocodes_from_here_maps(address):
    """Fetching geocodes form Here maps"""
    params = {"searchtext": address, "apiKey": HERE_API_KEY}
    response_from_here = requests.get(HERE_GEOCODE_API_URL, params=params).json()
    latitude, longitude = response_from_here["Response"]["View"][0]["Result"][0][
        "Location"
    ]["DisplayPosition"].values()
    return (latitude, longitude)


def get_polyline_from_here_maps(
    source_latitude, source_longitude, destination_latitude, destination_longitude
):
    """Fetching Polyline from Here Maps"""
    # Query Here Maps with Key and Source-Destination coordinates
    url = "{a}?transportMode=car&origin={b},{c}&destination={d},{e}&apiKey={f}&return=polyline".format(
        a=HERE_API_URL,
        b=source_latitude,
        c=source_longitude,
        d=destination_latitude,
        e=destination_longitude,
        f=HERE_API_KEY,
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
    return polyline_from_heremaps


"""Calling Tollguru API"""


def get_rates_from_tollguru(polyline):
    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLLGURU_API_KEY}
    params = {
        **request_parameters,
        "source": "here",
        "polyline": polyline,  #  this is polyline that we fetched from the mapping service
    }

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

# Step 2 : Get polyline for given source-destination route
polyline_from_heremaps = get_polyline_from_here_maps(
    source_latitude, source_longitude, destination_latitude, destination_longitude
)

# Step 3 : Get rates from tollguru
rates_from_tollguru = get_rates_from_tollguru(polyline_from_heremaps)

# Print the rates of all the available modes of payment
if rates_from_tollguru == {}:
    print("The route doesn't have tolls")
else:
    print(f"The rates are \n {rates_from_tollguru}")

"""Program Ends"""
