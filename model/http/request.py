from __future__ import annotations

from urllib.parse import (
    unquote_plus,
    urlencode,
    urljoin
)

from requests import Request as _Request

from .message import Message


class Request(Message):
    headers: dict
    body: dict
    params: dict
    cookies: dict
    allow_redirects: bool

    def __init__(self, method: str, host: str, path_url: str, **kwargs):
        self.method: str = method
        self.host: str = host
        # Url part after domain name (local path_url)
        self.path_url: str = path_url
        for name, attr in kwargs.items():
            if attr is not None:
                setattr(self, name, attr)

    def _repr(self):
        msg = f'curl -X {self.method} ' \
              f'"{self.url}{unquote_plus(self.query_string)}" \\' \
              f'{self.formatted_headers}' \
              f'{self.formatted_body}'
        if msg[len(msg) - 2:len(msg) - 1] == '\\':
            msg = msg[0:len(msg) - 3] + '\n'
        return msg

    def __str__(self):
        return self._repr()

    def __repr__(self):
        return self._repr()

    @property
    def url(self):
        return urljoin(self.host, self.path_url)

    @property
    def query_string(self):
        result = ''
        params = []
        if hasattr(self, 'params'):
            for key, value in self.params.items():
                if key.endswith('[]') and isinstance(value, list):
                    for val in value:
                        params.append((key, val))
                    continue
                params.append((key, value))

            result += '?' + urlencode(params) if params else '?' + urlencode(
                self.params)
        if result == '?':
            return ''
        return result

    @classmethod
    def build(cls, method: str, host: str, path_url: str, params: dict = None,
              body: dict = None, headers: dict = None, cookies: dict = None,
              allow_redirects: bool = False):
        return cls(
            method=method,
            host=host,
            path_url=path_url,
            headers=headers or {},
            body=body,
            params=params,
            cookies=cookies,
            allow_redirects=allow_redirects
        )

    @classmethod
    def parse(cls, request: _Request) -> Request:
        if hasattr(request, 'json'):
            body = request.json
        elif hasattr(request, 'data'):
            body = request.data
        elif hasattr(request, 'files'):
            body = request.files
        elif hasattr(request, 'body'):
            body = request.body
        else:
            body = {}

        headers = request.headers if hasattr(request, 'headers') else {}
        params = request.params if hasattr(request, 'params') else {}
        cookies = request.cookies if hasattr(request, 'cookies') else {}
        path_url = request.path_url if hasattr(request, 'path_url') else ''

        return cls.build(
            method=request.method,
            host=request.url,
            path_url=path_url,
            headers=headers,
            body=body,
            params=params,
            cookies=cookies,
        )
