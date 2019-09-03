
from nfa import nfa
import re, time

class pygex:

    def __init__(self, regex, log = False):
        self.regex = regex
        self.nfa = nfa(self.regex, log)

    def match(self, str):
        return self.nfa.match(str) 


if __name__ == '__main__':
    
    regex = '(hello|goodbye)? world'
    str1 = 'hello world'

    t0 = time.time()
    gex = pygex(regex, log=True)
    matched = gex.match(str1)
    total = time.time() - t0
    print((str(matched) + " in " + str(total)))

    t0 = time.time()
    rex = re.compile(regex)
    matched = rex.match(str1)
    total = time.time() - t0
    if matched:
        print(("True in " + str(total)))
    else:
        print(("False in " + str(total)))





    