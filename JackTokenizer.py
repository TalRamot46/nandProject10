"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re
KEYWORD = "KEYWORD"
SYMBOL = "SYMBOL"
INT_CONST = "INT_CONST"
STRING_CONST = "STRING_CONST"
IDENTIFIER = "IDENTIFIER"


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
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
        input_lines = input_stream.read().splitlines()
        self.token_list = self.get_words_from_code_script_filtered(input_lines)
        self._current_token_index: int = 0
        if self.token_list:
            self._current_token: str = self.token_list[self._current_token_index]

    def get_cleaned_code_string(self, input_lines):
        """
        Helper method to process an array of strings to remove all comments
        and empty lines, returning a single concatenated string of the cleaned code.
        This step is necessary before tokenization to properly handle multi-line strings.

        Args:
            input_lines: An array (list) of strings, where each string is a line of code.

        Returns:
            A single string containing the cleaned code.
        """
        cleaned_parts = []
        in_multi_line_comment = False

        for line in input_lines:
            line_content = line.strip()

            if not line_content:
                continue # Skip truly empty lines

            # --- Handle Multi-line Comments that span lines ---
            if in_multi_line_comment:
                end_comment_match = re.search(r'\*/', line_content)
                if end_comment_match:
                    # Comment ends on this line, process the rest of the line
                    line_content = line_content[end_comment_match.end():]
                    in_multi_line_comment = False
                else:
                    continue # Still inside a multi-line comment, skip the whole line

            # --- Handle Multi-line Comments that start (and potentially end) on this line ---
            start_comment_match = re.search(r'/\*|\/\*\*', line_content)
            if start_comment_match:
                # Check for an inline end comment AFTER the start
                remaining_line_after_start = line_content[start_comment_match.end():]
                end_comment_match_inline = re.search(r'\*/', remaining_line_after_start)

                if end_comment_match_inline:
                    # Comment starts and ends on the same line
                    part_before_comment = line_content[:start_comment_match.start()]
                    part_after_comment = remaining_line_after_start[end_comment_match_inline.end():]
                    line_content = part_before_comment + part_after_comment
                else:
                    # Multi-line comment begins here and continues to next line
                    line_content = line_content[:start_comment_match.start()] # Keep only part before comment
                    in_multi_line_comment = True # Set flag for subsequent lines

            # --- Handle Single-line Comments (//) ---
            # IMPORTANT LIMITATION: This simplified approach will remove `//` even if
            # it's inside a string literal (e.g., "http://example.com").
            # A full lexer would be required for perfect handling of `//` inside strings.
            single_line_comment_match = re.search(r'//', line_content)
            if single_line_comment_match:
                line_content = line_content[:single_line_comment_match.start()]

            line_content = line_content.strip() # Re-strip after comment removal
            if line_content:
                cleaned_parts.append(line_content)

        # Join the cleaned parts with a space. This allows multi-line string literals
        # to be treated as a single continuous string for the next regex pass.
        # It also serves as a general separator between tokens that were on different lines.
        return " ".join(cleaned_parts)


    def get_words_from_code_script_filtered(self, input_lines):
        """
        Processes an array of strings (code lines) and returns a list of "words" in it.
        It first cleans the code by removing comments and empty lines, then tokenizes it.

        Args:
            input_lines: An array (list) of strings, where each string is a line of code.

        Returns:
            A list of strings, where each string is a word or symbol from the script.
        """
        # Step 1: Get a single string of code with comments and empty lines removed.
        cleaned_code = self.get_cleaned_code_string(input_lines) # Renamed method call

        # Step 2: Define a comprehensive regex pattern for tokenization.
        # The order of patterns is crucial: more specific/longer matches should come first.
        #
        # 1. Double-quoted strings:
        #    \"(?:[^\"\\]|\\.)*\"
        # 2. Numbers (positive, will be combined with standalone '-' for negative semantics):
        #    \d+(?:\.\d+)?
        # 3. Alphanumeric words (includes underscores):
        #    \w+
        # 4. Standalone dash:
        #    -
        # 5. Any other single non-whitespace character:
        #    \S
        item_pattern = re.compile(
            r'\"(?:[^\"\\]|\\.)*\"'  # 1. Double-quoted strings (must be first)
            r'|'                     # OR
            r'\d+(?:\.\d+)?'         # 2. Numbers (e.g., '2', '3.14')
            r'|'                     # OR
            r'\w+'                   # 3. Alphanumeric words
            r'|'                     # OR
            r'-'                     # 4. Standalone dash (e.g., for '5 - 3' or from '-2')
            r'|'                     # OR
            r'\S'                    # 5. Any other single non-whitespace character (e.g., '+', '=', ';')
        )

        # Step 3: Find all matches in the cleaned code string.
        words_and_symbols = item_pattern.findall(cleaned_code)

        return words_and_symbols
    
    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self._current_token_index < len(self.token_list)

    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self._current_token_index += 1
        if self.has_more_tokens():
            self._current_token = self.token_list[self._current_token_index]

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        keyword_list = ["CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"]
        if self._current_token.upper() in keyword_list:
            return KEYWORD
        
        symbol_list = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        if self._current_token in symbol_list:
            return SYMBOL
        
        if self.is_valid_identifier(self._current_token):
            return IDENTIFIER
        
        if self.is_valid_integer(self._current_token):
            return INT_CONST
        
        if self._current_token.startswith('\"') and self._current_token.endswith('\"'):
            return STRING_CONST
        
    def token_type_translated(self) -> str:
        """returns the token type at the same format of the xml file.
        for example "INT_CONST" changes to "integerConstant"

        Returns:
            str: The token type as it appears on the xml file.
        """
        translation_dict = {
            KEYWORD: "keyword",
            SYMBOL: "symbol",
            IDENTIFIER: "identifier",
            INT_CONST: "integerConstant",
            STRING_CONST: "stringConstant"
        }
        return translation_dict[self.token_type()]
    
    def current_token_val(self) -> str:
        """Returns the token after its type had been determined,
        used primarily for deleting the double-quotes from stringConstants
        and handling the symbols <,> and &.

        Returns:
            str: The current token.
        """
        cur_type = self.token_type()
        if cur_type == KEYWORD:
            return self.keyword()
        if cur_type == SYMBOL:
            return self.symbol()
        if cur_type == INT_CONST:
            return self.int_val()
        if cur_type == STRING_CONST:
            return self.string_val()
        if cur_type == IDENTIFIER:
            return self.identifier()

    
    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self._current_token.lower()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self._current_token == '<': return '&lt'
        if self._current_token == '>': return '&gt'
        if self._current_token == '&': return '&amp'
        return self._current_token

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
        return self._current_token
    
    def is_valid_identifier(self, s: str) -> bool:
        """
        Checks if a string is a sequence of letters, digits, and underscores ('_'),
        and does not start with a digit. This is a common pattern for valid identifiers
        in many programming languages (like Python, C, Java variable names).

        Args:
            s: The input string to check.

        Returns:
            True if the string meets the criteria, False otherwise.
        """
        if not isinstance(s, str):
            # Handle non-string input gracefully, or raise an error
            return False

        # An empty string is not a valid identifier
        if not s:
            return False

        # Regex breakdown:
        # ^       : Start of the string
        # [a-zA-Z_] : The first character must be a letter (a-z, A-Z) or an underscore.
        # \w* : The rest of the string can be zero or more word characters (letters, digits, or underscores).
        # $       : End of the string
        pattern = re.compile(r'^[a-zA-Z_]\w*$')

        return bool(pattern.match(s))

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self._current_token)
    
    def is_valid_integer(self, s: str) -> bool:
        """
        Checks if a string represents an integer within the inclusive range of 0 to 32767.

        Args:
            s: The input string to check.

        Returns:
            True if the string represents an integer in the specified range, False otherwise.
        """
        # 1. Ensure the input is a string
        if not isinstance(s, str):
            return False

        # 2. Attempt to convert the string to an integer
        try:
            num = int(s)
        except ValueError:
            # If conversion fails (e.g., "abc", "1.5", "-"), it's not a valid integer string
            return False

        # 3. Check if the integer falls within the specified range [0, 32767]
        return 0 <= num <= 32767

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self._current_token[1:-1]