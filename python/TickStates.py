import bit_conversions as bc
import CacheTables as ct


class TickStates:

    MPT_TABLE_LENGTH = 32
    MPT_ENTRY_LENGTH = 4

    RET_TABLE_LENGTH = 32
    RET_ENTRY_LENGTH = 4


    def __init__(self):
        self.state = 0
        self.mpt_lows   = [0] * TickStates.MPT_ENTRY_LENGTH
        self.mpt_valids = [0] * TickStates.MPT_ENTRY_LENGTH
        self.ret_addrs  = [0] * TickStates.MPT_ENTRY_LENGTH
        self.y_mins     = [0] * TickStates.RET_ENTRY_LENGTH
        self.y_maxs     = [0] * TickStates.RET_ENTRY_LENGTH
        self.ret_valids = [0] * TickStates.RET_ENTRY_LENGTH
        self.rect_length = 0
        self.rect_color = 'black'
        self.x_lens     = [0] * TickStates.RET_ENTRY_LENGTH
        self.colors     = ['black'] * TickStates.RET_ENTRY_LENGTH

        self.next_ret_addr = 0

        self.mpt = ct.PixelTable(TickStates.MPT_TABLE_LENGTH, TickStates.MPT_ENTRY_LENGTH)
        self.ret = ct.RectTable(TickStates.RET_TABLE_LENGTH, TickStates.RET_ENTRY_LENGTH)


    def writeRectangle(self, xpos, ymin, ymax, xlength, color):
        # Let there be 160 x pixels and 120 y pixels
        # => 8b x position, 7b y position
        # upper 5 bits of x are the table index, lower 3 bits for indexing
        x_bin = bc.int_to_bitstring(xpos, 8, 0)
        x_high = bc.bitstring_to_int(x_bin[0:5])
        x_low = bc.bitstring_to_int(x_bin[5:])

        print("INPUT X OF " + str(xpos) + " results in high of " + str(x_high) + " and low of " + str(x_low))

        [lows, valids, ret_addrs] = self.mpt.readEntry(x_high)
        
        
        for i in range(len(valids)):
            if valids[i] == 1 and lows[i] == x_low:
                # ALREADY A RECTANGLE FOR THIS X POSITION
                print("WRITE ENTRY ONCE")
                self.ret.writeEntry(ret_addrs[i], ymin, ymax, xlength, color)
                return 1
            elif valids[i] == 0:
                print("WRITE ENTRY " + str(x_high) + " " + str(x_low))
                self.ret.writeEntry(self.next_ret_addr, ymin, ymax, xlength, color)
                self.mpt.writeEntry(x_high, x_low, self.next_ret_addr)
                self.next_ret_addr += 1
                return 1
        return 0

    def tick(self, x_pos, y_pos):
        # State |  Meaning
        #  0    |  x_pos and y_pos have just changed, and the Match Pixel Table(MPT) is being accessed
        #  1    |  The MPT has been accessed and the x_low comparison generates address for Rectangle Entry Table (RET)
        #  2    |  RET table has been accessed, and comparisons are done on the y limits
        #  3    |  Rectangle has either been found or not found

        # extract x high bits
        # extract x low bits
        x_bin = bc.int_to_bitstring(x_pos, 8, 0)
        x_high = bc.bitstring_to_int(x_bin[0:5])
        x_low = bc.bitstring_to_int(x_bin[5:])

        if self.state == 0:
            # Need to access the MPT
            [self.mpt_lows, self.mpt_valids, self.ret_addrs] = self.mpt.readEntry(x_high)
            self.state = 1 
            self.found_rect = 0

        elif self.state == 1:
            ret_addr = -1
            # loop through the MPT entry values
            for i in range(TickStates.MPT_ENTRY_LENGTH):
                if (self.mpt_valids[i] == 0):
                    break
                elif (self.mpt_lows[i] == x_low):
                    ret_addr = self.ret_addrs[i]
            
            # if we didn't match with an x position, go to state 3 immediately
            if ret_addr == -1:
                self.state = 4 #buffer state
            else:
                [self.y_mins, self.y_maxs, self.ret_valids, self.x_lens, self.colors] = self.ret.readEntry(ret_addr)
                self.state = 2

        elif self.state == 2:
            for i in range(TickStates.RET_ENTRY_LENGTH - 1, -1, -1):
                if (self.ret_valids[i] and y_pos >= self.y_mins[i] and y_pos <= self.y_maxs[i]):
                    self.rect_length = self.x_lens[i]
                    self.found_rect = 1
                    self.rect_color = self.colors[i]
            self.state = 3
        elif self.state == 3:
            
            # ONLY POSSIBLY RETURN VALID RECTANGLE IN STATE 3
            self.state = 0
            return [self.found_rect, self.rect_length, self.rect_color]
        elif self.state == 4:
            # Extra Buffer State
            self.state = 3

        # return invalid rectangle stuff
        return [0, 0, 'black']

    def printTables(self):
        print("Match Pixel Table:")
        print("Upper X bits ||| x_low 0 | ret_addr 0 || x_low 1 | ret_addr 1 || x_low 2 | ret_addr 2 || x_low 3 | ret_addr 3")
        print("-------------------------------------------------------------------------------------------------------------")
        for i in range(TickStates.MPT_TABLE_LENGTH):
            [lows, valids, ret_addrs] = self.mpt.readEntry(i)
            print(str(i) + "          ||| ", end="")
            for i in range (TickStates.MPT_ENTRY_LENGTH):
                print(str(lows[i]) + "       | " + str(ret_addrs[i]) + "          || ", end = "")
            print("")
        print("\n\n")

        print("Rect Entry Table:")
        print("Addr |||  | y_min0 || y_max0 | x_len  | color || more")
        print("-------------------------------------------------------------------------------------------------------------")
        for i in range(TickStates.RET_TABLE_LENGTH):
            [y_mins, y_maxs, valids, x_lens, colors] = self.ret.readEntry(i)
            print(str(i) + "          ||| ", end="")
            for i in range (TickStates.MPT_ENTRY_LENGTH):
                print(str(y_mins[i]) + "    | " + str(y_maxs[i]) + "  | " + str(x_lens[i]) + "    | " + str(colors[i]) + "    || ", end = "")
            print("")

        



                
class RectCounter:

    def __init__(self):
        self.count = 0
        self.active = 0
        self.color = 'black'

    def reset(self):
        self.count = 0
        self.active = 0
        self.color = 'black'

    def isActive(self):
        return self.active

    def startRect(self, count, color):
        self.count = count
        self.active = 1
        self.color = color

    def getColor(self):
        return self.color

    def shiftIn(self, rectCounter):
        if (rectCounter.active):
            print("SHIFTED IN ACTIVE COUNTER")
        self.count = rectCounter.count
        self.active = rectCounter.active
        self.color = rectCounter.color
        if self.active:
            print("Count=" + str(self.count) + ", color=" + self.color)

    def doCount(self):
        if self.active:
            self.count = self.count - 1
            self.active = (self.count >= 0)
        
        return self.active