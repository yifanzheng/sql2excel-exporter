from typing import Any
from typing import Optional

import psycopg2
import pymysql
from pymysql.cursors import SSCursor

from core.models import DataBase, DataBaseType


class DataSource:
    def __init__(self, database_type: DataBaseType, database_info: DataBase) -> None:
        self.database_type = database_type
        self.database_info = database_info

    def get_connection(self) -> Optional[Any]:
        if self.database_type == DataBaseType.MYSQL:
            return MySQLDataSource().get_connection(self.database_info)
        elif self.database_type == DataBaseType.POSTGRESQL:
            return PostgreSQLDataSource().get_connection(self.database_info)
        else:
            raise ValueError(f"Unsupported database type: {self.database_type.value}")


class MySQLDataSource:

    @staticmethod
    def get_connection(self, database_info: DataBase) -> Optional[Any]:
        """建立数据库连接(使用PyMySQL)"""
        try:
            connection = pymysql.connect(
                host=database_info.host,
                port=int(database_info.port) if database_info.port else 3306,
                user=database_info.username,
                password=database_info.password,
                database=database_info.database,
                charset='utf8mb4',
                cursorclass=SSCursor
            )
            return connection
        except pymysql.Error as e:
            return None


class PostgreSQLDataSource:

    @staticmethod
    def get_connection(self, database_info: DataBase) -> Optional[Any]:
        """建立数据库连接(使用psycopg2)"""
        try:
            connection = psycopg2.connect(
                host=database_info.host,
                port=int(database_info.port) if database_info.port else 5432,
                user=database_info.username,
                password=database_info.password,
                database=database_info.database
            )
            return connection
        except psycopg2.Error as e:
            return None
