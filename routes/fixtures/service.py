import pytest

from routes import ExampleApi


@pytest.fixture(scope='session')
def example(env: str, extdict) -> ExampleApi:
    environments = extdict({
        "qa": {
            "url": "https://httpbin.org"
        }
    })
    return ExampleApi(url=environments[env].url)
