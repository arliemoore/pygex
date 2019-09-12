
import sys  
sys.path.append('src/')

from nfa import nfa
from re2post import re2post
import re, time

class pygex:

    def __init__(self, regex, log = False):
        self.regex = regex
        self.log = log
        
        #Get Postfix Expression for the regex
        self.postfix = re2post(self.regex)
        self._log(("postfix = " + self.postfix + "\n###\nBuilding NFA\n###"))

        #Build NFA with postfix
        self.nfa = nfa(self.postfix, log)

    def match(self, str):
        return self.nfa.match(str)


    def _log(self, str):
        if self.log:
            print(str)

    