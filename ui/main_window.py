from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTabWidget, QListWidget, QStackedWidget, QFrame)

from core.local_storage import LocalStorage
from ui.data_source_form import DataSourceForm
from ui.script_form import ScriptForm
from ui.styles import apply_style


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SQL2Excel Exporter")
        self.resize(1000, 600)
        self.setStyleSheet("""
            QMainWindow {
                background: #F6F8FA;
            }
            QStatusBar {
                background: white;
                border-top: 1px solid #E1E4E8;
            }
        """)

        self.db = LocalStorage()
        self.current_data_source = None
        self.current_script = None

        self.init_ui()
        apply_style(self)

    def init_ui(self):
        # 主布局使用左右分割
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧区域 (占1/4宽度)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)

        # 上部按钮区域
        btn_widget = QWidget()
        btn_layout = QHBoxLayout(btn_widget)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        self.add_ds_btn = QPushButton("新增数据源")
        self.add_ds_btn.clicked.connect(self.show_add_data_source_form)
        self.add_script_btn = QPushButton("新增脚本")
        self.add_script_btn.clicked.connect(self.show_add_script_form)

        btn_layout.addWidget(self.add_ds_btn)
        btn_layout.addWidget(self.add_script_btn)

        # 下部标签页区域
        self.tab_widget = QTabWidget()
        self.data_source_list = QListWidget()
        self.script_list = QListWidget()

        self.data_source_list.itemClicked.connect(self.show_data_source_details)
        self.script_list.itemClicked.connect(self.show_script_details)

        self.data_source_list.setFrameShape(QFrame.Shape.NoFrame)
        self.script_list.setFrameShape(QFrame.Shape.NoFrame)

        self.tab_widget.addTab(self.data_source_list, "数据源")
        self.tab_widget.addTab(self.script_list, "脚本")
        # 去除标签页边框
        self.tab_widget.setDocumentMode(True)

        left_layout.addWidget(btn_widget)
        left_layout.addWidget(self.tab_widget)

        # 右侧区域 (占3/4宽度)
        self.right_stacked = QStackedWidget()

        # 初始空白页面
        self.blank_page = QWidget()
        self.right_stacked.addWidget(self.blank_page)

        # 数据源表单
        self.ds_form = DataSourceForm(self.db)
        self.ds_form.saved.connect(self.refresh_data_sources)
        self.ds_form.deleted.connect(self.handle_data_source_deleted)
        self.right_stacked.addWidget(self.ds_form)

        # 脚本表单
        self.script_form = ScriptForm(self.db)
        self.script_form.saved.connect(self.refresh_scripts)
        self.script_form.deleted.connect(self.handle_script_deleted)
        self.right_stacked.addWidget(self.script_form)

        splitter.addWidget(left_widget)
        splitter.addWidget(self.right_stacked)
        splitter.setSizes([250, 750])

        self.setCentralWidget(splitter)
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.refresh_data_sources()
        self.refresh_scripts()

    def show_first_data_source(self):
        """显示第一个数据源(如果有)"""
        if self.data_source_list.count() > 0:
            first_item = self.data_source_list.item(0)
            first_item.setSelected(True)
            self.show_data_source_details(first_item)
        else:
            self.right_stacked.setCurrentWidget(self.blank_page)

    def show_first_script(self):
        """显示第一个脚本(如果有)"""
        if self.script_list.count() > 0:
            first_item = self.script_list.item(0)
            first_item.setSelected(True)
            self.show_script_details(first_item)
        else:
            self.right_stacked.setCurrentWidget(self.blank_page)

    def on_tab_changed(self, index):
        if index == 0:  # 数据源标签页
            self.show_first_data_source()
        elif index == 1:  # 脚本标签页
            self.show_first_script()


    def show_add_data_source_form(self):
        self.ds_form.set_mode('add')
        self.right_stacked.setCurrentWidget(self.ds_form)

    def show_add_script_form(self):
        self.script_form.set_mode('add')
        self.right_stacked.setCurrentWidget(self.script_form)

    def show_data_source_details(self, item):
        self.current_data_source = item.text()
        ds = self.db.data_sources.get(self.current_data_source)
        if ds:
            self.ds_form.set_mode('edit', ds)
            self.right_stacked.setCurrentWidget(self.ds_form)

    def show_script_details(self, item):
        self.current_script = item.text()
        script = self.db.scripts.get(self.current_script)
        if script:
            self.script_form.set_mode('edit', script)
            self.right_stacked.setCurrentWidget(self.script_form)

    def refresh_data_sources(self):
        self.data_source_list.clear()
        for name in self.db.data_sources.keys():
            self.data_source_list.addItem(name)
        # self.show_first_data_source()

    def handle_data_source_deleted(self, name):
        """处理数据源删除事件"""
        self.refresh_data_sources()
        self.right_stacked.setCurrentWidget(self.blank_page)

    def refresh_scripts(self):
        self.script_list.clear()
        for name in self.db.scripts.keys():
            self.script_list.addItem(name)
        # self.show_first_script()

    def handle_script_deleted(self, name):
        self.refresh_scripts()
        self.right_stacked.setCurrentWidget(self.blank_page)