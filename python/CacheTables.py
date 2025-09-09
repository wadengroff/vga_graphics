


class PixelTableEntry:

    def __init__(self, ENTRY_LENGTH):
        self.numEntries = ENTRY_LENGTH
        # initialize with everything set to 0
        self.lows = [0] * ENTRY_LENGTH
        self.valids = [0] * ENTRY_LENGTH
        self.ret_addrs = [0] * ENTRY_LENGTH

    def writeEntry(self, low, ret_addr):
        foundEntry = 0
        for i in range(self.numEntries):
            if self.valids[i] == 0:
                foundEntry = 1
                self.lows[i] = low
                self.valids[i] = 1
                self.ret_addrs[i] = ret_addr
                break

        if not foundEntry:
            self.lows[0] = low
            self. valids[0] = 1
            self.ret_addrs[0] = ret_addr

    def readEntry(self):
        return [self.lows, self.valids, self.ret_addrs]



# Table storing Rectange Entry address corresponding to x positions
class PixelTable:

    def __init__(self, TABLE_LENGTH, ENTRY_LENGTH):
        self.tableLength = TABLE_LENGTH
        self.entryLength = ENTRY_LENGTH

        self.pixelTable = []

        for i in range(TABLE_LENGTH):
            self.pixelTable.append(PixelTableEntry(ENTRY_LENGTH))


    def writeEntry(self, x_high, x_low, ret_addr):
        self.pixelTable[x_high].writeEntry(x_low, ret_addr)

    def readEntry(self, x_high):
        return self.pixelTable[x_high].readEntry()

#################################################################################

class RectTableEntry:

    def __init__(self, ENTRY_LENGTH):
        self.ENTRY_LENGTH = ENTRY_LENGTH
        self.y_mins = [0] * ENTRY_LENGTH
        self.y_maxs = [0] * ENTRY_LENGTH
        self.x_lens = [0] * ENTRY_LENGTH
        self.valids = [0] * ENTRY_LENGTH # still need valid bits if we are allowing for more than one y entry
        self.colors = ['black'] * ENTRY_LENGTH
        
    def writeEntry(self, y_min, y_max, x_len, color):
        foundEntry = 0
        for i in range(self.ENTRY_LENGTH):
            if self.valids[i] == 0:
                foundEntry = 1
                self.valids[i] = 1
                self.y_mins[i] = y_min
                self.y_maxs[i] = y_max
                self.x_lens[i] = x_len
                self.colors[i] = color
                break

        # if didn't find, overwrite 0th entry
        if not foundEntry:
            self.valids[0] = 1
            self.y_mins[0] = y_min
            self.y_maxs[0] = y_max
            self.x_lens[0] = x_len
            self.colors[0] = color

    def readEntry(self):
        return [self.y_mins, self.y_maxs, self.valids, self.x_lens, self.colors]


# Rectangle Entry Table
class RectTable:

    def __init__(self, TABLE_LENGTH, ENTRY_LENGTH):
        self.tableLength = TABLE_LENGTH
        self.entryLength = ENTRY_LENGTH

        self.rectTable = []
        for i in range(TABLE_LENGTH):
            self.rectTable.append(RectTableEntry(ENTRY_LENGTH))

    def writeEntry(self, ret_addr, y_min, y_max, x_len, color):
        self.rectTable[ret_addr].writeEntry(y_min, y_max, x_len, color)

    def readEntry(self, ret_addr):
        return self.rectTable[ret_addr].readEntry()


