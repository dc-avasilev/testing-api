from strenum import StrEnum


class Method(StrEnum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    TRACE = 'TRACE'
    CONNECT = 'CONNECT'
