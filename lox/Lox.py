import os, sys, readline
from lox.Expr import Binary, Grouping, Literal, Unary, ExprVisitor

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
    PRINT = "PRINT"
    RETURN = "RETURN"
    SUPER = "SUPER"
    THIS = "THIS"
    TRUE = "TRUE"
    VAR = "VAR"
    WHILE = "WHILE"

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
    "print": "PRINT",
    "return": "RETURN",
    "super": "SUPER",
    "this": "THIS",
    "true": "TRUE",
    "var": "VAR",
    "while": "WHILE"
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
        
        
    ## Addtional methods 
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
        
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()    
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression. ")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")
        
    
    def unary(self):
        if (self.match(TokenType.BANG, TokenType.MINUS)):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()
    
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
    
    def expression(self):
        return self.equality()
    
    ## Parse
    def parse(self):
        try: 
            return self.expression()
        except self.LOX_ParserError as e:
            return None

class LOX_RuntimeError(RuntimeError):
    def __init__(self, token, message):
        super().__init__(message)
        self.token = token


## Interpreter (Visitor Class)
class Interpreter(ExprVisitor):
    
    # Error Handling
    def checkNumberOperand_unary(self, operator, operand):
        if isinstance(operand, float): return
        raise LOX_RuntimeError(operator, "Operand must be a number.")  
    
    def checkNumberOperand_binary(self, operator, left, right):
        if isinstance(left, float) and isinstance(right, float):
            return
        raise LOX_RuntimeError(operator, "Operands mush be numbers")
            
    # other methods
    def isTruthy(self, obj):
        if object is None: return False
        if isinstance(obj, bool): return obj
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
    
    # visitor patterns (overiding methods)
    
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
    
    # Interperter
    def interpret(self, expression, lox):
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except LOX_RuntimeError as error:
            lox.errorRuntime(error)
    

## The printAst class
class AstPrinter(ExprVisitor):
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme,
                                 expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *exprs):
        result = "(" + name
        for expr in exprs:
            result += " " + expr.accept(self)
        result += ")"
        return result 
    

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
        
        '''
        for token in tokens: 
            print(token)
        '''
        
        parser = Parser(tokens, self)
        expression = parser.parse()
        
        if self.hadError: return

        print("=== AST Tree ===")
        printer = AstPrinter()      
        print(printer.print(expression))
        
        
        self.interpreter.interpret(expression, self)
        
    def run_prompt(self):
        while True:
            prompt = ">> "
            line = input(prompt)
            if line == None: break
            self.run(line)
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
            self.report(token.line, " at '" + token.lexeme + ",", message)

    def errorRuntime(self, error):
        print(f"{error.args[0]}\n[line {error.token.line}]")
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

    # Instantiate the Lox class
    lox = Lox()

    # Call the main method with appropriate arguments   
    lox.main(len(sys.argv), sys.argv)