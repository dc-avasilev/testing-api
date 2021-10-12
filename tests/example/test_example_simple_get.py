import pytest

from routes import ExampleApi


@pytest.mark.simple_get
def test_example_simple_get(example: ExampleApi):
    response = example.simple_get(
        params={
            "foo": "bar"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_get.json")
