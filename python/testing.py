

import bit_conversions as bc
import pixel_operations as po

import matplotlib.pyplot as plt
import numpy as np

# print(bc.to_fixed(7.254, 10, 8))

# print(bc.bitstring_to_int("011001"))

# print(bc.from_fixed(bc.to_fixed(13.52735863, 13, 8), 8))

fig = plt.figure()

# [x, y] = po.make_line(np.array([0,0]), 8, 8)
# plt.scatter(x,y)

# [x, y] = po.make_line(np.array([70, 65]), 20, 4)
# plt.scatter(x,y)

# [x, y] = po.make_line(np.array([150, 0]), 10, 0)
# plt.scatter(x, y)

# [x, y] = po.make_line(np.array([0, 110]), 0, 10)
# plt.scatter(x, y)
# print(bc.to_fixed(0.5,5,4))
# [x, y] = po.make_line_quant(np.array(["0000000", "00000000"]), bc.int_to_bitstring(10,5,0), bc.to_fixed(0.5,5,4), bc.to_fixed(0.5,5,4))
# plt.scatter(x,y)

# [x, y] = po.make_line_quant(np.array(["0000000", "00000000"]), bc.int_to_bitstring(10,5,0), bc.to_fixed(0.8,5,4), bc.to_fixed(1,5,4))
# plt.scatter(x,y)

print("horizontal line")
[x,y] = po.make_line_ideal_compare(np.array([bc.int_to_bitstring(150,8,0), "00"]), 10, 0)
plt.scatter(x,y)

print("Vertical line")
[x,y] = po.make_line_ideal_compare(np.array(["00", bc.int_to_bitstring(110,7,0)]), 0, 10)
plt.scatter(x,y)

print("Other line")
[x,y] = po.make_line_ideal_compare(np.array(["0000", "111111"]), 20,30)
plt.scatter(x,y)

[x,y] = po.make_line_ideal_compare(np.array(["1111", "1111"]), 50, 10)
plt.scatter(x,y)

plt.show()