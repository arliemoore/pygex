from Stack import Stack

'''
    These methods convert a regex to postfix notation

    Original Java code can be found below. This is a remake
    of the code in Python. 
    https://gist.github.com/gmenard/6161825

'''

''' Operators precedence map '''
precedenceMap = {
    '(':1,
    '|':2,
    '.':3,
    '?':4,
    '*':4,
    '+':4,
    '^':5,
}

'''
    Get character precedences
'''
def getPrecedence(char):
    try:
        precedence = precedenceMap[char]
    except KeyError:
        precedence = 6
    return precedence

'''
    Transform regular expression by inserting 
    a '.' as explicit concatenation
'''
def formatRegEx(regex):
    res = ''
    allOperators = ['|', '?', '+', '*', '^']
    binaryOperators = ['^', '|']

    for i in range(0, len(regex)):
        c1 = regex[i]
        if i + 1 < len(regex):
            c2 = regex[i+1]
            res = res + c1
            if(c1 != '(' and c2 != ')' and c2 not in allOperators and c1 not in binaryOperators):
                res = res + '.'
         
    res = res + regex[len(regex) - 1]

    return res

'''
    Convert regular expression from infix to postfix notation using
'''
def re2post(regex):
    postfix = ''

    stack = Stack()
    formattedRegex = formatRegEx(regex)

    for char in formattedRegex:
        if char == '(':
            stack.push(char)
            continue
        elif char == ')':
            while (stack.peek() != '('):
                postfix = postfix + stack.pop()
            stack.pop()
            continue
        else:
            while stack.size() > 0:
                peekedChar = stack.peek()

                peekedCharPrecedence = getPrecedence(peekedChar)
                currentCharPrecedence = getPrecedence(char)

                if peekedCharPrecedence >= currentCharPrecedence:
                    postfix = postfix + stack.pop()
                else:
                    break
            
            stack.push(char)
            continue

    while stack.size() > 0:
        postfix = postfix + stack.pop()
    
    return postfix


