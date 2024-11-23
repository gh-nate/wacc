# Copyright (c) 2024 gh-nate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asdl
import lexer


def take_token(tokens: list[str]) -> str:
    index = 0
    result = tokens[index]
    del tokens[index]
    return result


def expect(expected: str, tokens: list[str]) -> None:
    actual = take_token(tokens)
    if actual != expected:
        raise ValueError(f"Syntax error: Expected '{expected}' but got '{actual}'.")


def parse_program(tokens: list[str]) -> asdl.ProgramAstNode:
    result = asdl.ProgramAstNode(parse_function(tokens))
    if tokens:
        raise RuntimeError(f"Syntax error: Nonempty tokens after parsing: {tokens}")
    return result


def parse_function(tokens: list[str]) -> asdl.FunctionAstNode:
    expect("int", tokens)
    identifier = parse_identifier(tokens)
    for expected in ["(", "void", ")", "{"]:
        expect(expected, tokens)
    statement = parse_statement(tokens)
    expect("}", tokens)
    return asdl.FunctionAstNode(identifier, statement)


def parse_statement(tokens: list[str]) -> asdl.ReturnAstNode:
    expect("return", tokens)
    return_val = parse_exp(tokens)
    expect(";", tokens)
    return asdl.ReturnAstNode(return_val)


def parse_exp(tokens: list[str]) -> asdl.ConstantAstNode:
    return parse_int(tokens)


def parse_identifier(tokens: list[str]) -> asdl.Identifier:
    actual = take_token(tokens)
    if not lexer.patterns[0].match(actual):
        raise ValueError(f"Syntax error: Invalid identifier '{actual}'")
    return asdl.Identifier(actual)


def parse_int(tokens: list[str]) -> asdl.ConstantAstNode:
    return asdl.ConstantAstNode(int(take_token(tokens)))
