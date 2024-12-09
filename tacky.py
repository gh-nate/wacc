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


def _mk_inc(prefix):
    count = 0
    while True:
        yield f"{prefix}{count}"
        count += 1


def make_temporary(g):
    return next(g)


make_label = make_temporary


def convert(tree):
    return convert_program(tree)


def convert_program(node):
    return asdl.ProgramTACKY(convert_function_definition(node.function_definition))


def convert_function_definition(node):
    return asdl.FunctionTACKY(node.name, convert_statement(node.body))


def convert_statement(node):
    g, h, i = _mk_inc("tmp."), _mk_inc("and_"), _mk_inc("or_")
    instructions = []
    v = convert_tacky(g, h, i, node.exp, instructions)
    instructions.append(asdl.ReturnTACKY(v))
    return instructions


def convert_tacky(g, h, i, node, instructions):
    c0, c1 = asdl.ConstantTACKY(0), asdl.ConstantTACKY(1)
    end_label = "end"
    match node:
        case asdl.ConstantAST(c):
            return asdl.ConstantTACKY(c)
        case asdl.UnaryAST(op, inner):
            src = convert_tacky(g, h, i, inner, instructions)
            dst_name = make_temporary(g)
            dst = asdl.VarTACKY(dst_name)
            tacky_op = convert_unop(op)
            instructions.append(asdl.UnaryTACKY(tacky_op, src, dst))
            return dst
        case asdl.BinaryAST(op, e1, e2):
            dst_name = make_temporary(g)
            dst = asdl.VarTACKY(dst_name)
            v1 = convert_tacky(g, h, i, e1, instructions)
            match op:
                case asdl.AndAST():
                    false_label = make_label(h)
                    instructions.append(asdl.JumpIfZeroTACKY(v1, false_label))
                    v2 = convert_tacky(g, h, i, e2, instructions)
                    instructions += [
                        asdl.JumpIfZeroTACKY(v2, false_label),
                        asdl.CopyTACKY(c1, dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(false_label),
                        asdl.CopyTACKY(c0, dst),
                        asdl.LabelTACKY(end_label),
                    ]
                case asdl.OrAST():
                    true_label = make_label(h)
                    instructions.append(asdl.JumpIfNotZeroTACKY(v1, true_label))
                    v2 = convert_tacky(g, h, i, e2, instructions)
                    instructions += [
                        asdl.JumpIfNotZeroTACKY(v2, true_label),
                        asdl.CopyTACKY(c0, dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(true_label),
                        asdl.CopyTACKY(c1, dst),
                        asdl.LabelTACKY(end_label),
                    ]
                case _:
                    v2 = convert_tacky(g, h, i, e2, instructions)
                    tacky_op = convert_binop(op)
                    instructions.append(asdl.BinaryTACKY(tacky_op, v1, v2, dst))
            return dst


def convert_unop(op):
    match op:
        case asdl.ComplementAST():
            return asdl.ComplementTACKY()
        case asdl.NegateAST():
            return asdl.NegateTACKY()
        case asdl.NotAST():
            return asdl.NotTACKY()


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
        case asdl.EqualAST():
            return asdl.EqualTACKY()
        case asdl.NotEqualAST():
            return asdl.NotEqualTACKY()
        case asdl.LessThanAST():
            return asdl.LessThanTACKY()
        case asdl.LessOrEqualAST():
            return asdl.LessOrEqualTACKY()
        case asdl.GreaterThanAST():
            return asdl.GreaterThanTACKY()
        case asdl.GreaterOrEqualAST():
            return asdl.GreaterOrEqualAST()
