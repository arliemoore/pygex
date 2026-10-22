import random
import re
import unittest

from pygex import Pygex, PatternError

'''Test Cases

    Each entry is (regex, string, expected). Every case is also checked
    against Python's re.search so the expected values can't drift from
    real regex behaviour.
'''

MATCH_CASES = [
    # Literal characters and concatenation
    ('hello', 'hello', True),
    ('hello', 'world hello    ', True),
    ('hello', 'hello world', True),
    ('hello', 'hhello', True),
    ('hello', '!hello', True),
    ('hello', ',hello', True),
    ('hello', '#hello', True),
    ('hello', ' hello', True),
    ('hello', 'O hello this is a long sentence', True),
    ('hello', 'goodbye', False),
    ('hello', 'ello', False),
    ('hello', 'gello', False),
    ('hello', 'hell', False),
    ('hello', '', False),
    ('ab', 'aab', True),
    ('abc', 'ababc', True),
    ('abc', 'abab', False),

    # Single characters
    ('h', 'h', True),
    ('h', ' h', True),
    ('h', '!h', True),
    ('h', 'x', False),
    ('h', '', False),

    # Alternation
    ('hello|world', 'hello', True),
    ('hello|world', 'world', True),
    ('hello|world', 'one hello', True),
    ('hello|world', 'help', False),
    ('ab|cd', 'xcd', True),
    ('ab|cd', 'ac', False),
    ('(a|b)c', 'bc', True),
    ('(a|b)c', 'xbc', True),
    ('(a|b)c', 'cc', False),

    # Nested groups
    ('(a|b(c|(d|e)))', 'a', True),
    ('(a|b(c|(d|e)))', 'bd', True),
    ('(a|b(c|(d|e)))', 'be', True),
    ('(a|b(c|(d|e)))', 'bf', False),
    ('(((a|b)|c)d|e)', 'ad', True),
    ('(((a|b)|c)d|e)', 'cd', True),
    ('(((a|b)|c)d|e)', 'e', True),
    ('(((a|b)|c)d|e)', 'dcb', False),

    # Zero or one
    ('(hello|goodbye)? world', 'hello world', True),
    ('(hello|goodbye)? world', ' world', True),
    ('(hello|goodbye)? world', 'goodbye world', True),
    ('(hello|goodbye)? world', 'world', False),
    ('colou?r', 'color', True),
    ('colou?r', 'colour', True),
    ('colou?r', 'colouur', False),
    ('a?', 'b', True),
    ('a?', '', True),

    # Zero or more
    ('(hello|bye)*', 'hellohellohellobye', True),
    ('(hello|bye)*', '', True),
    ('a*b', 'b', True),
    ('a*b', 'aaab', True),
    ('xa*y', 'xy', True),
    ('xa*y', 'xaaay', True),
    ('xa*y', 'xaaby', False),

    # One or more
    ('a+', 'aaa', True),
    ('a+', '', False),
    ('a+b', 'aab', True),
    ('xa+y', 'xy', False),
    ('xa+y', 'xay', True),
    ('(ab)+c', 'ababc', True),
    ('(ab)+c', 'ac', False),

    # Any character
    ('.', 'x', True),
    ('.', '', False),
    ('.*', '', True),
    ('.*', '!@#$%^&*()', True),
    ('a.b', 'axb', True),
    ('a.b', 'a.b', True),
    ('a.b', 'ab', False),
    ('.b', 'xb', True),
    ('a.', 'ax', True),
    ('a.', 'a', False),

    # Escaped special characters
    ('(aa\\(\\)|\\|hello)', 'aa()', True),
    ('(aa\\(\\)|\\|hello)', '|hello', True),
    ('(aa\\(\\)|\\|hello)', 'hello', False),
    ('aa(\\()', 'aa(', True),
    ('a(\\))', 'a)', True),
    ('a(\\()', 'a(', True),
    ('a\\.b', 'a.b', True),
    ('a\\.b', 'axb', False),
    ('\\.', 'x', False),
    ('a\\*', 'a*', True),
    ('a\\*', 'aaa', False),
    ('\\\\', 'a\\b', True),
    ('\\^\\$', '^$', True),

    # Empty patterns and empty alternatives
    ('', '', True),
    ('', 'abc', True),
    ('()', 'abc', True),
    ('a|', 'b', True),
    ('(|a)b', 'b', True),
    ('(|a)b', 'ab', True),
    ('x(|a)y', 'xy', True),
    ('x(|a)y', 'xay', True),
    ('x(|a)y', 'xby', False),
    ('()*', '', True),
    ('(a*)*', 'b', True),
    ('(a*)+b', 'aab', True),
]

INVALID_PATTERNS = [
    '(',
    '(ab',
    ')',
    'a)',
    '(a))',
    '*',
    'a**',
    'a+?',
    '(*a)',
    'a|*',
    '\\',
    'a\\',
    '\\d',
    '^a',
    'a$',
    '[ab]',
    'a{2}',
]

POSTFIX_CASES = [
    ('ab', 'ab·'),
    ('a|bc', 'abc·|'),
    ('(a|b)c', 'ab|c·'),
    ('ab*', 'ab*·'),
    ('(ab)+', 'ab·+'),
    ('a.b', 'a.·b·'),
    ('a\\.b', 'a\\.·b·'),
    ('a|', 'aε|'),
    ('', 'ε'),
]


def random_regex(rng, depth):
    """Build a random pattern that both pygex and re can compile"""
    r = rng.random()
    if depth <= 0 or r < 0.3:
        expr = rng.choice(['a', 'b', 'c', '.', '\\.', '\\*', '\\('])
    elif r < 0.5:
        return random_regex(rng, depth - 1) + random_regex(rng, depth - 1)
    elif r < 0.7:
        left = '' if rng.random() < 0.1 else random_regex(rng, depth - 1)
        right = '' if rng.random() < 0.1 else random_regex(rng, depth - 1)
        return left + '|' + right
    else:
        expr = '(' + random_regex(rng, depth - 1) + ')'
    # Only quantify a single atom or group, so we never build 'a**'
    if rng.random() < 0.35:
        expr += rng.choice('*+?')
    return expr


def random_text(rng):
    return ''.join(rng.choice('abc.*(') for _ in range(rng.randint(0, 8)))


class pygex_tests(unittest.TestCase):

    def test_match_cases(self):
        for regex, text, expected in MATCH_CASES:
            with self.subTest(regex=regex, text=text):
                self.assertEqual(Pygex(regex).search(text), expected)

    def test_match_cases_agree_with_re(self):
        for regex, text, expected in MATCH_CASES:
            with self.subTest(regex=regex, text=text):
                self.assertEqual(bool(re.search(regex, text)), expected)

    def test_invalid_patterns_raise(self):
        for regex in INVALID_PATTERNS:
            with self.subTest(regex=regex):
                with self.assertRaises(PatternError):
                    Pygex(regex)

    def test_pattern_error_is_value_error(self):
        with self.assertRaises(ValueError):
            Pygex('(')

    def test_postfix(self):
        for regex, expected in POSTFIX_CASES:
            with self.subTest(regex=regex):
                self.assertEqual(Pygex(regex).postfix_string(), expected)

    def test_reuse_compiled_pattern(self):
        gex = Pygex('a.c')
        self.assertTrue(gex.search('abc'))
        self.assertFalse(gex.search('ab'))
        self.assertTrue(gex.search('xxaxc'))
        self.assertFalse(gex.search(''))

    def test_long_pattern_and_text(self):
        # Would hit the recursion limit if states were added recursively
        alternatives = '|'.join('x' * 3 + chr(c) for c in range(0x100, 0x100 + 3000))
        gex = Pygex(alternatives)
        self.assertTrue(gex.search('aaxxx' + chr(0x100 + 2999)))
        self.assertFalse(gex.search('xx' + chr(0x100)))

    def test_no_exponential_blowup(self):
        # Classic pathological case for backtracking engines: (a?){n}a{n}
        n = 30
        gex = Pygex('a?' * n + 'a' * n)
        self.assertTrue(gex.search('a' * n))
        self.assertFalse(gex.search('a' * (n - 1)))

    def test_random_patterns_agree_with_re(self):
        rng = random.Random(1234)
        for _ in range(500):
            regex = random_regex(rng, 4)
            gex = Pygex(regex)
            for _ in range(20):
                text = random_text(rng)
                with self.subTest(regex=regex, text=text):
                    self.assertEqual(gex.search(text), bool(re.search(regex, text)))


if __name__ == '__main__':
    unittest.main()
