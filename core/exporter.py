import time

import xlsxwriter
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, QMetaObject, Qt
from PySide6.QtCore import Q_ARG
from pymysql.cursors import SSCursor

from datasource.mysql_datasource import MysqlDataSource


class ExportTask(QRunnable):
    def __init__(self, db, script_name, output_path):
        super().__init__()
        self.db = db
        self.script_name = script_name
        self.output_path = output_path
        self.signals = ExportSignals()
        self._is_cancelled = False  # 取消标志

    def cancel(self):
        """标记任务为已取消"""
        self._is_cancelled = True

    def run(self):
        try:
            script = self.db.scripts.get(self.script_name)
            if not script:
                self.signals.failed.emit(f"Script '{self.script_name}' not found")
                return

            data_source = self.db.data_sources.get(script.data_source_name)
            if not data_source:
                self.signals.failed.emit(f"Data source '{script.data_source_name}' not found")
                return

            # 连接数据库
            with MysqlDataSource.get_connection(data_source) as connection:
                if not connection:
                    self.signals.failed.emit("Failed to connect to database")
                    return

                with connection.cursor() as cursor:
                    count_sql = f"SELECT COUNT(*) FROM ({script.sql}) as subquery"
                    cursor.execute(count_sql)
                    total_rows = cursor.fetchone()[0]
                    self.signals.total_rows.emit(total_rows)

                # 执行查询
                with connection.cursor(SSCursor) as cursor:
                    cursor.execute(script.sql)
                    # excel
                    output_file = self.output_path if self.output_path.endswith('.xlsx') else f"{self.output_path}.xlsx"
                    fields = script.fields.split(',')
                    if not fields:
                        self.signals.failed.emit("No fields specified and no columns returned from query")
                        return
                    with xlsxwriter.Workbook(output_file, {'constant_memory': True}) as workbook:
                        worksheet = workbook.add_worksheet("data")
                        # 写 ExcelHeader
                        header_format = workbook.add_format({
                            'bold': True,  # 加粗
                            'font_color': 'black',  # 字体颜色
                            'bg_color': '#92D050',  # 背景颜色
                        })
                        worksheet.write_row('A1', fields, header_format)
                        row = 1
                        # 逐行读取（流式）
                        while not self._is_cancelled:
                            result = cursor.fetchone()
                            if not result or self._is_cancelled:
                                break
                            self.signals.progress.emit(row)
                            # 写入Excel
                            Exporter._write_to_excel_rowline(worksheet, row, list(result))
                            row += 1
                            # time.sleep(0.01)  # 短暂释放控制权

                    if self._is_cancelled:
                        return

                    if row > 1:
                        self.signals.finished.emit(f"Exported {total_rows} rows to {self.output_path}")
                    else:
                        self.signals.finished.emit("No data to export")
        except Exception as e:
            if not self._is_cancelled:
                # 只有在未取消的情况下才发出失败信号
                self.signals.failed.emit(f"Export failed: {str(e)}")


class ExportSignals(QObject):
    progress = Signal(int)  # 当前已处理行数
    total_rows = Signal(int)  # 总行数
    finished = Signal(str)  # 完成信号
    failed = Signal(str)  # 失败信号


class Exporter(QObject):
    # 这些信号将在主线程中发出
    progress_updated = Signal(int)
    total_rows_updated = Signal(int)
    export_finished = Signal(str)
    export_failed = Signal(str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(1)  # 限制同时只能有一个导出任务
        self.current_task = None  # 跟踪当前任务

    def export_to_excel(self, script_name, output_path):
        self.current_task = ExportTask(self.db, script_name, output_path)
        self.current_task.signals.progress.connect(self._update_progress)
        self.current_task.signals.total_rows.connect(self._set_total_rows)
        self.current_task.signals.finished.connect(self._export_finished)
        self.current_task.signals.failed.connect(self._export_failed)
        self.thread_pool.start(self.current_task)

    def _update_progress(self, rows_processed):
        # 通过主线程更新UI
        QMetaObject.invokeMethod(self, "progress_updated",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(int, rows_processed))

    def _set_total_rows(self, total_rows):
        QMetaObject.invokeMethod(self, "total_rows_updated",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(int, total_rows))

    def _export_finished(self, message):
        QMetaObject.invokeMethod(self, "export_finished",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, message))

    def _export_failed(self, message):
        QMetaObject.invokeMethod(self, "export_failed",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(str, message))

    def cancel_export(self):
        """取消当前导出任务"""
        if self.current_task:
            self.current_task.cancel()
        self.thread_pool.clear()  # 清除线程池中的任务

    @staticmethod
    def _write_to_excel_rowline(sheet: any, row: int, rowline: list):
        col = 0
        # 取出每个单元格的内容
        for cell in rowline:
            sheet.write(row, col, cell)
            col += 1
