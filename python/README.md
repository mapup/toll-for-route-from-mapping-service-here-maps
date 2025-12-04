# HERE Maps + TollGuru Python Integration

Get toll rates for routes using HERE Maps routing and TollGuru toll calculation APIs.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Running the Scripts](#running-the-scripts)
- [Testing](#testing)
- [API Endpoints Used](#api-endpoints-used)
- [API Documentation](#api-documentation)

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- HERE Maps API key
- TollGuru API key

## Installation

### 1. Install Python (if not already installed)

#### Check if Python is installed

Open your terminal/command prompt and run:

```bash
python --version
```

or

```bash
python3 --version
```

If you see a version number (e.g., `Python 3.x.x`), Python is already installed. Skip to step 2.

#### Installing Python

**On macOS:**
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
# Visit https://www.python.org/downloads/macos/
```

**On Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**On Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
```

**On Windows:**
- Download the installer from https://www.python.org/downloads/windows/
- Run the installer
- **Important:** Check the box "Add Python to PATH" during installation
- Click "Install Now"

#### Verify pip is installed

After installing Python, verify pip is available:

```bash
pip --version
```

or

```bash
pip3 --version
```

**Note on pip vs pip3:**
- If you have only Python 3 installed, use `pip`
- If you have both Python 2 and Python 3, use `pip3` for Python 3 packages
- Similarly, use `python` or `python3` based on your system

For the rest of this guide:
- Replace `python3` with `python` if that's what works on your system
- Replace `pip3` with `pip` if that's what works on your system

### 2. Create a Virtual Environment

Creating a virtual environment helps isolate project dependencies from your system Python installation.

**On macOS/Linux:**
```bash
# Navigate to the python directory
cd python

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

**On Windows:**
```cmd
# Navigate to the python directory
cd python

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### 3. Install Required Dependencies

With the virtual environment activated, install all required Python packages:

**If using pip:**
```bash
pip install -r requirements.txt
```

**If using pip3:**
```bash
pip3 install -r requirements.txt
```

This will install:
- `requests` - For making HTTP API calls
- `flexpolyline` - For decoding HERE Maps flexible polylines
- `polyline` - For encoding polylines
- `python-dotenv` - For loading environment variables from .env file

### 4. Deactivating the Virtual Environment

When you're done working, you can deactivate the virtual environment:

```bash
deactivate
```

## Environment Variables

Create a `.env` file in the `python` directory with your API keys:

```bash
HERE_API_KEY=your_here_maps_api_key_here
TOLLGURU_API_KEY=your_tollguru_api_key_here
```

**Important:** Never commit your `.env` file to version control. It should be in `.gitignore`.

## Running the Scripts

### Main Script

The main script (`Here_Maps.py`) calculates tolls for a single route:

```bash
# Make sure your virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

You can modify the source and destination in the script:
```python
source = "Philadelphia, PA"
destination = "New York, NY"
```

### Output

The script will display:
- API request payload sent to TollGuru
- API response received from TollGuru
- Toll costs for different payment methods (tag, cash, etc.)

## Testing

The `Testing` folder contains `Test_Here_Maps.py` which processes multiple routes from a CSV file.

### Running Tests

```bash
cd Testing

# Make sure .env file exists in Testing directory
# Run the test script (use python or python3 depending on your system)
python Test_Here_Maps.py
# or
python3 Test_Here_Maps.py
```

### Input File Format

The test script reads from `testCases.csv` with the following columns:
- Test case ID
- Source address
- Destination address
- Departure time (optional)
- Vehicle type (optional, defaults to "2AxlesAuto")

### Output

Results are saved to `testCases_result.csv` with additional columns:
- Input polyline
- TollGuru tag cost
- TollGuru cash cost
- Query time in seconds

The script also displays detailed logs including:
- Departure/arrival times
- Polyline information
- LocTimes array
- TollGuru API request payload
- TollGuru API response

---

# API Endpoints Used

This project uses the following API endpoints:

## HERE Maps API Endpoints

### 1. Geocoding API
**Endpoint:** `https://geocode.search.hereapi.com/v1/geocode`

**Purpose:** Converts addresses to geographic coordinates (latitude, longitude)

**Method:** GET

**Parameters:**
- `q` - Address to geocode (e.g., "Philadelphia, PA")
- `apiKey` - Your HERE Maps API key

**Used in:**
- `get_geocodes_from_here_maps()` function

### 2. Routing API
**Endpoint:** `https://router.hereapi.com/v8/routes`

**Purpose:** Calculates routes between two points and returns polyline data

**Method:** GET

**Parameters:**
- `transportMode` - Type of transport (car, truck, bus)
- `origin` - Starting coordinates (latitude,longitude)
- `destination` - Ending coordinates (latitude,longitude)
- `apiKey` - Your HERE Maps API key
- `return` - Data to return (polyline)

**Used in:**
- `get_polyline_from_here_maps()` function

## TollGuru API Endpoint

### Complete Polyline API
**Endpoint:** `https://apis.tollguru.com/toll/v2/complete-polyline-from-mapping-service`

**Purpose:** Calculates toll costs for a route based on polyline data

**Method:** POST

**Headers:**
- `Content-type: application/json`
- `x-api-key: YOUR_TOLLGURU_API_KEY`

**Request Body:**
```json
{
  "source": "here",
  "polyline": "encoded_polyline_string",
  "vehicle": {
    "type": "2AxlesAuto"
  },
  "departure_time": "2021-01-05T09:46:08Z",
  "locTimes": [[0, 1764665410], [872, 1764669484]]
}
```

**Parameters:**
- `source` - Mapping service name (here, google, mapbox, etc.)
- `polyline` - Encoded polyline string from mapping service
- `vehicle.type` - Vehicle type (see [TollGuru vehicle types](https://tollguru.com/toll-api-docs#vehicle-types-supported-by-tollguru))
- `departure_time` - ISO 8601 timestamp (optional but recommended)
- `locTimes` - Array of [index, timestamp] pairs for accurate time-based tolls (optional)

**Used in:**
- `get_rates_from_tollguru()` function

**Response:**
Returns toll costs in different payment methods (tag, cash, license plate, etc.)

---

# API Documentation

## [HERE Maps](https://developer.here.com/)

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
