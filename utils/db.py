# import mysql.connector
from abc import (
    ABC,
    abstractmethod
)

import psycopg2
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder

from model.helpers.logger import Logger
from utils.altcollections import RecursiveConverter


class SQLDB(ABC):

    @abstractmethod
    def select_one(self, query, logging=None):
        pass

    @abstractmethod
    def select_all(self, query, logging=None):
        pass

    @abstractmethod
    def execute(self, query):
        pass


# class MySql(SQLDB):
#
#     def __init__(self, connection, database=None):
#         self._connection = connection
#         if database:
#             self._connection.database = database
#
#     def __str__(self):
#         if self._connection.is_connected():
#             string = 'Connected to {info} on {host}:{port}'.format(
#                 info=self._connection.database,
#                 host=self._connection.server_host,
#                 port=self._connection.server_port)
#         else:
#             string = 'No connection'
#         return '\n--------------\n{}\n--------------'.format(string)
#
#     def select_one(self, query, logging=None):
#         cursor = self._connection.cursor(dictionary=True, buffered=True)
#         cursor.execute(query)
#         self._connection.commit()
#         result = cursor.fetchone()
#         Logger.append_sql(query, result) if logging else ...
#         return RecursiveConverter(result)
#
#     def select_all(self, query, logging=None):
#         cursor = self._connection.cursor(dictionary=True, buffered=True)
#         cursor.execute(query)
#         self._connection.commit()
#         result = cursor.fetchall()
#         Logger.append_sql(query, result) if logging else ...
#         return RecursiveConverter(result)
#
#     def execute(self, query):
#         cursor = self._connection.cursor(buffered=True)
#         try:
#             cursor.execute(query)
#             if cursor.rowcount > 0:
#                 self._connection.commit()
#         except:
#             self._connection.rollback()
#         return cursor.rowcount


class Postgres(SQLDB):

    def __init__(self, connection):
        self._connection = connection

    def __str__(self):
        if self._connection:
            string = 'Connected on {host}:{port}'.format(
                host=self._connection.server_host,
                port=self._connection.server_port)
        else:
            string = 'No connection'
        return '\n--------------\n{}\n--------------'.format(string)

    def select_one(self, query):
        cursor = self._common_cursor_steps(query)
        result = cursor.fetchone()
        if Logger.log_sql:
            Logger.append_sql(query, result)
        return RecursiveConverter(result)

    def select_all(self, query):
        cursor = self._common_cursor_steps(query)
        result = cursor.fetchall()
        if Logger.log_sql:
            Logger.append_sql(query, result)
        return RecursiveConverter(result)

    def _common_cursor_steps(self, query):
        result = self._connection.cursor(cursor_factory=RealDictCursor)
        result.execute(query)
        self._connection.commit()
        return result

    def execute(self, query):
        cursor = self._connection.cursor()
        try:
            cursor.execute(query)
            if cursor.rowcount > 0:
                self._connection.commit()
            else:
                Logger.append_text(f'Count of changed rows: {cursor.rowcount}\n'
                                   f'Request: "{query}"')
        except Exception as e:
            Logger.append_text(f'Postgres database error:\n{e}')
            self._connection.rollback()
        return cursor.rowcount

    def execute_few_transactions(self, queries):
        """
        queries - is a python list with all queries you need to execute
        Example: DELETE_TABLES = ["DELETE FROM TEST", "DELETE FROM TEST1"]
        """
        cursor = self._connection.cursor()
        try:
            for query in queries:
                cursor.execute(query)
                self._connection.commit()
        except psycopg2.DatabaseError as e:
            Logger.append_text(f'Postgres database error:\n{e}')
            self._connection.rollback()
        return cursor.rowcount


class ConnectionManager(ABC):

    def __init__(self, config, pytest_request=None):
        self.config = config
        self.pytest_request = pytest_request
        self.tunnel = None

    def get_connection(self):
        if self.config.get('ssh_host'):
            self.open_tunnel()
            connection = self.connect_with_tunnel()
        else:
            connection = self.connect_direct()
        if self.pytest_request:
            self.pytest_request.addfinalizer(self.close_connection)
        return connection

    @abstractmethod
    def connect_with_tunnel(self):
        pass

    @abstractmethod
    def connect_direct(self):
        pass

    def close_connection(self):
        if self.tunnel:
            self.tunnel.stop()

    def open_tunnel(self):
        self.tunnel = SSHTunnelForwarder(
            (self.config['ssh_host'], self.config['ssh_port']),
            ssh_username=self.config['ssh_user'],
            ssh_password=self.config['ssh_password'],
            remote_bind_address=(self.config['db_host'], self.config['db_port'])
        )
        self.tunnel.start()


# class MysqlConnectionManager(ConnectionManager):
#
#     def connect_with_tunnel(self):
#         return mysql.connector.MySQLConnection(
#             user=self.config['db_user'],
#             password=self.config['db_password'],
#             host=self.tunnel.local_bind_host,
#             port=self.tunnel.local_bind_port
#         )
#
#     def connect_direct(self):
#         return mysql.connector.MySQLConnection(
#             user=self.config['db_user'],
#             password=self.config['db_password'],
#             database=self.config['db_name'],
#             host=self.config['db_host'],
#             port=self.config['db_port']
#         )


class PostgresConnectionManager(ConnectionManager):

    def connect_with_tunnel(self):
        return psycopg2.connect(
            dbname=self.config['db_name'],
            user=self.config['db_user'],
            password=self.config['db_password'],
            host=self.tunnel.local_bind_host,
            port=self.tunnel.local_bind_port
        )

    def connect_direct(self):
        return psycopg2.connect(
            dbname=self.config['db_name'],
            user=self.config['db_user'],
            password=self.config['db_password'],
            host=self.config['db_host'],
            port=self.config['db_port']
        )
