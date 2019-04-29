
class state_list:
    def __init__(self):
        self.n = 0
        self.states = []
    
    def __repr__(self):
        return "s_l[%s %s]" % (self.n, self.states)

    def __str__(self):
        return "s_l[%s %s]" % (self.n, self.states)