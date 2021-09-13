from urllib.parse import (
    unquote_plus,
    urlencode,
    urljoin
)

from .message import Message


class Request(Message):
    headers: dict
    body: dict
    params: dict
    cookies: dict
    allow_redirects: bool

    def __init__(self, http_method: str, host: str, path: str, **kwargs):
        self.http_method: str = http_method
        self.host: str = host
        self.path: str = path  # Url part after domain name (local path)
        for name, attr in kwargs.items():
            if attr is not None:
                setattr(self, name, attr)

    def __str__(self):
        msg = f'curl -X {self.http_method} ' \
              f'"{self.url}{unquote_plus(self.query_string)}" \\' \
              f'{self.formatted_headers}' \
              f'{self.formatted_body}'
        if msg[len(msg) - 2:len(msg) - 1] == '\\':
            msg = msg[0:len(msg) - 3] + '\n'
        return msg

    @property
    def url(self):
        return urljoin(self.host, self.path)

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
        return result

    @classmethod
    def build(cls, http_method: str, host: str, path: str, params: dict = None,
              body: dict = None, headers: dict = None, cookies: dict = None,
              allow_redirects: bool = False):
        return cls(
            http_method,
            host=host,
            path=path,
            headers=headers or {},
            body=body,
            params=params,
            cookies=cookies,
            allow_redirects=allow_redirects
        )
