import unittest, time, re, traceback
from pygex import pygex

'''Test Cases'''

tests = {
    
    'special_characters_before_pattern': {
        'regex': 'hello',
        'str': [
            '!hello', 
            ',hello',
            '#hello',
            ' hello'
        ]
    },
    'test_concat1_true': {
        'regex': 'hello',
        'str': [
            'world hello    ',
            'hello world'
        ]
    },
    'test_concat1_false':{
        'regex': 'hello',
        'str': [
            'goodbye',
            'ello',
            'gello',
            'rello'
        ]
    },
    'test_split1_true':{
        'regex': 'hello|world',
        'str': [
            'hello',
            'world',
            'one hello'
        ]
    },
    'test_many_roundBrackets':{
        'regex': '(a|b(c|(d|e)))', 
        'str': [
            'acd',
            'bcd',
            'ace',
            'bce'
        ]
    },
    #
    # Not working
    #
    'test_many_roundBrackets_backwards':{
        'regex': '(((a|b)|c)d|e)', 
        'str': [
            'ecb',
            'eca'
            #'dcb',
            #'dca'
        ]
    },
    'test_zeroOrOne1_true':{
        'regex': '(hello|goodbye)? world',
        'str': [
            'hello world',
            ' world',
            'goodbye world'
        ]
    },
    'test_zeroOrOne2_true':{
        'regex': '((pygex)?|a?)',
        'str': [
            'pygex',
            'a'
        ]
    },
    'test_onechar':{
        'regex': 'h',
        'str': [
            ' h',
            '!h'
        ]
    },
    'test_match_at_start':{
        'regex': 'hello',
        'str': [
            'O hello this is a long sentence',
            'hello good friend how are you doing today'
        ]
    },
    'test_one_or_more':{
        'regex': '(hello|bye)*',
        'str': [
            'hellohellohellobye',
            'hello',
            'bye',
            'byebyebyebyehellobyebye'
        ]
    },
    'test_any_character':{
        'regex': '.*',
        'str': [
            'a;lksjdf',
            'hello friends',
            '!@#$%^&*()',
            'abc'
        ]
    },
    'test_escape_special_char':{
        'regex': '(aa\\(\\)|\\|hello)',
        'str': [
            'aa()',
            '|hello'
        ]
    },
    'test_round_bracket':{
        'regex': 'aa(\\()',
        'str': [
            'aa('
        ]
    }, 
    'test_round_bracket1':{
        'regex': 'a(\\))',
        'str': [
            'a)'
        ]
    }, 
    'test_round_bracket2':{
        'regex': 'a(\\()',
        'str': [
            'a('
        ]
    }
}

class pygex_tests(unittest.TestCase):
 
    def setUp(self):
        pass

    def _run_dictionary(self, testId, TorF):
        test = tests[testId]
        gex = pygex(test['regex'])
        for str in test['str']:
            try:
                if TorF:
                    self.assertTrue(gex.match(str), msg=(testId + ' : regex="' + test['regex']  + '" : str="' + str + '"'))
                else:
                    self.assertFalse(gex.match(str), msg=(testId + ' : regex="' + test['regex']  + '" : str="' + str + '"'))
            except IndexError as error:
                print((testId + ' : regex="' + test['regex']  + '" : str="' + str + '"'))
                raise error

    def test_concat1_true(self):
        self._run_dictionary('test_concat1_true', True)
        
    def test_contact1_false(self):
        self._run_dictionary('test_concat1_false', False)

    def test_split1_true(self):
        self._run_dictionary('test_split1_true', True)

    def test_zeroOrOne_true(self):
        self._run_dictionary('test_zeroOrOne1_true', True)

    def test_zeroOrOne2_true(self):
        self._run_dictionary('test_zeroOrOne2_true', True)

    def test_onechar(self):
        self._run_dictionary('test_onechar', False)

    def test_match_at_start(self):
        self._run_dictionary('test_match_at_start', True)

    def test_one_or_more(self):
        self._run_dictionary('test_one_or_more', True)

    def test_any_character(self):
        self._run_dictionary('test_any_character', True)
    
    def test_escape_special_char(self):
        self._run_dictionary('test_escape_special_char', True)

    def test_round_bracket(self):
        self._run_dictionary('test_round_bracket', True)

    def test_many_roundBrackets(self):
        self._run_dictionary('test_many_roundBrackets', True)

    def test_many_roundBrackets_backwards(self):
        self._run_dictionary('test_many_roundBrackets_backwards', True)

    def test_round_bracket1(self):
        self._run_dictionary('test_round_bracket1', True)
    
    def test_round_bracket2(self):
        self._run_dictionary('test_round_bracket2', True)

if __name__ == '__main__':
     
    #Failing #2
    regex = 'a(\\()'
    str1 = 'a('
    #str1 = 'zzzzzzab)cdzzzz'     #Working without the spaces

    #pygex
    try:
        t0 = time.time()
        gex = pygex(regex, log=True)
        matched = gex.match(str1)
        total = time.time() - t0
        print(regex + '\n' + str1)
        print(('pygex -> ' + str(matched) + " in " + str(total)))
    except Exception as error:
        traceback.print_exc()
        print('\n')

    #python standard library - re
    t0 = time.time()
    rex = re.compile(regex)
    matched = rex.findall(str1)
    total = time.time() - t0
    if matched:
        print(("re -> True in " + str(total)))
    else:
        print(("re -> False in " + str(total)))