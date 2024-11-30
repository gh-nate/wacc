# Copyright (C) 2024 gh-nate
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import asdl
import lexer


def take_token(tokens):
    token = tokens[0]
    del tokens[0]
    return token


def expect(expected, tokens):
    actual = take_token(tokens)
    if actual != expected:
        raise ValueError(f"Syntax error: Expected '{expected}' but got '{actual}'")


def parse(tokens):
    program = parse_program(tokens)
    if tokens:
        raise RuntimeError(f"Nonempty tokens after parsing program: {tokens}")
    return program


def parse_program(tokens):
    return asdl.ProgramAST(parse_function(tokens))


def parse_function(tokens):
    expect("int", tokens)
    key, name = "identifier", take_token(tokens)
    if not lexer.token_patterns[key].match(name):
        raise ValueError(f"Syntax error: '{name}' is not a valid {key}")
    for token in ["(", "void", ")", "{"]:
        expect(token, tokens)
    body = parse_statement(tokens)
    expect("}", tokens)
    return asdl.FunctionAST(name, body)


def parse_statement(tokens):
    expect("return", tokens)
    exp = parse_exp(tokens)
    expect(";", tokens)
    return asdl.ReturnAST(exp)


def parse_exp(tokens):
    key, i = "constant", take_token(tokens)
    if not lexer.token_patterns[key].match(i):
        raise ValueError(f"Syntax error: '{i}' is not a valid {key}")
    return asdl.ConstantAST(int(i))
