import json
import os
import re
from pathlib import Path
from typing import Type

import pytest

from config import config
from model.helpers import (
    JsonHelper,
    YamlHelper
)
from utils.altcollections import (
    ExtDict,
    TupleDict
)
from utils.faker import (
    Fake
)


# """Фикстуры сервисов"""
pytest_plugins = [
    'tests.example.fixtures.service',
    'tests.example.fixtures.db_example_fixtures'
]

# """Фикстуры общего назначения"""
pytest_plugins += [
    # Model
    'model.helpers.plugin'
]


@pytest.fixture(scope='session')
def project_root(request) -> Path:
    return Path(request.config.rootdir)


@pytest.fixture(scope='session', autouse=True)
def allure_env(request, env, metadata, project_root):
    allure_dir = request.config.getoption('--alluredir')
    if allure_dir:
        allure_path = project_root / allure_dir
        with open(allure_path / 'environment.properties',
                  'w') as environment_file:
            environment_file.write(f'Environment={env}\n')
            for key, value in metadata.items():
                environment_file.write(f'{key}={value}\n')
            tag = os.getenv('TAG')
            if tag:
                service = os.getenv('QA_SERVICES')
                environment_file.write(f'Service={service}\n')
                environment_file.write(f'TAG={tag}\n')
        with open(allure_path / 'categories.json', 'w') as categories_file:
            categories_file.write(json.dumps([
                {
                    'name': 'Skipped',
                    'matchedStatuses': ['skipped']
                },
            ], indent='  '))


@pytest.fixture(scope='session')
def env(request) -> str:
    return request.config.getoption('--test_env')


@pytest.fixture(scope='session', autouse=True)
def global_config() -> ExtDict:
    return config


@pytest.fixture(scope='session')
def fake():
    return Fake.ru()


@pytest.fixture(scope='session')
def fake_en():
    return Fake.en()


@pytest.fixture(scope='session')
def extdict() -> Type[ExtDict]:
    return ExtDict


@pytest.fixture(scope='session')
def tupledict() -> Type[TupleDict]:
    return TupleDict


@pytest.fixture(scope='session', autouse=True)
def metadata_for_tests(metadata, env):
    metadata['Test environment'] = env


def _rotate_report(path: Path, limit: int, counter=1):
    if path.exists():
        if counter == limit:
            os.remove(path)
        else:
            new_path = Path.joinpath(
                path.parent,
                f"{re.findall(r'([a-zA-Z]+)([0-9]*)', path.stem)[0][0]}{counter}{path.suffix}"
            )
            if new_path.exists():
                _rotate_report(new_path, limit, counter + 1)
            path.rename(new_path)


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")
    project_root = Path(config.rootdir)
    services = project_root / 'tests'

    for service in [x for x in services.iterdir() if
                    x.is_dir() and x.parts[-1] != '__pycache__']:
        schema = service / 'schema'
        data = service / 'data'

        if schema.exists():
            JsonHelper.schema_dirs.append(schema)
        if data.exists():
            JsonHelper.data_dirs.append(data)
            YamlHelper.data_dirs.append(data)

        YamlHelper.services_dirs.append(service)


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_sessionstart(session):
    if html_path := session.config.getoption('--html'):
        _rotate_report(Path(html_path),
                       session.config.getoption('--max-reports'))


def pytest_addoption(parser):
    parser.addoption('--test_env', action='store', default='qa',
                     help='Test run environment: qa')
    # parser.addoption('--prometheus', action='store_true')
    parser.addoption(
        "--runslow", action="store_true", default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--max-reports", action="store", default=1, type=int,
        choices=range(1, 1001),
        help="Maximum count of stored reports before rotation."
    )