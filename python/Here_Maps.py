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
response=requests.get(url).json()                               #'''TODO : Check for exceptions in response
   
#Extracting polyline
polyline_here=response["routes"][0]["sections"][0]['polyline']  #this polyline is here map polypine , but we need google polyline to get Tollguru API working
polyline=Poly.encode(fp.decode(polyline_here))                  #we decoded here polyline (flexpolyline) into coordinates and encoded that to google polyline



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
    #extracting rates from Tollguru response if there's no error
    print(*response_tollguru['summary']['rates'].items(),end="\n\n")
else:
    raise Exception(response_tollguru['message'])

