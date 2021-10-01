from http import HTTPStatus
from io import BytesIO
from json import loads
from json.decoder import JSONDecodeError
from pathlib import Path
from xml.parsers.expat import ExpatError

import pytest
import xmltodict
import yaml
from jsonschema import (
    RefResolver,
    validate
)
from jsonschema.exceptions import (
    SchemaError,
    ValidationError
)
from jsonschema.validators import urlopen
from lxml import etree

from model.helpers import JsonHelper
from utils.altcollections import RecursiveConverter
from .message import (
    MediaType,
    Message
)


STATUS_NAMES = [x for x in HTTPStatus.__dict__ if not x.startswith('_')]
STATUS_CODE_NAME = {getattr(HTTPStatus, x): x for x in STATUS_NAMES}


class ResponseStatusChecker:
    def __init__(self, response):
        self.response = response
        self.status = response.status

    def __getattr__(self, name):
        if name not in STATUS_NAMES:
            raise AttributeError(f'HTTP code "{name}" does not exist')
        code = getattr(HTTPStatus, name)
        assert self.status == code, f'Expected status: {code}, ' \
                                    f'actual: {self.status}' \
                                    f'\n\n***DEBUG:***\n{self.response}'
        return True


class Response(Message):
    def __init__(self, status, reason, body, headers, cookies=None,
                 original_response=None):
        self.status = status
        self.reason = reason
        self.body = body
        self.headers = headers
        self.cookies = cookies
        self.original_response = original_response
        if self.original_response is not None:
            self.url = self.original_response.url
        else:
            self.url = 'Unknown'

    def __str__(self):
        return f'\n---------------------------------------' \
               f'\nResponse:\n' \
               f'HTTP status: {self.status} ' \
               f'{self.reason}\n' \
               f'{self.raw_formatted_headers}' \
               f'\n{self.raw_formatted_body}'

    def conforms_to(self, schema_file_name, **kwargs):
        schema, schema_path = get_schema(schema_file_name)
        try:
            validate_response(self.body, schema, schema_path)
        except ValidationError as e:
            additional_info = ''
            if kwargs:
                additional_info = '\nADDITIONAL INFO: \n' + '\n'.join(
                    f'{key} = {value}' for key, value in kwargs.items()
                )
            pytest.fail(f'{e}\n\nschema_file_name: {schema_file_name}\n'
                        f'response:{self}\n{additional_info}\n')
        return True

    @property
    def status_is(self) -> HTTPStatus:
        """usage: 'assert response.status_is.OK'"""
        return ResponseStatusChecker(self)

    def status_eq(self, status_code: int):
        """usage: 'assert response.status_eq(200)'"""
        return getattr(ResponseStatusChecker(self),
                       STATUS_CODE_NAME[status_code])

    @classmethod
    def build(cls, _response):
        content_type = cls.parse_content_type(
            _response.headers.get('content-type', '')) or MediaType.TEXT
        if content_type == MediaType.JSON:
            body = cls._parse_body(_response)
        elif content_type in (MediaType.TEXT_XML,
                              MediaType.HTML,
                              MediaType.TEXT):
            if _response.content.startswith(b'<?xml'):
                body = XMLBodyParser.parse(_response.content)
            else:
                body = _response.text
        else:
            body = _response.text

        headers = _response.headers

        return cls(
            status=_response.status_code,
            reason=_response.reason,
            body=body,
            headers=headers,
            cookies=_response.cookies,
            original_response=_response
        )

    @staticmethod
    def _parse_body(request):
        try:
            res = request.json()
        except JSONDecodeError:
            return request.text
        else:
            if isinstance(res, (dict, list)):
                return RecursiveConverter(res)
            return res


class BaseBodyParser:
    @classmethod
    def parse(cls, raw_body):
        return raw_body.decode('utf-8', 'replace')


class JSONBodyParser(BaseBodyParser):
    @classmethod
    def parse(cls, raw_body):
        try:
            body = loads(raw_body.decode('UTF-8'))
        except JSONDecodeError:
            body = BaseBodyParser.parse(raw_body)
        return body


class XMLBodyParser(BaseBodyParser):
    @classmethod
    def parse(cls, raw_body):
        try:
            parser = etree.XMLParser(ns_clean=True)
            xml_parse = etree.parse(BytesIO(raw_body), parser)
            encoding = xml_parse.docinfo.encoding
            body = xmltodict.parse(raw_body, encoding=str(encoding))
        except ExpatError:
            body = BaseBodyParser.parse(raw_body)
        return body


def get_schema(schema_file_name):
    schema_path = JsonHelper.locate_schema(schema_file_name)
    schema = JsonHelper.parse(schema_path)
    return schema, schema_path


def validate_response(data, schema, schema_file_path: Path):
    resolver = RefResolver(
        'file://{}/'.format(schema_file_path.parents[0]),
        schema, handlers={
            'file': lambda x: yaml.unsafe_load(urlopen(x))
        })
    try:
        validate(data, schema, resolver=resolver)
    except SchemaError as se:
        pytest.fail(f'Provided schema is not valid!\n{se}')
