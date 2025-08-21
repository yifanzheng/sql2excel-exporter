from typing import Optional

import pymysql
from pymysql.cursors import SSCursor
from pymysql import Error

from core.models import DataBase


class MysqlDataSource:

    @staticmethod
    def get_connection(data_source: DataBase) -> Optional[pymysql.Connection]:
        """建立MySQL数据库连接(使用PyMySQL)"""
        try:
            connection = pymysql.connect(
                host=data_source.host,
                port=int(data_source.port) if data_source.port else 3306,
                user=data_source.username,
                password=data_source.password,
                database=data_source.database,
                charset='utf8mb4',
                cursorclass=SSCursor
            )
            return connection
        except Error as e:
            return None
