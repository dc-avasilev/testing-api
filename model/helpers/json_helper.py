import json
from datetime import datetime


class SchemaNotFoundError(Exception):
    pass


class MultipleSchemaFoundError(Exception):
    pass


class JsonHelper:
    schema_dirs = []
    data_dirs = []

    @classmethod
    def locate_schema(cls, file_name):
        return cls._locate_file(file_name, cls.schema_dirs)

    @classmethod
    def parse_data(cls, file_name):
        return cls.parse(cls._locate_file(file_name, cls.data_dirs))

    @staticmethod
    def parse(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def _locate_file(file_name, dirs):
        matches = []
        for folder in dirs:
            for file in folder.iterdir():
                if file.parts[-1] == file_name:
                    matches.append(file)
        if not matches:
            raise SchemaNotFoundError(f'Файл {file_name} не найден!')
        elif len(matches) > 1:
            msg = f'Найдено несколько файлов с названием {file_name}:\n{matches}'
            raise MultipleSchemaFoundError(msg)
        return matches[0]


class AlternateJsonEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, bytes):
            import ast
            return ast.literal_eval(o.decode())
        return json.JSONEncoder.default(self, o)
