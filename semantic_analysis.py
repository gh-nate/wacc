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


def analyze(tree, symbols):
    declarations = tree.declarations
    identifier_resolution(declarations)
    type_check(declarations, symbols)
    loop_label(declarations)


def identifier_resolution(declarations):
    identifier_map, g = {}, {}
    for declaration in declarations:
        resolve_declaration(declaration, identifier_map, g)


def resolve_block(block, identifier_map, g):
    for block_item in block.items:
        resolve_block_item(block_item, identifier_map, g)


def resolve_block_item(block_item, identifier_map, g):
    match block_item:
        case asdl.SAST(statement):
            resolve_statement(statement, identifier_map, g)
        case asdl.DAST(declaration):
            resolve_declaration(declaration, identifier_map, g, True)


def resolve_for_init(init, identifier_map, g):
    match init:
        case asdl.InitDeclAST(d):
            resolve_declaration(d, identifier_map, g, True)
        case asdl.InitExpAST(e):
            resolve_exp(e, identifier_map)


@dataclass
class MapEntry:
    new_name: str
    from_current_scope: bool
    has_linkage: bool


def resolve_declaration(declaration, identifier_map, g, is_block_scope=False):
    match declaration:
        case asdl.FuncDeclAST(name, _, body):
            if body and is_block_scope:
                raise ResolutionError(f"Local '{name}' function declaration with body")
            resolve_function_declaration(declaration, identifier_map, g)
        case asdl.VarDeclAST():
            if is_block_scope:
                resolve_local_variable_declaration(declaration, identifier_map, g)
            else:
                resolve_file_scope_variable_declaration(declaration, identifier_map)


def resolve_file_scope_variable_declaration(declaration, identifier_map):
    name = declaration.name
    identifier_map[name] = MapEntry(name, True, True)


def resolve_local_variable_declaration(declaration, identifier_map, g):
    name = declaration.name
    if name in identifier_map:
        prev_entry = identifier_map[name]
        if prev_entry.from_current_scope:
            if not (
                prev_entry.has_linkage
                and declaration.storage_class == asdl.StorageClassAST.EXTERN
            ):
                raise ResolutionError(f"Conflicting local declarations for {name}")
    if declaration.storage_class == asdl.StorageClassAST.EXTERN:
        identifier_map[name] = MapEntry(name, True, True)
    else:
        if name not in g:
            g[name] = _mk_tmp(name + ".")
        declaration.name = make_temporary(g[name])
        identifier_map[name] = MapEntry(declaration.name, True, False)
        resolve_exp(declaration.init, identifier_map)


def resolve_function_declaration(decl, identifier_map, g):
    name = decl.name
    if name in identifier_map:
        prev_entry = identifier_map[name]
        if prev_entry.from_current_scope and not prev_entry.has_linkage:
            raise ResolutionError(f"Duplicate declaration: {name}")

    identifier_map[name] = MapEntry(name, True, True)
    inner_map = copy_identifier_map(identifier_map)
    for index, param in enumerate(decl.params[:]):
        decl.params[index] = resolve_param(param, inner_map, g)

    if body := decl.body:
        resolve_block(body, inner_map, g)


def resolve_param(name, identifier_map, g):
    if name in identifier_map:
        if identifier_map[name].from_current_scope:
            raise ResolutionError(f"Duplicate identifier declaration for {name}!")
    if name not in g:
        g[name] = _mk_tmp(name + ".")
    new_name = make_temporary(g[name])
    identifier_map[name] = MapEntry(new_name, True, False)
    return new_name


def resolve_statement(statement, identifier_map, g):
    match statement:
        case asdl.ReturnAST(e) | asdl.ExpressionAST(e):
            resolve_exp(e, identifier_map)
        case asdl.IfAST(condition, then, else_):
            resolve_exp(condition, identifier_map)
            resolve_statement(then, identifier_map, g)
            resolve_statement(else_, identifier_map, g)
        case asdl.WhileAST(condition, body, _):
            resolve_exp(condition, identifier_map)
            resolve_statement(body, identifier_map, g)
        case asdl.DoWhileAST(body, condition, _):
            resolve_statement(body, identifier_map, g)
            resolve_exp(condition, identifier_map)
        case asdl.ForAST(init, condition, post, body, _):
            new_identifier_map = copy_identifier_map(identifier_map)
            resolve_for_init(init, new_identifier_map, g)
            resolve_exp(condition, new_identifier_map)
            resolve_exp(post, new_identifier_map)
            resolve_statement(body, new_identifier_map, g)
        case asdl.CompoundAST(block):
            resolve_block(block, copy_identifier_map(identifier_map), g)


def resolve_exp(e, identifier_map):
    match e:
        case asdl.VarAST(identifier):
            if identifier not in identifier_map:
                raise ResolutionError(f"Undeclared variable: {identifier}!")
            e.identifier = identifier_map[identifier].new_name
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
            if name not in identifier_map:
                raise ResolutionError(f"Undeclared function: {name}")
            e.name = identifier_map[name].new_name
            for arg in args:
                resolve_exp(arg, identifier_map)


def copy_identifier_map(identifier_map):
    new_identifier_map = {}
    for name, map_entry in identifier_map.items():
        new_identifier_map[name] = MapEntry(
            map_entry.new_name, False, map_entry.has_linkage
        )
    return new_identifier_map


def type_check(declarations, symbols):
    for declaration in declarations:
        match declaration:
            case asdl.FuncDeclAST():
                type_check_function_declaration(declaration, symbols)
            case asdl.VarDeclAST():
                type_check_file_scope_variable_declaration(declaration, symbols)


@dataclass
class SymbolEntry:
    type: asdl.Type
    attrs: asdl.IdentifierAttrs | None


def type_check_file_scope_variable_declaration(decl, symbols):
    match decl.init:
        case asdl.ConstantAST(i):
            initial_value = asdl.InitialTC(i)
        case None:
            if decl.storage_class == asdl.StorageClassAST.EXTERN:
                initial_value = asdl.NoInitializerTC()
            else:
                initial_value = asdl.TentativeTC()
        case _:
            raise TypeCheckError(f"Non-constant initializer for '{decl.name}'")

    globl = decl.storage_class != asdl.StorageClassAST.STATIC

    name = decl.name
    if name in symbols:
        old_decl = symbols[name]
        if old_decl.type != asdl.IntType:
            raise TypeCheckError(f"Function '{name}' redeclared as variable")
        if decl.storage_class == asdl.StorageClassAST.EXTERN:
            globl = old_decl.attrs.globl
        elif old_decl.attrs.globl != globl:
            raise TypeCheckError(f"Conflicting variable linkage for '{name}'")

        if isinstance(old_decl.attrs.init, asdl.InitialTC):
            if isinstance(initial_value, asdl.InitialTC):
                raise TypeCheckError(
                    f"Conflicting file scope variable declarations '{name}'"
                )
            else:
                initial_value = old_decl.attrs.init
        elif not isinstance(initial_value, asdl.InitialTC) and isinstance(
            old_decl.attrs.init, asdl.TentativeTC
        ):
            initial_value = asdl.TentativeTC()
    symbols[name] = SymbolEntry(asdl.IntType, asdl.StaticAttrTC(initial_value, globl))


def type_check_local_variable_declaration(decl, symbols):
    name = decl.name
    match decl.storage_class:
        case asdl.StorageClassAST.EXTERN:
            if decl.init:
                raise TypeCheckError(
                    f"Initializer on local extern variable declaration for '{name}'"
                )
            if name in symbols:
                old_decl = symbols[name]
                if old_decl.type != asdl.IntType:
                    raise TypeCheckError(
                        f"Function redeclared as variable for '{name}'"
                    )
            else:
                symbols[name] = SymbolEntry(
                    asdl.IntType, asdl.StaticAttrTC(asdl.NoInitializerTC, True)
                )
        case asdl.StorageClassAST.STATIC:
            match decl.init:
                case asdl.ConstantAST(i):
                    initial_value = asdl.InitialTC(i)
                case None:
                    initial_value = asdl.InitialTC(0)
                case _:
                    raise TypeCheckError(
                        f"Non-constant initializer on local static variable '{name}'"
                    )
            symbols[name] = SymbolEntry(
                asdl.IntType, asdl.StaticAttrTC(initial_value, False)
            )
        case _:
            symbols[name] = SymbolEntry(asdl.IntType, asdl.LocalAttrTC())
            if init := decl.init:
                type_check_exp(init, symbols)


def type_check_function_declaration(decl, symbols):
    params = decl.params
    fun_type = asdl.FunType(len(params))
    body = decl.body
    has_body = body is not None
    already_defined = False
    globl = decl.storage_class != asdl.StorageClassAST.STATIC

    name = decl.name
    if name in symbols:
        old_decl = symbols[name]
        if old_decl.type != fun_type:
            raise TypeCheckError(
                f"Incompatible function declarations: {old_decl.type} v.s. {fun_type}"
            )
        already_defined = old_decl.attrs.defined
        if already_defined and has_body:
            raise TypeCheckError(f"Function '{name}' is defined more than once")

        if old_decl.attrs.globl and decl.storage_class == asdl.StorageClassAST.STATIC:
            raise TypeCheckError(
                f"Static function declaration follows non-static for '{name}'"
            )
        globl = old_decl.attrs.globl

    symbols[name] = SymbolEntry(
        fun_type,
        asdl.FunAttrTC(already_defined or has_body, globl),
    )

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
                case asdl.FuncDeclAST(name, _, _, storage_class):
                    if storage_class and storage_class == asdl.StorageClassAST.STATIC:
                        raise TypeCheckError(
                            f"Cannot declare '{name}' block-scope function declaration with `static`"
                        )
                    type_check_function_declaration(declaration, symbols)
                case asdl.VarDeclAST():
                    type_check_local_variable_declaration(declaration, symbols)


def type_check_block(block, symbols):
    for block_item in block.items:
        type_check_block_item(block_item, symbols)


def type_check_for_init(i, symbols):
    match i:
        case asdl.InitDeclAST(var_decl):
            if var_decl.storage_class:
                raise TypeCheckError(
                    "Forbidden storage-class specifier for '{var_decl.name}'"
                )
            type_check_local_variable_declaration(var_decl, symbols)
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


def loop_label(declarations):
    g = {label: _mk_tmp(label) for label in ["w", "d", "f"]}
    for declaration in declarations:
        if isinstance(declaration, asdl.FuncDeclAST):
            label_func_decl(g, declaration)


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
