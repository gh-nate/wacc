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

# import asdl
# import emit
# import random
import unittest


class TestEmit(unittest.TestCase):
    def test_output(self):
        pass
        # n = str(random.randint(0, 255))
        # name = "main"
        # asm_tree = asdl.ProgramASM(
        #     asdl.FunctionASM(
        #         name, [asdl.MovASM(asdl.ImmASM(n), asdl.RegisterASM()), asdl.RetASM()]
        #     )
        # )
        # if emit.SYSTEM == "Darwin":
        #     name = "_" + name
        # expected = f"\t.globl {name}\n{name}:\n\tmovl ${n}, %eax\n\tret\n"
        # if emit.SYSTEM == "Linux":
        #     expected += emit.NO_EXEC_STACK
        # self.assertEqual(emit.output(asm_tree), expected)


if __name__ == "__main__":
    unittest.main()
