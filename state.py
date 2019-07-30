

class state:
    def __init__(self, char, out, out1):
        # 1. c < 256 ::: Normal -> out
        # 2. c = 256 ::: Split -> out & out1
        # 3. c = 257 ::: Matched
        self.char = char
        self.out = out
        self.out1 = out1
        self.last_list = -1

    def set_out(self, s):
        self.out = s

    def set_out1(self, s):
        self.out1 = s

