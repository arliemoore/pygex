import unittest, pygex

'''Test Cases'''

tests = {
    
    #This is failing, but should work.
    #Special characters and spaces are messing up the first part of the pattern?
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
    }
}

class pygex_tests(unittest.TestCase):
 
    def setUp(self):
        pass

    def test_concat1_true(self):
        test = tests['test_concat1_true']
        gex = pygex.pygex(test['regex'])
        for str in test['str']:
            self.assertTrue(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))

    def test_contact1_false(self):
        test = tests['test_concat1_false']
        gex = pygex.pygex(test['regex'])
        for str in test['str']:
            self.assertFalse(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))

    def test_split1_true(self):
        test = tests['test_split1_true']
        gex = pygex.pygex(test['regex'])
        for str in test['str']:
            self.assertTrue(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))

    def test_zeroOrOne_true(self):
        test = tests['test_zeroOrOne1_true']
        gex = pygex.pygex(test['regex'])
        for str in test['str']:
            self.assertTrue(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))

    def test_zeroOrOne2_true(self):
        test = tests['test_zeroOrOne2_true']
        gex = pygex.pygex(test['regex'])
        for str in test['str']:
            self.assertTrue(gex.match(str), msg=('regex="' + test['regex']  + '" : str="' + str + '"'))
 
if __name__ == '__main__':
    unittest.main()