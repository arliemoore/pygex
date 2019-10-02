from Stack import Stack

'''
Thompson NFA
'''
class nfa:
    
    def __init__(self, log = False):
        self.listId = 0
        self.log = log
        self.fragment_stack = Stack()
        self.head_state = None
    
    '''
    Generates an NFA and must take in a valid postfix string
    '''
    def push(self, char):
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
        e = self.fragment_stack.pop()
        self._patch(e.out_states, state('match', None, None))
        self.head_state = e.start_state

    def _list1(self, s):
        if s == None:
            return []
        else:
            return [s]
    
    '''
    Appends two state_lists together
    '''
    def _append(self, state_list1, state_list2):
        return state_list1 + state_list2

    '''
    Takes a list of states and patches its self.out to the state passed in. 
    '''
    def _patch(self, state_list, s):
        for st_func in state_list:
            st_func(s)

    '''
        Matching Methods
    '''
    def match(self, str):
        self._log("###\nStarting Matching\n###")
        clist = state_list()
        start = self.head_state
        nlist = state_list()
        clist = self._start_list(start, clist)
        for char in str:
            self._step(clist, char, nlist)
            t = clist
            clist = nlist
            nlist = t
            if self._is_match(clist):
                return True      
        return False
    
    def _start_list(self, s, l):
        self.listId = self.listId + 1
        l.n = 0
        self._add_state(l, s)
        return l

    def _add_state(self, l, s):
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

    def _step(self, clist, char, nlist):
        self.listId = self.listId + 1
        nlist.n = 0
        for state in clist.states:
            #Special character '.' that can be anything
            if state.char == '.' and state.char.is_special_char():
                self._add_state(nlist, state.out)
            if state.char == char:
                self._add_state(nlist, state.out)

    def _is_match(self, clist):
        for state in clist.states:
            if state.char == 'match':
                return True
        return False

    def _log(self, message):
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


'''

'''
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

'''

'''
class frag:
    def __init__(self, start_state, out_states):
        #Points to start state for the fragment
        self.start_state = start_state
        
        #List of states that are not yet connected to anything.
        #These are dangling arrows in the NFA fragment
        self.out_states = out_states

'''

'''
class state_list:
    def __init__(self):
        self.n = 0
        self.states = []


'''
Custom string class that allows precedence values to be set
'''
class p_str(str):
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