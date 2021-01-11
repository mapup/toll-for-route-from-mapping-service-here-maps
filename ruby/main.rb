require 'HTTParty'
require 'json'
require '.\flex_polyline.rb'
require "fast_polylines"

# Dallas, TX
source = {
    longitude: '-96.7970',
    latitude: '32.7767',
}
# New York, NY
destination = {
    longitude: '-96.924',
    latitude: '32.9756'
}

key = ''
here_url = "https://router.hereapi.com/v8/routes?transportMode=car&origin=#{source[:latitude]},#{source[:longitude]}&destination=#{destination[:latitude]},#{destination[:longitude]}&apiKey=#{key}&return=polyline"

response = HTTParty.get(here_url).body

json_parsed = JSON.parse(response)
polyline = json_parsed['routes'].map { |x| x['sections'] }.flatten(2). map { |y| y['polyline'] }.pop
#polyline = 'BA3E0E'
here_decoded = decode(polyline)
google_polyline = FastPolylines.encode(here_decoded)
#_polyline = 'izruB~yyzQx@CAREhAOvEMxEG`D@Nh@?`CClBItEEhEIpCM`AAb@?VMb@AIf@U|ICzFN~AMvBi@bDmAtG}@lEaAvE[`C]`BWjDAxCDtHKxGCtLBlX@bJ@bAJjATv@zAlCzBdDlD~ErDfFnBjCzDtE|BhDx@fAbCvD|BtEh@lBd@nBf@dBRt@v@zAbBdBdFdEpD|CdDvDxElFjIlIfDjDrBpAtC`A`EhAlEfA|@R|@f@v@l@Xb@N`@Dh@KzBw@vFaDnSuAdIUz@L|ADPUxAu@xEeAxHkCdQqClPmCjQk@pCk@nCYd@_@jBW`@]Ne@D_AUgJeDmKqDuLaE{MmEcBo@{GgC}DwAaA]eAQeAGwAD}Bb@_D`B{EhCsCn@o@@aBQk@EqB@kAFoA^yCZmB@gAEwAQeD{@{B_@}@EeB@w@HoEfAaJjCwVvHwb@nMeo@nR{GpBwAXmAH}BKsD{@}@W_Ba@mDu@{AGcBNoA`@_BhAm@r@k@lA]pAIt@QfFOvAOr@cAxBiAnAoBfAeCbAIFILqBp@_Bf@aF~AcUjHsG~AeDh@qD^gKp@oDZeDj@oC|@gBp@uAZkC^cCG}BMqD}@wEcA}BYuBKoBEwCBeCBqEMmNCaXMoVMeKMcN@cEKmCAsj@QqIOcIG_VKoPKcJDkMUiE?aC?{EI_TOsOImB@__@]uNI}BGaMI}DFgLC{XJka@[iC?cBH_Dr@eChAgCbBcIdG_OzKcClA}GvAeEx@aA\mClBkFfEcElDaK`KqFxFgBfAaJnCmHfCsEvBuCfAmn@xTun@`U}ItDkEpBeGtCiDvAqAXwAL_EF}CDu@H{@?{@LqAZcC`AqB~@QAUMe@e@IU{Bv@{E|Aw@TIAISa@sJc@cJq@kPSuE[mGf@_AVQVId@@VH\^h@vATbBAp@M^SRe@Pk@DgEcBsF{B_D}AsDoDmDyAcAFuAGqAWsBk@}d@aSmIsDwX}LoTgJoWcL_ZkMcQsH}RoIiGiCoDcB_H_DeFwB{K}EsIyDe@g@uFgEuCyCe@g@w@kAkAgBQe@@]NUnHP`@@LLPVF`@Eb@wArCa@zAeChEiGxLkApB_CpEfGb@b@Fb@R|@f@|@ZpB^lGn@rKtBfFz@\XALGN}B|FmA`Fu@nFS~CAjH?RLC?tB?vC?dQ?dT@~L?LMBCBCFCDATHPHFD?CtCQrCcBrLU|@OBCBQCU@iBSsFs@gKcBmEw@cEo@ENq@dEMpAa@pDgArJEl@g@e@y@e@mDqAeA_@G@aAfI'

# Sending POST request to tollguru
tollguruUrl = 'https://dev.tollguru.com/v1/calc/route'

tollguruKey = ''
headers = {'content-type' => 'application/json', 'x-api-key' => tollguruKey}
body = {'source' => "here", 'polyline' => _polyline, 'vehicleType' => "2AxlesAuto", 'departure_time' => "2021-01-05T09:46:08Z"}
tollguru_response = HTTParty.post(tollguruUrl,:body => body.to_json, :headers => headers)