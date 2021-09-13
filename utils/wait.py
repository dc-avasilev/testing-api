import time
from functools import wraps

import pytest


def for_db_state(db: object,
                 query: str,
                 check_if_success: object,
                 timeout: int = 60,
                 not_found_error: str = 'no entry found!',
                 timeout_error: str = 'timeout exceeded!'):
    error = 'Waiting for db state failed: {}'
    for _ in range(timeout):
        result = db.select_one(query)
        print(result)
        if not result:
            pytest.fail(error.format(not_found_error))
        elif not check_if_success(result):
            time.sleep(1)
            continue
        else:
            return result
    pytest.fail(error.format(timeout_error))


def success_waiter(timeout: int = 30,
                   interval: float = 0.3,
                   exception: AssertionError = AssertionError):
    def decorator(function):
        @wraps(function)
        def wrapper(*args,
                    **kwargs):
            timestamp = time.time() + timeout
            error: str = ''
            while time.time() < timestamp:
                try:
                    return function(*args, **kwargs)
                except exception as err:
                    error = err
                    time.sleep(interval)
            raise type(error)(f"\nERROR: function '{function.__name__}' failed."
                              f"\n{error}\n")

        return wrapper

    return decorator


def response_waiter(timeout: int = 10,
                    interval: float = 0.5,
                    error_codes=(408,)):
    def decorator(function):
        def wrapper(*args,
                    **kwargs):
            timestamp = time.time() + timeout
            while time.time() < timestamp:
                response = function(*args, **kwargs)
                if response.status not in error_codes:
                    return response
                time.sleep(interval)
            raise AssertionError(f"\nERROR: unexpected HTTP response received:"
                                 f"\n{response}")

        return wrapper

    return decorator
