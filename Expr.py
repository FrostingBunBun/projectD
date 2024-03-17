class Expr:
    def __str__(self):
        return "Generic Expr"
    
    def __init__(self):
        pass

    def accept(self, visitor):
        pass


class Visitor:
    def visitBinaryExpr(self, expr):
        pass

    def visitGroupingExpr(self, expr):
        pass

    def visitLiteralExpr(self, expr):
        pass

    def visitUnaryExpr(self, expr):
        pass

class Binary(Expr):
    def __str__(self):
        return f"Binary Expr: {self.left} {self.operator} {self.right}"
    
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinaryExpr(self)

class Grouping(Expr):
    def __str__(self):
        return f"Grouping Expr: {self.expression}"
    
    def __init__(self, expression):
        self.expression = expression

    def accept(self, visitor):
        return visitor.visitGroupingExpr(self)

class Literal(Expr):
    def __str__(self):
        return f"Literal: {self.value}"
    
    def __init__(self, value):
        self.value = value

    def accept(self, visitor):
        return visitor.visitLiteralExpr(self)

class Unary(Expr):
    def __str__(self):
        return f"Unary Expr: {self.operator} {self.right}"
    
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        return visitor.visitUnaryExpr(self)
