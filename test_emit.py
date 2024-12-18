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

from test_common import TestCommon

import emit
import unittest


class TestEmit(TestCommon):
    def test_output(self):
        def fill(interlude):
            name = "main"
            if emit.SYSTEM == "Darwin":
                name = "_" + name
            prologue = f"\t.globl {name}\n{name}:\n\tpushq %rbp\n\tmovq %rsp, %rbp\n"
            epilogue = "\tmovq %rbp, %rsp\n\tpopq %rbp\n\tret\n"
            if emit.SYSTEM == "Linux":
                epilogue += emit.NO_EXEC_STACK
            return prologue + interlude + epilogue

        s = """\
\tsubq $0, %rsp
\tmovl $2, %eax
"""
        self.assertEqual(emit.output(self.listing_1_1_asm), fill(s))

        s = "\tsubq $8, %rsp\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnegl -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tnotl -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %eax\n"
        self.assertEqual(emit.output(self.listing_2_1_asm), fill(s))

        s = "\tsubq $4, %rsp\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnotl -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %eax\n"
        self.assertEqual(emit.output(self.table_2_1_row_2_asm), fill(s))

        s = "\tsubq $8, %rsp\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnegl -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tnegl -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %eax\n"
        self.assertEqual(emit.output(self.listing_2_4_asm), fill(s))

        s = "\tsubq $12, %rsp\n"
        s += "\tmovl $8, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnegl -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tnotl -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %r10d\n"
        s += "\tmovl %r10d, -12(%rbp)\n"
        s += "\tnegl -12(%rbp)\n"
        s += "\tmovl -12(%rbp), %eax\n"
        self.assertEqual(emit.output(self.table_2_1_row_3_asm), fill(s))

        s = "\tsubq $8, %rsp\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r11d\n"
        s += "\timull $3, %r11d\n"
        s += "\tmovl %r11d, -4(%rbp)\n"
        s += "\tmovl $1, %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\taddl %r10d, -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %eax\n"
        self.assertEqual(emit.output(self.figure_3_1_asm), fill(s))

        s = "\tsubq $8, %rsp\n"
        s += "\tmovl $1, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tmovl $2, %r10d\n"
        s += "\taddl %r10d, -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %r11d\n"
        s += "\timull $3, %r11d\n"
        s += "\tmovl %r11d, -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %eax\n"
        self.assertEqual(emit.output(self.figure_3_2_asm), fill(s))

        s = "\tsubq $12, %rsp\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r11d\n"
        s += "\timull $3, %r11d\n"
        s += "\tmovl %r11d, -4(%rbp)\n"
        s += "\tmovl $1, %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\taddl %r10d, -8(%rbp)\n"
        s += "\tmovl -8(%rbp), %r10d\n"
        s += "\tmovl %r10d, -12(%rbp)\n"
        s += "\tmovl $4, %r10d\n"
        s += "\taddl %r10d, -12(%rbp)\n"
        s += "\tmovl -12(%rbp), %eax\n"
        self.assertEqual(emit.output(self.dealing_with_precedence_asm), fill(s))

        s = "\tsubq $16, %rsp\n"
        s += "\tmovl $1, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tmovl -4(%rbp), %r11d\n"
        s += "\timull $2, %r11d\n"
        s += "\tmovl %r11d, -4(%rbp)\n"
        s += "\tmovl $4, %r10d\n"
        s += "\tmovl %r10d, -8(%rbp)\n"
        s += "\tmovl $5, %r10d\n"
        s += "\taddl %r10d, -8(%rbp)\n"
        s += "\tmovl $3, %r10d\n"
        s += "\tmovl %r10d, -12(%rbp)\n"
        s += "\tmovl -12(%rbp), %r11d\n"
        s += "\timull -8(%rbp), %r11d\n"
        s += "\tmovl %r11d, -12(%rbp)\n"
        s += "\tmovl -4(%rbp), %r10d\n"
        s += "\tmovl %r10d, -16(%rbp)\n"
        s += "\tmovl -12(%rbp), %r10d\n"
        s += "\tsubl %r10d, -16(%rbp)\n"
        s += "\tmovl -16(%rbp), %eax\n"
        self.assertEqual(emit.output(self.precedence_climbing_in_action_asm), fill(s))

        s = "\tsubq $4, %rsp\n"
        s += "\tmovl $1, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnegl -4(%rbp)\n"
        if emit.SYSTEM == "Linux":
            s += "\tjmp .Lthere\n"
        elif emit.SYSTEM == "Darwin":
            s += "\tjmp Lthere\n"
        s += "\tmovl $2, %r10d\n"
        s += "\tmovl %r10d, -4(%rbp)\n"
        s += "\tnegl -4(%rbp)\n"
        if emit.SYSTEM == "Linux":
            s += ".Lthere:\n"
        elif emit.SYSTEM == "Darwin":
            s += "Lthere:\n"
        s += "\tmovl -4(%rbp), %eax\n"
        self.assertEqual(emit.output(self.listing_4_5_asm), fill(s))


if __name__ == "__main__":
    unittest.main()
