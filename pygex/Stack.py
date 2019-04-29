class Stack:

    def __init__(self):
        self.stack = []

    # Use list append method to add element
    def push(self, dataval):
        self.stack.append(dataval)
        
    # Use list pop method to remove element
    def pop(self):
        return self.stack.pop()

    def peek(self):     
	    return self.stack[-1]

    def size(self):
        return len(self.stack)

    def __str__(self):
        return str(self.stack)