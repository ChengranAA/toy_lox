#!/opt/homebrew/bin/python3
import os, sys, readline, time
from Expr import Binary, Grouping, Literal, Unary, Variable, Assign, Call, Logical, ExprVisitor
from Stmt import Put, Expression, Var, Block, If, While, Function, Return, StmtVisitor
from Callable import LoxCallable, LoxFunction
from Environment import Environment, LOX_RuntimeError
from Return import ReturnException
from GlobalFunction import *

## TOKEN TYPE DEFINE
class TokenType:
    # Single-character tokens.
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    STAR = "STAR"

    # One or two character tokens.
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"

    # Literals.
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # Keywords.
    AND = "AND"
    CLASS = "CLASS"
    ELSE = "ELSE"
    FALSE = "FALSE"
    FUN = "FUN"
    FOR = "FOR"
    IF = "IF"
    NIL = "NIL"
    OR = "OR"
    PUT = "PUT"
    RETURN = "RETURN"
    SUPER = "SUPER"
    THIS = "THIS"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"
    BREAK = "BREAK"
    CONTINUE = "CONTINUE"

    EOF = "EOF"

## Reserve keywords
keywords = {
    "and": "AND",
    "class": "CLASS",
    "else": "ELSE",
    "false": "FALSE",
    "for": "FOR",
    "fun": "FUN",
    "if": "IF",
    "nil": "NIL",
    "or": "OR",
    "put": "PUT",
    "return": "RETURN",
    "super": "SUPER",
    "this": "THIS",
    "true": "TRUE",
    "var": "VAR",
    "while": "WHILE", 
    "break": "BREAK",
    "continue": "CONTINUE"
}


class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    
    def __str__(self):
        return f"{self.type} {self.lexeme} {self.literal}"
    
## The Scanner class
class Scanner():
    
    def __init__(self, source, lox): 
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1
        self.tokens = []
        self.lox = lox
    
    def isAtEnd(self):
        return self.current >= len(self.source)   
    
    
    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char
    
    def addToken(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
    
    def match(self, expected):
        if self.isAtEnd(): return False
        if self.source[self.current] != expected: return False
        
        self.current += 1 # behave like advance
        return True
    
    # Peaks
    def peak(self):
        if self.isAtEnd(): return '\0'
        return self.source[self.current]
    
    def peakNext(self):
        if self.current +1 >= len(self.source): return '\0' # when the next next c exceed the length of the file, return \0
        return self.source[self.current+1]
    
    # Method for handling string
    def string(self):
        while self.peak() != '"' and not self.isAtEnd():
            if self.peak == '\n': 
                self.line += 1
            self.advance()
        if self.isAtEnd():
            self.lox.error(self.line, "Unterminated string. ")
            return
        
        self.advance()
        
        value = self.source[self.start+1:self.current-1]
        self.addToken(TokenType.STRING, value)
    
    # Methods for handling digits
    def isDigit(self, c):
        return c >= '0' and c <= '9'
    
    def number(self):
        while self.isDigit(self.peak()): self.advance()     
        if self.peak() == '.' and self.isDigit(self.peakNext()): # if the next character is . and the next next character is a digit, the continue advance 
            self.advance()
            
            while self.isDigit(self.peak()): self.advance()
            
        self.addToken(TokenType.NUMBER, float(self.source[self.start: self.current])) # reach the end, parse the string to double
    
    # Methods for handling identifiers
    def isAlpha(self,c):
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_' # ASCII character
      
    def isAlphaNumeric(self,c):
        return self.isAlpha(c) or self.isDigit(c)
    
    def identifier(self):
        while self.isAlphaNumeric(self.peak()): self.advance() # if the next c is alphabet and number then keep advancing
        text = self.source[self.start:self.current]
        type = keywords.get(text)
        if type == None: type = TokenType.IDENTIFIER
        self.addToken(type)
        
    def scanToken(self):
        c = self.advance()
        match c: 
            case '(': 
                self.addToken(TokenType.LEFT_PAREN)
            case ')': 
                self.addToken(TokenType.RIGHT_PAREN)
            case '{': 
                self.addToken(TokenType.LEFT_BRACE)
            case '}': 
                self.addToken(TokenType.RIGHT_BRACE)
            case ',': 
                self.addToken(TokenType.COMMA)
            case '.': 
                self.addToken(TokenType.DOT)
            case '-': 
                self.addToken(TokenType.MINUS)
            case '+': 
                self.addToken(TokenType.PLUS)
            case ';': 
                self.addToken(TokenType.SEMICOLON)
            case '*': 
                self.addToken(TokenType.STAR)
            case '!':
                self.addToken(TokenType.BANG_EQUAL if self.match('=') else TokenType.BANG)
            case '=':
                self.addToken(TokenType.EQUAL_EQUAL if self.match('=') else TokenType.EQUAL)
            case '<':
                self.addToken(TokenType.LESS_EQUAL if self.match('=') else TokenType.LESS)
            case '>':
                self.addToken(TokenType.GREATER_EQUAL if self.match('=') else TokenType.GREATER)
            case '/':
                if self.match('/'):
                    while(self.peak() != '\n' and not self.isAtEnd()) : 
                        self.advance()
                elif self.match('*'):
                    while(self.peak() != '*' and self.peakNext () != '/' and not self.isAtEnd()):
                        if self.peak == '\n': 
                            self.line += 1
                        self.advance()
                    if self.isAtEnd():
                        self.lox.error(self.line, "Unterminated comment. ")
                    else:
                        self.advance()
                        self.advance()
                    
                else:
                    self.addToken(TokenType.SLASH) 
            case ' ':
                pass
            case '\r':
                pass
            case '\t':
                pass
            case '\n':
                self.line += 1
            case '"':
                self.string() 
            case 'o':
                if self.match('r'):
                    self.addToken(TokenType.OR)
            case _:
                if self.isDigit(c) :
                   self.number() 
                elif self.isAlpha(c):
                    self.identifier()
                else: 
                    self.lox.error(self.line, "Unexpected character.")
    
    def scanTokens(self):
        while (not self.isAtEnd()):
            self.start = self.current
            self.scanToken()
        
        self.tokens.append(Token(TokenType.EOF, "", None, self.line))
        return self.tokens

## The parser class
class Parser: 
    
    class LOX_ParserError(RuntimeError):
        pass
    
    def __init__(self, tokens, lox):
        self.results = []
        self.tokens = tokens
        self.current = 0
        self.lox = lox
        
        
    ## Addtional methods for expressions
    def peek(self):
        return self.tokens[self.current]
    
    def previous(self):
        return self.tokens[self.current - 1]
    
    def isAtEnd(self):
        return self.peek().type == TokenType.EOF
    
    def check(self, type):
        if self.isAtEnd():
            return False
        return self.peek().type == type
    
    def advance(self):
        if not self.isAtEnd():
            self.current += 1
        return self.previous()

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True
        return False
    
    ## Error Handling 
    def consume(self, type, message):
        if self.check(type): return self.advance()
        self.error(self.peek(), message)
    
    def synchronize(self):
        self.advance()
        
        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON: return
            match self.peek().type:
                case TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PUT, TokenType.RETURN: 
                    return
                
            self.advance()
    
    
    def error(self, token, message):
        self.lox.errorToken(token, message)
        raise self.LOX_ParserError()
    
    
    ## Expressions 
    def primary(self):
        if self.match(TokenType.FALSE): return Literal(False)
        if self.match(TokenType.TRUE): return Literal(True)
        if self.match(TokenType.NIL): return Literal(None)
        
        if self.match(TokenType.NUMBER, TokenType.STRING): 
            return Literal(self.previous().literal)
        
        if self.match(TokenType.IDENTIFIER): 
            return Variable(self.previous())
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()    
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression. ")
            return Grouping(expr)
        
        raise self.error(self.peek(), "Expect expression.")
    
    def finishCall(self, callee):
        arguments = []
        while not self.check(TokenType.RIGHT_PAREN):
            if len(arguments) >= 255:
                self.error(self.peek(), "Cant't have more than 255 arguments. ")
            if self.match(TokenType.COMMA):
                continue
            arguments.append(self.expression())
        
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        
        return Call(callee, paren, arguments)    
        
    def call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break
            
        return expr
                
    def unary(self):
        if (self.match(TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.call()
    
    def factor(self):
        expr = self.unary()
        while(self.match(TokenType.SLASH, TokenType.STAR)):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr
    
    
    def term(self):
        expr = self.factor()
        while(self.match(TokenType.MINUS, TokenType.PLUS)):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        
        return expr
    
    
    def comparison(self):
        expr = self.term()
        while(self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL)):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr
        
        
    def equality(self):
        expr = self.comparison()
        while(self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL)):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr
    
    
    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)
        
        return expr
    
    def assignment(self):
        expr  = self.logical_or()
        
        if (self.match(TokenType.EQUAL)):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            self.error(equals, "Invalid assignment target.")
            
        return expr 
    
    def expression(self):
        return self.assignment()
    
    ## other methods for statements
    def block(self):
        statements = []
        while (not self.check(TokenType.RIGHT_BRACE) and not self.isAtEnd()):
            statements.append(self.declaration())
            
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block")
        return statements
        
    def putStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Put(value)

    def function(self, kind):
        name = self.consume(TokenType.IDENTIFIER, "Expect " + kind + " name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after " + kind + " name.")
        parameters = []
        while not self.check(TokenType.RIGHT_PAREN):
            if len(parameters) >= 255:
                self.error(self.peek(), "Can't have more than 255 parameters.")
            if self.match(TokenType.COMMA):
                continue
            parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters")
        
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before " + kind + " body.")
        body = self.block()
        return Function(name, parameters, body)
    
    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return Expression(expr)
    
    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return Var(name, initializer)
    
    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expec ')' ater if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()
        
        return If(condition, thenBranch, elseBranch)
    
    def returnStatement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
            
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        
        return Return(keyword, value)
    
    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after 'while'.")
        body = self.statement()
        
        return While(condition, body)
    
    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        
        initilizer = None
        if self.match(TokenType.SEMICOLON):
            initilizer = None
        elif self.match(TokenType.VAR):
            initilizer = self.varDeclaration()
        else:
            initilizer = self.expressionStatement()
        
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.") 
        
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses")
        
        body = self.statement()
        
        if increment is not None:
            body = Block([body, Expression(increment)])
            
        if condition is not None:
            body = While(condition, body)
            
        if initilizer is not None:
            body = Block([initilizer, body])
        
        return body #which show this is a syntatic sugar, the body is a collection of statement of class
    
    ## Statement
    def statement(self):
        if self.match(TokenType.FOR): return self.forStatement()
        if self.match(TokenType.IF): return self.ifStatement()
        if self.match(TokenType.PUT): return self.putStatement()
        if self.match(TokenType.RETURN): return self.returnStatement()
        if self.match(TokenType.WHILE): return self.whileStatement()
        if self.match(TokenType.LEFT_BRACE): 
            return Block(self.block())
        return self.expressionStatement()
    
    def declaration(self):
        try:
            if self.match(TokenType.FUN): return self.function("function")
            if self.match(TokenType.VAR): return self.varDeclaration()
            return self.statement()
        except self.LOX_ParserError:
            self.synchronize()
            return None
    
    ## Parse
    def parse(self):
        statements = []
        while not self.isAtEnd():
            statements.append(self.declaration())
        return statements


## Interpreter (Visitor Class)
class Interpreter(ExprVisitor, StmtVisitor):
    
    def __init__(self):
        super().__init__()
        self.globals = Environment()
        self.environment = self.globals
        self.GlobalFunction()
        
        
    # Global function define
    def GlobalFunction(self):                 
        self.globals.define("clock", ClockCallable())
        self.globals.define("clear", ClearCallable())
        self.globals.define("quit", QuitCallable())
        self.globals.define("str", StrCallable())
    
    # Error Handling for expression
    def checkNumberOperand_unary(self, operator, operand):
        if isinstance(operand, float): return
        raise LOX_RuntimeError(operator, "Operand must be a number.")  
    
    def checkNumberOperand_binary(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LOX_RuntimeError(operator, "Operands mush be numbers")
            
    # other methods for expression
    def isTruthy(self, object):
        if object is None: return False
        if isinstance(object, bool): return object
        return True
    
    def isEqual(self, a, b):
        if a is None and b is None: return True
        if a is None: return False
        return a==b
    
    def evaluate(self, expr):
        return expr.accept(self)
    
    def stringify(self, object):
        if object is None: return "nil"
        
        if isinstance(object, float): 
            text = str(object)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        
        return str(object)
    
    # visitor patterns (overiding methods for expression) 
    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        
        if expr.operator.type == TokenType.OR:
            if self.isTruthy(left): return left
        else:
            if not self.isTruthy(left): return left
        
        return self.evaluate(expr.right)
    
    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)
        self.environment.assign(expr.name, value)
        return value
    
    
    def visit_literal_expr(self, expr):
        return expr.value
    
    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)
    
    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)
        
        match expr.operator.type:
            case TokenType.MINUS:
                self.checkNumberOperand_unary(expr.operator, right)
                return -right
            case TokenType.BANG:
                return not self.isTruthy(right)
        
        return None
    
    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)
        
        arguments = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
    
        
        if not isinstance(callee, LoxCallable):
            raise LOX_RuntimeError(expr.paren, "Can only call functions and classes. ")
        
        function = callee
        
        if len(arguments) != function.arity():
            raise LOX_RuntimeError(expr.paren, "Expected " + function.arity() + " arguments but got "+ len(arguments) + ".")
        
        return function.call(self, arguments)
    
    def visit_variable_expr(self, expr):
        return self.environment.get(expr.name)
    
    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        
        match expr.operator.type:
            case TokenType.GREATER:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left <= right
            case TokenType.BANG_EQUAL:
                return not self.isEqual(left, right)
            case TokenType.EQUAL_EQUAL:
                return self.isEqual(left, right)
            case TokenType.MINUS:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                raise LOX_RuntimeError(expr.operator, "Operand must be two numbers or two strings")
            case TokenType.SLASH:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                self.checkNumberOperand_binary(expr.operator, left, right)
                return left * right
        
        return None
    
    # other methods for statements
    def execute(self, stmt):
        stmt.accept(self)
        
    def executeBlock(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements: 
                self.execute(statement)
        finally:
            self.environment = previous
                
    
    # Visitor patterns (override methods for statements)
    def visit_block_stmt(self, stmt):
        self.executeBlock(stmt.statements, Environment(self.environment))
        return None
    
    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)
        return None
    
    def visit_put_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None
    
    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer !=  None:
            value = self.evaluate(stmt.initializer)
        
        self.environment.define(stmt.name.lexeme, value)
        return None
    
    def visit_if_stmt(self, stmt):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseBranch != None:
            self.execute(stmt.elseBranch)
        return None

    def visit_while_stmt(self, stmt):
        while self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None
    
    def visit_return_stmt(self, stmt):
        value = None
        if stmt.value != None: value = self.evaluate(stmt.value);

        raise ReturnException(value)
    
    def visit_function_stmt(self, stmt):
        function = LoxFunction(stmt)
        self.environment.define(stmt.name.lexeme, function)
        
        return None
    
    # Interperter
    def interpret(self, statements, lox):
        try:
            for statement in statements:
                self.execute(statement)
        except LOX_RuntimeError as error:
            lox.errorRuntime(error)

## Application class  
class Lox: 
    
    def __init__(self):
        self.hadError = False
        self.hadRuntimeError = False
        self.interpreter = Interpreter()
    
    # Run methods
    def run(self, source):
        
        scanner = Scanner(source,self)
        tokens = scanner.scanTokens()

        if DEBUG:
            for token in tokens: 
                print(token)
            return
        
        parser = Parser(tokens, self)
        statements = parser.parse()
        
        if self.hadError: return
        self.interpreter.interpret(statements, self)
       
    def run_prompt(self):
        while True:
            prompt = ">> "
            line = input(prompt)
            if line == None: break
            if line.endswith(';'):
                self.run(line)
            else:
                self.run(line + ";")
            self.hadError = False
            
    def run_file(self, path):
        with open(path, 'rb') as file:
            bytes_data = file.read()
            self.run(bytes_data.decode('utf-8'))
            if self.hadError: sys.exit(65)
            if self.hadRuntimeError: sys.exit(70)
    
    # Error handling
    def error(self, line, message): 
        self.report(line, "", message)
        
    def errorToken(self, token, message):
        if (token.type == TokenType.EOF):
            self.report(token.line, " at end", message)
        else: 
            self.report(token.line, " at '" + token.lexeme + "'", message)

    def errorRuntime(self, error):
        print("[line " + str(error.token.line) + "] Error: " + error.args[0])
        self.hadRuntimeError = True
    
    def report(self, line, where, message):
        print("[line " + str(line) + "] Error" + str(where) + ": " + message)
        self.hadError = True
    
    # Main function for lox interpreter
    def main(self, argc, argv):
        if argc > 2: 
            print("Usage: python lox.py [script]")
            sys.exit(64)
        elif argc == 2: 
            self.run_file(argv[1])
        else:
            self.run_prompt()


if __name__ == "__main__":
    # DEBUG
    DEBUG = False

    # Instantiate the Lox class
    lox = Lox()

    # Call the main method with appropriate arguments   
    lox.main(len(sys.argv), sys.argv)