"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

from JackTokenizer import JackTokenizer, KEYWORD, SYMBOL, INT_CONST, STRING_CONST, IDENTIFIER
import xml.etree.ElementTree as ET
from xml.dom import minidom
from io import StringIO


class CompilationError(Exception):
    pass

class Compilationengine:
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
        self.tknzr = input_stream
        self.output_stream = output_stream
        self.current_xml_parent: ET.Element = None

    def run(self):
        classRoot = self.compile_class()

        def add_spaces_to_texts(elem, level=0):
            if elem.text != None and str(elem.text).strip() != None:
                elem.text = f" {str(elem.text)} "
            elif len(elem) == 0:
                elem.text = "\n"  + ("  " * level) # Fix: match opening tag level
            for child in elem:
                add_spaces_to_texts(child, level + 1)

        add_spaces_to_texts(classRoot)

        rough_string = ET.tostring(classRoot, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        pretty_xml_lines = pretty_xml.split('\n')
        for i in range(len(pretty_xml_lines)):
            line = pretty_xml_lines[i]
            if "&amp;lt" in line:
                pretty_xml_lines[i] = pretty_xml_lines[i].replace('&amp;lt', '&lt;')
            if "&amp;gt" in line:
                pretty_xml_lines[i] = pretty_xml_lines[i].replace('&amp;gt', '&gt;')
            if "&amp;amp" in line:
                pretty_xml_lines[i] = pretty_xml_lines[i].replace('&amp;amp', '&amp;')


        if pretty_xml_lines[0].startswith('<?xml'):
            pretty_xml = '\n'.join(pretty_xml_lines[1:]).strip()
        pretty_xml += '\n'

        self.output_stream.write(pretty_xml)



    ###################################################################################################################################################
    #   Program Control
    ###################################################################################################################################################
    def compile_class(self) -> ET.Element:
        """Compiles a complete class.
        
        Returns:
            ET.Element: The root of the xml file.
        """
        class_root = ET.Element("class")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = class_root

        # class keyword
        self.add_token_to_xml(KEYWORD, "class")

        # className
        self.add_token_to_xml(IDENTIFIER)

        # '{'
        self.add_token_to_xml(SYMBOL, "{")

        # classVarDec* (zero or more class variable declarations)
        while self.tknzr._current_token in ("static", "field"):
            self.compile_class_var_dec()

        # subroutineDec* (zero or more subroutine declarations)
        while self.tknzr._current_token in ("constructor", "function", "method"):
            self.compile_subroutine()

        # '}'
        self.add_token_to_xml(SYMBOL, "}")

        # restore parent
        self.current_xml_parent = prev_parent
        return class_root


    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        var_dec = ET.SubElement(self.current_xml_parent, "classVarDec")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = var_dec

        # 'static' or 'field'
        self.add_token_to_xml(KEYWORD)

        # type: 'int' | 'char' | 'boolean' | className
        if self.tknzr.token_type() == KEYWORD:
            self.add_token_to_xml(KEYWORD)  # int, char, boolean
        elif self.tknzr.token_type() == IDENTIFIER:
            self.add_token_to_xml(IDENTIFIER)  # className

        # varName
        self.add_token_to_xml(IDENTIFIER)

        # 0 or more (',' varName)
        while self.tknzr._current_token == ",":
            self.add_token_to_xml(SYMBOL, ",")
            self.add_token_to_xml(IDENTIFIER)

        # ';'
        self.add_token_to_xml(SYMBOL, ";")

        # restore parent
        self.current_xml_parent = prev_parent


    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        subroutine_el = ET.SubElement(self.current_xml_parent, "subroutineDec")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = subroutine_el

        # 'constructor' | 'function' | 'method'
        self.add_token_to_xml(KEYWORD)

        # 'void' | type (int, char, boolean, or className)
        if self.tknzr.token_type() == KEYWORD:
            self.add_token_to_xml(KEYWORD)
        else:
            self.add_token_to_xml(IDENTIFIER)

        # subroutineName
        self.add_token_to_xml(IDENTIFIER)

        # '('
        self.add_token_to_xml(SYMBOL, '(')

        # parameterList
        self.compile_parameter_list()

        # ')'
        self.add_token_to_xml(SYMBOL, ')')

        # subroutineBody
        body_el = ET.SubElement(self.current_xml_parent, "subroutineBody")
        prev_body_el = self.current_xml_parent
        self.current_xml_parent = body_el

        # '{'
        self.add_token_to_xml(SYMBOL, '{')

        # var declerations
        while self.tknzr._current_token == "var":
            self.compile_var_dec()

        # statements
        self.compile_statements()

        # '}'
        self.add_token_to_xml(SYMBOL, '}')

        # restore parent
        self.current_xml_parent = prev_body_el
        self.current_xml_parent = prev_parent


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        param_list_el = ET.SubElement(self.current_xml_parent, "parameterList")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = param_list_el

        # Empty parameter list
        if self.tknzr._current_token == ')':
            # Force newline text so minidom adds line breaks
            self.current_xml_parent = prev_parent
            return

        # At least one parameter: type varName
        if self.tknzr.token_type() == KEYWORD:
            self.add_token_to_xml(KEYWORD)
        else:
            self.add_token_to_xml(IDENTIFIER)

        self.add_token_to_xml(IDENTIFIER)

        # Additional parameters
        while self.tknzr._current_token == ',':
            self.add_token_to_xml(SYMBOL, ',')
            if self.tknzr.token_type() == KEYWORD:
                self.add_token_to_xml(KEYWORD)
            else:
                self.add_token_to_xml(IDENTIFIER)
            self.add_token_to_xml(IDENTIFIER)

        self.current_xml_parent = prev_parent




    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        var_dec_el = ET.SubElement(self.current_xml_parent, "varDec")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = var_dec_el

        # 'var'
        self.add_token_to_xml(KEYWORD, "var")

        # type (int, char, boolean, or className)
        if self.tknzr.token_type() == KEYWORD:
            self.add_token_to_xml(KEYWORD)
        else:
            self.add_token_to_xml(IDENTIFIER)  # className

        # varName
        self.add_token_to_xml(IDENTIFIER)

        # (',' varName)*
        while self.tknzr._current_token == ",":
            self.add_token_to_xml(SYMBOL, ",")
            self.add_token_to_xml(IDENTIFIER)

        # ';'
        self.add_token_to_xml(SYMBOL, ";")

        self.current_xml_parent = prev_parent


    def compile_statements(self) -> None:
        """Compiles a sequence of statements."""
        statements_el = ET.SubElement(self.current_xml_parent, "statements")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = statements_el

        while self.tknzr.token_type() == KEYWORD and \
                self.tknzr._current_token in ['let', 'if', 'while', 'do', 'return']:

            token = self.tknzr._current_token
            if token == 'let':
                self.compile_let()
            elif token == 'if':
                self.compile_if()
            elif token == 'while':
                self.compile_while()
            elif token == 'do':
                self.compile_do()
            elif token == 'return':
                self.compile_return()

        self.current_xml_parent = prev_parent


    ###################################################################################################################################################
    #   A statement
    ###################################################################################################################################################

    def compile_do(self) -> None:
        """Compiles a do statement."""
        do_el = ET.SubElement(self.current_xml_parent, "doStatement")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = do_el

        self.add_token_to_xml(KEYWORD, 'do')
        self.add_token_to_xml(IDENTIFIER)  # subroutineName or class/var

        if self.tknzr._current_token == ".":
            self.add_token_to_xml(SYMBOL, '.')
            self.add_token_to_xml(IDENTIFIER)  # subroutineName

        self.add_token_to_xml(SYMBOL, '(')
        self.compile_expression_list()
        self.add_token_to_xml(SYMBOL, ')')
        self.add_token_to_xml(SYMBOL, ';')

        self.current_xml_parent = prev_parent


    def compile_let(self) -> None:
        """Compiles a let statement."""
        let_el = ET.SubElement(self.current_xml_parent, "letStatement")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = let_el

        self.add_token_to_xml(KEYWORD, 'let')
        self.add_token_to_xml(IDENTIFIER)  # varName

        #array
        if self.tknzr._current_token == '[':
            self.add_token_to_xml(SYMBOL, '[')
            self.compile_expression()
            self.add_token_to_xml(SYMBOL, ']')

        self.add_token_to_xml(SYMBOL, '=')
        self.compile_expression()
        self.add_token_to_xml(SYMBOL, ';')

        self.current_xml_parent = prev_parent


    def compile_while(self) -> None:
        """Compiles a while statement."""
        while_el = ET.SubElement(self.current_xml_parent, "whileStatement")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = while_el

        self.add_token_to_xml(KEYWORD, 'while')
        self.add_token_to_xml(SYMBOL, '(')
        self.compile_expression()
        self.add_token_to_xml(SYMBOL, ')')
        self.add_token_to_xml(SYMBOL, '{')
        self.compile_statements()
        self.add_token_to_xml(SYMBOL, '}')

        self.current_xml_parent = prev_parent


    def compile_return(self) -> None:
        """Compiles a return statement."""
        return_el = ET.SubElement(self.current_xml_parent, "returnStatement")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = return_el

        self.add_token_to_xml(KEYWORD, 'return')

        if not (self.tknzr.token_type() == SYMBOL and self.tknzr._current_token == ';'):
            self.compile_expression()

        self.add_token_to_xml(SYMBOL, ';')

        self.current_xml_parent = prev_parent


    def compile_if(self) -> None:
        """Compiles an if statement, possibly with a trailing else clause."""
        if_el = ET.SubElement(self.current_xml_parent, "ifStatement")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = if_el

        self.add_token_to_xml(KEYWORD, 'if')
        self.add_token_to_xml(SYMBOL, '(')
        self.compile_expression()
        self.add_token_to_xml(SYMBOL, ')')
        self.add_token_to_xml(SYMBOL, '{')
        self.compile_statements()
        self.add_token_to_xml(SYMBOL, '}')

        if self.tknzr.token_type() == KEYWORD and self.tknzr._current_token == 'else':
            self.add_token_to_xml(KEYWORD, 'else')
            self.add_token_to_xml(SYMBOL, '{')
            self.compile_statements()
            self.add_token_to_xml(SYMBOL, '}')

        self.current_xml_parent = prev_parent


    ###################################################################################################################################################
    #   Expressions
    ###################################################################################################################################################
    
    def compile_term(self) -> None:
        """Compiles a term."""
        term_element = ET.SubElement(self.current_xml_parent, "term")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = term_element

        token_type = self.tknzr.token_type()
        token = self.tknzr.current_token_val()

        # Case 0: Unary operator (~ or -)
        if token in ['~', '-']:
            self.add_token_to_xml(SYMBOL)  # Add unary operator
            self.compile_term()            # Recursively compile the next term

        # Case 1: Integer, string, keyword constant
        elif token_type in [INT_CONST, STRING_CONST, KEYWORD] and token_type != IDENTIFIER:
            self.add_token_to_xml(token_type)

        # Case 2: Parenthesized expression
        elif token == '(':
            self.add_token_to_xml(SYMBOL, '(')
            self.compile_expression()
            self.add_token_to_xml(SYMBOL, ')')

        # Case 3: Identifier - var, array, or subroutine call
        elif token_type == IDENTIFIER:
            self.add_token_to_xml(IDENTIFIER)

            if self.tknzr._current_token == '[':
                self.add_token_to_xml(SYMBOL, '[')
                self.compile_expression()
                self.add_token_to_xml(SYMBOL, ']')

            elif self.tknzr._current_token == '(':
                self.add_token_to_xml(SYMBOL, '(')
                self.compile_expression_list()
                self.add_token_to_xml(SYMBOL, ')')

            elif self.tknzr._current_token == '.':
                self.add_token_to_xml(SYMBOL, '.')
                self.add_token_to_xml(IDENTIFIER)
                self.add_token_to_xml(SYMBOL, '(')
                self.compile_expression_list()
                self.add_token_to_xml(SYMBOL, ')')

        self.current_xml_parent = prev_parent

    def compile_expression(self) -> None:
        """Compiles an expression."""
        expr_element = ET.SubElement(self.current_xml_parent, "expression")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = expr_element

        # Always start with a term
        self.compile_term()

        # Binary operators only
        while self.tknzr._current_token in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            if self.tknzr._current_token == '&':
                pass
            self.add_token_to_xml(SYMBOL)  # the operator
            self.compile_term()

        self.current_xml_parent = prev_parent


    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Create <expressionList> XML node
        expr_list_element = ET.SubElement(self.current_xml_parent, "expressionList")
        prev_parent = self.current_xml_parent
        self.current_xml_parent = expr_list_element

        # Check if the list is non-empty
        if self.tknzr._current_token != ')':
            self.compile_expression()
            # If there are more expressions, separated by commas
            while self.tknzr._current_token == ',':
                self.add_token_to_xml(SYMBOL, ',')
                self.compile_expression()

        self.current_xml_parent = prev_parent


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
        if self.tknzr.token_type() == expected_type and \
        (expected_value is None or self.tknzr._current_token == expected_value):
    
            token_element = ET.SubElement(self.current_xml_parent, self.tknzr.token_type_translated())
            token_element.text = self.tknzr.current_token_val()
            self.tknzr.advance()
        else:
            raise CompilationError(f"Mismatched token: Expected {expected_type}/{expected_value}, got {self.tknzr.token_type()}/{self.tknzr.current_token_val()}")

