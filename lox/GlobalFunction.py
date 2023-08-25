from Callable import LoxCallable, LoxFunction
import os, time
            
class ClearCallable(LoxCallable):
        def call(self, interpreter, arguments):
            os.system('clear')
            return 0
            
        def arity(self):
            return 0
            
        def __str__(self):
            return "<native fn>"
            
class QuitCallable(LoxCallable):
        def call(self, interpreter, arguments):
            quit()
            
        def arity(self):
            return 0
            
        def __str__(self):
            return "<native fn>" 


class ClockCallable(LoxCallable):
        def call(self, interpreter, arguments):
            return float(time.time())
    
        def arity(self):
            return 0
    
        def __str__(self):
            return "<native fn>"
        
        
class PrintCallable(LoxFunction):
    def __init__(self, declaration=0):
        self.declaration = declaration
        
    def call(self, interpreter, arguments):
        for argument in arguments:
            print(interpreter.evaluate(argument))
        return 0
    
    def arity(self):
        return 0
    
    def __str__(self):
        return "<native fn>"