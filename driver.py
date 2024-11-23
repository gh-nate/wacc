#!/usr/bin/env python3

# Copyright (c) 2024 gh-nate
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

import argparse
import codegen
import lexer
import parser
import subprocess
import sys

COMMON_ACTION = "store_true"
ap = argparse.ArgumentParser()
ap.add_argument("input_file")
ap.add_argument(
    "-S",
    action=COMMON_ACTION,
    help="emit an assembly file, but not assemble or link it",
)
ap.add_argument(
    "--lex", action=COMMON_ACTION, help="run the lexer, but stop before parsing"
)
ap.add_argument(
    "--parse",
    action=COMMON_ACTION,
    help="run the lexer and parser, but stop before assembly generation",
)
ap.add_argument(
    "--codegen",
    action=COMMON_ACTION,
    help="perform lexing, parsing, and assembly generation, but stop before code emission",
)
args = ap.parse_args()

stem = Path(args.input_file).stem

preprocessed_file = Path(stem + ".i")
subprocess.run(["gcc", "-E", "-P", args.input_file, "-o", str(preprocessed_file)])

tokens = lexer.lex(preprocessed_file)
preprocessed_file.unlink()

if args.lex:
    sys.exit()

tree = parser.parse_program(tokens)

if args.parse:
    sys.exit()

codegen.translate_program(tree)

if args.codegen:
    sys.exit()

if args.S:
    sys.exit()

assembly_file = Path(stem + ".s")
subprocess.run(["gcc", str(assembly_file), "-o", stem])
assembly_file.unlink()
