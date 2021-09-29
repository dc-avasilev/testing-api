from os import getenv

from utils.altcollections import ExtDict


local_env_dblogin: str = getenv("QA_AUTOTESTS_DB_L", "qa")
local_env_dbpassword: str = getenv("QA_AUTOTESTS_DB_P", "")

is_needed_request_logs: bool = getenv("QA_AUTOTESTS_REQUEST_LOGS",
                                      "yes") == "yes"
is_needed_sql_logs: bool = getenv("QA_AUTOTESTS_SQL_LOGS", "yes") == "yes"

proxy: str = getenv("QA_AUTOTESTS_PROXY_FOR_DEBUG")

config: ExtDict = ExtDict({
    "db": {
        "example_pg": {
            "dev": {
                "db_host": "postgresql.dev.ru",
                "db_name": "db_name",
                "db_password": local_env_dbpassword,
                "db_port": 5432,
                "db_user": local_env_dblogin
            }
        }
    }
})
