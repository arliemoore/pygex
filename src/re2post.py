from Stack import Stack
from nfa import nfa, p_str

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
                if c1 == '\\' and not escaped:
                    escaped = True
                else:
                    cur = p_str(c1)
                    #Check if character is a special character
                    if cur in SPECIAL_CHARS:
                        cur.set_special_character(True)
                    cur.set_escaped(escaped)
                    self.precedence_stacker(cur)
                    
                    ''' 
                        Concatnation if statement - Only concat if...
                        1. <FILL IN>
                        2. Current character is escaped AND next character is not a special character. 
                    '''
                    if (c1 != '('  and c2 != ')' and c2 not in allOperators and c1 not in binaryOperators) \
                                or (cur.is_escaped() and c2 not in SPECIAL_CHARS):
                        cur = p_str('.')
                        self.precedence_stacker(cur)
                    
                    escaped = False

        #Last character always comes here  
        cur = p_str(regex[len(regex) - 1])
        if escaped:
            cur.set_escaped(True)
        if cur in SPECIAL_CHARS:
            cur.set_special_character(True)
        
        self.precedence_stacker(cur)

    '''
        Convert regular expression from infix to postfix notation using
    '''
    def precedence_stacker(self, char):
        stack = self.char_stack
        thompson_nfa = self.nfa

        #Figure out char character precedence level
        char.set_precedence(self.getPrecedence(char))
        self._log((char.object_string() + ' --- p_stack -> ' + str(stack)))
            
        if char == '(' and not char.is_escaped():
            stack.push(char)
        elif char == ')' and not char.is_escaped():
            while stack.peek() != '(' or (stack.peek() == '(' and stack.peek().is_escaped()):
                thompson_nfa.push(stack.pop())
            stack.pop()
        else:
            while stack.size() > 0:
                peekedChar = stack.peek()
                self._log(("prec check: '" + peekedChar + "'=" + str(peekedChar.get_precedence()) + "  >=  '" + char + "'=" + str(char.get_precedence())))
                if peekedChar.get_precedence() >= char.get_precedence():
                    thompson_nfa.push(stack.pop())
                else:
                    break
            stack.push(char)

    '''
    Complete the NFA
    '''
    def finish_nfa(self):
        stack = self.char_stack
        thompson_nfa = self.nfa
        self._log("finish_nfa")
        #Pop the rest of the characters
        #and push them into the NFA
        while stack.size() > 0:
            thompson_nfa.push(stack.pop())

        #Close the nfa
        thompson_nfa.finish_nfa()
        return thompson_nfa