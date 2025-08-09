from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QTextEdit,
                               QComboBox, QPushButton, QHBoxLayout, QMessageBox,
                               QFileDialog, QProgressBar, QLabel)

from core.exporter import Exporter
from core.models import ExportScript


class ScriptForm(QWidget):
    saved = Signal()
    deleted = Signal(str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.mode = 'add'  # 'add' or 'edit'
        self.current_script_name = ""  # 当前编辑的脚本名称
        # 导出标识
        self.export_in_progress = False
        self.exporter = Exporter(db)
        self.exporter.progress_updated.connect(self.update_progress)
        self.exporter.total_rows_updated.connect(self.set_total_rows)
        self.exporter.export_finished.connect(self.export_finished)
        self.exporter.export_failed.connect(self.export_failed)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.fields_edit = QLineEdit()
        self.fields_edit.setPlaceholderText("多个字段用逗号分隔")
        self.sql_edit = QTextEdit()
        self.sql_edit.setPlaceholderText("请输入SQL查询语句")

        self.ds_combo = QComboBox()
        self.refresh_ds_combo()

        layout.addRow("脚本名称:", self.name_edit)
        layout.addRow("数据源:", self.ds_combo)
        layout.addRow("字段名称:", self.fields_edit)
        layout.addRow("SQL脚本:", self.sql_edit)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addRow(self.progress_bar)

        # 添加进度显示标签
        self.progress_label = QLabel("准备导出...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.progress_label.setVisible(False)
        layout.addRow(self.progress_label)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.save_script)

        self.export_btn = QPushButton("执行导出")
        self.export_btn.clicked.connect(self.export_data)

        self.cancel_btn = QPushButton("取消导出")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.clicked.connect(self.cancel_export)
        self.cancel_btn.setVisible(False)
        self.cancel_btn.setEnabled(False)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_script)
        self.delete_btn.setVisible(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.delete_btn)

        layout.addRow(btn_layout)

    def refresh_ds_combo(self):
        self.ds_combo.clear()
        self.ds_combo.addItem("")
        for name in self.db.data_sources.keys():
            self.ds_combo.addItem(name)

    def set_mode(self, mode, script=None):
        self.mode = mode
        if mode == 'add':
            self.name_edit.clear()
            self.fields_edit.clear()
            self.sql_edit.clear()
            self.ds_combo.setCurrentIndex(0)
            self.name_edit.setEnabled(True)
            self.export_btn.setEnabled(False)
            self.delete_btn.setVisible(False)  # 添加模式隐藏删除按钮
            self.current_script_name = ""
        elif mode == 'edit' and script:
            self.name_edit.setText(script.name)
            self.fields_edit.setText(script.fields)
            self.sql_edit.setPlainText(script.sql)
            self.ds_combo.setCurrentText(script.data_source_name)
            self.name_edit.setEnabled(False)
            self.export_btn.setEnabled(True)
            self.delete_btn.setVisible(True)  # 编辑模式显示删除按钮
            self.current_script_name = script.name

    def save_script(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入脚本名称")
            return

        fields = self.fields_edit.text().strip()
        if not fields:
            QMessageBox.warning(self, "警告", "请输入字段名称")
            return

        sql = self.sql_edit.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, "警告", "请输入SQL脚本")
            return

        try:
            script = ExportScript(
                name=name,
                fields=fields,
                sql=sql,
                data_source_name=self.ds_combo.currentText()
            )

            self.db.scripts[name] = script
            self.db.save()
            self.saved.emit()
            QMessageBox.information(self, "成功", "脚本保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def export_data(self):
        script_name = self.name_edit.text().strip()
        if not script_name:
            QMessageBox.warning(self, "警告", "请先保存脚本")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出Excel文件", "", "Excel Files (*.xlsx)"
        )

        if file_path:
            self.export_in_progress = True
            # 禁用按钮避免重复点击
            self._toggle_ui_status(True)

            # 显示进度条
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.progress_label.setVisible(True)
            self.progress_label.setText("准备导出...")

            self.exporter.export_to_excel(script_name, file_path)

    def delete_script(self):
        """删除当前脚本"""
        if not self.current_script_name:
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除脚本 '{self.current_script_name}' 吗?\n此操作不可恢复!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 执行删除
                del self.db.scripts[self.current_script_name]
                self.db.save()
                self.deleted.emit(self.current_script_name)  # 发射删除信号
                QMessageBox.information(self, "成功", "脚本已删除")

                # 重置表单
                self.set_mode('add')

            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")

    def set_total_rows(self, total):
        self.total_rows = total
        self.update_progress(0)

    def update_progress(self, processed):
        if hasattr(self, 'total_rows') and self.total_rows > 0:
            percent = int(processed / self.total_rows * 100)
            self.progress_label.setText(
                f"导出进度: {processed}/{self.total_rows} ({percent}%)"
            )
            self.progress_bar.setValue(percent)
        else:
            self.progress_label.setText(f"已处理: {processed} 行")

    def cancel_export(self):
        """取消正在进行的导出"""
        if self.export_in_progress:
            # 调用导出器的取消方法
            self.exporter.cancel_export()
            self.export_in_progress = False
            self._toggle_ui_status(False)
            self.progress_label.setText("导出已取消")
            self.progress_bar.setValue(0)

            QMessageBox.information(self, "信息", "导出操作已取消")

    def export_finished(self, message):
        self.export_in_progress = False
        # 重新启用按钮
        self._toggle_ui_status(False)
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(False)

        # 显示完成消息
        QMessageBox.information(self, "完成", message)

    def export_failed(self, message):
        self.export_in_progress = False
        # 重新启用按钮
        self._toggle_ui_status(False)
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(False)
        # 显示错误消息
        QMessageBox.critical(self, "错误", message)

    def _toggle_ui_status(self, exporting):
        """切换UI状态"""
        self.export_btn.setEnabled(not exporting)
        self.save_btn.setEnabled(not exporting)
        self.delete_btn.setEnabled(not exporting)

        self.cancel_btn.setVisible(exporting)
        self.cancel_btn.setEnabled(exporting)
