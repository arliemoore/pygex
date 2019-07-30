
from state import state

class frag:
    def __init__(self, start_state, out_states):
        #Points to start state for the fragment
        self.start_state = start_state
        
        #List of states that are not yet connected to anything.
        #These are dangling arrows in the NFA fragment
        self.out_states = out_states