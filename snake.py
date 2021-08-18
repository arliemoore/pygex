import copy, boto3, botocore, unittest

'''
Main function to import for use.
'''
def Slither(str):
    snake_start_location, snake_end_location = [0, 0], [4, 4]
    s = snake(snake_start_location, snake_end_location)
    cage = snake_cage(5, 5)
    output = s.slither(str, cage)
    return output

'''
Snake object that has a starting and ending location.
'''
class snake():
    def __init__(self, start, end, log=False):
        #Coordinates of snake starting location
        self.start = start
        #Coordinates of snake ending location
        self.end = end    
        #Print debug'ing statements
        self.log = log

    def slither(self, input, sc):
        #Insert Snake into cage
        sc.insert_snake(self.start)
        #Move the snake to its end location
        return self._move(input, '', sc)

    '''
    Move the snake through the cage 
    '''  
    def _move(self, input, output, sc):
        self._log('###')
        self._log(sc.cage_str())
        self._log(("in='" + input + "' : out='" + output + "'"))
        #Check if all input has been consumed
        if input == '':
            s = sc.find_snake()
            self._log(('End: ' + str(self.end) + ' --- Snake: [' + str(s[1]) + ', ' + str(s[0]) + ']'))
            #Check if snake is in bottom right corner
            if sc.is_in(self.end):
                self._log('MATCH')
                return output
            #All input has been consumed but snake not in correct location
            else:
                self._log("DEAD END")
                return ''
        #Consume a character
        try:
            char = input[:1]
            if char == 'r':
                sc.move_direction(char)
                return self._move(input[1:], (output + char), sc)
            elif char == 'l':
                sc.move_direction(char)
                return self._move(input[1:], (output + char), sc)
            elif char == 'u':
                sc.move_direction(char)
                return self._move(input[1:], (output + char), sc)
            elif char == 'd':
                sc.move_direction(char)
                return self._move(input[1:], (output + char), sc)
            elif char == '?':
                #Try moving right first
                try:
                    out = self._move(('r' + input[1:]), output, snake_cage(sc.get_h(), sc.get_w(), sc.copy_cage()))
                    if out != '':
                        return out
                except IndexError as e:
                    self._log(("Snake hit wall r -> " + str(e)))
                #Try moving left
                try:
                    out = self._move(('l' + input[1:]), output, snake_cage(sc.get_h(), sc.get_w(), sc.copy_cage()))
                    if out != '':
                        return out
                except IndexError as e:
                    self._log(("Snake hit wall l -> " + str(e)))
                #Try moving up
                try:
                    out = self._move(('u' + input[1:]), output, snake_cage(sc.get_h(), sc.get_w(), sc.copy_cage()))
                    if out != '':
                        return out
                except IndexError as e:
                    self._log(("Snake hit wall u -> " + str(e)))
                #Try moving down
                try:
                    out = self._move(('d' + input[1:]), output, snake_cage(sc.get_h(), sc.get_w(), sc.copy_cage()))
                    if out != '':
                        return out
                except IndexError as e:
                    self._log(("Snake hit wall d -> " + str(e)))
                return '' 
            else:
                raise ValueError(("Bad input character " + char))
        except IndexError as e:
            self._log(("Snake hit wall -> " + str(e)))
            return ''
    
    def _log(self, str):
        if self.log:
            print(str)

'''
Cage object that is represented as a matrix

Matix/Cage Map
(w,h) (5x5)
|  0,0  0,1  0,2  0,3  0,4  |
|  1,0  1,1  1,2  1,3  1,4  |
|  2,0  2,1  2,2  2,3  2,4  |
|  3,0  3,1  3,2  3,3  3,4  |
|  4,0  4,1  4,2  4,3  4,4  |
'''
class snake_cage():
    def __init__(self, h, w, cage=None):
        self.h = h
        self.w = w
        
        #Create new cage
        if cage == None:
            self.cage = my_list([my_list([0 for x in range(self.w)]) for y in range(self.h)])
        #Copied cage
        else:
            self.cage = cage
    
    '''
    Getter methods for height and width
    '''
    def get_w(self):
        return self.w
    def get_h(self):
        return self.h

    '''
    Insert snake into cage at starting location
    '''
    def insert_snake(self, start):
        self.cage[start[0]][start[1]] = 1
    
    '''
    Used to copy a cage matrix that will be used 
    to create another cage_snake object
    '''
    def copy_cage(self):
        return copy.deepcopy(self.cage)
    
    '''
    Move the snake up, down, left, or right
    inside the cage
    '''
    def move_direction(self, direction):
        snake = self.find_snake()
        if snake is not None:
            #Snakes current location
            w = snake[0]
            h = snake[1]
            
            #Set current cell to 2 since snake is moving
            #and has already been in this cell
            self.cage[h][w] = 2

            #Figure out direction to move snake
            if direction == 'd':
                #height + 1 to move down
                h = h + 1
            elif direction == 'u':
                #height - 1 to move up
                h = h - 1
            elif direction == 'r':
                #width + 1 to move right
                w = w + 1
            elif direction == 'l':
                #width - 1 to move left
                w = w - 1
            else:
                raise ValueError('Invalid direction to move')

            if self.cage[h][w] == 0:
                #Move snake down a cell
                self.cage[h][w] = 1
                return
            else:
                #Snake has already been here, throw index error
                raise IndexError("Snake already been here")
    
    '''
    Return coordinates of snakes current location
    '''
    def find_snake(self):
        for h in range(0, self.h):
            for w in range(0, self.w):
                if self.cage[h][w] == 1:
                    return [w, h]
        raise IndexError("Snake is not in the cage")
    
    '''
    Return true if snake is located in specific (x, y)
    '''
    def is_in(self, location):
        if self.cage[location[0]][location[1]] == 1:
            return True
        else:
            return False
    
    '''
    Return string representation of the cage
    '''
    def cage_str(self):
        out = ''
        for h in range(0, self.h):
            out = out + '|  '
            for w in range(0, self.w):
                if self.cage[h][w] == 1:
                    out = out + '1  '
                elif self.cage[h][w] == 2:
                    out = out + '2  '
                else:
                    out = out + '0  '
            out = out + '|\n'
        return out

'''
Custom list class to error out for negative index.
'''
class my_list(list):
    def __getitem__(self, index):
        if index < 0:
            raise IndexError("list index out of range")
        return super(my_list, self).__getitem__(index)

'''
Pull test case file from S3. Read the file line
by line and run Slither(str). 
'''
def s3_tests():
    
    #S3 Variables
    BUCKET_NAME = 'slither'
    TEST_FILE = 'slither.txt'
    s3 = boto3.resource('s3')

    try:
        s3.Bucket(BUCKET_NAME).download_file(TEST_FILE, TEST_FILE)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

    #Open file, read lines, and continue printing
    with open(TEST_FILE, 'r') as file:
        for line in file:
            if line != '':
                print(Slither(line.strip()))

'''
Unit tests for slither
'''
class slither_tests(unittest.TestCase):
 
    def setUp(self):
        pass

    def test1(self):
        self.assertEqual(Slither('???rrurdr?'), 'dddrrurdrd')

    def test2(self):
        self.assertEqual(Slither('drdr??rrddd?'), 'drdruurrdddd')

    def test3(self):
        self.assertEqual(Slither('rrrrdlllld?rrr??????????'), 'rrrrdlllldrrrrdlllldrrrr')
    
    def test4(self):
        self.assertEqual(Slither('rrrr???l?r'), 'rrrrdddldr')

    def test5(self):
        self.assertEqual(Slither('d??dr????lu????????rdddd'), 'ddddrrrullurrullurrrdddd')

    def test6(self):
        self.assertEqual(Slither('??dd?ld???dr'), 'rrddlldrrrdr')

    def test7(self):
        self.assertEqual(Slither('????dddd'), 'rrrrdddd')

    def test8(self):
        self.assertEqual(Slither('????rrrr'), 'ddddrrrr')

    def test9(self):
        self.assertEqual(Slither('r????????ruuuurr????'), 'rdldrdldrruuuurrdddd')

    def test10(self):
        self.assertEqual(Slither('??dddd??'), 'rrddddrr')

    def tes11(self):
        self.assertEqual(Slither('rr????rr'), 'rrddddrr')
    
    def test12(self):
        self.assertEqual(Slither('r?r?r?r?'), 'rdrdrdrd')

    '''
    These tests are for other features like alternative cage sizes
    '''
    def test_cage_3x4(self):
        snake_start_location, snake_end_location = [0, 0], [3, 2]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(4, 3)
        self.assertEqual(s.slither('rr?dd', cage), 'rrddd')

    def test_cage_3x7(self):
        snake_start_location, snake_end_location = [0, 0], [6, 2]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(7, 3)
        self.assertEqual(s.slither('???dddruuuuuurddd?dd', cage), 'ddddddruuuuuurdddddd')

    def test_cage_21x17(self):
        snake_start_location, snake_end_location = [0, 0], [0, 1]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(17, 21)
        self.assertEqual(s.slither('d?u', cage), 'dru')

    def test_starting_ending_location1(self):
        snake_start_location, snake_end_location = [6, 4], [0, 1]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(7, 5)
        self.assertEqual(s.slither('??luuuu??', cage), 'llluuuuuu')

    def test_starting_ending_location2(self):
        snake_start_location, snake_end_location = [5, 7], [10, 0]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(11, 9)
        self.assertEqual(s.slither('uuuuur??????????luuuullllllldddd', cage), 'uuuuurddddddddddluuuullllllldddd')

    def test_starting_ending_location3(self):
        snake_start_location, snake_end_location = [1, 1], [0, 1]
        s = snake(snake_start_location, snake_end_location)
        cage = snake_cage(2, 2)
        self.assertEqual(s.slither('??r', cage), 'lur')

    
if __name__ == '__main__':
    s3_tests()
