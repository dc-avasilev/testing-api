import json

from model.helpers import AlternateJsonEncoder


class MediaType:
    JSON = 'application/json'
    X_WWW_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    FORM_DATA = 'multipart/form-data'
    XML = 'application/xml'
    TEXT = 'text/plain'
    TEXT_XML = 'text/xml'
    HTML = 'text/html'


class Message:
    @property
    def formatted_body(self):
        result = ''
        if hasattr(self, 'body'):
            result += '--data \'' + json.dumps(self.body,
                                               indent=4,
                                               ensure_ascii=False,
                                               cls=AlternateJsonEncoder) + "'"
        return result

    @property
    def raw_formatted_body(self):
        result = ''
        if hasattr(self, 'body'):
            result += json.dumps(self.body,
                                 indent=4,
                                 ensure_ascii=False,
                                 cls=AlternateJsonEncoder)
        return result

    @property
    def formatted_headers(self):
        result = ''
        if hasattr(self, 'headers'):
            for key, value in self.headers.items():
                result += f'\n-H "{key}: {value}" \\'
            result += '\n'
        return result

    @property
    def raw_formatted_headers(self):
        result = ''
        if hasattr(self, 'headers'):
            for key, value in self.headers.items():
                result += f'\n{key}: {value}'
            result += '\n'
        return result

    @property
    def media_type(self):
        if hasattr(self, 'headers'):
            header_value = self.headers.get('Content-Type', '')
            return self.parse_content_type(header_value)

    @staticmethod
    def parse_content_type(header_value):
        return header_value.split(';')[0]
