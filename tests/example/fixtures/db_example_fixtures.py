import pytest

from utils.db import (
    Postgres,
    PostgresConnectionManager
)


@pytest.fixture(scope='session')
def db_example(env: str, global_config, request) -> Postgres:
    return Postgres(PostgresConnectionManager(
        global_config.db.example_pg[env],
        request
    ).get_connection())
