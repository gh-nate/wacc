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


class SyntaxError(Exception):
    pass


def take_token(tokens):
    token = tokens[0]
    del tokens[0]
    return token


def expect(expected, tokens):
    actual = take_token(tokens)
    if actual != expected:
        raise SyntaxError(f"Expected '{expected}' but got '{actual}'")


def peek(tokens):
    return tokens[0]


def parse(tokens):
    program = parse_program(tokens)
    if tokens:
        raise SyntaxError(f"Nonempty tokens after parsing program: {tokens}")
    return program


def parse_program(tokens):
    return asdl.ProgramAST(parse_function(tokens))


def parse_function(tokens):
    expect("int", tokens)
    key, name = lexer.TOKEN.IDENTIFIER, take_token(tokens)
    if not lexer.TOKEN_PATTERNS[key].match(name):
        raise SyntaxError(f"'{name}' is not a valid {key}")
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
    key, next_token = lexer.TOKEN.CONSTANT, peek(tokens)
    if lexer.TOKEN_PATTERNS[key].match(next_token):
        return asdl.ConstantAST(int(take_token(tokens)))
    elif next_token in ["~", "-"]:
        return asdl.UnaryAST(parse_unop(tokens), parse_exp(tokens))
    elif next_token == "(":
        take_token(tokens)
        inner_exp = parse_exp(tokens)
        expect(")", tokens)
        return inner_exp
    raise SyntaxError(f"Malformed expression: {next_token}")


def parse_unop(tokens):
    match token := take_token(tokens):
        case "~":
            return asdl.UnaryOperatorAST.COMPLEMENT
        case "-":
            return asdl.UnaryOperatorAST.NEGATE
        case _:
            raise SyntaxError(f"Unknown unary operator: '{token}'")
