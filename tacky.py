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


class G:
    def __init__(self):
        self.temp_vars = self._mk_inc("tmp.")
        self.and_false = self._mk_inc("and_false")
        self.or_true = self._mk_inc("or_true")
        self.end = self._mk_inc("end")

    def _mk_inc(self, prefix):
        count = 0
        while True:
            yield f"{prefix}{count}"
            count += 1

    def make_temp_vars(self):
        return next(self.temp_vars)

    def make_and_false_label(self):
        return next(self.and_false)

    def make_or_true_label(self):
        return next(self.or_true)

    def make_end_label(self):
        return next(self.end)


def convert(tree):
    return convert_program(tree)


def convert_program(tree):
    return asdl.ProgramTACKY(convert_function_definition(tree.function_definition))


def convert_function_definition(node):
    g, instructions = G(), []
    for block_item in node.body:
        instructions.extend(convert_block_item(g, block_item))
    instructions.append(asdl.ReturnTACKY(asdl.ConstantTACKY(0)))
    return asdl.FunctionTACKY(node.name, instructions)


def convert_block_item(g, node):
    match node:
        case asdl.SAST(statement):
            return convert_statement(g, statement)
        case asdl.DAST(declaration):
            return convert_declaration(g, declaration)


def convert_statement(g, node):
    instructions = []
    match node:
        case asdl.ReturnAST(e):
            v = emit_tacky(g, e, instructions)
            instructions.append(asdl.ReturnTACKY(v))
        case asdl.ExpressionAST(e):
            emit_tacky(g, e, instructions)
    return instructions


def convert_declaration(g, node):
    instructions = []
    if init := node.init:
        v = emit_tacky(g, init, instructions)
        instructions.append(asdl.CopyTACKY(v, asdl.VarTACKY(node.name)))
    return instructions


def convert_unop(unop):
    match unop:
        case asdl.UnaryOperatorAST.COMPLEMENT:
            return asdl.UnaryOperatorTACKY.COMPLEMENT
        case asdl.UnaryOperatorAST.NEGATE:
            return asdl.UnaryOperatorTACKY.NEGATE
        case asdl.UnaryOperatorAST.NOT:
            return asdl.UnaryOperatorTACKY.NOT


def convert_binop(binop):
    match binop:
        case asdl.BinaryOperatorAST.ADD:
            return asdl.BinaryOperatorTACKY.ADD
        case asdl.BinaryOperatorAST.SUBTRACT:
            return asdl.BinaryOperatorTACKY.SUBTRACT
        case asdl.BinaryOperatorAST.MULTIPLY:
            return asdl.BinaryOperatorTACKY.MULTIPLY
        case asdl.BinaryOperatorAST.DIVIDE:
            return asdl.BinaryOperatorTACKY.DIVIDE
        case asdl.BinaryOperatorAST.REMAINDER:
            return asdl.BinaryOperatorTACKY.REMAINDER
        case asdl.BinaryOperatorAST.EQUAL:
            return asdl.BinaryOperatorTACKY.EQUAL
        case asdl.BinaryOperatorAST.NOT_EQUAL:
            return asdl.BinaryOperatorTACKY.NOT_EQUAL
        case asdl.BinaryOperatorAST.LESS_THAN:
            return asdl.BinaryOperatorTACKY.LESS_THAN
        case asdl.BinaryOperatorAST.LESS_OR_EQUAL:
            return asdl.BinaryOperatorTACKY.LESS_OR_EQUAL
        case asdl.BinaryOperatorAST.GREATER_THAN:
            return asdl.BinaryOperatorTACKY.GREATER_THAN
        case asdl.BinaryOperatorAST.GREATER_OR_EQUAL:
            return asdl.BinaryOperatorTACKY.GREATER_OR_EQUAL


def emit_tacky(g, exp, instructions):
    match exp:
        case asdl.ConstantAST(int):
            return asdl.ConstantTACKY(int)
        case asdl.VarAST(v):
            return asdl.VarTACKY(v)
        case asdl.UnaryAST(op, inner):
            src = emit_tacky(g, inner, instructions)
            dst = asdl.VarTACKY(g.make_temp_vars())
            instructions.append(asdl.UnaryTACKY(convert_unop(op), src, dst))
            return dst
        case asdl.BinaryAST(op, e1, e2):
            v1 = emit_tacky(g, e1, instructions)
            match op:
                case asdl.BinaryOperatorAST.AND:
                    end_label, false_label = (
                        g.make_end_label(),
                        g.make_and_false_label(),
                    )
                    instructions.append(asdl.JumpIfZeroTACKY(v1, false_label))
                    v2 = emit_tacky(g, e2, instructions)
                    dst = asdl.VarTACKY(g.make_temp_vars())
                    instructions += [
                        asdl.JumpIfZeroTACKY(v2, false_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(1), dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(false_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(0), dst),
                        asdl.LabelTACKY(end_label),
                    ]
                case asdl.BinaryOperatorAST.OR:
                    end_label, true_label = g.make_end_label(), g.make_or_true_label()
                    instructions.append(asdl.JumpIfNotZeroTACKY(v1, true_label))
                    v2 = emit_tacky(g, e2, instructions)
                    dst = asdl.VarTACKY(g.make_temp_vars())
                    instructions += [
                        asdl.JumpIfNotZeroTACKY(v2, true_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(0), dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(true_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(1), dst),
                        asdl.LabelTACKY(end_label),
                    ]
                case _:
                    v2 = emit_tacky(g, e2, instructions)
                    dst = asdl.VarTACKY(g.make_temp_vars())
                    instructions.append(
                        asdl.BinaryTACKY(convert_binop(op), v1, v2, dst)
                    )
            return dst
        case asdl.AssignmentAST(asdl.VarAST(v), rhs):
            result = emit_tacky(g, rhs, instructions)
            lhs = asdl.VarTACKY(v)
            instructions.append(asdl.CopyTACKY(result, lhs))
            return lhs
