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

from dataclasses import dataclass

import asdl


def _mk_tmp(prefix):
    count = 0
    while True:
        yield f"{prefix}{count}"
        count += 1


make_temporary = next
make_label = make_temporary


class ResolutionError(Exception):
    pass


class LoopLabellingError(Exception):
    pass


def analyze(tree):
    body = tree.function_definition.body
    variable_resolution(body)
    loop_label(body)


def variable_resolution(body):
    resolve_block(body, {})


def resolve_block(block, variable_map):
    for block_item in block.items:
        resolve_block_item(block_item, variable_map)


def resolve_block_item(block_item, variable_map):
    match block_item:
        case asdl.SAST(statement):
            resolve_statement(statement, variable_map)
        case asdl.DAST(declaration):
            resolve_declaration(declaration, variable_map)


def resolve_for_init(init, variable_map):
    match init:
        case asdl.InitDeclAST(d):
            resolve_declaration(d, variable_map)
        case asdl.InitExpAST(e):
            resolve_exp(e, variable_map)


@dataclass
class MapEntry:
    new_name: str
    from_current_block: bool


def resolve_declaration(declaration, variable_map):
    name = declaration.name
    if name in variable_map.keys():
        v = variable_map[name]
        if v[0].from_current_block:
            raise ResolutionError(f"Duplicate variable declaration for {name}!")
        g = v[1]
    else:
        g = _mk_tmp(name + ".")
    declaration.name = make_temporary(g)
    variable_map[name] = MapEntry(declaration.name, True), g
    resolve_exp(declaration.init, variable_map)


def resolve_statement(statement, variable_map):
    match statement:
        case asdl.ReturnAST(e) | asdl.ExpressionAST(e):
            resolve_exp(e, variable_map)
        case asdl.IfAST(condition, then, else_):
            resolve_exp(condition, variable_map)
            resolve_statement(then, variable_map)
            resolve_statement(else_, variable_map)
        case asdl.WhileAST(condition, body, _):
            resolve_exp(condition, variable_map)
            resolve_statement(body, variable_map)
        case asdl.DoWhileAST(body, condition, _):
            resolve_statement(body, variable_map)
            resolve_exp(condition, variable_map)
        case asdl.ForAST(init, condition, post, body, _):
            new_variable_map = copy_variable_map(variable_map)
            resolve_for_init(init, new_variable_map)
            resolve_exp(condition, new_variable_map)
            resolve_exp(post, new_variable_map)
            resolve_statement(body, new_variable_map)
        case asdl.CompoundAST(block):
            resolve_block(block, copy_variable_map(variable_map))


def resolve_exp(e, variable_map):
    match e:
        case asdl.VarAST(identifier):
            if identifier not in variable_map.keys():
                raise ResolutionError(f"Undeclared variable: {identifier}!")
            e.identifier = variable_map[identifier][0].new_name
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
        case asdl.ConditionalAST(condition, e1, e2):
            resolve_exp(condition, variable_map)
            resolve_exp(e1, variable_map)
            resolve_exp(e2, variable_map)


def copy_variable_map(variable_map):
    new_variable_map = {}
    for k, (map_entry, g) in variable_map.items():
        new_variable_map[k] = MapEntry(map_entry.new_name, False), g
    return new_variable_map


def loop_label(block):
    label_block({label: _mk_tmp(label) for label in ["w", "d", "f"]}, block)


def label_block(g, block, current_label=None):
    for item in block.items:
        match item:
            case asdl.SAST(statement):
                label_statement(g, statement, current_label)


def label_statement(g, statement, current_label=None):
    match statement:
        case asdl.IfAST(_, then, else_):
            label_statement(g, then, current_label)
            label_statement(g, else_, current_label)
        case asdl.BreakAST(_):
            if not current_label:
                raise LoopLabellingError("break statement outside of loop")
            statement.label = current_label
        case asdl.ContinueAST(_):
            if not current_label:
                raise LoopLabellingError("continue statement outside of loop")
            statement.label = current_label
        case asdl.WhileAST(_, body, _):
            new_label = make_label(g["w"])
            label_statement(g, body, new_label)
            statement.label = new_label
        case asdl.DoWhileAST(body, _, _):
            new_label = make_label(g["d"])
            label_statement(g, body, new_label)
            statement.label = new_label
        case asdl.ForAST(_, _, _, body, _):
            new_label = make_label(g["f"])
            label_statement(g, body, new_label)
            statement.label = new_label
        case asdl.CompoundAST(block):
            label_block(g, block, current_label)
