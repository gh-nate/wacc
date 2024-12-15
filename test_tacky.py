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
import tacky
import unittest


class TestTacky(TestCommon):
    def test_convert(self):
        self.assertEqual(
            tacky.convert(self.listing_1_1_ast),
            self.listing_1_1_tacky,
        )

        self.assertEqual(
            tacky.convert(
                asdl.ProgramAST(
                    asdl.FunctionAST(
                        "main",
                        asdl.ReturnAST(
                            asdl.UnaryAST(
                                asdl.UnaryOperatorAST.COMPLEMENT,
                                asdl.ConstantAST(2),
                            ),
                        ),
                    )
                ),
            ),
            self.table_2_1_row_2_tacky,
        )

        self.assertEqual(
            tacky.convert(self.listing_2_1_ast),
            self.listing_2_1_tacky,
        )

        self.assertEqual(
            tacky.convert(self.listing_2_4_ast),
            self.listing_2_4_tacky,
        )

        self.assertEqual(
            tacky.convert(
                asdl.ProgramAST(
                    asdl.FunctionAST(
                        "main",
                        asdl.ReturnAST(
                            asdl.UnaryAST(
                                asdl.UnaryOperatorAST.NEGATE,
                                asdl.UnaryAST(
                                    asdl.UnaryOperatorAST.COMPLEMENT,
                                    asdl.UnaryAST(
                                        asdl.UnaryOperatorAST.NEGATE,
                                        asdl.ConstantAST(8),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            self.table_2_1_row_3_tacky,
        )


if __name__ == "__main__":
    unittest.main()
