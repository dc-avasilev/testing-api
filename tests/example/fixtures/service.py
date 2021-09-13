import pytest

from routes.example import ExampleApi


@pytest.fixture(scope='session')
def example(env: str, extdict) -> ExampleApi:
    environments = extdict({
        "qa": {
            "url": "https://httpbin.org"
        },
        "dev": {
            "url": "https://httpbin.org"
        }
    })
    return ExampleApi(url=environments[env].url)
