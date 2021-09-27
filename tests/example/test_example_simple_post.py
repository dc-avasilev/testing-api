import pytest

from tests.example.fixtures.service import ExampleApi


@pytest.mark.simple_post
def test_example_simple_post(example: ExampleApi):
    response = example.simple_post(
        body={
            "foo": "bar",
            "bar": "foo"
        },
        headers={
            "Authorization": "JWT or Else"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_post.json")


@pytest.mark.simple_post
def test_example_simple_post_ct_x_www_form(example: ExampleApi):
    response = example.simple_post(
        body={
            "foo": "bar",
            "bar": "foo"
        },
        headers={
            "Authorization": "JWT or Else",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_post_ct_form.json")


@pytest.mark.simple_post
def test_example_simple_post_ct_multipart_form_data(example: ExampleApi):
    response = example.simple_post(
        body={
            "foo": "bar",
            "bar": "foo"
        },
        headers={
            "Authorization": "JWT or Else",
            "Content-Type": "multipart/form-data"
        }
    )

    assert response.status_is.OK
    assert response.body
    assert response.conforms_to("example_simple_post_ct_form.json")
