from PySide6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QComboBox,
                               QPushButton, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Signal
from core.models import DataSource, DataSourceType
from datasource.mysql_datasource import MysqlDataSource


class DataSourceForm(QWidget):
    saved = Signal()
    deleted = Signal(str)

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.mode = 'add'  # 'add' or 'edit'
        self.current_name = ''
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in DataSourceType])
        self.host_edit = QLineEdit()
        self.port_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.database_edit = QLineEdit()

        layout.addRow("名称:", self.name_edit)
        layout.addRow("类型:", self.type_combo)
        layout.addRow("Host:", self.host_edit)
        layout.addRow("Port:", self.port_edit)
        layout.addRow("用户名:", self.username_edit)
        layout.addRow("密码:", self.password_edit)
        layout.addRow("数据库:", self.database_edit)

        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self.test_connection)
        test_layout = QHBoxLayout()
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        layout.addRow(test_layout)

        # 按钮区域
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.save_data_source)

        self.delete_btn = QPushButton("删除")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_data_source)
        self.delete_btn.setVisible(False)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.delete_btn)

        layout.addRow(btn_layout)

    def set_mode(self, mode, data_source=None):
        self.mode = mode
        if mode == 'add':
            self.name_edit.clear()
            self.type_combo.setCurrentIndex(0)
            self.host_edit.clear()
            self.port_edit.clear()
            self.username_edit.clear()
            self.password_edit.clear()
            self.database_edit.clear()
            self.name_edit.setEnabled(True)
            self.delete_btn.setVisible(False)
            self.current_name = ''
        elif mode == 'edit' and data_source:
            self.name_edit.setText(data_source.name)
            self.type_combo.setCurrentText(data_source.type.value)
            self.host_edit.setText(data_source.host)
            self.port_edit.setText(data_source.port)
            self.username_edit.setText(data_source.username)
            self.password_edit.setText(data_source.password)
            self.database_edit.setText(data_source.database)
            self.name_edit.setEnabled(False)
            self.delete_btn.setVisible(True)
            self.current_name = data_source.name

    def test_connection(self):
        """测试数据库连接"""
        if not self._validate_inputs(show_message=True):
            return

        try:
            # 创建临时数据源对象
            ds = DataSource(
                name="connection_test",
                type=DataSourceType(self.type_combo.currentText()),
                host=self.host_edit.text().strip(),
                port=self.port_edit.text().strip(),
                username=self.username_edit.text().strip(),
                password=self.password_edit.text(),
                database=self.database_edit.text().strip()
            )

            # 测试连接
            if DataSourceForm._test_connection(ds):
                QMessageBox.information(self, "成功", "数据库连接成功！")
            else:
                QMessageBox.warning(self, "失败", "无法连接到数据库，请检查配置")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"连接测试失败: {str(e)}")

    def _validate_inputs(self, show_message=True) -> bool:
        """验证输入是否完整"""
        if not self.host_edit.text().strip():
            if show_message:
                QMessageBox.warning(self, "警告", "请输入主机地址")
            return False
        if not self.username_edit.text().strip():
            if show_message:
                QMessageBox.warning(self, "警告", "请输入用户名")
            return False
        return True

    @staticmethod
    def _test_connection(data_source: DataSource) -> bool:
        """测试数据库连接是否成功"""
        connection = None
        try:
            connection = MysqlDataSource.get_connection(data_source)
            if connection and connection.open:
                return True
            return False
        except Exception:
            return False
        finally:
            if connection and connection.open:
                connection.close()

    def save_data_source(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "请输入数据源名称")
            return

        try:
            ds = DataSource(
                name=name,
                type=DataSourceType(self.type_combo.currentText()),
                host=self.host_edit.text().strip(),
                port=self.port_edit.text().strip(),
                username=self.username_edit.text().strip(),
                password=self.password_edit.text(),
                database=self.database_edit.text().strip()
            )

            self.db.data_sources[name] = ds
            self.db.save()
            self.saved.emit()
            QMessageBox.information(self, "成功", "数据源保存成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")

    def delete_data_source(self):
        """删除当前数据源"""
        if not self.current_name:
            return

        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除数据源 '{self.current_name}' 吗?\n此操作不可恢复!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 检查是否有脚本使用此数据源
                used_by_scripts = [
                    name for name, script in self.db.scripts.items()
                    if script.data_source_name == self.current_name
                ]

                if used_by_scripts:
                    QMessageBox.warning(
                        self,
                        "无法删除",
                        f"该数据源被以下脚本引用，无法删除:\n{', '.join(used_by_scripts)}"
                    )
                    return

                # 执行删除
                del self.db.data_sources[self.current_name]
                self.db.save()
                self.deleted.emit(self.current_name)  # 发射删除信号
                QMessageBox.information(self, "成功", "数据源已删除")

                # 重置表单
                self.set_mode('add')

            except Exception as e:
                QMessageBox.critical(self, "错误", f"删除失败: {str(e)}")

    def cancel(self):
        self.saved.emit()