import pytest

from routes import ExampleApi


@pytest.mark.skip("URL for a problem in the task tracking system")
@pytest.mark.simple_get
def test_example_skiped(example: ExampleApi):
    response = example.simple_get(
        params={
            "foo": "bar"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_get.json")
