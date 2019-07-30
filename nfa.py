from state import state
from frag import frag
from re2post import re2post
from state_list import state_list
from Stack import Stack

class nfa:
    
    def __init__(self, regex, log = False):
        self.listId = 0
        self.log = log
        
        #Get postfix 
        postfix = re2post(regex)
        
        #Create nfa
        self.head_state = self._gen_nfa(postfix)
    
    '''
    Generates an NFA and must take in a valid postfix string
    '''
    def _gen_nfa(self, postfix):
        frag_stack = Stack()
        split = 'split'
        match = 'match'

        for char in postfix:
            self._log("char = " + char)
            if char == '.':
                e2 = frag_stack.pop()
                e1 = frag_stack.pop()
                self._patch(e1.out_states, e2.start_state)
                frag_stack.push(frag(e1.start_state, e2.out_states))
            elif char == '|':
                e2 = frag_stack.pop()
                e1 = frag_stack.pop()
                s = state(split, e1.start_state, e2.start_state)
                frag_stack.push(frag(s, self._append(e1.out_states, e2.out_states)))
            elif char == '?':
                e = frag_stack.pop()
                s = state(split, e.start_state, None)
                frag_stack.push(frag(s, self._append(e.out_states, self._list1(s.set_out1))))
            elif char == '*':
                e = frag_stack.pop()
                s = state(split, e.start_state, None)
                self._patch(e.out_states, s)
                frag_stack.push(frag(s, self._list1(s.set_out1)))
            elif char == '+':
                e = frag_stack.pop()
                s = state(split, e.start_state, None)
                self._patch(e.out_states, s)
                frag_stack.push(frag(e.start_state, self._list1(s.set_out1)))
            else:
                s = state(char, None, None)
                frag_stack.push(frag(s, self._list1(s.set_out)))
        e = frag_stack.pop()
        self._patch(e.out_states, state(match, None, None))
        return e.start_state

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
        return self._is_match(clist)
    
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