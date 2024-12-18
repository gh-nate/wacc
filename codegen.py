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


def convert(tree):
    tree = convert_program(tree)
    instructions = tree.function_definition.instructions
    stack_offset = replace_pseudoregisters(instructions)
    fix_instructions(instructions, stack_offset)
    return tree


def convert_program(tree):
    return asdl.ProgramASM(convert_function_definition(tree.function_definition))


def convert_function_definition(node):
    return asdl.FunctionASM(node.identifier, convert_instructions(node.body))


def convert_instructions(instructions):
    new_instructions = []
    for instruction in instructions:
        match instruction:
            case asdl.ReturnTACKY(val):
                new_instructions += [
                    asdl.MovASM(convert_val(val), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ]
            case asdl.UnaryTACKY(unop, src, dst):
                dst = convert_val(dst)
                if unop == asdl.UnaryOperatorTACKY.NOT:
                    new_instructions += [
                        asdl.CmpASM(asdl.ImmASM(0), convert_val(src)),
                        asdl.MovASM(asdl.ImmASM(0), dst),
                        asdl.SetCCASM(asdl.CondCode.E, dst),
                    ]
                else:
                    new_instructions += [
                        asdl.MovASM(convert_val(src), dst),
                        asdl.UnaryASM(convert_unary_operator(unop), dst),
                    ]
            case asdl.BinaryTACKY(op, src1, src2, dst):
                src1, src2, dst = convert_val(src1), convert_val(src2), convert_val(dst)
                match op:
                    case asdl.BinaryOperatorTACKY.DIVIDE:
                        new_instructions += [
                            asdl.MovASM(src1, asdl.RegASM(asdl.Reg.AX)),
                            asdl.CdqASM(),
                            asdl.IdivASM(src2),
                            asdl.MovASM(asdl.RegASM(asdl.Reg.AX), dst),
                        ]
                    case asdl.BinaryOperatorTACKY.REMAINDER:
                        new_instructions += [
                            asdl.MovASM(src1, asdl.RegASM(asdl.Reg.AX)),
                            asdl.CdqASM(),
                            asdl.IdivASM(src2),
                            asdl.MovASM(asdl.RegASM(asdl.Reg.DX), dst),
                        ]
                    case (
                        asdl.BinaryOperatorTACKY.EQUAL
                        | asdl.BinaryOperatorTACKY.NOT_EQUAL
                        | asdl.BinaryOperatorTACKY.LESS_THAN
                        | asdl.BinaryOperatorTACKY.LESS_OR_EQUAL
                        | asdl.BinaryOperatorTACKY.GREATER_THAN
                        | asdl.BinaryOperatorTACKY.GREATER_OR_EQUAL
                    ):
                        new_instructions += [
                            asdl.CmpASM(src2, src1),
                            asdl.MovASM(asdl.ImmASM(0), dst),
                            asdl.SetCCASM(convert_relational_operator(op), dst),
                        ]
                    case _:
                        new_instructions += [
                            asdl.MovASM(src1, dst),
                            asdl.BinaryASM(convert_binary_operator(op), src2, dst),
                        ]
            case asdl.JumpTACKY(target):
                new_instructions.append(asdl.JmpASM(target))
            case asdl.JumpIfZeroTACKY(condition, target):
                new_instructions += [
                    asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                    asdl.JmpCCASM(asdl.CondCode.E, target),
                ]
            case asdl.JumpIfNotZeroTACKY(condition, target):
                new_instructions += [
                    asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                    asdl.JmpCCASM(asdl.CondCode.NE, target),
                ]
            case asdl.CopyTACKY(src, dst):
                new_instructions.append(asdl.MovASM(convert_val(src), convert_val(dst)))
            case asdl.LabelTACKY(identifier):
                new_instructions.append(asdl.LabelASM(identifier))
    return new_instructions


def convert_val(node):
    match node:
        case asdl.ConstantTACKY(int):
            return asdl.ImmASM(int)
        case asdl.VarTACKY(identifier):
            return asdl.PseudoASM(identifier)


def convert_unary_operator(node):
    match node:
        case asdl.UnaryOperatorTACKY.COMPLEMENT:
            return asdl.UnaryOperatorASM.NOT
        case asdl.UnaryOperatorTACKY.NEGATE:
            return asdl.UnaryOperatorASM.NEG


def convert_binary_operator(node):
    match node:
        case asdl.BinaryOperatorTACKY.ADD:
            return asdl.BinaryOperatorASM.ADD
        case asdl.BinaryOperatorTACKY.SUBTRACT:
            return asdl.BinaryOperatorASM.SUB
        case asdl.BinaryOperatorTACKY.MULTIPLY:
            return asdl.BinaryOperatorASM.MULT


def convert_relational_operator(node):
    match node:
        case asdl.BinaryOperatorTACKY.EQUAL:
            return asdl.CondCode.E
        case asdl.BinaryOperatorTACKY.NOT_EQUAL:
            return asdl.CondCode.NE
        case asdl.BinaryOperatorTACKY.LESS_THAN:
            return asdl.CondCode.L
        case asdl.BinaryOperatorTACKY.LESS_OR_EQUAL:
            return asdl.CondCode.LE
        case asdl.BinaryOperatorTACKY.GREATER_THAN:
            return asdl.CondCode.G
        case asdl.BinaryOperatorTACKY.GREATER_OR_EQUAL:
            return asdl.CondCode.GE


def replace_pseudoregisters(instructions):
    def replace(identifier, stack_offset, identifiers_offsets):
        if identifier not in identifiers_offsets:
            stack_offset -= 4
            identifiers_offsets[identifier] = stack_offset
        return asdl.StackASM(identifiers_offsets[identifier]), stack_offset

    identifiers_offsets, stack_offset = {}, 0
    for index, instruction in enumerate(instructions[:]):
        match instruction:
            case asdl.MovASM(asdl.PseudoASM(x), asdl.PseudoASM(y)):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.MovASM(src, dst)
            case asdl.MovASM(asdl.PseudoASM(x), y):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                instructions[index] = asdl.MovASM(src, y)
            case asdl.MovASM(x, asdl.PseudoASM(y)):
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.MovASM(x, dst)
            case asdl.UnaryASM(unary_operator, asdl.PseudoASM(identifier)):
                operand, stack_offset = replace(
                    identifier, stack_offset, identifiers_offsets
                )
                instructions[index] = asdl.UnaryASM(unary_operator, operand)
            case asdl.BinaryASM(op, asdl.PseudoASM(x), asdl.PseudoASM(y)):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.BinaryASM(op, src, dst)
            case asdl.BinaryASM(op, asdl.PseudoASM(x), y):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                instructions[index] = asdl.BinaryASM(op, src, y)
            case asdl.BinaryASM(op, x, asdl.PseudoASM(y)):
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.BinaryASM(op, x, dst)
            case asdl.IdivASM(asdl.PseudoASM(identifier)):
                operand, stack_offset = replace(
                    identifier, stack_offset, identifiers_offsets
                )
                instructions[index] = asdl.IdivASM(operand)
            case asdl.CmpASM(asdl.PseudoASM(x), asdl.PseudoASM(y)):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.CmpASM(src, dst)
            case asdl.CmpASM(asdl.PseudoASM(x), y):
                src, stack_offset = replace(x, stack_offset, identifiers_offsets)
                instructions[index] = asdl.CmpASM(src, y)
            case asdl.CmpASM(x, asdl.PseudoASM(y)):
                dst, stack_offset = replace(y, stack_offset, identifiers_offsets)
                instructions[index] = asdl.CmpASM(x, dst)
            case asdl.SetCCASM(op, asdl.PseudoASM(identifier)):
                operand, stack_offset = replace(
                    identifier, stack_offset, identifiers_offsets
                )
                instructions[index] = asdl.SetCCASM(op, operand)
    return abs(stack_offset)


def fix_instructions(instructions, stack_offset):
    index = 0
    instructions.insert(index, asdl.AllocateStackASM(stack_offset))
    index += 1
    while index < len(instructions):
        offset = 1
        match instructions[index]:
            case asdl.MovASM(src, asdl.StackASM(stack_offset)):
                instructions[index] = asdl.MovASM(src, asdl.RegASM(asdl.Reg.R10))
                instructions.insert(
                    index + offset,
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(stack_offset)),
                )
                offset += 1
            case asdl.IdivASM(asdl.ImmASM(i)):
                instructions[index] = asdl.MovASM(
                    asdl.ImmASM(i), asdl.RegASM(asdl.Reg.R10)
                )
                instructions.insert(
                    index + offset, asdl.IdivASM(asdl.RegASM(asdl.Reg.R10))
                )
                offset += 1
            case asdl.BinaryASM(binop, src, asdl.StackASM(stack_offset)):
                match binop:
                    case asdl.BinaryOperatorASM.ADD | asdl.BinaryOperatorASM.SUB:
                        instructions[index] = asdl.MovASM(
                            src, asdl.RegASM(asdl.Reg.R10)
                        )
                        instructions.insert(
                            index + offset,
                            asdl.BinaryASM(
                                binop,
                                asdl.RegASM(asdl.Reg.R10),
                                asdl.StackASM(stack_offset),
                            ),
                        )
                        offset += 1
                    case asdl.BinaryOperatorASM.MULT:
                        instructions[index] = asdl.MovASM(
                            asdl.StackASM(stack_offset), asdl.RegASM(asdl.Reg.R11)
                        )
                        instructions.insert(
                            index + offset,
                            asdl.BinaryASM(binop, src, asdl.RegASM(asdl.Reg.R11)),
                        )
                        offset += 1
                        instructions.insert(
                            index + offset,
                            asdl.MovASM(
                                asdl.RegASM(asdl.Reg.R11), asdl.StackASM(stack_offset)
                            ),
                        )
                        offset += 1
            case asdl.CmpASM(x, y):
                match y:
                    case asdl.StackASM(stack_offset):
                        instructions[index] = asdl.MovASM(x, asdl.RegASM(asdl.Reg.R10))
                        instructions.insert(
                            index + offset,
                            asdl.CmpASM(
                                asdl.RegASM(asdl.Reg.R10), asdl.StackASM(stack_offset)
                            ),
                        )
                        offset += 1
                    case asdl.ImmASM(i):
                        instructions[index] = asdl.MovASM(
                            asdl.ImmASM(i), asdl.RegASM(asdl.Reg.R11)
                        )
                        instructions.insert(
                            index + offset,
                            asdl.CmpASM(x, asdl.RegASM(asdl.Reg.R11)),
                        )
                        offset += 1
        index += offset
