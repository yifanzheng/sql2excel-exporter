import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # 设置为Fusion风格
    window = MainWindow()
    window.show()
    sys.exit(app.exec())