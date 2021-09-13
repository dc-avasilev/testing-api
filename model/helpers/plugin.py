from pathlib import PurePath

import pytest

from .logger import Logger


def pytest_cmdline_preparse(config, args):
    if [x for x in args if x.startswith('--html')]:
        style_path = PurePath(config.rootdir) / 'model/helpers/style.css'
        args.append(f'--css={style_path}')


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.pop()


@pytest.mark.optionalhook
def pytest_html_results_table_html(report, data):
    if report.passed:
        del data[-1]


@pytest.mark.hookwrapper
def pytest_runtest_makereport(
    item,
    call,
    # env
):
    outcome = yield
    report = outcome.get_result()
    statuses = ['call', 'teardown']

    if report.failed:
        statuses.append('setup')
    if report.when in statuses:
        comment = 'teardown' if report.when == 'teardown' else None
        if item.config.getoption('--html'):
            extra = [
                Logger.pytest_html_attach(log_item, comment=comment)
                for log_item in Logger.items if hasattr(Logger, 'items')
            ]

            report.extra = extra
        if item.config.getoption('--alluredir'):
            for log_item in Logger.items:
                Logger.allure_attach(log_item,
                                     comment=comment)
        if hasattr(Logger, 'items'):
            Logger.items = []
