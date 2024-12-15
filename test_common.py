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
        self.listing_1_1_tacky = asdl.ProgramTACKY(
            asdl.FunctionTACKY(
                "main",
                [asdl.ReturnTACKY(asdl.ConstantTACKY(2))],
            ),
        )
        self.listing_1_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(0),
                    asdl.MovASM(asdl.ImmASM(2), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ],
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
        self.listing_2_1_tacky = asdl.ProgramTACKY(
            asdl.FunctionTACKY(
                "main",
                [
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.NEGATE,
                        asdl.ConstantTACKY(2),
                        asdl.VarTACKY("tmp.0"),
                    ),
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.COMPLEMENT,
                        asdl.VarTACKY("tmp.0"),
                        asdl.VarTACKY("tmp.1"),
                    ),
                    asdl.ReturnTACKY(asdl.VarTACKY("tmp.1")),
                ],
            ),
        )
        self.listing_2_1_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(8),
                    asdl.MovASM(asdl.ImmASM(2), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-4)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, asdl.StackASM(-4)),
                    asdl.MovASM(asdl.StackASM(-4), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-8)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, asdl.StackASM(-8)),
                    asdl.MovASM(asdl.StackASM(-8), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ],
            ),
        )

        self.table_2_1_row_2_tacky = asdl.ProgramTACKY(
            asdl.FunctionTACKY(
                "main",
                [
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.COMPLEMENT,
                        asdl.ConstantTACKY(2),
                        asdl.VarTACKY("tmp.0"),
                    ),
                    asdl.ReturnTACKY(asdl.VarTACKY("tmp.0")),
                ],
            ),
        )
        self.table_2_1_row_2_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(4),
                    asdl.MovASM(asdl.ImmASM(2), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-4)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, asdl.StackASM(-4)),
                    asdl.MovASM(asdl.StackASM(-4), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ],
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
        self.listing_2_4_tacky = asdl.ProgramTACKY(
            asdl.FunctionTACKY(
                "main",
                [
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.NEGATE,
                        asdl.ConstantTACKY(2),
                        asdl.VarTACKY("tmp.0"),
                    ),
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.NEGATE,
                        asdl.VarTACKY("tmp.0"),
                        asdl.VarTACKY("tmp.1"),
                    ),
                    asdl.ReturnTACKY(asdl.VarTACKY("tmp.1")),
                ],
            ),
        )
        self.listing_2_4_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(8),
                    asdl.MovASM(asdl.ImmASM(2), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-4)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, asdl.StackASM(-4)),
                    asdl.MovASM(asdl.StackASM(-4), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-8)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, asdl.StackASM(-8)),
                    asdl.MovASM(asdl.StackASM(-8), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ],
            ),
        )

        self.table_2_1_row_3_tacky = asdl.ProgramTACKY(
            asdl.FunctionTACKY(
                "main",
                [
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.NEGATE,
                        asdl.ConstantTACKY(8),
                        asdl.VarTACKY("tmp.0"),
                    ),
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.COMPLEMENT,
                        asdl.VarTACKY("tmp.0"),
                        asdl.VarTACKY("tmp.1"),
                    ),
                    asdl.UnaryTACKY(
                        asdl.UnaryOperatorTACKY.NEGATE,
                        asdl.VarTACKY("tmp.1"),
                        asdl.VarTACKY("tmp.2"),
                    ),
                    asdl.ReturnTACKY(asdl.VarTACKY("tmp.2")),
                ],
            ),
        )
        self.table_2_1_row_3_asm = asdl.ProgramASM(
            asdl.FunctionASM(
                "main",
                [
                    asdl.AllocateStackASM(12),
                    asdl.MovASM(asdl.ImmASM(8), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-4)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, asdl.StackASM(-4)),
                    asdl.MovASM(asdl.StackASM(-4), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-8)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NOT, asdl.StackASM(-8)),
                    asdl.MovASM(asdl.StackASM(-8), asdl.RegASM(asdl.Reg.R10)),
                    asdl.MovASM(asdl.RegASM(asdl.Reg.R10), asdl.StackASM(-12)),
                    asdl.UnaryASM(asdl.UnaryOperatorASM.NEG, asdl.StackASM(-12)),
                    asdl.MovASM(asdl.StackASM(-12), asdl.RegASM(asdl.Reg.AX)),
                    asdl.RetASM(),
                ],
            ),
        )
