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
        instructions.extend(convert_instruction(instruction))
    return instructions


def convert_instruction(tacky_instruction):
    match tacky_instruction:
        case asdl.ReturnTACKY(val):
            return [
                asdl.MovASM(convert_val(val), asdl.RegisterASM(asdl.RegASM.AX)),
                asdl.RetASM(),
            ]
        case asdl.UnaryTACKY(op, src, dst):
            dst = convert_val(dst)
            return [
                asdl.MovASM(convert_val(src), dst),
                asdl.UnaryASM(convert_unary_operator(op), dst),
            ]


def convert_val(val):
    match val:
        case asdl.ConstantTACKY(int):
            return asdl.ImmASM(int)
        case asdl.VarTACKY(identifier):
            return asdl.PseudoASM(identifier)


def convert_unary_operator(operator):
    match operator:
        case asdl.UnaryOperatorTACKY.COMPLEMENT:
            return asdl.UnaryOperatorASM.NOT
        case asdl.UnaryOperatorTACKY.NEGATE:
            return asdl.UnaryOperatorASM.NEG


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
            case asdl.UnaryASM(_, asdl.PseudoASM(identifier)):
                instructions[index].operand = replace(identifier)

    return abs(stack_offset)


def fix_instructions(instructions, stack_offset):
    index = 0
    instructions.insert(index, asdl.AllocateStackASM(stack_offset))
    index += 1
    r10 = asdl.RegisterASM(asdl.RegASM.R10)
    while index < len(instructions):
        offset = 1
        match instructions[index]:
            case asdl.MovASM(asdl.StackASM(_), asdl.StackASM(y)):
                instructions[index].dst = r10
                instructions.insert(index + offset, asdl.MovASM(r10, asdl.StackASM(y)))
                offset += 1
        index += offset
