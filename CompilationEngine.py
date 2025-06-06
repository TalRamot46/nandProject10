"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackAnalyzer import ET
from JackTokenizer import JackTokenizer, KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER

class CompilationError(Exception):
    pass

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: 'JackTokenizer', output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        self.tknzr = input_stream
        self.current_xml_parent: ET.Element = None
        try:
            classRoot: ET.Element = self.compile_class()
        except CompilationError as e:
            print(str(e))
            exit()
        try:
            xml_bytes = ET.tostring(classRoot, encoding="utf-8", xml_declaration=False)
            xml_string = xml_bytes.decode("utf-8")
            output_stream.write(xml_string)
        except Exception as e:
            print(f"Error writing XML content to TextIO object: {e}")

        # output_stream.write("Hello world! \n")
        pass

    ###################################################################################################################################################
    #   Program Control
    ###################################################################################################################################################
    def compile_class(self) -> ET.Element:
        """Compiles a complete class.
        
        Returns:
            ET.Element: The root of the xml file.
        """
        classRoot = ET.Element("class")
        self.current_xml_parent = classRoot
        # ...
        return classRoot

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # Your code goes here!
        pass

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        # Your code goes here!
        pass

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        # Your code goes here!
        pass

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # Your code goes here!
        pass

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # Your code goes here!
        pass

    ###################################################################################################################################################
    #   A statement
    ###################################################################################################################################################

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        pass

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        pass

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.current_root = ET.Element("whileStatement")
        self.add_token_to_xml(KEYWORD, 'while')
        self.add_token_to_xml(SYMBOL, '(')
        self.compile_expression()
        self.add_token_to_xml(SYMBOL,')')
        self.add_token_to_xml(SYMBOL, '{')
        self.compile_statements()
        self.add_token_to_xml(SYMBOL, '}')


    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        pass

    ###################################################################################################################################################
    #   Expressions
    ###################################################################################################################################################
    
    def compile_expression(self) -> None:
        """Compiles an expression."""
        # Your code goes here!
        pass

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass

    ###################################################################################################################################################
    #   Helper Methods
    ###################################################################################################################################################

    def add_token_to_xml(self, expected_type: str, expected_value: str = None) -> None:
        """This checks the token and then adds it.
        So called "eat" method.

        Args:
            expected_type (str): expected_type.
            expected_value (str, optional): expected_value. Defaults to None.

        Raises:
            CompilationError: Mismatched token (as far as grammar).
        """
        if self.tknzr.token_type_translated() == expected_type and \
        (expected_value is None or self.tknzr._current_token == expected_value):
    
            token_element = ET.SubElement(self.current_xml_parent, self.tknzr.token_type_translated())
            token_element.text = self.tknzr.current_token_val()
            self.tknzr.advance()
            if not self.tknzr.has_more_tokens():
                raise CompilationError("File ended with a gramatically wrong token.")
        else:
            raise CompilationError(f"Mismatched token: Expected {expected_type}/{expected_value}, got {self.tknzr.token_type_translated()}/{self.tknzr._current_token}")

