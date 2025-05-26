import struct
import random
def random_based_on_size(size, endianness):
    byteorder = 'little' if endianness == 'le' else 'big'
    random_number = random.randint(0, 2**(size * 8) - 1)
    return random_number.to_bytes(size, byteorder=byteorder)


def random_based_on_type(size, type_field, endianness, encoding=None):
    if type_field == 'u1':
        return struct.pack(f'{endianness}B', random.randint(0, 0xFF))
    elif type_field == 'u2':
        return struct.pack(f'{endianness}H', random.randint(0, 0xFFFF))
    elif type_field == 'u4':
        return struct.pack(f'{endianness}I', random.randint(0, 0xFFFFFFFF))
    elif type_field == 'u8':
        return struct.pack(f'{endianness}Q', random.randint(0, 0xFFFFFFFFFFFFFFFF))
    elif type_field == 's2':
        return struct.pack(f'{endianness}h', random.randint(-32768, 32767))
    elif type_field == 's4':
        return struct.pack(f'{endianness}i', random.randint(-2147483648, 2147483647))
    elif type_field == 's8':
        return struct.pack(f'{endianness}q', random.randint(-9223372036854775808, 9223372036854775807))
    elif type_field == 'f4':
        return struct.pack(f'{endianness}f', random.uniform(1.17549435e-38, 3.4028235e+38))
    elif type_field == 'f8':
        return struct.pack(f'{endianness}d', random.uniform(2.2250738585072014e-308, 1.7976931348623157e+308))
    elif type_field.startswith('b') and type_field[1:].isdigit():
        bits = int(type_field[1:])
        if 1 <= bits <= 8:
            max_val = (1 << bits) - 1
            value = random.randint(0, max_val)
            return struct.pack(f'{endianness}B', value)
    elif type_field == 'str':
        if encoding == 'UTF-8':
            return ''.join(chr(random.randint(33, 126)) for _ in range(size)).encode('utf-8')
        elif encoding == 'ASCII':
            return ''.join(chr(random.randint(33, 126)) for _ in range(size)).encode('ascii')
        elif encoding and encoding.lower() in ['iso8859-1', 'iso-8859-1', 'latin1', 'latin-1']:
            return ''.join(chr(random.randint(33, 126)) for _ in range(size)).encode('iso-8859-1')
        else:
            return ''.join(chr(random.randint(33, 126)) for _ in range(size)).encode('ascii')
    else:
        return b''

    

def convert_value_to_type(value, type_field, endianness, encoding=None, size=None):
    print("VALUE is", value)
    print(f"Converting value: {value}, type_field: {type_field}, endianness: {endianness}")
    if type_field == 'u1':
        val= struct.pack(f'{endianness}B', value)
        print("Val is ", val)
        return val
    elif type_field == 'b1':
        return struct.pack(f'{endianness}B', value & 0b1)
    elif type_field == 'b4':
        return struct.pack(f'{endianness}B', value & 0b1111)
    elif type_field == 'b2':
        return struct.pack(f'{endianness}B', value & 0b11)
    elif type_field == 'b5':
        return struct.pack(f'{endianness}B', value & 0b11111)
    elif type_field == 'u2':
        return struct.pack(f'{endianness}H', value)
    elif type_field == 'u4':
        return struct.pack(f'{endianness}I', value)
    elif type_field == 'u8':
        return struct.pack(f'{endianness}Q', value)
    elif type_field == 's2':
        return struct.pack(f'{endianness}h', value)
    elif type_field == 's4':
        return struct.pack(f'{endianness}i', value)
    elif type_field == 's8':
        return struct.pack(f'{endianness}q', value)
    elif type_field == 'f4':
        return struct.pack(f'{endianness}f', value)
    elif type_field == 'f8':
        return struct.pack(f'{endianness}d', value)
    elif type_field == 'str':
        value = str(value)
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        if encoding is None:
            encoding = 'ascii'  # Default encoding if none specified
        encoded_value = str(value).encode(encoding)
        if size:
            if len(encoded_value) > size:
                print("Converted value in the field truncated size", encoded_value)
                return encoded_value[:size]  # Truncate if too long
            else:
                print("Converted value in the field of sometimes padded", encoded_value)
                return encoded_value.ljust(size, b'\x00')  # Pad with null bytes if too short
        else:
            print("Converted value is ", encoded_value)
            return encoded_value
    else:
        return b''

import struct

def unpack_value_from_type(value_bytes, type_field, endianness):
    """
    Unpack the given bytes into a Python value based on the type_field and endianness.
    This is the reverse of convert_value_to_type.
    """
    type_unpack_map = {
        'u1': 'B',
        'u2': 'H',
        'u4': 'I',
        'u8': 'Q',
        's2': 'h',
        's4': 'i',
        's8': 'q',
        'f4': 'f',
        'f8': 'd',
        'b1': 'B',
        'b2': 'B',
        'b4': 'B',
        'b5': 'B',
    }

    if type_field not in type_unpack_map:
        raise ValueError(f"Unsupported type_field '{type_field}' for unpacking.")

    fmt = f'{endianness}{type_unpack_map[type_field]}'
    raw_value = struct.unpack(fmt, value_bytes)[0]

    # Apply masking for bit fields
    if type_field == 'b1':
        return raw_value & 0b1
    elif type_field == 'b2':
        return raw_value & 0b11
    elif type_field == 'b4':
        return raw_value & 0b1111
    elif type_field == 'b5':
        return raw_value & 0b11111

    return raw_value
