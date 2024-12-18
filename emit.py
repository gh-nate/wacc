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
import io
import platform

NO_EXEC_STACK = '.section .note.GNU-stack,"",@progbits'
SYSTEM = platform.system()


def output(tree):
    with io.StringIO() as s:
        output_program(tree, s)
        if SYSTEM == "Linux":
            print(NO_EXEC_STACK, file=s)
        r = s.getvalue()
    return r


def output_program(tree, s):
    output_function(tree.function_definition, s)


def output_function(node, s):
    name = node.name
    if SYSTEM == "Darwin":
        name = "_" + name
    print(f"\t.globl {name}\n{name}:\n\tpushq %rbp\n\tmovq %rsp, %rbp", file=s)
    output_instructions(node.instructions, s)


def output_instructions(instructions, s):
    for instruction in instructions:
        match instruction:
            case asdl.MovASM(src, dst):
                s.write("\tmovl ")
                output_operand(src, s)
                s.write(", ")
                output_operand(dst, s)
                s.write("\n")
            case asdl.UnaryASM(unary_operator, operand):
                match unary_operator:
                    case asdl.UnaryOperatorASM.NEG:
                        s.write("\tnegl ")
                    case asdl.UnaryOperatorASM.NOT:
                        s.write("\tnotl ")
                output_operand(operand, s)
                s.write("\n")
            case asdl.BinaryASM(binary_operator, src, dst):
                match binary_operator:
                    case asdl.BinaryOperatorASM.ADD:
                        s.write("\taddl ")
                    case asdl.BinaryOperatorASM.SUB:
                        s.write("\tsubl ")
                    case asdl.BinaryOperatorASM.MULT:
                        s.write("\timull ")
                output_operand(src, s)
                s.write(", ")
                output_operand(dst, s)
                s.write("\n")
            case asdl.CmpASM(lhs, rhs):
                s.write("\tcmpl ")
                output_operand(lhs, s)
                s.write(", ")
                output_operand(rhs, s)
                s.write("\n")
            case asdl.IdivASM(operand):
                s.write("\tidivl ")
                output_operand(operand, s)
                s.write("\n")
            case asdl.CdqASM():
                print("\tcdq", file=s)
            case asdl.JmpASM(label):
                s.write("\tjmp ")
                output_label(label, s)
                s.write("\n")
            case asdl.JmpCCASM(cond_code, label):
                s.write("\tj")
                output_cond_code(cond_code, s)
                s.write(" ")
                output_label(label, s)
                s.write("\n")
            case asdl.SetCCASM(cond_code, operand):
                s.write("\tset")
                output_cond_code(cond_code, s)
                s.write(" ")
                output_operand(operand, s, True)
                s.write("\n")
            case asdl.LabelASM(label):
                output_label(label, s)
                print(":", file=s)
            case asdl.AllocateStackASM(i):
                print(f"\tsubq ${i}, %rsp", file=s)
            case asdl.RetASM():
                print("\tmovq %rbp, %rsp", file=s)
                print("\tpopq %rbp", file=s)
                print("\tret", file=s)


def output_operand(node, s, is_byte=False):
    match node:
        case asdl.RegASM(asdl.Reg.AX):
            s.write("%al" if is_byte else "%eax")
        case asdl.RegASM(asdl.Reg.DX):
            s.write("%dl" if is_byte else "%edx")
        case asdl.RegASM(asdl.Reg.R10):
            s.write("%r10b" if is_byte else "%r10d")
        case asdl.RegASM(asdl.Reg.R11):
            s.write("%r11b" if is_byte else "%r11d")
        case asdl.StackASM(i):
            s.write(f"{i}(%rbp)")
        case asdl.ImmASM(int):
            s.write(f"${int}")


def output_cond_code(cond_code, s):
    s.write(cond_code.value)


def output_label(label, s):
    if SYSTEM == "Linux":
        s.write(f".L{label}")
    elif SYSTEM == "Darwin":
        s.write(f"L{label}")
