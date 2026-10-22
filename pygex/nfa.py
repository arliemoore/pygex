"""
    --- Thompson NFA ---

    Builds an NFA from postfix tokens and simulates it to search for
    matches. Based on https://swtch.com/~rsc/regexp/regexp1.html
"""
from .parser import LITERAL, ANY, EMPTY, CONCAT, ALT, STAR, PLUS, QUEST

# State kinds
CHAR = 'CHAR'           # Matches one specific character -> out
WILDCARD = 'WILDCARD'   # Matches any character -> out
SPLIT = 'SPLIT'         # Empty transition to out and out1 (out1 may be None)
MATCH = 'MATCH'         # Pattern has matched


class State:
    """
        state object that represents one step in the NFA and has references
            to one or two other out states.
    """
    __slots__ = ('kind', 'char', 'out', 'out1', 'last_list')

    def __init__(self, kind, char=None, out=None, out1=None):
        self.kind = kind
        self.char = char
        self.out = out
        self.out1 = out1
        # Id of the last state list this state was added to, so a state is
        # never added to the same list twice
        self.last_list = -1

    def set_out(self, s):
        self.out = s

    def set_out1(self, s):
        self.out1 = s

    def accepts(self, char):
        """True if this state consumes char and moves to self.out"""
        return self.kind == WILDCARD or (self.kind == CHAR and self.char == char)

    def __repr__(self):
        if self.kind == CHAR:
            return 'State(%r)' % self.char
        return 'State(%s)' % self.kind


class Fragment:
    """
        A fragment of an NFA that has not been completed. It contains a start state
        and some out states.

        Used during building of the NFA, not used during matching.
    """
    def __init__(self, start_state, out_states):
        #Points to start state for the fragment
        self.start_state = start_state

        #List of state.set_out / state.set_out1 functions that are not yet
        #connected to anything. These are dangling arrows in the NFA fragment
        self.out_states = out_states


def _patch(out_states, s):
    """Connect every dangling arrow in out_states to the state s"""
    for set_out in out_states:
        set_out(s)


class NFA:
    """
        Contains the methods to build the NFA and methods
        to search through the NFA for matches.
    """

    def __init__(self, postfix):
        """Build the NFA

        Arguments:
            postfix {list} -- Tokens from parser.to_postfix()
        """
        self._list_id = 0
        self.start_state = self._build(postfix)

    def _build(self, postfix):
        stack = []
        for tok in postfix:
            if tok.kind == LITERAL:
                s = State(CHAR, tok.char)
                stack.append(Fragment(s, [s.set_out]))
            elif tok.kind == ANY:
                s = State(WILDCARD)
                stack.append(Fragment(s, [s.set_out]))
            elif tok.kind == EMPTY:
                #A split with a single arrow is an empty transition
                s = State(SPLIT)
                stack.append(Fragment(s, [s.set_out]))
            #Catenation
            elif tok.kind == CONCAT:
                e2 = stack.pop()
                e1 = stack.pop()
                _patch(e1.out_states, e2.start_state)
                stack.append(Fragment(e1.start_state, e2.out_states))
            #Alternation
            elif tok.kind == ALT:
                e2 = stack.pop()
                e1 = stack.pop()
                s = State(SPLIT, out=e1.start_state, out1=e2.start_state)
                stack.append(Fragment(s, e1.out_states + e2.out_states))
            #Zero or one
            elif tok.kind == QUEST:
                e = stack.pop()
                s = State(SPLIT, out=e.start_state)
                stack.append(Fragment(s, e.out_states + [s.set_out1]))
            #Zero or more
            elif tok.kind == STAR:
                e = stack.pop()
                s = State(SPLIT, out=e.start_state)
                _patch(e.out_states, s)
                stack.append(Fragment(s, [s.set_out1]))
            #One or more
            elif tok.kind == PLUS:
                e = stack.pop()
                s = State(SPLIT, out=e.start_state)
                _patch(e.out_states, s)
                stack.append(Fragment(e.start_state, [s.set_out1]))
            else:
                raise ValueError('unexpected token in postfix: %r' % (tok,))

        #The parser guarantees a well formed postfix expression
        e = stack.pop()
        assert not stack, 'postfix expression left extra fragments'
        _patch(e.out_states, State(MATCH))
        return e.start_state

    #########################
    '''
        End of Building NFA methods

        Start of matching methods
    '''
    #########################

    def search(self, text):
        """Stimulate the NFA with a string and see if the pattern
            matches anywhere inside it, like re.search.

        Arguments:
            text {string} -- String to stimulate the NFA with

        Returns:
            Boolean -- True if any substring of text matches the pattern
        """
        clist = self._start_list()
        for char in text:
            if self._is_match(clist):
                return True
            clist = self._step(clist, char)
        return self._is_match(clist)

    def _start_list(self):
        self._list_id += 1
        clist = []
        self._add_state(clist, self.start_state)
        return clist

    def _step(self, clist, char):
        """Follow every current state that accepts char, then start a new
            attempt so the pattern can begin at the next position too.

        Arguments:
            clist {list} -- States currently in
            char {string} -- Character to stimulate the NFA with

        Returns:
            list -- States the NFA is in after the step
        """
        self._list_id += 1
        nlist = []
        for s in clist:
            if s.accepts(char):
                self._add_state(nlist, s.out)
        self._add_state(nlist, self.start_state)
        return nlist

    def _add_state(self, states, s):
        """Add s to states, following empty transitions through SPLIT states

        Uses an explicit stack instead of recursion so that long patterns
        can't hit Python's recursion limit.
        """
        pending = [s]
        while pending:
            s = pending.pop()
            if s is None or s.last_list == self._list_id:
                continue
            s.last_list = self._list_id
            if s.kind == SPLIT:
                pending.append(s.out1)
                pending.append(s.out)
            else:
                states.append(s)

    def _is_match(self, clist):
        """Check if any of the current states is the match state"""
        return any(s.kind == MATCH for s in clist)
