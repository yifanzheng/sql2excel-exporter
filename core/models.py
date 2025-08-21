from dataclasses import dataclass
from enum import Enum

class DataBaseType(Enum):
    MYSQL = "MySQL"
    POSTGRESQL = "PostgreSQL"

@dataclass
class DataBase:
    name: str
    type: DataBaseType
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