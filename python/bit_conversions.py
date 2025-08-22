


def int_to_bitstring(value, length, signed):
    if (value == None):
        print("Can't convert a null value to a bitstring")
        return ""
    
    bitstring = ""

    if (not signed):
        if (value > 2**length - 1):
            print("Value " + str(value) + " out of range for signed length " + str(length))
            return ""
        return pos_int_to_bitstring(value, length)      

    else:
        if (value > 2**(length-1) - 1) or (value < -(2**(length-1))):
            print("Value " + str(value) + " out of range for signed length " + str(length))
            return ""
        
        if (value >= 0):
            return pos_int_to_bitstring(value, length)
        else:
            return neg_int_to_bitstring(value, length)
        


def to_fixed(value, length, frac_bits):
    int_len = length - frac_bits
    int_val = int(value)
    
    frac_val = value - int_val
    frac_quantized = int(frac_val * 2**frac_bits)

    bitstring = int_to_bitstring(int_val, int_len, 0)
    bitstring = bitstring + int_to_bitstring(frac_quantized, frac_bits, 0)
    return str(bitstring)


def from_fixed(bitstring, frac_bits):
    int_len = len(str(bitstring)) - frac_bits
    int_val = bitstring_to_int(bitstring[0:int_len])
    frac_val = bitstring_to_int(bitstring[int_len:])
    frac_val /= 2**frac_bits
    return frac_val + int_val


def pos_int_to_bitstring(value, length):
    bitstring = ""
    while (value != 0):
        bitstring =  str(value % 2) + bitstring
        value = value // 2
        
    while len(bitstring) < length:
        bitstring = "0" + bitstring
    return bitstring

def invert_bitstring(bitstring):
    for ind in range(len(bitstring)):
        if bitstring[ind] == "0":
            bitstring = bitstring[:ind] + "1" + bitstring[ind+1:]
        else:
            bitstring = bitstring[:ind] + "0" + bitstring[ind+1:]
    return bitstring

def add_one(bitstring):
    carry = 1
    for ind in range(len(bitstring)-1, -1, -1):
        if carry == 1 and bitstring[ind] == "1":
            bitstring = bitstring[:ind] + "0" + bitstring[ind+1:]
            carry = 1
        elif carry == 1:
            bitstring = bitstring[:ind] + "1" + bitstring[ind+1:]
            carry = 0
    return bitstring
    

def neg_int_to_bitstring(value, length):
    
    if value == -(2**(length-1)):
        bitstring = ""
        for i in range(length - 1):
            bitstring = bitstring + "0"
        return "1" + bitstring
    bitstring = pos_int_to_bitstring(abs(value), length)
    bitstring = invert_bitstring(bitstring)
    return add_one(bitstring)


def bitstring_to_int(bitstring):
    if len(bitstring) == 0:
        return 0
    
    total = 0
    multiplier = 1
    for i in range(len(bitstring)-1, -1, -1):
        if bitstring[i] == "1":
            total += multiplier
        multiplier *= 2
    return total

