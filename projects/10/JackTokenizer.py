"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

Keywords = {'class', 'constructor' , 'function' , 'method' , 'field' , 
               'static' , 'var' , 'int' , 'char' , 'boolean' , 'void' , 'true' ,
               'false' , 'null' , 'this' , 'let' , 'do' , 'if' , 'else' , 
               'while' , 'return'}

Symbols = {'{' , '}' , '(' , ')' , '[' , ']' , '.' , ',' , ';' , '+' , 
              '-' , '*' , '/' , '&' , '|' , '<' , '>' , '=' , '~' , '^' , '#'}

IntegerConstantRange = range(0, 32768)

StringConstantDelimiter = {'"', '\n'}

IdentifierStartChars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_")
IdentifierChars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")

class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line's end.

    - 'xxx': quotes are used for tokens that appear verbatim ('terminals').
    - xxx: regular typeface is used for names of language constructs 
           ('non-terminals').
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        self.input = input_stream.read()
        self.tokens = self.input
        # print("Untouched input:", self.input)
        self._delete_comments()
        # print("Input without comments:", self.input)
        self._isolate_strings()
        # print("Tokens after isolating strings:", self.tokens)
        self._split_non_string_tokens()
        # print("Final tokens:", self.tokens)
        self.current_index = 0
        self.current_token = None

    def _split_non_string_tokens(self) -> None:
        new_tokens = []
        for token in self.tokens:
            if token.startswith('"') and token.endswith('"'):
                new_tokens.append(token)
            else:
                current_token = ""
                for char in token:
                    if char in Symbols:
                        if current_token:
                            new_tokens.append(current_token)
                            current_token = ""
                        new_tokens.append(char)
                    elif char.isspace():
                        if current_token:
                            new_tokens.append(current_token)
                            current_token = ""
                    else:
                        current_token += char
                if current_token:
                    new_tokens.append(current_token)
        self.tokens = new_tokens

    def _isolate_strings(self) -> None:
        self.tokens = self.input.split('"')
        for i in range(1, len(self.tokens), 2):
            self.tokens[i] = '"' + self.tokens[i] + '"'

    def _delete_comments(self) -> str:
        """Deletes all comments from the input string.

        Args:
            input_str (str): input string.
        Returns:
            str: input string without comments.
        """
        in_block_comment = False
        in_line_comment = False
        i = 0
        result = ""
        while i < len(self.input):
            if in_block_comment:
                if self.input[i:i+2] == '*/':
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
            elif in_line_comment:
                if self.input[i] == '\n':
                    in_line_comment = False
                    result += self.input[i]
                    i += 1
                else:
                    i += 1
            else:
                if self.input[i:i+2] == '/*':
                    in_block_comment = True
                    i += 2
                elif self.input[i:i+2] == '//':
                    in_line_comment = True
                    i += 2
                else:
                    result += self.input[i]
                    i += 1
        self.input = result

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        # Your code goes here!
        return self.current_index < len(self.tokens)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        # Your code goes here!
        if self.has_more_tokens():
            self.current_token = self.tokens[self.current_index]
            self.current_index += 1
             
    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Check for keyword
        if self.current_token in Keywords:
            return "KEYWORD"
        # Check for symbol
        elif self.current_token in Symbols:
            return "SYMBOL"
        # Check for integer constant (only digits, within range 0-32767)
        elif self.current_token.isdigit() and int(self.current_token) in IntegerConstantRange:
            return "INT_CONST"
        # Check for string constant (enclosed in quotes, no internal quotes or newlines)
        elif (self.current_token.startswith('"') and 
              self.current_token.endswith('"') and 
              '\n' not in self.current_token and '"' not in self.current_token[1:-1]):
            return "STRING_CONST"
        # Check for valid identifier (starts with letter or underscore, contains only valid chars)
        elif (len(self.current_token) > 0 and 
              self.current_token[0] in IdentifierStartChars and 
              all(c in IdentifierChars for c in self.current_token)):
            return "IDENTIFIER"
        else:
            # Invalid token - shouldn't happen with valid Jack code
            return "IDENTIFIER"

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        # Your code goes here!
        if self.token_type() == "KEYWORD":
            return self.current_token.upper()
        else:
            raise ValueError("Current token is not a keyword")

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        # Your code goes here!
        if self.token_type() == "SYMBOL":
            return self.current_token
        else:
            raise ValueError("Current token is not a symbol")

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self.token_type() != "IDENTIFIER":
            raise ValueError(f"Current token '{self.current_token}' is not a valid identifier")
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        # Your code goes here!
        if self.token_type() == "INT_CONST":
            return int(self.current_token)
        else:
            raise ValueError("Current token is not an integer constant")

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        # Your code goes here!
        if self.token_type() == "STRING_CONST":
            return self.current_token[1:-1]
        else:
            raise ValueError("Current token is not a string constant")