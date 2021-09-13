import urllib.parse
from copy import deepcopy

import allure
import pytest_html.extras


class BaseLogger:
    @staticmethod
    def _pretty_request(request, service):
        return f'{request.http_method} ' \
               f'{service.protocol}://' \
               f'{service.host}' \
               f'{request.path}' \
               f'{urllib.parse.unquote_plus(request.query_string)}\n' \
               f'{request.formatted_headers}' \
               f'{request.formatted_body}'


class AllureLogger(BaseLogger):

    def attach_request(self, request, service):
        log = self._pretty_request(request, service)
        allure.attach(
            name=f'{request.http_method} {request.path}',
            body=log,
            attachment_type=allure.attachment_type.JSON
        )

    def attach_response(self, response):
        allure.attach(
            name=f'{response.status} {response.reason}, ',
            body=str(response),
            attachment_type=allure.attachment_type.JSON
        )


class PytestHTMLLogger(BaseLogger):

    def extra_request(self, request, service):
        log = self.__html_log(self._pretty_request(request, service))

        return pytest_html.extras.html(log)

    def extra_response(self, response):
        style = '''
        overflow-y: scroll;
        max-height: 500px;
        padding: 5px;
        border: 1px solid #e6e6e6;
        '''
        message = str(response)
        if len(message) > 1000000:
            message = str(response).split('\n')[0]
        log = self.__html_log(message, style)

        return pytest_html.extras.html(log)

    @classmethod
    def __html_log(cls, message, style=''):
        return f'<pre style="{style}">{message}</pre>'


class LogHelper:
    current_service = None
    current_response = None
    current_request = None
    allure = AllureLogger()
    html = PytestHTMLLogger()

    @classmethod
    def set(cls, service, request, response):
        LogHelper.current_request = deepcopy(request)
        LogHelper.current_response = deepcopy(response)
        LogHelper.current_service = service

    @classmethod
    def clear(cls):
        cls.current_service = None
        cls.current_response = None
        cls.current_request = None
