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
import unittest


class TestCommon(unittest.TestCase):
    def setUp(self):
        def fill_tokens(*tokens):
            return (
                ["int", "main", "(", "void", ")", "{", "return"]
                + [*tokens]
                + [";", "}"]
            )

        def fill_ast(exp):
            return asdl.ProgramAST(asdl.FunctionAST("main", asdl.ReturnAST(exp)))

        self.listing_1_1_tokens = fill_tokens("2")
        self.listing_1_1_ast = fill_ast(asdl.ConstantAST(2))
        self.listing_1_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [asdl.MovASM(asdl.ImmASM(2), asdl.RegisterASM()), asdl.RetASM()],
            )
        )

        self.listing_2_1_tokens = fill_tokens("~", "(", "-", "2", ")")
        self.listing_2_1_ast = fill_ast(
            asdl.UnaryAST(
                asdl.UnaryOperatorAST.COMPLEMENT,
                asdl.UnaryAST(asdl.UnaryOperatorAST.NEGATE, asdl.ConstantAST(2)),
            )
        )

        self.listing_2_3_tokens = fill_tokens("--", "2")

        self.listing_2_4_tokens = fill_tokens("-", "(", "-", "2", ")")
