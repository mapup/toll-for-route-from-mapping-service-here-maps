require 'HTTParty'
require 'json'
require_relative 'flex_polyline'
require "fast_polylines"
require 'cgi'

HERE_API_KEY = ENV["HERE_API_KEY"]  # API key for Here Maps
HERE_API_URL = "https://router.hereapi.com/v8/routes"
HERE_GEOCODE_API_URL = "https://geocode.search.hereapi.com/v1/geocode"

TOLLGURU_API_KEY = ENV["TOLLGURU_API_KEY"]  # API key for Tollguru
TOLLGURU_API_URL = "https://apis.tollguru.com/toll/v2"
POLYLINE_ENDPOINT = "complete-polyline-from-mapping-service"

def get_toll_rate(source,destination)
    def get_coord_hash(loc)
        geocoding_url = "#{HERE_GEOCODE_API_URL}?q=#{CGI::escape(loc)}&apiKey=#{HERE_API_KEY}"
        coord = HTTParty.get(geocoding_url)
        begin
            return (JSON.parse(coord.body)['items'].pop)['position']
        rescue
            raise "#{coord.response.code} #{coord.response.message}, #{coord.body}"
        end
    end

    # Get source coordinates from Geocoding API
    source = get_coord_hash(source)
    # Get destination coordinates from Geocoding API
    destination = get_coord_hash(destination)

    # GET Request to HERE Maps for Polyline

    here_url = "#{HERE_API_URL}?transportMode=car&origin=#{source["lat"]},#{source["lng"]}&destination=#{destination["lat"]},#{destination["lng"]}&apiKey=#{HERE_API_KEY}&return=polyline"
    response = HTTParty.get(here_url)
    begin
        if response.response.code == '200'
            json_parsed = JSON.parse(response.body)
            # Extracting HERE polyline from JSON
            polyline = json_parsed['routes'].map { |x| x['sections'] }.flatten(2). map { |y| y['polyline'] }.pop
             # Using flex_polyline decode method to get coordinates
            here_decoded = decode(polyline)
            # Converting coordinates to google polyline
            google_encoded_polyline = FastPolylines.encode(here_decoded)
        else
            raise "error"
        end
    rescue Exception => e
        raise "#{response.response.code} #{response.response.message}"
    end

    # Sending POST request to TollGuru
    tollguru_url = "#{TOLLGURU_API_URL}/#{POLYLINE_ENDPOINT}"
    headers = {'content-type' => 'application/json', 'x-api-key' => TOLLGURU_API_KEY}
    body = {'source' => "here", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
    tollguru_response = HTTParty.post(tollguru_url,:body => body.to_json, :headers => headers, :timeout => 400)
    begin
        toll_body = JSON.parse(tollguru_response.body)    
        if toll_body["route"]["hasTolls"] == true
            return google_encoded_polyline,toll_body["route"]["costs"]["tag"], toll_body["route"]["costs"]["cash"] 
        else
            raise "No tolls encountered in this route"
        end
    rescue Exception => e
        puts e.message 
    end

end

