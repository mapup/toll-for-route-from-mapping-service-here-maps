require 'HTTParty'
require 'json'
require_relative 'flex_polyline'
require "fast_polylines"
require "cgi"

START_LOC = "Dallas, TX"
END_LOC = "New York, NY"
KEY = ENV['HERE_KEY']

def get_coord_hash(loc)
    geocoding_url = "https://geocode.search.hereapi.com/v1/geocode?q=#{CGI::escape(loc)}&apiKey=#{KEY}"
    coord = JSON.parse(HTTParty.get(geocoding_url).body)
    return (coord['items'].pop)['position']
end

# Get source coordinates from Geocoding API
source = get_coord_hash(START_LOC)
# Get destination coordinates from Geocoding API
destination = get_coord_hash(END_LOC)

# GET Request to HERE Maps for Polyline

HERE_URL = "https://router.hereapi.com/v8/routes?transportMode=car&origin=#{source["lat"]},#{source["lng"]}&destination=#{destination["lat"]},#{destination["lng"]}&apiKey=#{KEY}&return=polyline"
RESPONSE = HTTParty.get(HERE_URL).body
json_parsed = JSON.parse(RESPONSE)

# Extracting HERE polyline from JSON
polyline = json_parsed['routes'].map { |x| x['sections'] }.flatten(2). map { |y| y['polyline'] }.pop
# Using flex_polyline decode method to get coordinates
here_decoded = decode(polyline)
# Converting coordinates to google polyline
google_encoded_polyline = FastPolylines.encode(here_decoded)

# Sending POST request to TollGuru
TOLLGURU_URL = 'https://dev.tollguru.com/v1/calc/route'
TOLLGURU_KEY = ENV['TOLLGURU_KEY']
headers = {'content-type' => 'application/json', 'x-api-key' => TOLLGURU_KEY}
body = {'source' => "here", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
tollguru_response = HTTParty.post(TOLLGURU_URL,:body => body.to_json, :headers => headers)
