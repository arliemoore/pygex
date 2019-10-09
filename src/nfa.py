from Stack import Stack

class nfa:
    """
        --- Thompson NFA ---
        
        Contains the methods to build the NFA and methods
        to search through the NFA for matches.
    """
    
    def __init__(self, log = False):
        self.listId = 0
        self.log = log
        self.fragment_stack = Stack()
        self.head_state = None
    
    def push(self, char):
        """Push a character onto the NFA
        
        Arguments:
            char {p_str} -- Single character that is added to the NFA.
        """
        frag_stack = self.fragment_stack
        self._log("\t\tchar = " + char.object_string())
        escaped = char.is_escaped()
        special = char.is_special_char()
        #Catenation
        if char == '.' and not escaped and not special:
            e2 = frag_stack.pop()
            e1 = frag_stack.pop()
            self._patch(e1.out_states, e2.start_state)
            frag_stack.push(frag(e1.start_state, e2.out_states))
        #Alternation
        elif char == '|' and not escaped:
            e2 = frag_stack.pop()
            e1 = frag_stack.pop()
            s = state('split', e1.start_state, e2.start_state)
            frag_stack.push(frag(s, self._append(e1.out_states, e2.out_states)))
        #Zero or one
        elif char == '?' and not escaped:
            e = frag_stack.pop()
            s = state('split', e.start_state, None)
            frag_stack.push(frag(s, self._append(e.out_states, self._list1(s.set_out1))))
        #Zero or more
        elif char == '*' and not escaped:
            e = frag_stack.pop()
            s = state('split', e.start_state, None)
            self._patch(e.out_states, s)
            frag_stack.push(frag(s, self._list1(s.set_out1)))
        #One or more
        elif char == '+' and not escaped:
            e = frag_stack.pop()
            s = state('split', e.start_state, None)
            self._patch(e.out_states, s)
            frag_stack.push(frag(e.start_state, self._list1(s.set_out1)))
        #Literal characters
        else:
            s = state(char, None, None)
            frag_stack.push(frag(s, self._list1(s.set_out)))
    

    def finish_nfa(self):
        """
            Completes the NFA by patching the remaining fragments as matches
        """
        e = self.fragment_stack.pop()
        self._patch(e.out_states, state('match', None, None))
        self.head_state = e.start_state

    def _list1(self, s):
        """Returns a new list
        
        Arguments:
            s {state} -- either state.set_out() or state.set_out1() function reference
        
        Returns:
            list -- Either an empty list, or a list with a single state function call.
        """
        if s == None:
            return []
        else:
            return [s]

    def _append(self, state_list1, state_list2):
        """Appends two python lists of states together
        
        Arguments:
            state_list1 {list} -- Object with list of states
            state_list2 {list} -- Object with list of states
        
        Returns:
            {list} -- New python list that is a combination of list1 and list2
        """
        return state_list1 + state_list2

    def _patch(self, state_list, s):
        """Takes a list of states and patches its self.out to the state passed in.
        
        Arguments:
            state_list {list} -- list of function calls to a states
                state.set_out() or state.set_out1() function. 
            s {state} -- state object that is set to other states out and out1.
        """
        for st_func in state_list:
            st_func(s)

    #########################
    '''
        End of Building NFA methods

        Start of matching methods
    '''
    #########################

    def match(self, str):
        """Entry method to stimulate the NFA with a string and see
            if it matches the pattern to create the NFA.
        
        Arguments:
            str {string} -- String to stimulate the NFA with
        
        Returns:
            Boolean -- False if the string did not match the pattern
        """
        self._log("###\nStarting Matching\n###")
        clist = state_list()
        nlist = state_list()
        
        for char in str:
            self._log(("match: '" + char + "'"))
            
            '''
                Reset the current list of states to the head state
                because there are no next states to look at.
            '''
            if len(nlist.states) <= 0 or nlist is None:
                self._log('\t\t\t\t\t\t\t\t\tReset clist')
                clist = state_list()
                nlist = state_list()
                clist = self._start_list(self.head_state, clist)
            self._step(clist, char, nlist)
            t = clist
            clist = nlist
            nlist = t
            if self._is_match(clist):
                return True      
        return False
    
    def _step(self, clist, char, nlist):
        """Stimulate the NFA and follow current states to potential
            out states.
        
        Arguments:
            clist {state_list} -- Current states currently in
            char {[type]} -- Character to stimulate the NFA with
            nlist {[type]} -- Next states that the NFA will be in after simulation
        """
        self.listId = self.listId + 1
        nlist.n = 0
        self._log(("\tstep: '" + char + "' clist:" + str(clist) + ' nlist:' + str(nlist)))
        for state in clist.states:
            #Special character '.' that can be anything
            if state.char == '.' and state.char.is_special_char():
                self._add_state(nlist, state.out)
            if state.char == char:
                self._add_state(nlist, state.out)

    def _start_list(self, s, l):
        """Helper method, for creating new state_lists
        
        Arguments:
            s {state} -- state object to put into the empty state_list
            l {state_list} -- Empty state_list object
        
        Returns:
            stae_list -- state_list containing the state passed in
        """
        self.listId = self.listId + 1
        l.n = 0
        self._add_state(l, s)
        return l

    def _add_state(self, l, s):
        """Add the state to the state_list
        
        Arguments:
            s {state} -- state object to put into the state_list
            l {state_list) -- state_list object
        
        Returns:
            stae_list -- state_list containing the state passed in
        """
        self._log(("\t\t\t\tadd_state: '" + str(s) + "' -> " + str(l)))
        if s == None:
            return
        if s.last_list == self.listId:
            return
        s.last_list = self.listId
        if s.char == 'split':
            self._add_state(l, s.out)
            self._add_state(l, s.out1)
            return
        l.states.append(s)

    def _is_match(self, clist):
        """Check if the current states are match states
        
        Arguments:
            clist {state_list} -- state_list of current states
        
        Returns:
            Boolean -- False if none of the current states are a match state
        """
        for state in clist.states:
            if state.char == 'match':
                return True
        return False

    def _log(self, message):
        """Function to log debugging information if set to do so.
        
        Arguments:
            message {string} -- message to log to terminal
        """
        if self.log is True:
            print(message)

    def _print(self, s1, s2, depth):
        if s2 != None and s1 != None:
            if s1 != s2.out:
                self._print(s2, s2.out, depth + 1)
            elif s1 != s2.out1:
                self._print(s2, s2.out1, depth + 1)
        elif s2 != None:
            self._print(s2, s2.out1, depth + 1)


class state:
    """
        state object that represents a character and has references
            to one or two other out states.
    """
    def __init__(self, char, out, out1):
        """initionalization method for a state
        
        Arguments:
            char {p_str} -- custom string which is a single character
                1. char = p_str ::: Normal -> out
                    - Normal State that points to a single out state
                2. char = 'split' -> out & out1
                    - Split State that points to two possible out states
                3. char = 'match'
                    - Matched State
            out {state} -- reference to a state object
            out1 {state} -- reference to another state object
        """
        self.char = char
        self.out = out
        self.out1 = out1
        self.last_list = -1

    def set_out(self, s):
        self.out = s

    def set_out1(self, s):
        self.out1 = s

    def __str__(self):
        return self.char


class frag:
    """
        A fragment of an NFA that has not been completed. It contains a start state
        and some out states.

        Used during building of the NFA, not used during matching.
    """
    def __init__(self, start_state, out_states):
        #Points to start state for the fragment
        self.start_state = start_state
        
        #List of states that are not yet connected to anything.
        #These are dangling arrows in the NFA fragment
        self.out_states = out_states


class state_list:
    """An object with a list of states and an Id number

        This object is only used during matching methods
    """
    def __init__(self):
        self.n = 0
        self.states = []

    def __str__(self):
        if len(self.states) > 0:
            s = '[' + str(self.states[0])
            for i in range(1, len(self.states) - 1):
                s = s + ', ' + str(i)
            s = s + "]"
            return s
        return '[]'


class p_str(str):
    """Custom string class that allows some custom attributes to be set

        Custom Attributes:
            1. precedence: The precedence value associated with a character
            2. escaped: True if the character was escaped with a forward slash
            3. special_char: True if the character is a special character
    
    Arguments:
        str {string} -- Inherites from the string class
    """
    def __init__(self, char):
        super().__init__()
        self.precedence = None
        self.escaped = False
        self.special_char = False

    def set_precedence(self, pres):
        self.precedence = pres

    def get_precedence(self):
        return self.precedence
    
    def set_escaped(self, esc):
        self.escaped = esc
    
    def is_escaped(self):
        return self.escaped

    def set_special_character(self, special_char):
        self.special_char = special_char

    def is_special_char(self):
        return self.special_char

    def object_string(self):
        escaped = 'F'
        special = 'F'
        if self.escaped:
            escaped = 'T'
        if self.special_char:
            special = 'T'

        return ("p_str( '" + super().__str__() + "' : esc='" + escaped + "' : spec='" + special + "' : pres='" + str(self.precedence) + "' )")