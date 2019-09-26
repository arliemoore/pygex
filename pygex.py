
import sys  
sys.path.append('src/')

from nfa import nfa, p_str
from Stack import Stack
import re, time

class pygex:

    def __init__(self, regex, log=False):
        self.regex = regex
        self.log = log
        
        #Get Postfix Expression for the regex
        parser = parse(log)
        parser.parse(regex)
        self.nfa = parser.finish_nfa()
        #self._log(("postfix = " + self.postfix + "\n###\nBuilding NFA\n###"))

    def match(self, str):
        return self.nfa.match(str)

    def _log(self, str):
        if self.log:
            print(str)




'''
    These methods convert a regex to postfix notation

    Original Java code can be found below. This is a remake
    of the code in Python. 
    https://gist.github.com/gmenard/6161825

'''
class parse():
    
    def __init__(self, log=False):
        ''' Operators precedence map '''
        self.precedenceMap = {
            '(':1,
            '|':2,
            '.':3,
            '?':4,
            '*':4,
            '+':4,
            '^':5,
        }
        self.char_stack = Stack()
        self.log = log
        self.nfa = nfa(log)

    def _log(self, str):
        if self.log:
            print(str)
    '''
        Get character precedences
    '''
    def getPrecedence(self, char):
        
        #If the character is escaped, then its a literal
        if char.is_escaped():
            return 6
        if char.is_special_char():
            if char == '.':
                self._log((char + ' is special char'))
                return 6
        try:
            precedence = self.precedenceMap[char]
        except KeyError:
            precedence = 6
        
        return precedence

    '''
        Transform regular expression by inserting 
        a '.' as explicit concatenation
    '''
    def parse(self, regex):
        # Special Characters from online for Regex
        # [ '-' , '[' , ']' , '{' , '}' , '(' , ')' , '*' , '+' , '?' , '.' , ',' , '\' , '/' , '^' , '$' , '|' , '#'  ]
        #
        SPECIAL_CHARS = [ '-' , '[' , ']' , '{' , '}' , '(' , ')' , '*' , '+' , '?' , '.' , ',' , '\\' , '/' , '^' , '$' , '|' , '#'  ]

        allOperators = ['|', '?', '+', '*']         #Removed to have '^' in allOperators
        binaryOperators = ['^', '|']
        escaped = False

        for i in range(0, len(regex)):
            #Current character
            c1 = regex[i]
            if i + 1 < len(regex):
                #Next Character
                c2 = regex[i+1]
                
                #Escapes Special Character
                if c1 == '\\' and c2 in SPECIAL_CHARS:
                    escaped = True
                elif escaped and c1 in SPECIAL_CHARS:
                    next = p_str(c1)
                    next.set_escaped(True)
                    self.precedence_stacker(next)
                    escaped = False
                    if(c2 not in allOperators and c1 not in binaryOperators):
                        next = p_str('.')
                        self.precedence_stacker(next)
                #Character is not escaped
                else:
                    next = p_str(c1)
                    #Check if character is a special character
                    if next in SPECIAL_CHARS:
                        next.set_special_character(True)
                    self.precedence_stacker(next)
                    #Concatnation of two literals
                    if(c1 != '(' and c2 != ')' and c2 not in allOperators and c1 not in binaryOperators):
                        next = p_str('.')
                        self.precedence_stacker(next)

        #Last character always comes here  
        next = p_str(regex[len(regex) - 1])
        if escaped:
            next.set_escaped(True)
        self.precedence_stacker(next)

    '''
        Convert regular expression from infix to postfix notation using
    '''
    def precedence_stacker(self, next):
        stack = self.char_stack
        thompson_nfa = self.nfa

        self._log((next + '    --- p_stack -> ' + str(stack)))
        #Figure out next character precedence level
        next.set_precedence(self.getPrecedence(next))
            
        if next == '(' and not next.is_escaped():
            stack.push(next)
        elif next == ')' and not next.is_escaped():
            while (stack.peek() != '(' and not stack.peek().is_escaped()):
                thompson_nfa.push(stack.pop())
            stack.pop()
        else:
            while stack.size() > 0:
                peekedChar = stack.peek()

                #Old Implementation
                #peekedCharPrecedence = self.getPrecedence(peekedChar)
                #currentCharPrecedence = self.getPrecedence(next)
                self._log(("prec check: '" + peekedChar + "'=" + str(peekedChar.get_precedence()) + "  >=  '" + next + "'=" + str(next.get_precedence())))
                if peekedChar.get_precedence() >= next.get_precedence():
                    thompson_nfa.push(stack.pop())
                else:
                    break
            stack.push(next)

    '''
    Complete the NFA
    '''
    def finish_nfa(self):
        stack = self.char_stack
        thompson_nfa = self.nfa
        
        #Pop the rest of the characters
        #and push them into the NFA
        while stack.size() > 0:
            thompson_nfa.push(stack.pop())

        #Close the nfa
        thompson_nfa.finish_nfa()
        return thompson_nfa
