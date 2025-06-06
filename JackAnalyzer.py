"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from JackTokenizer import JackTokenizer
import xml.etree.ElementTree as ET


def analyze_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Analyzes a single file.

    Args:
        input_file (typing.TextIO): the file to analyze.
        output_file (typing.TextIO): writes all output to this file.
    """
    # Your code goes here!
    # It might be good to start by creating a new JackTokenizer and CompilationEngine:
    # tokenizer = JackTokenizer(input_file)
    # engine = CompilationEngine(tokenizer, output_file)

def create_token_file(
    input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """creates a token file using the JackTokenizer module.

    Args:
        input_file (typing.TextIO): the file to analyze.
        output_file (typing.TextIO): writes all output to this file.
    """
    root = ET.Element("tokens")
    tokenizer = JackTokenizer(input_file)
    while tokenizer.has_more_tokens():
        tokenElement = ET.SubElement(root, tokenizer.token_type_translated())
        tokenElement.text = " " + str(tokenizer.current_token_val()) + " "
        tokenizer.advance()
    try:
        xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=False)
        xml_string = xml_bytes.decode("utf-8")
        output_file.write(xml_string)
    except Exception as e:
        print(f"Error writing XML content to TextIO object: {e}")



def main_only_tokens():
        # Parses the input path and calls analyze_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename = os.path.basename(input_path).split('.')[0]
        _, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        input_dir = os.path.dirname(input_path)
        # creating a new directory for our result xml file
        compare_folder = input_dir + "\\Compare"
        if not os.path.exists(compare_folder):
            os.makedirs(compare_folder)
        output_path = compare_folder + "\\" + filename + "T.xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            create_token_file(input_file, output_file)

def main_analyzing() -> None:
    # Parses the input path and calls analyze_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            analyze_file(input_file, output_file)


if "__main__" == __name__:
    # commenting out our second main function used
    # for the sake of unit-testing the JackTokenizer module. 
    main_only_tokens()
    # main_analyzing()

