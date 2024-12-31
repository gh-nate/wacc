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


def _mk_tmp(name):
    count = 0
    while True:
        yield f"{name}.{count}"
        count += 1


make_temporary = next


class ResolutionError(Exception):
    pass


def analyze(tree):
    variable_resolution(tree.function_definition.body)


def variable_resolution(body):
    variable_map = {}
    for block_item in body:
        resolve_block_item(block_item, variable_map)


def resolve_block_item(block_item, variable_map):
    match block_item:
        case asdl.SAST(statement):
            resolve_statement(statement, variable_map)
        case asdl.DAST(declaration):
            resolve_declaration(declaration, variable_map)


def resolve_declaration(declaration, variable_map):
    name = declaration.name
    if name in variable_map.keys():
        raise ResolutionError(f"Duplicate variable declaration for {name}!")
    g = _mk_tmp(name)
    declaration.name = make_temporary(g)
    variable_map[name] = declaration.name, g
    resolve_exp(declaration.init, variable_map)


def resolve_statement(statement, variable_map):
    match statement:
        case asdl.ReturnAST(e) | asdl.ExpressionAST(e):
            resolve_exp(e, variable_map)


def resolve_exp(e, variable_map):
    match e:
        case asdl.VarAST(identifier):
            if identifier not in variable_map.keys():
                raise ResolutionError(f"Undeclared variable: {identifier}!")
            e.identifier = variable_map[identifier][0]
        case asdl.UnaryAST(_, exp):
            resolve_exp(exp, variable_map)
        case asdl.BinaryAST(_, e1, e2):
            resolve_exp(e1, variable_map)
            resolve_exp(e2, variable_map)
        case asdl.AssignmentAST(left, right):
            if not isinstance(left, asdl.VarAST):
                raise ResolutionError(f"Invalid lvalue: {left}!")
            resolve_exp(left, variable_map)
            resolve_exp(right, variable_map)
