import pytest

from tests.example.fixtures.service import ExampleApi


@pytest.mark.simple_get
def test_example_fail(example: ExampleApi):
    response = example.simple_get(
        params={
            "foo": "bar"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_get.json")
    assert response.body.args.foo == "wrong text"
