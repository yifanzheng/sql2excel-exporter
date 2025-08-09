from dataclasses import dataclass
from enum import Enum

class DataSourceType(Enum):
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"
    SQLITE = "SQLite"
    ORACLE = "Oracle"

@dataclass
class DataSource:
    name: str
    type: DataSourceType
    host: str
    port: str
    username: str = ""
    password: str = ""
    database: str = ""

@dataclass
class ExportScript:
    name: str
    fields: str  # 逗号分隔的字段名
    sql: str
    data_source_name: str = ""