"""
    These methods convert a regex to postfix notation

    The conversion uses the shunting-yard algorithm. It was originally
    based on the Java code below, and has since been reworked to use
    explicit tokens instead of overloading characters like '.'.
    https://gist.github.com/gmenard/6161825
"""
from collections import namedtuple

# Operand token kinds
LITERAL = 'LITERAL'     # A single character that must match exactly
ANY = 'ANY'             # '.' which matches any single character
EMPTY = 'EMPTY'         # Matches the empty string, e.g. either side of '|' in '(|a)'

# Operator token kinds
CONCAT = 'CONCAT'       # Implicit concatenation, inserted by the parser
ALT = 'ALT'             # '|'
STAR = 'STAR'           # '*'
PLUS = 'PLUS'           # '+'
QUEST = 'QUEST'         # '?'
LPAREN = 'LPAREN'       # '('
RPAREN = 'RPAREN'       # ')'

QUANTIFIERS = {'*': STAR, '+': PLUS, '?': QUEST}
SYMBOLS = {ALT: '|', STAR: '*', PLUS: '+', QUEST: '?', LPAREN: '(', RPAREN: ')',
           ANY: '.', EMPTY: 'ε', CONCAT: '·'}
METACHARS = set('\\.|*+?()^$[]{}')

# Characters that have a meaning in other regex engines but not in pygex.
# Rejecting them is safer than silently treating them as literals.
UNSUPPORTED = set('^$[]{}')

# Binary operator precedence. Quantifiers bind tighter than both, and
# because they are postfix they go straight to the output.
PRECEDENCE = {ALT: 1, CONCAT: 2}


class PatternError(ValueError):
    """Raised when a regular expression cannot be parsed."""


class Token(namedtuple('Token', 'kind char pos', defaults=(None, None))):
    """A single parsed piece of a regular expression

    Arguments:
        kind {string} -- One of the token kind constants in this module
        char {string} -- The character to match, only set for LITERAL tokens
        pos {int} -- Position in the pattern, used for error messages
    """
    __slots__ = ()

    def __str__(self):
        if self.kind == LITERAL:
            return '\\' + self.char if self.char in METACHARS else self.char
        return SYMBOLS[self.kind]


def tokenize(regex):
    """Split a regular expression into tokens, resolving escapes

    Arguments:
        regex {string} -- Regular expression to tokenize

    Returns:
        list -- Tokens in the same order as the pattern
    """
    tokens = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\':
            if i + 1 == len(regex):
                raise PatternError('pattern ends with an unfinished escape')
            escaped = regex[i + 1]
            # '\d', '\w', etc. are character classes in other engines,
            # so only allow escaping characters that are not alphanumeric
            if escaped.isalnum():
                raise PatternError("escape '\\%s' at position %d is not supported" % (escaped, i))
            tokens.append(Token(LITERAL, escaped, i))
            i += 2
            continue

        if c in QUANTIFIERS:
            tokens.append(Token(QUANTIFIERS[c], pos=i))
        elif c == '|':
            tokens.append(Token(ALT, pos=i))
        elif c == '(':
            tokens.append(Token(LPAREN, pos=i))
        elif c == ')':
            tokens.append(Token(RPAREN, pos=i))
        elif c == '.':
            tokens.append(Token(ANY, pos=i))
        elif c in UNSUPPORTED:
            raise PatternError("'%s' at position %d is not supported; escape it as '\\%s' "
                               "to match it literally" % (c, i, c))
        else:
            tokens.append(Token(LITERAL, c, i))
        i += 1
    return tokens


def insert_operators(tokens):
    """Insert explicit CONCAT and EMPTY tokens and validate the pattern

    A CONCAT goes between any two adjacent operands, e.g. 'ab' -> a CONCAT b.
    An EMPTY goes wherever an operand is missing, e.g. 'a|' or '()'.

    Arguments:
        tokens {list} -- Tokens from tokenize()

    Returns:
        list -- Tokens ready to be converted to postfix
    """
    result = []
    open_parens = []
    # True at the start, and after '(' or '|', where an operand must come next
    expect_operand = True
    prev = None

    for tok in tokens:
        if tok.kind in (LITERAL, ANY, LPAREN):
            if not expect_operand:
                result.append(Token(CONCAT))
            result.append(tok)
            expect_operand = tok.kind == LPAREN
            if tok.kind == LPAREN:
                open_parens.append(tok)
        elif tok.kind in (ALT, RPAREN):
            if expect_operand:
                result.append(Token(EMPTY))
            if tok.kind == RPAREN:
                if not open_parens:
                    raise PatternError("unbalanced ')' at position %d" % tok.pos)
                open_parens.pop()
            result.append(tok)
            expect_operand = tok.kind == ALT
        else:
            #Quantifiers
            if expect_operand:
                raise PatternError("nothing to repeat at position %d" % tok.pos)
            if prev.kind in QUANTIFIERS.values():
                raise PatternError("multiple repeat at position %d" % tok.pos)
            result.append(tok)
        prev = tok

    if expect_operand:
        result.append(Token(EMPTY))
    if open_parens:
        raise PatternError("missing ')' for '(' at position %d" % open_parens[-1].pos)
    return result


def to_postfix(regex):
    """Convert a regular expression from infix to postfix tokens

    Arguments:
        regex {string} -- Regular expression to convert

    Returns:
        list -- Tokens in postfix order, e.g. 'a|bc' -> a b c CONCAT ALT
    """
    output = []
    operators = []

    for tok in insert_operators(tokenize(regex)):
        if tok.kind in (LITERAL, ANY, EMPTY) or tok.kind in QUANTIFIERS.values():
            output.append(tok)
        elif tok.kind == LPAREN:
            operators.append(tok)
        elif tok.kind == RPAREN:
            while operators[-1].kind != LPAREN:
                output.append(operators.pop())
            operators.pop()
        else:
            #Binary operators: CONCAT and ALT
            while operators and operators[-1].kind != LPAREN \
                    and PRECEDENCE[operators[-1].kind] >= PRECEDENCE[tok.kind]:
                output.append(operators.pop())
            operators.append(tok)

    while operators:
        output.append(operators.pop())
    return output


def postfix_string(tokens):
    """Readable form of postfix tokens, useful for debugging

    CONCAT is shown as '·' and EMPTY as 'ε' so they can't be
    confused with the '.' wildcard or a missing character.
    """
    return ''.join(str(tok) for tok in tokens)
