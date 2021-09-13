#!/usr/bin/env python3

"""
Утилита для перевода всех JSON в указанных поддиректориях в YAML
(с соответствующим переименованием файла) или наоборот.
Кроме конвертации файлов и их переименования, умеет искать все упоминания
исходного файла в небинарных файлах и менять их на новый путь.
"""
import argparse
import json
import os
import re
from pathlib import Path

import yaml

from altcollections import (
    ARRAYS,
    RecursiveSort
)


ROOTDIR = Path('.')
EXCLUDED_DIRS = ('reports', 'venv', '.pytest_cache', '__')
SCHEMA_SUBDIR = Path('schema')
EMULATE = False
SORT = False
NO_SORT_PAIRS = 'type:object,type:array'
ADDITIONAL_DATA_PAIRS = 'type:object;additionalProperties:false,type:array;uniqueItems:true'
VERBOSE = False

PAIR_TEMPLATE = r'^\S+?:\S+?$'
JSON = 'json'
YAML = 'yml'
FILE_TYPES = [JSON, YAML, 'yaml']

TYPES_MAPPING = {
    None: ('none', 'null'),
    True: ('true',),
    False: ('false',)
}


class Converter:

    @classmethod
    def load(cls, filepath=None, source_type=JSON, data=None):
        """If exists, 'data' should be a file-like object."""
        func = json.load if source_type == JSON else yaml.unsafe_load
        if data:
            return func(data)
        with open(filepath, encoding='utf-8') as file:
            return func(file)

    @classmethod
    def dump(cls, data, filepath, dest_type=YAML):
        with open(filepath, 'w', encoding='utf-8') as file:
            if dest_type == JSON:
                json.dump(data, file, ensure_ascii=False, indent=4)
            else:
                yaml.dump(data, file, allow_unicode=True, indent=4,
                          sort_keys=False)
        if VERBOSE:
            print(f'Converted to: {filepath}')

    @classmethod
    def convert(cls, sourcepath, dest=None, source_type=JSON, dest_type=YAML,
                sort=False, unsorted_items=None, unsorted_pairs=None,
                emulate=False, exclude_all_from_sorting=False, preserve=False,
                enrich=False, new_data=None, normalize_value=True):
        if not dest:
            name = f'{sourcepath.stem}.{dest_type}'
            dest = sourcepath.parent.joinpath(name)
        if VERBOSE:
            print(f'Source file: {sourcepath}')
        if not emulate:
            try:
                data = cls.load(sourcepath, source_type)
            except Exception as err:
                print(f'ERROR parsing source:\n{err}\n')
            else:
                if enrich:
                    for item in cls._parse_data_string(
                        new_data, normalize_value=normalize_value):
                        cls._check_data_recursive(data, item)
                if sort:
                    if not unsorted_items:
                        unsorted_items = []
                    if not unsorted_pairs:
                        unsorted_pairs = {}
                    data = RecursiveSort(data, *unsorted_items, *unsorted_pairs,
                                         __exclude_all__=exclude_all_from_sorting)
                try:
                    cls.dump(data, dest, dest_type)
                except Exception as err:
                    print(f'ERROR saving destination file {dest}:\n{err}\n')
                else:
                    if sourcepath != dest and not preserve:
                        cls.remove(sourcepath)
        return dest

    @classmethod
    def remove(cls, filepath):
        os.remove(filepath)

    @classmethod
    def _check_data_recursive(cls, data, data_to_add):
        if hasattr(data, 'keys'):
            return cls._enrich_dict(data, data_to_add)
        elif isinstance(data, ARRAYS):
            cls._prepare_array(data, data_to_add)
        return data

    @classmethod
    def _prepare_array(cls, data, data_to_add):
        return type(data)(
            [cls._check_data_recursive(x, data_to_add) for x in data])

    @classmethod
    def _enrich_dict(cls, data, data_to_add):
        if data_to_add[0] in data.items():
            data.update([data_to_add[1]])
        for key, value in data.items():
            data[key] = cls._check_data_recursive(value, data_to_add)
        return data

    @classmethod
    def _parse_data_string(cls, string, normalize_value=True):
        res = []
        if string:
            for sub in _parse_arg_list(string):
                splitted = _parse_arg_pair(sub, r'^\S+?:\S+?;\S+?:\S+?$', ';',
                                           normalize_value=False)
                res.append([tuple(_parse_arg_pair(splitted[0],
                                                  normalize_value=normalize_value)),
                            tuple(_parse_arg_pair(splitted[1],
                                                  normalize_value=normalize_value))])
        return res


def check_dir(path):
    return not any(path.endswith(name) for name in EXCLUDED_DIRS)


def paths(root, schemadir=SCHEMA_SUBDIR, filetype=JSON, filelist=None,
          recursive=False):
    if schemadir == root:
        return _file_paths(root, filetype, filelist, recursive=recursive)
    filepaths = []
    for dirpath in root.rglob('*'):
        if (
            dirpath.is_dir()
            and dirpath.name == schemadir.name
            and check_dir(dirpath.name)
        ):
            filepaths.extend(_file_paths(dirpath, filetype, filelist,
                                         recursive=recursive))
    return filepaths


def _file_paths(dirpath, filetype, filelist, recursive=False):
    filepaths = []
    func = dirpath.rglob if recursive else dirpath.glob
    if filelist:
        for file in func('*'):
            if file.name in filelist:
                filepaths.append(file)
    else:
        for file in func(f'*.{filetype}'):
            filepaths.append(file)
    return filepaths


def edit(source, dest, root, emulate=False):
    for item in root.rglob('*'):
        if item.is_file() and check_dir(item.parent.name):
            try:
                text = item.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                continue
            else:
                if source in text:
                    if emulate:
                        message = f'File to be changed path in: {item}'
                    else:
                        text = text.replace(source, dest)
                        with item.open('w', encoding='utf-8') as file:
                            file.write(text)
                        message = f'Changed path in file: {item}'
                    if VERBOSE:
                        print(message)


def _parse_arg_list(data: str):
    return tuple(map(str.strip, data.split(',')))


def _parse_arg_pair(data: str, template: str = PAIR_TEMPLATE, sep: str = ':',
                    normalize_value=True):
    if not re.match(template, data):
        raise ValueError(
            f"String '{data}' does not match regexp: '{template}'")
    res = data.split(sep)
    if normalize_value:
        res[1] = _normalize_type(res[1])
    return res


def _normalize_type(string):
    for key, value in TYPES_MAPPING.items():
        if string.lower() in value:
            return key
    if string.isdigit():
        return int(string)
    try:
        return float(string)
    except ValueError:
        return string


def _prepare_input_output_type(data):
    if data.lower() == 'yaml':
        return YAML
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-root", "--rootdir", type=str,
                        help="Root directory inside which all changes will be made.",
                        default=ROOTDIR)
    parser.add_argument("-s", "--schemadir", type=str,
                        help="Directory inside rootdir where all schemas are.",
                        default=SCHEMA_SUBDIR)
    parser.add_argument("-f", "--files", type=str,
                        help="Comma-separated list of filenames to convert. "
                             "If exists, only these files in "
                             "corresponding directories will be converted.")
    parser.add_argument("-i", "--input-type", type=str,
                        help="[json|yaml] Type of source files which have to be converted.",
                        choices=FILE_TYPES, default=JSON)
    parser.add_argument("-o", "--output-type", type=str,
                        help="[json|yaml] Type of destination files.",
                        choices=FILE_TYPES, default=YAML)
    parser.add_argument("-r", "--recursive",
                        help="Parse all files in provided directory recursively.",
                        action='store_true')
    parser.add_argument("-e", "--emulate",
                        help="Just print list of affected files, do nothing.",
                        action='store_true')
    parser.add_argument("--sort",
                        help="Sort dictionaries keys and arrays.",
                        action='store_true')
    parser.add_argument("--unsorted-items", type=str,
                        help="Comma-separated list of items. Structures "
                             "(objects, arrays) containing these items "
                             "will not be sorted.")
    parser.add_argument("--unsorted-pairs", type=str,
                        help="Comma-separated list of key:value pairs. Objects "
                             "containing these pairs will not be sorted.",
                        default=NO_SORT_PAIRS)
    parser.add_argument("--exclude-all-from-sorting", action='store_true',
                        help="If true, from sorting will be excluded only enumerations"
                             " which meet all exclusion criteria.")
    parser.add_argument("-p", "--preserve", action='store_true',
                        help="Preserve (do not remove) source files.")
    parser.add_argument("--enrich", action='store_true',
                        help="If true, data from parameter --new-data will be added.")
    parser.add_argument("--new-data", type=str,
                        help="Comma-separated list of 'search_key:search_value;key:value' "
                             "pairs. key:value will be added to the dict where "
                             "search_key:search_value is found.",
                        default=ADDITIONAL_DATA_PAIRS)
    parser.add_argument("--no-normalize", action='store_true',
                        help="If true, second part (after colon) in every "
                             "key:value pair in parameters will NOT be normalized.")
    parser.add_argument("-v", "--verbose", action='store_true',
                        help="If true, all info messages will be printed to stdout.")
    args = parser.parse_args()
    VERBOSE = True if args.emulate else args.verbose
    in_type = _prepare_input_output_type(args.input_type)
    out_type = _prepare_input_output_type(args.output_type)
    files = args.files
    if args.files:
        files = _parse_arg_list(args.files)
    root = Path(args.rootdir)
    unsorted_items = None
    if args.unsorted_items:
        unsorted_items = _parse_arg_list(args.unsorted_items)
    unsorted_pairs = None
    if args.unsorted_pairs:
        unsorted_pairs = [
            _parse_arg_pair(x, normalize_value=not args.no_normalize)
            for x in _parse_arg_list(args.unsorted_pairs)]
    for item in paths(root, Path(args.schemadir), in_type, files,
                      recursive=args.recursive):
        destpath = Converter.convert(
            item, source_type=in_type, dest_type=out_type, sort=args.sort,
            unsorted_items=unsorted_items, unsorted_pairs=unsorted_pairs,
            emulate=args.emulate,
            exclude_all_from_sorting=args.exclude_all_from_sorting,
            preserve=args.preserve, enrich=args.enrich, new_data=args.new_data,
            normalize_value=not args.no_normalize
        )
        if item.name != destpath.name:
            edit(item.name, destpath.name, root, emulate=args.emulate)
