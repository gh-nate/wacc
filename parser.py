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


BINARY_OPERATOR_PRECEDENCE = {
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
    "?": 3,
    "=": 1,
}


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


def parse(tokens):
    program = parse_program(tokens)
    if tokens:
        raise SyntaxError(f"Nonempty tokens after parsing program: {tokens}")
    return program


def parse_program(tokens):
    return asdl.ProgramAST(parse_function_definition(tokens))


def parse_function_definition(tokens):
    expect("int", tokens)
    key, name = lexer.TOKEN.IDENTIFIER, take_token(tokens)
    if not lexer.TOKEN_PATTERNS[key].match(name):
        raise SyntaxError(f"'{name}' is not a valid {key}")
    for token in ["(", "void", ")"]:
        expect(token, tokens)
    return asdl.FunctionAST(name, parse_block(tokens))


def parse_block(tokens):
    expect("{", tokens)
    items = []
    while tokens[0] != "}":
        items.append(parse_block_item(tokens))
    take_token(tokens)
    return asdl.BlockAST(items)


def parse_block_item(tokens):
    if tokens[0] == "int":
        return asdl.DAST(parse_declaration(tokens))
    return asdl.SAST(parse_statement(tokens))


def parse_for_init(tokens):
    if tokens[0] == "int":
        return asdl.InitDeclAST(parse_declaration(tokens))
    exp, token = None, ";"
    if tokens[0] != token:
        exp = parse_exp(tokens)
    expect(token, tokens)
    return asdl.InitExpAST(exp)


def parse_declaration(tokens):
    expect("int", tokens)
    name = take_token(tokens)
    if not lexer.TOKEN_PATTERNS[lexer.TOKEN.IDENTIFIER].match(name):
        raise SyntaxError(f"Not an identifier: {name}")
    exp = None
    if tokens[0] == "=":
        take_token(tokens)
        exp = parse_exp(tokens)
    expect(";", tokens)
    return asdl.DeclarationAST(name, exp)


def parse_statement(tokens):
    match tokens[0]:
        case "return":
            take_token(tokens)
            exp = parse_exp(tokens)
            expect(";", tokens)
            return asdl.ReturnAST(exp)
        case "if":
            take_token(tokens)
            expect("(", tokens)
            condition = parse_exp(tokens)
            expect(")", tokens)
            then = parse_statement(tokens)
            else_ = None
            if tokens[0] == "else":
                take_token(tokens)
                else_ = parse_statement(tokens)
            return asdl.IfAST(condition, then, else_)
        case "{":
            return asdl.CompoundAST(parse_block(tokens))
        case "break":
            take_token(tokens)
            expect(";", tokens)
            return asdl.BreakAST("")
        case "continue":
            take_token(tokens)
            expect(";", tokens)
            return asdl.ContinueAST("")
        case "while":
            take_token(tokens)
            expect("(", tokens)
            condition = parse_exp(tokens)
            expect(")", tokens)
            body = parse_statement(tokens)
            return asdl.WhileAST(condition, body, "")
        case "do":
            take_token(tokens)
            body = parse_statement(tokens)
            for token in ["while", "("]:
                expect(token, tokens)
            condition = parse_exp(tokens)
            for token in [")", ";"]:
                expect(token, tokens)
            return asdl.DoWhileAST(body, condition, "")
        case "for":
            take_token(tokens)
            expect("(", tokens)
            init = parse_for_init(tokens)
            condition, token = None, ";"
            if tokens[0] != token:
                condition = parse_exp(tokens)
            expect(token, tokens)
            post, token = None, ")"
            if tokens[0] != token:
                post = parse_exp(tokens)
            expect(token, tokens)
            body = parse_statement(tokens)
            return asdl.ForAST(init, condition, post, body, "")
        case ";":
            take_token(tokens)
            return asdl.NullAST()
        case _:
            exp = parse_exp(tokens)
            expect(";", tokens)
            return asdl.ExpressionAST(exp)


def parse_factor(tokens):
    next_token = tokens[0]
    if lexer.TOKEN_PATTERNS[lexer.TOKEN.CONSTANT].match(next_token):
        take_token(tokens)
        return asdl.ConstantAST(int(next_token))
    elif lexer.TOKEN_PATTERNS[lexer.TOKEN.IDENTIFIER].match(next_token):
        for keyword in [
            lexer.TOKEN.INT_KEYWORD,
            lexer.TOKEN.VOID_KEYWORD,
            lexer.TOKEN.RETURN_KEYWORD,
            lexer.TOKEN.IF_KEYWORD,
            lexer.TOKEN.ELSE_KEYWORD,
            lexer.TOKEN.DO_KEYWORD,
            lexer.TOKEN.WHILE_KEYWORD,
            lexer.TOKEN.FOR_KEYWORD,
            lexer.TOKEN.BREAK_KEYWORD,
            lexer.TOKEN.CONTINUE_KEYWORD,
        ]:
            if lexer.TOKEN_PATTERNS[keyword].match(next_token):
                raise SyntaxError(f"{next_token} is a keyword and not an identifier")
        take_token(tokens)
        return asdl.VarAST(next_token)
    elif next_token in ["~", "-", "!"]:
        return asdl.UnaryAST(
            parse_unop(tokens),
            parse_factor(tokens),
        )
    elif next_token == "(":
        take_token(tokens)
        inner_exp = parse_exp(tokens)
        expect(")", tokens)
        return inner_exp
    else:
        raise SyntaxError(f"Malformed expression: {next_token}")


def parse_exp(tokens, min_prec=0):
    left = parse_factor(tokens)
    next_token = tokens[0]
    while (
        next_token in BINARY_OPERATOR_PRECEDENCE
        and BINARY_OPERATOR_PRECEDENCE[next_token] >= min_prec
    ):
        match next_token:
            case "=":
                take_token(tokens)
                right = parse_exp(tokens, BINARY_OPERATOR_PRECEDENCE[next_token])
                left = asdl.AssignmentAST(left, right)
            case "?":
                middle = parse_conditional_middle(tokens)
                right = parse_exp(tokens, BINARY_OPERATOR_PRECEDENCE[next_token])
                left = asdl.ConditionalAST(left, middle, right)
            case _:
                operator = parse_binop(tokens)
                right = parse_exp(tokens, BINARY_OPERATOR_PRECEDENCE[next_token] + 1)
                left = asdl.BinaryAST(operator, left, right)
        next_token = tokens[0]
    return left


def parse_conditional_middle(tokens):
    expect("?", tokens)
    condition = parse_exp(tokens)
    expect(":", tokens)
    return condition


def parse_unop(tokens):
    match token := take_token(tokens):
        case "-":
            return asdl.UnaryOperatorAST.NEGATE
        case "~":
            return asdl.UnaryOperatorAST.COMPLEMENT
        case "!":
            return asdl.UnaryOperatorAST.NOT
        case _:
            raise SyntaxError(f"Unknown unary operator: {token}")


def parse_binop(tokens):
    match token := take_token(tokens):
        case "-":
            return asdl.BinaryOperatorAST.SUBTRACT
        case "+":
            return asdl.BinaryOperatorAST.ADD
        case "*":
            return asdl.BinaryOperatorAST.MULTIPLY
        case "/":
            return asdl.BinaryOperatorAST.DIVIDE
        case "%":
            return asdl.BinaryOperatorAST.REMAINDER
        case "<":
            return asdl.BinaryOperatorAST.LESS_THAN
        case "<=":
            return asdl.BinaryOperatorAST.LESS_OR_EQUAL
        case ">":
            return asdl.BinaryOperatorAST.GREATER_THAN
        case ">=":
            return asdl.BinaryOperatorAST.GREATER_OR_EQUAL
        case "==":
            return asdl.BinaryOperatorAST.EQUAL
        case "!=":
            return asdl.BinaryOperatorAST.NOT_EQUAL
        case "&&":
            return asdl.BinaryOperatorAST.AND
        case "||":
            return asdl.BinaryOperatorAST.OR
        case "=":
            return asdl.BinaryOperatorAST.VAR_ASSIGN
        case _:
            raise SyntaxError(f"Unknown binary operator: {token}")
