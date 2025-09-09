import CacheTables as tbls
import pixel_operations as po
import TickStates as ts

import matplotlib.pyplot as plt
import numpy as np



MAX_X = 160
MAX_Y = 120


# SET UP FIGURE
fig = plt.figure()

# Makes a MAX_X x MAX_Y array of colors
pixels = []




# Tick Entity
tickStates = ts.TickStates()

tickStates.writeRectangle(10, 20, 50, 60, 'green')
tickStates.writeRectangle(15, 35, 45, 10, 'red')
tickStates.writeRectangle(55, 35, 45, 10, 'red')
tickStates.writeRectangle(25, 27, 30, 30, 'blue')
tickStates.writeRectangle(15, 24, 27, 10, 'blue')
tickStates.writeRectangle(55, 24, 27, 10, 'blue')
#tickStates.writeRectangle(7, 30, 40, 40, 'green')
#tickStates.writeRectangle(0, 0, 15, 10, 'red')
#tickStates.writeRectangle(0, 10, 20, 20, 'blue')


tickStates.printTables()

# Initialize 4 counters (allows 4 rectangle objects to be in window at a time)
counters = []
for i in range(4):
    counters.append(ts.RectCounter())
cntrExpired = [0] * 4

            


# loop through in VGA protocol style
for y_pos in range(MAX_Y):
    for cntr in counters:
        cntr.reset()

    pixels.append([])

    for x_pos in range(MAX_X):
        # Core clock is at 100MHz, but the VGA clock is at 25MHz
        # So, we need 4 extra clock cycles anyway, using these for identifying starts of rectange shapes
        # only get the valid output data on the fourth cycle
        tickStates.tick(x_pos, y_pos)
        tickStates.tick(x_pos, y_pos)
        tickStates.tick(x_pos, y_pos)
        [found_rect, rect_length, rect_color] = tickStates.tick(x_pos, y_pos)

        for i in range(len(counters)-1, 0, -1):
            cntrExpired[i-1] = not counters[i-1].doCount()
            if cntrExpired[i-1]:
                if (counters[i].isActive()):
                    print("COUNTER " + str(i) + " IS ACTIVE, REPCLAING COUNTER " + str(i-1))
                    
                counters[i-1].shiftIn(counters[i])
                counters[i].reset()

        if x_pos == 0 and y_pos == 1:
            print("0, 2 results in found_rect of " + str(found_rect))

        if (found_rect):
            print("Counter 0 value before=" + counters[0].getColor())
            # Only start the rectangle if not all counters are in use, otherwise throw out
            if (not counters[len(counters)-1].isActive()):
                print("PUTTING COLOR IN")
                for i in range(len(counters)-1, 0, -1):
                    counters[i].shiftIn(counters[i-1])

                counters[0].startRect(rect_length, rect_color)
                print("x: " + str(x_pos) + ", y: " + str(y_pos) + "Color: " + counters[0].getColor())
                print("Moved counter 0 values to counter 1: Color=" + counters[1].getColor())

        # if (x_pos < 80 and y_pos < 80):
        #     print("x: " + str(x_pos) + ", y: " + str(y_pos) + "Color: " + counters[0].getColor())
        pixels[y_pos].append(counters[0].getColor())


# PLOT OUTPUT
x_coords = [x for x in range(MAX_X)] * MAX_Y
y_coords = [0] * MAX_Y * MAX_X
colors = ['black'] * MAX_Y * MAX_X
for y in range(MAX_Y):
    for x in range(MAX_X):
        y_coords[y*MAX_X + x] = y
        colors[y*MAX_X + x] = pixels[y][x]


plt.scatter(x_coords, y_coords, c=colors)
plt.title("Scatter plot of all pixel values")
plt.show()

print(pixels[12][0])

# for y in range(MAX_Y):
#     for x in range(60):
#         if pixels[y][x] == 'black':
#             print("0", end="")
#         elif pixels[y][x] == 'red':
#             print("1", end="")
#         elif pixels[y][x] == 'green':
#             print("$", end="")
#         elif pixels[y][x] == 'blue':
#             print("&", end="")
#     print("")


