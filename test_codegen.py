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

import asdl
import codegen
import unittest


class TestCodegen(TestCommon):
    def test_convert(self):
        self.assertEqual(
            codegen.convert(self.listing_1_1_tacky),
            self.listing_1_1_asm,
        )

        r10 = asdl.RegisterASM(asdl.RegASM.R10)
        stack_4, stack_8 = asdl.StackASM(-4), asdl.StackASM(-8)
        self.assertEqual(
            codegen.convert(self.listing_2_1_tacky),
            asdl.ProgramASM(
                asdl.FunctionASM(
                    "main",
                    [
                        asdl.AllocateStackASM(8),
                        asdl.MovASM(asdl.ImmASM(2), stack_4),
                        asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, stack_4),
                        asdl.MovASM(stack_4, r10),
                        asdl.MovASM(r10, stack_8),
                        asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, stack_8),
                        asdl.MovASM(stack_8, asdl.RegisterASM(asdl.RegASM.AX)),
                        asdl.RetASM(),
                    ],
                ),
            ),
        )


if __name__ == "__main__":
    unittest.main()
