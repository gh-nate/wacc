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

import re

token_patterns = {
    "identifier": re.compile(r"[a-zA-Z_]\w*\b"),
    "constant": re.compile(r"[0-9]+\b"),
    "int keyword": re.compile(r"int\b"),
    "void keyword": re.compile(r"void\b"),
    "return keyword": re.compile(r"return\b"),
    "open parenthesis": re.compile(r"\("),
    "close parenthesis": re.compile(r"\)"),
    "open brace": re.compile(r"{"),
    "close brace": re.compile(r"}"),
    "semicolon": re.compile(r";"),
    "bitwise complement operator": re.compile(r"~"),
    "negation operator": re.compile(r"-"),
    "decrement operator": re.compile(r"--"),
    "addition operator": re.compile(r"\+"),
    "multiplication operator": re.compile(r"\*"),
    "division operator": re.compile(r"/"),
    "remainder operator": re.compile(r"%"),
}


def tokenize(s):
    tokens = []
    while s := s.lstrip():
        longest_length = 0
        for pattern in token_patterns.values():
            if m := pattern.match(s):
                match = m.group()
                match_length = len(match)
                if match_length > longest_length:
                    longest = match
                    longest_length = match_length
        if not longest_length:
            raise RuntimeError(f"No match found for '{s}'")
        tokens.append(longest)
        s = s[longest_length:]
    return tokens
