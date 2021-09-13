import yaml


class YamlNotFoundError(Exception):
    pass


class YamlHelper:
    services_dirs = []
    data_dirs = []

    @classmethod
    def parse_config(cls, file_name, service_name):
        return cls._parse_file(file_name, cls.services_dirs, service_name)

    @classmethod
    def parse_data(cls, file_name):
        return cls._parse_file(file_name, cls.data_dirs)

    @classmethod
    def parse_file(cls, filepath):
        with open(filepath, encoding='utf-8') as file:
            return yaml.unsafe_load(file)

    @staticmethod
    def _parse_file(file_name, dirs, service_name=None):
        matches = []
        for folder in dirs:
            if (
                service_name
                and folder.parts[-1] == service_name
                or not service_name
            ):
                for file in folder.iterdir():
                    if file.parts[-1] == file_name:
                        matches.append(file)
        if not matches:
            raise YamlNotFoundError(f'Файл {file_name} не найден!')

        with open(matches[0], 'r', encoding='utf-8') as file:
            return yaml.safe_load(file.read())
