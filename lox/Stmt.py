from abc import ABC, abstractmethod

class Stmt(ABC):
	@abstractmethod
	def accept(self, visitor):
		pass

class StmtVisitor:
	@abstractmethod
	def visit_block_stmt(self, stmt):
		pass

	@abstractmethod
	def visit_expression_stmt(self, stmt):
		pass

	@abstractmethod
	def visit_if_stmt(self, stmt):
		pass

	@abstractmethod
	def visit_print_stmt(self, stmt):
		pass

	@abstractmethod
	def visit_var_stmt(self, stmt):
		pass

	@abstractmethod
	def visit_while_stmt(self, stmt):
		pass

class Block(Stmt):
	def __init__(self, statements):
		self.statements = statements
	def accept(self, visitor):
		return visitor.visit_block_stmt(self)

class Expression(Stmt):
	def __init__(self, expression):
		self.expression = expression
	def accept(self, visitor):
		return visitor.visit_expression_stmt(self)

class If(Stmt):
	def __init__(self, condition, thenBranch, elseBranch):
		self.condition = condition
		self.thenBranch = thenBranch
		self.elseBranch = elseBranch
	def accept(self, visitor):
		return visitor.visit_if_stmt(self)

class Print(Stmt):
	def __init__(self, expression):
		self.expression = expression
	def accept(self, visitor):
		return visitor.visit_print_stmt(self)

class Var(Stmt):
	def __init__(self, name, initializer):
		self.name = name
		self.initializer = initializer
	def accept(self, visitor):
		return visitor.visit_var_stmt(self)

class While(Stmt):
	def __init__(self, condition, body):
		self.condition = condition
		self.body = body
	def accept(self, visitor):
		return visitor.visit_while_stmt(self)

