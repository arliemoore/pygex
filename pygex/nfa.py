"""
    --- Thompson NFA ---

    Builds an NFA from postfix tokens and searches with it by building
    a DFA lazily, one cached state at a time.
    Based on https://swtch.com/~rsc/regexp/regexp1.html
"""
from .parser import LITERAL, ANY, EMPTY, CONCAT, ALT, STAR, PLUS, QUEST

# State kinds
CHAR = 'CHAR'           # Matches one specific character -> out
WILDCARD = 'WILDCARD'   # Matches any character -> out
SPLIT = 'SPLIT'         # Empty transition to out and out1 (out1 may be None)
MATCH = 'MATCH'         # Pattern has matched

# Most patterns need only a handful of DFA states. The limit stops patterns
# like '(a|b)*a(a|b)(a|b)(a|b)...' from using unbounded memory.
DEFAULT_CACHE_SIZE = 1000


class State:
    """
        state object that represents one step in the NFA and has references
            to one or two other out states.
    """
    __slots__ = ('kind', 'char', 'out', 'out1')

    def __init__(self, kind, char=None, out=None, out1=None):
        self.kind = kind
        self.char = char
        self.out = out
        self.out1 = out1

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

    def __init__(self, postfix, cache_size=DEFAULT_CACHE_SIZE):
        """Build the NFA

        Arguments:
            postfix {list} -- Tokens from parser.to_postfix()

        Keyword Arguments:
            cache_size {int} -- Most DFA states to cache before clearing the
                cache. Must be at least 3.
        """
        if cache_size < 3:
            raise ValueError('cache_size must be at least 3')
        self.cache_size = cache_size
        self.start_state = self._build(postfix)
        self._reset_cache()

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

        The set of NFA states we could be in is tracked as a DFA state,
        and transitions between DFA states are cached as they are
        discovered (a "lazy DFA"). Once the cache is warm, each character
        costs a single dictionary lookup.

        Arguments:
            text {string} -- String to stimulate the NFA with

        Returns:
            Boolean -- True if any substring of text matches the pattern
        """
        d = self._start
        if d.is_match:
            return True
        for char in text:
            nxt = d.next.get(char)
            d = nxt if nxt is not None else self._step(d, char)
            if d.is_match:
                return True
        return False

    def _reset_cache(self):
        """Throw away every cached DFA state and start over"""
        self._cache = {}
        self._start = self._dstate(_closure([self.start_state]))

    def _dstate(self, states):
        """Return the cached DFA state for this set of NFA states, creating it if needed"""
        key = frozenset(states)
        d = self._cache.get(key)
        if d is None:
            d = self._cache[key] = DState(states)
        return d

    def _step(self, d, char):
        """Follow every NFA state in d that accepts char, then start a new
            attempt so the pattern can begin at the next position too.
            The result is cached on d for next time.

        Arguments:
            d {DState} -- DFA state currently in
            char {string} -- Character to stimulate the NFA with

        Returns:
            DState -- DFA state after the step
        """
        outs = [s.out for s in d.states if s.accepts(char)]
        outs.append(self.start_state)
        states = _closure(outs)

        if len(self._cache) >= self.cache_size:
            # Cached states link to each other through their next dicts, so
            # the whole graph has to go. Re-create d in the new cache so this
            # transition is still remembered.
            self._reset_cache()
            d = self._dstate(d.states)

        nxt = self._dstate(states)
        d.next[char] = nxt
        return nxt


class DState:
    """
        One state of the lazy DFA: a set of NFA states the search could be
        in at the same time, plus the transitions found from it so far.
    """
    __slots__ = ('states', 'is_match', 'next')

    def __init__(self, states):
        self.states = states
        self.is_match = any(s.kind == MATCH for s in states)
        #Maps a character to the DState it leads to
        self.next = {}


def _closure(states):
    """Follow empty transitions through SPLIT states

    Uses an explicit stack instead of recursion so that long patterns
    can't hit Python's recursion limit.

    Arguments:
        states {list} -- States to start from (None entries are ignored)

    Returns:
        tuple -- Every non-SPLIT state reachable without reading a character
    """
    result = []
    seen = set()
    pending = list(states)
    while pending:
        s = pending.pop()
        if s is None or s in seen:
            continue
        seen.add(s)
        if s.kind == SPLIT:
            pending.append(s.out1)
            pending.append(s.out)
        else:
            result.append(s)
    return tuple(result)
