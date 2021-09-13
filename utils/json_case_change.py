"""
Tool for changing strings in JSON from snake_case to camelCase.
"""
import argparse
import re
from itertools import zip_longest


JSONFILE = "json.txt"
OUTFILE = "json_schema.txt"
PATTERN = re.compile(r'"[a-z_]+_+[a-z]+"')


def write_result(data, filename):
    with open(filename, "w") as file:
        file.write(data)


def to_camel_case(string):
    words = string.split('_')
    return words[0] + ''.join(x.title() for x in words[1:])


def find_words(string):
    words = PATTERN.findall(string)
    if words:
        fillers = PATTERN.split(string)
        words = [to_camel_case(x) for x in words]
        return ''.join(
            [f'{x}{y if y else ""}' for x, y in zip_longest(fillers, words)])
    else:
        return string


def parse_file(filedata):
    res = ''
    for line in filedata:
        res += find_words(line)
    return res


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--jsonfile", help="File with JSON.",
                    default=JSONFILE)
parser.add_argument("-o", "--outfile",
                    help="Name of the file to export results to.",
                    default=OUTFILE)
args = parser.parse_args()

write_result(parse_file(open(args.jsonfile)), args.outfile)
