from core.models import DataBaseType, DataBase
from datasource.datasource import DataSource, MySQLDataSource, PostgreSQLDataSource


def get_datasource(database_info: DataBase) -> DataSource:
    if database_info.type == DataBaseType.MYSQL:
        return MySQLDataSource(database_info)
    elif database_info.type == DataBaseType.POSTGRESQL:
        return PostgreSQLDataSource(database_info)
