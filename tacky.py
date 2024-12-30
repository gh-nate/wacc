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
    counter = 0
    while True:
        yield f"tmp.{counter}"
        counter += 1


make_temporary = next


def convert(tree):
    return convert_program(tree)


def convert_program(tree):
    return asdl.ProgramTACKY(convert_function_definition(tree.function_definition))


def convert_function_definition(node):
    return asdl.FunctionTACKY(node.name, convert_statement(node.body))


def convert_statement(node):
    instructions = []
    v = emit_tacky(_mk_tmp(), node.exp, instructions)
    instructions.append(asdl.ReturnTACKY(v))
    return instructions


def convert_unop(unop):
    match unop:
        case asdl.UnaryOperatorAST.COMPLEMENT:
            return asdl.UnaryOperatorTACKY.COMPLEMENT
        case asdl.UnaryOperatorAST.NEGATE:
            return asdl.UnaryOperatorTACKY.NEGATE


def emit_tacky(g, exp, instructions):
    match exp:
        case asdl.ConstantAST(int):
            return asdl.ConstantTACKY(int)
        case asdl.UnaryAST(op, inner):
            src = emit_tacky(g, inner, instructions)
            dst = asdl.VarTACKY(make_temporary(g))
            instructions.append(asdl.UnaryTACKY(convert_unop(op), src, dst))
            return dst
