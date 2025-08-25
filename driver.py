#!/usr/bin/env python3

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

from pathlib import Path

import argparse
import codegen
import emit
import lexer
import parser
import semantic_analysis
import subprocess
import sys
import tacky

common_action = "store_true"
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument("input_file")
argument_parser.add_argument(
    "--lex", action=common_action, help="perform lexing, but stop before parsing"
)
argument_parser.add_argument(
    "--parse",
    action=common_action,
    help="perform lexing and parsing, but stop before semantic analysis",
)
argument_parser.add_argument(
    "--validate",
    action=common_action,
    help="perform lexing, parsing, and semantic analysis, but stop before TACKY generation",
)
argument_parser.add_argument(
    "--tacky",
    action=common_action,
    help="perform lexing, parsing, semantic analysis, and TACKY generation, but stop before assembly generation",
)
argument_parser.add_argument(
    "--codegen",
    action=common_action,
    help="perform lexing, parsing, semantic analysis, TACKY and assembly generation, but stop before code emission",
)
argument_parser.add_argument(
    "-S",
    action=common_action,
    help="emit an assembly file, but not assemble or link it",
)
argument_parser.add_argument(
    "-c",
    action=common_action,
    help="convert the assembly program into an object file",
)
arguments = argument_parser.parse_args()

input_file = Path(arguments.input_file)

preprocessed_file = input_file.with_suffix(".i")
subprocess.run(("gcc", "-E", "-P", str(input_file), "-o", str(preprocessed_file)))
with preprocessed_file.open() as f:
    tokens = lexer.tokenize(f.read())
preprocessed_file.unlink()
if arguments.lex:
    sys.exit()

tree = parser.parse(tokens)
if arguments.parse:
    sys.exit()

symbols = {}
semantic_analysis.analyze(tree, symbols)
if arguments.validate:
    sys.exit()

tree = tacky.convert(tree, symbols)
if arguments.tacky:
    sys.exit()

tree = codegen.convert(tree, symbols)
if arguments.codegen:
    sys.exit()

assembly_file = input_file.with_suffix(".s")
with assembly_file.open("w") as f:
    f.write(emit.output(tree))
if arguments.S:
    sys.exit()

if arguments.c:
    args = ("gcc", "-c", str(assembly_file), "-o", str(input_file.with_suffix(".o")))
else:
    args = ("gcc", str(assembly_file), "-o", str(input_file.with_suffix("")))
subprocess.run(args)
assembly_file.unlink()
