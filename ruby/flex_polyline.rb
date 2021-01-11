DECODING_TABLE = [
    62, -1, -1, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1,
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, -1, -1, -1, -1, 63, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
    36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51
]

FORMAT_VERSION = 1



def decode(encoded)
    #Return a list of coordinates. The number of coordinates are 2 or 3 depending on the polyline content
    return iter_decode(encoded).to_a
end

def decode_char(char)
    #Decode a single char to the corresponding value
    char_value = char.ord

    begin
        value = DECODING_TABLE[char_value - 45]
    rescue IndexError
        raise StandardError.new('Invalid encoding')
    end
    if value < 0
        raise StandardError.new('Invalid encoding')
    end
    return value
end

def decode_unsigned_values(encoded)
    #Return an iterator over encoded unsigned values part of an `encoded` polyline
    Enumerator.new do |enum|
        result = shift = 0
        encoded.each_char do |char|
            value = decode_char(char)
            result = result | ((value & 0x1F) << shift)
            if (value & 0x20) == 0
                enum.yield result
                result = shift = 0
            else
                shift += 5
            end
        end
        if shift > 0
            raise StandardError.new('Invalid encoding')
        end
    end
end

def to_signed(value)
    #Decode the sign from an unsigned value
    if value & 1
        value = ~value
    end
    value = (value >> 1)
    return value
end

PolylineHeader = Struct.new(:PolylineHeader, :precision,:third_dim,:third_dim_precision, keyword_init:true)

def decode_header(decoder)
    #Decode the polyline header from an `encoded_char`. Returns a PolylineHeader object."""
    version = decoder.next
    if version != FORMAT_VERSION
        raise ValueError('Invalid format version')
    end
    value = decoder.next
    precision = value & 15
    value = (value >> 4)
    third_dim = value & 7
    third_dim_precision = (value >> 3) & 15
    return PolylineHeader.new(precision:precision, third_dim:third_dim, third_dim_precision:third_dim_precision)
end


def iter_decode(encoded)
    #Return an iterator over coordinates. The number of coordinates are 2 or 3 depending on the polyline content
    Enumerator.new do |dec_st|
        last_lat, last_lng, last_z = 0 , 0, 0
        decoder = decode_unsigned_values(encoded)

        header = decode_header(decoder)
        factor_degree = 10.0 ** header.precision
        factor_z = 10.0 ** header.third_dim_precision
        third_dim = header.third_dim
            loop do
                begin
                    last_lat += to_signed(decoder.next)
                    last_lng += to_signed(decoder.next)
                    if third_dim!= 0
                        last_z += to_signed(decoder.next)
                        dec_st.yield ({'lat' => last_lat / factor_degree,'lng' => last_lng / factor_degree,'z' => last_z / factor_z}).values
                    else
                        dec_st.yield ({'lat'=> last_lat / factor_degree,'lng' => last_lng / factor_degree}).values
                    end
                rescue StopIteration
                    break
                # raise ValueError("Invalid encoding. Premature ending reached")
                end
            end

    end
end


           