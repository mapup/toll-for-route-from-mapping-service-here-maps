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
* Code to play with `flexible polyline` can be found at `Not Found`

```php

// Code will be added soon for encoding flexible polyline..

```

```php

//using heremaps API

//Source and Destination Coordinates..
$source_longitude='-96.79448';
$source_latitude='32.78165';
$destination_longitude='-96.818';
$destination_latitude='32.95399';

$key = 'heremaps_api_key';

$url='https://router.hereapi.com/v8/routes?transportMode=car&origin='.$source_latitude.','.$source_longitude.'&destination='.$destination_latitude.','.$destination_longitude.'&apiKey='.$key.'&return=polyline';
//connection...

$heremaps = curl_init();

curl_setopt($heremaps, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($heremaps, CURLOPT_SSL_VERIFYPEER, false);

curl_setopt($heremaps, CURLOPT_URL, $url);
curl_setopt($heremaps, CURLOPT_RETURNTRANSFER, true);

//getting response from googleapis..
$response = curl_exec($heremaps);
$err = curl_error($heremaps);

curl_close($heremaps);

if ($err) {
	  echo "cURL Error #:" . $err;
} else {
	  echo "200 : OK\n";
}

//extracting polyline from the JSON response..
$data_heremaps = json_decode($response, true);

//flexible polyline extraction..
$polyline = $data_heremaps['routes']['0']['section']['0']['polyline'];

'''

encoding flexible polyline to encoded polyline
$polyline_heremaps = @coded_will_be_added_soon

'''

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

```php

//using tollguru API..
$curl = curl_init();

curl_setopt($curl, CURLOPT_SSL_VERIFYHOST, false);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, false);


$postdata = array(
	"source" => "here",
	"polyline" => $polyline_heremaps
);

//json encoding source and polyline to send as postfields..
$encode_postData = json_encode($postdata);

curl_setopt_array($curl, array(
CURLOPT_URL => "https://dev.tollguru.com/v1/calc/route",
CURLOPT_RETURNTRANSFER => true,
CURLOPT_ENCODING => "",
CURLOPT_MAXREDIRS => 10,
CURLOPT_TIMEOUT => 30,
CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
CURLOPT_CUSTOMREQUEST => "POST",


//sending heremaps polyline to tollguru
CURLOPT_POSTFIELDS => $encode_postData,
CURLOPT_HTTPHEADER => array(
				      "content-type: application/json",
				      "x-api-key: 8hjbGhmFqP8HBQJ6NbMpT2FjRNhhtdgT"),
));

$response = curl_exec($curl);
$err = curl_error($curl);

curl_close($curl);

if ($err) {
	  echo "cURL Error #:" . $err;
} else {
	  echo "200 : OK\n";
}

//response from tollguru..
$data = var_dump(json_decode($response, true));
print_r($data);

```

The working code can be found in `php_curl_heremaps.php` file.

## License
ISC License (ISC). Copyright 2020 &copy;TollGuru. https://tollguru.com/

Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
