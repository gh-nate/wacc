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

import codegen
import unittest


class TestCodegen(TestCommon):
    def test_convert(self):
        self.assertEqual(codegen.convert(self.listing_1_1_tacky), self.listing_1_1_asm)

        self.assertEqual(
            codegen.convert(self.table_2_1_row_2_tacky),
            self.table_2_1_row_2_asm,
        )

        self.assertEqual(
            codegen.convert(self.listing_2_1_tacky),
            self.listing_2_1_asm,
        )

        self.assertEqual(
            codegen.convert(self.listing_2_4_tacky),
            self.listing_2_4_asm,
        )

        self.assertEqual(
            codegen.convert(self.table_2_1_row_3_tacky),
            self.table_2_1_row_3_asm,
        )


if __name__ == "__main__":
    unittest.main()
