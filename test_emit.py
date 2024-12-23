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
        def fill(*dialogue):
            name = "main"
            if emit.IS_MACOS:
                name = "_" + name
            asm = f"""\
\t.globl {name}
{name}:
\tpushq %rbp
\tmovq %rsp, %rbp
"""
            asm += "\n".join(dialogue)
            asm += """
\tmovq %rbp, %rsp
\tpopq %rbp
\tret
\tmovl $0, %eax
\tmovq %rbp, %rsp
\tpopq %rbp
\tret
"""
            if emit.IS_LINUX:
                asm += emit.NO_EXEC_STACK
            return asm

        self.assertEqual(
            emit.output(self.listing_1_1_asm),
            fill("\tsubq $0, %rsp", "\tmovl $2, %eax"),
        )

        self.assertEqual(
            emit.output(self.listing_2_1_asm),
            fill(
                "\tsubq $8, %rsp",
                "\tmovl $2, -4(%rbp)",
                "\tnegl -4(%rbp)",
                "\tmovl -4(%rbp), %r10d",
                "\tmovl %r10d, -8(%rbp)",
                "\tnotl -8(%rbp)",
                "\tmovl -8(%rbp), %eax",
            ),  # Listing 2-2
        )

        self.assertEqual(
            emit.output(self.listing_5_13_asm),
            fill(
                "\tsubq $16, %rsp",
                "\tmovl $10, -4(%rbp)",
                "\taddl $1, -4(%rbp)",
                "\tmovl -4(%rbp), %r10d",
                "\tmovl %r10d, -8(%rbp)",
                "\tmovl -8(%rbp), %r10d",
                "\tmovl %r10d, -12(%rbp)",
                "\tmovl -12(%rbp), %r11d",
                "\timull $2, %r11d",
                "\tmovl %r11d, -12(%rbp)",
                "\tmovl -12(%rbp), %r10d",
                "\tmovl %r10d, -16(%rbp)",
                "\tmovl -16(%rbp), %eax",
            ),
        )


if __name__ == "__main__":
    unittest.main()
