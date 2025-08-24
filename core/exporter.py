from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, QMetaObject, Qt
from PySide6.QtCore import Q_ARG

from datasource import datasource_container


class ExportTask(QRunnable):
    def __init__(self, db, script_name, output_path):
        super().__init__()
        self.db = db
        self.script_name = script_name
        self.output_path = output_path
        self.signals = ExportSignals()
        self.is_cancelled = False  # 取消标志

    def cancel(self):
        """标记任务为已取消"""
        self.is_cancelled = True

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

            datasource_service = datasource_container.get_datasource(data_source)

            output_file = self.output_path if self.output_path.endswith('.xlsx') else f"{self.output_path}.xlsx"
            datasource_service.export(script, output_file, self)
        except Exception as e:
            if not self.is_cancelled:
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
