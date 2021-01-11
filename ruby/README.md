# [HERE](https://developer.here.com/)

### Get API key to access HERE Maps APIs (if you have an API key skip this)
#### Step 1: Login/Singup
* Create an account to access [HERE Developer Portal](https://developer.here.com/)
* go to [signup/login](https://developer.here.com/login)
* you will need to agree to [HERE Map's Terms of Service](https://legal.here.com/en-gb/terms)

#### Step 2: Getting your Key
* Login to your HERE Maps Developer Portal
* Go to https://developer.here.com/projects
* Select your project
* After selecting your project you need to select the service, select
  `REST APIs`


With this in place, make a GET request: https://router.hereapi.com/v8/routes?transportMode=car&origin=#{SOURCE[:latitude]},#{SOURCE[:longitude]}&destination=#{DESTINATION[:latitude]},#{DESTINATION[:longitude]}&apiKey=#{KEY}&return=polyline
### Note:
* HERE accepts source and destination, as `:` seperated `[:longitude,:latitude]`.
* HERE maps doesn't return us route as a `encoded polyline`, but as
  `flexible polyline`, we will convert from `flexible polyline` to
  `encoded polyline`. HERE maps doesn't have support for flexible polyline gem in ruby
* To decode `flexible polyline` we used HERE maps flexpolyline module and modified python script to make 
  it work for ruby

```ruby
# Polyline from JSON
polyline = json_parsed['routes'].map { |x| x['sections'] }.flatten(2). map { |y| y['polyline'] }.pop
here_decoded = decode(polyline)
google_encoded_polyline = FastPolylines.encode(here_decoded)
```

```ruby
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
```

Note:

We extracted the polyline for a route from HERE Maps API

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to [receive a free key from TollGuru](https://tollguru.com/developers/get-api-key)
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.

the last line can be changed to following

```ruby
TOLLGURU_URL = 'https://dev.tollguru.com/v1/calc/route'
TOLLGURU_KEY = ENV['TOLLGURU_KEY']
headers = {'content-type' => 'application/json', 'x-api-key' => TOLLGURU_URL}
body = {'source' => "here", 'polyline' => google_encoded_polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
tollguru_response = HTTParty.post(TOLLGURU_URL,:body => body.to_json, :headers => headers)
```

The working code can be found in main.rb file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
