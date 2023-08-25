from abc import ABC, abstractmethod
from Environment import Environment
from Return import ReturnException

class LoxCallable(ABC):
    @abstractmethod
    def call(interpreter, arguments):
        pass
    
    @abstractmethod
    def arity(self):
        pass

class LoxFunction(LoxCallable):
    def __init__(self, declaration):
        self.declaration = declaration
    
    def call(self, interpreter, arguments):
        environment = Environment(interpreter.globals)
        for i in range(len(self.declaration.params)):
            environment.define(self.declaration.params[i].lexeme, arguments[i])
        try:
            interpreter.executeBlock(self.declaration.body, environment)
        except ReturnException as Return:
            return Return.value
        
        return None

    def arity(self):
        return len(self.declaration.params)
    
    def __str__(self):
        return "<fn " + self.declaration.name.lexeme + ">"