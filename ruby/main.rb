require 'HTTParty'
require 'json'
require_relative 'flex_polyline'
require "fast_polylines"

# Source Details in latitude-longitude pair (Dallas, TX - coordinates)
SOURCE = {longitude: '-96.7970', latitude: '32.7767'}
# Destination Details in latitude-longitude pair (New York, NY - coordinates)
DESTINATION = {longitude: '-96.924', latitude: '32.9756' }

# GET Request to HERE Maps for Polyline
KEY = ENV['HERE_KEY']
HERE_URL = "https://router.hereapi.com/v8/routes?transportMode=car&origin=#{SOURCE[:latitude]},#{SOURCE[:longitude]}&destination=#{DESTINATION[:latitude]},#{DESTINATION[:longitude]}&apiKey=#{KEY}&return=polyline"
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
a = 1