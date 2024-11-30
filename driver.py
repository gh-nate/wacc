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
import subprocess
import sys

argument_parser = argparse.ArgumentParser()
COMMON_ACTION = "store_true"
argument_parser.add_argument("input_file")
argument_parser.add_argument("--lex", action=COMMON_ACTION)
argument_parser.add_argument("--parse", action=COMMON_ACTION)
argument_parser.add_argument("--codegen", action=COMMON_ACTION)
argument_parser.add_argument("-S", action=COMMON_ACTION)
arguments = argument_parser.parse_args()

input_file = Path(arguments.input_file)
preprocessed_file = input_file.with_suffix(".i")
subprocess.run(["gcc", "-E", "-P", str(input_file), "-o", str(preprocessed_file)])
preprocessed_file.unlink()

if arguments.lex:
    sys.exit()

if arguments.parse:
    sys.exit()

if arguments.codegen:
    sys.exit()

if arguments.S:
    sys.exit()

assembly_file = input_file.with_suffix(".s")
output_file = input_file.with_suffix("")
subprocess.run(["gcc", str(assembly_file), "-o", str(output_file)])
assembly_file.unlink()
