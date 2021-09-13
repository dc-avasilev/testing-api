from dataclasses import dataclass

from model.http.endpoint import ApiEndpoint
from model.http.request_methods import Method
from model.http.response import Response


@dataclass
class ExampleApi:
    url: str

    def simple_get(self, *args, **kwargs) -> Response:
        """
        :param headers: dict
        :param body: dict
        :param params: dict
        :param cookies: dict
        :param allow_redirects: bool

        :return: Response
        """
        return ApiEndpoint(
            url=self.url,
            http_method=Method.GET,
            path="/get",
        ).do_request(tests_args=args,
                     tests_kwargs=kwargs)

    def simple_get_with_custom_value(self, *args, **kwargs) -> Response:
        """
        :param headers: dict
        :param body: dict
        :param params: dict
        :param cookies: dict
        :param allow_redirects: bool

        :return: Response
        """
        return ApiEndpoint(
            url=self.url,
            http_method=Method.GET,
            path="/{custom_value}",
        ).do_request(tests_args=args,
                     tests_kwargs=kwargs)

    def simple_post(self, *args, **kwargs) -> Response:
        """
        :param headers: dict
        :param body: dict
        :param params: dict
        :param cookies: dict
        :param allow_redirects: bool

        :return: Response
        """
        return ApiEndpoint(
            url=self.url,
            http_method=Method.POST,
            path="/post",
            headers={
                "Content-Type": "application/json"
            },
        ).do_request(tests_args=args,
                     tests_kwargs=kwargs)
