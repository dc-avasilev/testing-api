#!/usr/bin/env python3

"""
Tool for creating JSON schema from JSON. Input and output are files.
Requires module "genson" to be installed (https://pypi.org/project/genson/).
Should be run from command line.
Required parameters:
-i: input file path in JSON format. Defaults to "json.txt".
-o: output file path. Defaults to "json_schema.txt" in current directory.
"""

import argparse
import sys

import genson

from json_yaml_converter import (
    Converter,
    JSON,
    YAML
)


JSONFILE = "json.txt"
OUTFILE = "json_schema.txt"


def write_result(data, filename):
    with open(filename, "w") as file:
        file.write(data)


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--jsonfile", help="File with JSON.",
                    default=JSONFILE)
parser.add_argument("-o", "--outfile",
                    help="Name of the file to export results to.",
                    default=OUTFILE)
parser.add_argument("-f", "--format",
                    help="Format of output file: [yaml|json], default yaml.",
                    default=YAML)
args = parser.parse_args()

try:
    in_json = open(args.jsonfile, 'r')
except FileNotFoundError:
    print("JSON file not found.")
    sys.exit(1)

s = genson.SchemaBuilder()
s.add_object(eval(in_json.read()))
if args.format in (YAML, 'yaml'):
    func = Converter.dump
    res = s.to_schema()
elif args.format == JSON:
    func = write_result
    res = s.to_json()
else:
    exit('Incorrect value of --format argument')
try:
    func(res, args.outfile)
except Exception as err:
    print(err, '\n', res)
