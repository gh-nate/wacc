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
        self.else_ = self._mk_inc("else")
        self.e2 = self._mk_inc("e2_")

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

    def make_else_label(self):
        return next(self.else_)

    def make_e2_label(self):
        return next(self.e2)


def convert(tree, symbols):
    return convert_program(tree, symbols)


def convert_program(tree, symbols):
    top_level, g = [], G()
    for declaration in tree.declarations:
        if isinstance(declaration, asdl.FuncDeclAST) and declaration.body:
            convert_function_declaration(g, declaration, symbols, top_level)
    return asdl.ProgramTACKY(top_level + convert_symbols_to_tacky(symbols))


def convert_function_declaration(g, node, symbols, top_level):
    instructions = []
    convert_block(g, node.body, instructions, top_level)
    instructions.append(asdl.ReturnTACKY(asdl.ConstantTACKY(0)))
    name = node.name
    top_level.append(
        asdl.FunctionTACKY(name, symbols[name].attrs.globl, node.params, instructions)
    )


def convert_block(g, block, instructions, top_level):
    for block_item in block.items:
        if r := convert_block_item(g, block_item, top_level):
            instructions.extend(r)


def convert_block_item(g, node, top_level):
    match node:
        case asdl.SAST(statement):
            return convert_statement(g, statement, top_level)
        case asdl.DAST(asdl.VarDeclAST()):
            instructions, is_top_level = convert_variable_declaration(
                g, node.declaration
            )
            if is_top_level:
                top_level.extend(instructions)
                instructions.clear()
            return instructions


def convert_statement(g, node, top_level):
    break_prefix, continue_prefix = "break_", "continue_"
    instructions = []
    match node:
        case asdl.ReturnAST(e):
            v = emit_tacky(g, e, instructions)
            instructions.append(asdl.ReturnTACKY(v))
        case asdl.ExpressionAST(e):
            emit_tacky(g, e, instructions)
        case asdl.IfAST(condition, then, else_):
            if else_:
                else_label = g.make_else_label()
            end_label = g.make_end_label()
            c = emit_tacky(g, condition, instructions)
            instructions.append(
                asdl.JumpIfZeroTACKY(c, else_label if else_ else end_label)
            )
            instructions.extend(convert_statement(g, then, top_level))
            if else_:
                instructions += (
                    asdl.JumpTACKY(end_label),
                    asdl.LabelTACKY(else_label),
                )
                instructions.extend(convert_statement(g, else_, top_level))
            instructions.append(asdl.LabelTACKY(end_label))
        case asdl.CompoundAST(block):
            convert_block(g, block, instructions, top_level)
        case asdl.BreakAST(label):
            instructions.append(asdl.JumpTACKY(break_prefix + label))
        case asdl.ContinueAST(label):
            instructions.append(asdl.JumpTACKY(continue_prefix + label))
        case asdl.WhileAST(condition, body, label):
            continue_label = continue_prefix + label
            instructions.append(asdl.LabelTACKY(continue_label))
            c = emit_tacky(g, condition, instructions)
            break_label = break_prefix + label
            instructions.append(asdl.JumpIfZeroTACKY(c, break_label))
            instructions.extend(convert_statement(g, body, top_level))
            instructions += (
                asdl.JumpTACKY(continue_label),
                asdl.LabelTACKY(break_label),
            )
        case asdl.DoWhileAST(body, condition, label):
            instructions.append(asdl.LabelTACKY(label))
            instructions.extend(convert_statement(g, body, top_level))
            instructions.append(asdl.LabelTACKY(continue_prefix + label))
            c = emit_tacky(g, condition, instructions)
            instructions += (
                asdl.JumpIfNotZeroTACKY(c, label),
                asdl.LabelTACKY(break_prefix + label),
            )
        case asdl.ForAST(init, condition, post, body, label):
            match init:
                case asdl.InitDeclAST(d):
                    items, is_top_level = convert_variable_declaration(g, d)
                    if is_top_level:
                        top_level.extend(items)
                    else:
                        instructions.extend(items)
                case asdl.InitExpAST(e):
                    emit_tacky(g, e, instructions)
            instructions.append(asdl.LabelTACKY(label))
            break_label = break_prefix + label
            if condition:
                c = emit_tacky(g, condition, instructions)
                instructions.append(asdl.JumpIfZeroTACKY(c, break_label))
            instructions.extend(convert_statement(g, body, top_level))
            continue_label = continue_prefix + label
            instructions.append(asdl.LabelTACKY(continue_label))
            emit_tacky(g, post, instructions)
            instructions += (
                asdl.JumpTACKY(label),
                asdl.LabelTACKY(break_label),
            )
    return instructions


def convert_variable_declaration(g, node):
    instructions = []
    if init := node.init:
        v = emit_tacky(g, init, instructions)
        instructions.append(asdl.CopyTACKY(v, asdl.VarTACKY(node.name)))
    if (
        storage_class := node.storage_class
    ) and storage_class == asdl.StorageClassAST.STATIC:
        return instructions, True
    return instructions, False


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
                    instructions += (
                        asdl.JumpIfZeroTACKY(v2, false_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(1), dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(false_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(0), dst),
                        asdl.LabelTACKY(end_label),
                    )
                case asdl.BinaryOperatorAST.OR:
                    end_label, true_label = g.make_end_label(), g.make_or_true_label()
                    instructions.append(asdl.JumpIfNotZeroTACKY(v1, true_label))
                    v2 = emit_tacky(g, e2, instructions)
                    dst = asdl.VarTACKY(g.make_temp_vars())
                    instructions += (
                        asdl.JumpIfNotZeroTACKY(v2, true_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(0), dst),
                        asdl.JumpTACKY(end_label),
                        asdl.LabelTACKY(true_label),
                        asdl.CopyTACKY(asdl.ConstantTACKY(1), dst),
                        asdl.LabelTACKY(end_label),
                    )
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
        case asdl.ConditionalAST(condition, e1, e2):
            end_label, e2_label = g.make_end_label(), g.make_e2_label()
            result = asdl.VarTACKY(g.make_temp_vars())
            c = emit_tacky(g, condition, instructions)
            instructions.append(asdl.JumpIfZeroTACKY(c, e2_label))
            v1 = emit_tacky(g, e1, instructions)
            instructions += (
                asdl.CopyTACKY(v1, result),
                asdl.JumpTACKY(end_label),
                asdl.LabelTACKY(e2_label),
            )
            v2 = emit_tacky(g, e2, instructions)
            instructions += (
                asdl.CopyTACKY(v2, result),
                asdl.LabelTACKY(end_label),
            )
            return result
        case asdl.FunctionCallAST(name, args):
            args = [emit_tacky(g, arg, instructions) for arg in args]
            dst = asdl.VarTACKY(g.make_temp_vars())
            instructions.append(
                asdl.FunCallTACKY(
                    name,
                    args,
                    dst,
                )
            )
            return dst


def convert_symbols_to_tacky(symbols):
    tacky_defs = []
    for name, entry in symbols.items():
        match entry.attrs:
            case asdl.StaticAttrTC(init, globl):
                match init:
                    case asdl.InitialTC(i):
                        tacky_defs.append(asdl.StaticVariableTACKY(name, globl, i))
                    case asdl.TentativeTC():
                        tacky_defs.append(asdl.StaticVariableTACKY(name, globl, 0))
    return tacky_defs
