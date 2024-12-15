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
    stack_offset = replace_pseudoregisters(tree)
    fix_instructions(tree, stack_offset)
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
                new_instructions += [
                    asdl.MovASM(convert_val(src), dst),
                    asdl.UnaryASM(convert_unary_operator(unop), dst),
                ]
            case asdl.BinaryTACKY(asdl.BinaryOperatorTACKY.DIVIDE, src1, src2, dst):
                new_instructions += [
                    asdl.MovASM(convert_val(src1), asdl.RegASM(asdl.Reg.AX)),
                    asdl.CdqASM(),
                    asdl.IdivASM(convert_val(src2)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.AX), convert_val(dst)),
                ]
            case asdl.BinaryTACKY(asdl.BinaryOperatorTACKY.REMAINDER, src1, src2, dst):
                new_instructions += [
                    asdl.MovASM(convert_val(src1), asdl.RegASM(asdl.Reg.AX)),
                    asdl.CdqASM(),
                    asdl.IdivASM(convert_val(src2)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.DX), convert_val(dst)),
                ]
            case asdl.BinaryTACKY(op, src1, src2, dst):
                dst = convert_val(dst)
                new_instructions += [
                    asdl.MovASM(convert_val(src1), dst),
                    asdl.BinaryASM(convert_binary_operator(op), convert_val(src2), dst),
                ]
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


def replace_pseudoregisters(tree):
    def replace(identifier, stack_offset, identifiers_offsets):
        if identifier not in identifiers_offsets:
            stack_offset -= 4
            identifiers_offsets[identifier] = stack_offset
        return asdl.StackASM(identifiers_offsets[identifier]), stack_offset

    identifiers_offsets, stack_offset = {}, 0
    instructions = tree.function_definition.instructions
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
    return abs(stack_offset)


def fix_instructions(tree, stack_offset):
    index, instructions = (
        0,
        tree.function_definition.instructions,
    )
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
            case asdl.BinaryASM(
                asdl.BinaryOperatorASM.ADD, src, asdl.StackASM(stack_offset)
            ):
                instructions[index] = asdl.MovASM(src, asdl.RegASM(asdl.Reg.R10))
                instructions.insert(
                    index + offset,
                    asdl.BinaryASM(
                        asdl.BinaryOperatorASM.ADD,
                        asdl.RegASM(asdl.Reg.R10),
                        asdl.StackASM(stack_offset),
                    ),
                )
                offset += 1
            case asdl.BinaryASM(
                asdl.BinaryOperatorASM.SUB, src, asdl.StackASM(stack_offset)
            ):
                instructions[index] = asdl.MovASM(src, asdl.RegASM(asdl.Reg.R10))
                instructions.insert(
                    index + offset,
                    asdl.BinaryASM(
                        asdl.BinaryOperatorASM.SUB,
                        asdl.RegASM(asdl.Reg.R10),
                        asdl.StackASM(stack_offset),
                    ),
                )
                offset += 1
            case asdl.BinaryASM(
                asdl.BinaryOperatorASM.MULT, src, asdl.StackASM(stack_offset)
            ):
                instructions[index] = asdl.MovASM(
                    asdl.StackASM(stack_offset), asdl.RegASM(asdl.Reg.R11)
                )
                instructions.insert(
                    index + offset,
                    asdl.BinaryASM(
                        asdl.BinaryOperatorASM.MULT, src, asdl.RegASM(asdl.Reg.R11)
                    ),
                )
                offset += 1
                instructions.insert(
                    index + offset,
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R11), asdl.StackASM(stack_offset)),
                )
                offset += 1
        index += offset
