import pytest

from tests.example.fixtures.service import ExampleApi


@pytest.mark.simple_post
def test_example_simple_post(example: ExampleApi):
    response = example.simple_post(
        body={
            "foo": "bar"
        },
        headers={
            "Auth": "JWT or Else"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_post.json")
