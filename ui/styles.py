from PySide6.QtGui import QPalette, QColor, QFont


def apply_style(app):
    # 设置 GitHub 风格的调色板
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(246, 248, 250))  # 主背景
    palette.setColor(QPalette.WindowText, QColor(36, 41, 46))  # 主要文字
    palette.setColor(QPalette.Base, QColor(255, 255, 255))  # 输入控件背景
    palette.setColor(QPalette.AlternateBase, QColor(250, 251, 252))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(36, 41, 46))
    palette.setColor(QPalette.Text, QColor(36, 41, 46))  # 文本颜色
    palette.setColor(QPalette.Button, QColor(250, 251, 252))  # 按钮背景
    palette.setColor(QPalette.ButtonText, QColor(36, 41, 46))  # 按钮文字
    palette.setColor(QPalette.Highlight, QColor(3, 102, 214))  # 选中高亮
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    # 设置字体
    font = QFont("Segoe UI", 11)
    app.setFont(font)

    # GitHub Desktop 风格样式表
    style = """
    /* ===== 全局样式 ===== */
    * {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 11px;
        outline: none;
    }

    /* ===== 主窗口 ===== */
    QMainWindow {
        background-color: #F6F8FA;
    }

    /* ===== 分割线 ===== */
    QSplitter::handle {
        background: #E1E4E8;
        width: 1px;
    }

    /* ===== 按钮样式 ===== */
    QPushButton {
        padding: 5px 12px;
        border-radius: 6px;
        border: 1px solid rgba(27, 31, 35, 0.15);
        background-color: #F6F8FA;
        color: #24292E;
        font-weight: 500;
        min-width: 80px;
    }

    QPushButton:hover {
        background-color: #EFF3F6;
        border-color: rgba(27, 31, 35, 0.2);
    }

    QPushButton:pressed {
        background-color: #E9ECEF;
    }
    
     /* 标签页切换动画 */
    QTabWidget::pane {
        animation: fadeIn 200ms;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* 主要按钮 (绿色) */
    QPushButton#save_btn {
        background-color: #2EA44F;
        color: white;
        border-color: rgba(27, 31, 35, 0.15);
    }

    QPushButton#save_btn:hover {
        background-color: #2C974B;
    }

    QPushButton#save_btn:pressed {
        background-color: #298E46;
    }

    /* 次要按钮 (蓝色) */
    QPushButton#test_btn {
        background-color: #2188FF;
        color: white;
    }

    QPushButton#test_btn:hover {
        background-color: #1B7DE5;
    }

    QPushButton#test_btn:pressed {
        background-color: #1971D2;
    }

    /* 危险操作按钮 (红色) */
     QPushButton#delete_btn {
        background-color: #D73A49; 
        color: white;
        border: 1px solid #CB2431;
        border-radius: 6px;
        padding: 5px 12px;
        min-width: 80px;
        font-weight: 500;
    }
    
    QPushButton#delete_btn:hover {
        background-color: #CB2431;
        border-color: #B31D28;
    }

    QPushButton#delete_btn:pressed {
        background-color: #B31D28;
        border-color: #9E1C23;
    }

    QPushButton#delete_btn:disabled {
        background-color: #FFDCE0;
        color: #CB2431;
        border-color: #FFD1D7;
    }
    
    /* 取消按钮样式 */
    QPushButton#cancel_btn {
        background-color: #FF9800;
        color: white;
        border: 1px solid #F57C00;
    }
    
    QPushButton#cancel_btn:hover {
        background-color: #FB8C00;
    }
    
    QPushButton#cancel_btn:pressed {
        background-color: #F57C00;
    }

    /* ===== 输入控件 ===== */
    QLineEdit, QTextEdit, QComboBox {
        border: 1px solid #E1E4E8;
        border-radius: 6px;
        padding: 5px 8px;
        background: white;
        selection-background-color: #0366D6;
        selection-color: white;
    }

    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
        border-color: #2188FF;
        box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
    }

    QTextEdit {
        min-height: 120px;
    }

    /* ===== 标签页 ===== */
    QTabWidget::pane {
        border: none;
        background: white;
    }

    QTabBar {
        background: transparent;
    }

    QTabBar::tab {
        background: transparent;
        color: #586069;
        padding: 8px 16px;
        border-bottom: 2px solid transparent;
        font-weight: 500;
    }

    QTabBar::tab:selected {
        color: #24292E;
        border-bottom: 2px solid #F9826C;
        font-weight: 600;
    }

    QTabBar::tab:hover {
        color: #24292E;
    }

    /* ===== 列表控件 ===== */
    QListWidget {
        background: white;
        border: none;
        border-radius: 6px;
    }

    QListWidget::item {
        padding: 8px 12px;
        border-bottom: 1px solid #E1E4E8;
    }

    QListWidget::item:selected {
        background-color: #F6F8FA;
        color: #24292E;
        border-left: 3px solid #F9826C;
    }

    QListWidget::item:hover {
        background-color: #F6F8FA;
    }

    /* ===== 进度条 ===== */
    QProgressBar {
        border: 1px solid #E1E4E8;
        border-radius: 6px;
        background: white;
        height: 10px;
        text-align: center;
    }

    QProgressBar::chunk {
        background-color: #2EA44F;
        border-radius: 4px;
    }

    /* ===== 表单标签 ===== */
    QLabel {
        color: #24292E;
        font-weight: 600;
    }

    /* ===== 工具提示 ===== */
    QToolTip {
        background-color: #25292E;
        color: white;
        border: none;
        padding: 4px 8px;
        border-radius: 4px;
    }
    """
    app.setStyleSheet(style)
