from typing import List
from tokenType import TokenType
from bunToken import Token
from Expr import Expr, Binary, Unary, Literal, Grouping, Variable, Assign, If, Logical, Function, Call
import stmt
from stmt import Block, While, Expression, Return

class Parser:
    class ParseError(RuntimeError):
        pass

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0

    # def expression(self) -> Expr:
        # return self.equality()
        
    def expression(self) -> Expr:
        return self.assignment()
    
    def statement(self):
        if self.match(TokenType.PRINT):
            return self.printStatement()
        elif  self.match(TokenType.IF):
            return self.ifStatement()
        elif self.match(TokenType.LEFT_BRACE):
            return Block(self.block())
        elif self.match(TokenType.WHILE):
            return self.whileStatement()
        elif self.match(TokenType.FOR):
            return self.forStatement()
        elif self.match(TokenType.FUN):
            return self._function("function")
        elif self.match(TokenType.RETURN):
            return self.returnStatement()

        else:
            return self.expressionStatement()
        

    def returnStatement(self):
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return Return(keyword, value)

        
    def _function(self, kind):
        name = self.consume(TokenType.IDENTIFIER,"Expect " + kind + " name.")

        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.error(self.peek(), "Giga got more than 255 parameters.")
                parameters.append(self.consume(TokenType.IDENTIFIER, "Expect parameter name."))
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return Function(name, parameters, body)


        
    def forStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")

        initializer = None

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.varDeclaration()
        else:
            initializer = self.expressionStatement()

        condition = None
        if not (self.check(TokenType.SEMICOLON)):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not  (self.check(TokenType.RIGHT_PAREN)):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment != None:
            body = Block( [body, Expression(increment)] )
            # body = Block( [body, Expression.assign(increment)] )

        if condition is None:
            condition = Literal(True)
        
        body = While(condition, body)

        if (initializer != None):
            body = Block( [initializer, body] )


        return body



        
    def ifStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

        thenBranch = self.statement()
        elseBranch = None
        if self.match(TokenType.ELSE):
            elseBranch = self.statement()

        return If(condition, thenBranch, elseBranch)

    
    def printStatement(self):
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def expressionStatement(self):
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(expr)
    
    def block(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements
    
    # def assignment(self):
    #     # expr = self.equality()
    #     expr = self.or_()

    #     if self.match(TokenType.EQUAL):
    #         equals = self.previous()
    #         value = self.assignment()

    #         if isinstance(expr, Variable):
    #             name = expr.name
    #             return Assign(name, value)

    #         self.error(equals, "Invalid assignment target.")

    #     return expr

    def assignment(self):
        expr = self.or_()  # Assuming `or_()` parses logical OR expressions

        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()  # Recursively parse the right-hand side of the assignment

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)

            self.error(equals, "Invalid assignment target.")

        return expr



    def or_(self):
        expr = self.and_()

        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.and_()
            expr = Logical(expr, operator, right)

        return expr


    
    def and_(self):
        expr = self.equality()

        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr



    
    def equality(self):
        """
        equality → comparison ( ( "!=" | "==" ) comparison )* ;
        """
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    # Methods for other grammar rules can be added similarly

    def match(self, *types: TokenType) -> bool:
        """
        Check if the current token matches any of the given types.
        """
        for tokenType in types:
            if self.check(tokenType):
                self.advance()
                return True
        return False

    def check(self, tokenType: TokenType) -> bool:
        """
        Check if the current token is of the given type.
        """
        if self.is_at_end():
            return False
        return self.peek().token_type == tokenType

    def advance(self) -> Token:
        """
        Consume the current token and return it.
        """
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        """
        Check if we have reached the end of input.
        """
        return self.peek().token_type == TokenType.EOF

    def peek(self) -> Token:
        """
        Return the current token.
        """
        return self.tokens[self.current]

    def previous(self) -> Token:
        """
        Return the previous token.
        """
        return self.tokens[self.current - 1]

    def comparison(self) -> Expr:
        """
        comparison → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
        """
        expr = self.term()

        while self.match(TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self) -> Expr:
        """
        term → factor ( ( "-" | "+" ) factor )* ;
        """
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self) -> Expr:
        """
        factor → unary ( ( "/" | "*" ) unary )* ;
        """
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self) -> Expr:
        """
        unary → ( "!" | "-" ) unary | primary ;
        """
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        # return self.primary()
        return self.call()
    
    def call(self):
        expr = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finishCall(expr)
            else:
                break

        return expr
    
    def finishCall(self, callee):
        arguments = []

        # Parse the arguments if there are any
        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if (len(arguments) >= 255):
                    self.error(self.peek(), "Giga, too many arguments") 
                arguments.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break

        # Consume the closing parenthesis
        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        # Return a Call expression node
        return Call(callee, paren, arguments)



    def primary(self) -> Expr:
        """
        primary → NUMBER | STRING | "true" | "false" | "nil"
                | "(" expression ")" ;
        """
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)

        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")


    def consume(self, tokenType: TokenType, message: str) -> Token:
        """
        Consume the current token if it matches the given type,
        otherwise raise a syntax error with the provided message.
        """
        if self.check(tokenType):
            return self.advance()

        # Raise SyntaxError with the given message
        raise SyntaxError(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        """
        Raise a ParseError with the given message and token.
        """
        # Custom error reporting can be added here if needed
        raise self.ParseError(message)

    def synchronize(self):
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == TokenType.SEMICOLON:
                return

            # Check if the current token indicates the start of a new statement
            if self.peek().token_type in [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR,
                                          TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return

            self.advance()



    def declaration(self):
        try:
            if self.match(TokenType.VAR):
                return self.varDeclaration()
    
            return self.statement()
        except self.ParseError as error:
            self.synchronize()
            return None
        
    def varDeclaration(self):
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()

        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)
    


    
    def whileStatement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()

        return While(condition, body)





    def parse(self):
        declarations = []
        try:
            while not self.is_at_end():
                declarations.append(self.declaration())
        except self.ParseError as error:
            return error
        return declarations


    # def parse(self):
    #     statements = []
    #     try:
    #         while not self.is_at_end():
    #             statements.append(self.statement())
    #     except self.ParseError as error:
    #         return error
    #     return statements
