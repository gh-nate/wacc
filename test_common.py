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
        self.listing_1_1_tokens = [
            "int",
            "main",
            "(",
            "void",
            ")",
            "{",
            "return",
            "2",
            ";",
            "}",
        ]
        self.listing_1_1_ast = asdl.ProgramAST(
            asdl.FunctionAST("main", asdl.ReturnAST(asdl.ConstantAST(2)))
        )
        self.listing_1_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [asdl.MovASM(asdl.ImmASM(2), asdl.RegisterASM()), asdl.RetASM()],
            )
        )

        self.listing_2_1_tokens = [
            "int",
            "main",
            "(",
            "void",
            ")",
            "{",
            "return",
            "~",
            "(",
            "-",
            "2",
            ")",
            ";",
            "}",
        ]
        self.listing_2_1_ast = asdl.ProgramAST(
            asdl.FunctionAST(
                "main",
                asdl.ReturnAST(
                    asdl.UnaryAST(
                        asdl.UnaryOperatorAST.COMPLEMENT,
                        asdl.UnaryAST(
                            asdl.UnaryOperatorAST.NEGATE,
                            asdl.ConstantAST(2),
                        ),
                    ),
                ),
            ),
        )

        self.listing_2_3_tokens = [
            "int",
            "main",
            "(",
            "void",
            ")",
            "{",
            "return",
            "--",
            "2",
            ";",
            "}",
        ]

        self.listing_2_4_tokens = [
            "int",
            "main",
            "(",
            "void",
            ")",
            "{",
            "return",
            "-",
            "(",
            "-",
            "2",
            ")",
            ";",
            "}",
        ]
        self.listing_2_4_ast = asdl.ProgramAST(
            asdl.FunctionAST(
                "main",
                asdl.ReturnAST(
                    asdl.UnaryAST(
                        asdl.UnaryOperatorAST.NEGATE,
                        asdl.UnaryAST(
                            asdl.UnaryOperatorAST.NEGATE,
                            asdl.ConstantAST(2),
                        ),
                    ),
                ),
            ),
        )
