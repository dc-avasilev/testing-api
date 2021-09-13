import pytest

from tests.example.fixtures.service import ExampleApi


@pytest.mark.simple_get
def test_example_simple_get_with_custom_value(example: ExampleApi):
    response = example.simple_get_with_custom_value(
        "200"  # this is a custom value in path, its may be not one
    )

    assert response.status_is.OK
    assert not response.body
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
