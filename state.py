

class state:
    def __init__(self, char, out, out1):
        # 1. c < 256 ::: Normal -> out
        #   - Normal State that points to a single out state
        # 2. c = 256 ::: Split -> out & out1
        #   - Split State that points to two possible out states
        # 3. c = 257 ::: Matched
        #   - Matched State
        self.char = char
        self.out = out
        self.out1 = out1
        self.last_list = -1

    def set_out(self, s):
        self.out = s

    def set_out1(self, s):
        self.out1 = s

