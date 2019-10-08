import sys  
sys.path.append('src/')

from nfa import nfa, p_str
from re2post import parse

import re, time

class pygex:
    """
    Main object to interact with parsing and NFA methods
    """

    def __init__(self, regex, log=False):
        """initialization
        
        Arguments:
            regex {string} -- Regular Expression string to build an nfa from
        
        Keyword Arguments:
            log {bool} -- False does not log anything to the terminal for debugging
        """
        
        self.regex = regex
        self.log = log
        
        #Get Postfix Expression for the regex
        parser = parse(log)
        parser.parse(regex)
        self.nfa = parser.finish_nfa()
        #self._log(("postfix = " + self.postfix + "\n###\nBuilding NFA\n###"))

    def match(self, str):
        """[summary]
        
        Arguments:
            str {string} -- The string to check if the pattern is contains inside of it
        
        Returns:
            boolean --  True if str contains the pattern used to build the nfa
                        False if str does not contain the pattern
        """
        return self.nfa.match(str)

    def _log(self, str):
        """Logs debugging messages to terminal if logging is True
        
        Arguments:
            str {string} -- String to print to terminal
        """
        if self.log:
            print(str)



