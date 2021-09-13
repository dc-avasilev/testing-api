import inspect

from jwt import decode

from .altcollections import ExtDict


def whoami():
    return inspect.stack()[1][3]


def jwt_decode(token):
    return ExtDict(decode(token, verify=False))
