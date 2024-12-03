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
import emit
import random
import unittest


class TestEmit(unittest.TestCase):
    def test_output(self):
        n = str(random.randint(0, 255))
        name = "main"
        ax_reg = asdl.RegASM(asdl.AxASM())
        stack_offset = 0
        imm_asm = asdl.ImmASM(n)
        ret_asm = asdl.RetASM()
        asm_tree = asdl.ProgramASM(
            asdl.FunctionASM(
                name,
                [
                    asdl.AllocateStackASM(stack_offset),
                    asdl.MovASM(imm_asm, ax_reg),
                    ret_asm,
                ],
            )
        )
        if emit.SYSTEM == "Darwin":
            name = "_" + name
        common_prefix = f"\t.globl {name}\n{name}:\n\tpushq %rbp\n\tmovq %rsp, %rbp\n"
        common_suffix = "\tmovq %rbp, %rsp\n\tpopq %rbp\n\tret\n"
        expected = (
            common_prefix
            + f"\tsubq ${stack_offset}, %rsp\n\tmovl ${n}, %eax\n"
            + common_suffix
        )
        if emit.SYSTEM == "Linux":
            expected += emit.NO_EXEC_STACK
        self.assertEqual(emit.output(asm_tree), expected)

        stack_offset += 4
        r10_reg = asdl.RegASM(asdl.R10ASM())
        tmp_0_stack = asdl.StackASM(-stack_offset)
        not_asm = asdl.NotASM()
        asm_tree.function_definition.instructions = [
            asdl.AllocateStackASM(stack_offset),
            asdl.MovASM(imm_asm, r10_reg),
            asdl.MovASM(r10_reg, tmp_0_stack),
            asdl.UnaryASM(not_asm, tmp_0_stack),
            asdl.MovASM(tmp_0_stack, ax_reg),
            ret_asm,
        ]
        expected = (
            common_prefix
            + f"\tsubq ${stack_offset}, %rsp\n\tmovl ${n}, %r10d\n\tmovl %r10d, -4(%rbp)\n\tnotl -4(%rbp)\n\tmovl -4(%rbp), %eax\n"
            + common_suffix
        )
        if emit.SYSTEM == "Linux":
            expected += emit.NO_EXEC_STACK
        self.assertEqual(emit.output(asm_tree), expected)

        stack_offset += 8
        neg_asm = asdl.NegASM()
        tmp_1_stack = asdl.StackASM(-8)
        tmp_2_stack = asdl.StackASM(-12)
        asm_tree.function_definition.instructions = [
            asdl.AllocateStackASM(stack_offset),
            asdl.MovASM(imm_asm, r10_reg),
            asdl.MovASM(r10_reg, tmp_0_stack),
            asdl.UnaryASM(neg_asm, tmp_0_stack),
            asdl.MovASM(tmp_0_stack, r10_reg),
            asdl.MovASM(r10_reg, tmp_1_stack),
            asdl.UnaryASM(not_asm, tmp_1_stack),
            asdl.MovASM(tmp_1_stack, r10_reg),
            asdl.MovASM(r10_reg, tmp_2_stack),
            asdl.UnaryASM(neg_asm, tmp_2_stack),
            asdl.MovASM(tmp_2_stack, ax_reg),
            ret_asm,
        ]
        expected = (
            common_prefix
            + f"\tsubq ${stack_offset}, %rsp\n\tmovl ${n}, %r10d\n\tmovl %r10d, -4(%rbp)\n\tnegl -4(%rbp)\n\tmovl -4(%rbp), %r10d\n"
            + "\tmovl %r10d, -8(%rbp)\n\tnotl -8(%rbp)\n\tmovl -8(%rbp), %r10d\n\tmovl %r10d, -12(%rbp)\n\tnegl -12(%rbp)\n\tmovl -12(%rbp), %eax\n"
            + common_suffix
        )
        if emit.SYSTEM == "Linux":
            expected += emit.NO_EXEC_STACK
        self.assertEqual(emit.output(asm_tree), expected)


if __name__ == "__main__":
    unittest.main()
