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

_platform_system = platform.system()
IS_LINUX = _platform_system == "Linux"
IS_MACOS = _platform_system == "Darwin"


def output(tree):
    with io.StringIO() as s:
        output_program(tree, s)
        if IS_LINUX:
            print('.section .note.GNU-stack,"",@progbits', file=s)
        r = s.getvalue()
    return r


def output_program(tree, s):
    output_function(tree.function_definition, s)


def output_function(node, s):
    if IS_LINUX:
        name = node.name
    elif IS_MACOS:
        name = "_" + node.name
    print(
        f"""\
\t.globl {name}
{name}:
\tpushq %rbp
\tmovq %rsp, %rbp""",
        file=s,
    )
    output_instructions(node.instructions, s)


def output_instructions(instructions, s):
    for instruction in instructions:
        output_instruction(instruction, s)


def output_instruction(instruction, s):
    match instruction:
        case asdl.MovASM(src, dst):
            s.write("\tmovl ")
            output_operand(src, s)
            s.write(", ")
            output_operand(dst, s)
            s.write("\n")
        case asdl.UnaryASM(unop, operand):
            s.write("\t")
            output_unary_operator(unop, s)
            s.write(" ")
            output_operand(operand, s)
            s.write("\n")
        case asdl.BinaryASM(binop, src, dst):
            s.write("\t")
            output_binary_operator(binop, s)
            s.write(" ")
            output_operand(src, s)
            s.write(", ")
            output_operand(dst, s)
            s.write("\n")
        case asdl.CmpASM(o1, o2):
            s.write("\tcmpl ")
            output_operand(o1, s)
            s.write(", ")
            output_operand(o2, s)
            s.write("\n")
        case asdl.IdivASM(operand):
            s.write("\tidivl ")
            output_operand(operand, s)
            s.write("\n")
        case asdl.CdqASM():
            print("\tcdq", file=s)
        case asdl.JmpASM(identifier):
            s.write("\tjmp ")
            output_label(identifier, s)
            s.write("\n")
        case asdl.JmpCcASM(cond_code, identifier):
            s.write("\tj")
            output_cond_code(cond_code, s)
            s.write(" ")
            output_label(identifier, s)
            s.write("\n")
        case asdl.SetCcASM(cond_code, operand):
            s.write("\tset")
            output_cond_code(cond_code, s)
            s.write(" ")
            output_operand(operand, s, 1)
            s.write("\n")
        case asdl.LabelASM(identifier):
            output_label(identifier, s)
            print(":", file=s)
        case asdl.AllocateStackASM(int):
            print(f"\tsubq ${int}, %rsp", file=s)
        case asdl.RetASM():
            print(
                """\
\tmovq %rbp, %rsp
\tpopq %rbp
\tret""",
                file=s,
            )


def output_unary_operator(unop, s):
    s.write(unop.value)


output_binary_operator = output_unary_operator
output_cond_code = output_binary_operator


def output_operand(node, s, nbytes=4):
    match node:
        case asdl.ImmASM(int):
            s.write(f"${int}")
        case asdl.RegisterASM(asdl.RegASM.AX):
            match nbytes:
                case 4:
                    s.write("%eax")
                case 1:
                    s.write("%al")
        case asdl.RegisterASM(asdl.RegASM.DX):
            match nbytes:
                case 4:
                    s.write("%edx")
                case 1:
                    s.write("%dl")
        case asdl.RegisterASM(asdl.RegASM.R10):
            match nbytes:
                case 4:
                    s.write("%r10d")
                case 1:
                    s.write("%r10b")
        case asdl.RegisterASM(asdl.RegASM.R11):
            match nbytes:
                case 4:
                    s.write("%r11d")
                case 1:
                    s.write("%r11b")
        case asdl.StackASM(int):
            s.write(f"{int}(%rbp)")


def output_label(label, s):
    if IS_LINUX:
        s.write(".L" + label)
    elif IS_MACOS:
        s.write("L" + label)
