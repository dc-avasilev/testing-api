# -*- coding: utf-8 -*-
from copy import deepcopy

import allure
import pytest_html.extras

from my_config import (
    is_needed_request_logs,
    is_needed_sql_logs
)


class LogItem:
    __slots__ = ('type', 'data')

    def __init__(self, _type: str, data: dict):
        self.type = _type
        self.data = data


class Logger:
    items: list = []
    log_request_reponse: bool = is_needed_request_logs
    log_sql: bool = is_needed_sql_logs

    @classmethod
    def append_http(cls, request, response, comment=None):
        item = LogItem('http', {
            'request': request,
            'response': response,
            'comment': comment
        })
        cls.append(item)

    @classmethod
    def append_sql(cls, query, result, comment=None):
        item = LogItem('sql_query', {
            'query': query,
            'result': result,
            'comment': comment
        })
        cls.append(item)

    @classmethod
    def append_text(cls, item):
        cls.append(LogItem('text', item))

    @classmethod
    def append(cls, item):
        cls.items.append(deepcopy(item))

    @classmethod
    def pytest_html_attach(cls, item: LogItem, comment=None):
        log = ''
        if item.type == 'text':
            log = f'''
                <div class="extra_block">
                    <p>{item.data}<p>
                </div>
            '''
        elif item.type == 'http':
            comment = item.data.get('comment') or comment
            request = item.data.get('request')
            response = item.data.get('response')

            log = f'''
                <div class="extra_block">
                    <p>{comment or ''}<p>
                    <pre class="extra_request">{request or ''}</pre>
                    <hr>
                    <pre class="extra_response">{response or ''}</pre>
                </div>
            '''
        elif item.type == 'sql_query':
            log = cls._html_from_sql_item(item)
        return pytest_html.extras.html(log)

    @classmethod
    def allure_attach(cls, item: LogItem, comment=None):
        if item.type == 'http':
            comment = item.data.get('comment') or comment
            request = item.data.get('request')
            response = item.data.get('response')

            with allure.step(
                    comment or f'{request.method} {request.url}'
            ):
                allure.attach(
                    name='Request',
                    body=str(request),
                    attachment_type=allure.attachment_type.JSON
                )
                allure.attach(
                    name=f'Response -> {response.status} {response.reason}, ',
                    body=str(response),
                    attachment_type=allure.attachment_type.JSON
                )
        elif item.type == 'sql_query':
            query = item.data.get('query')
            comment = item.data.get('comment')

            with allure.step(comment or query):
                allure.attach(
                    name='SQL Query',
                    body=cls._html_from_sql_item(item),
                    attachment_type=allure.attachment_type.HTML
                )

    @staticmethod
    def _html_from_sql_item(item: LogItem) -> str:
        query = item.data.get('query')
        result = item.data.get('result')
        comment = item.data.get('comment')

        table_header = []
        table_body = []
        if result:
            if isinstance(result, list):
                keys = result[0].keys()
                rows = result
            else:
                keys = result.keys()
                rows = [result]
            table_header = [f'<th>{x}</th>' for x in keys]
            for row in rows:
                table_row_cells = [f'<td>{x}</td>' for x in row.values()]
                table_row = f'<tr>{"".join(table_row_cells)}</tr>'
                table_body.append(table_row)

        return f'''
                <div class="extra_block">
                    <p>{comment or ''}<p>
                    <pre>{query or ''}</pre>
                    <table>
                        <tr>{' '.join(table_header)}</tr>
                        <tbody>{''.join(table_body)}</tbody>
                    </table>
                </div>
            '''
