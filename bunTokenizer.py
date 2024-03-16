import re

# Define token regex patterns
token_patterns = [
    (r'\d+(\.\d+)?', 'NUMBER'),    # Numbers
    (r'\+', 'PLUS'),                 # Plus sign
    (r'-', 'MINUS'),                 # Minus sign
    (r'\*', 'MULTIPLY'),             # Multiply sign
    (r'/', 'DIVIDE'),                # Divide sign
    (r'\(', 'LPAREN'),               # Left parenthesis
    (r'\)', 'RPAREN'),               # Right parenthesis
    (r'=', 'ASSIGN'),                # Assignment operator
    (r'[a-zA-Z_][a-zA-Z0-9_]*', 'IDENTIFIER'),  # Identifier
    (r'\s+', None),                  # Whitespace (ignored)
]

# Tokenize input string
def tokenize(input_string):
    tokens = []
    while input_string:
        matched = False
        for pattern, token_type in token_patterns:
            match = re.match(pattern, input_string)
            if match:
                value = match.group(0)
                if token_type:
                    tokens.append((token_type, value))
                input_string = input_string[match.end():].strip()
                matched = True
                break
        if not matched:
            raise ValueError('Invalid character: ' + input_string[0])
    return tokens

# Test the tokenizer
input_string = "x = 10 + 20"
tokens = tokenize(input_string)
print(tokens)
