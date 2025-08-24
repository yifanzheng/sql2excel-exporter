from typing import Any
from typing import Optional

import psycopg2
import pymysql
from pymysql.cursors import SSCursor

from core.exporter import ExportTask
from core.models import DataBase, ExportScript
from utils import xlsxwriter_util


class DataSource:
    def __init__(self, database_info: DataBase) -> None:
        self.database_info = database_info

    def is_valid_connection(self) -> bool:
        pass

    def export(self, script: ExportScript, output_path: str, export_task: ExportTask):
        pass


class MySQLDataSource(DataSource):
    def __init__(self, database_info: DataBase) -> None:
        super().__init__(database_info)

    def is_valid_connection(self) -> bool:
        """测试数据库连接是否成功"""
        connection = None
        try:
            connection = self._get_connection()
            if connection and connection.open:
                return True
            return False
        except Exception:
            return False
        finally:
            if connection and connection.open:
                connection.close()

    def export(self, script: ExportScript, output_path: str, export_task: ExportTask) -> None:
        with self._get_connection() as connection:
            if not connection:
                export_task.signals.failed.emit("Failed to connect to database")
                return

            with connection.cursor() as cursor:
                count_sql = f"SELECT COUNT(*) FROM ({script.sql}) as subquery"
                cursor.execute(count_sql)
                total_rows = cursor.fetchone()[0]
                export_task.signals.total_rows.emit(total_rows)

            # 执行查询
            with connection.cursor(SSCursor) as cursor:
                cursor.execute(script.sql)
                # excel
                fields = script.fields.split(',')
                if not fields:
                    export_task.signals.failed.emit("No fields specified and no columns returned from query")
                    return
                workbook, worksheet = xlsxwriter_util.create_worksheet(output_path, fields)
                with workbook:
                    row = 1
                    # 逐行读取（流式）
                    while not export_task.is_cancelled:
                        result = cursor.fetchmany(500)
                        if not result or export_task.is_cancelled:
                            break
                        for data in result:
                            export_task.signals.progress.emit(row)
                            # 写入Excel
                            worksheet.write_row(row, 0, list(data))
                            row += 1
                        # time.sleep(0.01)  # 短暂释放控制权

                if export_task.is_cancelled:
                    return

                if row > 1:
                    export_task.signals.finished.emit(f"Exported {total_rows} rows to {output_path}")
                else:
                    export_task.signals.finished.emit("No data to export")

    def _get_connection(self) -> Optional[pymysql.Connection]:
        """建立数据库连接(使用PyMySQL)"""
        database_info = self.database_info
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


class PostgreSQLDataSource(DataSource):
    def __init__(self, database_info: DataBase) -> None:
        super().__init__(database_info)

    def is_valid_connection(self) -> bool:
        """测试数据库连接是否成功"""
        connection = None
        try:
            connection = self._get_connection()
            if connection and connection.open:
                return True
            return False
        except Exception:
            return False
        finally:
            if connection and connection.open:
                connection.close()

    def export(self, script: ExportScript, output_path: str, export_task: ExportTask) -> None:
        with self._get_connection() as connection:
            if not connection:
                export_task.signals.failed.emit("Failed to connect to database")
                return

            with connection.cursor() as cursor:
                count_sql = f"SELECT COUNT(*) FROM ({script.sql}) as subquery"
                cursor.execute(count_sql)
                total_rows = cursor.fetchone()[0]
                export_task.signals.total_rows.emit(total_rows)

            # 执行查询
            with connection.cursor() as cursor:
                cursor.execute(script.sql)
                # excel
                fields = script.fields.split(',')
                if not fields:
                    export_task.signals.failed.emit("No fields specified and no columns returned from query")
                    return

                workbook, worksheet = xlsxwriter_util.create_worksheet(output_path, fields)
                with workbook:
                    row = 1
                    # 逐行读取（流式）
                    while not export_task.is_cancelled:
                        result = cursor.fetchmany(500)
                        if not result or export_task.is_cancelled:
                            break
                        for data in result:
                            export_task.signals.progress.emit(row)
                            # 写入Excel
                            worksheet.write_row(row, 0, list(data))
                            row += 1
                        # time.sleep(0.01)  # 短暂释放控制权

                if export_task.is_cancelled:
                    return

                if row > 1:
                    export_task.signals.finished.emit(f"Exported {total_rows} rows to {output_path}")
                else:
                    export_task.signals.finished.emit("No data to export")

    def _get_connection(self) -> Optional[Any]:
        """建立数据库连接(使用psycopg2)"""
        database_info = self.database_info
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
