import json
from copy import deepcopy
from dataclasses import (
    dataclass,
    field
)
from string import Formatter
from urllib.parse import urlparse

from requests import (
    exceptions,
    request as _request
)
from urllib3.filepost import encode_multipart_formdata

from my_config import proxy
from model.helpers import (
    AlternateJsonEncoder,
    Logger
)
from model.http.message import MediaType
from model.http.request import Request
from model.http.response import Response
from utils.altcollections import ExtDict
from utils.wait import response_waiter


@dataclass
class ApiEndpoint:
    url: str
    method: str
    path_url: str
    headers: dict = field(default_factory=dict)
    cookies: dict = field(default_factory=dict)
    comment: str = field(default_factory=str)

    # example for .bashrc:
    # export QA_AUTOTESTS_PROXY_FOR_DEBUG='http://127.0.0.1:8888'
    _proxy: str = proxy

    def __str__(self):
        return f'{self.method} {self.path_url} - headers={self.headers}'

    @staticmethod
    def _check_url(url):
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https']:
            raise exceptions.InvalidSchema()
        return url

    def check_format_proxy(self, value):
        if self._proxy and "http" not in value:
            self._proxy = 'http://' + value
        return self._proxy

    def fire(self, request: Request) -> Response:
        stored_headers = ExtDict(request.headers)
        # To prevent specific headers overwrite by authorize function:
        request.headers.update(stored_headers)

        if request.media_type == MediaType.X_WWW_FORM_URLENCODED:
            body = request.body if hasattr(request,
                                           'body') else request.query_string[1:]
        elif request.media_type == MediaType.FORM_DATA:
            raw_body = request.body if hasattr(request, 'body') else {}
            body, content_type = encode_multipart_formdata(raw_body)
            request.headers['Content-Type'] = content_type
        elif request.media_type == MediaType.XML:
            raw_body = request.body if hasattr(request, 'body') else ''
            body = raw_body.encode('utf-8')
        elif request.media_type == MediaType.TEXT:
            body = request.body
        elif request.media_type == MediaType.JSON and hasattr(request, 'body'):
            body = json.dumps(
                request.body, ensure_ascii=False, cls=AlternateJsonEncoder
            ).encode('utf-8')
        else:
            body = request.raw_formatted_body.encode('utf-8')

        # dirty hack:
        # without it headers check under the hood of requests will fail
        for key, value in request.headers.items():
            if isinstance(value, (bool, int, float)):
                request.headers[key] = str(value)

        response = _request(
            method=request.method,
            url=self._check_url(request.url),
            data=body,
            headers=request.headers if hasattr(request, 'headers') else None,
            cookies=request.cookies if hasattr(request, 'cookies') else None,
            params=request.params if hasattr(request, 'params') else None,
            proxies={
                'http': self.check_format_proxy(self._proxy),
                'https': self.check_format_proxy(self._proxy)
            } if self._proxy else None,
            allow_redirects=request.allow_redirects,
            verify=False
        )

        return Response.build(response)

    @response_waiter(timeout=60)
    def do_request(self, tests_args, tests_kwargs) -> Response:
        prepared_request: Request = self._build_request(*tests_args,
                                                        **tests_kwargs)
        response: Response = self.fire(prepared_request)
        if Logger.log_request_reponse:
            Logger.append_http(Request.parse(
                response.original_response.request
            ), response,
                comment=tests_kwargs.get("comment"))
        return response

    def _build_request(self, *args, **kwargs) -> Request:
        builder_params = {
            'method': self.method,
            'host': self.url,
            'path_url': self._substitute_path_vars(self.path_url, *args,
                                                   **kwargs)
        }

        if kwargs.get('headers'):
            headers = deepcopy(self.headers)
            headers.update(kwargs['headers'])
            builder_params['headers'] = headers
        else:
            builder_params['headers'] = self.headers

        if kwargs.get('cookies'):
            cookies = deepcopy(self.cookies)
            cookies.update(kwargs['cookies'])
            builder_params['cookies'] = cookies
        else:
            builder_params['cookies'] = self.cookies

        if kwargs.get('session'):
            builder_params['cookies']['session'] = kwargs['session']

        if kwargs.get('body'):
            builder_params['body'] = kwargs['body']

        if kwargs.get('params'):
            builder_params['params'] = kwargs['params']

        if 'allow_redirects' in kwargs:
            builder_params['allow_redirects'] = kwargs['allow_redirects']

        if kwargs.get('log') is not None:
            builder_params['log'] = kwargs['log']

        return Request.build(**builder_params)

    @staticmethod
    def _substitute_path_vars(path_url, *args, **kwargs):
        path_vars = [item[1]
                     for item in Formatter().parse(path_url) if item[1]]
        if path_vars:
            request_params = list(args) + [kwargs[x] for x in path_vars if
                                           kwargs.get(x)]
            if len(request_params) != len(path_vars):
                error = f'Missing required positional arguments. ' \
                        f'Expected: {path_vars}; provided: {request_params}'
                raise TypeError(error)
            else:
                var_to_param = {x: request_params[i] for i, x in
                                enumerate(path_vars)}
                path_url = path_url.format(**var_to_param)
        return path_url
