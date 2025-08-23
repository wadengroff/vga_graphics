

import bit_conversions as bc
import numpy as np
import math


def make_line(start, x_len, y_len):
    x = start[0]
    y = start[1]

    x_end = x + x_len
    y_end = y + y_len

    mag = int(math.sqrt(x_len**2 + y_len**2))
    x_inc = x_len / mag
    y_inc = y_len / mag

    x_coords = np.ones(mag)
    y_coords = np.ones(mag)

    pixel_count = 0
    while (pixel_count < mag):
        x_coords[pixel_count] = int(x)
        y_coords[pixel_count] = int(y)
        x += x_inc
        y += y_inc
        pixel_count += 1
    
    return np.array([x_coords, y_coords])


# WAYS TO MAKE A LINE:
# 1. Get the magnitude and calculate constant increments
#     - works well, but requires much more computation at the start (like magnitude calculation)
# 2. Manually input the increment values and the magnitude
#     - Doesn't look quite as good, but still works
#     - requires computation to determin the necessary inputs to make a certain line
# 3. input the slope and continuously increment the x and y values, determining which is further away and incrementing that

def make_line_quant(start, magnitude, x_inc, y_inc):
    # x_inc/y_inc is a fixed-point, U1.4
    # leaves 5 bits for the magnitude
    # inputs are bitstrings
    x = bc.bitstring_to_int(start[0])
    y = bc.bitstring_to_int(start[1])

    mag = bc.bitstring_to_int(magnitude)
    x_coords = np.ones(mag)
    y_coords = np.ones(mag)

    x_inc_float = bc.from_fixed(x_inc, 4)
    y_inc_float = bc.from_fixed(y_inc, 4)

    pixel_cnt = 0
    while pixel_cnt < mag:
        x_coords[pixel_cnt] = int(x)
        y_coords[pixel_cnt] = int(y)
        x += x_inc_float
        y += y_inc_float
        pixel_cnt += 1

    return np.array([x_coords, y_coords])


# CALCULATE THE SLOPE, THEN DO THE SLOPE INCREMEMENT PROCEDURE CHECKING FOR LENGTH CONDITIONS
def make_line_ideal_compare(start ,x_length, y_length):
    x = bc.bitstring_to_int(start[0])
    y = bc.bitstring_to_int(start[1])


    neg_slope = True if y_length < 0 else False

    if x_length == 0:
        slope = 120
    else:
        slope = bc.from_fixed(bc.to_fixed(y_length/x_length,10,5),5)


    x_max = min(x + x_length, 160)

    if neg_slope:
        y_max = max(y + y_length, 0)
    else:
        y_max = min(y + y_length, 120)

    # Initialize y_ideal to y
    y_ideal = y

    x_coords = []
    y_coords = []


    while x != x_max or y != y_max:
        x_coords.append(int(x))
        y_coords.append(int(y))

        y_ideal_fixed = bc.to_fixed(y_ideal,12,5)
        y_ideal_int = bc.bitstring_to_int(y_ideal_fixed[0:7])
        
        if (y_ideal_int != y):
            y = y+1 if not neg_slope else y-1
        else:
            # The x and y values have reached the next ideal point
            # So now we increment the ideal one by 1 on x axis
            if x != x_max:
                x += 1
            if y != y_max:
                y_ideal += slope

    return np.array([x_coords, y_coords])
        


