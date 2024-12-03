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
import codegen
import random
import unittest


class TestCodegen(unittest.TestCase):
    def test_convert(self):
        n = random.randint(0, 255)
        name = "main"
        constant_tacky = asdl.ConstantTACKY(n)
        tacky_tree = asdl.ProgramTACKY(
            asdl.FunctionTACKY(name, [asdl.ReturnTACKY(constant_tacky)])
        )
        ax_reg = asdl.RegASM(asdl.AxASM())
        imm_asm = asdl.ImmASM(n)
        ret_asm = asdl.RetASM()
        asm_tree = asdl.ProgramASM(
            asdl.FunctionASM(
                name,
                [
                    asdl.AllocateStackASM(0),
                    asdl.MovASM(imm_asm, ax_reg),
                    ret_asm,
                ],
            )
        )
        self.assertEqual(codegen.convert(tacky_tree), asm_tree)

        tmp_0 = asdl.VarTACKY("tmp.0")
        complement_tacky = asdl.ComplementTACKY()
        tacky_tree.function_definition.body = [
            asdl.UnaryTACKY(complement_tacky, constant_tacky, tmp_0),
            asdl.ReturnTACKY(tmp_0),
        ]
        not_asm = asdl.NotASM()
        r10_reg = asdl.RegASM(asdl.R10ASM())
        tmp_0_stack = asdl.StackASM(-4)
        asm_tree.function_definition.instructions = [
            asdl.AllocateStackASM(4),
            asdl.MovASM(imm_asm, r10_reg),
            asdl.MovASM(r10_reg, tmp_0_stack),
            asdl.UnaryASM(not_asm, tmp_0_stack),
            asdl.MovASM(tmp_0_stack, ax_reg),
            ret_asm,
        ]
        self.assertEqual(codegen.convert(tacky_tree), asm_tree)

        negate_tacky = asdl.NegateTACKY()
        tmp_1 = asdl.VarTACKY("tmp.1")
        tmp_2 = asdl.VarTACKY("tmp.2")
        tacky_tree.function_definition.body = [
            asdl.UnaryTACKY(negate_tacky, constant_tacky, tmp_0),
            asdl.UnaryTACKY(complement_tacky, tmp_0, tmp_1),
            asdl.UnaryTACKY(negate_tacky, tmp_1, tmp_2),
            asdl.ReturnTACKY(tmp_2),
        ]
        neg_asm = asdl.NegASM()
        tmp_1_stack = asdl.StackASM(-8)
        tmp_2_stack = asdl.StackASM(-12)
        asm_tree.function_definition.instructions = [
            asdl.AllocateStackASM(12),
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
        self.assertEqual(codegen.convert(tacky_tree), asm_tree)


if __name__ == "__main__":
    unittest.main()
