require 'HTTParty'
require 'json'
require_relative 'flex_polyline'
require "fast_polylines"
require "cgi"

HERE_API_KEY = ENV["HERE_API_KEY"]  # API key for Here Maps
HERE_API_URL = "https://router.hereapi.com/v8/routes"
HERE_GEOCODE_API_URL = "https://geocode.search.hereapi.com/v1/geocode"

TOLLGURU_API_KEY = ENV["TOLLGURU_API_KEY"]  # API key for Tollguru
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"
POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service"

source = 'Philadelphia, PA'
destination = 'New York, NY'

# Explore https://tollguru.com/toll-api-docs to get the best of all the parameters that tollguru has to offer
request_parameters = {
  "vehicle": {
    "type": "2AxlesAuto",
  },
  # Visit https://en.wikipedia.org/wiki/Unix_time to know the time format
  "departure_time": "2021-01-05T09:46:08Z",
}

def get_coord_hash(loc)
    geocoding_url = "#{HERE_GEOCODE_API_URL}?q=#{CGI::escape(loc)}&apiKey=#{HERE_API_KEY}"
    coord = JSON.parse(HTTParty.get(geocoding_url).body)
    return (coord['items'].pop)['position']
end

# Get source coordinates from Geocoding API
source = get_coord_hash(source)
# Get destination coordinates from Geocoding API
destination = get_coord_hash(destination)

# GET Request to HERE Maps for Polyline

HERE_URL = "#{HERE_API_URL}?transportMode=car&origin=#{source["lat"]},#{source["lng"]}&destination=#{destination["lat"]},#{destination["lng"]}&apiKey=#{HERE_API_KEY}&return=polyline"
RESPONSE = HTTParty.get(HERE_URL).body
json_parsed = JSON.parse(RESPONSE)

# Extracting HERE polyline from JSON
polyline = json_parsed['routes'].map { |x| x['sections'] }.flatten(2). map { |y| y['polyline'] }.pop
# Using flex_polyline decode method to get coordinates
here_decoded = decode(polyline)
# Converting coordinates to google polyline
google_encoded_polyline = FastPolylines.encode(here_decoded)

# Sending POST request to TollGuru
TOLLGURU_URL = "#{TOLLGURU_API_URL}/#{POLYLINE_ENDPOINT}"
headers = {'content-type': 'application/json', 'x-api-key': TOLLGURU_API_KEY}
body = {
  'source': "esri",
  'polyline': google_encoded_polyline,
  **request_parameters,
}
tollguru_response = HTTParty.post(TOLLGURU_URL,:body => body.to_json, :headers => headers)
