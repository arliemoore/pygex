"""
    pygex -- Pattern matcher that uses a Thompson NFA.
"""
from .nfa import NFA
from .parser import PatternError, to_postfix, postfix_string

__all__ = ['Pygex', 'PatternError']


class Pygex:
    """
    Main object to interact with parsing and NFA methods
    """

    def __init__(self, regex):
        """Parse the regex and build its NFA

        Arguments:
            regex {string} -- Regular Expression string to build an nfa from

        Raises:
            PatternError -- If the regex is invalid or uses unsupported syntax
        """
        self.regex = regex
        self.postfix = to_postfix(regex)
        self.nfa = NFA(self.postfix)

    def search(self, text):
        """Check if the pattern matches anywhere in text, like re.search

        Arguments:
            text {string} -- The string to search for the pattern

        Returns:
            boolean --  True if text contains a match for the pattern
        """
        return self.nfa.search(text)

    def postfix_string(self):
        """The parsed pattern in postfix form, for debugging"""
        return postfix_string(self.postfix)

    def __repr__(self):
        return 'Pygex(%r)' % self.regex
