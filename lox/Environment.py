class LOX_RuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token

class Environment:
    def __init__(self, enclosing = None):
        self.values = {}
        self.enclosing = enclosing
        
    def assign(self, name, value):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None: 
            self.enclosing.assign(name, value) 
            return
        raise LOX_RuntimeError(name, "Undefined variable '" + name.lexeme + "'.")
    
    def define(self, name, value):
        self.values[name] = value
        
    def get(self, name):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None: return self.enclosing.get(name)
        raise LOX_RuntimeError(name, "Undefined variable '"+ name.lexeme + "'.")