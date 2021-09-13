from os import getenv

from utils.altcollections import ExtDict


local_env_login: str = getenv("DB_L", "qa")
local_env_password: str = getenv("DB_P", "")

is_needed_request_logs = bool(getenv("test_request_logs", True))
is_needed_sql_logs = bool(getenv("test_sql_logs", True))

proxy: str = getenv("QA_AUTOTESTS_PROXY_FOR_DEBUG")

config: ExtDict = ExtDict({
    "db": {
        "example_pg": {
            "dev": {
                "db_host": "postgresql.dev.ru",
                "db_name": "db_name",
                "db_password": local_env_password,
                "db_port": 5432,
                "db_user": local_env_login
            }
        }
    }
})
