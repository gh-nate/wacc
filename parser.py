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


def peek(tokens):
    return tokens[0]


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


precedence = {
    "*": 50,
    "/": 50,
    "%": 50,
    "+": 45,
    "-": 45,
    "<": 35,
    "<=": 35,
    ">": 35,
    ">=": 35,
    "==": 30,
    "!=": 30,
    "&&": 10,
    "||": 5,
}


def parse_exp(tokens, min_prec=0):
    left = parse_factor(tokens)
    next_token = peek(tokens)
    while next_token in precedence and precedence[next_token] >= min_prec:
        operator = parse_binop(tokens)
        right = parse_exp(tokens, precedence[next_token] + 1)
        left = asdl.BinaryAST(operator, left, right)
        next_token = peek(tokens)
    return left


def parse_factor(tokens):
    key, next_token = "constant", peek(tokens)
    if lexer.token_patterns[key].match(next_token):
        take_token(tokens)
        return asdl.ConstantAST(int(next_token))
    elif next_token in ["~", "-", "!"]:
        operator = parse_unop(tokens)
        inner_exp = parse_factor(tokens)
        return asdl.UnaryAST(operator, inner_exp)
    elif next_token == "(":
        take_token(tokens)
        inner_exp = parse_exp(tokens)
        expect(")", tokens)
        return inner_exp
    else:
        raise ValueError(f"Syntax error: Malformed factor: {tokens}")


def parse_unop(tokens):
    match token := take_token(tokens):
        case "~":
            return asdl.ComplementAST()
        case "-":
            return asdl.NegateAST()
        case "!":
            return asdl.NotAST()
        case _:
            raise ValueError(f"Syntax error: Unknown unary operator '{token}'")


def parse_binop(tokens):
    match token := take_token(tokens):
        case "-":
            return asdl.SubtractAST()
        case "+":
            return asdl.AddAST()
        case "*":
            return asdl.MultiplyAST()
        case "/":
            return asdl.DivideAST()
        case "%":
            return asdl.RemainderAST()
        case "&&":
            return asdl.AndAST()
        case "||":
            return asdl.OrAST()
        case "==":
            return asdl.EqualAST()
        case "!=":
            return asdl.NotEqualAST()
        case "<":
            return asdl.LessThanAST()
        case "<=":
            return asdl.LessOrEqualAST()
        case ">":
            return asdl.GreaterThanAST()
        case ">=":
            return asdl.GreaterOrEqualAST()
        case _:
            raise ValueError(f"Syntax error: Unknown binary operator '{token}'")
