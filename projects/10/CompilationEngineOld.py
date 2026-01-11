"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.output = output_stream

    def compile_class(self) -> None:
        """Compiles a complete class.
        Grammar: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        # Expect 'class' keyword
        if self.tokenizer.token_type() != "KEYWORD" or self.tokenizer.keyword() != "CLASS":
            raise ValueError(f"Expected 'class', got {self.tokenizer.current_token}")
        
        self.output.write("<class>\n")
        self.output.write(f"<keyword> class </keyword>\n")
        self.tokenizer.advance()
        
        # Expect className (identifier)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected className, got {self.tokenizer.current_token}")
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> {{ </symbol>\n")
        self.tokenizer.advance()
        
        # Parse classVarDec* (zero or more)
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["STATIC", "FIELD"]):
            self.compile_class_var_dec()
        
        # Parse subroutineDec* (zero or more)
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]):
            self.compile_subroutine()
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> }} </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</class>\n")
        

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration.
        Grammar: ('static' | 'field') type varName (',' varName)* ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() in ["STATIC", "FIELD"]):
            return
        
        self.output.write("<classVarDec>\n")
        
        # Parse 'static' or 'field'
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Parse type
        self._parse_type()
        
        # Parse varName (',' varName)*
        while True:
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected identifier, got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            
            if self.tokenizer.current_token == ",":
                self.output.write(f"<symbol> , </symbol>\n")
                self.tokenizer.advance()
            else:
                break
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        Grammar: ('constructor' | 'function' | 'method') ('void' | type) 
                 subroutineName '(' parameterList ')' subroutineBody
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() in ["CONSTRUCTOR", "FUNCTION", "METHOD"]):
            return
        
        self.output.write("<subroutineDec>\n")
        
        # Parse 'constructor', 'function', or 'method'
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Parse return type ('void' or type)
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword() == "VOID":
            self.output.write(f"<keyword> void </keyword>\n")
            self.tokenizer.advance()
        else:
            self._parse_type()
        
        # Parse subroutineName (identifier)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected subroutine name, got {self.tokenizer.current_token}")
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Parse '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # Parse parameterList
        self.compile_parameter_list()
        
        # Parse ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()
        
        # Parse subroutineBody
        self.compile_subroutine_body()
        
        self.output.write("</subroutineDec>\n")

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        Grammar: ((type varName) (',' type varName)*)?
        """
        self.output.write("<parameterList>\n")
        
        # Check if parameter list is empty
        if self.tokenizer.current_token == ")":
            self.output.write("</parameterList>\n")
            return
        
        # Parse first parameter
        self._parse_type()
        
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected parameter name, got {self.tokenizer.current_token}")
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Parse additional parameters
        while self.tokenizer.current_token == ",":
            self.output.write(f"<symbol> , </symbol>\n")
            self.tokenizer.advance()
            
            self._parse_type()
            
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected parameter name, got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        
        self.output.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration.
        Grammar: 'var' type varName (',' varName)* ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "VAR"):
            return
        
        self.output.write("<varDec>\n")
        
        # Parse 'var' keyword
        self.output.write(f"<keyword> var </keyword>\n")
        self.tokenizer.advance()
        
        # Parse type
        self._parse_type()
        
        # Parse varName (',' varName)*
        while True:
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected identifier, got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            
            if self.tokenizer.current_token == ",":
                self.output.write(f"<symbol> , </symbol>\n")
                self.tokenizer.advance()
            else:
                break
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</varDec>\n")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        Grammar: statement*
        """
        self.output.write("<statements>\n")
        
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() in ["LET", "IF", "WHILE", "DO", "RETURN"]):
            if self.tokenizer.keyword() == "LET":
                self.compile_let()
            elif self.tokenizer.keyword() == "IF":
                self.compile_if()
            elif self.tokenizer.keyword() == "WHILE":
                self.compile_while()
            elif self.tokenizer.keyword() == "DO":
                self.compile_do()
            elif self.tokenizer.keyword() == "RETURN":
                self.compile_return()
        
        self.output.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement.
        Grammar: 'do' subroutineCall ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "DO"):
            return
        
        self.output.write("<doStatement>\n")
        
        # 1. 'do' keyword
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # 2. subroutineCall logic
        # Expect Identifier (className | varName | subroutineName)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected identifier in do statement, got {self.tokenizer.current_token}")
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Check for '.' (method call like Game.run)
        if self.tokenizer.current_token == ".":
            self.output.write(f"<symbol> . </symbol>\n")
            self.tokenizer.advance()
            
            # Expect subroutineName
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected subroutine name after '.', got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # 3. Compile expression list
        # Note: We must manually write the tags because compile_expression_list 
        # in your code doesn't write the opening/closing tags itself.
        self.output.write("<expressionList>\n")
        self.compile_expression_list()
        self.output.write("</expressionList>\n")
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()
        
        # 4. Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</doStatement>\n")
    
    def compile_let(self) -> None:
        """Compiles a let statement.
        Grammar: 'let' varName ('[' expression ']')? '=' expression ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "LET"):
            return
        
        self.output.write("<letStatement>\n")
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Expect varName
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected variable name, got {self.tokenizer.current_token}")
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Handle optional array subscript: '[' expression ']'
        if self.tokenizer.current_token == "[":
            self.output.write(f"<symbol> [ </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            if self.tokenizer.current_token != "]":
                raise ValueError(f"Expected ']', got {self.tokenizer.current_token}")
            self.output.write(f"<symbol> ] </symbol>\n")
            self.tokenizer.advance()
        
        # Expect '='
        if self.tokenizer.current_token != "=":
            raise ValueError(f"Expected '=', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> = </symbol>\n")
        self.tokenizer.advance()
        
        # Expect expression
        self.compile_expression()
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement.
        Grammar: 'while' '(' expression ')' '{' statements '}'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "WHILE"):
            return
        
        self.output.write("<whileStatement>\n")
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # Parse expression
        self.compile_expression()
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> {{ </symbol>\n")
        self.tokenizer.advance()
        
        # Parse statements
        self.compile_statements()
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> }} </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</whileStatement>\n")

    def compile_return(self) -> None:
        """Compiles a return statement.
        Grammar: 'return' expression? ';'
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "RETURN"):
            return
        
        self.output.write("<returnStatement>\n")
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Parse optional expression
        if self.tokenizer.current_token != ";":
            self.compile_expression()
        
        # Expect ';'
        if self.tokenizer.current_token != ";":
            raise ValueError(f"Expected ';', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ; </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause.
        Grammar: 'if' '(' expression ')' '{' statements '}' ('else' '{' statements '}')?
        """
        if not (self.tokenizer.token_type() == "KEYWORD" and 
                self.tokenizer.keyword() == "IF"):
            return
        
        self.output.write("<ifStatement>\n")
        self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
        self.tokenizer.advance()
        
        # Expect '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # Parse expression
        self.compile_expression()
        
        # Expect ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()
        
        # Expect '{'
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> {{ </symbol>\n")
        self.tokenizer.advance()
        
        # Parse statements
        self.compile_statements()
        
        # Expect '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> }} </symbol>\n")
        self.tokenizer.advance()
        
        # Handle optional else clause
        if (self.tokenizer.token_type() == "KEYWORD" and 
            self.tokenizer.keyword() == "ELSE"):
            self.output.write(f"<keyword> else </keyword>\n")
            self.tokenizer.advance()
            
            # Expect '{'
            if self.tokenizer.current_token != "{":
                raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
            self.output.write(f"<symbol> {{ </symbol>\n")
            self.tokenizer.advance()
            
            # Parse statements
            self.compile_statements()
            
            # Expect '}'
            if self.tokenizer.current_token != "}":
                raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
            self.output.write(f"<symbol> }} </symbol>\n")
            self.tokenizer.advance()
        
        self.output.write("</ifStatement>\n")
                            

    def compile_expression(self) -> None:
        """Compiles an expression.
        Grammar: term (op term)*
        """
        # Check if we have content for an expression
        if self.tokenizer.current_token in [';', ']', ')', ',']:
            return
        
        self.output.write("<expression>\n")
        
        # Parse first term
        self.compile_term()
        
        # Parse (op term)* - zero or more operators followed by terms
        while (self.tokenizer.token_type() == "SYMBOL" and 
               self.tokenizer.symbol() in ["+", "-", "*", "/", "&", "|", "<", ">", "="]):
            self.output.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            self.compile_term()
        
        self.output.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term.
        Grammar: integerConstant | stringConstant | keywordConstant | varName | 
                 varName '[' expression ']' | subroutineCall | 
                 '(' expression ')' | unaryOp term
        """
        # UNCOMMENT THIS LINE:
        self.output.write("<term>\n")  # <--- Turn this back on
        
        # Handle unary operators: unaryOp term
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() in ["-", "~", "^", "#"]:
            self.output.write(f"<symbol> {self.tokenizer.symbol()} </symbol>\n")
            self.tokenizer.advance()
            # Recursively compile the term after unary operator
            self.compile_term()
            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # Handle parenthesized expression: '(' expression ')'
        if self.tokenizer.token_type() == "SYMBOL" and self.tokenizer.symbol() == "(":
            self.output.write(f"<symbol> ( </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()
            if self.tokenizer.current_token != ")":
                raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
            self.output.write(f"<symbol> ) </symbol>\n")
            self.tokenizer.advance()
            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # Handle integer constant
        if self.tokenizer.token_type() == "INT_CONST":
            self.output.write(f"<integerConstant> {self.tokenizer.int_val()} </integerConstant>\n")
            self.tokenizer.advance()
            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # Handle string constant
        if self.tokenizer.token_type() == "STRING_CONST":
            self.output.write(f"<stringConstant> {self.tokenizer.string_val()} </stringConstant>\n")
            self.tokenizer.advance()
            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # Handle keyword constant (true, false, null, this)
        if self.tokenizer.token_type() == "KEYWORD" and self.tokenizer.keyword().lower() in ["true", "false", "null", "this"]:
            self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
            self.tokenizer.advance()
            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # Handle identifier: varName, varName '[' expression ']', or subroutineCall
        if self.tokenizer.token_type() == "IDENTIFIER":
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
            
            # ... (Logic for array/subroutine calls) ...
            if self.tokenizer.current_token == "[":
                self.output.write(f"<symbol> [ </symbol>\n")
                self.tokenizer.advance()
                self.compile_expression()
                if self.tokenizer.current_token != "]":
                     raise ValueError(f"Expected ']', got {self.tokenizer.current_token}")
                self.output.write(f"<symbol> ] </symbol>\n")
                self.tokenizer.advance()
            elif self.tokenizer.current_token == "." or self.tokenizer.current_token == "(":
                 # ... (Subroutine call logic) ...
                 if self.tokenizer.current_token == ".":
                     self.output.write(f"<symbol> . </symbol>\n")
                     self.tokenizer.advance()
                     if self.tokenizer.token_type() != "IDENTIFIER":
                         raise ValueError(f"Expected subroutine name, got {self.tokenizer.current_token}")
                     self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
                     self.tokenizer.advance()
                
                 if self.tokenizer.current_token != "(":
                     raise ValueError(f"Expected '(', got {self.tokenizer.current_token}")
                 self.output.write(f"<symbol> ( </symbol>\n")
                 self.tokenizer.advance()
                
                 self.output.write("<expressionList>\n")
                 self.compile_expression_list()
                 self.output.write("</expressionList>\n")
                
                 if self.tokenizer.current_token != ")":
                     raise ValueError(f"Expected ')', got {self.tokenizer.current_token}")
                 self.output.write(f"<symbol> ) </symbol>\n")
                 self.tokenizer.advance()

            # UNCOMMENT THIS LINE:
            self.output.write("</term>\n") # <--- Turn this back on
            return
        
        # UNCOMMENT THIS LINE:
        self.output.write("</term>\n") # <--- Turn this back on
        raise ValueError(f"Expected term, got {self.tokenizer.current_token}")
    
    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions.
        Grammar: (expression (',' expression)* )?
        """
        # Check if empty
        if self.tokenizer.current_token == ")":
            return
        
        # Parse first expression
        self.compile_expression()
        
        # Parse additional expressions
        while self.tokenizer.current_token == ",":
            self.output.write(f"<symbol> , </symbol>\n")
            self.tokenizer.advance()
            self.compile_expression()

    def compile_subroutine_body(self) -> None:
        """Compiles a subroutine body.
        Grammar: '{' varDec* statements '}'
        """
        if self.tokenizer.current_token != "{":
            raise ValueError(f"Expected '{{', got {self.tokenizer.current_token}")
        
        self.output.write("<subroutineBody>\n")
        self.output.write(f"<symbol> {{ </symbol>\n")
        self.tokenizer.advance()
        
        # Parse varDec* (zero or more)
        while (self.tokenizer.token_type() == "KEYWORD" and 
               self.tokenizer.keyword() == "VAR"):
            self.compile_var_dec()
        
        # Parse statements
        self.compile_statements()
        
        # Parse '}'
        if self.tokenizer.current_token != "}":
            raise ValueError(f"Expected '}}', got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> }} </symbol>\n")
        self.tokenizer.advance()
        
        self.output.write("</subroutineBody>\n")

    def compile_subroutine_call_direct(self) -> None:
        """Compiles a subroutine call directly (without expression wrapper).
        Used by do statements.
        Grammar: subroutineName '(' expressionList ')' | 
                 (className | varName) '.' subroutineName '(' expressionList ')'
        """
        # Parse subroutineName or (className|varName)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected identifier in subroutine call, got {self.tokenizer.current_token}")
        
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Check for '.' (method call on object/class)
        if self.tokenizer.current_token == ".":
            self.output.write(f"<symbol> . </symbol>\n")
            self.tokenizer.advance()
            
            # Parse subroutineName
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected subroutine name after '.', got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        
        # Parse '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(' in subroutine call, got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # Parse expressionList
        self.output.write("<expressionList>\n")
        self.compile_expression_list()
        self.output.write("</expressionList>\n")
        
        # Parse ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')' in subroutine call, got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()

    def compile_subroutine_call(self) -> None:
        """Compiles a subroutine call.
        Grammar: subroutineName '(' expressionList ')' | 
                 (className | varName) '.' subroutineName '(' expressionList ')'
        """
        # Parse subroutineName or (className|varName)
        if self.tokenizer.token_type() != "IDENTIFIER":
            raise ValueError(f"Expected identifier in subroutine call, got {self.tokenizer.current_token}")
        
        self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
        self.tokenizer.advance()
        
        # Check for '.' (method call on object/class)
        if self.tokenizer.current_token == ".":
            self.output.write(f"<symbol> . </symbol>\n")
            self.tokenizer.advance()
            
            # Parse subroutineName
            if self.tokenizer.token_type() != "IDENTIFIER":
                raise ValueError(f"Expected subroutine name after '.', got {self.tokenizer.current_token}")
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        
        # Parse '('
        if self.tokenizer.current_token != "(":
            raise ValueError(f"Expected '(' in subroutine call, got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ( </symbol>\n")
        self.tokenizer.advance()
        
        # Parse expressionList
        self.output.write("<expressionList>\n")
        self.compile_expression_list()
        self.output.write("</expressionList>\n")
        
        # Parse ')'
        if self.tokenizer.current_token != ")":
            raise ValueError(f"Expected ')' in subroutine call, got {self.tokenizer.current_token}")
        self.output.write(f"<symbol> ) </symbol>\n")
        self.tokenizer.advance()

    def _parse_type(self) -> None:
        """Helper method to parse a type (int | char | boolean | className)."""
        if self.tokenizer.token_type() == "KEYWORD" and \
           self.tokenizer.keyword() in ["INT", "CHAR", "BOOLEAN"]:
            self.output.write(f"<keyword> {self.tokenizer.keyword().lower()} </keyword>\n")
            self.tokenizer.advance()
        elif self.tokenizer.token_type() == "IDENTIFIER":
            self.output.write(f"<identifier> {self.tokenizer.identifier()} </identifier>\n")
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected type, got {self.tokenizer.current_token}")