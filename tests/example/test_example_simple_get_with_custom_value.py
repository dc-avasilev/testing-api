import pytest

from tests.example.fixtures.service import ExampleApi


@pytest.mark.simple_get
def test_example_simple_get_with_custom_value(example: ExampleApi):
    response = example.simple_get_with_custom_value(
        "headers",  # this is a custom value in path, its may be not one
        headers={
            "foo": "bar"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_get_with_custom_value.json")
    assert response.body.headers.Foo == "bar"
