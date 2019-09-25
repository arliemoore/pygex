import unittest, time, re
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
    }
}

class pygex_tests(unittest.TestCase):
 
    def setUp(self):
        pass

    def _run_dictionary(self, testId, TorF):
        test = tests[testId]
        gex = pygex(test['regex'])
        for str in test['str']:
            if TorF:
                self.assertTrue(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))
            else:
                self.assertFalse(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))
    

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

if __name__ == '__main__':
    
    regex = 'hello'
    str1 = 'hello everyone how are you doing today'

    #pygex
    t0 = time.time()
    gex = pygex(regex, log=True)
    matched = gex.match(str1)
    total = time.time() - t0
    print((str(matched) + " in " + str(total)))

    #python re
    t0 = time.time()
    rex = re.compile(regex)
    matched = rex.match(str1)
    total = time.time() - t0
    if matched:
        print(("True in " + str(total)))
    else:
        print(("False in " + str(total)))