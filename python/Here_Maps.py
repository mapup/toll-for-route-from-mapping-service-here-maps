#Importing modules
import json
import requests
import os
import flexpolyline as fp
import polyline as poly

'''Fetching Polyline from Here Maps'''

#API key for Here Maps
key=os.environ.get('Here_Maps_API_Key')

#Source and Destination Coordinates
#Dallas, TX
source_longitude='-96.7970'
source_latitude='32.7767'
#New York, NY
destination_longitude='-74.0060'
destination_latitude='40.7128'

#Query Here Maps with Key and Source-Destination coordinates
url='https://router.hereapi.com/v8/routes?transportMode=car&origin={a},{b}&destination={c},{d}&apiKey={e}&return=polyline'.format(a=source_latitude,b=source_longitude,c=destination_latitude,d=destination_longitude,e=key)

#converting the response to json
response=requests.get(url).json()                               
   
#Extracting polyline
flex_polyline_here=response["routes"][0]["sections"][0]['polyline']    #heremaps provide a flexpolyline
polyline_from_heremap=poly.encode(fp.decode(flex_polyline_here))       # we converted that to encoded(google) polyline



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
            'polyline': polyline_from_heremap ,         #  this is polyline that we fetched from the mapping service     
            'vehicleType': '2AxlesAuto',                #'''Visit https://tollguru.com/developers/docs/#vehicle-types to know more options'''
            'departure_time' : "2021-01-05T09:46:08Z"   #'''Visit https://en.wikipedia.org/wiki/Unix_time to know the time format'''
        }

#Requesting Tollguru with parameters
response_tollguru= requests.post(Tolls_URL, json=params, headers=headers).json()

#checking for errors or printing rates
if str(response_tollguru).find('message')==-1:
    print('\n The Rates Are ')
    #extracting rates from Tollguru response if there's no error
    print(*response_tollguru['route']['costs'].items(),end="\n\n")
else:
    raise Exception(response_tollguru['message'])

