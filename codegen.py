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

ARG_REGISTERS = [
    asdl.RegASM.DI,
    asdl.RegASM.SI,
    asdl.RegASM.DX,
    asdl.RegASM.CX,
    asdl.RegASM.R8,
    asdl.RegASM.R9,
]
NUM_ARGS_IN_REGISTERS = len(ARG_REGISTERS)


def convert(tree, symbols):
    tree = convert_program(tree)
    for item in tree.top_level:
        match item:
            case asdl.FunctionASM(_, _, instructions):
                stack_offset = replace_pseudoregisters(instructions, symbols)
                fix_instructions(instructions, stack_offset)
    return tree


def convert_program(tree):
    return asdl.ProgramASM(convert_top_level(tree.top_level))


def convert_top_level(top_level):
    items = []
    for item in top_level:
        match item:
            case asdl.FunctionTACKY():
                items.append(convert_function_definition(item))
            case asdl.StaticVariableTACKY():
                items.append(convert_static_variable(item))
    return items


def convert_function_definition(node):
    instructions = []
    for arg_register, param in zip(ARG_REGISTERS, node.params[:NUM_ARGS_IN_REGISTERS]):
        instructions.append(
            asdl.MovASM(asdl.RegisterASM(arg_register), asdl.PseudoASM(param))
        )
    stack_offset = 16
    for param in node.params[NUM_ARGS_IN_REGISTERS:]:
        instructions.append(
            asdl.MovASM(asdl.StackASM(stack_offset), asdl.PseudoASM(param))
        )
        stack_offset += 8
    return asdl.FunctionASM(
        node.identifier, node.globl, instructions + convert_instructions(node.body)
    )


def convert_static_variable(node):
    return asdl.StaticVariableASM(node.identifier, node.globl, node.init)


def convert_function_call(fc):
    instructions = []

    # Adjust stack alignment.
    register_args, stack_args = (
        fc.args[:NUM_ARGS_IN_REGISTERS],
        fc.args[NUM_ARGS_IN_REGISTERS:],
    )
    stack_args.reverse()
    if stack_padding := 8 if len(stack_args) % 2 else 0:
        instructions.append(asdl.AllocateStackASM(stack_padding))

    # Pass args in registers.
    for arg_register, tacky_arg in zip(ARG_REGISTERS, register_args):
        instructions.append(
            asdl.MovASM(convert_val(tacky_arg), asdl.RegisterASM(arg_register))
        )

    # Pass args on stack.
    rax = asdl.RegisterASM(asdl.RegASM.AX)
    for tacky_arg in stack_args:
        assembly_arg = convert_val(tacky_arg)
        if isinstance(assembly_arg, asdl.ImmASM):
            instructions.append(asdl.PushASM(assembly_arg))
        else:
            instructions += [
                asdl.MovASM(assembly_arg, rax),
                asdl.PushASM(rax),
            ]

    instructions.append(asdl.CallASM(fc.fun_name))

    # Adjust stack pointer.
    if bytes_to_remove := 8 * len(stack_args) + stack_padding:
        instructions.append(asdl.DeallocateStackASM(bytes_to_remove))

    # Retrieve return value.
    instructions.append(asdl.MovASM(rax, convert_val(fc.dst)))
    return instructions


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
        case asdl.UnaryTACKY(unop, src, dst):
            src, dst = convert_val(src), convert_val(dst)
            if unop == asdl.UnaryOperatorTACKY.NOT:
                imm_0 = asdl.ImmASM(0)
                return [
                    asdl.CmpASM(imm_0, src),
                    asdl.MovASM(imm_0, dst),
                    asdl.SetCcASM(asdl.CondCodeASM.E, dst),
                ]
            else:
                return [
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
                    return [
                        asdl.MovASM(src1, ax),
                        asdl.CdqASM(),
                        asdl.IdivASM(src2),
                        asdl.MovASM(ax, dst),
                    ]
                case asdl.BinaryOperatorTACKY.REMAINDER:
                    return [
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
                    return [
                        asdl.CmpASM(src2, src1),
                        asdl.MovASM(asdl.ImmASM(0), dst),
                        asdl.SetCcASM(convert_relational_operator(binop), dst),
                    ]
                case _:
                    return [
                        asdl.MovASM(src1, dst),
                        asdl.BinaryASM(convert_arithmetic_operator(binop), src2, dst),
                    ]
        case asdl.CopyTACKY(src, dst):
            return [asdl.MovASM(convert_val(src), convert_val(dst))]
        case asdl.JumpTACKY(target):
            return [asdl.JmpASM(target)]
        case asdl.JumpIfZeroTACKY(condition, target):
            return [
                asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                asdl.JmpCcASM(asdl.CondCodeASM.E, target),
            ]
        case asdl.JumpIfNotZeroTACKY(condition, target):
            return [
                asdl.CmpASM(asdl.ImmASM(0), convert_val(condition)),
                asdl.JmpCcASM(asdl.CondCodeASM.NE, target),
            ]
        case asdl.LabelTACKY(identifier):
            return [asdl.LabelASM(identifier)]
        case asdl.FunCallTACKY():
            return convert_function_call(tacky_instruction)


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


def convert_val(val):
    match val:
        case asdl.ConstantTACKY(int):
            return asdl.ImmASM(int)
        case asdl.VarTACKY(identifier):
            return asdl.PseudoASM(identifier)


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


def replace_pseudoregisters(instructions, symbols):
    def replace(identifier):
        if identifier not in identifiers_offsets:
            if identifier in symbols and isinstance(
                symbols[identifier].attrs, asdl.StaticAttrTC
            ):
                return asdl.DataASM(identifier)
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
                | asdl.PushASM(asdl.PseudoASM(identifier))
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
    instructions.insert(
        index, asdl.AllocateStackASM(stack_offset + 16 - stack_offset % 16)
    )
    index += 1
    r10 = asdl.RegisterASM(asdl.RegASM.R10)
    r11 = asdl.RegisterASM(asdl.RegASM.R11)
    while index < len(instructions):
        offset = 1
        match instructions[index]:
            case asdl.MovASM(asdl.StackASM(), asdl.StackASM(y)) | asdl.MovASM(
                asdl.DataASM(), asdl.StackASM(y)
            ):
                instructions[index].dst = r10
                instructions.insert(index + offset, asdl.MovASM(r10, asdl.StackASM(y)))
                offset += 1
            case asdl.MovASM(asdl.StackASM(), asdl.DataASM(y)) | asdl.MovASM(
                asdl.DataASM(), asdl.DataASM(y)
            ):
                instructions[index].dst = r10
                instructions.insert(index + offset, asdl.MovASM(r10, asdl.DataASM(y)))
                offset += 1
            case asdl.BinaryASM(op, o, asdl.StackASM(i)) | asdl.BinaryASM(
                op, o, asdl.DataASM(i)
            ):
                match i:
                    case int():
                        dst = asdl.StackASM(i)
                    case str():
                        dst = asdl.DataASM(i)
                match op:
                    case asdl.BinaryOperatorASM.ADD | asdl.BinaryOperatorASM.SUB if (
                        isinstance(o, asdl.StackASM) or isinstance(o, asdl.DataASM)
                    ):
                        instructions[index] = asdl.MovASM(o, r10)
                        instructions.insert(
                            index + offset, asdl.BinaryASM(op, r10, dst)
                        )
                        offset += 1
                    case asdl.BinaryOperatorASM.MULT:
                        instructions[index] = asdl.MovASM(dst, r11)
                        instructions.insert(index + offset, asdl.BinaryASM(op, o, r11))
                        offset += 1
                        instructions.insert(index + offset, asdl.MovASM(r11, dst))
                        offset += 1
            case asdl.CmpASM(x, y):
                match x, y:
                    case (asdl.StackASM(), asdl.StackASM(v)) | (
                        asdl.DataASM(),
                        asdl.StackASM(v),
                    ):
                        instructions[index] = asdl.MovASM(x, r10)
                        instructions.insert(
                            index + offset, asdl.CmpASM(r10, asdl.StackASM(v))
                        )
                        offset += 1
                    case (asdl.StackASM(), asdl.DataASM(v)) | (
                        asdl.DataASM(),
                        asdl.DataASM(v),
                    ):
                        instructions[index] = asdl.MovASM(x, r10)
                        instructions.insert(
                            index + offset, asdl.CmpASM(r10, asdl.DataASM(v))
                        )
                        offset += 1
                    case _, asdl.ImmASM(y):
                        instructions[index] = asdl.MovASM(asdl.ImmASM(y), r11)
                        instructions.insert(index + offset, asdl.CmpASM(x, r11))
                        offset += 1
            case asdl.IdivASM(asdl.ImmASM(i)):
                instructions[index] = asdl.MovASM(asdl.ImmASM(i), r10)
                instructions.insert(index + offset, asdl.IdivASM(r10))
                offset += 1
        index += offset
