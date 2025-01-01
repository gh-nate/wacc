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


class TypeCheckError(Exception):
    pass


def analyze(tree):
    function_declarations = tree.function_declarations
    identifier_resolution(function_declarations)
    type_check(function_declarations, {})
    loop_label(function_declarations)


def identifier_resolution(function_declarations):
    identifier_map = {}
    for function_declaration in function_declarations:
        resolve_function_declaration(function_declaration, identifier_map)


def resolve_block(block, identifier_map):
    for block_item in block.items:
        resolve_block_item(block_item, identifier_map)


def resolve_block_item(block_item, identifier_map):
    match block_item:
        case asdl.SAST(statement):
            resolve_statement(statement, identifier_map)
        case asdl.DAST(declaration):
            resolve_declaration(declaration, identifier_map)


def resolve_for_init(init, identifier_map):
    match init:
        case asdl.InitDeclAST(d):
            resolve_declaration(d, identifier_map)
        case asdl.InitExpAST(e):
            resolve_exp(e, identifier_map)


@dataclass
class MapEntry:
    new_name: str
    from_current_scope: bool
    has_linkage: bool


def resolve_declaration(declaration, identifier_map):
    match declaration:
        case asdl.FuncDeclAST(name, _, body):
            if body:
                raise ResolutionError(f"Local '{name}' function declaration with body")
            resolve_function_declaration(declaration, identifier_map)
        case asdl.VarDeclAST():
            resolve_variable_declaration(declaration, identifier_map)


def resolve_variable_declaration(declaration, identifier_map):
    g, name, init = None, declaration.name, declaration.init
    if name in identifier_map.keys():
        v = identifier_map[name]
        if v[0].from_current_scope:
            raise ResolutionError(f"Duplicate identifier declaration for {name}!")
        g = v[1]
    if not g:
        g = _mk_tmp(name + ".")
    declaration.name = make_temporary(g)
    identifier_map[name] = MapEntry(declaration.name, True, False), g
    resolve_exp(init, identifier_map)


def resolve_function_declaration(decl, identifier_map):
    g, name = None, decl.name
    if name in identifier_map.keys():
        v = identifier_map[name]
        prev_entry = v[0]
        if prev_entry.from_current_scope and not prev_entry.has_linkage:
            raise ResolutionError(f"Duplicate declaration: {name}")
        g = v[1]

    identifier_map[name] = MapEntry(name, True, True), g
    inner_map = copy_identifier_map(identifier_map)
    for index, param in enumerate(decl.params[:]):
        decl.params[index] = resolve_param(param, inner_map)

    if body := decl.body:
        resolve_block(body, inner_map)


def resolve_param(name, identifier_map):
    g = None
    if name in identifier_map.keys():
        v = identifier_map[name]
        if v[0].from_current_scope:
            raise ResolutionError(f"Duplicate identifier declaration for {name}!")
        g = v[1]
    if not g:
        g = _mk_tmp(name + ".")
    new_name = make_temporary(g)
    identifier_map[name] = MapEntry(new_name, True, False), g
    return new_name


def resolve_statement(statement, identifier_map):
    match statement:
        case asdl.ReturnAST(e) | asdl.ExpressionAST(e):
            resolve_exp(e, identifier_map)
        case asdl.IfAST(condition, then, else_):
            resolve_exp(condition, identifier_map)
            resolve_statement(then, identifier_map)
            resolve_statement(else_, identifier_map)
        case asdl.WhileAST(condition, body, _):
            resolve_exp(condition, identifier_map)
            resolve_statement(body, identifier_map)
        case asdl.DoWhileAST(body, condition, _):
            resolve_statement(body, identifier_map)
            resolve_exp(condition, identifier_map)
        case asdl.ForAST(init, condition, post, body, _):
            new_identifier_map = copy_identifier_map(identifier_map)
            resolve_for_init(init, new_identifier_map)
            resolve_exp(condition, new_identifier_map)
            resolve_exp(post, new_identifier_map)
            resolve_statement(body, new_identifier_map)
        case asdl.CompoundAST(block):
            resolve_block(block, copy_identifier_map(identifier_map))


def resolve_exp(e, identifier_map):
    match e:
        case asdl.VarAST(identifier):
            if identifier not in identifier_map.keys():
                raise ResolutionError(f"Undeclared variable: {identifier}!")
            e.identifier = identifier_map[identifier][0].new_name
        case asdl.UnaryAST(_, exp):
            resolve_exp(exp, identifier_map)
        case asdl.BinaryAST(_, e1, e2):
            resolve_exp(e1, identifier_map)
            resolve_exp(e2, identifier_map)
        case asdl.AssignmentAST(left, right):
            if not isinstance(left, asdl.VarAST):
                raise ResolutionError(f"Invalid lvalue: {left}!")
            resolve_exp(left, identifier_map)
            resolve_exp(right, identifier_map)
        case asdl.ConditionalAST(condition, e1, e2):
            resolve_exp(condition, identifier_map)
            resolve_exp(e1, identifier_map)
            resolve_exp(e2, identifier_map)
        case asdl.FunctionCallAST(name, args):
            if name not in identifier_map.keys():
                raise ResolutionError(f"Undeclared function: {name}")
            e.name = identifier_map[name][0].new_name
            for arg in args:
                resolve_exp(arg, identifier_map)


def copy_identifier_map(identifier_map):
    new_identifier_map = {}
    for k, (map_entry, g) in identifier_map.items():
        new_identifier_map[k] = (
            MapEntry(map_entry.new_name, False, map_entry.has_linkage),
            g,
        )
    return new_identifier_map


def type_check(function_declarations, symbols):
    for function_declaration in function_declarations:
        type_check_function_declaration(function_declaration, symbols)


@dataclass
class SymbolEntry:
    type: asdl.Type
    defined: bool | None


def type_check_variable_declaration(decl, symbols):
    symbols[decl.name] = SymbolEntry(asdl.IntType, None)
    if init := decl.init:
        type_check_exp(init, symbols)


def type_check_function_declaration(decl, symbols):
    params = decl.params
    fun_type = asdl.FunType(len(params))
    body = decl.body
    has_body = body is not None
    already_defined = False

    name = decl.name
    if name in symbols.keys():
        old_decl = symbols[name]
        if old_decl.type != fun_type:
            raise TypeCheckError(
                f"Incompatible function declarations: {old_decl.type} v.s. {fun_type}"
            )
        already_defined = old_decl.defined
        if already_defined and has_body:
            raise TypeCheckError(f"Function '{name}' is defined more than once")

    symbols[name] = SymbolEntry(fun_type, already_defined or has_body)

    if has_body:
        for param in params:
            symbols[param] = SymbolEntry(asdl.IntType, None)
        type_check_block(body, symbols)


def type_check_block_item(block_item, symbols):
    match block_item:
        case asdl.SAST(statement):
            type_check_statement(statement, symbols)
        case asdl.DAST(declaration):
            match declaration:
                case asdl.FuncDeclAST():
                    type_check_function_declaration(declaration, symbols)
                case asdl.VarDeclAST():
                    type_check_variable_declaration(declaration, symbols)


def type_check_block(block, symbols):
    for block_item in block.items:
        type_check_block_item(block_item, symbols)


def type_check_for_init(i, symbols):
    match i:
        case asdl.InitDeclAST(var_decl):
            type_check_variable_declaration(var_decl, symbols)
        case asdl.InitExpAST(e):
            type_check_exp(e, symbols)


def type_check_statement(s, symbols):
    match s:
        case asdl.ReturnAST(e) | asdl.ExpressionAST(e):
            type_check_exp(e, symbols)
        case asdl.IfAST(condition, then, else_):
            type_check_exp(condition, symbols)
            type_check_statement(then, symbols)
            type_check_statement(else_, symbols)
        case asdl.WhileAST(cond, body, _) | asdl.DoWhileAST(body, cond, _):
            type_check_exp(cond, symbols)
            type_check_statement(body, symbols)
        case asdl.ForAST(init, cond, post, body, _):
            type_check_for_init(init, symbols)
            type_check_exp(cond, symbols)
            type_check_exp(post, symbols)
            type_check_statement(body, symbols)
        case asdl.CompoundAST(block):
            type_check_block(block, symbols)


def type_check_exp(e, symbols):
    match e:
        case asdl.UnaryAST(_, e):
            type_check_exp(e, symbols)
        case asdl.BinaryAST(_, lhs, rhs) | asdl.AssignmentAST(lhs, rhs):
            type_check_exp(lhs, symbols)
            type_check_exp(rhs, symbols)
        case asdl.ConditionalAST(cond, e1, e2):
            type_check_exp(cond, symbols)
            type_check_exp(e1, symbols)
            type_check_exp(e2, symbols)
        case asdl.FunctionCallAST(f, args):
            f_type = symbols[f].type
            if f_type == asdl.IntType:
                raise TypeCheckError(f"Variable {f} used as function name")
            if f_type.param_count != len(args):
                raise TypeCheckError(
                    f"Function {f} called with the wrong number of arguments"
                )
            for arg in args:
                type_check_exp(arg, symbols)
        case asdl.VarAST(v):
            if symbols[v].type != asdl.IntType:
                raise TypeCheckError(f"Function name {v} used a variable")


def loop_label(function_declarations):
    g = {label: _mk_tmp(label) for label in ["w", "d", "f"]}
    for function_declaration in function_declarations:
        label_func_decl(g, function_declaration)


def label_func_decl(g, function_declaration):
    if block := function_declaration.body:
        label_block(g, block)


def label_block(g, block, current_label=None):
    for block_item in block.items:
        label_block_item(g, block_item, current_label)


def label_block_item(g, block_item, current_label=None):
    match block_item:
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
