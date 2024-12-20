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
        name = "main"
        if emit.IS_MACOS:
            name = "_" + name
        asm = f"""\t.globl {name}
{name}:
\tmovl $2, %eax
\tret
"""
        if emit.IS_LINUX:
            asm += emit.NO_EXEC_STACK
        self.assertEqual(emit.output(self.listing_1_1_asm), asm)


if __name__ == "__main__":
    unittest.main()
