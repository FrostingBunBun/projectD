from Expr import Visitor
from tokenType import TokenType
from stmt import StmtVisitor


class Interpreter(Visitor, StmtVisitor):

    def evaluate(self, expr):
        return expr.accept(self)
    
    def execute(self, stmt):
        stmt.accept(self)
    
    def visitExpressionStmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None
    
    def visitPrintStmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))
        return None

    
    @staticmethod
    def isTruthy(obj):
        if obj is None:
            return False
        if isinstance(obj, bool):
            return obj
        return True

    @staticmethod
    def isEqual(object1, object2):
        if object1 is None and object2 is None:
            return True
        if object1 is None:
            return False
        return object1 == object2

    @staticmethod
    def stringify(object):
        if object is None:
            return "nil"
        if isinstance(object, (float, int)):
            text = str(object)
            if text.endswith(".0"):
                text = text[:-2]
            return text
        return str(object)


    @staticmethod
    def checkNumberOperands(operator, left, right):
        if isinstance(left, (float, int)) and isinstance(right, (float, int)):
            return
        raise RuntimeError(operator, "Operands must be numbers.")

    def visitLiteralExpr(self, expr):
        return expr.value

    def visitGroupingExpr(self, expr):
        return self.evaluate(expr.expression)
    
    @staticmethod
    def checkNumberOperand(operator, operand):
        if isinstance(operand, (float, int)):
            return
        raise RuntimeError(operator, "Operand must be a number.")

    def visitUnaryExpr(self, expr):
        right = self.evaluate(expr.right)
        # print("Unary Expr - Operator:", expr.operator.token_type)
        # print("Unary Expr - Right:", right)

        if expr.operator.token_type == TokenType.MINUS:
            self.checkNumberOperand(expr.operator.token_type, right)
            return -float(right)
        elif expr.operator.token_type == TokenType.BANG:
            return not self.isTruthy(right)

        # Unreachable.
        return None

    def visitBinaryExpr(self, expr):

        
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

       
        # print("Unary Expr - Left:", left)
        # print("Unary Expr - Right:", right)
        # print("\n")
        # print("Unary Expr - Operator:", expr.operator)
        # print("TEST: ", TokenType.PLUS)
        # print("OPERATOR type: ", expr.operator.token_type)

        # print("ACTUAL1: ", type(TokenType.PLUS))
        # print("ACTUAL2: ", type(expr.operator))
        # print("ACTUAL2: ", type(expr.operator.token_type))
        # print("\n")
        

        if expr.operator.token_type == TokenType.MINUS:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) - float(right)
        elif expr.operator.token_type == TokenType.SLASH:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            if right == 0:
                raise RuntimeError(expr.operator.token_type, "Division by zero")
            return float(left) / float(right)
        elif expr.operator.token_type == TokenType.STAR:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) * float(right)
        
        elif expr.operator.token_type == TokenType.PLUS:
            if isinstance(left, (float, int)) and isinstance(right, (float, int)) or isinstance(left, int) and isinstance(right, int):
                return float(left) + float(right)
            if isinstance(left, str) and isinstance(right, str):
                return str(left) + str(right)
            raise RuntimeError(expr.operator.token_type, "Operands must be two numbers or two strings.")
        
        elif expr.operator.token_type == TokenType.GREATER:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) > float(right)
        elif expr.operator.token_type == TokenType.GREATER_EQUAL:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) >= float(right)
        elif expr.operator.token_type == TokenType.LESS:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) < float(right)
        elif expr.operator.token_type == TokenType.LESS_EQUAL:
            self.checkNumberOperands(expr.operator.token_type, left, right)
            return float(left) <= float(right)
        elif expr.operator.token_type == TokenType.BANG_EQUAL:
            return not self.isEqual(left, right)
        elif expr.operator.token_type == TokenType.EQUAL_EQUAL:
            return self.isEqual(left, right)
    
        # Unreachable.
        return None


    def interpret(self, statements):
        try:
            for statement in statements:
                self.execute(statement)
        except RuntimeError as error:
            print(error)