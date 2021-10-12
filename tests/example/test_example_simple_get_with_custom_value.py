import pytest

from routes import ExampleApi


@pytest.mark.simple_get
def test_example_simple_get_with_custom_value_200(example: ExampleApi):
    response = example.simple_get_with_custom_value(
        "200"  # this is a custom value in path, its may be not one
    )

    assert response.status_is.OK
    assert not response.body
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"


@pytest.mark.simple_get
def test_example_simple_get_with_custom_value_400(example: ExampleApi):
    response = example.simple_get_with_custom_value(
        "400"  # this is a custom value in path, its may be not one
    )

    assert response.status_is.BAD_REQUEST
    assert not response.body
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
