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


def convert_instructions(tacky_instructions):
    instructions = []
    for instruction in tacky_instructions:
        match instruction:
            case asdl.ReturnTACKY(val):
                instructions += [
                    asdl.MovASM(convert_val(val), asdl.RegisterASM(asdl.RegASM.AX)),
                    asdl.RetASM(),
                ]
            case asdl.UnaryTACKY(unop, src, dst):
                src, dst = convert_val(src), convert_val(dst)
                if unop == asdl.UnaryOperatorTACKY.NOT:
                    imm_0 = asdl.ImmASM(0)
                    instructions += [
                        asdl.CmpASM(imm_0, src),
                        asdl.MovASM(imm_0, dst),
                        asdl.SetCcASM(asdl.CondCodeASM.E, dst),
                    ]
                else:
                    instructions += [
                        asdl.MovASM(src, dst),
                        asdl.UnaryASM(convert_arithmetic_operator(unop), dst),
                    ]
            case asdl.BinaryTACKY(binop, src1, src2, dst):
                src1, src2, dst = (
                    convert_val(src1),
                    convert_val(src2),
                    convert_val(dst),
                )
                match binop:
                    case asdl.BinaryOperatorTACKY.DIVIDE:
                        ax = asdl.RegisterASM(asdl.RegASM.AX)
                        instructions += [
                            asdl.MovASM(src1, ax),
                            asdl.CdqASM(),
                            asdl.IdivASM(src2),
                            asdl.MovASM(ax, dst),
                        ]
                    case asdl.BinaryOperatorTACKY.REMAINDER:
                        instructions += [
                            asdl.MovASM(src1, asdl.RegisterASM(asdl.RegASM.AX)),
                            asdl.CdqASM(),
                            asdl.IdivASM(src2),
                            asdl.MovASM(asdl.RegisterASM(asdl.RegASM.DX), dst),
                        ]
                    case (
                        asdl.BinaryOperatorTACKY.EQUAL
                        | asdl.BinaryOperatorTACKY.NOT_EQUAL
                        | asdl.BinaryOperatorTACKY.LESS_THAN
                        | asdl.BinaryOperatorTACKY.LESS_OR_EQUAL
                        | asdl.BinaryOperatorTACKY.GREATER_THAN
                        | asdl.BinaryOperatorTACKY.GREATER_OR_EQUAL
                    ):
                        instructions += [
                            asdl.CmpASM(src2, src1),
                            asdl.MovASM(asdl.ImmASM(0), dst),
                            asdl.SetCcASM(convert_relational_operator(binop), dst),
                        ]
                    case _:
                        instructions += [
                            asdl.MovASM(src1, dst),
                            asdl.BinaryASM(
                                convert_arithmetic_operator(binop), src2, dst
                            ),
                        ]
            case asdl.CopyTACKY(src, dst):
                instructions.append(asdl.MovASM(convert_val(src), convert_val(dst)))
            case asdl.JumpTACKY(target):
                instructions.append(asdl.JmpASM(target))
            case asdl.JumpIfZeroTACKY(condition, target):
                instructions += [
                    asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                    asdl.JmpCcASM(asdl.CondCodeASM.E, target),
                ]
            case asdl.JumpIfNotZeroTACKY(condition, target):
                instructions += [
                    asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                    asdl.JmpCcASM(asdl.CondCodeASM.NE, target),
                ]
            case asdl.LabelTACKY(identifier):
                instructions.append(asdl.LabelASM(identifier))
    return instructions


def convert_relational_operator(operator):
    match operator:
        case asdl.BinaryOperatorTACKY.EQUAL:
            return asdl.CondCodeASM.E
        case asdl.BinaryOperatorTACKY.NOT_EQUAL:
            return asdl.CondCodeASM.NE
        case asdl.BinaryOperatorTACKY.LESS_THAN:
            return asdl.CondCodeASM.L
        case asdl.BinaryOperatorTACKY.LESS_OR_EQUAL:
            return asdl.CondCodeASM.LE
        case asdl.BinaryOperatorTACKY.GREATER_THAN:
            return asdl.CondCodeASM.G
        case asdl.BinaryOperatorTACKY.GREATER_OR_EQUAL:
            return asdl.CondCodeASM.GE


def convert_arithmetic_operator(operator):
    match operator:
        case asdl.UnaryOperatorTACKY.COMPLEMENT:
            return asdl.UnaryOperatorASM.NOT
        case asdl.UnaryOperatorTACKY.NEGATE:
            return asdl.UnaryOperatorASM.NEG
        case asdl.UnaryOperatorTACKY.NOT:
            return asdl.UnaryOperatorASM.NOT
        case asdl.BinaryOperatorTACKY.ADD:
            return asdl.BinaryOperatorASM.ADD
        case asdl.BinaryOperatorTACKY.SUBTRACT:
            return asdl.BinaryOperatorASM.SUB
        case asdl.BinaryOperatorTACKY.MULTIPLY:
            return asdl.BinaryOperatorASM.MULT


def convert_val(val):
    match val:
        case asdl.ConstantTACKY(int):
            return asdl.ImmASM(int)
        case asdl.VarTACKY(identifier):
            return asdl.PseudoASM(identifier)


def replace_pseudoregisters(instructions):
    def replace(identifier):
        if identifier not in identifiers_offsets:
            nonlocal stack_offset
            stack_offset -= 4
            identifiers_offsets[identifier] = stack_offset
        return asdl.StackASM(identifiers_offsets[identifier])

    identifiers_offsets, stack_offset = {}, 0
    for index, instruction in enumerate(instructions[:]):
        match instruction:
            case asdl.MovASM(src, dst):
                if isinstance(src, asdl.PseudoASM):
                    instructions[index].src = replace(src.identifier)
                if isinstance(dst, asdl.PseudoASM):
                    instructions[index].dst = replace(dst.identifier)
            case (
                asdl.UnaryASM(_, asdl.PseudoASM(identifier))
                | asdl.IdivASM(asdl.PseudoASM(identifier))
                | asdl.SetCcASM(_, asdl.PseudoASM(identifier))
            ):
                instructions[index].operand = replace(identifier)
            case asdl.BinaryASM(_, o1, o2) | asdl.CmpASM(o1, o2):
                if isinstance(o1, asdl.PseudoASM):
                    instructions[index].o1 = replace(o1.identifier)
                if isinstance(o2, asdl.PseudoASM):
                    instructions[index].o2 = replace(o2.identifier)

    return abs(stack_offset)


def fix_instructions(instructions, stack_offset):
    index = 0
    instructions.insert(index, asdl.AllocateStackASM(stack_offset))
    index += 1
    r10 = asdl.RegisterASM(asdl.RegASM.R10)
    r11 = asdl.RegisterASM(asdl.RegASM.R11)
    while index < len(instructions):
        offset = 1
        match instructions[index]:
            case asdl.MovASM(asdl.StackASM(_), asdl.StackASM(y)):
                instructions[index].dst = r10
                instructions.insert(index + offset, asdl.MovASM(r10, asdl.StackASM(y)))
                offset += 1
            case asdl.BinaryASM(binop, o, asdl.StackASM(i)):
                match binop:
                    case (
                        asdl.BinaryOperatorASM.ADD
                        | asdl.BinaryOperatorASM.SUB
                    ) if isinstance(o, asdl.StackASM):
                        instructions[index] = asdl.MovASM(o, r10)
                        instructions.insert(
                            index + offset, asdl.BinaryASM(binop, r10, asdl.StackASM(i))
                        )
                        offset += 1
                    case asdl.BinaryOperatorASM.MULT:
                        dst = asdl.StackASM(i)
                        instructions[index] = asdl.MovASM(dst, r11)
                        instructions.insert(
                            index + offset, asdl.BinaryASM(binop, o, r11)
                        )
                        offset += 1
                        instructions.insert(index + offset, asdl.MovASM(r11, dst))
                        offset += 1
            case asdl.CmpASM(x, y):
                match x, y:
                    case asdl.StackASM(_), asdl.StackASM(v):
                        instructions[index] = asdl.MovASM(x, r10)
                        instructions.insert(
                            index + offset, asdl.CmpASM(r10, asdl.StackASM(v))
                        )
                        offset += 1
                    case v, asdl.ImmASM(i):
                        instructions[index] = asdl.MovASM(asdl.ImmASM(i), r11)
                        instructions.insert(index + offset, asdl.CmpASM(v, r11))
                        offset += 1
            case asdl.IdivASM(asdl.ImmASM(int)):
                instructions[index] = asdl.MovASM(asdl.ImmASM(int), r10)
                instructions.insert(index + offset, asdl.IdivASM(r10))
                offset += 1
        index += offset
