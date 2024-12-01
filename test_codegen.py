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
        ast_tree = asdl.ProgramAST(
            asdl.FunctionAST(name, asdl.ReturnAST(asdl.ConstantAST(n)))
        )
        asm_ast = asdl.ProgramASM(
            asdl.FunctionASM(
                name, [asdl.MovASM(asdl.ImmASM(n), asdl.RegisterASM()), asdl.RetASM()]
            )
        )
        self.assertEqual(codegen.convert(ast_tree), asm_ast)


if __name__ == "__main__":
    unittest.main()
