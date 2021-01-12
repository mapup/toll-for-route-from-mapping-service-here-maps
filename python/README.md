# [HERE](https://developer.here.com/)

### Get API key to access HERE Maps APIs (if you have an API key skip this)
#### Step 1: Login/Singup
* Create an account to access [HERE Developer Portal](https://developer.here.com/)
* go to signup/login link https://developer.here.com/login
* you will need to agree to HERE's Terms of Service https://legal.here.com/en-gb/terms

#### Step 2: Getting your Key
* Login to your HERE Maps Developer Portal
* Go to https://developer.here.com/projects
* Select your project
* After selecting your project you need to select the service, select
  `REST APIs`


With this in place, make a GET request: https://router.hereapi.com/v8/routes?transportMode=car&origin=${source.latitude},${source.longitude}&destination=${destination.latitude},${destination.longitude}&apiKey=${key}&return=polyline
### Note:
* HERE accepts source and destination, as `:` seperated `{longitude,latitude}`.
* HERE maps doesn't return us route as a `endoced polyline`, but as
  `flexible polyline`, we will covert it from `flexible polyline` to
  `encoded polyline`.
* Code to play with `flexible polyline` can be found at https://github.com/heremaps/flexible-polyline/tree/master/python

```python
import flexpolyline as fp
import polyline as Poly

polyline_here=response["routes"][0]["sections"][0]['polyline']  #this polyline is here map polypine , but we need google polyline to get Tollguru API working
polyline=Poly.encode(fp.decode(polyline_here))                  #we decoded here polyline (flexpolyline) into coordinates and encoded that to google polyline

```

```python
#Importing modules
import json
import requests
import os
import flexpolyline as fp
import polyline as Poly

'''Fetching Polyline from Here Maps'''

#API key for MapmyIndia
key=os.environ.get('Here_Maps_API_Key')

#Source and Destination Coordinates
#Dallas, TX
source_longitude='-96.7970'
source_latitude='32.7767'
#New York, NY
destination_longitude='-74.0060'
destination_latitude='40.7128'

#Query MapmyIndia with Key and Source-Destination coordinates
url='https://router.hereapi.com/v8/routes?transportMode=car&origin={a},{b}&destination={c},{d}&apiKey={e}&return=polyline'.format(a=source_latitude,b=source_longitude,c=destination_latitude,d=destination_longitude,e=key)

#converting the response to json
response=requests.get(url).json()
   
#Extracting polyline
polyline_here=response["routes"][0]["sections"][0]['polyline']  #this polyline is here map polypine , but we need google polyline to get Tollguru API working
polyline=Poly.encode(fp.decode(polyline_here))                  #we decoded here polyline (flexpolyline) into coordinates and encoded that to google polyline


```

Note:

We extracted the polyline for a route from HERE Maps API

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* create a dev account to receive a free key from TollGuru https://tollguru.com/developers/get-api-key
* suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.

the last line can be changed to following

```python

'''Calling Tollguru API'''

#API key for Tollguru
Tolls_Key = os.environ.get('TollGuru_API_Key')

#Tollguru querry url
Tolls_URL = 'https://dev.tollguru.com/v1/calc/route'

#Tollguru resquest parameters
headers = {
            'Content-type': 'application/json',
            'x-api-key': Tolls_Key
          }
params = {
            'source': "here",
            'polyline': polyline ,                      #  this is polyline that we fetched from the mapping service     
            'vehicleType': '2AxlesAuto',                #'''TODO - Need to provide users a slist of acceptable values for vehicle type'''
            'departure_time' : "2021-01-05T09:46:08Z"   #'''TODO - Specify time formats'''
        }

#Requesting Tollguru with parameters
response_tollguru= requests.post(Tolls_URL, json=params, headers=headers).json()

#checking for errors or printing rates
if str(response_tollguru).find('message')==-1:
    print('\n The Rates Are ')
    #extracting rates from Tollguru response is no error
    print(*response_tollguru['summary']['rates'].items(),end="\n\n")
else:
    raise Exception(response_tollguru['message'])
```

The working code can be found in index.js file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
