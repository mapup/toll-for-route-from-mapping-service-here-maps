#Importing modules
import json
import requests
import flexpolyline as fp
import polyline as poly
import os
#API key for Here Maps
key=os.environ.get('Here_Maps_API_Key')
#API key for Tollguru
Tolls_Key = os.environ.get('TollGuru_API_Key')

'''Fetching geocodes form here maps'''
def get_geocodes_from_here_maps(address):
    url='https://geocoder.ls.hereapi.com/6.2/geocode.json'
    para={
        'searchtext': address ,
        'apiKey'    : key
        }
    response_from_here=requests.get(url,params=para).json()
    latitude,longitude=response_from_here['Response']['View'][0]['Result'][0]['Location']['DisplayPosition'].values()
    return(latitude,longitude)

'''Fetching Polyline from Here Maps'''
def get_polyline_from_here_maps(source_latitude,source_longitude,destination_latitude,destination_longitude):
    #Query Here Maps with Key and Source-Destination coordinates
    url='https://router.hereapi.com/v8/routes?transportMode=car&origin={a},{b}&destination={c},{d}&apiKey={e}&return=polyline'.format(a=source_latitude,b=source_longitude,c=destination_latitude,d=destination_longitude,e=key)
    #converting the response to json
    response=requests.get(url).json()                               
    #Extracting polyline
    flex_polyline_here=response["routes"][0]["sections"][0]['polyline']     # heremaps provide a flexpolyline
    polyline_from_heremaps=poly.encode(fp.decode(flex_polyline_here))       # we converted that to encoded(google) polyline
    return(polyline_from_heremaps)


'''Calling Tollguru API'''
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
                'polyline': polyline ,                      #  this is polyline that we fetched from the mapping service     
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


            
'''Testing'''
#Importing Functions
from csv import reader,writer
temp_list=[]
with open('testCases.csv','r') as f:
    csv_reader=reader(f)
    for count,i in enumerate(csv_reader):
        #if count>2:
        #  break
        if count==0:
            i.extend(("Polyline","TollGuru_Rates"))
        else:
            try:
                source_latitude,source_longitude=get_geocodes_from_here_maps(i[1])
                destination_latitude,destination_longitude=get_geocodes_from_here_maps(i[2])
                polyline=get_polyline_from_here_maps(source_latitude,source_longitude,destination_latitude,destination_longitude)
                i.append(polyline)
            except:
                i.append("Routing Error") 
            
            try:
                rates=get_rates_from_tollguru(polyline)
            except:
                i.append(False)
            if rates=={}:
                i.append("NO_TOLL")
            else:
                i.append(rates['tag'])
        #print(f"{len(i)}   {i}\n")
        temp_list.append(i)

with open('testCases_result.csv','w') as f:
    writer(f).writerows(temp_list)

'''Testing Ends'''