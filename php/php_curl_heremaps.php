<?php
//using heremaps API

//Source and Destination Coordinates..
$source_longitude='-96.79448';
$source_latitude='32.78165';
$destination_longitude='-96.818';
$destination_latitude='32.95399';
$key = 'XG3D1wgroxSBF0IHXvECeDFpaL_H9diRkdj3SxQnnSo';

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

//polyline extraction..
$data_new = $data_heremaps['routes'];
$new_data = $data_new['0'];
$pol_data = $new_data['sections'];
$pol_data_new = $pol_data['0'];
//polyline..
$polyline = $pol_data_new['polyline'];

// encoding flexible polyline to encoded polyline
// polyline_heremaps = `coded_will_be_added_soon`


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
var_dump(json_decode($response, true));
// $data = var_dump(json_decode($response, true));
//print_r($data);
?>