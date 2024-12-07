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


def _mk_tmp():
    count = 0
    while True:
        yield f"tmp.{count}"
        count += 1


def make_temporary(g):
    return next(g)


def convert(tree):
    return convert_program(tree)


def convert_program(node):
    return asdl.ProgramTACKY(convert_function_definition(node.function_definition))


def convert_function_definition(node):
    return asdl.FunctionTACKY(node.name, convert_statement(node.body))


def convert_statement(node):
    g, instructions = _mk_tmp(), []
    v = convert_tacky(g, node.exp, instructions)
    instructions.append(asdl.ReturnTACKY(v))
    return instructions


def convert_tacky(g, node, instructions):
    match node:
        case asdl.ConstantAST(c):
            return asdl.ConstantTACKY(c)
        case asdl.UnaryAST(op, inner):
            src = convert_tacky(g, inner, instructions)
            dst_name = make_temporary(g)
            dst = asdl.VarTACKY(dst_name)
            tacky_op = convert_unop(op)
            instructions.append(asdl.UnaryTACKY(tacky_op, src, dst))
            return dst
        case asdl.BinaryAST(op, e1, e2):
            v1 = convert_tacky(g, e1, instructions)
            v2 = convert_tacky(g, e2, instructions)
            dst_name = make_temporary(g)
            dst = asdl.VarTACKY(dst_name)
            tacky_op = convert_binop(op)
            instructions.append(asdl.BinaryTACKY(tacky_op, v1, v2, dst))
            return dst


def convert_unop(op):
    match op:
        case asdl.ComplementAST():
            return asdl.ComplementTACKY()
        case asdl.NegateAST():
            return asdl.NegateTACKY()


def convert_binop(op):
    match op:
        case asdl.AddAST():
            return asdl.AddTACKY()
        case asdl.SubtractAST():
            return asdl.SubtractTACKY()
        case asdl.MultiplyAST():
            return asdl.MultiplyTACKY()
        case asdl.DivideAST():
            return asdl.DivideTACKY()
        case asdl.RemainderAST():
            return asdl.RemainderTACKY()
