"""主窗口 — 按原型设计"""

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from ui.page_merge import MergePage
from ui.page_split import SplitPage
from ui.page_word2pdf import Word2PdfPage
from ui.widgets import ToastNotification

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF 工具箱")
        self.setMinimumSize(1100, 700)
        self.resize(1200, 800)
        self.setup_ui()
    
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        # ===== 顶部栏 =====
        topbar = QWidget()
        topbar.setFixedHeight(56)
        topbar.setStyleSheet("background: white; border-bottom: 1px solid #E5E7EB;")
        tb = QHBoxLayout(topbar)
        tb.setContentsMargins(24, 0, 24, 0)
        
        # Logo
        logo = QLabel()
        logo.setText('<span style="font-size:18px;font-weight:700;'
                     'background:linear-gradient(135deg,#365EFF,#7C3AED);'
                     '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">'
                     '📄 PDF 工具箱</span>')
        logo.setTextFormat(Qt.RichText)
        tb.addWidget(logo)
        tb.addStretch()
        
        badge = QLabel("♾️ 无限页数 · 全部免费")
        badge.setStyleSheet("font-size:12px;background:#ECFDF5;color:#10B981;"
                           "padding:4px 14px;border-radius:20px;font-weight:600;"
                           "border:1px solid #A7F3D0;")
        tb.addWidget(badge)
        
        btn_setting = QPushButton("⚙️")
        btn_setting.setFixedSize(32, 32)
        btn_setting.setStyleSheet("QPushButton{background:white;border:1px solid #E5E7EB;"
                                 "border-radius:6px;font-size:16px;}"
                                 "QPushButton:hover{background:#F3F4F6;}")
        tb.addWidget(btn_setting)
        main.addWidget(topbar)
        
        # ===== 主体 =====
        body = QWidget()
        body.setStyleSheet("background: #F5F6F8;")
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        
        # 侧边栏
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background: white; border: none;
                border-right: 1px solid #E5E7EB;
                padding: 16px 8px; font-size: 14px; color: #6B7280; outline: none;
            }
            QListWidget::item {
                padding: 10px 14px; border-radius: 6px; margin: 1px 6px;
            }
            QListWidget::item:selected {
                background: #EEF2FF; color: #365EFF; font-weight: 600;
                border-left: 3px solid #365EFF;
            }
            QListWidget::item:hover:!selected {
                background: #F3F4F6; color: #365EFF;
            }
        """)
        
        self.page_keys = ["merge", "split", "word"]
        tabs = [
            "📄  PDF 合并", "✂️  拆分文档",
            "📝  Word 转 PDF",
        ]
        for t in tabs:
            self.sidebar.addItem(QListWidgetItem(t))
        self.sidebar.currentRowChanged.connect(self._on_nav)
        body_layout.addWidget(self.sidebar)
        
        # 页面
        self.stack = QStackedWidget()
        pages = [
            MergePage(), SplitPage(),
            Word2PdfPage(),
        ]
        self.pages = {key: p for key, p in zip(self.page_keys, pages)}
        for p in pages:
            self.stack.addWidget(p)
        body_layout.addWidget(self.stack, 1)
        main.addWidget(body, 1)
        
        # Toast
        self.toast = ToastNotification(self)
    
    def _on_nav(self, idx):
        if 0 <= idx < len(self.page_keys):
            self.stack.setCurrentWidget(self.pages[self.page_keys[idx]])
    
    def go_to(self, key):
        if key in self.page_keys:
            self.sidebar.setCurrentRow(self.page_keys.index(key))
