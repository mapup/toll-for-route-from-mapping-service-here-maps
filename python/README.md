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
  
#### Step 3: Getting Geocodes for source and destination from Here
* Use the code below to call Here API to fetch geocodes for an address.
```python
import json
import requests
import os

#API key for Here Maps
key=os.environ.get('Here_Maps_API_Key')

def get_geocodes_from_here_maps(address):
    url='https://geocoder.ls.hereapi.com/6.2/geocode.json'
    para={
        'searchtext': address ,
        'apiKey'    : key
        }
    response_from_here=requests.get(url,params=para).json()
    latitude,longitude=response_from_here['Response']['View'][0]['Result'][0]['Location']['DisplayPosition'].values()
    return(latitude,longitude)
```
With this in place, make a GET request: https://router.hereapi.com/v8/routes?transportMode=car&origin=${source.latitude},${source.longitude}&destination=${destination.latitude},${destination.longitude}&apiKey=${key}&return=polyline

#### Step 4: Extrating Flexpolyline from Here and converting that to Encoded(Google) Polyline
### Note:
* HERE accepts source and destination, as `:` seperated `{longitude,latitude}`.
* HERE maps doesn't return us route as a `endoced polyline`, but as
  `flexible polyline`, we will covert it from `flexible polyline` to
  `encoded polyline`.
* Code to play with `flexible polyline` can be found at https://github.com/heremaps/flexible-polyline/tree/master/python

```python
import flexpolyline as fp
import polyline as poly

flex_polyline_here=response["routes"][0]["sections"][0]['polyline']     # heremaps provide a flexpolyline
polyline_from_heremaps=poly.encode(fp.decode(flex_polyline_here))       # we converted that to encoded(google) polyline
return(polyline_from_heremaps)
```
```python
import json
import requests
import flexpolyline as fp
import polyline as poly
import os

#API key for Here Maps
key=os.environ.get('Here_Maps_API_Key')

def get_polyline_from_here_maps(source_latitude,source_longitude,destination_latitude,destination_longitude):
    #Query Here Maps with Key and Source-Destination coordinates
    url='https://router.hereapi.com/v8/routes?transportMode=car&origin={a},{b}&destination={c},{d}&apiKey={e}&return=polyline'.format(a=source_latitude,b=source_longitude,c=destination_latitude,d=destination_longitude,e=key)
    #converting the response to json
    response=requests.get(url).json()                               
    #Extracting polyline
    flex_polyline_here=response["routes"][0]["sections"][0]['polyline']     # heremaps provide a flexpolyline
    polyline_from_heremaps=poly.encode(fp.decode(flex_polyline_here))       # we converted that to encoded(google) polyline
    return(polyline_from_heremaps)
```

Note:

We extracted the polyline for a route from HERE Maps API

We need to send this route polyline to TollGuru API to receive toll information

## [TollGuru API](https://tollguru.com/developers/docs/)

### Get key to access TollGuru polyline API
* Create a dev account to receive a free key from TollGuru https://tollguru.com/developers/get-api-key
* Suggest adding `vehicleType` parameter. Tolls for cars are different than trucks and therefore if `vehicleType` is not specified, may not receive accurate tolls. For example, tolls are generally higher for trucks than cars. If `vehicleType` is not specified, by default tolls are returned for 2-axle cars. 
* Similarly, `departure_time` is important for locations where tolls change based on time-of-the-day.
* Use the following function to get rates from TollGuru.

```python
import json
import requests
import os

#API key for Tollguru
Tolls_Key = os.environ.get('TollGuru_API_Key')

def get_rates_from_tollguru(polyline):
    #Tollguru querry url
    Tolls_URL = 'https://dev.tollguru.com/v1/calc/route'
    
    #Tollguru resquest parameters
    headers = {
                'Content-type': 'application/json',
                'x-api-key': Tolls_Key
                }
    params = {   
                # explore https://tollguru.com/developers/docs/ to get best off all the parameter that tollguru offers 
                'source': "here",
                'polyline': polyline,                       #  this is polyline that we fetched from the mapping service     
                'vehicleType': '2AxlesAuto',                #'''Visit https://tollguru.com/developers/docs/#vehicle-types to know more options'''
                'departure_time' : "2021-01-05T09:46:08Z"   #'''Visit https://en.wikipedia.org/wiki/Unix_time to know the time format'''
                }
    
    #Requesting Tollguru with parameters
    response_tollguru= requests.post(Tolls_URL, json=params, headers=headers).json()
    
    #checking for errors or printing rates
    if str(response_tollguru).find('message')==-1:
        return(response_tollguru['route']['costs'])
    else:
        raise Exception(response_tollguru['message'])
```

The working code can be found in Here_Maps.py file.

## License
ISC License (ISC). Copyright 2020 &copy ;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
